import ssl
from dataclasses import dataclass
from typing import Optional, Dict, Union, TypeVar
from pathlib import Path
import warnings

# Enhanced type definitions for improved type safety and clarity
ProxyType = TypeVar("ProxyType", bound="Proxy")
SSLType = TypeVar("SSLType", bound="SSL")
HeadersType = Dict[str, str]
SSLContextType = Union[ssl.SSLContext, bool, None]
FilePathType = str
HostType = str
PortType = int


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

    host: HostType  # Proxy server hostname or IP address
    port: PortType  # Proxy server port number
    username: Optional[str] = None  # Username for proxy authentication
    password: Optional[str] = None  # Password for proxy authentication
    headers: Optional[HeadersType] = None  # Additional headers for proxy requests

    def __post_init__(self) -> None:
        """Initialize default proxy headers and validate configuration.

        This method is automatically called after the dataclass is initialized.
        It ensures that the headers attribute is always a dictionary, validates
        proxy configuration parameters, and issues security warnings for
        potentially unsafe configurations.

        Returns:
            None

        Raises:
            ValueError: If proxy configuration is invalid.
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

        # Security warning for authentication credentials without proper validation
        if self.username and self.password:
            warnings.warn(
                "Proxy credentials are being used. Ensure the proxy connection "
                "uses HTTPS/TLS to protect authentication data in transit. "
                "Credentials sent over unencrypted connections can be intercepted.",
                UserWarning,
                stacklevel=3,
            )

        # Security warning for username without password (likely misconfiguration)
        if self.username and not self.password:
            warnings.warn(
                "Proxy username provided without password. This may indicate "
                "a configuration error or incomplete authentication setup.",
                UserWarning,
                stacklevel=3,
            )

        # Security warning for password without username (likely misconfiguration)
        if self.password and not self.username:
            warnings.warn(
                "Proxy password provided without username. This may indicate "
                "a configuration error or incomplete authentication setup.",
                UserWarning,
                stacklevel=3,
            )

        # Security warning for potentially unsafe proxy hosts
        if self.host.lower() in ['localhost', '127.0.0.1', '::1']:
            warnings.warn(
                "Using localhost proxy configuration. Ensure this is intended "
                "and the local proxy service is properly secured and configured.",
                UserWarning,
                stacklevel=3,
            )

        # Security warning for custom headers that might contain sensitive data
        if self.headers:
            sensitive_headers = {'authorization', 'cookie', 'x-api-key', 'x-auth-token'}
            found_sensitive = [
                header for header in self.headers.keys()
                if header.lower() in sensitive_headers
            ]
            if found_sensitive:
                warnings.warn(
                    f"Sensitive headers detected in proxy configuration: {', '.join(found_sensitive)}. "
                    "Ensure these headers are properly secured and the proxy connection uses encryption.",
                    UserWarning,
                    stacklevel=3,
                )


@dataclass
class SSL:
    """
    SSL/TLS configuration for HTTPS requests.

    Controls SSL certificate verification and encryption settings for secure
    HTTP connections. Provides flexible configuration options for various
    SSL/TLS scenarios including custom certificates, CA bundles, and cipher suites.

    SSL/TLS configuration is critical for secure communication and proper
    certificate validation. This class provides both simple verification
    control and advanced configuration options for enterprise environments
    requiring client certificates, custom CA bundles, or specific cipher suites.

    Attributes:
        verify: Whether to verify SSL certificates against trusted CAs.
               When False, connections are vulnerable to man-in-the-middle attacks
               but may be necessary for development or internal services with self-signed certs.
        cert: Path to client certificate file for mutual TLS authentication.
              Required for services that validate client identity through certificates.
        key: Path to client private key file for mutual TLS authentication.
             Must correspond to the certificate specified in 'cert' parameter.
        bundle: Path to custom CA bundle file for certificate verification.
                Useful for private CAs or additional trusted certificate authorities.
        ciphers: Allowed SSL cipher suites string for encryption control.
                Format follows OpenSSL cipher list format for fine-grained security control.
        context: Pre-configured SSL context object or False to disable verification.
                Allows complete control over SSL settings when default configuration insufficient.
    """

    verify: bool = True  # Whether to verify SSL certificates against trusted CAs
    cert: Optional[FilePathType] = None  # Path to client certificate file for mutual TLS
    key: Optional[FilePathType] = None  # Path to client private key file for mutual TLS
    bundle: Optional[FilePathType] = None  # Path to custom CA bundle file for verification
    ciphers: Optional[str] = None  # Allowed SSL cipher suites string
    context: SSLContextType = None  # SSL context or False to disable

    def __post_init__(self) -> None:
        """
        Validate SSL configuration and initialize SSL context after initialization.

        Performs comprehensive validation of SSL parameters to ensure they are
        consistent and point to valid files. Creates an appropriate SSL context
        based on the configuration, handling various scenarios from simple
        verification control to complex enterprise setups.

        The method validates file paths, certificate/key pairs, and SSL context
        compatibility. It provides clear error messages for common configuration
        mistakes and security warnings for potentially unsafe configurations.

        Returns:
            None

        Raises:
            ValueError: If SSL configuration is invalid or inconsistent.
                       Includes specific error messages for different validation failures.
        """
        # Validate certificate and key file pairing
        # Both must be provided together for mutual TLS authentication
        if bool(self.cert) != bool(self.key):
            raise ValueError(
                "Both certificate and key must be provided together for mutual TLS"
            )

        # Validate certificate file existence and readability
        if self.cert:
            path: Path = Path(self.cert)
            if not path.exists():
                raise ValueError(f"Certificate file not found: {self.cert}")
            if not path.is_file():
                raise ValueError(f"Certificate path is not a file: {self.cert}")

        # Validate private key file existence and readability
        if self.key:
            path = Path(self.key)
            if not path.exists():
                raise ValueError(f"Private key file not found: {self.key}")
            if not path.is_file():
                raise ValueError(f"Private key path is not a file: {self.key}")

        # Validate CA bundle file existence and readability
        if self.bundle:
            path = Path(self.bundle)
            if not path.exists():
                raise ValueError(f"CA bundle file not found: {self.bundle}")
            if not path.is_file():
                raise ValueError(f"CA bundle path is not a file: {self.bundle}")

        # Validate SSL context parameter type
        if self.context is not None and not isinstance(
                self.context, (ssl.SSLContext, bool)
        ):
            raise ValueError(
                "SSL context must be an SSLContext object, boolean, or None"
            )

        # Security warning for disabled certificate verification
        if not self.verify:
            warnings.warn(
                "SSL certificate verification is disabled. "
                "This makes connections vulnerable to man-in-the-middle attacks. "
                "Only use this setting in development or trusted network environments.",
                UserWarning,
                stacklevel=3,
            )

        # Warn about potentially incompatible configuration
        if self.context is False and any(
                [self.cert, self.key, self.bundle, self.ciphers]
        ):
            warnings.warn(
                "SSL context is explicitly disabled, but other SSL parameters are configured. "
                "These parameters will be ignored.",
                UserWarning,
                stacklevel=3,
            )

        # Initialize SSL context based on validated configuration parameters
        # If context is already explicitly set, don't override it
        if self.context is not None:
            return

        # For simple verification control without advanced features
        if not any([self.cert, self.key, self.bundle, self.ciphers]):
            # Use None for default verification, False for disabled verification
            self.context = None if self.verify else False
            return

        # Create SSL context with secure default settings for advanced configuration
        try:
            ctx: ssl.SSLContext = ssl.create_default_context()
        except ssl.SSLError as error:
            raise ValueError(f"Failed to create default SSL context: {error}")

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
            except ssl.SSLError as error:
                raise ValueError(f"Failed to load client certificate chain: {error}")
            except FileNotFoundError as error:
                raise ValueError(f"Certificate or key file not found: {error}")
            except PermissionError as error:
                raise ValueError(
                    f"Permission denied accessing certificate files: {error}"
                )

        # Load custom CA bundle for certificate verification
        if self.bundle:
            try:
                ctx.load_verify_locations(cafile=self.bundle)
            except ssl.SSLError as error:
                raise ValueError(f"Failed to load CA bundle: {error}")
            except FileNotFoundError as error:
                raise ValueError(f"CA bundle file not found: {error}")
            except PermissionError as error:
                raise ValueError(f"Permission denied accessing CA bundle: {error}")

        # Configure allowed cipher suites for encryption control
        if self.ciphers:
            try:
                ctx.set_ciphers(self.ciphers)
            except ssl.SSLError as error:
                raise ValueError(f"Invalid cipher suite configuration: {error}")

        # Store the configured SSL context
        self.context = ctx