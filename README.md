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
    # Make a simple GET request
    response = await crawlpy.get('https://httpbin.org/get')
    print(f"Status: {response.status}")
    print(f"Content: {response.json()}")

# Run the async function
asyncio.run(main())
```

## HTTP Methods

### GET - Retrieve Data
```python
# Basic GET request to fetch data
response = await crawlpy.get('https://api.example.com/users')

# GET with query parameters (adds ?page=1&limit=10 to URL)
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://api.example.com/users', params=params)

# GET with custom headers (e.g., API key authentication)
headers = {'X-API-Key': 'your-api-key-here', 'Accept': 'application/json'}
response = await crawlpy.get('https://api.example.com/profile', headers=headers)
```

### POST - Create Resources
```python
# POST with JSON data (automatically sets Content-Type: application/json)
json = {'name': 'Alice', 'email': 'alice@example.com'}
response = await crawlpy.post('https://api.example.com/users', json=json)

# POST with form data (Content-Type: application/x-www-form-urlencoded)
data = {'username': 'alice', 'password': 'secret'}
response = await crawlpy.post('https://api.example.com/login', data=data)

# POST with file upload (multipart/form-data)
files = {'document': open('report.pdf', 'rb')}
response = await crawlpy.post('https://api.example.com/upload', files=files)
```

### PUT - Replace Resources
```python
# PUT request to completely replace a resource
json = {'id': 1, 'name': 'Alice Updated', 'email': 'alice@new.com'}
response = await crawlpy.put('https://api.example.com/users/1', json=json)
```

### PATCH - Partial Updates
```python
# PATCH request to partially update a resource
json = {'status': 'completed', 'priority': 'high'}
response = await crawlpy.patch('https://api.example.com/tasks/789', json=json)
```

### DELETE - Remove Resources
```python
# DELETE request with confirmation parameter
params = {'confirm': True}
response = await crawlpy.delete('https://api.example.com/users/123', params=params)
```

### HEAD - Metadata Only
```python
# HEAD request to get headers without downloading content
response = await crawlpy.head('https://cdn.example.com/large-file.zip')
# Check file size without downloading
size = response.headers.get('Content-Length')
```

### OPTIONS - Discover Capabilities
```python
# OPTIONS request to discover allowed HTTP methods
response = await crawlpy.options('https://api.example.com/users')
# Get supported methods from response
methods = response.headers.get('Allow')
```

## Custom Requests

For advanced use cases or custom HTTP methods:

```python
# Custom HTTP method (e.g., WebDAV PROPFIND)
response = await crawlpy.request('PROPFIND', 'https://webdav.example.com/files')

# Custom method with query parameters
params = {'query': 'python'}
response = await crawlpy.request('SEARCH', 'https://api.example.com/search', params=params)

# Custom method with headers and JSON body
headers = {'Authorization': 'Bearer token'}
json = {'filters': {'active': True}}
response = await crawlpy.request('SEARCH', 'https://api.example.com/search', 
                                headers=headers, json=json)
```

## Configuration Classes

### Redirects
```python
from crawlpy import Redirects

# Follow up to 5 redirects (default is usually 30)
redirects = Redirects(follow=True, limit=5)
response = await crawlpy.get('https://example.com/redirect', redirects=redirects)

# Disable automatic redirect following
redirects = Redirects(follow=False)
response = await crawlpy.get('https://example.com/redirect', redirects=redirects)
```

### Timeouts
```python
from crawlpy import Timeout

# Simple timeout in seconds (applies to entire request)
response = await crawlpy.get('https://example.com', timeout=10.0)

# Detailed timeout configuration for different phases
timeout = Timeout(
    connect=5.0,    # Time to establish connection
    read=30.0,      # Time to read response data
    write=10.0,     # Time to send request data
    pool=60.0       # Time to get connection from pool
)
response = await crawlpy.get('https://example.com', timeout=timeout)
```

### Retry Logic
```python
from crawlpy import Retry

# Basic retry configuration (retry up to 3 times)
retry = Retry(total=3)
response = await crawlpy.get('https://example.com', retry=retry)

# Advanced retry with exponential backoff
retry = Retry(
    total=5,                        # Maximum retry attempts
    backoff=1.5,                   # Backoff multiplier (1.5^attempt seconds)
    status=[500, 502, 503, 504]    # Only retry on these HTTP status codes
)
response = await crawlpy.get('https://example.com', retry=retry)
```

### Connection Limits
```python
from crawlpy import Limits

# Global connection pool limits
limits = Limits(
    connections=50,    # Total connections across all hosts
    keepalive=10      # Keep-alive connections to maintain
)
response = await crawlpy.get('https://example.com', limits=limits)

# Per-host connection limits
limits = Limits(
    connections=100,   # Total connections
    host=20           # Max connections per host
)
response = await crawlpy.get('https://example.com', limits=limits)
```

## Response Handling

```python
response = await crawlpy.get('https://httpbin.org/json')

# Status information
print(response.status)          # HTTP status code (e.g., 200)
print(response.reason)          # Status reason phrase (e.g., 'OK')
print(response.url)             # Final URL after any redirects
print(response.elapsed)         # Total request duration

# Content access methods
print(response.text)            # Response body as string
print(response.content)         # Response body as raw bytes
print(response.json())          # Parse JSON response to Python dict/list
print(response.headers)         # Response headers as dict-like object
print(response.type)            # Content-Type header value
```

## Sessions

Sessions maintain state across multiple requests and provide better performance through connection reuse:

### Basic Session
```python
from crawlpy import Session

async with Session() as session:
    # Set headers that will be used for all requests in this session
    session.headers.update({'User-Agent': 'MyApp/1.0'})
    
    # All requests in this session share the same connection pool and headers
    user = await session.get('https://api.example.com/user')
    data = await session.get('https://api.example.com/data')
    # Connection is automatically reused between requests
```

### Configured Session
```python
from crawlpy import Session, Timeout, Retry, Limits

# Create session with default configuration for all requests
session = Session(
    timeout=Timeout(connect=5.0, read=30.0),    # Default timeouts
    retry=Retry(total=3, backoff=2.0),          # Default retry behavior
    limits=Limits(connections=100, keepalive=20) # Connection pool settings
)

async with session:
    # All requests use the session's default configuration
    response = await session.get('https://api.example.com/data')
```

### Prepared Requests
```python
from crawlpy import Session, Request

async with Session() as session:
    # Create a reusable request template
    request = Request(
        method='POST',
        url='https://api.example.com/data',
        headers={'Authorization': 'Bearer token'},
        json={'key': 'value'}
    )
    
    # Prepare the request (validates and processes it)
    prepared = session.prepare(request)
    
    # Send the prepared request (can be reused multiple times)
    response = await session.send(prepared)
```

## Cookie Management

```python
from crawlpy import Cookies

# Create a cookie jar to store and manage cookies
cookies = Cookies()

# Set cookies manually
cookies.set('session', 'abc123', domain='example.com')
cookies.set('theme', 'dark', domain='example.com', path='/app')

# Use cookies with requests (automatically sent with matching domain/path)
response = await crawlpy.get('https://example.com', cookies=cookies)

# Access cookies from response (automatically stored in jar if provided)
response_cookies = response.cookies
auth_token = response_cookies.get('auth_token')
```

## Request/Response Hooks

Process requests before sending and responses after receiving:

### Request Hooks
```python
# Function to add forwarding headers
def forwarded(request):
    request.headers['X-Forwarded-For'] = '192.168.1.1'
    return request

# Function to add user agent
def agent(request):
    request.headers['User-Agent'] = 'CrawlPy/1.0'
    return request
```

### Response Hooks
```python
# Function to log response details
def logging(response):
    print(f"Status: {response.status} for {response.url}")
    return response

# Function to handle response checking
def check(response):
    if response.status >= 400:
        print(f"Warning: HTTP {response.status} error")
    return response
```

### Using Hooks
```python
from crawlpy import Session

async with Session() as client:
    # Add hooks to session (applied to all requests)
    client['before'].append(forwarded)
    client['before'].append(useragent)
    client['after'].append(logging)
    client['after'].append(validate)
    
    # Hooks are automatically applied
    response = await client.get('https://api.example.com/data')

# Or apply hooks to individual requests only
response = await crawlpy.get(
    'https://api.example.com/data',
    before=[forwarded, useragent],
    after=[logging, validate]
)
```

## Proxy Support

```python
from crawlpy import Proxy

# Configure HTTP proxy with authentication
proxy = Proxy(
    host='proxy.example.com',
    port=8080,
    username='user',           # Optional: proxy username
    password='pass',           # Optional: proxy password
    scheme='http'              # http or https
)

# Use proxy for requests
response = await crawlpy.get('https://example.com', proxy=proxy)
```

## SSL Configuration

```python
import ssl

# Create custom SSL context for specific requirements
context = ssl.create_default_context()
context.check_hostname = False              # Disable hostname verification
context.verify_mode = ssl.CERT_REQUIRED     # Require valid certificates

response = await crawlpy.get('https://example.com', context=context)

# Configure client certificates for mutual TLS
context = ssl.create_default_context()
context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')
response = await crawlpy.get('https://example.com', context=context)
```

## Error Handling

CrawlPy provides specific exception types for different error conditions:

```python
from crawlpy import (
    HTTPError, TimeoutError, ConnectionError, RequestError,
    SSLError, ProxyError, TooManyRedirectsError
)

try:
    response = await crawlpy.get('https://example.com/api')
    # Raise exception for 4xx/5xx status codes
    response.raise_for_status()
    
except HTTPError as error:
    # Handle HTTP errors (4xx, 5xx status codes)
    print(f"HTTP error {error.response.status}: {error}")
    
except TimeoutError as error:
    # Handle request timeouts
    print(f"Request timed out: {error}")
    
except ConnectionError as error:
    # Handle connection failures (network issues, DNS resolution, etc.)
    print(f"Connection failed: {error}")
    
except SSLError as error:
    # Handle SSL/TLS certificate errors
    print(f"SSL/TLS error: {error}")
    
except RequestError as error:
    # Handle general request errors
    print(f"Request error: {error}")
```

## API Reference

### Main Functions
- `crawlpy.get(url, **kwargs)` - GET request
- `crawlpy.post(url, **kwargs)` - POST request  
- `crawlpy.put(url, **kwargs)` - PUT request
- `crawlpy.patch(url, **kwargs)` - PATCH request
- `crawlpy.delete(url, **kwargs)` - DELETE request
- `crawlpy.head(url, **kwargs)` - HEAD request
- `crawlpy.options(url, **kwargs)` - OPTIONS request
- `crawlpy.request(method, url, **kwargs)` - Custom request

### Configuration Classes
- `Session(**kwargs)` - HTTP session
- `Timeout(**kwargs)` - Timeout configuration
- `Retry(**kwargs)` - Retry logic
- `Redirects(**kwargs)` - Redirect handling
- `Limits(**kwargs)` - Connection limits
- `Cookies()` - Cookie management
- `Proxy(**kwargs)` - Proxy configuration

### Common Parameters
- `url` - Target URL
- `params` - Query parameters (dict)
- `headers` - HTTP headers (dict)
- `json` - JSON data to send
- `data` - Form data to send
- `files` - Files to upload
- `timeout` - Request timeout
- `retry` - Retry configuration
- `redirects` - Redirect handling
- `cookies` - Cookie jar
- `proxy` - Proxy settings
- `before` - Request hook functions
- `after` - Response hook functions
