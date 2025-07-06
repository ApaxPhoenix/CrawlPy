import aiohttp
import json
import time
from typing import Dict, Any, AsyncIterator


class Response:
    """
    Class for handling HTTP responses with comprehensive response data access.

    This class wraps aiohttp responses to provide a unified interface for accessing
    response data, headers, status codes, and other metadata. It tracks timing
    information and provides convenient methods for different content types.
    """

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        """
        Initialize Response with the underlying HTTP response.

        Args:
            response: The aiohttp ClientResponse object to wrap
        """
        self.response = response
        self.time = time.time()  # Record response creation time for elapsed calculation

    @property
    def status(self) -> int:
        """
        Return the HTTP status code (error.g., 200, 404, 500).

        Returns:
            int: The HTTP status code from the response
        """
        return self.response.status

    @property
    def reason(self) -> str:
        """
        Return the HTTP reason phrase (error.g., "OK", "Not Found", "Internal Server Error").

        Returns:
            str: The HTTP reason phrase associated with the status code
        """
        return self.response.reason

    @property
    def url(self) -> str:
        """
        Return the final URL after any redirects have been followed.

        Returns:
            str: The final URL that was actually requested
        """
        return str(self.response.url)

    @property
    def elapsed(self) -> float:
        """
        Return the request duration in seconds from response creation.

        Returns:
            float: Time elapsed since response object was created
        """
        return time.time() - self.time

    @property
    def headers(self) -> Dict[str, str]:
        """
        Return the HTTP response headers as a dictionary.

        Returns:
            Dict[str, str]: Dictionary containing all response headers
        """
        return dict(self.response.headers)

    @property
    def type(self) -> str:
        """
        Return the Content-Type header value for determining response format.

        Returns:
            str: The Content-Type header value, or empty string if not present
        """
        return self.response.headers.get('Content-Type', '')

    async def text(self) -> str:
        """
        Return the response content as decoded text string.

        Returns:
            str: The response body decoded as text using the appropriate encoding
        """
        return await self.response.text()

    async def content(self) -> bytes:
        """
        Return the response content as raw bytes without any decoding.

        Returns:
            bytes: The raw response body as bytes
        """
        return await self.response.read()

    async def json(self) -> Dict[str, Any]:
        """
        Return the response content as parsed JSON data.

        Returns:
            Dict[str, Any]: The parsed JSON response as a dictionary

        Raises:
            ValueError: If the response cannot be parsed as valid JSON
        """
        try:
            return await self.response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as error:
            raise ValueError(f"Failed to parse JSON: {error}")

    async def read(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Yield response content in chunks for streaming large responses.

        This method is useful for processing large responses without loading
        the entire content into memory at once.

        Args:
            size: The maximum size of each chunk in bytes (default: 8192)

        Yields:
            bytes: Chunks of the response content
        """
        async for chunk in self.response.content.iter_chunked(size):
            yield chunk


class Stream(Response):
    """
    Class for handling streaming HTTP responses with bidirectional streaming support.

    This class extends Response to provide streaming capabilities for both
    reading from and writing to HTTP streams. It's particularly useful for
    large file uploads, downloads, or real-time data streaming scenarios.
    """

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        """
        Initialize Stream with the underlying HTTP response.

        Args:
            response: The aiohttp ClientResponse object to wrap
        """
        super().__init__(response)
        self.data = b""  # Buffer for write operations

    async def write(self, data: bytes) -> None:
        """
        Write data to the stream buffer for upload streaming operations.

        This method accumulates data that will be sent to the server.
        Useful for streaming large files or data uploads.

        Args:
            data: The bytes to write to the stream buffer
        """
        self.data += data

    async def read(self, size: int = 8192) -> AsyncIterator[bytes]:
        """
        Read response content in chunks for download streaming operations.

        This method streams content from the server in manageable chunks,
        preventing memory overflow when handling large responses.

        Args:
            size: The maximum size of each chunk in bytes (default: 8192)

        Yields:
            bytes: Chunks of the response content
        """
        async for chunk in self.response.content.iter_chunked(size):
            yield chunk

    def response(self) -> Response:
        """
        Get the final response after streaming operations are complete.

        This method returns a standard Response object that can be used
        to access status codes, headers, and other response metadata.

        Returns:
            Response: A Response object wrapping the underlying HTTP response
        """
        return Response(self.response)