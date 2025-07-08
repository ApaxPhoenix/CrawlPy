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
            raise ValueError(
                "Maximum requests should not exceed pool size by more than 10x"
            )
