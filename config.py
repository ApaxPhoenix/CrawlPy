from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Limits:
    """Connection limit configuration for the HTTP client.

    This class defines the connection pooling and keepalive settings
    to control resource usage and connection management. Proper limit
    configuration helps prevent resource exhaustion and improves
    application performance.

    Attributes:
        connections: Maximum total connections in the pool.
        keepalive: Maximum keepalive connections to maintain.
        host: Maximum connections per host.
    """

    connections: int = 50  # Maximum total connections in the pool
    keepalive: int = 10  # Maximum keepalive connections to maintain
    host: int = 20  # Maximum connections per host

    def __post_init__(self) -> None:
        """Validate connection limit configuration.

        Ensures that the connection limits are logically consistent
        and within reasonable bounds for typical usage scenarios.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Validate that all limits are positive integers
        if self.connections <= 0:
            raise ValueError("Total connections must be positive")
        if self.keepalive < 0:
            raise ValueError("Keepalive connections cannot be negative")
        if self.host <= 0:
            raise ValueError("Host connections must be positive")

        # Ensure keepalive doesn't exceed total connections
        if self.keepalive > self.connections:
            raise ValueError("Keepalive connections cannot exceed total connections")

        # Ensure per-host limit doesn't exceed total connections
        if self.host > self.connections:
            raise ValueError("Per-host connections cannot exceed total connections")


@dataclass
class Retry:
    """Retry configuration for failed requests.

    Defines the retry behavior for HTTP requests that fail due to
    network issues or server errors. Implements exponential backoff
    to avoid overwhelming servers during recovery periods.

    Attributes:
        total: Total number of retry attempts.
        backoff: Exponential backoff factor between retries.
        status: HTTP status codes that trigger retries.
    """

    total: int = 3  # Total number of retry attempts
    backoff: float = 1.0  # Exponential backoff factor between retries
    status: Optional[List[int]] = None  # HTTP status codes that trigger retries

    def __post_init__(self) -> None:
        """Initialize default retry status codes if not provided.

        Sets default status codes for server errors (5xx) that should
        trigger automatic retries. Also validates configuration values.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Initialize default retry status codes for server errors
        if self.status is None:
            # Common server error codes that typically benefit from retries
            self.status = [500, 502, 503, 504]

        # Validate retry configuration
        if self.total < 0:
            raise ValueError("Total retries cannot be negative")
        if self.backoff <= 0:
            raise ValueError("Backoff factor must be positive")
        if not self.status:
            raise ValueError("Status codes list cannot be empty")

        # Validate status codes are in valid HTTP range
        for code in self.status:
            if not (100 <= code <= 599):
                raise ValueError(f"Invalid HTTP status code: {code}")


@dataclass
class Timeout:
    """Timeout configuration for HTTP requests.

    Defines various timeout values to prevent requests from hanging
    indefinitely and ensure responsive behavior. Different timeout
    types handle different phases of the HTTP request lifecycle.

    Attributes:
        connect: Time to wait for initial connection establishment.
        read: Time to wait for response data after request sent.
        write: Time to wait when sending request data.
        pool: Total time limit for the entire request operation.
    """

    connect: float = 5.0  # Time to wait for initial connection establishment
    read: float = 30.0  # Time to wait for response data after request sent
    write: float = 10.0  # Time to wait when sending request data
    pool: float = 60.0  # Total time limit for the entire request operation

    def __post_init__(self) -> None:
        """Validate timeout configuration.

        Ensures that all timeout values are positive and logically
        consistent with each other.

        Returns:
            None

        Raises:
            ValueError: If timeout values are invalid.
        """
        # Validate that all timeouts are positive
        if self.connect <= 0:
            raise ValueError("Connect timeout must be positive")
        if self.read <= 0:
            raise ValueError("Read timeout must be positive")
        if self.write <= 0:
            raise ValueError("Write timeout must be positive")
        if self.pool <= 0:
            raise ValueError("Pool timeout must be positive")

        # Ensure pool timeout is reasonable compared to individual timeouts
        min_required = max(self.connect, self.read, self.write)
        if self.pool < min_required:
            raise ValueError(f"Pool timeout ({self.pool}) must be at least {min_required}")


@dataclass
class Redirects:
    """Redirect configuration for HTTP requests.

    Controls how HTTP redirects (3xx responses) are handled during
    request processing. Proper redirect handling is essential for
    following moved resources and API endpoints.

    Attributes:
        maximum: Maximum number of redirects to follow.
    """

    maximum: int = 10  # Maximum number of redirects to follow

    def __post_init__(self) -> None:
        """Validate redirect configuration.

        Ensures that redirect limits are within reasonable bounds
        to prevent infinite redirect loops and excessive resource usage.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Validate maximum redirects
        if self.maximum < 0:
            raise ValueError("Maximum redirects cannot be negative")
