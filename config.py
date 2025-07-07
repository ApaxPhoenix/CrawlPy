import aiohttp
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

    def connector(self) -> aiohttp.TCPConnector:
        """Create aiohttp TCPConnector with these limits.

        Returns:
            Configured TCPConnector instance for use with aiohttp sessions.
        """
        return aiohttp.TCPConnector(
            limit=self.connections,
            limit_per_host=self.host,
            keepalive_timeout=30,  # Default keepalive timeout
            enable_cleanup_closed=True
        )

    def available(self, count: int) -> int:
        """Calculate available connections from total pool.

        Args:
            count: Number of connections currently in use.

        Returns:
            Number of available connections remaining.
        """
        return max(0, self.connections - count)

    def exhausted(self, count: int) -> bool:
        """Check if connection pool is exhausted.

        Args:
            count: Number of connections currently in use.

        Returns:
            True if no connections are available, False otherwise.
        """
        return count >= self.connections

    def within(self, count: int) -> bool:
        """Check if connection usage is within limits.

        Args:
            count: Number of connections currently in use.

        Returns:
            True if usage is within limits, False otherwise.
        """
        return count <= self.connections

    def percentage(self, count: int) -> float:
        """Calculate percentage of connections in use.

        Args:
            count: Number of connections currently in use.

        Returns:
            Percentage of connections in use (0.0 to 1.0).
        """
        return min(1.0, count / self.connections)


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

    def delay(self, number: int) -> float:
        """Calculate delay for a specific retry attempt.

        Uses exponential backoff to calculate the delay before the next
        retry attempt. This helps avoid overwhelming servers during
        temporary outages.

        Args:
            number: Current retry attempt number (0-based).

        Returns:
            Delay in seconds before the next retry.
        """
        # Calculate exponential backoff delay
        return self.backoff * (2 ** number)

    def retriable(self, code: int) -> bool:
        """Check if a status code should trigger a retry.

        Args:
            code: HTTP status code to check.

        Returns:
            True if the status code should trigger a retry, False otherwise.
        """
        return code in self.status

    def remaining(self, number: int) -> int:
        """Calculate remaining retry attempts.

        Args:
            number: Current retry attempt number (0-based).

        Returns:
            Number of retry attempts remaining.
        """
        return max(0, self.total - number)

    def exhausted(self, number: int) -> bool:
        """Check if retry attempts are exhausted.

        Args:
            number: Current retry attempt number (0-based).

        Returns:
            True if no retry attempts remain, False otherwise.
        """
        return number >= self.total

    def available(self, number: int) -> bool:
        """Check if retry attempts are still available.

        Args:
            number: Current retry attempt number (0-based).

        Returns:
            True if retry attempts are available, False otherwise.
        """
        return number < self.total


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

    def convert(self) -> aiohttp.ClientTimeout:
        """Convert to aiohttp ClientTimeout object.

        Transforms the timeout configuration into aiohttp's native
        ClientTimeout format for use with HTTP sessions.

        Returns:
            Configured timeout object for aiohttp.
        """
        return aiohttp.ClientTimeout(
            total=self.pool,
            connect=self.connect,
            sock_read=self.read,
            sock_connect=self.connect
        )

    def elapsed(self, time: float) -> bool:
        """Check if operation duration exceeds pool timeout.

        Args:
            time: Time elapsed in seconds.

        Returns:
            True if duration exceeds pool timeout, False otherwise.
        """
        return time > self.pool

    def remaining(self, time: float) -> float:
        """Calculate remaining time before pool timeout.

        Args:
            time: Time elapsed in seconds.

        Returns:
            Remaining time in seconds before timeout.
        """
        return max(0.0, self.pool - time)

    def urgent(self, time: float) -> bool:
        """Check if timeout is approaching (80% of pool timeout).

        Args:
            time: Time elapsed in seconds.

        Returns:
            True if timeout is approaching, False otherwise.
        """
        return time > (self.pool * 0.8)

    def acceptable(self, time: float) -> bool:
        """Check if operation duration is within acceptable limits.

        Args:
            time: Time elapsed in seconds.

        Returns:
            True if duration is acceptable, False otherwise.
        """
        return time <= self.pool

    def percentage(self, time: float) -> float:
        """Calculate percentage of pool timeout used.

        Args:
            time: Time elapsed in seconds.

        Returns:
            Percentage of timeout used (0.0 to 1.0+).
        """
        return time / self.pool


@dataclass
class Redirects:
    """Redirect configuration for HTTP requests.

    Controls how HTTP redirects (3xx responses) are handled during
    request processing. Proper redirect handling is essential for
    following moved resources and API endpoints.

    Attributes:
        maximum: Maximum number of redirects to follow.
        history: Whether to maintain redirect history in response.
    """

    maximum: int = 10  # Maximum number of redirects to follow
    history: bool = True  # Whether to maintain redirect history in response

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
        if self.maximum > 30:
            raise ValueError("Maximum redirects should not exceed 30")

    def allowed(self, count: int) -> bool:
        """Check if redirect count is within allowed limits.

        Args:
            count: Current number of redirects followed.

        Returns:
            True if more redirects are allowed, False otherwise.
        """
        return count < self.maximum

    def exhausted(self, count: int) -> bool:
        """Check if redirect limit has been exhausted.

        Args:
            count: Current number of redirects followed.

        Returns:
            True if redirect limit is exhausted, False otherwise.
        """
        return count >= self.maximum

    def remaining(self, count: int) -> int:
        """Calculate remaining redirects allowed.

        Args:
            count: Current number of redirects followed.

        Returns:
            Number of redirects remaining.
        """
        return max(0, self.maximum - count)

    def trackable(self) -> bool:
        """Check if redirect history should be maintained.

        Returns:
            True if history should be tracked, False otherwise.
        """
        return self.history

    def percentage(self, count: int) -> float:
        """Calculate percentage of redirect limit used.

        Args:
            count: Current number of redirects followed.

        Returns:
            Percentage of redirect limit used (0.0 to 1.0+).
        """
        return count / self.maximum if self.maximum > 0 else 0.0