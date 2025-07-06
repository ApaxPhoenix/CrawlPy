import aiohttp
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Limits:
    """Connection limit configuration for the HTTP client.

    This class defines the connection pooling and keepalive settings
    to control resource usage and connection management.
    """
    connections: int = 50  # Maximum total connections in the pool
    keepalive: int = 10  # Maximum keepalive connections to maintain
    host: int = 20  # Maximum connections per host


@dataclass
class Retry:
    """Retry configuration for failed requests.

    Defines the retry behavior for HTTP requests that fail due to
    network issues or server errors.
    """
    total: int = 3  # Total number of retry attempts
    backoff: float = 1.0  # Exponential backoff factor between retries
    status: Optional[List[int]] = None  # HTTP status codes that trigger retries

    def __post_init__(self):
        """Initialize default retry status codes if not provided.

        Sets default status codes for server errors (5xx) that should
        trigger automatic retries.
        """
        if self.status is None:
            self.status = [500, 502, 503, 504]


@dataclass
class Timeout:
    """Timeout configuration for HTTP requests.

    Defines various timeout values to prevent requests from hanging
    indefinitely and ensure responsive behavior.
    """
    connect: float = 5.0  # Time to wait for initial connection establishment
    read: float = 30.0  # Time to wait for response data after request sent
    write: float = 10.0  # Time to wait when sending request data
    pool: float = 60.0  # Total time limit for the entire request operation

    def convert(self) -> aiohttp.ClientTimeout:
        """Convert to aiohttp ClientTimeout object.

        Transforms the timeout configuration into aiohttp's native
        ClientTimeout format for use with HTTP sessions.

        Returns:
            aiohttp.ClientTimeout: Configured timeout object for aiohttp
        """
        return aiohttp.ClientTimeout(
            total=self.pool,
            connect=self.connect,
            sock_read=self.read,
            sock_connect=self.connect
        )


@dataclass
class Redirects:
    """Redirect configuration for HTTP requests.

    Controls how HTTP redirects (3xx responses) are handled during
    request processing.
    """
    maximum: int = 10  # Maximum number of redirects to follow
    history: bool = True  # Whether to maintain redirect history in response