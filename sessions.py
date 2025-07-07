from typing import Optional, Dict, Any, Union, Callable
from core import CrawlCore
from config import Limits, Retry, Timeout, Redirects
from settings import SSL, Proxy
from broadcast import Response, Stream
from auth import Basic, Bearer, JWT, Key, OAuth
from adapters import HTTPAdapter


class Session(CrawlCore):
    """High-level HTTP session manager with persistent config and adapters.

    This class provides a session-based HTTP client that maintains persistent
    configuration, headers, and adapters across multiple requests. It extends
    CrawlCore to provide additional session management capabilities.

    Attributes:
        headers: Dictionary of default headers for all requests.
        verify: Boolean flag for SSL certificate verification.
        adapters: Dictionary mapping URL prefixes to HTTPAdapter instances.
    """

    def __init__(
            self,
            endpoint: str,
            limits: Optional[Limits] = None,
            timeout: Optional[Timeout] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[Redirects] = None,
            proxy: Optional[Proxy] = None,
            ssl: Optional[SSL] = None,
            auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None,
            hooks: Optional[Dict[str, Callable[..., Any]]] = None,
            headers: Optional[Dict[str, str]] = None,
            verify: bool = True,
    ) -> None:
        """Initialize HTTP session with configuration options.

        Args:
            endpoint: Base URL endpoint for the session.
            limits: Rate limiting configuration.
            timeout: Request timeout settings.
            retry: Retry policy configuration.
            redirects: Redirect handling configuration.
            proxy: Proxy server settings.
            ssl: SSL/TLS configuration.
            auth: Authentication credentials.
            hooks: Event hooks for request/response processing.
            headers: Default headers to include in all requests.
            verify: Whether to verify SSL certificates.

        Returns:
            None
        """
        # Initialize parent class with core HTTP configuration
        super().__init__(
            endpoint=endpoint,
            limits=limits,
            timeout=timeout,
            retry=retry,
            redirects=redirects,
            proxy=proxy,
            ssl=ssl,
            auth=auth,
            hooks=hooks
        )

        # Initialize session-specific attributes
        self.headers: Dict[str, str] = headers or {}
        self.verify: bool = verify
        self.adapters: Dict[str, HTTPAdapter] = {}

        # Mount default HTTP and HTTPS adapters
        # These handle the standard HTTP protocols
        self.mount('http://', HTTPAdapter())
        self.mount('https://', HTTPAdapter())

    def mount(self, prefix: str, adapter: HTTPAdapter) -> None:
        """Mount an adapter for handling URLs with a specific prefix.

        Adapters are used to customize request handling for different URL patterns.
        They are sorted by prefix length (longest first) to ensure most specific
        matches are tried first.

        Args:
            prefix: URL prefix to match (e.g., 'https://api.example.com/').
            adapter: HTTPAdapter instance to handle matching URLs.

        Returns:
            None
        """
        # Store the adapter for this prefix
        self.adapters[prefix] = adapter

        # Sort adapters by prefix length (descending) to ensure
        # longest/most specific prefixes are matched first
        self.adapters = dict(
            sorted(self.adapters.items(), key=lambda x: len(x[0]), reverse=True)
        )

    def adapter(self, url: str) -> HTTPAdapter:
        """Get the appropriate adapter for a given URL.

        Searches through mounted adapters to find the one with the longest
        matching prefix. If no adapter matches, returns a default HTTPAdapter.

        Args:
            url: The URL to find an adapter for.

        Returns:
            HTTPAdapter instance to handle the URL.
        """
        # Search through adapters for the longest matching prefix
        for prefix, adapter in self.adapters.items():
            if url.startswith(prefix):
                return adapter

        # Return default adapter if no prefix matches
        return HTTPAdapter()

    def merge(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """Merge adapter configuration with request parameters.

        This method combines configuration from three sources in order of precedence:
        1. Request-specific parameters (highest priority)
        2. Adapter configuration (medium priority)
        3. Session defaults (lowest priority)

        Args:
            url: URL to get adapter configuration for.
            **kwargs: Request-specific parameters.

        Returns:
            Dictionary containing merged configuration parameters.
        """
        # Get the appropriate adapter for this URL
        adapter = self.adapter(url)
        merged = kwargs.copy()

        # Merge adapter configuration if not overridden by request params
        if adapter.timeout and 'timeout' not in merged:
            merged['timeout'] = adapter.timeout

        if adapter.retry and 'retry' not in merged:
            merged['retry'] = adapter.retry

        if adapter.proxy and 'proxy' not in merged:
            merged['proxy'] = adapter.proxy

        if adapter.ssl and 'ssl' not in merged:
            merged['ssl'] = adapter.ssl

        if adapter.auth and 'auth' not in merged:
            merged['auth'] = adapter.auth

        # Merge headers with precedence: request > adapter > session
        headers = self.headers.copy()  # Start with session headers
        if adapter.headers:
            headers.update(adapter.headers)  # Add adapter headers
        if 'headers' in merged:
            headers.update(merged['headers'])  # Add request headers
        merged['headers'] = headers

        return merged

    async def get(
            self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP GET request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            params: Query parameters to include in the request.
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, params=params, headers=headers)

        # Delegate to parent class implementation
        return await super().get(url, **merged)

    async def post(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP POST request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            data: Form data or raw string data to send.
            json: JSON data to send (takes precedence over data).
            files: Files to upload.
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, data=data, json=json, files=files, headers=headers)

        # Delegate to parent class implementation
        return await super().post(url, **merged)

    async def put(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP PUT request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            data: Form data or raw string data to send.
            json: JSON data to send (takes precedence over data).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, data=data, json=json, headers=headers)

        # Delegate to parent class implementation
        return await super().put(url, **merged)

    async def patch(
            self,
            url: str,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP PATCH request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            data: Form data or raw string data to send.
            json: JSON data to send (takes precedence over data).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, data=data, json=json, headers=headers)

        # Delegate to parent class implementation
        return await super().patch(url, **merged)

    async def delete(
            self,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP DELETE request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, headers=headers)

        # Delegate to parent class implementation
        return await super().delete(url, **merged)

    async def head(
            self,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP HEAD request.

        HEAD requests are like GET requests but only return headers,
        not the response body. Useful for checking if resources exist.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, headers=headers)

        # Delegate to parent class implementation
        return await super().head(url, **merged)

    async def options(
            self,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
    ) -> Optional[Response]:
        """Send an HTTP OPTIONS request.

        OPTIONS requests are used to determine the allowed HTTP methods
        and other communication options for a resource.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, headers=headers)

        # Delegate to parent class implementation
        return await super().options(url, **merged)

    async def request(
            self,
            method: str,
            url: str,
            timeout: Optional[Union[float, Timeout]] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[bool] = None,
            **kwargs: Any,
    ) -> Optional[Response]:
        """Send an HTTP request using the specified method and URL.

        This is the core method that all other HTTP methods use internally.
        It handles various types of errors gracefully and provides comprehensive
        configuration merging with adapters.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS).
            url: URL to send request to (absolute or relative to endpoint).
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.
            **kwargs: Additional request parameters (headers, data, json, etc.).

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, timeout=timeout, retry=retry, redirects=redirects, **kwargs)

        # Delegate to parent class implementation
        return await super().request(method, url, **merged)

    async def stream(
            self,
            method: str,
            url: str,
            timeout: Optional[Union[float, Timeout]] = None,
            **kwargs: Any,
    ) -> Stream:
        """Send a streaming HTTP request.

        Streaming requests allow processing of large responses without
        loading the entire response into memory at once.

        Args:
            method: HTTP method to use (GET, POST, etc.).
            url: URL to send request to (absolute or relative to endpoint).
            timeout: Request timeout override.
            **kwargs: Additional request parameters.

        Returns:
            Stream object for reading the response incrementally.
        """
        # Convert relative URLs to absolute by prepending endpoint
        if url.startswith('/'):
            url = self.endpoint + url

        # Merge adapter configuration with request parameters
        merged = self.merge(url, **kwargs)

        # Delegate to parent class implementation
        return await super().stream(method, url, timeout=timeout, **merged)

    def close(self) -> None:
        """Close the session and clean up resources.

        This method clears all adapters and headers to free up memory
        and ensure proper cleanup of the session.

        Returns:
            None
        """
        # Clear all mounted adapters
        self.adapters.clear()

        # Clear session headers
        self.headers.clear()