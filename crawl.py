import http.client
from urllib.parse import urlparse
from objects import HTTPRequest, HTTPResponse

class HTTPClient:
    """Class for managing HTTP connections."""

    def __init__(self, proxies=None):
        """Initialize HTTPClient with optional proxies."""
        self.connections = {}
        self.proxies = proxies

    def connect(self, url):
        """Establish a connection to the given URL."""
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme.lower()
        if scheme not in ['http', 'https']:
            raise ValueError("Only HTTP and HTTPS protocols are supported.")
        netloc = parsed_url.netloc
        if netloc not in self.connections:
            if scheme == 'https':
                if self.proxies:
                    self.connections[netloc] = http.client.HTTPSConnection(netloc, timeout=10)
                else:
                    self.connections[netloc] = http.client.HTTPSConnection(netloc)
            else:
                if self.proxies:
                    self.connections[netloc] = http.client.HTTPConnection(netloc, timeout=10)
                else:
                    self.connections[netloc] = http.client.HTTPConnection(netloc)

    def close(self):
        """Close all connections."""
        for connection in self.connections.values():
            connection.close()
        self.connections = {}

class CrawlPy:
    """Class for simplified HTTP requests."""

    def __init__(self, proxies=None):
        """Initialize CrawlPy with optional proxies."""
        self.http_client = HTTPClient(proxies=proxies)
        self.http_request = HTTPRequest(self.http_client)

    def get(self, url, params=None, headers=None, cookies=None):
        """Make a GET request."""
        response = self.http_request.request('GET', url, params=params, headers=headers, cookies=cookies)
        return HTTPResponse(response)

    def post(self, url, data=None, headers=None, cookies=None):
        """Make a POST request."""
        response = self.http_request.request('POST', url, data=data, headers=headers, cookies=cookies)
        return HTTPResponse(response)

    def close(self):
        """Close all connections."""
        self.http_client.close()

# Create a CrawlPy instance
crawler = CrawlPy()

# Make a GET request
response = crawler.get('https://example.com/resource')

# Check the response status code
print("Status Code:", response.status)

# Read the response content
content = response.read().decode('utf-8')
print("Response Content:", content)
