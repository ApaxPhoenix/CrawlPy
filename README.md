# CrawlPy
**Modern HTTP Client Library - Like Requests, But Better**

CrawlPy is a modern async HTTP client library that combines the simplicity of requests with asynchronous performance and advanced crawling capabilities. Built for developers who need powerful web scraping, API interaction, and data extraction tools with minimal complexity.

## Installation
```bash
pip install crawlpy
```

## Quick Start

```python
import crawlpy
import asyncio
from crawlpy import Session, Auth, Hook, Schema

async def main():
    # Simple requests
    response = await crawlpy.get('https://httpbin.org/get')
    print(response.status)  # 200
    print(response.json())  # JSON response
    
    # Multiple URLs
    urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent'
    ]
    responses = await crawlpy.get(urls)
    
    # Advanced features with classes
    schema = Schema()
    data = await schema.css(
        url="https://example.com/products", 
        selectors={"title": "h1.product-title"}
    )

asyncio.run(main())
```

## Core HTTP Methods

```python
# GET requests
response = await crawlpy.get('https://httpbin.org/get')

# GET with params
response = await crawlpy.get('https://httpbin.org/get', params={
    'page': 1,
    'limit': 50,
    'sort': 'date'
})

# POST with JSON
response = await crawlpy.post('https://httpbin.org/post', 
    json={'name': 'John', 'email': 'john@example.com'}
)

# POST with form data
response = await crawlpy.post('https://httpbin.org/post',
    data={'user': 'john', 'pass': 'secret'}
)

# Other HTTP methods
response = await crawlpy.put('https://httpbin.org/put', json={'id': 123})
response = await crawlpy.delete('https://httpbin.org/delete')
response = await crawlpy.head('https://httpbin.org/get')
response = await crawlpy.patch('https://httpbin.org/patch', json={'status': 'active'})

# Multiple URLs for any method
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
responses = await crawlpy.get(urls)
```

### HTTP Method Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `url` | str/list[str] | Single URL or list of URLs | `'https://api.com'` or `['https://api1.com', 'https://api2.com']` |
| `params` | dict | URL query parameters | `{'page': 1, 'limit': 50}` |
| `headers` | dict | HTTP headers | `{'User-Agent': 'MyApp/1.0'}` |
| `proxy` | str/list | Proxy server(s) | `'http://proxy:8080'` or `['http://p1:8080', 'http://p2:8080']` |
| `ssl` | bool | SSL certificate verification | `True` |
| `auth` | Auth | Authentication object | `Auth(type='basic', user='user', password='pass')` |
| `token` | str | Bearer token | `'abc123xyz'` |
| `cookies` | dict/Cookie | HTTP cookies | `{'session': 'abc123'}` |
| `json` | dict | JSON payload (POST/PUT/PATCH) | `{'name': 'John', 'age': 30}` |
| `data` | dict | Form data payload | `{'user': 'john'}` |
| `files` | dict | File uploads | `{'upload': open('file.pdf', 'rb')}` |

## Response Handling

```python
# Response handling
response = await crawlpy.get('https://httpbin.org/json')

# Status and headers
print(response.status)          # 200
print(response.reason)          # 'OK'
print(response.headers)         # Response headers dict
print(response.encoding)        # Character encoding

# Content access
print(response.text)            # Text content as string
print(response.content)         # Raw bytes content
print(response.json())          # Parse JSON response to dict/list

# Response metadata
print(response.url)             # Final URL after redirects
print(response.history)         # List of redirect responses
print(response.elapsed)         # Request duration in seconds
print(response.size)            # Response size in bytes

# Status checking
if response.status == 200:      
    data = response.json()
elif response.status >= 400:
    print(f"Error: {response.status} {response.reason}")
    
response.raise_for_status()     # Raise exception for 4xx/5xx
```

## Authentication

```python
from crawlpy import Auth

# Basic authentication
auth = Auth(type='basic', user='username', password='password')
response = await crawlpy.get('https://api.example.com/data', auth=auth)

# OAuth2 authentication
auth = Auth(type='oauth2', id='client_id', secret='client_secret', 
           endpoint='https://api.example.com/token')
response = await crawlpy.get('https://api.example.com/data', auth=auth)

# API key authentication
auth = Auth(type='key', value='apikey', name='X-API-Key')
response = await crawlpy.get('https://api.example.com/data', auth=auth)

# JWT authentication
auth = Auth(type='jwt', token='token')
response = await crawlpy.get('https://api.example.com/data', auth=auth)
```

### Authentication Types

| Type | Description | Parameters | Example |
|------|-------------|------------|---------|
| `basic` | HTTP Basic Authentication | `user`, `password` | `Auth(type='basic', user='user', password='pass')` |
| `jwt` | JWT Bearer Token | `token` | `Auth(type='jwt', token='eyJ0eXAi...')` |
| `oauth2` | OAuth2 Authentication | `id`, `secret`, `endpoint` | `Auth(type='oauth2', id='id', secret='secret', endpoint='url')` |
| `key` | API Key Authentication | `value`, `name` | `Auth(type='key', value='key123', name='X-API-Key')` |
| `custom` | Custom headers | `headers` | `Auth(type='custom', headers={'X-Auth': 'token'})` |

## Schema Extraction

```python
from crawlpy import Schema

schema = Schema()

# Extract structured data with CSS selectors
data = await schema.css(url="https://example.com/products", selectors={
    "title": "h1.product-title",
    "price": ".product-price",
    "images": ["img.product-image", "src"],
    "description": ".product-description",
    "stock": ".stock-status"
})

# Extract with XPath
data = await schema.xpath(url="https://example.com/products", paths={
    "title": "//h1[@class='product-title']/text()",
    "links": "//a[@class='product-link']/@href",
    "prices": "//span[@class='price']/text()"
})

# Extract with JavaScript
data = await schema.js(url="https://example.com/products", expressions={
    "total": "document.querySelectorAll('.product').length",
    "title": "document.title",
    "data": "window.userData || {}"
})

# Extract from multiple URLs
urls = [
    "https://example.com/product/1",
    "https://example.com/product/2",
    "https://example.com/product/3"
]
products = await schema.css(url=urls, selectors={
    "name": "h1.title",
    "price": ".price-value",
    "rating": ".rating-score"
})

# Define reusable scheme
scheme = schema.define({
    "css": {
        "title": "h1.product-title",
        "price": ".price-value",
        "images": ["img.product-image", "src"]
    },
    "xpath": {
        "description": "//div[@class='description']/text()",
        "rating": "//span[@class='rating']/@data-score"
    },
    "js": {
        "stock": "window.productData.stock",
        "count": "document.querySelectorAll('.recommended').length"
    }
})

# Apply scheme to URL
data = await schema.extract(url="https://example.com/product/123", pattern=scheme)
```

### Schema Methods

| Method | Description | Parameters | Example |
|--------|-------------|------------|---------|
| `.css()` | Extract using CSS selectors | `url`, `selectors` | `schema.css(url="...", selectors={"title": "h1"})` |
| `.xpath()` | Extract using XPath expressions | `url`, `paths` | `schema.xpath(url="...", paths={"title": "//h1/text()"})` |
| `.js()` | Extract using JavaScript | `url`, `expressions` | `schema.js(url="...", expressions={"count": "document.querySelectorAll('div').length"})` |
| `.define()` | Define extraction pattern | `dict` | `schema.define({"css": {"title": "h1"}})` |
| `.extract()` | Extract using scheme | `url`, `pattern` | `schema.extract(url="...", pattern=scheme)` |

## Hooks

```python
from crawlpy import Hook

hook = Hook()

@hook.before('header')
def modify_headers(request):
    request.headers['X-Custom-Header'] = 'MyValue'

@hook.after('error')
def handle_response(response):
    if response.status >= 400:
        print(f"Error occurred: {response.status}")

# Use hooks with requests
response = await crawlpy.get('https://httpbin.org/get', hooks=hook)

# Multiple URLs with hooks
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
responses = await crawlpy.get(urls, hooks=hook)

# Clear hooks
hook.clear()
```

### Hook Methods

| Method | Description | Parameters | Example |
|--------|-------------|------------|---------|
| `@.before('name')` | Decorator for before request | `name`, `function` | `@hook.before('log')` |
| `@.after('name')` | Decorator for after response | `name`, `function` | `@hook.after('log')` |
| `.register()` | Register hook function | `name`, `function`, `type` | `hook.register('log', func, 'before')` |
| `.clear()` | Clear all hooks | None | `hook.clear()` |

## Sessions

```python
from crawlpy import Session

# Create a session
session = Session()

# Configure session defaults
session.headers.update({'User-Agent': 'MyApp/2.0'})
session.auth = Auth(type='basic', user='username', password='password')
session.ssl = False

# Make requests with session
response = await session.get('https://api.example.com/profile')
response = await session.post('https://api.example.com/data', json={'key': 'value'})

# Session supports multiple URLs too
urls = ['https://api.example.com/user1', 'https://api.example.com/user2']
responses = await session.get(urls)

# Session context manager
async with Session() as session:
    session.url = 'https://api.example.com'
    session.headers.update({'Authorization': 'Bearer token123'})
    
    user = await session.get('/user/123')
    posts = await session.get('/user/123/posts')
```

### Session Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `url` | str | Base URL for all requests | `'https://api.example.com'` |
| `headers` | dict | Default headers for all requests | `{'User-Agent': 'MyApp/2.0'}` |
| `auth` | Auth | Default authentication | `Auth(type='basic', user='username', password='password')` |
| `token` | str | Default bearer token | `'abc123xyz'` |
| `ssl` | bool | Default SSL verification | `True` |
| `proxy` | str/list | Default proxy server(s) | `'http://proxy:8080'` |
| `cookies` | dict | Default cookies | `{'session_id': 'abc123'}` |

## Proxy Support

```python
from crawlpy import Proxy

# Single proxy
response = await crawlpy.get('https://example.com',
    proxy='http://proxy.example.com:8080'
)

# Proxy with authentication
response = await crawlpy.get('https://example.com',
    proxy='http://user:pass@proxy.example.com:8080'
)

# Multiple proxies with rotation
proxy = Proxy([
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080', 
    'http://proxy3.example.com:8080'
])

response = await crawlpy.get('https://example.com', proxy=proxy)

# Use proxies with multiple URLs
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']
responses = await crawlpy.get(urls, proxy=proxy)
```

## Cookie Management

```python
from crawlpy import Cookie

# Request with cookies
response = await crawlpy.get('https://example.com/login', 
    cookies={'session_id': 'abc123'}
)

# Persistent cookie storage
cookie = Cookie()
response = await crawlpy.get('https://example.com/login', cookies=cookie)
response = await crawlpy.get('https://example.com/dashboard', cookies=cookie)

# Save/load cookies
cookie.save('cookies.txt')
cookie = Cookie.load('cookies.txt')

# Cookie with multiple URLs
urls = ['https://example.com/page1', 'https://example.com/page2']
responses = await crawlpy.get(urls, cookies=cookie)
```

### Cookie Methods

| Method | Description | Parameters | Example |
|--------|-------------|------------|---------|
| `.save()` | Save cookies to file | `filename` | `cookie.save('cookies.txt')` |
| `.load()` | Load cookies from file | `filename` | `Cookie.load('cookies.txt')` |
| `.update()` | Update cookies | `cookies` | `cookie.update({'session': 'abc'})` |
| `.clear()` | Clear all cookies | None | `cookie.clear()` |

## Content Format Adapters

```python
from crawlpy import Adapter

# JSON adapter
adapter = Adapter(type='json')
response = await crawlpy.get('https://api.example.com/data', adapter=adapter)
data = response.data  # Automatically parsed JSON

# XML adapter
adapter = Adapter(type='xml')
response = await crawlpy.get('https://api.example.com/feed.xml', adapter=adapter)
data = response.data  # Parsed XML to dict

# CSV adapter
adapter = Adapter(type='csv', delimiter=';', quote='"')
response = await crawlpy.get('https://api.example.com/data.csv', adapter=adapter)
data = response.data  # Parsed CSV to list of dicts

# Use adapters with multiple URLs
urls = ['https://api.example.com/data1.json', 'https://api.example.com/data2.json']
responses = await crawlpy.get(urls, adapter=Adapter(type='json'))
data = [response.data for response in responses]
```

### Adapter Types

| Type | Description | Parameters | Example |
|------|-------------|------------|---------|
| `json` | Parse JSON responses | None | `Adapter(type='json')` |
| `xml` | Parse XML responses | None | `Adapter(type='xml')` |
| `csv` | Parse CSV responses | `delimiter`, `quote` | `Adapter(type='csv', delimiter=';')` |

## Error Handling

```python
import crawlpy
from crawlpy import (
    CrawlPyError, ConnectionError, ConnectTimeout, ReadTimeout, 
    HTTPError, RequestError, InvalidURL, TooManyRedirects, 
    SSLError, ProxyError, JSONDecodeError, ChunkedEncodingError,
    ContentDecodingError, StreamConsumedError, RetryError
)

try:
    response = await crawlpy.get('https://api.example.com/data')
    response.raise_for_status()
    return response.json()
    
except ConnectionError as error:
    print(f"Failed to connect: {error}")
    
except ConnectTimeout as error:
    print(f"Connection timeout: {error}")
    
except ReadTimeout as error:
    print(f"Read timeout: {error}")
    
except HTTPError as error:
    print(f"HTTP error: {error.response.status}")
    
except InvalidURL as error:
    print(f"Invalid URL: {error}")
    
except TooManyRedirects as error:
    print(f"Too many redirects: {error}")
    
except SSLError as error:
    print(f"SSL error: {error}")
    
except ProxyError as error:
    print(f"Proxy error: {error}")
    
except JSONDecodeError as error:
    print(f"JSON decode error: {error}")
    
except ChunkedEncodingError as error:
    print(f"Chunked encoding error: {error}")
    
except ContentDecodingError as error:
    print(f"Content decoding error: {error}")
    
except StreamConsumedError as error:
    print(f"Stream consumed error: {error}")
    
except RetryError as error:
    print(f"Retry error: {error}")
    
except RequestError as error:
    print(f"Request error: {error}")
    
except CrawlPyError as error:
    print(f"CrawlPy error: {error}")
```

### Error Types

| Exception | Description | Example |
|-----------|-------------|---------|
| `CrawlPyError` | Base exception class | All CrawlPy errors inherit from this |
| `ConnectionError` | Connection failed | Network unreachable, DNS resolution failed |
| `ConnectTimeout` | Connection timeout | Server took too long to establish connection |
| `ReadTimeout` | Read timeout | Server took too long to send response |
| `HTTPError` | HTTP error status | 404 Not Found, 500 Internal Server Error |
| `RequestError` | General request error | Invalid request format |
| `InvalidURL` | Invalid URL format | Malformed URL string |
| `TooManyRedirects` | Too many redirects | Redirect loop detected |
| `SSLError` | SSL/TLS error | Certificate verification failed |
| `ProxyError` | Proxy server error | Proxy authentication failed |
| `JSONDecodeError` | JSON parsing error | Invalid JSON response |
| `ChunkedEncodingError` | Chunked encoding error | Invalid chunked response |
| `ContentDecodingError` | Content decoding error | Invalid gzip/deflate encoding |
| `StreamConsumedError` | Stream already consumed | Response body already read |
| `RetryError` | Retry attempts exhausted | Max retries exceeded |
