import json
from urllib.parse import urlparse


class Response:
    """Class for handling HTTP responses."""

    def __init__(self, response):
        """Initialize HTTPResponse with the underlying HTTP response."""
        # Store the underlying HTTP response object
        self.response = response

    @property
    def status(self):
        """Return the HTTP status code."""
        # Return the status code of the response
        return self.response.status

    @property
    def headers(self):
        """Return the HTTP response headers."""
        # Return the headers of the response
        return self.response.headers

    async def read(self):
        """Read and return the content of the HTTP response asynchronously."""
        # Asynchronously read the response content and return it
        return await self.response.text()


class Request:
    """Class for making HTTP requests."""

    def __init__(self, connection):
        """Initialize HTTPRequest with a connection."""
        # Store the connection object that will manage connections
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
        # Parse the URL to extract its components
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        # If the connection does not exist for this URL's netloc, create a new connection
        if netloc not in self.connection.connections:
            await self.connection.connect(url)

        # Get the session for the connection
        connection = self.connection.connections[netloc]["session"]

        # Set default headers if none are provided
        if headers is None:
            headers = {}

        # If cookies are provided, add them to the request headers
        if cookies:
            headers['Cookie'] = '; '.join([f"{key}={value}" for key, value in cookies.items()])

        # If data is provided, convert it to JSON and set the appropriate content-type header
        if data is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data)

        # If parameters are provided, add them to the URL as query string
        if params:
            url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])

        # Make the asynchronous HTTP request and return the Response object
        async with connection.request(method, url, headers=headers, data=data) as response:
            return Response(response)
