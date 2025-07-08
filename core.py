import aiohttp
import asyncio
import warnings
from typing import Optional, Dict, Union, Callable
from urllib.parse import urlparse
from .broadcast import Stream, Response
from .settings import SSL, Proxy
from .auth import Basic, Bearer, JWT, Key, OAuth
from .config import Redirects, Retry, Limits, Timeout


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
        endpoint: str,
        limits: Optional[Limits] = None,
        retry: Optional[Retry] = None,
        timeout: Optional[Timeout] = None,
        redirects: Optional[Redirects] = None,
        proxy: Optional[Proxy] = None,
        ssl: Optional[SSL] = None,
        auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None,
        cookies: Optional[Dict[str, str]] = None,
        hooks: Optional[Dict[str, Callable]] = None,
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
        self.endpoint = endpoint

        # Apply default configurations if not provided
        # Each configuration class provides sensible defaults
        self.limits = limits or Limits()
        self.retry = retry or Retry()
        self.timeout = timeout or Timeout()
        self.redirects = redirects or Redirects()
        self.ssl = ssl or SSL()

        # Store optional configurations
        # These may be None and will be handled appropriately
        self.proxy = proxy
        self.cookies = cookies or {}
        self.hooks = hooks or {}
        self.auth = auth

        # Validate proxy configuration if provided
        # All proxy parameters must be valid for connection to work
        if self.proxy:
            if not (
                bool(self.proxy.host.strip())
                and 1 <= self.proxy.port <= 65535
                and (not self.proxy.username or bool(self.proxy.username.strip()))
                and (not self.proxy.password or bool(self.proxy.password.strip()))
            ):
                raise ValueError("Invalid proxy configuration")

        # Validate SSL configuration if provided
        # SSL context must be properly configured or None
        if self.ssl and not self.ssl.context is not None:
            raise ValueError("Invalid SSL configuration")

        # Initialize session as None - will be created in __aenter__
        # This allows proper async context manager usage
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "CrawlCore":
        """
        Asynchronously enter the context manager and initialize the HTTP session.

        This method sets up the aiohttp ClientSession for making requests.
        The session manages connection pooling, cookies, and other HTTP features.

        The session is only created once and reused for all requests within
        the context manager scope, providing efficient connection pooling.

        Returns:
            CrawlCore: The initialized CrawlCore instance

        Raises:
            ValueError: If the endpoint protocol is not HTTP or HTTPS
        """
        # Only create session if it doesn't exist
        # This prevents multiple session creation in nested contexts
        if not self.session:
            # Parse the endpoint URL to extract scheme
            # This is used for protocol validation
            parsed = urlparse(self.endpoint)
            scheme = parsed.scheme.lower()

            # Validate protocol scheme
            # Only HTTP and HTTPS are supported protocols
            if scheme not in ["http", "https"]:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")

            # Create TCP connector with connection limits from dataclass
            # This manages the connection pool and keep-alive behavior
            connector = aiohttp.TCPConnector(
                limit=self.limits.connections,
                limit_per_host=self.limits.host,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

            # Configure SSL context with enhanced security validation
            # This applies custom SSL settings if provided
            if self.ssl.context:
                # Use the configured SSL context
                # This allows custom certificate validation
                connector._ssl = self.ssl.context

                # Warn if using insecure SSL configuration
                # This helps identify potential security issues
                if self.ssl.verify or self.ssl.context is False:
                    warnings.warn(
                        "SSL verification is disabled - connection is vulnerable to attacks"
                    )

            # Create timeout configuration from dataclass
            # This sets up comprehensive timeout handling
            timeout = aiohttp.ClientTimeout(
                total=self.timeout.pool,
                connect=self.timeout.connect,
                sock_read=self.timeout.read,
                sock_connect=self.timeout.connect,
            )

            # Create HTTP session with connector and default timeout
            # This is the core session used for all HTTP requests
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
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
        method: str,
        url: str,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Optional[Response]:
        """
        Send an HTTP request using the specified method and URL with comprehensive error handling and retry logic.

        This method handles authentication, cookies, hooks, proxy configuration, and implements retry logic
        with exponential backoff for failed requests. It's the core method that all HTTP operations use.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
            url: The target URL for the request
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Cookies for this request (merged with instance cookies)
            **kwargs: Additional arguments passed to aiohttp (headers, data, json, etc.)

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred

        Raises:
            RuntimeError: If the session is not initialized (not used in async with block)
        """
        # Ensure session is initialized
        # This prevents usage outside of async context manager
        if not self.session:
            raise RuntimeError(
                "CrawlCore session is not initialized. Use it within an 'async with' block."
            )

        # Apply authentication
        # Authentication is applied to headers or query parameters based on type
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})

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
        # This ensures authentication is applied to the request
        kwargs["headers"] = headers
        if params:
            kwargs["params"] = params

        # Merge cookies (request cookies override instance cookies)
        # This allows per-request cookie customization
        merged = self.cookies.copy()
        if cookies:
            merged.update(cookies)
        if merged:
            kwargs["cookies"] = merged

        # Execute request hook if provided
        # This allows custom request processing before sending
        if "request" in self.hooks:
            try:
                await self.hooks["request"](method, url, **kwargs)
            except Exception as error:
                warnings.warn(f"Request hook failed: {error}")

        # Handle timeout parameter conversion
        # This normalizes timeout formats for aiohttp
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

        # Handle redirect parameters using dataclass values
        # This configures redirect behavior for the request
        if redirects is not None:
            kwargs["allow_redirects"] = redirects
        kwargs["max_redirects"] = self.redirects.limit

        # Build full URL from endpoint and relative path
        # This handles both absolute and relative URLs
        if url.startswith("/"):
            url = self.endpoint + url

        # Attempt request with retry logic using dataclass values
        # This implements exponential backoff for failed requests
        for attempt in range(self.retry.total + 1):
            try:
                # Set up proxy
                # Proxy configuration is validated and applied per request
                if self.proxy:
                    # Validate proxy before use
                    # This prevents invalid proxy configurations from causing errors
                    if not (
                        bool(self.proxy.host.strip())
                        and 1 <= self.proxy.port <= 65535
                        and (
                            not self.proxy.username or bool(self.proxy.username.strip())
                        )
                        and (
                            not self.proxy.password or bool(self.proxy.password.strip())
                        )
                    ):
                        warnings.warn("Invalid proxy configuration detected")
                        break

                    # Generate proxy URL
                    # This creates the proxy URL with optional authentication
                    if self.proxy.username and self.proxy.password:
                        kwargs["proxy"] = (
                            f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
                        )
                        warnings.warn("Using authenticated proxy connection")
                    else:
                        kwargs["proxy"] = f"http://{self.proxy.host}:{self.proxy.port}"
                        warnings.warn("Using anonymous proxy connection")

                    # Add proxy headers if configured
                    # This allows custom proxy headers to be sent
                    if self.proxy.headers:
                        headers = kwargs.get("headers", {})
                        headers.update(self.proxy.headers)
                        kwargs["headers"] = headers

                # Make HTTP request using session
                # This is the actual HTTP request execution
                async with self.session.request(method, url, **kwargs) as response:
                    # Check if we should retry based on status code from dataclass
                    # This handles retryable HTTP status codes
                    if (
                        response.status in self.retry.status
                        and attempt < self.retry.total
                    ):
                        warnings.warn(
                            f"Request failed with status {response.status}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                        )
                        # Calculate exponential backoff delay using dataclass value
                        # This prevents overwhelming the server with rapid retries
                        delay = self.retry.backoff * (2**attempt)
                        await asyncio.sleep(delay)
                        continue

                    # Raise exception for HTTP error status codes
                    # This handles HTTP error responses
                    response.raise_for_status()

                    # Create response object
                    # This wraps the aiohttp response in our custom Response class
                    response = Response(response)

                    # Execute response hook if provided
                    # This allows custom response processing after receiving
                    if "response" in self.hooks:
                        try:
                            await self.hooks["response"](response)
                        except Exception as error:
                            warnings.warn(f"Response hook failed: {error}")

                    return response

            except aiohttp.ClientResponseError as error:
                # Handle HTTP response errors with retry logic
                # This manages HTTP error status codes with retry capability
                if error.status in self.retry.status and attempt < self.retry.total:
                    warnings.warn(
                        f"Request failed with status {error.status}, retrying... (attempt {attempt + 1}/{self.retry.total})"
                    )
                    # Calculate exponential backoff delay using dataclass value
                    # This implements exponential backoff for retryable errors
                    delay = self.retry.backoff * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Log final failure
                    # This records the final failure after all retries
                    warnings.warn(
                        f"Request failed with status {error.status}: {error.message}"
                    )
                    break
            except (
                aiohttp.ClientConnectionError,
                aiohttp.ServerTimeoutError,
                aiohttp.ClientProxyConnectionError,
            ) as error:
                # Handle connection, timeout, and proxy errors
                # These are network-level errors that may be retryable
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
                    # Calculate exponential backoff delay using dataclass value
                    # This implements exponential backoff for network errors
                    delay = self.retry.backoff * (2**attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Log final failure with proxy info if applicable
                    # This provides detailed error information for debugging
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
                # Handle unexpected errors
                # This catches any other exceptions that may occur
                warnings.warn(f"An unexpected error occurred: {error}")
                break

        # Return None if all retries failed
        # This indicates that the request could not be completed
        return None

    async def stream(
        self,
        method: str,
        url: str,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Stream:
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
            url: The target URL for the streaming request
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
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})

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
        merged = self.cookies.copy()
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
            if self.proxy.username and self.proxy.password:
                kwargs["proxy"] = (
                    f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
                )
            else:
                kwargs["proxy"] = f"http://{self.proxy.host}:{self.proxy.port}"

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
        if url.startswith("/"):
            url = self.endpoint + url

        # Execute request hook if provided
        # This allows custom request processing before streaming
        if "request" in self.hooks:
            try:
                await self.hooks["request"](method, url, **kwargs)
            except Exception as error:
                warnings.warn(f"Request hook failed: {error}")

        try:
            # Make streaming HTTP request
            # This creates the streaming connection
            response = await self.session.request(method, url, **kwargs)

            # Raise exception for HTTP error status codes
            # This handles HTTP error responses for streaming
            response.raise_for_status()

            # Create stream wrapper
            # This wraps the aiohttp response in our custom Stream class
            stream = Stream(response)

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
