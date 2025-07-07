from dataclasses import dataclass
from typing import Optional, Dict, Any
import base64
import json


@dataclass
class Basic:
    """Basic authentication configuration.

    Handles HTTP Basic Authentication using username and password
    credentials encoded in base64 format according to RFC 7617.

    Attributes:
        user: Username for authentication.
        password: Password for authentication.
        auth: Complete authorization header string.
    """
    user: str
    password: str
    auth: str = ""

    def __post_init__(self) -> None:
        """Initialize default basic auth header if not provided.

        Automatically generates the Basic authentication header by encoding
        username:password in base64 format as required by HTTP Basic Auth.

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
    """Bearer token authentication configuration.

    Handles OAuth 2.0 Bearer tokens and similar token-based authentication
    schemes commonly used with REST APIs and modern web services.

    Attributes:
        token: Authentication token string.
        scheme: Authentication scheme name (default: "Bearer").
        auth: Complete authorization header string.
    """
    token: str
    scheme: str = "Bearer"
    auth: str = ""

    def __post_init__(self) -> None:
        """Initialize default bearer auth header if not provided.

        Automatically generates the Bearer authentication header using
        the specified scheme and token.

        Returns:
            None
        """
        # Generate Bearer auth header if not already provided
        if not self.auth:
            # Create authorization header with scheme and token
            self.auth = f"{self.scheme} {self.token}"


@dataclass
class JWT:
    """JSON Web Token authentication configuration.

    Handles JWT tokens with automatic header and payload extraction
    for debugging and validation purposes. Supports standard JWT format.

    Attributes:
        token: JWT token string in format header.payload.signature.
        scheme: Authentication scheme name (default: "Bearer").
        auth: Complete authorization header string.
        data: Decoded JWT payload dictionary.
    """
    token: str
    scheme: str = "Bearer"
    auth: str = ""
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default JWT auth header and decode payload if not provided.

        Automatically generates the JWT authentication header and attempts
        to decode the JWT payload for inspection and validation.

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
                parts = self.token.split('.')
                if len(parts) >= 2:
                    # Extract payload part (second component)
                    part = parts[1]

                    # Add base64 padding if necessary for proper decoding
                    padding = 4 - len(part) % 4
                    if padding != 4:
                        part += '=' * padding

                    # Decode base64 payload and parse JSON
                    decoded = base64.b64decode(part)
                    self.data = json.loads(decoded.decode())
            except Exception:
                # If JWT decoding fails, keep empty payload
                # This prevents crashes with malformed tokens
                pass


@dataclass
class Key:
    """API key authentication configuration.

    Handles API key authentication which can be sent via headers,
    query parameters, or other custom locations based on API requirements.

    Attributes:
        value: API key value string.
        place: Where to place the key ("header" or "query").
        name: Parameter/header name for the API key.
    """
    value: str
    place: str = "header"
    name: str = "X-API-Key"

    def __post_init__(self) -> None:
        """Validate API key configuration.

        Ensures that the placement and name are valid for API key usage.

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
    """OAuth 2.0 authentication configuration.

    Handles OAuth 2.0 flow with client credentials and token management
    for server-to-server authentication and user authorization flows.

    Attributes:
        client: OAuth client ID string.
        secret: OAuth client secret string.
        url: OAuth token endpoint URL.
        scope: OAuth scope string for permissions.
        token: Current access token string.
        refresh: Refresh token for token renewal.
        expires: Token expiration timestamp.
        auth: Complete authorization header string.
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
        """Initialize default OAuth configuration and header if not provided.

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
