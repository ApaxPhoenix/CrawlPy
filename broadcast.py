import json
from urllib.parse import urlparse


class Response:
    """Class for handling HTTP responses."""

    def __init__(self, response):
        """Initialize HTTPResponse with the underlying HTTP response."""
        self.response = response

    @property
    def status(self):
        """Return the HTTP status code."""
        return self.response.status

    @property
    def headers(self):
        """Return the HTTP response headers."""
        return self.response.headers

    async def read(self):
        """Read and return the content of the HTTP response asynchronously."""
        return await self.response.text()


class Request:
    """Class for making HTTP requests."""

    def __init__(self, connection):
        """Initialize HTTPRequest with a connection."""
        self.connection = connection

    async def request(self, method, url, params=None, data=None, headers=None, cookies=None):
        """
        Make an HTTP request.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): URL to make the request to.
            params (dict, optional): Dictionary of query parameters.
            data (dict, optional): Data to be sent in the request body.
            headers (dict, optional): Headers to be included in the request.
            cookies (dict, optional): Cookies to be included in the request.

        Returns:
            HTTPResponse: Response object.
        """
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        if netloc not in self.connection.connections:
            await self.connection.connect(url)
        connection = self.connection.connections[netloc]["session"]

        if headers is None:
            headers = {}
        if cookies:
            headers['Cookie'] = '; '.join([f"{key}={value}" for key, value in cookies.items()])
        if data is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data)
        if params:
            url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])

        async with connection.request(method, url, headers=headers, data=data) as response:
            return Response(response)
