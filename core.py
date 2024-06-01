import re
import aiohttp
from urllib.parse import urlparse


class HTTPClient:
    """Class for managing HTTP connections."""

    def __init__(self, proxies=None):
        """Initialize HTTPClient with optional proxies."""
        self.session = None
        self.proxies = proxies

    async def connect(self, url, timeout=60):
        """Establish a connection to the given URL."""
        if not self.session:
            url_obj = urlparse(url)
            scheme = url_obj.scheme.lower()
            if scheme not in ['http', 'https']:
                raise ValueError("Only HTTP and HTTPS protocols are supported.")
            connector = aiohttp.TCPConnector(ssl=scheme == 'https')
            timeout_settings = aiohttp.ClientTimeout(total=timeout)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout_settings)

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None