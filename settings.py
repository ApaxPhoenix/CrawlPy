import ssl
from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class Proxy:
    """Proxy configuration for HTTP requests.
    Defines proxy settings for routing HTTP traffic through
    intermediate servers for privacy or network requirements.
    """
    host: str  # Proxy server hostname or IP address
    port: int  # Proxy server port number
    username: Optional[str] = None  # Username for proxy authentication
    password: Optional[str] = None  # Password for proxy authentication
    headers: Optional[Dict[str, str]] = None  # Additional headers for proxy requests

    def __post_init__(self) -> None:
        """Initialize default proxy headers if not provided."""
        if self.headers is None:
            self.headers = {}


@dataclass
class SSL:
    """SSL/TLS configuration for HTTPS requests.
    Controls SSL certificate verification and encryption settings
    for secure HTTP connections.
    """
    verify: bool = True  # Whether to verify SSL certificates
    cert: Optional[str] = None  # Path to client certificate file
    key: Optional[str] = None  # Path to client private key file
    bundle: Optional[str] = None  # Path to custom CA bundle file
    ciphers: Optional[str] = None  # Allowed SSL cipher suites
    context: Optional[Union[ssl.SSLContext, bool]] = None  # SSL context object or False to disable

    def __post_init__(self) -> None:
        """Initialize SSL context based on configuration."""
        if not any([self.cert, self.key, self.bundle, self.ciphers]):
            self.context = None if self.verify else False
            return

        ctx: ssl.SSLContext = ssl.create_default_context()

        if not self.verify:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        if self.cert and self.key:
            ctx.load_cert_chain(self.cert, self.key)

        if self.bundle:
            ctx.load_verify_locations(cafile=self.bundle)

        if self.ciphers:
            ctx.set_ciphers(self.ciphers)

        self.context = ctx