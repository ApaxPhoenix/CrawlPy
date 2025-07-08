from typing import Optional, Dict, Union
from dataclasses import dataclass
from .config import Retry, Timeout
from .settings import SSL, Proxy
from .auth import Basic, Bearer, JWT, Key, OAuth


@dataclass
class HTTPAdapter:
    """
    HTTP adapter for customizing request behavior per URL prefix.

    This class provides configuration for HTTP requests including retry
    policies, timeouts, proxy settings, SSL verification, authentication,
    and connection pooling. Each adapter can be customized for specific
    URL patterns or endpoints to handle different service requirements
    and performance characteristics.

    HTTPAdapter instances are registered with HTTP clients to manage
    requests to specific URL prefixes, enabling different configurations
    for different services. This pattern is commonly used in microservices
    architectures where endpoints may require different timeout values,
    authentication methods, or connection pool sizes.

    The adapter supports connection pooling for improved performance,
    concurrent request limiting for resource management, and various
    authentication mechanisms for secure API access. SSL verification
    can be configured based on environment requirements.

    Attributes:
        retry: Retry configuration for failed requests.
               Defines retry attempts, backoff strategies, and status codes
               that should trigger retries for transient failures.
        timeout: Timeout configuration for requests.
                 Specifies connect and read timeouts to prevent hanging
                 requests and ensure responsive behavior.
        proxy: Proxy server configuration.
               Enables routing requests through HTTP/HTTPS/SOCKS proxies
               for corporate networks or geographic routing.
        ssl: SSL/TLS configuration settings.
             Controls certificate verification, cipher suites, and
             protocol versions for secure connections.
        headers: Default headers to include with requests.
                 Common headers like User-Agent, Accept, or custom
                 API headers that should be sent with every request.
        pool: Connection pool size for this adapter.
              Number of persistent connections to maintain for reuse,
              improving performance by avoiding connection overhead.
        limit: Maximum concurrent requests allowed.
               Limits simultaneous requests to prevent resource exhaustion
               and maintain system stability under load.
        verify: Whether to verify SSL certificates.
                Should be True for production environments but can be
                disabled for development or internal services.
        auth: Authentication configuration.
              Supports Basic, Bearer, JWT, API Key, and OAuth authentication
              methods for secure API access.
    """

    retry: Optional[Retry] = None
    timeout: Optional[Timeout] = None
    proxy: Optional[Proxy] = None
    ssl: Optional[SSL] = None
    headers: Optional[Dict[str, str]] = None
    pool: int = 10
    limit: int = 10
    verify: bool = True
    auth: Optional[Union[Basic, Bearer, JWT, Key, OAuth]] = None

    def __post_init__(self) -> None:
        """
        Validate adapter configuration.

        Ensures that all configuration values are valid and consistent
        with each other for proper HTTP adapter operation. Validates
        pool sizes, concurrent request limits, and their relationships
        to prevent configuration errors that could impact performance
        or system stability.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Validate pool size is positive and reasonable
        if self.pool <= 0:
            raise ValueError("Pool size must be positive")
        if self.pool > 100:
            raise ValueError("Pool size should not exceed 100")

        # Validate maximum concurrent requests is positive and reasonable
        if self.limit <= 0:
            raise ValueError("Maximum requests must be positive")
        if self.limit > 1000:
            raise ValueError("Maximum requests should not exceed 1000")

        # Ensure maximum doesn't exceed pool size significantly
        # This prevents resource exhaustion from too many concurrent requests
        if self.limit > self.pool * 10:
            raise ValueError(
                "Maximum requests should not exceed pool size by more than 10x"
            )
