from typing import Optional, Dict, Union, TypeVar
from dataclasses import dataclass
import warnings
from config import Retry, Timeout
from settings import SSL, Proxy
from auth import Basic, Bearer, JWT, Key, OAuth

# Enhanced type definitions for improved type safety and clarity
HTTPAdapterType = TypeVar("HTTPAdapterType", bound="HTTPAdapter")
AuthType = Union[Basic, Bearer, JWT, Key, OAuth]
HeadersType = Dict[str, str]


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
    headers: Optional[HeadersType] = None
    pool: int = 10
    limit: int = 10
    verify: bool = True
    auth: Optional[AuthType] = None

    def __post_init__(self) -> None:
        """
        Validate adapter configuration and issue security warnings.

        Ensures that all configuration values are valid and consistent
        with each other for proper HTTP adapter operation. Validates
        pool sizes, concurrent request limits, and their relationships
        to prevent configuration errors that could impact performance
        or system stability. Issues security warnings for potentially
        unsafe configurations.

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

        # Security warning for disabled SSL verification
        if not self.verify:
            warnings.warn(
                "SSL certificate verification is disabled in HTTPAdapter. "
                "This makes connections vulnerable to man-in-the-middle attacks. "
                "Only use this setting in development or trusted network environments.",
                UserWarning,
                stacklevel=3,
            )

        # Security warning for authentication credentials configuration
        if self.auth:
            if isinstance(self.auth, (Basic, Bearer, JWT, Key, OAuth)):
                warnings.warn(
                    "Authentication credentials configured in HTTPAdapter. "
                    "Ensure these credentials are properly secured and the connection uses HTTPS "
                    "to protect authentication data in transit.",
                    UserWarning,
                    stacklevel=3,
                )

        # Security warning for sensitive headers
        if self.headers:
            sensitive_headers = {'authorization', 'cookie', 'x-api-key', 'x-auth-token', 'api-key'}
            found_sensitive = [
                header for header in self.headers.keys()
                if header.lower() in sensitive_headers
            ]
            if found_sensitive:
                warnings.warn(
                    f"Sensitive headers detected in HTTPAdapter configuration: {', '.join(found_sensitive)}. "
                    "Ensure these headers are properly secured and connections use HTTPS encryption.",
                    UserWarning,
                    stacklevel=3,
                )

        # Performance warning for very large pool sizes
        if self.pool > 50:
            warnings.warn(
                f"Large connection pool size configured: {self.pool}. "
                "This may consume significant system resources. "
                "Consider reducing pool size if not handling high concurrent loads.",
                UserWarning,
                stacklevel=3,
            )

        # Performance warning for very high concurrent request limits
        if self.limit > 500:
            warnings.warn(
                f"High concurrent request limit configured: {self.limit}. "
                "This may overwhelm target servers or consume excessive resources. "
                "Consider implementing proper rate limiting.",
                UserWarning,
                stacklevel=3,
            )

        # Warning for potentially unsafe proxy configuration
        if self.proxy and hasattr(self.proxy, 'username') and hasattr(self.proxy, 'password'):
            if self.proxy.username and self.proxy.password:
                warnings.warn(
                    "Proxy authentication credentials configured in HTTPAdapter. "
                    "Ensure proxy connections use secure protocols to protect credentials.",
                    UserWarning,
                    stacklevel=3,
                )

        # Warning for mismatched pool and limit configuration
        if self.limit < self.pool:
            warnings.warn(
                f"Concurrent request limit ({self.limit}) is less than connection pool size ({self.pool}). "
                "This may result in unused pooled connections and inefficient resource usage.",
                UserWarning,
                stacklevel=3,
            )