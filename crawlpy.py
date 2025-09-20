import aiohttp
import warnings
from typing import Optional, Any, Dict, Union, TypeVar, Awaitable, Callable
from core import CrawlCore
from config import Limits, Retry, Timeout, Redirects
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth
from broadcast import Response, Stream

# Enhanced type definitions for improved type safety and clarity
T = TypeVar("T")
CrawlPyType = TypeVar("CrawlPyType", bound="CrawlPy")
CoreType = TypeVar("CoreType", bound=CrawlCore)
ResponseType = TypeVar("ResponseType", bound=Response)
StreamType = TypeVar("StreamType", bound=Stream)
AuthType = TypeVar("AuthType", bound=Union[Basic, Bearer, JWT, Key, OAuth])
ConfigType = TypeVar("ConfigType")
HookType = Callable[..., Awaitable[Any]]
RequestHandlerType = Callable[[aiohttp.ClientRequest], Awaitable[aiohttp.ClientResponse]]
ResponseHandlerType = Callable[[aiohttp.ClientResponse], Awaitable[Response]]
TimeoutType = Union[float, aiohttp.ClientTimeout]
HeadersType = Dict[str, str]
CookiesType = Dict[str, str]
ParamsType = Dict[str, Any]
DataType = Union[Dict[str, Any], str, bytes]
FilesType = Dict[str, Any]
JsonType = Dict[str, Any]
HooksType = Dict[str, HookType]
UrlType = str
HttpMethod = str


class CrawlPy(CrawlCore):
    """
    A high-level HTTP client that extends CrawlCore functionality.
    Provides intuitive methods for making HTTP requests with a familiar interface.

    This class inherits all CrawlCore capabilities and adds convenience methods
    that follow familiar HTTP client patterns for ease of use.

    As a superset of CrawlCore, it maintains full backward compatibility while
    providing additional high-level HTTP method wrappers.
    """

    def __init__(
            self,
            endpoint: Optional[UrlType] = None,
            limits: Optional[Limits] = None,
            timeout: Optional[Timeout] = None,
            retry: Optional[Retry] = None,
            redirects: Optional[Redirects] = None,
            proxy: Optional[Proxy] = None,
            ssl: Optional[SSL] = None,
            auth: Optional[AuthType] = None,
            cookies: Optional[CookiesType] = None,
            hooks: Optional[HooksType] = None,
    ) -> None:
        """
        Initialize CrawlPy as an extension of CrawlCore.

        Args:
            endpoint: Base URL for all requests. If provided, will be prepended to all request URLs
            limits: Connection limits configuration
            timeout: Timeout configuration for requests
            retry: Retry configuration for failed requests
            redirects: Redirect handling configuration
            proxy: Proxy configuration for requests
            ssl: SSL/TLS configuration
            auth: Authentication configuration (Basic, Bearer, JWT, Key, or OAuth)
            cookies: Default cookies as key-value pairs
            hooks: Request/response hooks {"request": callable, "response": callable}
        """
        # Initialize parent CrawlCore with all configuration
        # This gives us access to all core HTTP client functionality
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

    async def get(
            self,
            url: UrlType,
            params: Optional[ParamsType] = None,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a GET request to retrieve data from the specified URL.
        GET requests are used to fetch resources from the server without
        modifying server state. Query parameters can be included.

        Args:
            url: The target URL for the GET request
            params: Optional query parameters as key-value pairs
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # GET requests are idempotent and safe - they don't modify server state
            return await self.request(
                "GET",
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"GET request failed: {error}")
            return None

    async def post(
            self,
            url: UrlType,
            data: Optional[DataType] = None,
            json: Optional[JsonType] = None,
            files: Optional[FilesType] = None,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a POST request to submit data to the specified URL.
        POST requests are used to create new resources or submit data to the server.
        This method handles both regular form data and file uploads automatically.

        Args:
            url: The target URL for the POST request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            files: Optional file uploads as key-value pairs
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Handle file uploads by creating multipart form data
            # This is necessary because files require special encoding
            if files:
                # Create multipart form for file uploads
                # aiohttp.FormData handles the proper multipart/form-data encoding
                form: aiohttp.FormData = aiohttp.FormData()

                # Add files first to the form data
                # Files need to be processed before regular form fields
                for key, file in files.items():
                    form.add_field(key, file)

                # Add regular data fields if they exist
                # This allows mixing file uploads with regular form data
                if data and isinstance(data, dict):
                    for key, value in data.items():
                        form.add_field(key, value)

                # Send request with multipart form data
                # The form object handles all the encoding automatically
                return await self.request(
                    "POST",
                    url,
                    data=form,
                    headers=headers,
                    timeout=timeout,
                    redirects=redirects,
                    cookies=cookies,
                )
            else:
                # No files, use data or json directly
                # This is the standard path for most POST requests
                return await self.request(
                    "POST",
                    url,
                    data=data,
                    json=json,
                    headers=headers,
                    timeout=timeout,
                    redirects=redirects,
                    cookies=cookies,
                )
        except Exception as error:
            warnings.warn(f"POST request failed: {error}")
            return None

    async def put(
            self,
            url: UrlType,
            data: Optional[DataType] = None,
            json: Optional[JsonType] = None,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a PUT request to update or create a resource at the specified URL.
        PUT requests are used to update existing resources or create new ones
        with a specific identifier. The request replaces the entire resource.

        Args:
            url: The target URL for the PUT request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # PUT requests are idempotent - multiple identical requests have the same effect
            return await self.request(
                "PUT",
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"PUT request failed: {error}")
            return None

    async def patch(
            self,
            url: UrlType,
            data: Optional[DataType] = None,
            json: Optional[JsonType] = None,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a PATCH request to partially update a resource at the specified URL.
        PATCH requests are used to make partial updates to existing resources,
        unlike PUT which replaces the entire resource.

        Args:
            url: The target URL for the PATCH request
            data: Optional form data as dictionary or string
            json: Optional JSON data as dictionary (automatically serialized)
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # PATCH requests are not necessarily idempotent - they modify specific fields
            return await self.request(
                "PATCH",
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"PATCH request failed: {error}")
            return None

    async def delete(
            self,
            url: UrlType,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a DELETE request to remove a resource at the specified URL.
        DELETE requests are used to remove resources from the server.

        Args:
            url: The target URL for the DELETE request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # DELETE requests are idempotent - multiple deletions have the same effect
            return await self.request(
                "DELETE",
                url,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"DELETE request failed: {error}")
            return None

    async def head(
            self,
            url: UrlType,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send a HEAD request to retrieve headers from the specified URL.
        HEAD requests are used to fetch response headers without the response body.

        Args:
            url: The target URL for the HEAD request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # HEAD requests are identical to GET but return only headers, no body
            return await self.request(
                "HEAD",
                url,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"HEAD request failed: {error}")
            return None

    async def options(
            self,
            url: UrlType,
            headers: Optional[HeadersType] = None,
            timeout: Optional[TimeoutType] = None,
            redirects: Optional[bool] = None,
            cookies: Optional[CookiesType] = None,
    ) -> Optional[ResponseType]:
        """
        Send an OPTIONS request to retrieve allowed methods for the specified URL.
        OPTIONS requests are used to check what HTTP methods are supported.

        Args:
            url: The target URL for the OPTIONS request
            headers: Optional HTTP headers as key-value pairs
            timeout: Request timeout (float for simple timeout, ClientTimeout for detailed control)
            redirects: Whether to follow redirects (uses default if not provided)
            cookies: Optional cookies as key-value pairs

        Returns:
            Optional[Response]: Response object if successful, None if an error occurred
        """
        try:
            # Use inherited request method from CrawlCore
            # OPTIONS requests are used for CORS preflight and API capability discovery
            return await self.request(
                "OPTIONS",
                url,
                headers=headers,
                timeout=timeout,
                redirects=redirects,
                cookies=cookies,
            )
        except Exception as error:
            warnings.warn(f"OPTIONS request failed: {error}")
            return None