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
    context: Optional[Union[ssl.SSLContext, bool]] = (
        None  # SSL context object or False to disable
    )

    def __post_init__(self) -> None:
        """Initialize SSL context based on configuration.


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
