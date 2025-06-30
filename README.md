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

Get requests retrieve data from servers and are perfect for fetching resources.

```python
import crawlpy

# Basic data retrieval - returns user info from API
response = await crawlpy.get('https://httpbin.org/get')
print(response.json())  # Shows request details and headers

# Paginated data with query params - fetches page 1 with 10 items
parameters = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://api.example.com/users', params=parameters)
# URL becomes: https://api.example.com/users?page=1&limit=10

# Authenticated request - accesses protected user data
headers = {'Authorization': 'Bearer token', 'Accept': 'application/json'}
response = await crawlpy.get('https://api.example.com/profile', headers=headers)
# Returns 200 with user profile data or 401 if token invalid

# Search with multiple tags - finds posts matching any tag
parameters = {'tags': ['python', 'async', 'http'], 'active': True}
response = await crawlpy.get('https://api.example.com/posts', params=parameters)
# URL: ?tags=python&tags=async&tags=http&active=true

# Text search with filters - searches content with status filter
parameters = {'q': 'machine learning', 'category': 'tech', 'year': 2024}
headers = {'User-Agent': 'CrawlPy/1.0'}
response = await crawlpy.get('https://api.example.com/search', params=parameters, headers=headers)
# Returns matching articles published in 2024
```

### POST Requests

Post requests create new resources and submit data to servers.

```python
import crawlpy

# Create new user account - returns 201 with user ID
data = {'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'}
response = await crawlpy.post('https://api.example.com/users', json=data)
print(response.json()['id'])  # New user ID from server

# Login with form data - returns auth token on success
form = {'username': 'alice', 'password': 'secret'}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = await crawlpy.post('https://api.example.com/login', data=form, headers=headers)
# Returns 200 with {"token": "abc123"} or 401 for invalid credentials

# Upload document with metadata - creates file record
files = {'document': open('report.pdf', 'rb')}
data = {'title': 'Q4 Report', 'category': 'finance', 'public': False}
parameters = {'folder': 'reports', 'notify': True}
response = await crawlpy.post('https://api.example.com/upload', files=files, data=data, params=parameters)
# Returns 201 with file URL and metadata

# Submit order with tracking - creates order and sends confirmation
headers = {'Authorization': 'Bearer token', 'Idempotency-Key': 'order-123'}
order = {'items': [{'id': 1, 'qty': 2}], 'shipping': 'express'}
parameters = {'calculate_tax': True, 'send_email': True}
response = await crawlpy.post('https://api.example.com/orders', json=order, headers=headers, params=parameters)
# Returns 201 with order number and total cost including tax
```

### PUT Requests

Put requests completely replace existing resources with new data.

```python
import crawlpy

# Update user profile completely - replaces all user data
customer = {'identifier': 1, 'fullname': 'Alice Updated', 'contact': 'alice.new@example.com', 'status': 'active'}
parameters = {'validate': True, 'send_notification': False}
response = await crawlpy.put('https://api.example.com/users/1', json=customer, params=parameters)
# Returns 200 with updated user data or 404 if user not found

# Replace configuration settings - overwrites entire config
headers = {'Content-Type': 'application/json'}
configuration = {'theme': 'dark', 'notifications': True, 'language': 'english'}
response = await crawlpy.put('https://api.example.com/settings', json=configuration, headers=headers)
# Returns 200 with confirmation or 403 if unauthorized

# Update file with versioning - replaces file content
headers = {'If-Match': 'etag123', 'Content-Type': 'text/plain'}
document = {'content': 'Updated document content', 'version': 2}
parameters = {'create_backup': True, 'preserve_history': True}
response = await crawlpy.put('https://api.example.com/documents/123', json=document, headers=headers, params=parameters)
# Returns 200 with new etag or 412 if etag mismatch (concurrent edit)
```

### DELETE Requests

Delete requests remove resources from the server permanently.

```python
import crawlpy

# Delete user account with confirmation - removes user permanently
parameters = {'confirm': True, 'transfer_data': False}
headers = {'Authorization': 'Bearer admin-token'}
response = await crawlpy.delete('https://api.example.com/users/123', params=parameters, headers=headers)
# Returns 204 (no content) on success or 404 if user not found

# Soft delete with reason - marks item as deleted but keeps data
data = {'reason': 'spam', 'preserve_relations': True}
parameters = {'soft_delete': True, 'notify_moderators': True}
response = await crawlpy.delete('https://api.example.com/posts/456', json=data, params=parameters)
# Returns 200 with deletion timestamp and recovery token

# Bulk delete operation - removes multiple items at once
items = {'ids': [1, 2, 3, 4], 'cascade': True}
headers = {'Content-Type': 'application/json', 'X-Bulk-Operation': 'true'}
parameters = {'dry_run': False, 'max_items': 100}
response = await crawlpy.delete('https://api.example.com/cleanup', json=items, headers=headers, params=parameters)
# Returns 200 with count of deleted items and any failures
```

### PATCH Requests

Patch requests partially update existing resources without replacing everything.

```python
import crawlpy

# Update only specific fields - changes just status and priority
update = {'status': 'completed', 'priority': 'low'}
parameters = {'validate_dependencies': True, 'send_notification': False}
response = await crawlpy.patch('https://api.example.com/tasks/789', json=update, params=parameters)
# Returns 200 with updated task or 400 if validation fails

# Partial profile update - updates only provided fields
headers = {'Content-Type': 'application/merge-patch+json', 'Authorization': 'Bearer token'}
changes = {'bio': 'Updated bio text', 'location': 'New York'}
response = await crawlpy.patch('https://api.example.com/profile', json=changes, headers=headers)
# Returns 200 with patched profile, other fields remain unchanged

# Atomic field updates - ensures all changes apply or none do
parameters = {'atomic': True, 'validate_business_rules': True}
fields = {'price': 29.99, 'discount': 10, 'active': True}
headers = {'If-Unmodified-Since': 'Wed, 21 Oct 2024 07:28:00 GMT'}
response = await crawlpy.patch('https://api.example.com/products/123', json=fields, headers=headers, params=parameters)
# Returns 200 if successful, 409 if concurrent modification detected
```

### HEAD Requests

Head requests check resource metadata without downloading the actual content.

```python
import crawlpy

# Check if large file exists and get size - saves bandwidth
parameters = {'include_metadata': True}
response = await crawlpy.head('https://cdn.example.com/video.mp4', params=parameters)
size = response.headers.get('Content-Length')  # File size in bytes
# Returns headers only, no file downloaded

# Verify authentication and permissions - quick access check  
headers = {'Authorization': 'Bearer token'}
parameters = {'check_permissions': 'read,write'}
response = await crawlpy.head('https://api.example.com/private-data', headers=headers, params=parameters)
# Returns 200 if authorized, 401/403 if not, without transferring data

# Check document freshness - see if content changed
headers = {'If-Modified-Since': 'Mon, 15 Jan 2024 10:00:00 GMT'}
response = await crawlpy.head('https://api.example.com/reports/latest', headers=headers)
# Returns 304 if unchanged, 200 with new last-modified if updated
last_modified = response.headers.get('Last-Modified')
```

### OPTIONS Requests

Options requests discover what HTTP methods and headers are allowed for a resource.

```python
import crawlpy

# Discover API capabilities - check what methods are supported
response = await crawlpy.options('https://api.example.com/users')
allowed_methods = response.headers.get('Allow')  # 'GET, POST, PUT, DELETE'
# Shows which operations are permitted on the users endpoint

# CORS preflight check - verify cross-origin request permissions
headers = {
    'Origin': 'https://myapp.com',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'Content-Type, Authorization'
}
response = await crawlpy.options('https://api.example.com/data', headers=headers)
# Returns CORS headers indicating if cross-origin POST is allowed

# API exploration with detailed info - get comprehensive endpoint data
parameters = {'format': 'detailed', 'include_schemas': True}
headers = {'Accept': 'application/vnd.api+json'}
response = await crawlpy.options('https://api.example.com/v1', params=parameters, headers=headers)
# Returns detailed API documentation and supported operations
```

## Advanced Requests

For additional flexibility, use the request method to create HTTP requests with any method and configuration.

```python
import crawlpy

# Custom method request
response = await crawlpy.request('PROPFIND', 'https://httpbin.org/webdav')

# Advanced request with full configuration
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer token'}
parameters = {'depth': 1, 'include': 'properties'}
data = {'query': 'status:active', 'limit': 50}
response = await crawlpy.request(
    method='SEARCH',
    url='https://api.example.com/search',
    headers=headers,
    params=parameters,
    json=data,
    timeout=30.0
)

# WebDAV operations with parameters
parameters = {'overwrite': False, 'lock': True}
headers = {'Destination': '/new/location', 'Depth': 'infinity'}
response = await crawlpy.request(
    'MOVE',
    'https://webdav.example.com/files/document.pdf',
    headers=headers,
    params=parameters
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
jar = Cookies()

# Add cookies
jar.set('session', 'abc123', domain='example.com')
jar.set('theme', 'dark', domain='example.com', path='/app')

# Use cookies with requests
response = await crawlpy.get('https://example.com/login', cookies=jar)

# Access cookies from response
cookies = response.cookies
print(cookies.get('token'))

# Cookie jar with expiration
jar.set(
    'temp', 
    'xyz789', 
    domain='api.example.com',
    expires=datetime.now() + timedelta(hours=1)
)

# Clear all cookies
jar.clear()

# Remove specific cookie
jar.delete('session', domain='example.com')
```

## Hooks

Use hooks to intercept and modify requests and responses at different stages of the HTTP lifecycle.

### Request Hooks

```python
from crawlpy import Session

def log_request(req):
    """Log outgoing requests"""
    print(f"Sending {req.method} to {req.url}")
    return req

def add_auth(req):
    """Add authentication header"""
    req.headers['Authorization'] = 'Bearer token'
    return req

def add_timestamp(req):
    """Add timestamp to requests"""
    req.headers['X-Timestamp'] = str(time.time())
    return req

def validate_url(req):
    """Validate request URLs"""
    if not req.url.startswith('https://'):
        raise ValueError("Only HTTPS URLs allowed")
    return req
```

### Response Hooks

```python
def log_response(res):
    """Log incoming responses"""
    print(f"Received {res.status} from {res.url}")
    return res

def cache_response(res):
    """Cache successful responses"""
    if res.status == 200:
        cache.store(res.url, res.content)
    return res

def validate_json(res):
    """Validate JSON responses"""
    if 'application/json' in res.headers.get('content-type', ''):
        try:
            res.json()  # Validate JSON
        except ValueError:
            raise ValueError("Invalid JSON response")
    return res

def track_metrics(res):
    """Track response metrics"""
    metrics.record(res.url, res.elapsed, res.status)
    return res
```

### Using Hooks with Sessions

```python
from crawlpy import Session

async with Session() as client:
    # Add request hooks
    client.hooks['request'].append(log_request)
    client.hooks['request'].append(add_auth)
    client.hooks['request'].append(validate_url)
    
    # Add response hooks
    client.hooks['response'].append(log_response)
    client.hooks['response'].append(cache_response)
    client.hooks['response'].append(track_metrics)
    
    # All requests trigger hooks
    response = await client.get('https://api.example.com/data')
```

### Using Hooks with Individual Requests

```python
# Single request with hooks
response = await crawlpy.get(
    'https://api.example.com/data',
    hooks={
        'request': [log_request, add_auth],
        'response': [log_response, validate_json]
    }
)

# Different hooks for different requests
login_hooks = {
    'request': [add_timestamp, log_request],
    'response': [cache_response, track_metrics]
}

data_hooks = {
    'request': [add_auth, validate_url],
    'response': [validate_json, log_response]
}

login = await crawlpy.post('https://api.example.com/login', hooks=login_hooks)
data = await crawlpy.get('https://api.example.com/data', hooks=data_hooks)
```

### Hook Chaining and Error Handling

```python
def safe_hook(func):
    """Wrapper for safe hook execution"""
    def wrapper(obj):
        try:
            return func(obj)
        except Exception as e:
            print(f"Hook error: {e}")
            return obj
    return wrapper

@safe_hook
def risky_transform(req):
    """Hook that might fail"""
    req.headers['X-Custom'] = process_data(req.url)
    return req

# Conditional hooks
def conditional_auth(req):
    """Add auth only for certain domains"""
    if 'api.example.com' in req.url:
        req.headers['Authorization'] = 'Bearer token'
    return req

# Hook with state
class RateLimitHook:
    def __init__(self, limit=10):
        self.limit = limit
        self.count = 0
        
    def __call__(self, req):
        if self.count >= self.limit:
            raise Exception("Rate limit exceeded")
        self.count += 1
        return req

rate_limit = RateLimitHook(limit=5)

async with Session() as client:
    client.hooks['request'].append(conditional_auth)
    client.hooks['request'].append(rate_limit)
    client.hooks['request'].append(risky_transform)
```

## Sessions

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
    session.headers.update({'Authorization': 'Bearer token'})
    
    # All requests in this session will use these settings
    user = await session.get('https://api.example.com/user')
    data = await session.get('https://api.example.com/data')
```

### Prepared Requests

Prepare requests in advance for better performance and reusability.

```python
from crawlpy import Session, Request

async with Session() as client:
    # Prepare a request
    req = Request(
        method='POST',
        url='https://api.example.com/data',
        headers={'Authorization': 'Bearer token'},
        json={'name': 'John', 'email': 'john@example.com'}
    )
    
    prepared = client.prepare(req)
    response = await client.send(prepared)
```

### Session Cookies

Manage cookies across requests within a session.

```python
from crawlpy import Session

async with Session() as client:
    # Set cookies
    client.cookies.set('session', 'abc123')
    client.cookies.set('theme', 'dark')
    
    # Cookies are automatically included in all requests
    response = await client.get('https://api.example.com/dashboard')
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

async with Session() as client:
    client.mount('https://api.example.com', adapter)
    response = await client.get('https://api.example.com/data')
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
