from typing import Optional, Dict, Any, Union, List
from core import CrawlCore
from config import Limits, Retry, Timeout, Redirects
from settings import SSL, Proxy
from broadcast import Response, Stream


class Session(CrawlCore):
    """
    A high-level HTTP session manager that extends CrawlCore with persistent headers
    and simplified configuration management.
    """

    def __init__(self, endpoint: str,
                 limits: Optional[Limits] = None,
                 timeout: Optional[Timeout] = None,
                 retry: Optional[Retry] = None,
                 redirects: Optional[Redirects] = None,
                 proxies: Optional[Union[Proxy, List[Proxy]]] = None,
                 ssl: Optional[SSL] = None,
                 headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize a new HTTP session with optional configuration.

        Args:
            endpoint: The base URL for HTTP requests (must include http:// or https://)
            limits: Connection limits configuration
            timeout: Default timeout configuration
            retry: Default retry configuration
            redirects: Redirect handling configuration
            proxies: Single proxy or list of proxies for rotation
            ssl: SSL/TLS configuration
            headers: Default headers to include with all requests

        Raises:
            TypeError: If endpoint is not a string
            ValueError: If endpoint doesn't start with http:// or https://
        """
        super().__init__(
            endpoint=endpoint,
            limits=limits,
            timeout=timeout,
            retry=retry,
            redirects=redirects,
            proxies=proxies,
            ssl=ssl
        )

        self.headers: Dict[str, str] = headers or {}

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[Union[float, Timeout]] = None,
                  retry: Optional[Retry] = None,
                  redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a GET request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().get(url, params=params, headers=merged,
                                 timeout=timeout, retry=retry, redirects=redirects)

    async def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   json: Optional[Dict[str, Any]] = None,
                   files: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[Union[float, Timeout]] = None,
                   retry: Optional[Retry] = None,
                   redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a POST request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().post(url, data=data, json=json, files=files,
                                  headers=merged, timeout=timeout,
                                  retry=retry, redirects=redirects)

    async def put(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                  json: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[Union[float, Timeout]] = None,
                  retry: Optional[Retry] = None,
                  redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a PUT request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().put(url, data=data, json=json, headers=merged,
                                 timeout=timeout, retry=retry, redirects=redirects)

    async def patch(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                    json: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    timeout: Optional[Union[float, Timeout]] = None,
                    retry: Optional[Retry] = None,
                    redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a PATCH request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().patch(url, data=data, json=json, headers=merged,
                                   timeout=timeout, retry=retry, redirects=redirects)

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None,
                     timeout: Optional[Union[float, Timeout]] = None,
                     retry: Optional[Retry] = None,
                     redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a DELETE request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().delete(url, headers=merged, timeout=timeout,
                                    retry=retry, redirects=redirects)

    async def head(self, url: str, headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[Union[float, Timeout]] = None,
                   retry: Optional[Retry] = None,
                   redirects: Optional[bool] = None) -> Optional[Response]:
        """Send a HEAD request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().head(url, headers=merged, timeout=timeout,
                                  retry=retry, redirects=redirects)

    async def options(self, url: str, headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[Union[float, Timeout]] = None,
                      retry: Optional[Retry] = None,
                      redirects: Optional[bool] = None) -> Optional[Response]:
        """Send an OPTIONS request with session headers automatically merged."""
        merged = self.headers.copy()
        if headers:
            merged.update(headers)
        return await super().options(url, headers=merged, timeout=timeout,
                                     retry=retry, redirects=redirects)

    async def stream(self, method: str, url: str,
                     timeout: Optional[Union[float, Timeout]] = None,
                     **kwargs) -> Stream:
        """Send a streaming HTTP request with session headers automatically merged."""
        if 'headers' in kwargs:
            merged = self.headers.copy()
            merged.update(kwargs['headers'])
            kwargs['headers'] = merged
        else:
            kwargs['headers'] = self.headers.copy()

        return await super().stream(method, url, timeout=timeout, **kwargs)