from dataclasses import dataclass
from typing import Optional, Dict, Any, TypeVar
import base64
import json
import warnings

# Enhanced type definitions for improved type safety and clarity
BasicType = TypeVar("BasicType", bound="Basic")
BearerType = TypeVar("BearerType", bound="Bearer")
JWTType = TypeVar("JWTType", bound="JWT")
KeyType = TypeVar("KeyType", bound="Key")
OAuthType = TypeVar("OAuthType", bound="OAuth")
CredentialsType = str
TokenType = str
AuthHeaderType = str
JWTPayloadType = Dict[str, Any]
APIKeyPlaceType = str
APIKeyNameType = str
ScopeType = str
URLType = str
TimestampType = int


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

    user: CredentialsType
    password: CredentialsType
    auth: AuthHeaderType = ""

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
        # Validate credentials are not empty
        if not self.user.strip():
            raise ValueError("Username cannot be empty")
        if not self.password.strip():
            raise ValueError("Password cannot be empty")

        # Generate Basic auth header if not already provided
        if not self.auth:
            # Combine username and password with colon separator
            credentials: str = f"{self.user}:{self.password}"
            # Encode credentials in base64 as required by RFC 7617
            encoded: str = base64.b64encode(credentials.encode()).decode()
            # Create complete authorization header
            self.auth = f"Basic {encoded}"

        # Security warning about Basic authentication
        warnings.warn(
            "Basic authentication transmits credentials with every request. "
            "Ensure connections use HTTPS to protect credentials in transit. "
            "Consider using token-based authentication for better security.",
            UserWarning,
            stacklevel=3,
        )

        # Warning for weak passwords
        if len(self.password) < 8:
            warnings.warn(
                f"Password is only {len(self.password)} characters long. "
                "Consider using stronger passwords with at least 8 characters.",
                UserWarning,
                stacklevel=3,
            )


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

    token: TokenType
    scheme: str = "Bearer"
    auth: AuthHeaderType = ""

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
        # Validate token is not empty
        if not self.token.strip():
            raise ValueError("Token cannot be empty")

        # Validate scheme is not empty
        if not self.scheme.strip():
            raise ValueError("Scheme cannot be empty")

        # Generate Bearer auth header if not already provided
        if not self.auth:
            # Create authorization header with scheme and token
            self.auth = f"{self.scheme} {self.token}"

        # Security warning for very short tokens
        if len(self.token) < 16:
            warnings.warn(
                f"Token is only {len(self.token)} characters long. "
                "Very short tokens may be less secure and easier to guess.",
                UserWarning,
                stacklevel=3,
            )


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

    token: TokenType
    scheme: str = "Bearer"
    auth: AuthHeaderType = ""
    data: Optional[JWTPayloadType] = None

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
        # Validate token is not empty
        if not self.token.strip():
            raise ValueError("JWT token cannot be empty")

        # Validate token has correct JWT format (three parts separated by dots)
        parts = self.token.split(".")
        if len(parts) != 3:
            warnings.warn(
                "JWT token does not have the expected format (header.payload.signature). "
                "This may not be a valid JWT token.",
                UserWarning,
                stacklevel=3,
            )

        # Generate JWT auth header if not already provided
        if not self.auth:
            # Create authorization header with scheme and token
            self.auth = f"{self.scheme} {self.token}"

        # Decode JWT payload if not already provided
        if self.data is None:
            self.data = {}
            try:
                # Extract payload part (second component)
                if len(parts) >= 2:
                    part: str = parts[1]

                    # Add base64 padding if necessary for proper decoding
                    padding: int = 4 - len(part) % 4
                    if padding != 4:
                        part += "=" * padding

                    # Decode base64 payload and parse JSON
                    decoded: bytes = base64.b64decode(part)
                    self.data = json.loads(decoded.decode())

                    # Check for token expiration if present
                    if 'exp' in self.data:
                        import time
                        current_time = int(time.time())
                        if self.data['exp'] < current_time:
                            warnings.warn(
                                "JWT token appears to be expired based on 'exp' claim. "
                                "Authentication may fail.",
                                UserWarning,
                                stacklevel=3,
                            )
            except Exception:
                # If JWT decoding fails, keep empty payload
                # This prevents crashes with malformed tokens
                warnings.warn(
                    "Failed to decode JWT payload. Token may be malformed.",
                    UserWarning,
                    stacklevel=3,
                )


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

    value: TokenType
    place: APIKeyPlaceType = "header"
    name: APIKeyNameType = "X-API-Key"

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
        # Validate API key value is not empty
        if not self.value.strip():
            raise ValueError("API key value cannot be empty")

        # Validate placement option
        if self.place not in ["header", "query"]:
            raise ValueError("Place must be 'header' or 'query'")

        # Validate name is not empty
        if not self.name.strip():
            raise ValueError("Name cannot be empty")

        # Security warning for query parameter placement
        if self.place == "query":
            warnings.warn(
                "API key is configured to be sent as a query parameter. "
                "Query parameters may be logged in server logs and browser history. "
                "Consider using header placement for better security.",
                UserWarning,
                stacklevel=3,
            )

        # Warning for short API keys
        if len(self.value) < 16:
            warnings.warn(
                f"API key is only {len(self.value)} characters long. "
                "Short API keys may be less secure and easier to guess.",
                UserWarning,
                stacklevel=3,
            )


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

    client: CredentialsType
    secret: CredentialsType
    url: URLType
    scope: Optional[ScopeType] = None
    token: Optional[TokenType] = None
    refresh: Optional[TokenType] = None
    expires: Optional[TimestampType] = None
    auth: AuthHeaderType = ""

    def __post_init__(self) -> None:
        """
        Initialize OAuth 2.0 authentication configuration.

        Sets up default values and generates authorization header if
        a token is already available.

        Returns:
            None
        """
        # Validate required fields
        if not self.client.strip():
            raise ValueError("OAuth client ID cannot be empty")
        if not self.secret.strip():
            raise ValueError("OAuth client secret cannot be empty")
        if not self.url.strip():
            raise ValueError("OAuth token URL cannot be empty")

        # Initialize scope to empty string if not provided
        if self.scope is None:
            self.scope = ""

        # Generate authorization header if token is available
        if self.token:
            if not self.token.strip():
                warnings.warn(
                    "OAuth token is empty or whitespace only.",
                    UserWarning,
                    stacklevel=3,
                )
            else:
                self.auth = f"Bearer {self.token}"

        # Check for token expiration if both token and expires are set
        if self.token and self.expires:
            import time
            current_time = int(time.time())
            if self.expires < current_time:
                warnings.warn(
                    "OAuth access token appears to be expired. "
                    "Consider refreshing the token before making requests.",
                    UserWarning,
                    stacklevel=3,
                )

        # Warning if no refresh token is available for token renewal
        if self.token and not self.refresh:
            warnings.warn(
                "OAuth access token is set but no refresh token is available. "
                "Token renewal may not be possible when the access token expires.",
                UserWarning,
                stacklevel=3,
            )

        # Validate URL format
        if not self.url.startswith(('http://', 'https://')):
            warnings.warn(
                "OAuth token URL does not start with http:// or https://. "
                "This may not be a valid URL.",
                UserWarning,
                stacklevel=3,
            )