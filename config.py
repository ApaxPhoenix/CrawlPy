from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Limits:
    """
    Connection limit configuration for the HTTP client.

    This class defines the connection pooling and keepalive settings
    to control resource usage and connection management. Proper limit
    configuration helps prevent resource exhaustion and improves
    application performance by reusing connections efficiently.

    Connection pooling reduces the overhead of establishing new connections
    for each request, while keepalive connections enable HTTP/1.1 persistent
    connections for better performance with multiple requests to the same host.

    Attributes:
        connections: Maximum total connections in the pool across all hosts.
                    Higher values allow more concurrent requests but consume more memory.
        keepalive: Maximum keepalive connections to maintain when idle.
                  These connections are kept open for reuse to improve performance.
        host: Maximum connections per individual host/domain.
              Prevents any single host from monopolizing the connection pool.
    """

    connections: int = 50  # Maximum total connections in the pool
    keepalive: int = 10  # Maximum keepalive connections to maintain
    host: int = 20  # Maximum connections per host

    def __post_init__(self) -> None:
        """
        Validate connection limit configuration after initialization.

        Ensures that the connection limits are logically consistent
        and within reasonable bounds for typical usage scenarios.
        This validation prevents common configuration errors that
        could lead to poor performance or resource exhaustion.

        The validation ensures:
        - All values are positive (negative connections don't make sense)
        - Keepalive doesn't exceed total (can't keep more than we have)
        - Per-host doesn't exceed total (logical constraint)

        Returns:
            None

        Raises:
            ValueError: If any configuration values are invalid or inconsistent.
                       Includes specific error messages for different validation failures.
        """
        # Validate that all limits are positive integers
        # Zero or negative connections would prevent any HTTP requests
        if self.connections <= 0:
            raise ValueError("Total connections must be positive")

        # Keepalive can be zero (no keepalive) but not negative
        if self.keepalive < 0:
            raise ValueError("Keepalive connections cannot be negative")

        # Per-host connections must be positive to allow requests to any host
        if self.host <= 0:
            raise ValueError("Host connections must be positive")

        # Ensure keepalive doesn't exceed total connections
        # This would be logically impossible and indicates a configuration error
        if self.keepalive > self.connections:
            raise ValueError("Keepalive connections cannot exceed total connections")

        # Ensure per-host limit doesn't exceed total connections
        # This constraint maintains pool consistency across multiple hosts
        if self.host > self.connections:
            raise ValueError("Per-host connections cannot exceed total connections")


@dataclass
class Retry:
    """
    Retry configuration for failed requests.

    Defines the retry behavior for HTTP requests that fail due to
    network issues or server errors. Implements exponential backoff
    to avoid overwhelming servers during recovery periods and reduce
    the chance of cascading failures.

    Retry logic is essential for building resilient applications that
    can handle temporary network issues, server overload, and other
    transient failures without immediate user-facing errors.

    Attributes:
        total: Total number of retry attempts after the initial request.
               Higher values increase resilience but also increase latency for persistent failures.
        backoff: Exponential backoff factor between retries.
                Starting delay = backoff * (2 ^ attempt_number).
                Helps prevent thundering herd problems during server recovery.
        status: HTTP status codes that trigger automatic retries.
                Typically includes 5xx server errors but excludes 4xx client errors.
    """

    total: int = 3  # Total number of retry attempts
    backoff: float = 1.0  # Exponential backoff factor between retries
    status: Optional[List[int]] = None  # HTTP status codes that trigger retries

    def __post_init__(self) -> None:
        """
        Initialize default retry status codes if not provided and validate configuration.

        Sets default status codes for server errors (5xx) that should
        trigger automatic retries. Client errors (4xx) are typically not
        retried as they indicate problems with the request itself.

        The validation ensures retry parameters are within reasonable bounds
        to prevent excessive retry attempts that could worsen server load.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
                       Includes specific error messages for different validation failures.
        """
        # Initialize default retry status codes for server errors
        # These codes indicate temporary server issues that may resolve with retry
        if self.status is None:
            # 500: Internal Server Error - server encountered an unexpected condition
            # 502: Bad Gateway - server received an invalid response from upstream
            # 503: Service Unavailable - server is temporarily overloaded or down
            # 504: Gateway Timeout - server didn't receive a timely response from upstream
            self.status = [500, 502, 503, 504]

        # Validate retry configuration parameters
        if self.total < 0:
            raise ValueError("Total retries cannot be negative")

        # Backoff must be positive to create meaningful delays between retries
        if self.backoff <= 0:
            raise ValueError("Backoff factor must be positive")

        # Empty status list would disable all retries, which is probably not intended
        if not self.status:
            raise ValueError("Status codes list cannot be empty")

        # Validate each status code is in the valid HTTP range
        # HTTP status codes are defined as 3-digit numbers from 100-599
        for code in self.status:
            if not (100 <= code <= 599):
                raise ValueError(f"Invalid HTTP status code: {code}")


@dataclass
class Timeout:
    """
    Timeout configuration for HTTP requests.

    Defines various timeout values to prevent requests from hanging
    indefinitely and ensure responsive behavior. Different timeout
    types handle different phases of the HTTP request lifecycle,
    allowing fine-grained control over request timing.

    Proper timeout configuration is crucial for application responsiveness
    and preventing resource exhaustion from hung connections.

    Attributes:
        connect: Time to wait for initial connection establishment.
                Covers DNS resolution and TCP handshake phases.
        read: Time to wait for response data after request sent.
              Applies to reading the response headers and body.
        write: Time to wait when sending request data.
               Important for large POST/PUT requests with significant data.
        pool: Total time limit for the entire request operation.
              Acts as a failsafe upper bound for the complete request cycle.
    """

    connect: float = 5.0  # Time to wait for initial connection establishment
    read: float = 30.0  # Time to wait for response data after request sent
    write: float = 10.0  # Time to wait when sending request data
    pool: float = 60.0  # Total time limit for the entire request operation

    def __post_init__(self) -> None:
        """
        Validate timeout configuration after initialization.

        Ensures that all timeout values are positive and logically
        consistent with each other. The pool timeout should be sufficient
        to accommodate the individual operation timeouts.

        Returns:
            None

        Raises:
            ValueError: If timeout values are invalid or inconsistent.
                       Includes specific error messages for different validation failures.
        """
        # Validate that all timeouts are positive
        # Zero or negative timeouts would either disable timeouts or be invalid
        if self.connect <= 0:
            raise ValueError("Connect timeout must be positive")
        if self.read <= 0:
            raise ValueError("Read timeout must be positive")
        if self.write <= 0:
            raise ValueError("Write timeout must be positive")
        if self.pool <= 0:
            raise ValueError("Pool timeout must be positive")

        # Ensure pool timeout is reasonable compared to individual timeouts
        # The pool timeout should be at least as long as the longest individual timeout
        # to allow operations to complete within their specific timeouts
        required = max(self.connect, self.read, self.write)
        if self.pool < required:
            raise ValueError(f"Pool timeout ({self.pool}) must be at least {required}")


@dataclass
class Redirects:
    """
    Redirect configuration for HTTP requests.

    Controls how HTTP redirects (3xx responses) are handled during
    request processing. Proper redirect handling is essential for
    following moved resources and API endpoints that have changed
    locations.

    HTTP redirects are a fundamental web mechanism for handling
    resource movement, load balancing, and API versioning. However,
    unlimited redirects can lead to infinite loops or be exploited
    for denial-of-service attacks.

    Attributes:
        limit: Maximum number of redirects to follow before giving up.
              Prevents infinite redirect loops and limits resource usage.
              Common values range from 5-30, with 10 being a reasonable default.
    """

    limit: int = 10  # Maximum number of redirects to follow

    def __post_init__(self) -> None:
        """
        Validate redirect configuration after initialization.

        Ensures that redirect limits are within reasonable bounds
        to prevent infinite redirect loops and excessive resource usage.
        A maximum of 0 effectively disables redirect following.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
                       Includes specific error messages for validation failures.
        """
        # Validate maximum redirects
        # Negative values don't make sense for redirect counts
        # Zero is valid and disables redirect following
        if self.limit < 0:
            raise ValueError("Maximum redirects cannot be negative")

        # Optional: Warn about potentially excessive redirect limits
        # Very high redirect limits might indicate a configuration error
        # or could be exploited to cause excessive resource usage
        if self.limit > 50:
            import warnings

            warnings.warn(
                f"Maximum redirects ({self.limit}) is unusually high. "
                "Consider if this is intentional to avoid potential abuse."
            )
