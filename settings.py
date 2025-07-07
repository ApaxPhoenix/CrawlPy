import ssl
from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class Proxy:
    """Proxy configuration for HTTP requests.

    Defines proxy settings for routing HTTP traffic through intermediate servers
    for privacy, security, or network requirements. Supports both authenticated
    and anonymous proxy connections with custom headers.

    Attributes:
        host: Proxy server hostname or IP address.
        port: Proxy server port number.
        username: Username for proxy authentication (optional).
        password: Password for proxy authentication (optional).
        headers: Additional headers to send with proxy requests (optional).
    """

    host: str  # Proxy server hostname or IP address
    port: int  # Proxy server port number
    username: Optional[str] = None  # Username for proxy authentication
    password: Optional[str] = None  # Password for proxy authentication
    headers: Optional[Dict[str, str]] = None  # Additional headers for proxy requests

    def __post_init__(self) -> None:
        """Initialize default proxy headers if not provided.

        This method is automatically called after the dataclass is initialized.
        It ensures that the headers attribute is always a dictionary, even if
        None was provided during initialization.

        Returns:
            None
        """
        # Initialize empty headers dictionary if none provided
        # This prevents None reference errors when accessing headers
        if self.headers is None:
            self.headers = {}

        # Validate proxy configuration
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        if not self.host.strip():
            raise ValueError("Host cannot be empty")

    def authenticated(self) -> bool:
        """Check if proxy requires authentication.

        Returns:
            True if username and password are provided, False otherwise.
        """
        return self.username is not None and self.password is not None

    def anonymous(self) -> bool:
        """Check if proxy is configured for anonymous access.

        Returns:
            True if no authentication is configured, False otherwise.
        """
        return not self.authenticated()

    def url(self) -> str:
        """Generate proxy URL string.

        Returns:
            Formatted proxy URL with or without authentication.
        """
        if self.authenticated():
            return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"http://{self.host}:{self.port}"

    def address(self) -> str:
        """Get proxy address without authentication.

        Returns:
            Proxy address in host:port format.
        """
        return f"{self.host}:{self.port}"

    def secured(self) -> bool:
        """Check if proxy connection uses HTTPS.

        Returns:
            True if proxy uses secure connection, False otherwise.
        """
        return self.port == 443 or self.port == 8443

    def standard(self) -> bool:
        """Check if proxy uses standard HTTP port.

        Returns:
            True if using standard ports (80, 8080, 3128), False otherwise.
        """
        return self.port in [80, 8080, 3128]

    def valid(self) -> bool:
        """Check if proxy configuration is valid.

        Returns:
            True if configuration is valid, False otherwise.
        """
        return (
                bool(self.host.strip()) and
                1 <= self.port <= 65535 and
                (not self.username or bool(self.username.strip())) and
                (not self.password or bool(self.password.strip()))
        )

    def merge(self, other: 'Proxy') -> 'Proxy':
        """Merge configuration from another proxy.

        Args:
            other: Another Proxy to merge configuration from.

        Returns:
            New Proxy with merged configuration.
        """
        merged_headers = {}
        if self.headers:
            merged_headers.update(self.headers)
        if other.headers:
            merged_headers.update(other.headers)

        return Proxy(
            host=other.host if other.host else self.host,
            port=other.port if other.port else self.port,
            username=other.username if other.username else self.username,
            password=other.password if other.password else self.password,
            headers=merged_headers if merged_headers else None
        )

    def clone(self) -> 'Proxy':
        """Create a copy of this proxy configuration.

        Returns:
            New Proxy with identical configuration.
        """
        return Proxy(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            headers=self.headers.copy() if self.headers else None
        )


@dataclass
class SSL:
    """SSL/TLS configuration for HTTPS requests.

    Controls SSL certificate verification and encryption settings for secure
    HTTP connections. Provides flexible configuration options for various
    SSL/TLS scenarios including custom certificates, CA bundles, and cipher suites.

    Attributes:
        verify: Whether to verify SSL certificates against trusted CAs.
        cert: Path to client certificate file for mutual TLS authentication.
        key: Path to client private key file for mutual TLS authentication.
        bundle: Path to custom CA bundle file for certificate verification.
        ciphers: Allowed SSL cipher suites string for encryption control.
        context: SSL context object or False to disable SSL verification.
    """

    verify: bool = True  # Whether to verify SSL certificates
    cert: Optional[str] = None  # Path to client certificate file
    key: Optional[str] = None  # Path to client private key file
    bundle: Optional[str] = None  # Path to custom CA bundle file
    ciphers: Optional[str] = None  # Allowed SSL cipher suites
    context: Optional[Union[ssl.SSLContext, bool]] = None  # SSL context object or False to disable

    def __post_init__(self) -> None:
        """Initialize SSL context based on configuration.

        This method automatically creates an appropriate SSL context based on
        the provided configuration options. It handles various scenarios:
        - Basic verification (default behavior)
        - Custom client certificates for mutual TLS
        - Custom CA bundles for private certificate authorities
        - Custom cipher suites for specific security requirements
        - Disabled verification for testing environments

        Returns:
            None
        """
        # Check if any advanced SSL configuration is provided
        # If not, use simple verification settings
        if not any([self.cert, self.key, self.bundle, self.ciphers]):
            # Set context to None for normal verification, False to disable
            self.context = None if self.verify else False
            return

        # Create default SSL context with secure settings
        ctx: ssl.SSLContext = ssl.create_default_context()

        # Configure certificate verification behavior
        if not self.verify:
            # Disable hostname checking and certificate verification
            # WARNING: This makes connections vulnerable to man-in-the-middle attacks
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        # Load client certificate and private key for mutual TLS authentication
        if self.cert and self.key:
            try:
                ctx.load_cert_chain(self.cert, self.key)
            except (ssl.SSLError, FileNotFoundError) as error:
                raise ValueError(f"Failed to load client certificate: {error}")

        # Load custom CA bundle for certificate verification
        if self.bundle:
            try:
                ctx.load_verify_locations(cafile=self.bundle)
            except (ssl.SSLError, FileNotFoundError) as error:
                raise ValueError(f"Failed to load CA bundle: {error}")

        # Configure allowed cipher suites for encryption
        if self.ciphers:
            try:
                ctx.set_ciphers(self.ciphers)
            except ssl.SSLError as error:
                raise ValueError(f"Invalid cipher suite configuration: {error}")

        # Store the configured SSL context
        self.context = ctx

    def enabled(self) -> bool:
        """Check if SSL verification is enabled.

        Returns:
            True if SSL verification is enabled, False otherwise.
        """
        return self.verify and self.context is not False

    def disabled(self) -> bool:
        """Check if SSL verification is disabled.

        Returns:
            True if SSL verification is disabled, False otherwise.
        """
        return not self.verify or self.context is False

    def mutual(self) -> bool:
        """Check if mutual TLS authentication is configured.

        Returns:
            True if client certificate and key are provided, False otherwise.
        """
        return self.cert is not None and self.key is not None

    def custom(self) -> bool:
        """Check if custom SSL configuration is used.

        Returns:
            True if any custom SSL settings are configured, False otherwise.
        """
        return any([self.cert, self.key, self.bundle, self.ciphers])

    def bundled(self) -> bool:
        """Check if custom CA bundle is configured.

        Returns:
            True if custom CA bundle is set, False otherwise.
        """
        return self.bundle is not None

    def ciphered(self) -> bool:
        """Check if custom cipher suites are configured.

        Returns:
            True if custom ciphers are set, False otherwise.
        """
        return self.ciphers is not None

    def secured(self) -> bool:
        """Check if SSL provides secure configuration.

        Returns:
            True if SSL is properly configured for security, False otherwise.
        """
        return self.verify and self.context is not False

    def insecure(self) -> bool:
        """Check if SSL configuration is insecure.

        Returns:
            True if SSL verification is disabled, False otherwise.
        """
        return not self.verify or self.context is False

    def valid(self) -> bool:
        """Check if SSL configuration is valid.

        Returns:
            True if configuration is valid, False otherwise.
        """
        try:
            # Basic validation
            if self.cert and not self.key:
                return False
            if self.key and not self.cert:
                return False

            # If context is already set, assume it's valid
            if self.context is not None:
                return True

            return True
        except Exception:
            return False

    def strength(self) -> str:
        """Get SSL security strength level.

        Returns:
            String indicating security strength: 'high', 'medium', 'low', or 'none'.
        """
        if self.disabled():
            return 'none'
        if self.mutual() and self.bundled():
            return 'high'
        if self.mutual() or self.bundled():
            return 'medium'
        return 'low'

    def clone(self) -> 'SSL':
        """Create a copy of this SSL configuration.

        Returns:
            New SSL with identical configuration.
        """
        return SSL(
            verify=self.verify,
            cert=self.cert,
            key=self.key,
            bundle=self.bundle,
            ciphers=self.ciphers,
            context=self.context
        )

    def merge(self, other: 'SSL') -> 'SSL':
        """Merge configuration from another SSL config.

        Args:
            other: Another SSL to merge configuration from.

        Returns:
            New SSL with merged configuration.
        """
        return SSL(
            verify=other.verify if other.verify != True else self.verify,
            cert=other.cert if other.cert else self.cert,
            key=other.key if other.key else self.key,
            bundle=other.bundle if other.bundle else self.bundle,
            ciphers=other.ciphers if other.ciphers else self.ciphers,
            context=other.context if other.context else self.context
        )