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

## Installation

```bash
pip install crawlpy
```

## Quick Start

```python
import asyncio
from crawlpy import CrawlPy

async def main():
    # Configure client with base endpoint
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

## HTTP Methods

### GET Requests

```python
async with CrawlPy() as client:
    # Basic GET
    response = await client.get('https://example.com/users')

    # With parameters
    response = await client.get('https://example.com/users', parameters={'page': 1, 'limit': 10})

    # With headers
    response = await client.get('https://example.com/profile', headers={'Accept': 'application/json'})

    # With timeout and cookies
    response = await client.get(
        'https://example.com/data',
        timeout=15.0,
        cookies={'session': 'abc123'}
    )
```

### POST Requests

```python
async with CrawlPy() as client:
    # JSON data (auto sets Content-Type)
    response = await client.post('https://example.com/users', json={'name': 'Alice', 'email': 'alice@example.com'})

    # Form data
    response = await client.post('https://example.com/login', data={'username': 'alice', 'password': 'secret'})

    # File upload
    files = {'document': open('report.pdf', 'rb')}
    response = await client.post('https://example.com/upload', files=files)

    # Mixed form and files
    response = await client.post(
        'https://example.com/submit',
        data={'title': 'My Document'},
        files={'file': open('document.pdf', 'rb')}
    )
```

### Other Methods

```python
async with CrawlPy() as client:
    # Replace resource
    response = await client.put('https://example.com/users/1', json={'name': 'Bob', 'email': 'bob@example.com'})

    # Partial update
    response = await client.patch('https://example.com/tasks/789', json={'status': 'completed'})

    # Delete resource
    response = await client.delete('https://example.com/users/123')

    # Headers only
    response = await client.head('https://cdn.example.com/large-file.zip')

    # Check methods
    response = await client.options('https://api.example.com/users')
```

## Configuration

### Timeout

```python
from configuration import Timeout

timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
client = CrawlPy(timeout=timeout)

# Per-request override
async with client:
    response = await client.get('https://example.com', timeout=15.0)
```

### Retry

```python
from configuration import Retry

retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
client = CrawlPy(retry=retry)
```

### Limits

```python
from configuration import Limits

limits = Limits(connections=100, keepalive=20, host=10)
client = CrawlPy(limits=limits)
```

### Redirects

```python
from configuration import Redirects

redirects = Redirects(maximum=10)
client = CrawlPy(redirects=redirects)
```

## Authentication

### Basic Authentication

```python
from authentication import Basic

authentication = Basic('username', 'password')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://example.com/protected')
```

### Token Authentication

```python
from authentication import Bearer

authentication = Bearer('your-access-token')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/data')
```

### JWT Authentication

```python
from authentication import JWT

authentication = JWT('your-jwt-token')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/secure')
```

### API Key Authentication

```python
from authentication import Key

authentication = Key('your-api-key', header='X-API-Key')
client = CrawlPy(authentication=authentication)

async with client:
    response = await client.get('https://api.example.com/data')
```

### OAuth Authentication

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

```python
async with CrawlPy() as client:
    response = await client.get('https://httpbin.org/json')

    # Status and metadata
    print(response.status)      # 200
    print(response.reason)      # 'OK'
    print(response.url)         # Final URL after redirects
    print(response.elapsed)     # Request duration

    # Content formats
    print(response.text)        # String content
    print(response.content)     # Raw bytes
    print(response.json())      # Parsed JSON
    print(response.headers)     # Headers dictionary
    print(response.content_type) # Content-Type header

    # Error check
    if response.status >= 400:
        print(f"Error: {response.status} - {response.reason}")
```

## Streaming

### Download Stream

```python
async with CrawlPy() as client:
    # Stream large downloads
    stream = await client.stream('GET', 'https://example.com/large-file.zip')
    if stream:
        with open('large-file.zip', 'wb') as file:
            async for chunk in stream:
                file.write(chunk)
```

### Upload Stream

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

## Cookies

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

```python
from settings import Proxy

# Basic proxy
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

**Note:** CrawlPy uses warning-based error handling. Failed requests return `None` and emit warnings rather than raising exceptions.

## Base URL with Relative Paths

```python
# Set base endpoint
client = CrawlPy(endpoint='https://api.example.com/v1')

async with client:
    # All requests use base endpoint
    users = await client.get('/users')          # GET https://api.example.com/v1/users
    user = await client.get('/users/123')       # GET https://api.example.com/v1/users/123
    posts = await client.get('/posts')          # GET https://api.example.com/v1/posts
```

## Hooks

```python
def add_user_agent(request):
    request.headers['User-Agent'] = 'MyApp/1.0'
    return request

def log_response(response):
    print(f"Response: {response.status} - {response.url}")
    return response

client = CrawlPy(hooks={
    'request': add_user_agent,
    'response': log_response
})
```