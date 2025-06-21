# CrawlPy
**Modern Async HTTP Client Library**

CrawlPy is a high-performance asynchronous HTTP client library built on Python's asyncio framework. It enables efficient concurrent HTTP requests while maintaining clean, readable code for web scraping and API interactions.

## Quick Installation

```bash
pip install crawlpy
```

## Core Components

CrawlPy provides several key components for comprehensive HTTP client functionality:

- **Async HTTP Methods**: Full async/await support for GET, POST, PUT, DELETE, PATCH, and HEAD requests
- **Response Objects**: Rich response handling with automatic content parsing and error detection
- **Session Management**: Persistent connections with cookie handling and connection pooling
- **Proxy Support**: Single proxy and proxy pool rotation capabilities

## Basic Usage

All CrawlPy methods are asynchronous and return response objects with comprehensive metadata and content parsing.

```python
import asyncio
import crawlpy

# Single HTTP request
response = await crawlpy.get('https://httpbin.org/get')
print(f"Status: {response.status}")
print(f"JSON: {response.parse()}")

# Multiple concurrent requests
urls = [
    'https://httpbin.org/get',
    'https://httpbin.org/ip',
    'https://httpbin.org/agent'
]
results = await crawlpy.get(urls)

# Process all responses
for response in results:
    print(f"Status: {response.status}, URL: {response.url}")
```

## HTTP Methods

### GET Requests

```python
# Basic GET request
response = await crawlpy.get('https://httpbin.org/get')

# GET request with query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', params=params)

# GET request with custom headers
headers = {'User-Agent': 'MyApp/1.0'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Multiple GET requests concurrently
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
results = await crawlpy.get(urls)
```

### POST Requests

```python
# POST request with JSON data
json = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=json)

# POST request with form data
data = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=data)

# POST request with file upload
with open('file.pdf', 'rb') as file:
    files = {'document': file}
    response = await crawlpy.post('https://httpbin.org/post', files=files)
```

### Other HTTP Methods

```python
# PUT request to update resource
json = {'status': 'updated'}
response = await crawlpy.put('https://httpbin.org/put', json=json)

# DELETE request to remove resource
response = await crawlpy.delete('https://httpbin.org/delete')

# PATCH request for partial updates
json = {'status': 'partial'}
response = await crawlpy.patch('https://httpbin.org/patch', json=json)

# HEAD request to get headers only
response = await crawlpy.head('https://httpbin.org/get')
```

## Response Objects

```python
# Make request and get response
response = await crawlpy.get('https://httpbin.org/json')

# Access response properties
status = response.status        # HTTP status code
headers = response.headers      # Response headers
url = response.url             # Final URL after redirects
text = response.text           # Response as string
content = response.content     # Response as bytes
data = response.parse()        # Parsed JSON
elapsed = response.elapsed     # Request duration
encoding = response.encoding   # Character encoding

# Validate response status
try:
    response.validate()  # Raises exception for 4xx/5xx
    print(f"Success: {status}")
except crawlpy.HTTPError as error:
    print(f"Error: {error}")
```

## Request Building

```python
# Build GET request
request = crawlpy.build('GET', 'https://httpbin.org/get')
print(f"Method: {request.method}")
print(f"URL: {request.url}")
print(f"Headers: {request.headers}")

# Build POST request with data
json = {'user': 'john', 'pass': 'secret'}
request = crawlpy.build('POST', 'https://httpbin.org/post', json=json)
print(f"Body: {request.body}")

# Build with headers and params
headers = {'Authorization': 'Bearer token123'}
params = {'limit': 10, 'page': 1}
request = crawlpy.build('GET', 'https://api.com/data', headers=headers, params=params)

# Execute built request
response = await crawlpy.execute(request)
print(f"Status: {response.status}")

# Modify before execution
request.headers['User-Agent'] = 'CrawlPy/1.0'
request.url = 'https://httpbin.org/headers'
response = await crawlpy.execute(request)
```

## Sessions

```python
from crawlpy import Session

# Basic session usage
async with Session() as session:
    # Set session headers
    session.headers.update({'User-Agent': 'CrawlPy/2.0'})
    response = await session.get('https://httpbin.org/get')
    
    # Set base URL for relative requests
    session.base = 'https://api.example.com/v1'
    profile = await session.get('/user/123')

# Session with configuration
async with Session(
    timeout=60.0,
    headers={'User-Agent': 'MyApp/1.0'},
    cookies={'session': 'abc123'}
) as session:
    response = await session.get('https://api.example.com/data')
```

## Proxy Support

```python
# Single proxy server
response = await crawlpy.get('https://httpbin.org/ip', proxy='http://proxy.com:8080')

# Authenticated proxy
proxy = 'http://user:pass@proxy.com:8080'
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)

# Proxy rotation
proxy = [
    'http://us-east.proxy.com:8080',
    'http://eu-west.proxy.com:8080',
    'http://asia.proxy.com:8080'
]

response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)
print(f"IP: {response.parse()['origin']}")

# Protocol specific proxies
proxy = {
    'http': 'http://fast-proxy.com:8080',
    'https': 'https://secure-proxy.com:8443'
}
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)

# Geographic load balancing
proxy = [
    'http://nyc-01.proxies.com:8080',
    'http://lax-01.proxies.com:8080',
    'http://mia-01.proxies.com:8080',
    'http://chi-01.proxies.com:8080'
]

urls = [
    'https://api.weather.com/forecast',
    'https://api.news.com/headlines',
    'https://api.finance.com/stocks'
]

results = await crawlpy.get(urls, proxy=proxy)

for response in results:
    print(f"Response: {response.elapsed}s via {response.url}")
```

## Error Handling

```python
import crawlpy
from crawlpy import HTTPError, Timeout, ConnectionError

try:
    response = await crawlpy.get('https://httpbin.org/status/404', timeout=10.0)
    response.validate()
    return response.parse()
    
except HTTPError as error:
    status = error.response.status
    url = error.response.url
    print(f"HTTP Error {status} for {url}")
    
except Timeout as error:
    print(f"Timeout: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except Exception as error:
    print(f"Error: {error}")
```
