from dataclasses import dataclass
from typing import Optional, Dict, Any
import base64
import json
import time


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

    def valid(self) -> bool:
        """Check if basic auth credentials are valid.

        Returns:
            True if user and password are provided, False otherwise.
        """
        return bool(self.user and self.password)

    def empty(self) -> bool:
        """Check if credentials are empty.

        Returns:
            True if user or password is empty, False otherwise.
        """
        return not self.user or not self.password

    def encoded(self) -> str:
        """Get base64 encoded credentials.

        Returns:
            Base64 encoded username:password string.
        """
        credentials = f"{self.user}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()

    def header(self) -> Dict[str, str]:
        """Get authorization header dictionary.

        Returns:
            Dictionary containing Authorization header.
        """
        return {"Authorization": self.auth}

    def matches(self, other: 'Basic') -> bool:
        """Check if credentials match another Basic auth.

        Args:
            other: Another Basic auth instance to compare.

        Returns:
            True if credentials match, False otherwise.
        """
        return self.user == other.user and self.password == other.password


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

    def valid(self) -> bool:
        """Check if bearer token is valid.

        Returns:
            True if token is provided, False otherwise.
        """
        return bool(self.token)

    def empty(self) -> bool:
        """Check if token is empty.

        Returns:
            True if token is empty, False otherwise.
        """
        return not self.token

    def header(self) -> Dict[str, str]:
        """Get authorization header dictionary.

        Returns:
            Dictionary containing Authorization header.
        """
        return {"Authorization": self.auth}

    def matches(self, other: 'Bearer') -> bool:
        """Check if token matches another Bearer auth.

        Args:
            other: Another Bearer auth instance to compare.

        Returns:
            True if tokens match, False otherwise.
        """
        return self.token == other.token and self.scheme == other.scheme

    def length(self) -> int:
        """Get token length.

        Returns:
            Number of characters in the token.
        """
        return len(self.token)


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

    def valid(self) -> bool:
        """Check if JWT token is valid format.

        Returns:
            True if token has valid JWT format, False otherwise.
        """
        return bool(self.token and len(self.token.split('.')) == 3)

    def empty(self) -> bool:
        """Check if token is empty.

        Returns:
            True if token is empty, False otherwise.
        """
        return not self.token

    def expired(self) -> bool:
        """Check if JWT token is expired.

        Returns:
            True if token is expired, False if valid or no expiration.
        """
        if not self.data or 'exp' not in self.data:
            return False
        return time.time() > self.data['exp']

    def remaining(self) -> int:
        """Get remaining time before token expires.

        Returns:
            Seconds until expiration, 0 if expired or no expiration.
        """
        if not self.data or 'exp' not in self.data:
            return 0
        return max(0, int(self.data['exp'] - time.time()))

    def header(self) -> Dict[str, str]:
        """Get authorization header dictionary.

        Returns:
            Dictionary containing Authorization header.
        """
        return {"Authorization": self.auth}

    def payload(self) -> Dict[str, Any]:
        """Get decoded JWT payload.

        Returns:
            Dictionary containing JWT payload data.
        """
        return self.data or {}

    def subject(self) -> Optional[str]:
        """Get JWT subject claim.

        Returns:
            Subject claim from JWT payload, None if not present.
        """
        return self.data.get('sub') if self.data else None

    def issuer(self) -> Optional[str]:
        """Get JWT issuer claim.

        Returns:
            Issuer claim from JWT payload, None if not present.
        """
        return self.data.get('iss') if self.data else None


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

    def valid(self) -> bool:
        """Check if API key is valid.

        Returns:
            True if value is provided, False otherwise.
        """
        return bool(self.value)

    def empty(self) -> bool:
        """Check if API key is empty.

        Returns:
            True if value is empty, False otherwise.
        """
        return not self.value

    def header(self) -> Dict[str, str]:
        """Get API key as header dictionary.

        Returns:
            Dictionary containing API key header if place is 'header'.
        """
        if self.place == "header":
            return {self.name: self.value}
        return {}

    def query(self) -> Dict[str, str]:
        """Get API key as query parameter dictionary.

        Returns:
            Dictionary containing API key parameter if place is 'query'.
        """
        if self.place == "query":
            return {self.name: self.value}
        return {}

    def matches(self, other: 'Key') -> bool:
        """Check if API key matches another Key auth.

        Args:
            other: Another Key auth instance to compare.

        Returns:
            True if keys match, False otherwise.
        """
        return (self.value == other.value and
                self.place == other.place and
                self.name == other.name)

    def length(self) -> int:
        """Get API key length.

        Returns:
            Number of characters in the key value.
        """
        return len(self.value)


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

    def valid(self) -> bool:
        """Check if OAuth configuration is valid.

        Returns:
            True if client and secret are provided, False otherwise.
        """
        return bool(self.client and self.secret)

    def empty(self) -> bool:
        """Check if OAuth credentials are empty.

        Returns:
            True if client or secret is empty, False otherwise.
        """
        return not self.client or not self.secret

    def authenticated(self) -> bool:
        """Check if OAuth has valid access token.

        Returns:
            True if access token is present, False otherwise.
        """
        return bool(self.token)

    def expired(self) -> bool:
        """Check if OAuth token is expired.

        Returns:
            True if token is expired, False if valid or no expiration.
        """
        if not self.expires:
            return False
        return time.time() > self.expires

    def remaining(self) -> int:
        """Get remaining time before token expires.

        Returns:
            Seconds until expiration, 0 if expired or no expiration.
        """
        if not self.expires:
            return 0
        return max(0, int(self.expires - time.time()))

    def refreshable(self) -> bool:
        """Check if OAuth has refresh token available.

        Returns:
            True if refresh token is present, False otherwise.
        """
        return bool(self.refresh)

    def header(self) -> Dict[str, str]:
        """Get authorization header dictionary.

        Returns:
            Dictionary containing Authorization header if token exists.
        """
        if self.token:
            return {"Authorization": self.auth}
        return {}

    def credentials(self) -> Dict[str, str]:
        """Get OAuth client credentials.

        Returns:
            Dictionary containing client ID and secret.
        """
        return {"client_id": self.client, "client_secret": self.secret}

    def payload(self) -> Dict[str, str]:
        """Get OAuth token request payload.

        Returns:
            Dictionary containing grant type, scope, and credentials.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client,
            "client_secret": self.secret
        }
        if self.scope:
            data["scope"] = self.scope
        return data