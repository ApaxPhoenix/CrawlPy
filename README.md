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
print(f"JSON: {response.parse()}")

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
data = response.parse()        # Parsed JSON response

# Retrieve performance and encoding information
duration = response.elapsed    # Request duration in seconds
encoding = response.encoding   # Character encoding

# Handle response errors
try:
    response.validate()  # Raises exception for 4xx/5xx status codes
    print(f"Success: {code}")
except crawlpy.HTTPError as error:
    print(f"Error: {error}")
```

## Request Preparation

The request preparation system enables request building and modification before transmission, useful for inspection, batch processing, or applying transformations.

```python
# Build GET request without executing
request = crawlpy.build('GET', 'https://httpbin.org/get')
print(f"Method: {request.method}")
print(f"URL: {request.url}")
print(f"Headers: {request.headers}")

# Construct POST request with JSON data
payload = {'user': 'john', 'pass': 'secret'}
request = crawlpy.build('POST', 'https://httpbin.org/post', json=payload)
print(f"Body: {request.body}")

# Build request with custom headers and parameters
headers = {'Auth': 'Bearer token123'}
params = {'limit': 10, 'page': 1}
request = crawlpy.build('GET', 'https://api.com/data', 
                        headers=headers, params=params)

# Execute prepared request
response = await crawlpy.execute(request)
print(f"Status: {response.status}")

# Modify prepared request before execution
request.headers['Agent'] = 'CrawlPy/1.0'
request.url = 'https://httpbin.org/headers'
response = await crawlpy.execute(request)
```

## Sessions

Sessions maintain cookies and connection pools across requests.

```python
from crawlpy import Session

# Basic session with context manager
async with Session() as client:
    # Set default headers
    client.headers.update({'Agent': 'CrawlPy/2.0'})
    
    # Make request with session
    response = await client.get('https://httpbin.org/get')
    
    # Set base URL for relative requests
    client.base = 'https://api.example.com/v1'
    profile = await client.get('/user/123')

# Session with custom configuration
async with Session(
    timeout=60.0,
    headers={'User-Agent': 'MyApp/1.0'},
    cookies={'session': 'abc123'}
) as client:
    response = await client.get('https://api.example.com/data')
```

## Retry Mechanisms

CrawlPy provides automatic retry functionality with the `Retry` class for handling transient failures and unstable connections.

```python
from crawlpy import Retry

# Configure retry with exponential backoff
retry = Retry(
    retries=3,
    multiplier=2.0,       # Exponential backoff: 2, 4, 8 seconds
    statuses=[429, 500, 502, 503, 504],
    timeout=True,         # Retry on timeout errors
    connect=True          # Retry on connection errors
)

# Use retry configuration with requests
response = await crawlpy.get(
    'https://unstable-api.example.com/data',
    retry=retry
)
```

## Rate Limiting

CrawlPy provides intelligent rate limiting with the `Limit` class to control request frequency and avoid overwhelming servers or hitting API limits.

```python
from crawlpy import Limit

# Configure rate limiting with burst allowance
limit = Limit(
    requests=100,      # 100 requests maximum
    window=3600,       # Per hour (3600 seconds)
    batch=10,          # Allow bursts of 10 requests
    delay=0.5          # Minimum 0.5 seconds between requests
)

# Use rate limiter with requests
response = await crawlpy.get(
    'https://api.example.com/data',
    limit=limit
)

# Check rate limiter status
print(f"Remaining requests: {limit.remaining}")
print(f"Reset time: {limit.reset}")
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
print(f"Response: {response.parse()}")

# Advanced proxy configuration
proxy = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://secure-proxy.example.com:8443'
}
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)

# Proxy with custom authentication
import base64
auth = base64.b64encode(b'username:password').decode('ascii')
headers = {'Proxy-Authorization': f'Basic {auth}'}
response = await crawlpy.get(
    'https://httpbin.org/ip',
    proxy='http://proxy.example.com:8080',
    headers=headers
)
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
    response.validate()
    return response.parse()
    
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
    print(f"Request failed after {error.retries} retries: {error}")
    
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
