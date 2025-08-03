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
from config import Timeout, Retry

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
from crawlpy import CrawlPy

async with CrawlPy() as client:
    # Basic GET request
    response = await client.get('https://example.com/users')
    # GET with query parameters (automatically URL-encoded)
    response = await client.get('https://example.com/users', params={'page': 1, 'limit': 10})
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
from crawlpy import CrawlPy

async with CrawlPy() as client:
    # JSON data (automatically sets Content-Type: application/json)
    response = await client.post('https://example.com/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    # Form data (automatically sets Content-Type: application/x-www-form-urlencoded)
    response = await client.post('https://example.com/login', data={'username': 'alice', 'password': 'secret'})
    # File upload (automatically sets Content-Type: multipart/form-data)
    document = {'document': open('report.pdf', 'rb')}  # Open file in binary read mode
    response = await client.post('https://example.com/upload', files=document)
    # Mixed form data and files
    response = await client.post(
        'https://example.com/submit',
        data={'title': 'My Document'},  # Form fields
        files={'file': open('document.pdf', 'rb')}  # File attachment
    )
```

### Other HTTP Methods
CrawlPy supports all standard HTTP methods for different operations:
```python
from crawlpy import CrawlPy

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
from crawlpy import CrawlPy
from config import Timeout

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
from crawlpy import CrawlPy
from config import Retry

# Configure retry behavior
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
client = CrawlPy(retry=retry)
```

### Connection Limits
Control connection pooling to optimize performance:
```python
from crawlpy import CrawlPy
from config import Limits

# Set connection pool limits
limits = Limits(connections=100, host=10)
client = CrawlPy(limits=limits)
```

### Redirect Handling
Configure how redirects are handled:
```python
from crawlpy import CrawlPy
from config import Redirects

# Set maximum redirects
redirects = Redirects(limit=10)
client = CrawlPy(redirects=redirects)
```

## Authentication

### Basic Authentication
Traditional username/password authentication:
```python
from crawlpy import CrawlPy
from auth import Basic

auth = Basic('username', 'password')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://example.com/protected')
```

### Bearer Token Authentication
API token authentication using Authorization header:
```python
from crawlpy import CrawlPy
from auth import Bearer

auth = Bearer('your-access-token')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/data')
```

### JWT Authentication
JSON Web Token authentication:
```python
from crawlpy import CrawlPy
from auth import JWT

auth = JWT('your-jwt-token')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/secure')
```

### API Key Authentication
Custom API key authentication with configurable header:
```python
from crawlpy import CrawlPy
from auth import Key

auth = Key('your-api-key', name='X-API-Key', place='header')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/data')
```

### OAuth Authentication
OAuth 2.0 client credentials flow:
```python
from crawlpy import CrawlPy
from auth import OAuth

auth = OAuth(
    client='your-client-id',
    secret='your-client-secret',
    url='https://auth.example.com/token'
)
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/data')
```

## Response Handling
Access response data in multiple formats and inspect metadata:
```python
from crawlpy import CrawlPy

async with CrawlPy() as client:
    response = await client.get('https://httpbin.org/json')
    
    # Status and metadata
    print(response.status)      # 200
    print(response.reason)      # 'OK'
    print(response.url)         # Final URL after redirects
    
    # Content in different formats
    text = await response.text()        # String content
    content = await response.bytes()    # Raw bytes
    data = await response.json()        # Parsed JSON
    
    print(response.headers)     # Headers dictionary
    print(response.type)        # Content-Type header
    
    # Error checking
    if response.status >= 400:
        print(f"Error: {response.status} - {response.reason}")
```

## Streaming

### Download Streaming
Handle large downloads without loading entire files into memory:
```python
from crawlpy import CrawlPy

async with CrawlPy() as client:
    # Stream large downloads
    stream = await client.stream('GET', 'https://example.com/large-file.zip')
    if stream:
        with open('large-file.zip', 'wb') as file:  # Open file in write-binary mode
            async for chunk in stream.stream():  # Process data in chunks
                file.write(chunk)
```

### Upload Streaming
Stream large uploads without memory overhead:
```python
from crawlpy import CrawlPy

async with CrawlPy() as client:
    # Stream large uploads
    stream = await client.stream(
        'POST', 
        'https://example.com/upload',
        headers={'Content-Type': 'application/octet-stream'}
    )
    if stream:
        with open('huge-file.dat', 'rb') as file:  # Open file in read-binary mode
            data = file.read()
            await stream.write(data)  # Stream file contents
```

## Cookie Management
Automatic cookie handling for session management:
```python
from crawlpy import CrawlPy

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
from crawlpy import CrawlPy
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
from crawlpy import CrawlPy
from settings import SSL

# Custom SSL with certificate verification
ssl = SSL(
    verify=True,
    cert='/path/to/client.crt',
    key='/path/to/client.key',
    bundle='/path/to/ca.crt'
)
client = CrawlPy(ssl=ssl)

# SSL with custom ciphers
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
CrawlPy uses warning-based error handling instead of exceptions:
```python
from crawlpy import CrawlPy

async def request():
    client = CrawlPy()
    
    try:
        async with client:
            response = await client.get('https://example.com/data')
            if response:
                return response.json()
            else:
                print("Request failed")
                return None
                
    except Exception as error:
        print(f"Request error: {error}")
        return None
```
**Note:** Failed requests return `None` and emit warnings rather than raising exceptions.

## Request/Response Hooks
Transform requests and responses with middleware functions:
```python
from crawlpy import CrawlPy

def agent(request):
    request.headers['User-Agent'] = 'CrawlPy/1.0'  # Set custom user agent
    return request

def log(response):
    print(f"Response: {response.status} - {response.url}")  # Log response details
    return response

client = CrawlPy(hooks={
    'request': agent,   # Apply to outgoing requests
    'response': log     # Apply to incoming responses
})
```