from typing import Optional, Dict, Any, Union, Callable
import aiohttp
from .crawlpy import CrawlPy
from .config import Limits, Retry, Timeout, Redirects
from .settings import SSL, Proxy
from .broadcast import Response, Stream
from .auth import Basic, Bearer, JWT, Key, OAuth


class Session(CrawlPy):
    """High-level HTTP session manager with persistent configuration.

    This class provides a session-based HTTP client that maintains persistent
    configuration, headers, and authentication across multiple requests. It extends
    CrawlPy to provide additional session management capabilities.

    Attributes:
        headers: Dictionary of default headers for all requests.
        cookies: Dictionary of cookies to include in all requests.
        hooks: Dictionary of event hooks for request/response processing.
        adapters: Dictionary of URL prefix to HTTPAdapter mappings.
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
        cookies: Optional[Dict[str, str]] = None,
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
            cookies: Default cookies to include in all requests.
        """
        # Initialize parent class with core HTTP configuration
        # This provides the foundational HTTP client capabilities
        super().__init__(
            endpoint=endpoint,
            limits=limits,
            timeout=timeout,
            retry=retry,
            redirects=redirects,
            proxy=proxy,
            ssl=ssl,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
        )

        # Initialize session-specific attributes with safe defaults
        # These attributes will be merged with request-specific values
        self.headers: Dict[str, str] = headers or {}
        self.cookies: Dict[str, str] = cookies or {}
        self.hooks: Dict[str, Callable[..., Any]] = hooks or {}
        self.adapters: Dict[str, Any] = {}

    def mount(self, prefix: str, adapter: Any) -> None:
        """Mount an HTTPAdapter instance for a specific URL prefix.

        Args:
            prefix: URL prefix to match (e.g., 'https://api.example.com/')
            adapter: HTTPAdapter instance to use for matching URLs

        Returns:
            None
        """
        self.adapters[prefix] = adapter

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[Response]:
        """Send an HTTP GET request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            params: Query parameters to include in the request.
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        # This allows users to make requests with just the path portion
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # Session headers serve as defaults, request headers override
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        # Similar to headers, session cookies are defaults
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        return await super().get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            redirects=redirects,
            cookies=cookies,
        )

    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
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
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # Request headers take precedence over session defaults
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # POST requests support multiple data formats: form data, JSON, files
        return await super().post(
            url,
            data=data,
            json=json,
            files=files,
            headers=headers,
            timeout=timeout,
            redirects=redirects,
            cookies=cookies,
        )

    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
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
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # This ensures consistent header handling across all HTTP methods
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # PUT requests typically used for creating or updating resources
        return await super().put(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            redirects=redirects,
            cookies=cookies,
        )

    async def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
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
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # Consistent header merging pattern across all HTTP methods
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # PATCH requests used for partial updates to existing resources
        return await super().patch(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            redirects=redirects,
            cookies=cookies,
        )

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[Response]:
        """Send an HTTP DELETE request.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # DELETE requests don't typically have body data
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # DELETE requests used for removing resources
        return await super().delete(
            url, headers=headers, timeout=timeout, redirects=redirects, cookies=cookies
        )

    async def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
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
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # HEAD requests useful for checking resource existence without downloading
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # HEAD requests return only headers, no body content
        return await super().head(
            url, headers=headers, timeout=timeout, redirects=redirects, cookies=cookies
        )

    async def options(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[Response]:
        """Send an OPTIONS request to retrieve allowed methods for the specified URL.

        OPTIONS requests are used to check what HTTP methods are supported.

        Args:
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            retry: Retry policy override.
            redirects: Whether to follow redirects.
            cookies: Request-specific cookies.

        Returns:
            Response object or None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # OPTIONS requests used for CORS preflight and capability discovery
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # OPTIONS requests return supported methods in Allow header
        return await super().options(
            url, headers=headers, timeout=timeout, redirects=redirects, cookies=cookies
        )

    async def stream(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[Union[float, aiohttp.ClientTimeout]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> Optional[Stream]:
        """Send a streaming HTTP request for handling large data transfers.

        This method creates a streaming connection that can be used for uploading
        or downloading large amounts of data without loading everything into memory.

        Args:
            method: HTTP method for the streaming request (GET, POST, etc.)
            url: URL to send request to (absolute or relative to endpoint).
            headers: Request-specific headers.
            timeout: Request timeout override.
            cookies: Request-specific cookies.
            **kwargs: Additional arguments to pass to the underlying stream request.

        Returns:
            Stream object if successful, None if request failed.
        """
        # Convert relative URLs to absolute using the session endpoint
        if url.startswith("/"):
            url = self.endpoint + url

        # Merge session headers with request-specific headers
        # Streaming requests benefit from session-level configuration
        headers = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # Streaming allows processing large responses without memory overhead
        return await super().stream(
            method, url, headers=headers, timeout=timeout, cookies=cookies, **kwargs
        )
