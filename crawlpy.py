from aiohttp import ClientSession, ClientConnectionError


class CrawlPy:
    """Class for simplified HTTP requests."""

    def __init__(self):
        """Initialize CrawlPy."""
        self.session = ClientSession()

    async def get(self, url, params=None, headers=None, cookies=None):
        """Make a GET request."""
        try:
            async with self.session.get(url, params=params, headers=headers, cookies=cookies) as response:
                return await response.text()
        except ClientConnectionError:
            print("Connection closed prematurely.")
        except Exception as error:
            print(f"An error occurred: {error}")

    async def close(self):
        """Close the session."""
        await self.session.close()
