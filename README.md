# CrawlPy

**CrawlPy** is a modern async HTTP client library for Python. Built for web scraping, API consumption, and HTTP communication with efficiency in mind.

## Core Features

* **Async/Await Support** - Native async programming
* **Smart Session Management** - Auto connection pooling and state persistence
* **Flexible Authentication** - Basic, Bearer, JWT, Key, and OAuth support
* **Streaming Support** - Handle large files without memory overhead
* **Retry Logic** - Smart retry with exponential backoff
* **Timeout Control** - Granular timeout configuration
* **Cookie Management** - Auto cookie handling
* **Proxy Support** - HTTP/HTTPS proxy with authentication
* **SSL Configuration** - Custom SSL contexts and certificates
* **Request/Response Hooks** - Transform requests/responses

## Quick Start

```python
import asyncio
from crawlpy import CrawlPy

async def main() -> None:
    # Configure client with base endpoint and connection settings
    client = CrawlPy(
        endpoint='https://api.example.com',
        timeout=Timeout(connect=5.0, read=30.0),
        retry=Retry(total=3)
    )
    
    # Use context manager for persistent connections
    async with client:
        response = await client.request('GET', '/users')
        print(f"Status: {response.status}")
        print(f"Content: {response.json()}")

asyncio.run(main())
```

## HTTP Methods

### GET Requests

```python
async with CrawlPy() as client:
    # Basic GET request to fetch all users
    response = await client.request('GET', 'https://example.com/users')

    # GET with query parameters for pagination
    response = await client.request('GET', 'https://example.com/users', params={'page': 1, 'limit': 10})

    # GET with custom headers for content negotiation
    response = await client.request('GET', 'https://example.com/profile', headers={'Accept': 'application/json'})

    # GET with timeout and session cookies
    response = await client.request(
        'GET',
        'https://example.com/data',
        timeout=15.0,
        cookies={'session': 'abc123'}
    )
```

### POST Requests

```python
async with CrawlPy() as client:
    # POST JSON data - automatically sets Content-Type to application/json
    response = await client.request('POST', 'https://example.com/users', json={'name': 'Alice', 'email': 'alice@example.com'})

    # POST form data - sends as application/x-www-form-urlencoded
    response = await client.request('POST', 'https://example.com/login', data={'username': 'alice', 'password': 'secret'})

    # POST file upload - sends as multipart/form-data
    files = {'document': open('report.pdf', 'rb')}
    response = await client.request('POST', 'https://example.com/upload', files=files)

    # POST mixed form data and files
    response = await client.request(
        'POST',
        'https://example.com/submit',
        data={'title': 'My Document'},
        files={'file': open('document.pdf', 'rb')}
    )
```

### PUT Requests

```python
async with CrawlPy() as client:
    # PUT to replace entire resource
    response = await client.request('PUT', 'https://example.com/users/1', json={'name': 'Bob', 'email': 'bob@example.com'})
```

### PATCH Requests

```python
async with CrawlPy() as client:
    # PATCH to partially update resource
    response = await client.request('PATCH', 'https://example.com/tasks/789', json={'status': 'completed'})
```

### DELETE Requests

```python
async with CrawlPy() as client:
    # DELETE to remove resource
    response = await client.request('DELETE', 'https://example.com/users/123')
```

### HEAD Requests

```python
async with CrawlPy() as client:
    # HEAD to get headers only (no body)
    response = await client.request('HEAD', 'https://cdn.example.com/large-file.zip')
```

### OPTIONS Requests

```python
async with CrawlPy() as client:
    # OPTIONS to check allowed methods
    response = await client.request('OPTIONS', 'https://api.example.com/users')
```

## Configuration

### Timeout

```python
from config import Timeout

# Set specific timeouts for different connection phases
timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
client = CrawlPy(timeout=timeout)

# Per-request timeout override
async with client:
    response = await client.request('GET', 'https://example.com', timeout=15.0)
```

### Retry

```python
from config import Retry

# Configure retry logic with exponential backoff for server errors
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
client = CrawlPy(retry=retry)
```

### Limits

```python
from config import Limits

# Set connection pooling limits to manage resource usage
limits = Limits(connections=100, keepalive=20, host=10)
client = CrawlPy(limits=limits)
```

### Redirects

```python
from config import Redirects

# Configure maximum number of redirects to follow
redirects = Redirects(maximum=10)
client = CrawlPy(redirects=redirects)
```

## Authentication

### Basic Authentication

```python
from auth import Basic

# Create HTTP Basic Authentication with username/password
auth = Basic('username', 'password')
client = CrawlPy(auth=auth)

async with client:
    # All requests will include Authorization header
    response = await client.request('GET', 'https://example.com/protected')
```

### Token Authentication

```python
from auth import Bearer

# Create Bearer token authentication
auth = Bearer('your-access-token')
client = CrawlPy(auth=auth)

async with client:
    # Sends "Authorization: Bearer your-access-token"
    response = await client.request('GET', 'https://api.example.com/data')
```

### JWT Authentication

```python
from auth import JWT

# Create JWT authentication with token validation
auth = JWT('your-jwt-token')
client = CrawlPy(auth=auth)

async with client:
    # Validates and sends JWT token
    response = await client.request('GET', 'https://api.example.com/secure')
```

### API Key Authentication

```python
from auth import Key

# Send API key in custom header
auth = Key('your-api-key', place='header', name='X-API-Key')
client = CrawlPy(auth=auth)

async with client:
    # Sends "X-API-Key: your-api-key" header
    response = await client.request('GET', 'https://api.example.com/data')
```

### OAuth Authentication

```python
from auth import OAuth

# Create OAuth 2.0 client credentials authentication
auth = OAuth(
    client='your-client-id',
    secret='your-client-secret',
    url='https://auth.example.com/token'
)
client = CrawlPy(auth=auth)

async with client:
    # Automatically handles token acquisition and refresh
    response = await client.request('GET', 'https://api.example.com/data')
```

## Response Handling

```python
async with CrawlPy() as client:
    response = await client.request('GET', 'https://httpbin.org/json')

    # Access response metadata
    print(response.status)      # HTTP status code (200)
    print(response.reason)      # Status reason phrase ('OK')
    print(response.url)         # Final URL after redirects
    print(response.headers)     # Response headers as dict
    print(response.cookies)     # Response cookies as dict
    print(response.type)        # Content-Type header value

    # Get response content in different formats
    text = await response.text()        # Decoded text content
    data = await response.content()     # Raw bytes
    json = await response.json()        # Parsed JSON object

    # Check for HTTP errors
    if response.status >= 400:
        print(f"Error: {response.status} - {response.reason}")
```

## Streaming

### Download Stream

```python
async with CrawlPy() as client:
    # Create streaming download for large files to avoid memory overhead
    stream = await client.stream('GET', 'https://example.com/large-file.zip')
    if stream:
        # Write chunks to file as they arrive
        with open('large-file.zip', 'wb') as file:
            async for chunk in stream.read():
                file.write(chunk)
```

### Upload Stream

```python
async with CrawlPy() as client:
    # Create streaming upload without loading entire file into memory
    stream = await client.stream(
        'POST', 
        'https://example.com/upload',
        headers={'Content-Type': 'application/octet-stream'}
    )
    if stream:
        # Stream file content in chunks
        with open('huge-file.dat', 'rb') as file:
            await stream.write(file.read())
        response = stream.response()
```

## Cookies

```python
# Set default cookies for all requests
client = CrawlPy(cookies={'session': 'abc123', 'user': 'alice'})

async with client:
    # Add additional cookies for specific request
    response = await client.request('GET', 'https://example.com', cookies={'temp': 'value'})

    # Extract cookies from response for future use
    if response.cookies:
        token = response.cookies.get('token')
```

## Proxy Support

```python
from settings import Proxy

# Basic proxy configuration
proxy = Proxy(host='proxy.example.com', port=8080)
client = CrawlPy(proxy=proxy)

# Proxy with authentication and custom headers
proxy = Proxy(
    host='proxy.example.com',
    port=8080,
    username='user',
    password='pass',
    headers={'Custom-Header': 'value'}
)
client = CrawlPy(proxy=proxy)
```

## SSL Configuration

```python
from settings import SSL

# Custom SSL with client certificates
ssl = SSL(
    verify=True,
    cert='/path/to/client.crt',
    key='/path/to/client.key',
    bundle='/path/to/ca.crt'
)
client = CrawlPy(ssl=ssl)

# SSL with custom cipher suites for security
ssl = SSL(
    verify=True,
    ciphers='ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
)
client = CrawlPy(ssl=ssl)

# Disable SSL verification (not recommended for production)
ssl = SSL(verify=False)
client = CrawlPy(ssl=ssl)
```

## Error Handling

```python
from crawlpy import CrawlPy

# CrawlPy returns None on failure instead of raising exceptions
async with CrawlPy() as client:
    response = await client.request('GET', 'https://example.com/data')
    if response:
        data = await response.json()
        return data
    else:
        print("Request failed - check warnings for details")
        return None
```

> **Note:** CrawlPy uses warning-based error handling. Failed requests return `None` and emit warnings rather than raising exceptions.

## Base URL with Relative Paths

```python
# Set base endpoint for all requests
client = CrawlPy(endpoint='https://api.example.com/v1')

async with client:
    # All requests automatically use the base endpoint
    users = await client.request('GET', '/users')          # GET https://api.example.com/v1/users
    user = await client.request('GET', '/users/123')       # GET https://api.example.com/v1/users/123
    posts = await client.request('GET', '/posts')          # GET https://api.example.com/v1/posts
```

## Hooks

```python
def agent(request):
    """Add User-Agent header to all outgoing requests."""
    request.headers['User-Agent'] = 'CrawlPy/1.0'
    return request

def address(response):
    """Add forwarding header to all incoming responses."""
    response.headers['X-Forwarded-For'] = '127.0.0.1'
    return response

# Configure request and response hooks for automatic transformations
client = CrawlPy(hooks={
    'request': agent,
    'response': address
})
```
