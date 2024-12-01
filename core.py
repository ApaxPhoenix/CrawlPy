import aiohttp
from urllib.parse import urlparse
from typing import Optional, Union


class HTTPClient:
    """Class for managing HTTP connections."""

    def __init__(self, url: str, timeout: Union[int, float] = 10, proxies: Optional[dict] = None):
        """
        Initialize HTTPClient with optional proxies, URL, and timeout.

        Args:
            url (str): The URL for the HTTP connection.
            timeout (Union[int, float], optional): The timeout for the connection, default is 10 seconds.
            proxies (Optional[dict], optional): Proxy configuration, default is None.
        """
        # Initialize session, proxies, URL, and timeout for the HTTPClient
        self.session: Optional[aiohttp.ClientSession] = None
        self.proxies = proxies
        self.url = url
        self.timeout = timeout

    async def __aenter__(self) -> "HTTPClient":
        """
        Enter asynchronous context for using HTTPClient.

        Initializes the session and sets up the connector if not already initialized.

        Returns:
            HTTPClient: The current instance of the HTTPClient.
        """
        # Check if the session is already initialized
        if not self.session:
            # Parse the URL to extract the scheme (protocol like 'http' or 'https')
            parse = urlparse(self.url)
            scheme = parse.scheme.lower()

            # Check if the scheme is valid (either 'http' or 'https')
            if scheme not in ['http', 'https']:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")

            # Initialize a TCPConnector with SSL enabled if 'https' is used
            connector = aiohttp.TCPConnector(ssl=scheme == 'https')

            # Set the timeout for the connection, using the provided timeout value
            timeout_settings = aiohttp.ClientTimeout(total=self.timeout)

            # Create a new aiohttp session with the given connector and timeout settings
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout_settings, trust_env=False)

        # Return the current instance of HTTPClient for use in the context
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit asynchronous context and close session.

        Ensures that the session is properly closed when exiting the context.

        Args:
            exc_type (type): Exception type, if any.
            exc_val (Exception): Exception value, if any.
            exc_tb (traceback): Traceback of the exception, if any.
        """
        # If the session was initialized, close it
        if self.session:
            await self.session.close()
            self.session = None
