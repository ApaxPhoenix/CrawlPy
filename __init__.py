__version__ = "0.1.0"
__author__ = "Andrew Hernandez"
__email__ = "andromedeyz@hotmail.com"
__license__ = "MIT"
__description__ = "A efficient web crawler in Python with customizable rules and dynamic content handling for easy data extraction."
__url__ = "http://github.com/ApaxPhoenix/CrawlPy"

# Main CrawlPy class - primary interface for web crawling operations
from .crawlpy import CrawlPy

# Client configuration classes for HTTP settings
from .config import (
    Timeout,  # Connection, read, write, and pool timeout settings
    Retry,  # Retry policies with exponential backoff strategies
    Limits,  # HTTP connection pool size limitations
    Redirects,  # HTTP redirect following configuration
)

# Authentication mechanisms for secure API access
from .auth import (
    Basic,  # HTTP Basic authentication with credentials
    Bearer,  # Bearer token-based authentication
    JWT,  # JSON Web Token authentication support
    Key,  # API key authentication with configurable headers
    OAuth,  # OAuth 2.0 client credentials authentication
)

# Network and security configuration classes
from .settings import (
    Proxy,  # HTTP/HTTPS proxy server configuration
    SSL,  # SSL/TLS certificate and security settings
)

# HTTP response processing and streaming classes
from .broadcast import (
    Response,  # Standard HTTP response with content parsing
    Stream,  # Streaming response handler for large content
)

# Public API exports for external use
__all__ = [
    # Primary crawler class
    "CrawlPy",
    # HTTP client configuration
    "Timeout",
    "Retry",
    "Limits",
    "Redirects",
    # Authentication methods
    "Basic",
    "Bearer",
    "JWT",
    "Key",
    "OAuth",
    # Network configuration
    "Proxy",
    "SSL",
    # Response processing
    "Response",
    "Stream",
    # Library metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__",
]

# Standard HTTP status codes with descriptive names
status = {
    # 1xx Informational responses
    100: "Continue",
    101: "Switching Protocols",
    # 2xx Success responses
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    # 3xx Redirection responses
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    # 4xx Client error responses
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    429: "Too Many Requests",
    # 5xx Server error responses
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

# MIME content types for HTTP requests and responses
types = {
    "json": "application/json",
    "form": "application/x-www-form-urlencoded",
    "multipart": "multipart/form-data",
    "text": "text/plain",
    "html": "text/html",
    "xml": "application/xml",
    "binary": "application/octet-stream",
}

# Browser user agent strings for web scraping stealth
agents = {
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "crawlpy": "CrawlPy/0.1.0 (http://github.com/ApaxPhoenix/CrawlPy)",
}

# Python version compatibility enforcement
import sys

if sys.version_info < (3, 9):
    raise RuntimeError("CrawlPy requires Python 3.9 or higher")
