# CrawlPy

**Modern Async HTTP Client Library for Python**

CrawlPy is a high-performance asynchronous HTTP client library that provides a clean, intuitive interface for making HTTP requests with full async/await support.

## Installation

```bash
pip install crawlpy
```

## Quick Start

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

All the standard HTTP methods you'd expect, with clean async/await syntax:

### GET - Retrieve Data
```python
# Basic GET request
response = await crawlpy.get('https://api.example.com/users')

# With query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://api.example.com/users', params=params)

# With custom headers
headers = {'X-API-Key': 'your-api-key', 'Accept': 'application/json'}
response = await crawlpy.get('https://api.example.com/profile', headers=headers)
```

### POST - Create Resources
```python
# JSON data (automatically sets Content-Type)
json = {'name': 'Alice', 'email': 'alice@example.com'}
response = await crawlpy.post('https://api.example.com/users', json=json)

# Form data
data = {'username': 'alice', 'password': 'secret'}
response = await crawlpy.post('https://api.example.com/login', data=data)

# File upload
files = {'document': open('report.pdf', 'rb')}
response = await crawlpy.post('https://api.example.com/upload', files=files)
```

### PUT, PATCH, DELETE, HEAD, OPTIONS
```python
# Replace entire resource
response = await crawlpy.put('https://api.example.com/users/1', json=user)

# Partial update
response = await crawlpy.patch('https://api.example.com/tasks/789', json={'status': 'done'})

# Delete resource
response = await crawlpy.delete('https://api.example.com/users/123')

# Get headers only
response = await crawlpy.head('https://cdn.example.com/large-file.zip')

# Discover capabilities
response = await crawlpy.options('https://api.example.com/users')
```

### Custom Methods
```python
# Any HTTP method works - that's why we have custom methods
response = await crawlpy.request('PROPFIND', 'https://webdav.example.com/files')
response = await crawlpy.request('SEARCH', 'https://api.example.com/search', params=query)
response = await crawlpy.request('LOCK', 'https://webdav.example.com/file', json=lock)
```

## Configuration

Configure timeouts, retries, redirects, and connection limits with simple classes:

### Timeouts
```python
from crawlpy import Timeout

# Simple timeout
response = await crawlpy.get('https://example.com', timeout=10.0)

# Detailed timeout control
timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
response = await crawlpy.get('https://example.com', timeout=timeout)
```

### Retries
```python
from crawlpy import Retry

# Basic retry
retry = Retry(total=3)
response = await crawlpy.get('https://example.com', retry=retry)

# Smart retry with backoff
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
response = await crawlpy.get('https://example.com', retry=retry)
```

### Redirects and Limits
```python
from crawlpy import Redirects, Limits

# Control redirects
redirects = Redirects(follow=True, limit=5)
response = await crawlpy.get('https://example.com', redirects=redirects)

# Connection pool limits
limits = Limits(connections=50, keepalive=10, host=20)
response = await crawlpy.get('https://example.com', limits=limits)
```

## Response Handling

Everything you need from HTTP responses in one clean interface:

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

## Sessions

Sessions maintain state and improve performance through connection reuse:

```python
from crawlpy import Session

async with Session() as session:
    # Set headers for all requests in this session
    session.headers.update({'User-Agent': 'MyApp/1.0'})
    
    # Reuse connections automatically
    user = await session.get('https://api.example.com/user')
    data = await session.get('https://api.example.com/data')
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
    response = await session.get('https://api.example.com/data')
```

### Prepared Requests
```python
async with Session() as session:
    # Create reusable request template
    request = session.build(
        method='POST',
        url='https://api.example.com/data',
        headers={'Authorization': 'Bearer token'},
        json={'key': 'value'}
    )
    
    # Prepare and send
    ready = session.prepare(request)
    response = await session.send(ready)
```

## Cookies

Simple cookie management that works automatically:

```python
from crawlpy import Cookies

cookies = Cookies()
cookies.set('session', 'abc123', domain='example.com')

# Cookies are automatically sent with matching requests
response = await crawlpy.get('https://example.com', cookies=cookies)

# Access response cookies
token = response.cookies.get('token')
```

## Request/Response Hooks

Transform requests before sending and responses after receiving with simple functions:

```python
# Define what you want to do
def key(request):
    request.headers['X-API-Key'] = 'your-secret-key'
    return request

def log(response):
    print(f"Got {response.status} from {response.url}")
    return response

# Apply to individual requests
response = await crawlpy.get(
    'https://api.example.com/data',
    before=[key],
    after=[log]
)

# Or apply to all requests in a session
async with Session() as client:
    client.before.append(key)
    client.after.append(log)
    
    # Hooks run automatically on every request
    response = await client.get('https://api.example.com/data')
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

## SSL Configuration

Custom SSL contexts for specific security requirements:

```python
import ssl

# Custom SSL context
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED

response = await crawlpy.get('https://example.com', context=context)

# Client certificates for mutual TLS
context = ssl.create_default_context()
context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')
response = await crawlpy.get('https://example.com', context=context)
```

## Error Handling

Specific exceptions for different error conditions make debugging easier:

```python
from crawlpy import (
    HTTPError, TimeoutError, ConnectionError, RequestError,
    SSLError, ProxyError, TooManyRedirectsError
)

try:
    response = await crawlpy.get('https://example.com/api')
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    
except HTTPError as error:
    print(f"HTTP error {error.response.status}: {error}")
    
except TimeoutError as error:
    print(f"Request timed out: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except SSLError as error:
    print(f"SSL/TLS error: {error}")
    
except RequestError as error:
    print(f"Request error: {error}")
```
