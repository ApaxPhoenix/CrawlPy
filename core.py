import aiohttp
import asyncio
import warnings
from typing import Optional, Dict, Union, Callable
from urllib.parse import urlparse
from broadcast import Stream, Response
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth
from config import Redirects, Retry, Limits, Timeout


class CrawlCore:
    """
    Asynchronous HTTP client for making web requests with comprehensive error handling,
    proxy support, SSL support, authentication, cookies, and hooks.
    This class provides a low-level interface for making HTTP requests using aiohttp.
    It supports session management, retry logic, and streaming capabilities.
    """

    def __init__(self, endpoint: str, limits: Optional[Limits] = None, retry: Optional[Retry] = None,
                 timeout: Optional[Timeout] = None, redirects: Optional[Redirects] = None,
                 proxy: Optional[Proxy] = None, ssl: Optional[SSL] = None,
                 auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None,
                 cookies: Optional[Dict[str, str]] = None, hooks: Optional[Dict[str, Callable]] = None) -> None:
        """
        Initialize the HTTP client with a base endpoint URL and configuration.
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
        """
        # Validate endpoint parameter type
        if not isinstance(endpoint, str):
            raise TypeError("Endpoint must be a string.")
        # Validate endpoint URL scheme
        if not urlparse(endpoint).scheme in {'http', 'https'}:
            raise ValueError("Endpoint must start with 'http' or 'https'.")

        # Store configuration
        self.endpoint = endpoint
        self.limits = limits or Limits()
        self.retry = retry or Retry()
        self.timeout = timeout or Timeout()
        self.redirects = redirects or Redirects()
        self.ssl = ssl or SSL()
        self.proxy = proxy
        self.cookies = cookies or {}
        self.hooks = hooks or {}
        self.auth = auth

        # Validate proxy configuration if provided
        if self.proxy:
            if not (bool(self.proxy.host.strip()) and
                   1 <= self.proxy.port <= 65535 and
                   (not self.proxy.username or bool(self.proxy.username.strip())) and
                   (not self.proxy.password or bool(self.proxy.password.strip()))):
                raise ValueError("Invalid proxy configuration")

        # Validate SSL configuration if provided
        if self.ssl and not self.ssl.context is not None:
            raise ValueError("Invalid SSL configuration")

        # Initialize session as None - will be created in __aenter__
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "CrawlCore":
        """
        Asynchronously enter the context manager and initialize the HTTP session.
        This method sets up the aiohttp ClientSession for making requests.
        The session manages connection pooling, cookies, and other HTTP features.
        Returns:
            CrawlCore: The initialized CrawlCore instance
        Raises:
            ValueError: If the endpoint protocol is not HTTP or HTTPS
        """
        # Only create session if it doesn't exist
        if not self.session:
            # Parse the endpoint URL to extract scheme
            parsed = urlparse(self.endpoint)
            scheme = parsed.scheme.lower()
            # Validate protocol scheme
            if scheme not in ['http', 'https']:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")

            # Create TCP connector with connection limits from dataclass
            connector = aiohttp.TCPConnector(
                limit=self.limits.connections,
                limit_per_host=self.limits.host,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )

            # Configure SSL context with enhanced security validation
            if self.ssl.context:
                # Use the configured SSL context
                connector._ssl = self.ssl.context
                # Warn if using insecure SSL configuration
                if self.ssl.verify or self.ssl.context is False:
                    warnings.warn("SSL verification is disabled - connection is vulnerable to attacks")

            # Create timeout configuration from dataclass
            timeout = aiohttp.ClientTimeout(
                total=self.timeout.pool,
                connect=self.timeout.connect,
                sock_read=self.timeout.read,
                sock_connect=self.timeout.connect
            )

            # Create HTTP session with connector and default timeout
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """
        Asynchronously exit the context manager and clean up the HTTP session.
        This method properly closes the aiohttp ClientSession and releases
        any associated resources like connection pools and file handles.
        Args:
            exc_type: Exception type if an exception occurred
            exc_value: Exception value if an exception occurred
            traceback: Exception traceback if an exception occurred
        """
        # Clean up session if it exists
        if self.session:
            await self.session.close()
            self.session = None

    async def request(self, method: str, url: str, timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                      redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None, **kwargs) -> Optional[Response]:
        """
        Send an HTTP request using the specified method and URL with comprehensive error handling and retry logic.
        This method handles authentication, cookies, hooks, proxy configuration, and implements retry logic
        with exponential backoff for failed requests.
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
        if not self.session:
            raise RuntimeError("CrawlCore session is not initialized. Use it within an 'async with' block.")

        # Apply authentication
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})

        if self.auth:
            # Apply authentication headers based on type
            if isinstance(self.auth, Basic):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Bearer):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, JWT):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Key):
                if self.auth.place == "header":
                    headers[self.auth.name] = self.auth.value
                elif self.auth.place == "query":
                    params[self.auth.name] = self.auth.value
            elif isinstance(self.auth, OAuth):
                if self.auth.token:
                    headers["Authorization"] = self.auth.auth

        kwargs['headers'] = headers
        if params:
            kwargs['params'] = params

        # Merge cookies (request cookies override instance cookies)
        merged = self.cookies.copy()
        if cookies:
            merged.update(cookies)
        if merged:
            kwargs['cookies'] = merged

        # Execute request hook if provided
        if 'request' in self.hooks:
            try:
                await self.hooks['request'](method, url, **kwargs)
            except Exception as error:
                warnings.warn(f"Request hook failed: {error}")

        # Handle timeout parameter conversion
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
                    sock_connect=self.timeout.connect
                )
            kwargs['timeout'] = timeout

        # Handle redirect parameters using dataclass values
        if redirects is not None:
            kwargs['allow_redirects'] = redirects
        kwargs['max_redirects'] = self.redirects.maximum

        # Build full URL from endpoint and relative path
        if url.startswith('/'):
            url = self.endpoint + url

        # Attempt request with retry logic using dataclass values
        for attempt in range(self.retry.total + 1):
            try:
                # Set up proxy
                if self.proxy:
                    # Validate proxy before use
                    if not (bool(self.proxy.host.strip()) and
                           1 <= self.proxy.port <= 65535 and
                           (not self.proxy.username or bool(self.proxy.username.strip())) and
                           (not self.proxy.password or bool(self.proxy.password.strip()))):
                        warnings.warn("Invalid proxy configuration detected")
                        break

                    # Generate proxy URL
                    if self.proxy.username and self.proxy.password:
                        kwargs['proxy'] = f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
                        warnings.warn("Using authenticated proxy connection")
                    else:
                        kwargs['proxy'] = f"http://{self.proxy.host}:{self.proxy.port}"
                        warnings.warn("Using anonymous proxy connection")

                    # Add proxy headers if configured
                    if self.proxy.headers:
                        headers = kwargs.get('headers', {})
                        headers.update(self.proxy.headers)
                        kwargs['headers'] = headers

                # Make HTTP request using session
                async with self.session.request(method, url, **kwargs) as response:
                    # Check if we should retry based on status code from dataclass
                    if response.status in self.retry.status and attempt < self.retry.total:
                        warnings.warn(
                            f"Request failed with status {response.status}, retrying... (attempt {attempt + 1}/{self.retry.total})")
                        # Calculate exponential backoff delay using dataclass value
                        delay = self.retry.backoff * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue

                    # Raise exception for HTTP error status codes
                    response.raise_for_status()

                    # Create response object
                    response = Response(response)

                    # Execute response hook if provided
                    if 'response' in self.hooks:
                        try:
                            await self.hooks['response'](response)
                        except Exception as error:
                            warnings.warn(f"Response hook failed: {error}")

                    return response

            except aiohttp.ClientResponseError as error:
                # Handle HTTP response errors with retry logic
                if error.status in self.retry.status and attempt < self.retry.total:
                    warnings.warn(
                        f"Request failed with status {error.status}, retrying... (attempt {attempt + 1}/{self.retry.total})")
                    # Calculate exponential backoff delay using dataclass value
                    delay = self.retry.backoff * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Log final failure
                    warnings.warn(f"Request failed with status {error.status}: {error.message}")
                    break
            except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError,
                    aiohttp.ClientProxyConnectionError) as error:
                # Handle connection, timeout, and proxy errors
                if attempt < self.retry.total:
                    if isinstance(error, aiohttp.ClientProxyConnectionError) and self.proxy:
                        warnings.warn(
                            f"Proxy connection failed to {self.proxy.host}:{self.proxy.port}, retrying... (attempt {attempt + 1}/{self.retry.total})")
                    else:
                        warnings.warn(
                            f"Request failed with {error.__class__.__name__}, retrying... (attempt {attempt + 1}/{self.retry.total})")
                    # Calculate exponential backoff delay using dataclass value
                    delay = self.retry.backoff * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Log final failure with proxy info if applicable
                    if isinstance(error, aiohttp.ClientProxyConnectionError) and self.proxy:
                        warnings.warn(f"Proxy connection failed permanently to {self.proxy.host}:{self.proxy.port}: {error}")
                    else:
                        warnings.warn(f"Request failed: {error}")
                    break
            except Exception as error:
                # Handle unexpected errors
                warnings.warn(f"An unexpected error occurred: {error}")
                break

        # Return None if all retries failed
        return None

    async def stream(self, method: str, url: str, timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                     cookies: Optional[Dict[str, str]] = None, **kwargs) -> Stream:
        """
        Send a streaming HTTP request for handling large data transfers.
        This method creates a streaming connection that can be used for uploading
        or downloading large amounts of data without loading everything into memory.
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
        if not self.session:
            raise RuntimeError("CrawlCore session is not initialized. Use it within an 'async with' block.")

        # Apply authentication
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})

        if self.auth:
            # Apply authentication headers based on type
            if isinstance(self.auth, Basic):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Bearer):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, JWT):
                headers["Authorization"] = self.auth.auth
            elif isinstance(self.auth, Key):
                if self.auth.place == "header":
                    headers[self.auth.name] = self.auth.value
                elif self.auth.place == "query":
                    params[self.auth.name] = self.auth.value
            elif isinstance(self.auth, OAuth):
                if self.auth.token:
                    headers["Authorization"] = self.auth.auth

        kwargs['headers'] = headers
        if params:
            kwargs['params'] = params

        # Merge cookies (request cookies override instance cookies)
        merged = self.cookies.copy()
        if cookies:
            merged.update(cookies)
        if merged:
            kwargs['cookies'] = merged

        # Handle timeout parameter conversion using dataclass values
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
                    sock_connect=self.timeout.connect
                )
            kwargs['timeout'] = timeout

        # Set up proxy for streaming request
        if self.proxy:
            # Validate proxy before use
            if not (bool(self.proxy.host.strip()) and
                   1 <= self.proxy.port <= 65535 and
                   (not self.proxy.username or bool(self.proxy.username.strip())) and
                   (not self.proxy.password or bool(self.proxy.password.strip()))):
                raise ValueError("Invalid proxy configuration for streaming request")

            # Generate proxy URL
            if self.proxy.username and self.proxy.password:
                kwargs['proxy'] = f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.host}:{self.proxy.port}"
            else:
                kwargs['proxy'] = f"http://{self.proxy.host}:{self.proxy.port}"

            # Add proxy headers if configured
            if self.proxy.headers:
                headers = kwargs.get('headers', {})
                headers.update(self.proxy.headers)
                kwargs['headers'] = headers

            # Log proxy usage for streaming
            if self.proxy.port == 443 or self.proxy.port == 8443:
                warnings.warn("Using secured proxy for streaming request")

        # Build full URL from endpoint and relative path
        if url.startswith('/'):
            url = self.endpoint + url

        # Execute request hook if provided
        if 'request' in self.hooks:
            try:
                await self.hooks['request'](method, url, **kwargs)
            except Exception as error:
                warnings.warn(f"Request hook failed: {error}")

        try:
            # Make streaming HTTP request
            response = await self.session.request(method, url, **kwargs)
            # Raise exception for HTTP error status codes
            response.raise_for_status()
            # Create stream wrapper
            stream = Stream(response)

            # Execute response hook if provided
            if 'response' in self.hooks:
                try:
                    await self.hooks['response'](stream)
                except Exception as error:
                    warnings.warn(f"Response hook failed: {error}")

            return stream
        except aiohttp.ClientResponseError as error:
            # Log and re-raise HTTP response errors
            warnings.warn(f"Request failed with status {error.status}: {error.message}")
            raise
        except (aiohttp.ClientConnectionError, aiohttp.ClientProxyConnectionError) as error:
            # Enhanced proxy error handling
            if isinstance(error, aiohttp.ClientProxyConnectionError) and self.proxy:
                warnings.warn(f"Proxy connection error to {self.proxy.host}:{self.proxy.port}: {error}")
            else:
                warnings.warn(f"Connection error: {error}")
            raise
        except aiohttp.ServerTimeoutError:
            # Log and re-raise timeout errors
            warnings.warn("Request timed out")
            raise
        except Exception as error:
            # Log and re-raise unexpected errors
            warnings.warn(f"An unexpected error occurred: {error}")
            raise