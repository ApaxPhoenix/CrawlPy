from typing import Optional, Dict, Any, Union, Callable, TypeVar, Awaitable
import aiohttp
from crawlpy import CrawlPy
from config import Limits, Retry, Timeout, Redirects
from settings import SSL, Proxy
from broadcast import Response, Stream
from auth import Basic, Bearer, JWT, Key, OAuth

# Enhanced type definitions for improved type safety and clarity
T = TypeVar("T")
SessionType = TypeVar("SessionType", bound="Session")
ResponseType = TypeVar("ResponseType", bound=Response)
StreamType = TypeVar("StreamType", bound=Stream)
AuthType = TypeVar("AuthType", bound=Union[Basic, Bearer, JWT, Key, OAuth])
ConfigType = TypeVar("ConfigType")
HookType = Callable[..., Awaitable[Any]]
AdapterType = TypeVar("AdapterType")
RequestHandlerType = Callable[[aiohttp.ClientRequest], Awaitable[aiohttp.ClientResponse]]
ResponseHandlerType = Callable[[aiohttp.ClientResponse], Awaitable[Response]]
CookieJarType = TypeVar("CookieJarType", bound=aiohttp.CookieJar)
TimeoutType = Union[float, aiohttp.ClientTimeout]
HeadersType = Dict[str, str]
CookiesType = Dict[str, str]
ParamsType = Dict[str, Any]
DataType = Union[Dict[str, Any], str, bytes]
FilesType = Dict[str, Any]
JsonType = Dict[str, Any]
HooksType = Dict[str, HookType]
AdaptersType = Dict[str, AdapterType]
UrlType = str
HttpMethod = str


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
        endpoint: UrlType,
        limits: Optional[Limits] = None,
        timeout: Optional[Timeout] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[Redirects] = None,
        proxy: Optional[Proxy] = None,
        ssl: Optional[SSL] = None,
        auth: Optional[AuthType] = None,
        hooks: Optional[HooksType] = None,
        headers: Optional[HeadersType] = None,
        cookies: Optional[CookiesType] = None,
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
        self.headers: HeadersType = headers or {}
        self.cookies: CookiesType = cookies or {}
        self.hooks: HooksType = hooks or {}
        self.adapters: AdaptersType = {}

    def mount(self, prefix: UrlType, adapter: AdapterType) -> None:
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
        url: UrlType,
        params: Optional[ParamsType] = None,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        # Similar to headers, session cookies are defaults
        cookies: CookiesType = self.cookies.copy()
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
        url: UrlType,
        data: Optional[DataType] = None,
        json: Optional[JsonType] = None,
        files: Optional[FilesType] = None,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
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
        url: UrlType,
        data: Optional[DataType] = None,
        json: Optional[JsonType] = None,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
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
        url: UrlType,
        data: Optional[DataType] = None,
        json: Optional[JsonType] = None,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
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
        url: UrlType,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # DELETE requests used for removing resources
        return await super().delete(
            url, 
            headers=headers, 
            timeout=timeout, 
            redirects=redirects, 
            cookies=cookies
        )

    async def head(
        self,
        url: UrlType,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # HEAD requests return only headers, no body content
        return await super().head(
            url, 
            headers=headers, 
            timeout=timeout, 
            redirects=redirects, 
            cookies=cookies
        )

    async def options(
        self,
        url: UrlType,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        retry: Optional[Retry] = None,
        redirects: Optional[bool] = None,
        cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # OPTIONS requests return supported methods in Allow header
        return await super().options(
            url, 
            headers=headers, 
            timeout=timeout, 
            redirects=redirects, 
            cookies=cookies
        )

    async def stream(
        self,
        method: HttpMethod,
        url: UrlType,
        headers: Optional[HeadersType] = None,
        timeout: Optional[TimeoutType] = None,
        cookies: Optional[CookiesType] = None,
        **kwargs: Any
    ) -> Optional[StreamType]:
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
        headers: HeadersType = self.headers.copy()
        if headers:
            headers.update(headers)

        # Merge session cookies with request-specific cookies
        cookies: CookiesType = self.cookies.copy()
        if cookies:
            cookies.update(cookies)

        # Delegate to parent class with merged configuration
        # Streaming allows processing large responses without memory overhead
        return await super().stream(
            method, 
            url, 
            headers=headers, 
            timeout=timeout, 
            cookies=cookies, 
            **kwargs
        )