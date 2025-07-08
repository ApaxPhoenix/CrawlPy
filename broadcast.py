import aiohttp
import json
from typing import Dict, Any, AsyncIterator


class Response:
    """
    HTTP response wrapper providing comprehensive response data access.

    This class wraps aiohttp ClientResponse objects to provide a unified,
    convenient interface for accessing response data, headers, status codes,
    cookies, and other metadata. It abstracts away the underlying HTTP
    library details while providing essential response information.

    The Response class handles different content types through specialized
    methods and provides proper error handling for JSON parsing and content
    decoding operations. It maintains access to the original response object
    for advanced use cases while offering a cleaner API for common operations.

    Response objects are typically created by HTTP client implementations
    and provide both synchronous property access for metadata and asynchronous
    methods for content retrieval to handle potentially large response bodies.

    Attributes:
        response: The underlying aiohttp ClientResponse object that provides
                 the actual HTTP response data and functionality.
    """

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        """
        Initialize Response wrapper with the underlying HTTP response.

        Creates a Response instance that wraps an aiohttp ClientResponse
        to provide a more convenient and consistent API for response handling.
        The wrapper maintains a reference to the original response object
        for accessing all underlying functionality.

        Args:
            response: The aiohttp ClientResponse object to wrap.
                     This should be an active response object from a completed
                     HTTP request that can be used for content retrieval.

        Returns:
            None
        """
        self.response = response

    @property
    def status(self) -> int:
        """
        HTTP status code from the response.

        Returns the numeric HTTP status code that indicates the result
        of the HTTP request. Common status codes include 200 (OK),
        404 (Not Found), 500 (Internal Server Error), etc.

        Status codes are grouped by their first digit:
        - 1xx: Informational responses
        - 2xx: Success responses
        - 3xx: Redirection messages
        - 4xx: Client error responses
        - 5xx: Server error responses

        Returns:
            int: The HTTP status code from the response (100-599).
        """
        return self.response.status

    @property
    def reason(self) -> str:
        """
        HTTP reason phrase explaining the status code.

        Returns the textual reason phrase that accompanies the HTTP status
        code, providing a human-readable explanation of the response status.
        Examples include "OK" for 200, "Not Found" for 404, etc.

        The reason phrase is standardized for common status codes but may
        vary between servers for less common codes or custom implementations.

        Returns:
            str: The HTTP reason phrase associated with the status code.
                Returns an empty string if no reason phrase is available.
        """
        return self.response.reason

    @property
    def url(self) -> str:
        """
        Final URL after following any redirects.

        Returns the actual URL that was ultimately requested after following
        any HTTP redirects. This may differ from the original request URL
        if the server responded with redirect status codes (3xx) that were
        automatically followed by the HTTP client.

        This is useful for tracking the final destination of requests and
        understanding the redirect chain that may have occurred during
        the request processing.

        Returns:
            str: The final URL that was actually requested.
                 Always returns a string representation of the URL.
        """
        return str(self.response.url)

    @property
    def headers(self) -> Dict[str, str]:
        """
        HTTP response headers as a dictionary.

        Returns all HTTP response headers sent by the server as a dictionary
        with header names as keys and header values as strings. Header names
        are case-insensitive in HTTP but are typically returned in a
        normalized form.

        Headers contain important metadata about the response including
        content type, content length, caching directives, security headers,
        and server information. Multiple headers with the same name are
        typically combined into a single value.

        Returns:
            Dict[str, str]: Dictionary containing all response headers.
                           Keys are header names, values are header values.
                           Returns an empty dict if no headers are present.
        """
        return dict(self.response.headers)

    @property
    def cookies(self) -> Dict[str, str]:
        """
        HTTP response cookies as a dictionary.

        Returns all cookies sent by the server in Set-Cookie headers,
        converted to a simple dictionary format with cookie names as keys
        and cookie values as strings. This provides easy access to cookie
        data for session management and state tracking.

        Note that this simplified representation loses cookie attributes
        like domain, path, expiration, and security flags. For full cookie
        details, access the underlying response object directly.

        Returns:
            Dict[str, str]: Dictionary containing cookie name-value pairs.
                           Keys are cookie names, values are cookie values.
                           Returns an empty dict if no cookies are present.
        """
        return {cookie.key: cookie.value for cookie in self.response.cookies.values()}

    @property
    def type(self) -> str:
        """
        Content-Type header value for response format detection.

        Returns the Content-Type header value which indicates the media type
        of the response body. This is essential for determining how to process
        the response content (e.g., "application/json", "text/html",
        "image/png", etc.).

        The Content-Type may include additional parameters like charset
        (e.g., "text/html; charset=utf-8") which specify how to interpret
        the content encoding.

        Returns:
            str: The Content-Type header value.
                Returns an empty string if the Content-Type header is not present.
        """
        return self.response.headers.get("Content-Type", "")

    async def text(self) -> str:
        """
        Response content as decoded text string.

        Retrieves the response body and decodes it to a text string using
        the appropriate character encoding. The encoding is determined from
        the Content-Type header or falls back to UTF-8 if not specified.

        This method is ideal for text-based responses like HTML, XML, plain
        text, or any content that should be processed as readable text.
        For binary content, use the content() method instead.

        Returns:
            str: The response body decoded as text using the appropriate encoding.
                 Returns an empty string for empty response bodies.

        Raises:
            UnicodeDecodeError: If the response content cannot be decoded
                               using the specified or detected encoding.
            aiohttp.ClientError: If there's an error reading the response content.
        """
        return await self.response.text()

    async def content(self) -> bytes:
        """
        Response content as raw bytes without decoding.

        Retrieves the complete response body as raw bytes without any
        character encoding or content processing. This is essential for
        binary content like images, files, or any data that should be
        processed as raw bytes.

        This method loads the entire response into memory, so it may not
        be suitable for very large responses. For streaming large content,
        use the read() method instead.

        Returns:
            bytes: The raw response body as bytes.
                  Returns an empty bytes object for empty response bodies.

        Raises:
            aiohttp.ClientError: If there's an error reading the response content.
        """
        return await self.response.read()

    async def json(self) -> Dict[str, Any]:
        """
        Response content as parsed JSON data.

        Retrieves the response body and parses it as JSON, returning the
        resulting Python data structure. This method handles JSON parsing
        errors and provides clear error messages for debugging.

        The method expects the response to contain valid JSON data and
        will raise an error if the content cannot be parsed. It's commonly
        used for API responses that return structured data.

        Returns:
            Dict[str, Any]: The parsed JSON response as a Python dictionary.
                           For JSON arrays, returns a list instead.
                           For JSON primitives, returns the corresponding Python type.

        Raises:
            ValueError: If the response content cannot be parsed as valid JSON.
                       The error message includes details about the parsing failure.
        """
        try:
            return await self.response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as error:
            raise ValueError(f"Failed to parse JSON: {error}")

    async def read(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream response content in chunks for memory-efficient processing.

        Yields the response content in manageable chunks rather than loading
        the entire response into memory at once. This is essential for
        processing large responses, file downloads, or streaming data without
        causing memory exhaustion.

        The method provides an asynchronous iterator that yields bytes chunks
        as they become available from the server. This enables efficient
        processing of large files or continuous data streams.

        Args:
            size: The maximum size of each chunk in bytes.
                 Default is 8192 bytes (8KB), which provides a good balance
                 between memory usage and I/O efficiency. Larger chunks may
                 improve performance for very large files.

        Yields:
            bytes: Chunks of the response content as they become available.
                  Each chunk will be at most 'size' bytes, with the final
                  chunk potentially being smaller.

        Raises:
            aiohttp.ClientError: If there's an error reading the response content.
        """
        async for chunk in self.response.content.iter_chunked(size):
            yield chunk


class Stream(Response):
    """
    Streaming HTTP response handler with bidirectional streaming support.

    This class extends Response to provide advanced streaming capabilities
    for both reading from and writing to HTTP streams. It's designed for
    scenarios that require efficient handling of large data transfers,
    real-time streaming, or bidirectional communication.

    Stream is particularly useful for:
    - Large file uploads and downloads
    - Real-time data streaming (WebRTC, live feeds)
    - Chunked transfer encoding scenarios
    - Memory-efficient processing of large responses
    - Bidirectional communication protocols

    The class maintains a write buffer for accumulating data to be sent
    to the server while providing efficient streaming read capabilities
    for processing server responses. This enables full-duplex communication
    patterns when supported by the underlying protocol.

    Attributes:
        response: The underlying aiohttp ClientResponse object inherited from Response.
        data: Internal buffer for accumulating data during write operations.
              This buffer stores bytes that will be sent to the server.
    """

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        """
        Initialize Stream with the underlying HTTP response and write buffer.

        Creates a Stream instance that wraps an aiohttp ClientResponse
        while adding streaming capabilities for both read and write operations.
        The stream maintains an internal buffer for write operations and
        provides efficient chunk-based reading for download operations.

        Args:
            response: The aiohttp ClientResponse object to wrap.
                     This should be an active response object from a streaming
                     HTTP request that supports bidirectional communication.

        Returns:
            None
        """
        super().__init__(response)
        # Initialize write buffer for accumulating outgoing data
        # This buffer stores bytes that will be sent to the server
        # during streaming upload operations
        self.data = b""

    async def write(self, data: bytes) -> None:
        """
        Write data to the stream buffer for upload streaming operations.

        Accumulates data in the internal buffer that will be sent to the
        server during streaming upload operations. This method is useful
        for building up data to be transmitted in chunks or for collecting
        data from multiple sources before transmission.

        The data is appended to the internal buffer and can be sent to
        the server using the underlying HTTP client's streaming mechanisms.
        This enables efficient handling of large uploads without requiring
        all data to be available in memory simultaneously.

        Args:
            data: The bytes to write to the stream buffer.
                 This data will be appended to any existing buffer content
                 and will be sent to the server during streaming operations.

        Returns:
            None

        Note:
            This method only buffers the data locally. Actual transmission
            to the server depends on the underlying HTTP client implementation
            and the specific streaming protocol being used.
        """
        self.data += data

    async def read(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream response content in chunks for download streaming operations.

        Yields the response content from the server in manageable chunks,
        enabling memory-efficient processing of large downloads or continuous
        data streams. This method is optimized for scenarios where the
        response data is too large to fit in memory or needs to be processed
        as it arrives.

        The streaming approach prevents memory overflow when handling large
        responses and enables real-time processing of data as it becomes
        available from the server. This is essential for large file downloads,
        media streaming, or any scenario requiring efficient memory usage.

        Args:
            size: The maximum size of each chunk in bytes.
                 Default is 8192 bytes (8KB), which provides optimal balance
                 between memory usage and I/O efficiency. Larger chunks may
                 improve throughput for very large files.

        Yields:
            bytes: Chunks of the response content as they arrive from the server.
                  Each chunk will be at most 'size' bytes, with the final
                  chunk potentially being smaller or empty when the stream ends.

        Raises:
            aiohttp.ClientError: If there's an error reading the response content
                               or if the connection is lost during streaming.
        """
        async for chunk in self.response.content.iter_chunked(size):
            yield chunk

    def response(self) -> Response:
        """
        Get the final response after streaming operations are complete.

        Creates a standard Response object that provides access to response
        metadata like status codes, headers, and cookies after streaming
        operations have finished. This is useful for accessing response
        information that becomes available only after the stream has been
        fully processed.

        The returned Response object wraps the same underlying HTTP response
        but provides the standard response interface rather than streaming
        capabilities. This enables normal response processing after streaming
        operations are complete.

        Returns:
            Response: A Response object wrapping the underlying HTTP response.
                     This object provides access to status, headers, cookies,
                     and other response metadata through the standard Response API.

        Note:
            The returned Response object shares the same underlying HTTP response,
            so any content that has already been consumed through streaming
            operations will not be available through the Response object's
            content methods.
        """
        return Response(self.response)
