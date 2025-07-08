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

    # With params
    response = await client.get('https://example.com/users', params={'page': 1, 'limit': 10})

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
from config import Timeout

timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
client = CrawlPy(timeout=timeout)

# Per-request override
async with client:
    response = await client.get('https://example.com', timeout=15.0)
```

### Retry

```python
from config import Retry

retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
client = CrawlPy(retry=retry)
```

### Limits

```python
from config import Limits

limits = Limits(connections=100, keepalive=20, host=10)
client = CrawlPy(limits=limits)
```

### Redirects

```python
from config import Redirects

redirects = Redirects(maximum=10)
client = CrawlPy(redirects=redirects)
```

## Authentication

### Basic Authentication

```python
from auth import Basic

auth = Basic('username', 'password')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://example.com/protected')
```

### Token Authentication

```python
from auth import Bearer

auth = Bearer('your-access-token')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/data')
```

### JWT Authentication

```python
from auth import JWT

auth = JWT('your-jwt-token')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/secure')
```

### API Key Authentication

```python
from auth import Key

auth = Key('your-api-key', place='header', name='X-API-Key')
client = CrawlPy(auth=auth)

async with client:
    response = await client.get('https://api.example.com/data')
```

### OAuth Authentication

```python
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

```python
async with CrawlPy() as client:
    response = await client.get('https://httpbin.org/json')

    # Status and metadata
    print(response.status)      # 200
    print(response.reason)      # 'OK'
    print(response.url)         # Final URL after redirects
    print(response.headers)     # Headers dictionary
    print(response.cookies)     # Cookies dictionary
    print(response.type)        # Content-Type header

    # Content formats
    text = await response.text()        # String content
    data = await response.content()     # Raw bytes
    json = await response.json()        # Parsed JSON

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
            async for chunk in stream.read():
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
        response = stream.response()
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

```python
from crawlpy import CrawlPy

async def safe_request():
    client = CrawlPy()
    
    try:
        async with client:
            response = await client.get('https://example.com/data')
            if response:
                data = await response.json()
                return data
            else:
                print("Request failed")
                return None
                
    except Exception as error:
        print(f"Request error: {error}")
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
def agent(request):
    request.headers['User-Agent'] = 'CrawlPy/1.0'
    return request

def address(response):
    response.headers['X-Forwarded-For'] = '127.0.0.1'
    return response

client = CrawlPy(hooks={
    'request': agent,
    'response': address
})
```
