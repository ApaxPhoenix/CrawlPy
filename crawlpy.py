import aiohttp
import warnings
from typing import Optional, Any, Dict, Union
from core import CrawlCore
from config import Limits, Retry, Timeout, Redirects
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth
from broadcast import Response, Stream


class CrawlPy:
    """
    A requests-like HTTP client wrapper for CrawlCore.
    Provides simple methods for making HTTP requests with a familiar interface.

    This class implements all standard HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
    and follows a similar pattern to the popular 'requests' library for ease of use.

    Supports both single-use requests and persistent client usage.
    """

    def __init__(self, endpoint: Optional[str] = None,
                 limits: Optional[Limits] = None,
                 timeout: Optional[Timeout] = None,
                 retry: Optional[Retry] = None,
                 redirects: Optional[Redirects] = None,
                 proxy: Optional[Proxy] = None,
                 ssl: Optional[SSL] = None,
                 auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None,
                 cookies: Optional[Dict[str, str]] = None,
                 hooks: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize CrawlPy with optional base URL and configurations.

        Args:
            endpoint: Base URL for all requests. If provided, will be prepended to all request URLs
            limits: Connection limits configuration
            timeout: Timeout configuration for requests
            retry: Retry configuration for failed requests
            redirects: Redirect handling configuration
            proxy: Proxy configuration for requests
            ssl: SSL/TLS configuration
            auth: Authentication configuration (Basic, Bearer, JWT, Key, or OAuth)
            cookies: Default cookies as key-value pairs
            hooks: Request/response hooks {"request": callable, "response": callable}
        """
        self.core: Optional[CrawlCore] = None
        self.endpoint = endpoint
        self.limits = limits
        self.timeout = timeout
        self.retry = retry
        self.redirects = redirects
        self.proxy = proxy
        self.ssl = ssl
        self.auth = auth
        self.cookies = cookies
        self.hooks = hooks

    async def __aenter__(self) -> "CrawlPy":
        """Enter async context manager for persistent client usage."""
        if not self.core and self.endpoint:
            self.core = CrawlCore(
                endpoint=self.endpoint,
                limits=self.limits,
                timeout=self.timeout,
                retry=self.retry,
                redirects=self.redirects,
                proxy=self.proxy,
                ssl=self.ssl,
                auth=self.auth,
                cookies=self.cookies,
                hooks=self.hooks
            )
            await self.core.__aenter__()
        return self

    async def __aexit__(self, t, v, tb):
        """Exit async context manager and cleanup client."""
        if self.core:
            await self.core.__aexit__(t, v, tb)
            self.core = None

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[Response]:
        """
        Core method to send HTTP requests. All other HTTP method helpers delegate to this method.

        Handles the creation and lifecycle of the CrawlCore client, URL path joining,
        and error handling for all requests.

        Args:
            method: HTTP method to use (GET, POST, etc.)
            url: URL or endpoint for the request
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            Optional[Response]: Response object if successful, None if the request fails
        """
        try:
            # If we have a persistent client, use it
            if self.core:
                return await self.core.request(method, url, **kwargs)

            # Otherwise, create a temporary client for this request
            # Determine the endpoint - use provided endpoint or extract from URL
            if self.endpoint:
                endpoint = self.endpoint
                path = url
            else:
                # Extract endpoint from URL for temporary client
                from urllib.parse import urlparse
                parsed = urlparse(url)
                endpoint = f"{parsed.scheme}://{parsed.netloc}"
                path = url

            # Create temporary CrawlCore instance
            core = CrawlCore(
                endpoint=endpoint,
                limits=self.limits,
                timeout=self.timeout,
                retry=self.retry,
                redirects=self.redirects,
                proxy=self.proxy,
                ssl=self.ssl,
                auth=self.auth,
                cookies=self.cookies,
                hooks=self.hooks
            )

            # Use context manager to ensure proper cleanup
            async with core as context:
                return await context.request(method, path, **kwargs)

        except Exception as error:
            warnings.warn(f"Request failed: {error}")
            return None

    async def stream(self, method: str, url: str,
                     headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                     cookies: Optional[Dict[str, str]] = None,
                     **kwargs: Any) -> Optional[Stream]:
        """
        Send a streaming HTTP request for handling large data transfers.

        This method creates a streaming connection that can be used for uploading
        or downloading large amounts of data without loading everything into memory.

        Args:
            method: HTTP method for the streaming request (GET, POST, etc.)
            url: The target URL for the streaming request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            cookies: Optional cookies as key-value pairs
            **kwargs: Additional arguments to pass to the underlying stream request

        Returns:
            Optional[Stream]: Stream object if successful, None if the request fails
        """
        try:
            # If we have a persistent client, use it
            if self.core:
                return await self.core.stream(method, url, timeout=timeout,
                                              cookies=cookies, headers=headers, **kwargs)

            # Otherwise, create a temporary client for this request
            # Determine the endpoint - use provided endpoint or extract from URL
            if self.endpoint:
                endpoint = self.endpoint
                path = url
            else:
                # Extract endpoint from URL for temporary client
                from urllib.parse import urlparse
                parsed = urlparse(url)
                endpoint = f"{parsed.scheme}://{parsed.netloc}"
                path = url

            # Create temporary CrawlCore instance
            core = CrawlCore(
                endpoint=endpoint,
                limits=self.limits,
                timeout=self.timeout,
                retry=self.retry,
                redirects=self.redirects,
                proxy=self.proxy,
                ssl=self.ssl,
                auth=self.auth,
                cookies=self.cookies,
                hooks=self.hooks
            )

            # Use context manager to ensure proper cleanup
            async with core as context:
                return await context.stream(method, path, timeout=timeout,
                                            cookies=cookies, headers=headers, **kwargs)

        except Exception as error:
            warnings.warn(f"Stream request failed: {error}")
            return None

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                  redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a GET request to retrieve data from the specified URL.
        GET requests are used to fetch resources from the server without
        modifying server state. Query parameters can be included.
        Args:
            url: The target URL for the GET request
            params: Optional query parameters as key-value pairs
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with GET verb
        return await self.request('GET', url, params=params, headers=headers,
                                  timeout=timeout, redirects=redirects, cookies=cookies)

    async def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   json: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                   redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
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
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
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
                                      timeout=timeout, redirects=redirects, cookies=cookies)
        else:
            # No files, use data or json directly
            return await self.request('POST', url, data=data, json=json, headers=headers,
                                      timeout=timeout, redirects=redirects, cookies=cookies)

    async def put(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                  json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
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
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with PUT verb
        return await self.request('PUT', url, data=data, json=json, headers=headers,
                                  timeout=timeout, redirects=redirects, cookies=cookies)

    async def patch(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                    json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                    timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
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
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with PATCH verb
        return await self.request('PATCH', url, data=data, json=json, headers=headers,
                                  timeout=timeout, redirects=redirects, cookies=cookies)

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                     redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a DELETE request to remove a resource at the specified URL.
        DELETE requests are used to remove resources from the server.
        Args:
            url: The target URL for the DELETE request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with DELETE verb
        return await self.request('DELETE', url, headers=headers, timeout=timeout,
                                  redirects=redirects, cookies=cookies)

    async def head(self, url: str, headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                   redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send a HEAD request to retrieve headers from the specified URL.
        HEAD requests are used to fetch response headers without the response body.
        Args:
            url: The target URL for the HEAD request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with HEAD verb
        return await self.request('HEAD', url, headers=headers, timeout=timeout,
                                  redirects=redirects, cookies=cookies)

    async def options(self, url: str, headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
                      redirects: Optional[bool] = None, cookies: Optional[Dict[str, str]] = None) -> Optional[Response]:
        """
        Send an OPTIONS request to retrieve allowed methods for the specified URL.
        OPTIONS requests are used to check what HTTP methods are supported.
        Args:
            url: The target URL for the OPTIONS request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs
        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        # Delegate to main request method with OPTIONS verb
        return await self.request('OPTIONS', url, headers=headers, timeout=timeout,
                                  redirects=redirects, cookies=cookies)