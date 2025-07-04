# CrawlPy

**CrawlPy** is a modern asynchronous HTTP client library designed to simplify web requests in Python. Whether you're building a web scraper, consuming APIs, or handling HTTP communication, CrawlPy provides the tools you need to get the job done efficiently. This documentation will guide you through the core features, configuration options, and essential functionalities of CrawlPy.

## Core Features

CrawlPy offers a comprehensive set of features for modern HTTP communication:

- **Async/Await Support** - Native asynchronous programming with full async/await syntax
- **Smart Session Management** - Automatic connection pooling and state persistence
- **Flexible Authentication** - Built-in support for Bearer, Basic, and custom auth methods
- **Streaming Support** - Handle large files and responses without memory overhead
- **Retry Logic** - Intelligent retry mechanisms with exponential backoff
- **Timeout Control** - Granular timeout configuration for different operations
- **Cookie Management** - Automatic cookie handling and persistence
- **Proxy Support** - HTTP/HTTPS proxy configuration with authentication
- **SSL Configuration** - Custom SSL contexts and certificate handling

## Installation

```bash
pip install crawlpy
```

## Quick Start

Get started with CrawlPy in just a few lines of code:

```python
import asyncio
import crawlpy

async def main():
    response = await crawlpy.get('https://httpbin.org/get')
    print(f"Status: {response.status}")
    print(f"Content: {response.json()}")

asyncio.run(main())
```

## HTTP Methods

CrawlPy supports all standard HTTP methods with clean, intuitive syntax:

### GET Requests
```python
# Basic GET request
response = await crawlpy.get('https://example.com/users')

# With query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://example.com/users', params=params)

# With custom headers
headers = {'Accept': 'application/json'}
response = await crawlpy.get('https://example.com/profile', headers=headers)
```

### POST Requests
```python
# JSON data (automatically sets Content-Type)
data = {'name': 'Alice', 'email': 'alice@example.com'}
response = await crawlpy.post('https://example.com/users', json=data)

# Form data
data = {'username': 'alice', 'password': 'secret'}
response = await crawlpy.post('https://example.com/login', data=data)

# File upload
files = {'document': open('report.pdf', 'rb')}
response = await crawlpy.post('https://example.com/upload', files=files)
```

### Other HTTP Methods
```python
# Replace entire resource
response = await crawlpy.put('https://example.com/users/1', json=user)

# Partial update
response = await crawlpy.patch('https://example.com/tasks/789', json={'status': 'done'})

# Delete resource
response = await crawlpy.delete('https://example.com/users/123')

# Get headers only
response = await crawlpy.head('https://cdn.example.com/large-file.zip')

# Custom methods
response = await crawlpy.request('PROPFIND', 'https://webdav.example.com/files')
```

## Configuration

Configure CrawlPy behavior with simple, powerful configuration classes:

### Timeout Configuration
```python
from crawlpy import Timeout

# Simple timeout
response = await crawlpy.get('https://example.com', timeout=10.0)

# Detailed timeout control
timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
response = await crawlpy.get('https://example.com', timeout=timeout)
```

### Retry Configuration
```python
from crawlpy import Retry

# Basic retry
retry = Retry(total=3)
response = await crawlpy.get('https://example.com', retry=retry)

# Smart retry with backoff
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
response = await crawlpy.get('https://example.com', retry=retry)
```

### Connection Limits
```python
from crawlpy import Limits

# Connection pool limits
limits = Limits(connections=50, keepalive=10, host=20)
response = await crawlpy.get('https://example.com', limits=limits)
```

## Session Management

Sessions provide connection reuse and state persistence for improved performance:

### Basic Session Usage
```python
from crawlpy import Session

async with Session() as session:
    # Set headers for all requests in this session
    session.headers.update({'User-Agent': 'MyApp/1.0'})
    
    # Reuse connections automatically
    user = await session.get('https://example.com/user')
    data = await session.get('https://example.com/data')
```

### Configured Sessions
```python
# Session with default configuration
session = Session(
    timeout=Timeout(connect=5.0, read=30.0),
    retry=Retry(total=3, backoff=2.0),
    limits=Limits(connections=100, keepalive=20)
)

async with session:
    response = await session.get('https://example.com/data')
```

## Authentication

Clean authentication handling for common patterns:

### Basic Authentication
```python
from crawlpy import BasicAuth

auth = BasicAuth('user', 'pass')
response = await crawlpy.get('https://example.com', auth=auth)
```

### Token Authentication
```python
from crawlpy import Bearer

auth = Bearer('token123')
response = await crawlpy.get('https://example.com', auth=auth)
```

### Custom Authentication
```python
from crawlpy import ApiKey

auth = ApiKey('secret-key', 'X-Custom-Key')
response = await crawlpy.get('https://example.com', auth=auth)
```

## Response Handling

Access response data through a clean, consistent interface:

```python
response = await crawlpy.get('https://httpbin.org/json')

# Status and metadata
print(response.status)      # 200
print(response.reason)      # 'OK'
print(response.url)         # Final URL after redirects
print(response.elapsed)     # Request duration

# Content in multiple formats
print(response.text)        # String
print(response.content)     # Raw bytes
print(response.json())      # Parsed JSON
print(response.headers)     # Headers dict
print(response.type)        # Content-Type
```

## Streaming

Handle large files and responses without loading everything into memory:

### Download Streaming
```python
# Download large files in chunks
async with crawlpy.stream('GET', 'https://example.com/large-file.zip') as response:
    with open('large-file.zip', 'wb') as file:
        async for chunk in response.chunks():
            file.write(chunk)
```

### Upload Streaming
```python
# Upload large files with streaming
async with crawlpy.stream('POST', 'https://example.com/upload') as stream:
    with open('huge-file.dat', 'rb') as file:
        await stream.write(file.read())
    response = await stream.response()
```

## Cookie Management

Automatic cookie handling that works seamlessly:

```python
from crawlpy import Cookies

cookies = Cookies()
cookies.set('session', 'abc123', domain='example.com')

# Cookies are automatically sent with matching requests
response = await crawlpy.get('https://example.com', cookies=cookies)

# Access response cookies
token = response.cookies.get('token')
```

## Proxy Support

Configure HTTP/HTTPS proxies with optional authentication:

```python
from crawlpy import Proxy

proxy = Proxy(
    host='proxy.example.com',
    port=8080,
    username='user',    # Optional
    password='pass',    # Optional
    scheme='http'
)

response = await crawlpy.get('https://example.com', proxy=proxy)
```

## Error Handling

Comprehensive error handling with specific exception types:

```python
from crawlpy import (
    HTTPError, TimeoutError, ConnectionError, RequestError,
    SSLError, ProxyError, TooManyRedirectsError
)

try:
    response = await crawlpy.get('https://example.com/data')
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    
except HTTPError as error:
    print(f"HTTP error {error.response.status}: {error}")
    
except TimeoutError as error:
    print(f"Request timed out: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except RequestError as error:
    print(f"Request error: {error}")
```

## Advanced Features

### Request/Response Hooks
```python
# Transform requests and responses
def authenticate(request):
    request.headers['X-Auth-Key'] = 'your-secret-key'
    return request

def cache(response):
    if response.status == 200:
        response.cache = True
    return response

# Apply hooks to requests
response = await crawlpy.get(
    'https://example.com/data',
    before=[authenticate],
    after=[cache]
)
```

### SSL Configuration
```python
import ssl

# Custom SSL context
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED

response = await crawlpy.get('https://example.com', context=context)
```

CrawlPy provides everything you need for modern HTTP communication in Python, with a focus on simplicity, performance, and flexibility.
