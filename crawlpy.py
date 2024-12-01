import warnings
from typing import Optional, Dict, Any
from core import HTTPClient, aiohttp

class CrawlPy:
    """Class for simplified HTTP requests."""

    def __init__(self) -> None:
        """Initialize CrawlPy."""
        self.client: Optional[HTTPClient] = None

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Make a GET request."""
        try:
            # Use the context manager to ensure the HTTP client is managed correctly
            async with HTTPClient(url) as self.client:
                # Perform the GET request
                response = await self.client.session.get(url, params=params, headers=headers, cookies=cookies)
                return await response.text()
        except aiohttp.ClientConnectionError:
            warnings.warn("Connection closed prematurely.")
        except Exception as error:
            warnings.warn(f"An error occurred: {error}")
        finally:
            # No need to explicitly close the session when using the context manager
            pass  # Context manager will handle session closure