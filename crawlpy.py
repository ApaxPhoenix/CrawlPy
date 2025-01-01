import warnings
from typing import Optional, Any
from core import CrawlCore


class CrawlPy:
    """
    Wrapper class for performing HTTP requests using CrawlCore.
    Allows sending dynamic HTTP requests (GET, POST, PUT, DELETE) based on the provided method and URL.
    """

    def __init__(self, endpoint: Optional[str] = None, duration: Optional[float] = 10,
                 proxy: Optional[dict] = None, ssl: Optional[bool] = None,
                 cookies: Optional[Any] = None) -> None:
        """
        Initialize CrawlPy with optional base URL and configurations.

        Args:
            endpoint (Optional[str], optional): The full base URL or endpoint for the client.
            duration (Optional[float], optional): Connection timeout in seconds, default is 10 seconds.
            proxy (Optional[dict], optional): Proxy configuration, default is None.
            ssl (Optional[bool], optional): SSL configuration, default is None.
            cookies (Optional[Any], optional): Cookie configuration, default is None.
        """
        self.client: Optional[CrawlCore] = None
        self.endpoint = endpoint
        self.duration = duration
        self.proxy = proxy
        self.ssl = ssl
        self.cookies = cookies

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send an HTTP request dynamically using the provided method and URL.

        This method delegates the HTTP request to CrawlCore for actual communication with the server.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The full URL or endpoint to which the request should be sent.

        Returns:
            Optional[str]: The response text if the request succeeds, otherwise None.
        """
        try:
            # Combine endpoint and URL using path joining
            path = f"{self.endpoint.rstrip('/')}/{url.lstrip('/')}" if self.endpoint else url

            # Initialize the CrawlCore client with configuration options
            self.client = CrawlCore(self.endpoint or url, self.duration, self.proxy, self.ssl, self.cookies)

            # Use the context manager to ensure the client session is handled properly
            async with self.client:
                # Forward the request to CrawlCore's request method
                response = await self.client.request(method, path, **kwargs)
                return response
        except Exception as error:
            warnings.warn(f"An error occurred while sending the request: {error}")
        return None