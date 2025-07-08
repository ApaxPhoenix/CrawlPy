# CrawlPy

**CrawlPy** is a high-performance, asynchronous HTTP client library for Python. Built with modern async/await patterns, it excels in web scraping, API integration, and high-throughput HTTP operations.

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

## Quick Start Guide

This example demonstrates the basic usage pattern. The library uses async context managers to ensure proper resource cleanup and connection pooling:

```python
import asyncio
from crawlpy import CrawlPy

async def main():
    # Configure client with base endpoint and connection settings
    client = CrawlPy(
        endpoint='https://api.example.com',
        timeout=Timeout(connect=5.0, read=30.0),
        retry=Retry(total=3)
    )
    
    # Use context manager for persistent connections
    async with client:
        response = await client.get('/users')
        print(f"Status: {response.status}")
        print(f"Content: {response.json()}")

asyncio.run(main())
```

**How it works:** Creates a CrawlPy client with base endpoint configuration, sets connection timeout to 5 seconds and read timeout to 30 seconds, configures automatic retry with up to 3 attempts, and uses async context manager to ensure proper connection cleanup.

## HTTP Methods

### GET Requests

The GET method retrieves data from servers. CrawlPy supports query parameters, custom headers, timeouts, and cookies:

```python
async with CrawlPy() as client:
    # Basic GET request
    response = await client.get('https://example.com/users')

    # GET with query parameters (automatically URL-encoded)
    response = await client.get('https://example.com/users', parameters={'page': 1, 'limit': 10})

    # GET with custom headers (useful for API authentication)
    response = await client.get('https://example.com/profile', headers={'Accept': 'application/json'})

    # GET with timeout and cookies (overrides client defaults)
    response = await client.get(
        'https://example.com/data',
        timeout=15.0,
        cookies={'session': 'abc123'}
    )
```

### POST Requests

POST requests send data to servers. CrawlPy automatically handles JSON serialization and sets appropriate Content-Type headers:

```python
async with CrawlPy() as client:
    # JSON data (automatically sets Content-Type: application/json)
    response = await client.post('https://example.com/users', json={'name': 'Alice', 'email': 'alice@example.com'})

    # Form data (automatically sets Content-Type: application/x-www-form-urlencoded)
    response = await client.post('https://example.com/login', data={'username': 'alice', 'password': 'secret'})

    # File upload (automatically sets Content-Type: multipart/form-data)
    files = {'document': open('report.pdf', 'rb')}
    response = await client.post('https://example.com/upload', files=files)

    # Mixed form data and files
    response = await client.post(
        'https://example.com/submit',
        data={'title': 'My Document'},
        files={'file': open('document.pdf', 'rb')}
    )
```

### Other HTTP Methods

CrawlPy supports all standard HTTP methods for different operations:

```python
async with CrawlPy() as client:
    # PUT - Replace entire resource
    response = await client.put('https://example.com/users/1', json={'name': 'Bob', 'email': 'bob@example.com'})

    # PATCH - Partial update of resource
    response = await client.patch('https://example.com/tasks/789', json={'status': 'completed'})

    # DELETE - Remove resource
    response = await client.delete('https://example.com/users/123')

    # HEAD - Get headers only (no body)
    response = await client.head('https://cdn.example.com/large-file.zip')

    # OPTIONS - Check allowed methods
    response = await client.options('https://api.example.com/users')
```

## Configuration

### Timeout Configuration

Control different phases of HTTP requests to prevent hanging connections:

```python
from configuration import Timeout

# Configure different timeout phases
timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
client = CrawlPy(timeout=timeout)

# Per-request timeout override
async with client:
    response = await client.get('https://example.com', timeout=15.0)
```

### Retry Configuration

Automatic retry with exponential backoff for handling transient failures:

```python
from configuration import Retry

# Configure retry behavior
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
client = CrawlPy(retry=retry)
```

### Connection Limits

Control connection pooling to optimize performance:

```python
from configuration import Limits

# Set connection pool limits
limits = Limits(connections=100, keepalive=20, host=10)
client = CrawlPy(limits=limits)
```

### Redirect Handling

Configure how redirects are handled:

```python
from configuration import Redirects

# Set maximum redirects
redirects = Redirects(maximum=10)
client = CrawlPy(redirects=redirects)
```

## Authentication

### Basic Authentication

Traditional username/password authentication:

```python
from authentication import Basic

authentication = Basic('username', 'password')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://example.com/protected')
```

### Bearer Token Authentication

API token authentication using Authorization header:

```python
from authentication import Bearer

authentication = Bearer('your-access-token')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/data')
```

### JWT Authentication

JSON Web Token authentication:

```python
from authentication import JWT

authentication = JWT('your-jwt-token')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/secure')
```

### API Key Authentication

Custom API key authentication with configurable header:

```python
from authentication import Key

authentication = Key('your-api-key', header='X-API-Key')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/data')
```

### OAuth Authentication

OAuth 2.0 client credentials flow:

```python
from authentication import OAuth

authentication = OAuth(
    client_id='your-client-id',
    client_secret='your-client-secret',
    token_url='https://authentication.example.com/token'
)
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/data')
```

## Response Handling

Access response data in multiple formats and inspect metadata:

```python
async with CrawlPy() as client:
    response = await client.get('https://httpbin.org/json')

    # Status and metadata
    print(response.status)      # 200
    print(response.reason)      # 'OK'
    print(response.url)         # Final URL after redirects
    print(response.elapsed)     # Request duration

    # Content in different formats
    print(response.text)        # String content
    print(response.content)     # Raw bytes
    print(response.json())      # Parsed JSON
    print(response.headers)     # Headers dictionary
    print(response.content_type) # Content-Type header

    # Error checking
    if response.status >= 400:
        print(f"Error: {response.status} - {response.reason}")
```

## Streaming

### Download Streaming

Handle large downloads without loading entire files into memory:

```python
async with CrawlPy() as client:
    # Stream large downloads
    stream = await client.stream('GET', 'https://example.com/large-file.zip')
    if stream:
        with open('large-file.zip', 'wb') as file:
            async for chunk in stream:
                file.write(chunk)
```

### Upload Streaming

Stream large uploads without memory overhead:

```python
async with CrawlPy() as client:
    # Stream large uploads
    stream = await client.stream(
        'POST', 
        'https://example.com/upload',
        headers={'Content-Type': 'application/octet-stream'}
    )
    if stream:
        with open('huge-file.dat', 'rb') as file:
            await stream.write(file.read())
        response = await stream.finish()
```

## Cookie Management

Automatic cookie handling for session management:

```python
# Set cookies for all requests
client = CrawlPy(cookies={'session': 'abc123', 'user': 'alice'})

async with client:
    # Per-request cookies
    response = await client.get('https://example.com', cookies={'temp': 'value'})

    # Access response cookies
    if response.cookies:
        token = response.cookies.get('token')
```

## Proxy Support

Route requests through HTTP/HTTPS proxies:

```python
from settings import Proxy

# Basic proxy configuration
proxy = Proxy(host='proxy.example.com', port=8080)
client = CrawlPy(proxy=proxy)

# Proxy with authentication
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

Custom SSL/TLS configuration for secure communications:

```python
from settings import SSL

# Custom SSL with certificate verification
ssl_configuration = SSL(
    verify=True,
    cert='/path/to/client.crt',
    key='/path/to/client.key',
    bundle='/path/to/ca.crt'
)
client = CrawlPy(ssl=ssl_configuration)

# SSL with custom ciphers
ssl_configuration = SSL(
    verify=True,
    ciphers='ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
)
client = CrawlPy(ssl=ssl_configuration)

# Disable SSL verification (not recommended for production)
ssl_configuration = SSL(verify=False)
client = CrawlPy(ssl=ssl_configuration)
```

## Error Handling

CrawlPy uses warning-based error handling instead of exceptions:

```python
from crawlpy import CrawlPy

async def safe_request():
    client = CrawlPy()
    
    try:
        async with client:
            response = await client.get('https://example.com/data')
            if response:
                return response.json()
            else:
                print("Request failed")
                return None
                
    except Exception as exception:
        print(f"Request error: {exception}")
        return None
```

**Note:** Failed requests return `None` and emit warnings rather than raising exceptions.

## Request/Response Hooks

Transform requests and responses with middleware functions:

```python
def agent(request):
    request.headers['User-Agent'] = 'CrawlPy/1.0'
    return request

def log(response):
    print(f"Response: {response.status} - {response.url}")
    return response

client = CrawlPy(hooks={
    'request': agent,
    'response': log
})
```