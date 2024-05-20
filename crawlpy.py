import http.client
from urllib.parse import urlparse
from .broadcast import Request, Response
import re


class HTTPClient:
    """Class for managing HTTP connections."""

    class Retriever:
        """Class for retrieving elements from HTML content."""

        @staticmethod
        def get_elements_by_tag(html_content, tag_name):
            """
            Retrieve elements from HTML content by tag name using regular expressions.

            Args:
                html_content (str): The HTML content.
                tag_name (str): The tag name to search for (e.g., 'a', 'p', 'body').

            Returns:
                list: A list of strings containing the content of elements matching the given tag name.
            """
            pattern = r"<{0}.*?>(.*?)<\/{0}>".format(tag_name)
            matches = re.findall(pattern, html_content, re.DOTALL)
            return matches

        @staticmethod
        def get_elements_by_class(html_content, class_name):
            """
            Retrieve elements from HTML content by CSS class name using regular expressions.

            Args:
                html_content (str): The HTML content.
                class_name (str): The CSS class name to search for.

            Returns:
                list: A list of strings containing the content of elements with the given CSS class.
            """
            pattern = r'class="{}"[^>]*?>(.*?)<\/[^>]+>'.format(class_name)
            matches = re.findall(pattern, html_content, re.DOTALL)
            return matches

        @staticmethod
        def get_elements_by_id(html_content, element_id):
            """
            Retrieve elements from HTML content by element ID using regular expressions.

            Args:
                html_content (str): The HTML content.
                element_id (str): The ID of the element to search for.

            Returns:
                list: A list of strings containing the content of elements with the given ID.
            """
            pattern = r'id="{}"[^>]*?>(.*?)<\/[^>]+>'.format(element_id)
            matches = re.findall(pattern, html_content, re.DOTALL)
            return matches

        @staticmethod
        def get_elements_by_css_selector(html_content, css_selector):
            """
            Retrieve elements from HTML content by CSS selector using regular expressions.

            Args:
                html_content (str): The HTML content.
                css_selector (str): The CSS selector to search for.

            Returns:
                list: A list of strings containing the content of elements matching the CSS selector.
            """
            selector_parts = css_selector.split()
            pattern = r"[\s>]+".join([r"({})".format(part) for part in selector_parts])
            pattern = pattern.replace("#", r"id=\"([^\"]*)\"").replace(".", r'class=\"([^\"]*)\"')
            pattern = r"<{}.*?>(.*?)<\/{}>".format(pattern, selector_parts[-1])
            matches = re.findall(pattern, html_content, re.DOTALL)
            return matches

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
        self.http_request = Request(self.http_client)
        self.Retriever = HTTPClient.Retriever

    def get(self, url, params=None, headers=None, cookies=None):
        """Make a GET request."""
        response = self.http_request.request('GET', url, params=params, headers=headers, cookies=cookies)
        return Response(response)

    def post(self, url, data=None, headers=None, cookies=None):
        """Make a POST request."""
        response = self.http_request.request('POST', url, data=data, headers=headers, cookies=cookies)
        return Response(response)

    def close(self):
        """Close all connections."""
        self.http_client.close()
