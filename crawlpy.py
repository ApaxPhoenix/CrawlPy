import warnings
from typing import Optional, Any, Dict
from .core import CrawlCore


class CrawlPy:
    """
    A requests-like HTTP client wrapper for CrawlCore.
    Provides simple methods for making HTTP requests with a familiar interface.

    This class implements all standard HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE)
    and follows a similar pattern to the popular 'requests' library for ease of use.
    """

    def __init__(self, endpoint: Optional[str] = None, duration: Optional[float] = 10,
                 proxy: Optional[dict] = None, ssl: Optional[bool] = None,
                 cookies: Optional[Any] = None) -> None:
        """
        Initialize CrawlPy with optional base URL and configurations.

        Args:
            endpoint (Optional[str]): Base URL for all requests. If provided, will be prepended to all request URLs
            duration (Optional[float]): Connection timeout in seconds (default: 10)
            proxy (Optional[dict]): Proxy configuration dictionary for proxy server settings
            ssl (Optional[bool]): SSL verification settings. Set to False to disable SSL verification
            cookies (Optional[Any]): Cookie configuration for maintaining session state
        """
        self.client: Optional[CrawlCore] = None
        self.endpoint = endpoint
        self.duration = duration
        self.proxy = proxy
        self.ssl = ssl
        self.cookies = cookies

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[str]:
        """
        Core method to send HTTP requests. All other HTTP method helpers delegate to this method.

        Handles the creation and lifecycle of the CrawlCore client, URL path joining,
        and error handling for all requests.

        Args:
            method (str): HTTP method to use (GET, POST, etc.)
            url (str): URL or endpoint for the request
            **kwargs: Additional arguments to pass to the underlying request

        Returns:
            Optional[str]: Response text if successful, None if the request fails
        """
        try:
            # Join endpoint and URL if endpoint is provided
            path = f"{self.endpoint.rstrip('/')}/{url.lstrip('/')}" if self.endpoint else url

            # Create new CrawlCore instance with configured settings
            self.client = CrawlCore(self.endpoint or url, self.duration, self.proxy, self.ssl, self.cookies)

            # Use context manager to ensure proper client cleanup
            async with self.client:
                return await self.client.request(method, path, **kwargs)
        except Exception as error:
            warnings.warn(f"Request failed: {error}")
            return None

    async def get(self, url: str, params: Optional[Dict] = None, **kwargs: Any) -> Optional[str]:
        """
        Send a GET request.

        Args:
            url (str): URL or endpoint for the request
            params (Optional[Dict]): Query parameters to append to the URL
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text if successful, None otherwise
        """
        kwargs['params'] = params
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, data: Optional[Any] = None,
                   json: Optional[Dict] = None, **kwargs: Any) -> Optional[str]:
        """
        Send a POST request.

        Args:
            url (str): URL or endpoint for the request
            data (Optional[Any]): Form-encoded data to send in the request body
            json (Optional[Dict]): JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text if successful, None otherwise
        """
        kwargs['data'] = data
        kwargs['json'] = json
        return await self.request('POST', url, **kwargs)

    async def put(self, url: str, data: Optional[Any] = None,
                  json: Optional[Dict] = None, **kwargs: Any) -> Optional[str]:
        """
        Send a PUT request.

        Args:
            url (str): URL or endpoint for the request
            data (Optional[Any]): Form-encoded data to send in the request body
            json (Optional[Dict]): JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text if successful, None otherwise
        """
        kwargs['data'] = data
        kwargs['json'] = json
        return await self.request('PUT', url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send a DELETE request.

        Args:
            url (str): URL or endpoint for the request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text if successful, None otherwise
        """
        return await self.request('DELETE', url, **kwargs)

    async def patch(self, url: str, data: Optional[Any] = None,
                    json: Optional[Dict] = None, **kwargs: Any) -> Optional[str]:
        """
        Send a PATCH request.

        Args:
            url (str): URL or endpoint for the request
            data (Optional[Any]): Form-encoded data to send in the request body
            json (Optional[Dict]): JSON data to send in the request body
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text if successful, None otherwise
        """
        kwargs['data'] = data
        kwargs['json'] = json
        return await self.request('PATCH', url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send a HEAD request. Similar to GET but returns only headers, no body.

        Args:
            url (str): URL or endpoint for the request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response headers if successful, None otherwise
        """
        return await self.request('HEAD', url, **kwargs)

    async def options(self, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send an OPTIONS request. Used to describe the communication options for the target resource.

        Args:
            url (str): URL or endpoint for the request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text containing allowed methods and other options
        """
        return await self.request('OPTIONS', url, **kwargs)

    async def trace(self, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send a TRACE request. Used to perform a message loop-back test along the path to the target resource.

        Args:
            url (str): URL or endpoint for the request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Optional[str]: Response text containing the TRACE message
        """
        return await self.request('TRACE', url, **kwargs)