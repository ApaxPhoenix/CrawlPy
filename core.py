import aiohttp
import asyncio
import warnings
from typing import Optional, Dict, Any, Union, Callable
from urllib.parse import urlparse
from config import Limits, Retry, Timeout, Redirects
from broadcast import Response, Stream
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth


class CrawlCore:
    """
    Asynchronous HTTP client for making web requests with comprehensive error handling,
    proxy support, SSL support, authentication, cookies, and hooks.
    This class provides a high-level interface for making HTTP requests using aiohttp.
    It supports all standard HTTP methods, file uploads, streaming, redirect handling,
    proxy support, SSL configuration, authentication, cookies, hooks, and proper session management through async context managers.
    """

    def __init__(self, endpoint: str, limits: Optional[Limits] = None,
                 timeout: Optional[Timeout] = None, retry: Optional[Retry] = None,
                 redirects: Optional[Redirects] = None, proxy: Optional[Proxy] = None,
                 ssl: Optional[SSL] = None, auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None,
                 cookies: Optional[Dict[str, str]] = None, hooks: Optional[Dict[str, Callable]] = None) -> None:
        """
        Initialize the HTTP client with a base endpoint URL and configuration.
        Args:
            endpoint: The base URL for HTTP requests (must include http:// or https://)
            limits: Connection limits configuration
            timeout: Default timeout configuration
            retry: Default retry configuration
            redirects: Redirect handling configuration
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
        # Store configuration with matching variable names
        self.endpoint = endpoint
        self.limits = limits or Limits()
        self.timeout = timeout or Timeout()
        self.retry = retry or Retry()
        self.redirects = redirects or Redirects()
        self.ssl = ssl or SSL()
        self.proxy = proxy
        self.cookies = cookies or {}
        self.hooks = hooks or {}
        self.auth = auth
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
            # Create TCP connector using the improved connector method
            connector = self.limits.connector()
            # Configure SSL context if available
            if self.ssl.context:
                connector._ssl = self.ssl.context
            # Create HTTP session with connector and default timeout
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout.convert()
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

    async def execute(self, method: str, url: str, retry: Optional[Retry] = None, **kwargs) -> Optional[Response]:
        """
        Make an HTTP request with retry logic and exponential backoff.
        This method handles retries for failed requests based on status codes
        and implements exponential backoff for rate limiting.
        Args:
            method: HTTP method to use
            url: Target URL
            retry: Retry configuration (uses default if not provided)
            **kwargs: Additional arguments for the request
        Returns:
            Optional[Response]: Response object if successful, None if failed after all retries
        """
        # Use instance retry config if none provided
        retry = retry or self.retry
        # Attempt request with retry logic
        for attempt in range(retry.total + 1):
            try:
                # Set up proxy for this attempt
                if self.proxy:
                    # Use the proxy URL method
                    kwargs['proxy'] = self.proxy.url()
                    # Add proxy headers if configured
                    if self.proxy.headers:
                        headers = kwargs.get('headers', {})
                        headers.update(self.proxy.headers)
                        kwargs['headers'] = headers
                # Make HTTP request using session
                async with self.session.request(method, url, **kwargs) as response:
                    # Check if we should retry based on status code using improved method
                    if retry.retriable(response.status) and not retry.exhausted(attempt):
                        warnings.warn(
                            f"Request failed with status {response.status}, retrying... (attempt {attempt + 1}/{retry.total})")
                        # Use improved delay calculation
                        await asyncio.sleep(retry.delay(attempt))
                        continue
                    # Raise exception for HTTP error status codes
                    response.raise_for_status()
                    return Response(response)
            except aiohttp.ClientResponseError as error:
                # Handle HTTP response errors with retry logic using improved methods
                if retry.retriable(error.status) and not retry.exhausted(attempt):
                    warnings.warn(
                        f"Request failed with status {error.status}, retrying... (attempt {attempt + 1}/{retry.total})")
                    # Use improved delay calculation
                    await asyncio.sleep(retry.delay(attempt))
                    continue
                else:
                    # Log final failure
                    warnings.warn(f"Request failed with status {error.status}: {error.message}")
                    break
            except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError,
                    aiohttp.ClientProxyConnectionError) as error:
                # Handle connection, timeout, and proxy errors
                if not retry.exhausted(attempt):
                    warnings.warn(
                        f"Request failed with {type(error).__name__}, retrying... (attempt {attempt + 1}/{retry.total})")
                    # Use improved delay calculation
                    await asyncio.sleep(retry.delay(attempt))
                    continue
                else:
                    # Log final failure
                    warnings.warn(f"Request failed: {error}")
                    break
            except Exception as error:
                # Handle unexpected errors
                warnings.warn(f"An unexpected error occurred: {error}")
                break
        # Return None if all retries failed
        return None

    async def request(self, method: str, url: str, timeout: Optional[Union[float, Timeout]] = None,
                      retry: Optional[Retry] = None, redirects: Optional[bool] = None,
                      cookies: Optional[Dict[str, str]] = None, **kwargs) -> Optional[Response]:
        """
        Send an HTTP request using the specified method and URL with comprehensive error handling.
        This is the core method that all other HTTP methods use internally.
        It handles various types of errors gracefully and provides warnings
        for debugging purposes.
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
            url: The target URL for the request
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
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

        # Apply authentication using the improved auth data classes
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})

        if self.auth:
            # Use the header() method from all auth classes
            auth_headers = self.auth.header()
            if auth_headers:
                headers.update(auth_headers)

            # Handle API key query parameters
            if isinstance(self.auth, Key):
                query_params = self.auth.query()
                if query_params:
                    params.update(query_params)

        kwargs['headers'] = headers
        if params:
            kwargs['params'] = params

        # Merge cookies (request cookies override instance cookies)
        merged_cookies = self.cookies.copy()
        if cookies:
            merged_cookies.update(cookies)
        if merged_cookies:
            kwargs['cookies'] = merged_cookies

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
            elif isinstance(timeout, Timeout):
                # Use improved convert method
                timeout = timeout.convert()
            else:
                # Use default timeout
                timeout = self.timeout.convert()
            kwargs['timeout'] = timeout
        # Handle redirect parameters using improved methods
        if redirects is not None:
            kwargs['allow_redirects'] = redirects
        # Use improved maximum redirect setting
        kwargs['max_redirects'] = self.redirects.maximum
        # Build full URL from endpoint and relative path
        if url.startswith('/'):
            url = self.endpoint + url
        # Execute request with retry logic
        response = await self.execute(method, url, retry, **kwargs)

        # Execute response hook if provided
        if response and 'response' in self.hooks:
            try:
                await self.hooks['response'](response)
            except Exception as error:
                warnings.warn(f"Response hook failed: {error}")

        return response

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None, timeout: Optional[Union[float, Timeout]] = None,
                  retry: Optional[Retry] = None, redirects: Optional[bool] = None,
                  cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a GET request to retrieve data from the specified URL.
        GET requests are used to fetch resources from the server without
        modifying server state. Query parameters can be included.
        Args:
            url: The target URL for the GET request
            params: Optional query parameters as key-value pairs
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with GET verb
        return await self.request('GET', url, params=params, headers=headers,
                                  timeout=timeout, retry=retry, redirects=redirects, cookies=cookies)

    async def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   json: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, timeout: Optional[Union[float, Timeout]] = None,
                   retry: Optional[Retry] = None, redirects: Optional[bool] = None,
                   cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a POST request to submit data to the specified URL.
        POST requests are used to create new resources or submit data to the server.
        This method handles both regular form data and file uploads automatically.
        Args:
            url: The target URL for the POST request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            files: Optional file uploads as key-value pairs
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Handle file uploads by creating multipart form data
        if files:
            # Create multipart form for file uploads
            form = aiohttp.FormData()
            # Add files first to the form data
            for key, file in files.items():
                form.add_field(key, file)
            # Add regular data fields if they exist
            if data:
                for key, value in data.items():
                    form.add_field(key, value)
            # Send request with multipart form data
            return await self.request('POST', url, data=form, headers=headers,
                                      timeout=timeout, retry=retry, redirects=redirects, cookies=cookies)
        else:
            # No files, use data or json directly
            return await self.request('POST', url, data=data, json=json, headers=headers,
                                      timeout=timeout, retry=retry, redirects=redirects, cookies=cookies)

    async def put(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                  json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[Union[float, Timeout]] = None, retry: Optional[Retry] = None,
                  redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a PUT request to update or create a resource at the specified URL.
        PUT requests are used to update existing resources or create new ones
        with a specific identifier. The request replaces the entire resource.
        Args:
            url: The target URL for the PUT request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with PUT verb
        return await self.request('PUT', url, data=data, json=json, headers=headers,
                                  timeout=timeout, retry=retry, redirects=redirects, cookies=cookies)

    async def patch(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                    json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                    timeout: Optional[Union[float, Timeout]] = None, retry: Optional[Retry] = None,
                    redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a PATCH request to partially update a resource at the specified URL.
        PATCH requests are used to make partial updates to existing resources,
        unlike PUT which replaces the entire resource.
        Args:
            url: The target URL for the PATCH request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with PATCH verb
        return await self.request('PATCH', url, data=data, json=json, headers=headers,
                                  timeout=timeout, retry=retry, redirects=redirects, cookies=cookies)

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[Union[float, Timeout]] = None, retry: Optional[Retry] = None,
                     redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a DELETE request to remove a resource at the specified URL.
        DELETE requests are used to remove resources from the server.
        Args:
            url: The target URL for the DELETE request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with DELETE verb
        return await self.request('DELETE', url, headers=headers, timeout=timeout,
                                  retry=retry, redirects=redirects, cookies=cookies)

    async def head(self, url: str, headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[Union[float, Timeout]] = None, retry: Optional[Retry] = None,
                   redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a HEAD request to retrieve headers from the specified URL.
        HEAD requests are used to fetch response headers without the response body.
        Args:
            url: The target URL for the HEAD request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with HEAD verb
        return await self.request('HEAD', url, headers=headers, timeout=timeout,
                                  retry=retry, redirects=redirects, cookies=cookies)

    async def options(self, url: str, headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[Union[float, Timeout]] = None, retry: Optional[Retry] = None,
                      redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send an OPTIONS request to retrieve allowed methods for the specified URL.
        OPTIONS requests are used to check what HTTP methods are supported.
        Args:
            url: The target URL for the OPTIONS request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
            retry: Retry configuration for this request
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with OPTIONS verb
        return await self.request('OPTIONS', url, headers=headers, timeout=timeout,
                                  retry=retry, redirects=redirects, cookies=cookies)

    async def stream(self, method: str, url: str, timeout: Optional[Union[float, Timeout]] = None,
                     cookies: Optional[Dict[str, str]] = None, **kwargs) -> Stream:
        """
        Send a streaming HTTP request for handling large data transfers.
        This method creates a streaming connection that can be used for uploading
        or downloading large amounts of data without loading everything into memory.
        Args:
            method: HTTP method for the streaming request
            url: The target URL for the streaming request
            timeout: Request timeout (float for simple timeout, Timeout object for detailed control)
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

        # Apply authentication using the improved auth data classes
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})

        if self.auth:
            # Use the header() method from all auth classes
            auth_headers = self.auth.header()
            if auth_headers:
                headers.update(auth_headers)

            # Handle API key query parameters
            if isinstance(self.auth, Key):
                query_params = self.auth.query()
                if query_params:
                    params.update(query_params)

        kwargs['headers'] = headers
        if params:
            kwargs['params'] = params

        # Merge cookies (request cookies override instance cookies)
        merged_cookies = self.cookies.copy()
        if cookies:
            merged_cookies.update(cookies)
        if merged_cookies:
            kwargs['cookies'] = merged_cookies

        # Handle timeout parameter conversion
        if timeout is not None:
            if isinstance(timeout, (int, float)):
                # Convert simple timeout to ClientTimeout
                timeout = aiohttp.ClientTimeout(total=timeout)
            elif isinstance(timeout, Timeout):
                # Use improved convert method
                timeout = timeout.convert()
            else:
                # Use default timeout
                timeout = self.timeout.convert()
            kwargs['timeout'] = timeout
        # Set up proxy for streaming request
        if self.proxy:
            # Use the improved proxy URL method
            kwargs['proxy'] = self.proxy.url()
            # Add proxy headers if configured
            if self.proxy.headers:
                headers = kwargs.get('headers', {})
                headers.update(self.proxy.headers)
                kwargs['headers'] = headers
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
            # Log and re-raise connection errors
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