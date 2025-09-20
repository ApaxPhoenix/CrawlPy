import aiohttp
import asyncio
import warnings
from typing import Optional, Dict, Union, Callable, TypeVar, Awaitable, Any
from urllib.parse import urlparse
from broadcast import Stream, Response
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth
from config import Redirects, Retry, Limits, Timeout

# Enhanced type definitions for improved type safety and clarity
T = TypeVar("T")
CrawlCoreType = TypeVar("CrawlCoreType", bound="CrawlCore")
ResponseType = TypeVar("ResponseType", bound=Response)
StreamType = TypeVar("StreamType", bound=Stream)
AuthType = TypeVar("AuthType", bound=Union[Basic, Bearer, JWT, Key, OAuth])
ConfigType = TypeVar("ConfigType")
HookType = Callable[..., Awaitable[Any]]
RequestHookType = Callable[[str, str], Awaitable[None]]
ResponseHookType = Callable[[ResponseType], Awaitable[None]]
StreamHookType = Callable[[StreamType], Awaitable[None]]
SessionType = TypeVar("SessionType", bound=aiohttp.ClientSession)
ConnectorType = TypeVar("ConnectorType", bound=aiohttp.TCPConnector)
TimeoutType = Union[float, aiohttp.ClientTimeout]
HeadersType = Dict[str, str]
CookiesType = Dict[str, str]
ParamsType = Dict[str, Any]
HooksType = Dict[str, HookType]
UrlType = str
HttpMethod = str
ProxyUrl = str


class CrawlCore:
    """
    Asynchronous HTTP client for making web requests with comprehensive error handling,
    proxy support, SSL support, authentication, cookies, and hooks.

    This class provides a low-level interface for making HTTP requests using aiohttp.
    It supports session management, retry logic, and streaming capabilities.

    The CrawlCore acts as the foundation for higher-level HTTP clients, providing
    robust connection management, automatic retries with exponential backoff,
    comprehensive authentication support, and detailed error handling.
    """

    def __init__(
            self,
            endpoint: UrlType,
            limits: Optional[Limits] = None,
            retry: Optional[Retry] = None,
            timeout: Optional[Timeout] = None,
            redirects: Optional[Redirects] = None,
            proxy: Optional[Proxy] = None,
            ssl: Optional[SSL] = None,
            auth: Optional[AuthType] = None,
            cookies: Optional[CookiesType] = None,
            hooks: Optional[HooksType] = None,
    ) -> None:
        """
        Initialize the HTTP client with a base endpoint URL and configuration.

        All configuration parameters are validated during initialization to ensure
        proper client setup. Default configurations are applied for optional parameters
        to provide sensible defaults while allowing fine-tuned control.

        Args:
            endpoint: The base URL for HTTP requests (must include http:// or https://)
            limits: Connection limit configuration (Limits dataclass)
            retry: Retry configuration (Retry dataclass)
            timeout: Timeout configuration (Timeout dataclass)
            redirects: Redirect configuration (Redirects dataclass)
            proxy: Proxy configuration for requests
            ssl: SSL/TLS configuration
            auth: Authentication configuration (Basic, Bearer, JWT, Key, or OAuth)
            cookies: Default cookies as key-value pairs
            hooks: Request/response hooks {"request": callable, "response": callable}

        Raises:
            TypeError: If endpoint is not a string
            ValueError: If endpoint doesn't start with http:// or https://
            ValueError: If proxy configuration is invalid
            ValueError: If SSL configuration is invalid
        """
        # Validate endpoint parameter type
        # This ensures the endpoint is a string before URL parsing
        if not isinstance(endpoint, str):
            raise TypeError("Endpoint must be a string.")

        # Validate endpoint URL scheme
        # Only HTTP and HTTPS protocols are supported for web requests
        if not urlparse(endpoint).scheme in {"http", "https"}:
            raise ValueError("Endpoint must start with 'http' or 'https'.")

        # Store core endpoint configuration
        # This will be used as the base URL for all requests
        self.endpoint: UrlType = endpoint

        # Apply default configurations if not provided
        # Each configuration class provides sensible defaults
        self.limits: Limits = limits or Limits()
        self.retry: Retry = retry or Retry()
        self.timeout: Timeout = timeout or Timeout()
        self.redirects: Redirects = redirects or Redirects()
        self.ssl: SSL = ssl or SSL()

        # Store optional configurations
        # These may be None and will be handled appropriately
        self.proxy: Optional[Proxy] = proxy
        self.cookies: CookiesType = cookies or {}
        self.hooks: HooksType = hooks or {}
        self.auth: Optional[AuthType] = auth

        # Initialize session as None - will be created in __aenter__
        # This allows proper async context manager usage
        self.session: Optional[SessionType] = None

    async def __aenter__(self) -> CrawlCoreType:
        """
        Asynchronously enter the context manager and initialize the HTTP session.
        """
        if not self.session:
            parsed = urlparse(self.endpoint)
            scheme: str = parsed.scheme.lower()

            if scheme not in ["http", "https"]:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")

            # Create TCP connector with connection limits from dataclass
            connector: ConnectorType = aiohttp.TCPConnector(
                limit=self.limits.connections,
                limit_per_host=self.limits.host,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

            # Configure SSL context
            if self.ssl.context is not None:
                # Use the configured SSL context (could be False to disable SSL verification)
                connector._ssl = self.ssl.context

                # Warn if SSL verification is disabled
                if self.ssl.context is False or not self.ssl.verify:
                    warnings.warn(
                        "SSL verification is disabled - connection is vulnerable to attacks"
                    )

            # Create timeout configuration from dataclass
            config: aiohttp.ClientTimeout = aiohttp.ClientTimeout(
                total=self.timeout.pool,
                connect=self.timeout.connect,
                sock_read=self.timeout.read,
                sock_connect=self.timeout.connect,
            )

            # Create HTTP session with connector and default timeout
            self.session = aiohttp.ClientSession(connector=connector, timeout=config)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """
        Asynchronously exit the context manager and clean up the HTTP session.

        This method properly closes the aiohttp ClientSession and releases
        any associated resources like connection pools and file handles.

        Proper cleanup is essential to prevent resource leaks and ensure
        all connections are properly closed.

        Args:
            exc_type: Exception type if an exception occurred
            exc_value: Exception value if an exception occurred
            traceback: Exception traceback if an exception occurred
        """
        # Clean up session if it exists
        # This ensures proper resource cleanup
        if self.session:
            await self.session.close()
            self.session = None

    async def request(
            self,
            method: HttpMethod,
            endpoint: UrlType,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
            **kwargs: Any,
    ) -> Optional[ResponseType]:
        """
        Send an HTTP request using the specified method and endpoint with comprehensive error handling and retry logic.

        This method handles authentication, cookies, hooks, proxy configuration, and implements retry logic
        with exponential backoff for failed requests. It's the core method that all HTTP operations use.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
            endpoint: The target endpoint for the request
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Cookies for this request (merged with instance cookies)
            **kwargs: Additional arguments passed to aiohttp (headers, data, json, etc.)

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred

        Raises:
            RuntimeError: If the session is not initialized (not used in async with block)
        """
        # Ensure session is initialized before making any requests
        if not self.session:
            raise RuntimeError(
                "CrawlCore session is not initialized. Use it within an 'async with' block."
            )

        # Extract headers and params from kwargs for authentication
        heads: HeadersType = kwargs.get("headers", {})
        params: ParamsType = kwargs.get("params", {})

        # Apply authentication headers or parameters based on auth type
        if self.auth:
            if isinstance(self.auth, Basic):
                # Add Basic authentication header
                heads["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Bearer):
                # Add Bearer token authentication header
                heads["Authorization"] = self.auth.auth
            elif isinstance(self.auth, JWT):
                # Add JWT authentication header
                heads["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Key):
                # Add API key to header or query parameter based on configuration
                if self.auth.place == "header":
                    heads[self.auth.name] = self.auth.value
                elif self.auth.place == "query":
                    params[self.auth.name] = self.auth.value
            elif isinstance(self.auth, OAuth):
                # Add OAuth token if available
                if self.auth.token:
                    heads["Authorization"] = self.auth.auth

        # Update kwargs with modified headers and params
        kwargs["headers"] = heads
        if params:
            kwargs["params"] = params

        # Merge instance cookies with request-specific cookies
        merged: CookiesType = self.cookies.copy()
        if cookies:
            merged.update(cookies)
        if merged:
            kwargs["cookies"] = merged

        # Execute pre-request hook if configured
        if "request" in self.hooks:
            try:
                await self.hooks["request"](method, endpoint, **kwargs)
            except Exception as error:
                # Log hook failure but continue with request
                warnings.warn(f"Request hook failed: {error}")

        # Handle timeout parameter conversion
        if timeout is not None:
            if isinstance(timeout, (int, float)):
                # Convert simple timeout to ClientTimeout object
                timeout = aiohttp.ClientTimeout(total=timeout)
            elif not isinstance(timeout, aiohttp.ClientTimeout):
                # Use default timeout configuration
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout.pool,
                    connect=self.timeout.connect,
                    sock_read=self.timeout.read,
                    sock_connect=self.timeout.connect,
                )
            kwargs["timeout"] = timeout

        # Handle redirect configuration
        if redirects is not None:
            kwargs["allow_redirects"] = redirects
        kwargs["max_redirects"] = self.redirects.limit

        # Build full URL by prepending endpoint if URL is relative
        if endpoint.startswith("/"):
            endpoint = self.endpoint + endpoint

        # Attempt request with retry logic and exponential backoff
        for attempt in range(self.retry.total + 1):
            try:
                # Configure proxy if specified
                if self.proxy:
                    # Validate proxy configuration
                    if not (
                            bool(self.proxy.host.strip())
                            and 1 <= self.proxy.port <= 65535
                            and (not self.proxy.username or bool(self.proxy.username.strip()))
                            and (not self.proxy.password or bool(self.proxy.password.strip()))
                    ):
                        warnings.warn("Invalid proxy configuration detected")
                        break

                    # Set up authenticated or anonymous proxy connection
                    url: ProxyUrl
                    if self.proxy.username and self.proxy.password:
                        url = (
                            f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
                        )
                        warnings.warn("Using authenticated proxy connection")
                    else:
                        url = f"http://{self.proxy.host}:{self.proxy.port}"
                        warnings.warn("Using anonymous proxy connection")

                    kwargs["proxy"] = url

                    # Add proxy-specific headers if configured
                    if self.proxy.headers:
                        heads = kwargs.get("headers", {})
                        heads.update(self.proxy.headers)
                        kwargs["headers"] = heads

                # Make the actual HTTP request using aiohttp session
                async with self.session.request(method, endpoint, **kwargs) as resp:
                    # Check if we should retry based on response status code
                    if (
                            resp.status in self.retry.status
                            and attempt < self.retry.total
                    ):
                        warnings.warn(
                            f"Request failed with status {resp.status}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                        )
                        # Calculate exponential backoff delay
                        delay: float = self.retry.backoff * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue

                    # Raise exception for HTTP error status codes
                    resp.raise_for_status()

                    # Create response wrapper for enhanced functionality
                    wrapper: ResponseType = Response(resp)

                    # CRITICAL: Pre-cache content to prevent connection closure issues
                    # This ensures we can access response data even after the context manager exits
                    try:
                        # Read and cache the response content while connection is active
                        await wrapper.bytes()
                    except Exception as error:
                        # Log caching failure but continue - user might handle connection issues
                        warnings.warn(f"Failed to cache response content: {error}")

                    # Execute post-response hook if configured
                    if "response" in self.hooks:
                        try:
                            await self.hooks["response"](wrapper)
                        except Exception as error:
                            # Log hook failure but continue with response
                            warnings.warn(f"Response hook failed: {error}")

                    return wrapper

            except aiohttp.ClientResponseError as error:
                # Handle HTTP response errors with retry logic
                if error.status in self.retry.status and attempt < self.retry.total:
                    warnings.warn(
                        f"Request failed with status {error.status}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                    )
                    # Calculate exponential backoff delay
                    delay = self.retry.backoff * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Max retries reached or status not in retry list
                    warnings.warn(
                        f"Request failed with status {error.status}: {error.message}"
                    )
                    break
            except (
                    aiohttp.ClientConnectionError,
                    aiohttp.ServerTimeoutError,
                    aiohttp.ClientProxyConnectionError,
            ) as error:
                # Handle connection, timeout, and proxy errors with retry logic
                if attempt < self.retry.total:
                    if (
                            isinstance(error, aiohttp.ClientProxyConnectionError)
                            and self.proxy
                    ):
                        warnings.warn(
                            f"Proxy connection failed to {self.proxy.host}:{self.proxy.port}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                        )
                    else:
                        warnings.warn(
                            f"Request failed with {error.__class__.__name__}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                        )
                    # Calculate exponential backoff delay
                    delay = self.retry.backoff * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Max retries reached - log final failure
                    if (
                            isinstance(error, aiohttp.ClientProxyConnectionError)
                            and self.proxy
                    ):
                        warnings.warn(
                            f"Proxy connection failed permanently to {self.proxy.host}:{self.proxy.port}: {error}"
                        )
                    else:
                        warnings.warn(f"Request failed: {error}")
                    break
            except Exception as error:
                # Handle any unexpected errors
                warnings.warn(f"An unexpected error occurred: {error}")
                break

        # Return None if all retry attempts failed
        return None

    async def stream(
            self,
            method: HttpMethod,
            endpoint: UrlType,
            timeout: Optional[TimeoutType] = None,
            cookies: Optional[CookiesType] = None,
            **kwargs: Any,
    ) -> StreamType:
        """
        Send a streaming HTTP request for handling large data transfers.

        This method creates a streaming connection that can be used for uploading
        or downloading large amounts of data without loading everything into memory.

        Streaming is essential for handling large files, real-time data, or any
        situation where loading the entire response into memory would be problematic.

        Unlike the regular request method, streaming doesn't implement retry logic
        since streams are typically used for one-time operations and retrying
        a partial stream could cause data corruption.

        Args:
            method: HTTP method for the streaming request
            endpoint: The target endpoint for the streaming request
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            cookies: Optional cookies as key-value pairs
            **kwargs: Additional arguments passed to aiohttp

        Returns:
            Stream: Stream object for handling the streaming operation

        Raises:
            RuntimeError: If the session is not initialized
            aiohttp.ClientResponseError: If the request fails with an HTTP error
            aiohttp.ClientConnectionError: If there's a connection problem
            aiohttp.ServerTimeoutError: If the request times out
        """
        # Ensure session is initialized
        # This prevents usage outside of async context manager
        if not self.session:
            raise RuntimeError(
                "CrawlCore session is not initialized. Use it within an 'async with' block."
            )

        # Apply authentication
        # Authentication is applied the same way as regular requests
        headers: HeadersType = kwargs.get("headers", {})
        params: ParamsType = kwargs.get("params", {})

        if self.auth:
            # Apply authentication headers based on type
            # Each auth type has specific header format requirements
            if isinstance(self.auth, Basic):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Bearer):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, JWT):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Key):
                # API keys can be in headers or query parameters
                if self.auth.place == "header":
                    headers[self.auth.name] = self.auth.value
                elif self.auth.place == "query":
                    params[self.auth.name] = self.auth.value
            elif isinstance(self.auth, OAuth):
                # OAuth requires token validation
                if self.auth.token:
                    headers["Authorization"] = self.auth.auth

        # Update kwargs with authentication data
        # This ensures authentication is applied to the streaming request
        kwargs["headers"] = headers
        if params:
            kwargs["params"] = params

        # Merge cookies (request cookies override instance cookies)
        # This allows per-request cookie customization for streaming
        merged: CookiesType = self.cookies.copy()
        if cookies:
            merged.update(cookies)
        if merged:
            kwargs["cookies"] = merged

        # Handle timeout parameter conversion using dataclass values
        # This normalizes timeout formats for aiohttp streaming
        if timeout is not None:
            if isinstance(timeout, (int, float)):
                # Convert simple timeout to ClientTimeout
                timeout = aiohttp.ClientTimeout(total=timeout)
            elif not isinstance(timeout, aiohttp.ClientTimeout):
                # Use default timeout from dataclass
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout.pool,
                    connect=self.timeout.connect,
                    sock_read=self.timeout.read,
                    sock_connect=self.timeout.connect,
                )
            kwargs["timeout"] = timeout

        # Set up proxy for streaming request
        # Proxy configuration is validated and applied for streaming
        if self.proxy:
            # Validate proxy before use
            # This prevents invalid proxy configurations from causing errors
            if not (
                    bool(self.proxy.host.strip())
                    and 1 <= self.proxy.port <= 65535
                    and (not self.proxy.username or bool(self.proxy.username.strip()))
                    and (not self.proxy.password or bool(self.proxy.password.strip()))
            ):
                raise ValueError("Invalid proxy configuration for streaming request")

            # Generate proxy URL
            # This creates the proxy URL with optional authentication
            url: ProxyUrl
            if self.proxy.username and self.proxy.password:
                url = (
                    f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
                )
            else:
                url = f"http://{self.proxy.host}:{self.proxy.port}"

            kwargs["proxy"] = url

            # Add proxy headers if configured
            # This allows custom proxy headers to be sent
            if self.proxy.headers:
                headers = kwargs.get("headers", {})
                headers.update(self.proxy.headers)
                kwargs["headers"] = headers

            # Log proxy usage for streaming
            # This helps identify secured proxy connections
            if self.proxy.port == 443 or self.proxy.port == 8443:
                warnings.warn("Using secured proxy for streaming request")

        # Build full URL from endpoint and relative path
        # This handles both absolute and relative URLs for streaming
        if endpoint.startswith("/"):
            endpoint = self.endpoint + endpoint

        # Execute request hook if provided
        # This allows custom request processing before streaming
        if "request" in self.hooks:
            try:
                await self.hooks["request"](method, endpoint, **kwargs)
            except Exception as error:
                warnings.warn(f"Request hook failed: {error}")

        try:
            # Make streaming HTTP request
            # This creates the streaming connection
            response: aiohttp.ClientResponse = await self.session.request(method, endpoint, **kwargs)

            # Raise exception for HTTP error status codes
            # This handles HTTP error responses for streaming
            response.raise_for_status()

            # Create stream wrapper
            # This wraps the aiohttp response in our custom Stream class
            stream: StreamType = Stream(response)

            # Execute response hook if provided
            # This allows custom response processing for streaming
            if "response" in self.hooks:
                try:
                    await self.hooks["response"](stream)
                except Exception as error:
                    warnings.warn(f"Response hook failed: {error}")

            return stream
        except aiohttp.ClientResponseError as error:
            # Log and re-raise HTTP response errors
            # This handles HTTP error responses for streaming
            warnings.warn(f"Request failed with status {error.status}: {error.message}")
            raise
        except (
                aiohttp.ClientConnectionError,
                aiohttp.ClientProxyConnectionError,
        ) as error:
            # Enhanced proxy error handling
            # This provides detailed error information for proxy issues
            if isinstance(error, aiohttp.ClientProxyConnectionError) and self.proxy:
                warnings.warn(
                    f"Proxy connection error to {self.proxy.host}:{self.proxy.port}: {error}"
                )
            else:
                warnings.warn(f"Connection error: {error}")
            raise
        except aiohttp.ServerTimeoutError:
            # Log and re-raise timeout errors
            # This handles timeout errors for streaming
            warnings.warn("Request timed out")
            raise
        except Exception as error:
            # Log and re-raise unexpected errors
            # This catches any other exceptions that may occur
            warnings.warn(f"An unexpected error occurred: {error}")
            raise