import aiohttp
import warnings
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class CrawlCore:
    def __init__(self, endpoint: str, duration: Optional[float] = 10,
                 proxy: Optional[Dict] = None, ssl: Optional[bool] = None,
                 cookies: Optional[aiohttp.CookieJar] = None) -> None:
        """
        Initialize the HTTP client with an endpoint, timeout, and optional proxy settings, SSL, and cookie jar.

        Args:
            endpoint (str): The full URL for the HTTP connection, including the protocol (http/https)
            duration (Optional[float]): Connection timeout in seconds, default is 10 seconds
            proxy (Optional[Dict]): Proxy configuration, default is None
            ssl (Optional[bool]): SSL verification configuration, default is None
            cookies (Optional[aiohttp.CookieJar]): Cookie jar configuration, default is None

        Raises:
            ValueError: If endpoint doesn't start with 'http' or 'https'
            ValueError: If duration is negative
        """
        if not isinstance(endpoint, str):
            raise TypeError("Endpoint must be a string.")
        if not urlparse(endpoint).scheme in {'http', 'https'}:
            raise ValueError("Endpoint must start with 'http' or 'https'.")
        if not isinstance(duration, (int, float)) or duration <= 0:
            raise ValueError("Duration must be a positive number.")
        if proxy and not isinstance(proxy, dict):
            raise TypeError("Proxy must be a dictionary or None.")
        if cookies and not isinstance(cookies, aiohttp.CookieJar):
            raise TypeError("Cookies must be an instance of aiohttp.CookieJar or None.")

        self.endpoint = endpoint
        self.duration = duration
        self.proxy = proxy
        self.ssl = ssl
        self.cookies = cookies
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "CrawlCore":
        """
        Asynchronously enters the context for managing the HTTP client session.

        Sets up an HTTP session using aiohttp.ClientSession with proper configuration (including proxy, SSL, and cookies).

        Returns:
            CrawlCore: The instance of the CrawlCore HTTP client.
        """
        if not self.session:
            parse = urlparse(self.endpoint)
            protocol = parse.scheme.lower()

            if protocol not in ['http', 'https']:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")

            connector = aiohttp.TCPConnector(ssl=self.ssl if self.ssl is not None else protocol == 'https')

            # Create a new aiohttp session with the provided cookie jar
            self.session = aiohttp.ClientSession(
                connector=connector,
                trust_env=False,
                cookie_jar=self.cookies
            )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Asynchronously exits the context and closes the session.

        Args:
            exc_type (type): Exception type, if any
            exc_val (Exception): Exception value, if any
            exc_tb (traceback): Traceback of the exception, if any
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send an HTTP request using the specified method and URL.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD')
            url (str): The full URL for the request
            **kwargs: Additional arguments to pass to the request method

        Returns:
            Optional[str]: The response text if the request succeeds, otherwise None
        """
        if not self.session:
            raise RuntimeError("CrawlCore session is not initialized. Use it within an 'async with' block.")

        try:
            # Perform the HTTP request
            response = await self.session.request(method, url, proxy=self.proxy, **kwargs)
            response.raise_for_status()  # Raise for bad responses (non-2xx)

            # Return the response text
            return await response.text()
        except aiohttp.ClientResponseError as error:
            warnings.warn(f"Request failed with status {error.status}: {error.message}")
        except aiohttp.ClientConnectionError:
            warnings.warn("Connection closed prematurely.")
        except Exception as error:
            warnings.warn(f"An unexpected error occurred: {error}")
        return None