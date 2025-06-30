# CrawlPy
**Async HTTP Client Library**

CrawlPy is an asynchronous HTTP client library for Python that provides a clean interface for making HTTP requests with async/await support.

## Installation

```bash
pip install crawlpy
```

## Quick Start

This section covers the basic usage patterns to get you started quickly with CrawlPy.

### Basic Usage

```python
import asyncio
import crawlpy

async def main():
    # Make a GET request
    response = await crawlpy.get('https://httpbin.org/get')
    print(f"Status: {response.status}")
    print(f"Text: {response.text}")

# Run the async function
asyncio.run(main())
```

## HTTP Methods

CrawlPy supports all standard HTTP methods. Each method returns a response object with the server's reply.

### GET Requests
Get requests are perfect for retrieving data from servers. They support query parameters and custom headers.

```python
import crawlpy

response = await crawlpy.get('https://httpbin.org/get')

# With query parameters
response = await crawlpy.get(
    'https://httpbin.org/get', 
    parameters={'page': 1, 'limit': 10}
)
```

### POST Requests
Post requests are used for creating resources and submitting data. They support both JSON and form data.

```python
import crawlpy

# JSON data
json = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=json)

# Form data
data = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=data)
```

### PUT Requests
Put requests are used for updating or creating resources with a complete replacement.

```python
import crawlpy

# Update resource with JSON
json = {'id': 1, 'name': 'Updated Name', 'status': 'active'}
response = await crawlpy.put('https://httpbin.org/put', json=json)

# Update with form data
data = {'field1': 'value1', 'field2': 'value2'}
response = await crawlpy.put('https://httpbin.org/put', data=data)
```

### DELETE Requests
Delete requests are used for removing resources from the server.

```python
import crawlpy

# Simple delete
response = await crawlpy.delete('https://httpbin.org/delete')

# Delete with confirmation data
json = {'confirm': True, 'reason': 'No longer needed'}
response = await crawlpy.delete('https://httpbin.org/delete', json=json)
```

### PATCH Requests
Patch requests are used for partial updates to existing resources.

```python
import crawlpy

# Partial update with JSON
json = {'status': 'inactive'}
response = await crawlpy.patch('https://httpbin.org/patch', json=json)

# Patch with form fields
data = {'field_to_update': 'new_value'}
response = await crawlpy.patch('https://httpbin.org/patch', data=data)
```

### HEAD Requests
Head requests retrieve only the headers without the response body, useful for checking resource metadata.

```python
import crawlpy

response = await crawlpy.head('https://httpbin.org/get')
# Only headers are returned, no body content
print(response.headers)
```

### OPTIONS Requests
Options requests are used to determine the communication options available for a resource.

```python
import crawlpy

response = await crawlpy.options('https://httpbin.org/get')
# Check allowed methods
print(response.headers.get('Allow'))
```

## Additional Requests

For additional flexibility, use the request method to create HTTP requests with any method and configuration.

```python
import crawlpy

# Additional method request
response = await crawlpy.request('PROPFIND', 'https://httpbin.org/webdav')

# Additional request with configuration
response = await crawlpy.request(
    method='MERGE',
    url='https://httpbin.org/merge',
    headers={'Content-Type': 'application/json'},
    json={'field': 'value'},
    timeout=30.0
)
```

## Headers and Parameters

Control request headers and URL parameters to customize how your requests are sent.

### Headers

```python
import crawlpy

# Custom headers
headers = {'User-Agent': 'CrawlPy', 'Accept': 'application/json'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)
```

### Parameters

```python
import crawlpy

# Simple parameters
params = {'page': 1, 'limit': 10, 'sort': 'name'}
response = await crawlpy.get('https://api.example.com/users', params=params)

# List parameters (multiple values for same key)
params = {'tags': ['python', 'crawlpy', 'api']}
response = await crawlpy.get('https://api.example.com/posts', params=params)
# Results in: ?tags=python&tags=crawlpy&tags=api

# Parameters with special characters
params = {'search': 'hello world', 'filter': 'status:active'}
response = await crawlpy.get('https://api.example.com/search', params=params)

# Manual URL building (less preferred)
url = 'https://api.example.com/users?page=1&limit=10'
response = await crawlpy.get(url)

# Combining headers and parameters
headers = {'User-Agent': 'CrawlPy', 'Accept': 'application/json'}
parameters = {'page': 1, 'limit': 10, 'sort': 'created_at'}
response = await crawlpy.get(
    'https://httpbin.org/get', 
    headers=headers, 
    parameters=parameters
)
```

## Redirects

Configure how CrawlPy handles HTTP redirects with the Redirects class for fine-grained control.

```python
from crawlpy import Redirects

# Basic redirect configuration
redirects = Redirects(follow=True, limit=5)
response = await crawlpy.get('https://httpbin.org/redirect/3', redirects=redirects)

# Disable redirects
redirects = Redirects(follow=False)
response = await crawlpy.get('https://httpbin.org/redirect/1', redirects=redirects)

# Custom redirect with history tracking
redirects = Redirects(follow=True, limit=10, history=True)
response = await crawlpy.get('https://httpbin.org/redirect/5', redirects=redirects)
print(redirects.history)  # List of redirect URLs
```

## Timeouts

Configure timeouts to control how long requests wait for responses and connections.

```python
from crawlpy import Timeout

# Simple timeout
response = await crawlpy.get('https://httpbin.org/get', timeout=10.0)

# Detailed timeout settings
timeout = Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
response = await crawlpy.get('https://httpbin.org/get', timeout=timeout)
```

## Retry Logic

Implement retry logic to handle temporary failures and improve request reliability.

```python
from crawlpy import Retry

# Basic retry
retry = Retry(total=3)
response = await crawlpy.get('https://httpbin.org/get', retry=retry)

# Flexible retry with backoff
retry = Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
response = await crawlpy.get('https://httpbin.org/get', retry=retry)
```

## Connection Pooling

Optimize performance by managing connection pools and limiting concurrent connections.

```python
from crawlpy import Limits

# Custom connection limits
limits = Limits(connections=50, keepalive=10)
response = await crawlpy.get('https://httpbin.org/get', limits=limits)

# Per-host limits
limits = Limits(connections=100, host=20)
response = await crawlpy.get('https://httpbin.org/get', limits=limits)
```

## Response Handling

Learn how to work with response objects and extract data from HTTP responses.

### Response Object Properties

Access various properties of the response to get status information and metadata.

```python
import crawlpy

response = await crawlpy.get('https://httpbin.org/json')

# Status and basic info
print(response.status)          # 200
print(response.reason)          # 'OK'
print(response.url)             # Final URL after redirects
print(response.encoding)        # 'utf-8'
print(response.elapsed)         # Request duration as timedelta
```

### Content Access Methods

Extract and parse response content in different formats.

```python
import crawlpy

response = await crawlpy.get('https://httpbin.org/json')

# Content access
print(response.text)            # Response as text
print(response.content)         # Raw bytes
print(response.json())          # Parse JSON
print(response.headers)         # Headers dict-like object
print(response.type)            # Content type (e.g., 'application/json', 'text/html')
```

## Cookies

CrawlPy provides built-in cookie management with the `Cookies()` class for handling cookies across requests.

```python
from crawlpy import Cookies

# Create cookie jar
cookies = Cookies()

# Add cookies
cookies.set('session_id', 'abc123', domain='example.com')
cookies.set('user_pref', 'dark_mode', domain='example.com', path='/app')

# Use cookies with requests
response = await crawlpy.get('https://example.com/login', cookies=cookies)

# Access cookies from response
response_cookies = response.cookies
print(response_cookies.get('auth_token'))

# Cookie jar with expiration
cookies.set(
    'temp_token', 
    'xyz789', 
    domain='api.example.com',
    expires=datetime.now() + timedelta(hours=1)
)

# Clear all cookies
cookies.clear()

# Remove specific cookie
cookies.delete('session_id', domain='example.com')
```

## Hooks

Use hooks to intercept and modify requests and responses at different stages of the HTTP lifecycle.

```python
from crawlpy import Session

def log_request(request):
    """Hook to log outgoing requests"""
    print(f"Sending {request.method} request to {request.url}")
    return request

def log_response(response):
    """Hook to log incoming responses"""
    print(f"Received {response.status} response from {response.url}")
    return response

def add_auth_header(request):
    """Hook to add authentication to all requests"""
    request.headers['Authorization'] = 'Bearer token123'
    return request

# Using hooks with session
async with Session() as session:
    # Add request hooks
    session.hooks['request'].append(log_request)
    session.hooks['request'].append(add_auth_header)
    
    # Add response hooks
    session.hooks['response'].append(log_response)
    
    # All requests will now trigger the hooks
    response = await session.get('https://api.example.com/data')

# Using hooks with individual requests
response = await crawlpy.get(
    'https://api.example.com/data',
    hooks={
        'request': [log_request, add_auth_header],
        'response': [log_response]
    }
)
```

Sessions allow you to persist settings across multiple requests and maintain state.

### Basic Session Usage

Configure sessions with timeout, retry, and connection settings.

```python
from crawlpy import Session, Timeout, Retry, Limits

# Session with configuration
session = Session(
    timeout=Timeout(connect=5.0, read=30.0),
    retry=Retry(total=3, backoff=2.0),
    limits=Limits(connections=100, keepalive=20),
    proxies={'https': 'http://proxy.example.com:8080'}
)

async with session:
    # Configure session-wide headers
    session.headers.update({'Authorization': 'Bearer token123'})
    
    # All requests in this session will use these settings
    user = await session.get('https://api.example.com/user')
    data = await session.get('https://api.example.com/data')
```

### Prepared Requests

Prepare requests in advance for better performance and reusability.

```python
from crawlpy import Session, Request

async with Session() as session:
    # Prepare a request
    request = Request(
        method='POST',
        url='https://api.example.com/data',
        headers={'Authorization': 'Bearer token123'},
        json={'name': 'John', 'email': 'john@example.com'}
    )
    
    prepared = session.prepare(request)
    response = await session.send(prepared)
```

### Session Cookies

Manage cookies across requests within a session.

```python
from crawlpy import Session

async with Session() as session:
    # Set cookies
    session.cookies.set('session_id', 'abc123')
    session.cookies.set('user_pref', 'dark_mode')
    
    # Cookies are automatically included in all requests
    response = await session.get('https://api.example.com/dashboard')
```

### Session Adapters

Use adapters to customize how sessions handle specific protocols or domains.

```python
import crawlpy
from crawlpy import Session, HTTPAdapter, Retry

# HTTP adapter for specific domain
adapter = HTTPAdapter(
    retries=Retry(total=5),
    connections=20,
    maxsize=50
)

async with Session() as session:
    session.mount('https://api.example.com', adapter)
    response = await session.get('https://api.example.com/data')
```

## Proxy Support

Route requests through proxy servers for security or access requirements.

```python
import crawlpy
from crawlpy import Proxy

# Create proxy instance
proxy = Proxy(
    host='proxy.example.com',
    port=8080,
    username='user',
    password='pass',
    scheme='http'
)

# Use proxy with requests
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)
```

## SSL Configuration

Customize SSL/TLS settings for secure connections and certificate handling.

```python
import ssl
import crawlpy

# Custom SSL context
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED
response = await crawlpy.get('https://example.com', context=context)

# Client certificate
context = ssl.create_default_context()
context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')
response = await crawlpy.get('https://example.com', context=context)
```

## Error Handling

Properly handle different types of errors that can occur during HTTP requests.

### Exception Types and Handling

Catch and handle specific types of HTTP and network errors.

```python
import crawlpy
from crawlpy import (
    HTTPError, TimeoutError, ConnectionError, RequestError,
    SSLError, ProxyError, TooManyRedirectsError, ChunkedEncodingError,
    ContentDecodingError, StreamConsumedError, RetryError
)

try:
    response = await crawlpy.get('https://httpbin.org/status/404')
    response.raise_for_status()  # Raises exception for 4xx/5xx status codes
    
except HTTPError as error:
    print(f"HTTP error: {error.response.status}")
    
except TimeoutError as error:
    print(f"Request timed out: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except SSLError as error:
    print(f"SSL/TLS error: {error}")
    
except ProxyError as error:
    print(f"Proxy error: {error}")
    
except TooManyRedirectsError as error:
    print(f"Too many redirects: {error}")
    
except ChunkedEncodingError as error:
    print(f"Chunked encoding error: {error}")
    
except ContentDecodingError as error:
    print(f"Content decoding error: {error}")
    
except StreamConsumedError as error:
    print(f"Stream already consumed: {error}")
    
except RetryError as error:
    print(f"Retry attempts exhausted: {error}")
    
except RequestError as error:
    print(f"General request error: {error}")
```
