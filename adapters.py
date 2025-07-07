from typing import Optional, Dict, Union
from dataclasses import dataclass
from config import Retry, Timeout
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth


@dataclass
class HTTPAdapter:
    """HTTP adapter for customizing request behavior per URL prefix.

    This class provides configuration for HTTP requests including retry
    policies, timeouts, proxy settings, SSL verification, authentication,
    and connection pooling. Each adapter can be customized for specific
    URL patterns or endpoints.

    Attributes:
        retry: Retry configuration for failed requests.
        timeout: Timeout configuration for requests.
        proxy: Proxy server configuration.
        ssl: SSL/TLS configuration settings.
        headers: Default headers to include with requests.
        pool: Connection pool size for this adapter.
        maximum: Maximum concurrent requests allowed.
        verify: Whether to verify SSL certificates.
        auth: Authentication configuration.
    """

    retry: Optional[Retry] = None
    timeout: Optional[Timeout] = None
    proxy: Optional[Proxy] = None
    ssl: Optional[SSL] = None
    headers: Optional[Dict[str, str]] = None
    pool: int = 10
    maximum: int = 10
    verify: bool = True
    auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None

    def __post_init__(self) -> None:
        """Validate adapter configuration.

        Ensures that all configuration values are valid and consistent
        with each other for proper HTTP adapter operation.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Validate pool size
        if self.pool <= 0:
            raise ValueError("Pool size must be positive")
        if self.pool > 100:
            raise ValueError("Pool size should not exceed 100")

        # Validate maximum concurrent requests
        if self.maximum <= 0:
            raise ValueError("Maximum requests must be positive")
        if self.maximum > 1000:
            raise ValueError("Maximum requests should not exceed 1000")

        # Ensure maximum doesn't exceed pool size significantly
        if self.maximum > self.pool * 10:
            raise ValueError("Maximum requests should not exceed pool size by more than 10x")

    def configured(self) -> bool:
        """Check if adapter has any configuration set.

        Returns:
            True if any configuration is set, False otherwise.
        """
        return any([
            self.retry is not None,
            self.timeout is not None,
            self.proxy is not None,
            self.ssl is not None,
            self.headers is not None,
            self.auth is not None
        ])

    def secured(self) -> bool:
        """Check if adapter has security configuration.

        Returns:
            True if SSL verification is enabled or auth is configured.
        """
        return self.verify or self.auth is not None

    def authenticated(self) -> bool:
        """Check if adapter has authentication configured.

        Returns:
            True if authentication is configured, False otherwise.
        """
        return self.auth is not None

    def proxied(self) -> bool:
        """Check if adapter uses a proxy server.

        Returns:
            True if proxy is configured, False otherwise.
        """
        return self.proxy is not None

    def retriable(self) -> bool:
        """Check if adapter has retry configuration.

        Returns:
            True if retry configuration is set, False otherwise.
        """
        return self.retry is not None

    def timed(self) -> bool:
        """Check if adapter has timeout configuration.

        Returns:
            True if timeout configuration is set, False otherwise.
        """
        return self.timeout is not None

    def available(self, active: int) -> int:
        """Calculate available connections in the pool.

        Args:
            active: Number of currently active connections.

        Returns:
            Number of available connections remaining.
        """
        return max(0, self.pool - active)

    def exhausted(self, active: int) -> bool:
        """Check if connection pool is exhausted.

        Args:
            active: Number of currently active connections.

        Returns:
            True if no connections are available, False otherwise.
        """
        return active >= self.pool

    def overloaded(self, requests: int) -> bool:
        """Check if adapter is handling too many requests.

        Args:
            requests: Number of current concurrent requests.

        Returns:
            True if request count exceeds maximum, False otherwise.
        """
        return requests >= self.maximum

    def capacity(self, requests: int) -> int:
        """Calculate remaining request capacity.

        Args:
            requests: Number of current concurrent requests.

        Returns:
            Number of additional requests that can be handled.
        """
        return max(0, self.maximum - requests)

    def utilization(self, active: int) -> float:
        """Calculate pool utilization percentage.

        Args:
            active: Number of currently active connections.

        Returns:
            Pool utilization as percentage (0.0 to 1.0+).
        """
        return active / self.pool

    def load(self, requests: int) -> float:
        """Calculate request load percentage.

        Args:
            requests: Number of current concurrent requests.

        Returns:
            Request load as percentage (0.0 to 1.0+).
        """
        return requests / self.maximum

    def merge(self, other: 'HTTPAdapter') -> 'HTTPAdapter':
        """Merge configuration from another adapter.

        Creates a new adapter with configuration from this adapter
        overridden by non-None values from the other adapter.

        Args:
            other: Another HTTPAdapter to merge configuration from.

        Returns:
            New HTTPAdapter with merged configuration.
        """
        merged_headers = None
        if self.headers or other.headers:
            merged_headers = {}
            if self.headers:
                merged_headers.update(self.headers)
            if other.headers:
                merged_headers.update(other.headers)

        return HTTPAdapter(
            retry=other.retry if other.retry is not None else self.retry,
            timeout=other.timeout if other.timeout is not None else self.timeout,
            proxy=other.proxy if other.proxy is not None else self.proxy,
            ssl=other.ssl if other.ssl is not None else self.ssl,
            headers=merged_headers,
            pool=other.pool if other.pool != 10 else self.pool,
            maximum=other.maximum if other.maximum != 10 else self.maximum,
            verify=other.verify if other.verify != True else self.verify,
            auth=other.auth if other.auth is not None else self.auth
        )

    def clone(self) -> 'HTTPAdapter':
        """Create a copy of this adapter.

        Returns:
            New HTTPAdapter with identical configuration.
        """
        return HTTPAdapter(
            retry=self.retry,
            timeout=self.timeout,
            proxy=self.proxy,
            ssl=self.ssl,
            headers=self.headers.copy() if self.headers else None,
            pool=self.pool,
            maximum=self.maximum,
            verify=self.verify,
            auth=self.auth
        )

    def reset(self) -> None:
        """Reset adapter to default configuration.

        Clears all configuration and resets to default values.
        """
        self.retry = None
        self.timeout = None
        self.proxy = None
        self.ssl = None
        self.headers = None
        self.pool = 10
        self.maximum = 10
        self.verify = True
        self.auth = None