from .core import HTTPClient, aiohttp
from .utils import Retriever, Selector

class CrawlPy:
    """Class for simplified HTTP requests."""

    def __init__(self):
        """Initialize CrawlPy."""
        self.http_client = HTTPClient()
        self.Retriever = Retriever
        self.Selector = Selector

    async def get(self, url, params=None, headers=None, cookies=None):
        """Make a GET request."""
        try:
            await self.http_client.connect(url)
            async with self.http_client.session.get(url, params=params, headers=headers, cookies=cookies) as response:
                return await response.text()
        except aiohttp.ClientConnectionError:
            print("Connection closed prematurely.")
        except Exception as error:
            print(f"An error occurred: {error}")
        finally:
            await self.http_client.close()

    async def close(self):
        """Close the HTTP client session."""
        await self.http_client.close()
