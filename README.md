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
- **Schema Structures**: CSS selector-based data extraction utilities
- **Proxy Support**: Single proxy and proxy pool rotation capabilities

## Basic Usage

All CrawlPy methods are asynchronous and return response objects with comprehensive metadata and content parsing.

```python
import asyncio
import crawlpy

# Execute single HTTP GET request
response = await crawlpy.get('https://httpbin.org/get')
print(f"Status: {response.status}")
print(f"JSON: {response.json()}")

# Execute multiple requests concurrently
targets = [
    'https://httpbin.org/get',
    'https://httpbin.org/ip',
    'https://httpbin.org/agent'
]
results = await crawlpy.get(targets)

for result in results:
    print(f"Status: {result.status}, URL: {result.url}")
```

## HTTP Methods

CrawlPy supports all standard HTTP methods with consistent async interfaces and common parameters including headers, timeouts, and authentication.

### GET Requests

```python
# Execute basic GET request
response = await crawlpy.get('https://httpbin.org/get')

# Send GET request with query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', params=params)

# Send GET request with custom headers
headers = {'Agent': 'MyApp/1.0'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Execute multiple GET requests simultaneously
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
responses = await crawlpy.get(urls)
```

### POST Requests

CrawlPy automatically sets appropriate headers based on the data format provided.

```python
# Send POST request with JSON payload
payload = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=payload)

# Submit form data via POST request
data = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=data)

# Upload file through POST request
with open('file.pdf', 'rb') as f:
    files = {'document': f}
    response = await crawlpy.post('https://httpbin.org/post', files=files)
```

### Other Methods

```python
# Prepare data payload for various operations
payload = {'status': 'updated'}

# Send PUT request to replace entire resource
response = await crawlpy.put('https://httpbin.org/put', json=payload)

# Send DELETE request to remove resource
response = await crawlpy.delete('https://httpbin.org/delete')

# Send PATCH request for partial resource modification
update = {'status': 'partial'}
response = await crawlpy.patch('https://httpbin.org/patch', json=update)

# Send HEAD request to retrieve headers only
response = await crawlpy.head('https://httpbin.org/get')
```

## Response Objects

Response objects provide comprehensive access to HTTP response data with automatic parsing and error handling.

```python
# Retrieve response from API endpoint
response = await crawlpy.get('https://httpbin.org/json')

# Access response metadata
code = response.status          # HTTP status code
headers = response.headers      # Response headers dictionary
location = response.url         # Final URL after redirects

# Extract response content in different formats
text = response.text           # Response body as string
content = response.content     # Response body as bytes
parsed = response.json()       # Parsed JSON response

# Retrieve performance and encoding information
duration = response.elapsed    # Request duration in seconds
charset = response.encoding    # Character encoding

# Handle response errors
try:
    response.check()  # Raises exception for 4xx/5xx status codes
    print(f"Success: {code}")
except crawlpy.HTTPError as err:
    print(f"Error: {err}")
```

## Request Preparation

The request preparation system enables request building and modification before transmission, useful for inspection, batch processing, or applying transformations.

```python
# Build GET request without executing
request = crawlpy.prepare('GET', 'https://httpbin.org/get')
print(f"Method: {request.method}")
print(f"URL: {request.url}")
print(f"Headers: {request.headers}")

# Construct POST request with JSON data
payload = {'user': 'john', 'pass': 'secret'}
request = crawlpy.prepare('POST', 'https://httpbin.org/post', json=payload)
print(f"Body: {request.body}")

# Build request with custom headers and parameters
headers = {'Auth': 'Bearer token123'}
params = {'limit': 10, 'page': 1}
request = crawlpy.prepare('GET', 'https://api.com/data', 
                         headers=headers, params=params)

# Execute prepared request
response = await crawlpy.send(request)
print(f"Status: {response.status}")

# Modify prepared request before execution
request.headers['Agent'] = 'CrawlPy/1.0'
request.url = 'https://httpbin.org/headers'
response = await crawlpy.send(request)
```

## Sessions

Sessions maintain cookies and connection pools across requests.

```python
from crawlpy import Session

# Create session
async with Session() as client:
    # Set default headers
    client.headers.update({'Agent': 'CrawlPy/2.0'})
    
    # Make request with session
    response = await client.get('https://httpbin.org/get')
    
    # Set base URL
    client.base = 'https://api.example.com/v1'
    profile = await client.get('/user/123')

# Manual session management
client = Session(timeout=30.0)
response = await client.get('https://httpbin.org/get')
await client.close()
```

## Retry Mechanisms

CrawlPy provides automatic retry functionality with the `Retry` class for handling transient failures and unstable connections.

```python
from crawlpy import Retry

# Configure basic retry behavior
policy = Retry(
    attempts=3,
    factor=1.0,
    codes=[429, 500, 502, 503, 504]
)

# Use retry configuration with requests
response = await crawlpy.get(
    'https://httpbin.org/status/503',
    retry=policy
)

# Advanced retry configuration
policy = Retry(
    attempts=5,
    factor=2.0,        # Exponential backoff: 2, 4, 8, 16 seconds
    ceiling=60.0,      # Maximum backoff time
    timeout=True,      # Retry on timeout errors
    connect=True,      # Retry on connection errors
    codes=[429, 500, 502, 503, 504]
)

response = await crawlpy.get(
    'https://api.example.com/endpoint',
    retry=policy
)

# Session-level retry configuration
from crawlpy import Session

async with Session(retry=policy) as client:
    response = await client.get('https://api.example.com/data')
```

## Rate Limiting

CrawlPy provides intelligent rate limiting with the `Limit` class to control request frequency and avoid overwhelming servers or hitting API limits.

```python
from crawlpy import Limit

# Configure basic rate limiting
throttle = Limit(
    calls=10,      # Maximum 10 requests
    window=60      # Per 60 seconds
)

# Use rate limiter with requests
response = await crawlpy.get(
    'https://api.example.com/data',
    limiter=throttle
)

# Advanced rate limiting configuration
throttle = Limit(
    calls=100,         # 100 requests maximum
    window=3600,       # Per hour (3600 seconds)
    burst=10,          # Allow bursts of 10 requests
    delay=0.5,         # Minimum 0.5 seconds between requests
    backoff=True,      # Enable exponential backoff on limit hit
    factor=2.0         # Backoff multiplier
)

response = await crawlpy.get(
    'https://api.example.com/endpoint',
    limiter=throttle
)

# Session-level rate limiting
from crawlpy import Session

async with Session(limiter=throttle) as client:
    # All requests through this session will be rate limited
    for i in range(50):
        response = await client.get(f'https://api.example.com/item/{i}')
        print(f"Item {i}: {response.status}")

# Multiple rate limiters for different endpoints
fast = Limit(calls=1000, window=3600)    # API limit
slow = Limit(calls=1, window=2)          # Gentle scraping

# Use different limiters for different requests
api_response = await crawlpy.get('https://api.com/data', limiter=fast)
page_response = await crawlpy.get('https://site.com/page', limiter=slow)

# Rate limiter with custom timing
throttle = Limit(
    calls=5,           # 5 requests
    window=10,         # Every 10 seconds
    spread=True,       # Spread requests evenly across window
    jitter=0.1         # Add random 0-0.1 second jitter
)

# Batch requests with rate limiting
urls = [f'https://api.example.com/item/{i}' for i in range(100)]
responses = await crawlpy.get(urls, limiter=throttle)

# Check rate limiter status
print(f"Remaining calls: {throttle.remaining}")
print(f"Reset time: {throttle.reset}")
print(f"Current window: {throttle.current}")
```

## Proxy Support

CrawlPy provides comprehensive proxy support for anonymous browsing, location spoofing, and load distribution.

```python
# Configure single proxy for request
response = await crawlpy.get(
    'https://httpbin.org/ip',
    proxy='http://proxy.example.com:8080'
)

# Use authenticated proxy
endpoint = 'http://user:pass@proxy.example.com:8080'
response = await crawlpy.get('https://httpbin.org/ip', proxy=endpoint)

# Configure proxy pool for automatic rotation
proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://proxy3.example.com:8080'
]

# Execute request with automatic proxy rotation
response = await crawlpy.get('https://httpbin.org/ip', pool=proxies)
print(f"Response: {response.json()}")
```

## Error Handling

CrawlPy provides specific exception types for different error conditions, enabling appropriate handling of network issues, timeouts, and HTTP errors.

```python
import crawlpy
from crawlpy import HTTPError, Timeout, ConnectionError, Retry, Limited

try:
    # Execute request with timeout specification
    response = await crawlpy.get('https://httpbin.org/status/404', timeout=10.0)
    # Validate status code for success (200-299)
    response.check()
    return response.json()
    
except HTTPError as error:
    # Handle HTTP errors (4xx client errors, 5xx server errors)
    code = error.response.status
    location = error.response.url
    print(f"HTTP Error {code} for URL: {location}")
    
except Limited as error:
    # Handle rate limit exceeded
    delay = error.wait
    print(f"Rate limited. Wait {delay} seconds before retry")
    
except Retry as error:
    # Handle retry exhaustion
    print(f"Request failed after {error.attempts} attempts: {error}")
    
except Timeout as error:
    # Handle request timeout errors
    print(f"Timeout: {error}")
    
except ConnectionError as error:
    # Handle network connection failures
    print(f"Connection failed: {error}")
    
except Exception as error:
    # Handle unexpected errors
    print(f"Error: {error}")
```
