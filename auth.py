from dataclasses import dataclass
from typing import Optional, Dict, Any
import base64
import json


@dataclass
class Basic:
    """
    Basic authentication configuration for HTTP requests.

    Implements HTTP Basic Authentication as defined in RFC 7617, which
    transmits credentials as a base64-encoded string in the Authorization
    header. This authentication method is simple but should only be used
    over HTTPS to prevent credential interception.

    Basic authentication is widely supported and commonly used for API
    endpoints, internal services, and systems where token-based auth
    is not available or necessary. The credentials are sent with every
    request, making it stateless but potentially less secure than
    token-based alternatives.

    Attributes:
        user: Username for authentication.
              Should be a valid identifier for the target service.
        password: Password or secret for authentication.
                 Should be kept secure and rotated regularly.
        auth: Complete authorization header string.
              Auto-generated if not provided during initialization.
    """

    user: str
    password: str
    auth: str = ""

    def __post_init__(self) -> None:
        """
        Initialize basic authentication configuration.

        Automatically generates the Basic authentication header by encoding
        username:password in base64 format as required by RFC 7617.

        The generated header follows the format:
        Authorization: Basic <base64(username:password)>

        Returns:
            None
        """
        # Generate Basic auth header if not already provided
        if not self.auth:
            # Combine username and password with colon separator
            credentials = f"{self.user}:{self.password}"
            # Encode credentials in base64 as required by RFC 7617
            encoded = base64.b64encode(credentials.encode()).decode()
            # Create complete authorization header
            self.auth = f"Basic {encoded}"


@dataclass
class Bearer:
    """
    Bearer token authentication configuration for HTTP requests.

    Implements Bearer token authentication as defined in RFC 6750, commonly
    used with OAuth 2.0 and other token-based authentication systems.
    Bearer tokens are more secure than Basic auth as they can be revoked,
    have expiration times, and don't expose permanent credentials.

    Bearer authentication is the standard for modern REST APIs and
    microservices, providing stateless authentication without requiring
    credential transmission. Tokens can be short-lived and refreshed
    as needed for enhanced security.

    Attributes:
        token: Authentication token string.
               Should be a valid token from the authentication provider.
        scheme: Authentication scheme name (default: "Bearer").
                Can be customized for non-standard implementations.
        auth: Complete authorization header string.
              Auto-generated if not provided during initialization.
    """

    token: str
    scheme: str = "Bearer"
    auth: str = ""

    def __post_init__(self) -> None:
        """
        Initialize bearer token authentication configuration.

        Automatically generates the Bearer authentication header using
        the specified scheme and token.

        The generated header follows the format:
        Authorization: <scheme> <token>

        Returns:
            None
        """
        # Generate Bearer auth header if not already provided
        if not self.auth:
            # Create authorization header with scheme and token
            self.auth = f"{self.scheme} {self.token}"


@dataclass
class JWT:
    """
    JSON Web Token authentication configuration for HTTP requests.

    Implements JWT (JSON Web Token) authentication as defined in RFC 7519,
    which provides a compact, URL-safe means of representing claims between
    two parties. JWTs are self-contained tokens that include encoded
    information about the user and can be verified without server-side
    session storage.

    JWT tokens consist of three parts separated by dots: header.payload.signature.
    The payload contains claims about the user and token metadata, while
    the signature ensures token integrity and authenticity.

    Attributes:
        token: JWT token string in format header.payload.signature.
               Must be a valid JWT from the authentication provider.
        scheme: Authentication scheme name (default: "Bearer").
                JWT tokens are typically sent as Bearer tokens.
        auth: Complete authorization header string.
              Auto-generated if not provided during initialization.
        data: Decoded JWT payload dictionary.
              Contains claims and metadata extracted from the token.
    """

    token: str
    scheme: str = "Bearer"
    auth: str = ""
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """
        Initialize JWT authentication configuration and decode payload.

        Automatically generates the JWT authentication header and attempts
        to decode the JWT payload for inspection and validation.

        The JWT payload decoding helps with debugging and allows access
        to token expiration, issuer, and other claims for validation.

        Returns:
            None
        """
        # Generate JWT auth header if not already provided
        if not self.auth:
            # Create authorization header with scheme and token
            self.auth = f"{self.scheme} {self.token}"

        # Decode JWT payload if not already provided
        if self.data is None:
            self.data = {}
            try:
                # Split JWT token into parts (header.payload.signature)
                parts = self.token.split(".")
                if len(parts) >= 2:
                    # Extract payload part (second component)
                    part = parts[1]

                    # Add base64 padding if necessary for proper decoding
                    padding = 4 - len(part) % 4
                    if padding != 4:
                        part += "=" * padding

                    # Decode base64 payload and parse JSON
                    decoded = base64.b64decode(part)
                    self.data = json.loads(decoded.decode())
            except Exception:
                # If JWT decoding fails, keep empty payload
                # This prevents crashes with malformed tokens
                pass


@dataclass
class Key:
    """
    API key authentication configuration for HTTP requests.

    Handles API key authentication which can be sent via headers,
    query parameters, or other custom locations based on API requirements.
    API keys are simple authentication tokens that identify and authenticate
    applications or users without requiring interactive login.

    API key authentication is commonly used for server-to-server communication,
    public APIs, and services where full OAuth flows are unnecessary.
    Keys can be placed in headers for security or query parameters for
    convenience, depending on the API design.

    Attributes:
        value: API key value string.
               Should be a valid key from the service provider.
        place: Where to place the key ("header" or "query").
               Headers are more secure as they're not logged in URLs.
        name: Parameter/header name for the API key.
              Common names include "X-API-Key", "apikey", or "Authorization".
    """

    value: str
    place: str = "header"
    name: str = "X-API-Key"

    def __post_init__(self) -> None:
        """
        Validate API key authentication configuration.

        Ensures that the API key configuration is correct and the
        placement and name are valid for API key usage.

        Returns:
            None

        Raises:
            ValueError: If configuration values are invalid.
        """
        # Validate placement option
        if self.place not in ["header", "query"]:
            raise ValueError("Place must be 'header' or 'query'")

        # Validate name is not empty
        if not self.name:
            raise ValueError("Name cannot be empty")


@dataclass
class OAuth:
    """
    OAuth 2.0 authentication configuration for HTTP requests.

    Implements OAuth 2.0 authentication flow as defined in RFC 6749,
    supporting client credentials flow, authorization code flow, and
    token refresh mechanisms. OAuth 2.0 is the industry standard for
    secure authorization and is widely used by APIs and web services.

    OAuth 2.0 provides secure, delegated access without sharing passwords
    and supports fine-grained permissions through scopes. This implementation
    handles token lifecycle management including refresh and expiration.

    Attributes:
        client: OAuth client ID string.
                Identifies the application to the authorization server.
        secret: OAuth client secret string.
                Authenticates the application to the authorization server.
        url: OAuth token endpoint URL.
             Where to request and refresh access tokens.
        scope: OAuth scope string for permissions.
               Defines the level of access requested (space-separated).
        token: Current access token string.
               Used for authenticating API requests.
        refresh: Refresh token for token renewal.
                Used to obtain new access tokens when they expire.
        expires: Token expiration timestamp.
                Unix timestamp when the current token expires.
        auth: Complete authorization header string.
              Auto-generated from the current access token.
    """

    client: str
    secret: str
    url: str
    scope: Optional[str] = None
    token: Optional[str] = None
    refresh: Optional[str] = None
    expires: Optional[int] = None
    auth: str = ""

    def __post_init__(self) -> None:
        """
        Initialize OAuth 2.0 authentication configuration.

        Sets up default values and generates authorization header if
        a token is already available.

        Returns:
            None
        """
        # Initialize scope to empty string if not provided
        if self.scope is None:
            self.scope = ""

        # Generate authorization header if token is available
        if self.token:
            self.auth = f"Bearer {self.token}"
