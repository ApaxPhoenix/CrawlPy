import aiohttp
import json
from typing import Dict, Any, AsyncIterator, Optional


class Response:
    """
    HTTP response wrapper providing comprehensive response data access with caching.

    This class wraps aiohttp ClientResponse objects to provide a unified,
    convenient interface for accessing response data, headers, status codes,
    cookies, and other metadata. It abstracts away the underlying HTTP
    library details while providing essential response information.

    The Response class handles different content types through specialized
    methods and provides proper error handling for JSON parsing and content
    decoding operations. It maintains access to the original response object
    for advanced use cases while offering a cleaner API for common operations.

    All response data is cached after first access to prevent "Connection closed"
    errors and improve performance. The cache can be modified externally if needed.

    Response objects are typically created by HTTP client implementations
    and provide both synchronous property access for metadata and asynchronous
    methods for content retrieval to handle potentially large response bodies.

    Attributes:
        resp: The underlying aiohttp ClientResponse object that provides
              the actual HTTP response data and functionality.
        cache: Dictionary storing cached response data including bytes, text,
               and parsed JSON to prevent multiple reads and connection errors.
    """

    def __init__(self, resp: aiohttp.ClientResponse) -> None:
        """
        Initialize Response wrapper with the underlying HTTP response and cache.

        Creates a Response instance that wraps an aiohttp ClientResponse
        to provide a more convenient and consistent API for response handling.
        The wrapper maintains a reference to the original response object
        for accessing all underlying functionality and initializes a cache
        dictionary for storing response data.

        Args:
            resp: The aiohttp ClientResponse object to wrap.
                  This should be an active response object from a completed
                  HTTP request that can be used for content retrieval.

        Returns:
            None
        """
        self.resp = resp
        # Cache dictionary to store response data and prevent connection errors
        # Keys: 'bytes' (bytes), 'text' (str), 'json' (dict/list/any)
        self.cache: Dict[str, Any] = {}

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
        return self.resp.status

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
        return self.resp.reason

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
        return str(self.resp.url)

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
        return dict(self.resp.headers)

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
        return {cookie.key: cookie.value for cookie in self.resp.cookies.values()}

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
        return self.resp.headers.get("Content-Type", "")

    async def text(self) -> str:
        """
        Response body as decoded text string with caching.

        Retrieves the response body and decodes it to a text string using
        the appropriate character encoding. The encoding is determined from
        the Content-Type header or falls back to UTF-8 if not specified.

        The decoded text is cached after first access to prevent multiple
        network reads and connection errors. Subsequent calls return the
        cached value.

        This method is ideal for text-based responses like HTML, XML, plain
        text, or any content that should be processed as readable text.
        For binary content, use the bytes() method instead.

        Returns:
            str: The response body decoded as text using the appropriate encoding.
                 Returns an empty string for empty response bodies.

        Raises:
            UnicodeDecodeError: If the response content cannot be decoded
                               using the specified or detected encoding.
            aiohttp.ClientError: If there's an error reading the response content
                               and no cached content is available.
        """
        # Return cached text if available
        if 'text' in self.cache:
            return self.cache['text']

        try:
            # Try to read from response if connection is still open
            self.cache['text'] = await self.resp.text()
        except (aiohttp.ClientConnectionError, RuntimeError):
            # If connection is closed, try to decode from cached bytes
            if 'bytes' in self.cache:
                data = self.cache['bytes']
                # Detect encoding from Content-Type header
                header = self.type.lower()
                encoding = 'utf-8'  # Default encoding

                if 'charset=' in header:
                    try:
                        encoding = header.split('charset=')[1].split(';')[0].strip()
                    except (IndexError, AttributeError):
                        pass

                try:
                    self.cache['text'] = data.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    # Fallback to utf-8 with error handling
                    self.cache['text'] = data.decode('utf-8', errors='replace')
            else:
                # Try to read bytes first, then decode to text
                try:
                    data = await self.bytes()
                    header = self.type.lower()
                    encoding = 'utf-8'

                    if 'charset=' in header:
                        try:
                            encoding = header.split('charset=')[1].split(';')[0].strip()
                        except (IndexError, AttributeError):
                            pass

                    try:
                        self.cache['text'] = data.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        self.cache['text'] = data.decode('utf-8', errors='replace')
                except Exception:
                    raise ValueError("Response connection closed and no cached content available")

        return self.cache['text']

    async def bytes(self) -> bytes:
        """
        Response body as raw bytes without decoding with caching.

        Retrieves the complete response body as raw bytes without any
        character encoding or content processing. This is essential for
        binary content like images, files, or any data that should be
        processed as raw bytes.

        The raw bytes are cached after first access to prevent multiple
        network reads and connection errors. Subsequent calls return the
        cached value.

        This method loads the entire response into memory, so it may not
        be suitable for very large responses. For streaming large content,
        use the stream() method instead.

        Returns:
            bytes: The raw response body as bytes.
                  Returns an empty bytes object for empty response bodies.

        Raises:
            aiohttp.ClientError: If there's an error reading the response content
                               and no cached content is available.
        """
        # Return cached bytes if available
        if 'bytes' in self.cache:
            return self.cache['bytes']

        try:
            # Try to read from response if connection is still open
            self.cache['bytes'] = await self.resp.read()
        except (aiohttp.ClientConnectionError, RuntimeError):
            raise ValueError("Response connection closed and no cached content available")

        return self.cache['bytes']

    async def json(self) -> Dict[str, Any]:
        """
        Response body as parsed JSON data with caching.

        Retrieves the response body and parses it as JSON, returning the
        resulting Python data structure. This method handles JSON parsing
        errors and provides clear error messages for debugging.

        The parsed JSON is cached after first access to prevent multiple
        network reads and parsing operations. Subsequent calls return the
        cached value.

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
        # Return cached JSON if available
        if 'json' in self.cache:
            return self.cache['json']

        try:
            # Try to read JSON directly from response if connection is still open
            self.cache['json'] = await self.resp.json()
        except (aiohttp.ClientConnectionError, RuntimeError):
            # If connection is closed, try to parse from cached text
            text_data = await self.text()  # This will use cache if available
            try:
                self.cache['json'] = json.loads(text_data)
            except json.JSONDecodeError as error:
                raise ValueError(f"Failed to parse JSON: {error}")
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as error:
            raise ValueError(f"Failed to parse JSON: {error}")

        return self.cache['json']

    async def stream(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream response body in chunks for memory-efficient processing.

        Yields the response content in manageable chunks rather than loading
        the entire response into memory at once. This is essential for
        processing large responses, file downloads, or streaming data without
        causing memory exhaustion.

        If bytes are already cached, yields them in chunks from memory.
        Otherwise, streams directly from the response and caches the complete
        content for future access.

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
        # If bytes are already cached, yield them in chunks
        if 'bytes' in self.cache:
            data = self.cache['bytes']
            for position in range(0, len(data), size):
                yield data[position:position + size]
        else:
            # Stream from response and build cache
            pieces = []
            try:
                async for piece in self.resp.content.iter_chunked(size):
                    pieces.append(piece)
                    yield piece

                # Cache the complete content
                self.cache['bytes'] = b''.join(pieces)
            except aiohttp.ClientConnectionError:
                # If we got some chunks before connection closed, cache what we have
                if pieces:
                    self.cache['bytes'] = b''.join(pieces)
                raise

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the response cache.

        Allows external modification of cached response data. This can be useful
        for preprocessing response data or injecting custom values.

        Args:
            key: The cache key to set ('bytes', 'text', 'json', or custom key)
            value: The value to store in the cache

        Returns:
            None
        """
        self.cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the response cache.

        Allows external access to cached response data for inspection or
        custom processing.

        Args:
            key: The cache key to retrieve

        Returns:
            Optional[Any]: The cached value if it exists, None otherwise
        """
        return self.cache.get(key)

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cached response data.

        Removes cached data to force fresh reads from the response object
        (if connection is still available) or to free memory.

        Args:
            key: Specific cache key to clear. If None, clears entire cache.

        Returns:
            None
        """
        if key is None:
            self.cache.clear()
        else:
            self.cache.pop(key, None)


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
        resp: The underlying aiohttp ClientResponse object inherited from Response.
        buffer: Internal buffer for accumulating data during write operations.
                This buffer stores bytes that will be sent to the server.
    """

    def __init__(self, resp: aiohttp.ClientResponse) -> None:
        """
        Initialize Stream with the underlying HTTP response and write buffer.

        Creates a Stream instance that wraps an aiohttp ClientResponse
        while adding streaming capabilities for both read and write operations.
        The stream maintains an internal buffer for write operations and
        provides efficient chunk-based reading for download operations.

        Args:
            resp: The aiohttp ClientResponse object to wrap.
                  This should be an active response object from a streaming
                  HTTP request that supports bidirectional communication.

        Returns:
            None
        """
        super().__init__(resp)
        # Initialize write buffer for accumulating outgoing data
        # This buffer stores bytes that will be sent to the server
        # during streaming upload operations
        self.buffer = b""

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
        self.buffer += data

    async def stream(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream response body in chunks for download streaming operations.

        Overrides the parent stream method to provide direct streaming without
        caching, which is more appropriate for streaming scenarios where
        data should be processed as it arrives rather than stored.

        Args:
            size: The maximum size of each chunk in bytes.
                 Default is 8192 bytes (8KB).

        Yields:
            bytes: Chunks of the response content as they arrive from the server.

        Raises:
            aiohttp.ClientError: If there's an error reading the response content.
        """
        async for chunk in self.resp.content.iter_chunked(size):
            yield chunk

    def wrap(self) -> 'Response':
        """
        Get a Response object for accessing response metadata.

        Creates a standard Response object that provides access to response
        metadata like status codes, headers, and cookies. The returned
        Response object shares the same cache as this Stream object.

        Returns:
            Response: A Response object for accessing response metadata.
        """
        wrapper = Response(self.resp)
        wrapper.cache = self.cache  # Share the cache
        return wrapper