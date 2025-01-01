import aiohttp
import warnings
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class CrawlCore:
    """
    Asynchronous HTTP client for managing connections and requests.
    Supports multiple HTTP methods like GET, POST, PUT, DELETE with headers, JSON data, and more.

    This class manages the connection session, handles timeout, and manages proxies, SSL settings, and cookies.
    """

    def __init__(self, endpoint: str, duration: Optional[float] = 10, proxy: Optional[Dict] = None,
                 ssl: Optional[bool] = None, cookies: Optional[aiohttp.CookieJar] = None) -> None:
        """
        Initialize the HTTP client with an endpoint, timeout, and optional proxy settings, SSL, and cookie jar.

        Args:
            endpoint (str): The full URL for the HTTP connection, including the protocol (http/https).
            duration (Optional[float], optional): Connection timeout in seconds, default is 10 seconds.
            proxy (Optional[Dict], optional): Proxy configuration, default is None.
            ssl (Optional[bool], optional): SSL configuration, default is None.
            cookies (Optional[aiohttp.CookieJar], optional): Cookie jar configuration, default is None.
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.proxy = proxy
        self.endpoint = endpoint
        self.duration = duration
        self.ssl = ssl
        self.cookies = cookies

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
            exc_type (type): Exception type, if any.
            exc_val (Exception): Exception value, if any.
            exc_tb (traceback): Traceback of the exception, if any.
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[str]:
        """
        Send an HTTP request using the specified method and URL.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The full URL for the request.

        Returns:
            Optional[str]: The response text if the request succeeds, otherwise None.
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
