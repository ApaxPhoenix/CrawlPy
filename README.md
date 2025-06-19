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
persons = await crawlpy.get('https://httpbin.org/get')
print(f"Status: {persons.status}")
print(f"JSON: {persons.json()}")

# Execute multiple requests concurrently
urls = [
    'https://httpbin.org/get',
    'https://httpbin.org/ip',
    'https://httpbin.org/user-agent'
]
results = await crawlpy.get(urls)

for r in results:
    print(f"Status: {r.status}, URL: {r.url}")
```

## HTTP Methods

CrawlPy supports all standard HTTP methods with consistent async interfaces and common parameters including headers, timeouts, and authentication.

### GET Requests

```python
# Execute basic GET request
persons = await crawlpy.get('https://httpbin.org/get')

# Send GET request with query parameters
params = {'page': 1, 'limit': 10}
persons = await crawlpy.get('https://httpbin.org/get', params=params)

# Send GET request with custom headers
headers = {'User-Agent': 'MyApp/1.0'}
persons = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Execute multiple GET requests simultaneously
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
results = await crawlpy.get(urls)
```

### POST Requests

CrawlPy automatically sets appropriate Content-Type headers based on the data format provided.

```python
# Send POST request with JSON payload
data = {'name': 'John', 'email': 'john@example.com'}
persons = await crawlpy.post('https://httpbin.org/post', json=data)

# Submit form data via POST request
form = {'username': 'john', 'password': 'secret'}
persons = await crawlpy.post('https://httpbin.org/post', data=form)

# Upload file through POST request
with open('file.pdf', 'rb') as file:
    files = {'document': file}
    persons = await crawlpy.post('https://httpbin.org/post', files=files)
```

### Other Methods

```python
# Prepare data payload for various operations
data = {'status': 'updated'}

# Send PUT request to replace entire resource
resp = await crawlpy.put('https://httpbin.org/put', json=data)

# Send DELETE request to remove resource
resp = await crawlpy.delete('https://httpbin.org/delete')

# Send PATCH request for partial resource modification
patch = {'status': 'partial'}
resp = await crawlpy.patch('https://httpbin.org/patch', json=patch)

# Send HEAD request to retrieve headers only
resp = await crawlpy.head('https://httpbin.org/get')
```

## Response Objects

Response objects provide comprehensive access to HTTP response data with automatic parsing and error handling.

```python
# Retrieve response from API endpoint
persons = await crawlpy.get('https://httpbin.org/json')

# Access response metadata
status = persons.status        # HTTP status code
headers = persons.headers      # Response headers dictionary
url = persons.url             # Final URL after redirects

# Extract response content in different formats
text = persons.text           # Response body as string
content = persons.content     # Response body as bytes
data = persons.json()         # Parsed JSON response

# Retrieve performance and encoding information
elapsed = persons.elapsed     # Request duration in seconds
encoding = persons.encoding   # Character encoding

# Handle response errors
try:
    persons.raise_for_status()  # Raises exception for 4xx/5xx status codes
    print(f"Success: {status}")
except crawlpy.HTTPError as error:
    print(f"Error: {error}")
```

## Request Preparation

The request preparation system enables request building and modification before transmission, useful for inspection, batch processing, or applying transformations.

```python
# Build GET request without executing
response = crawlpy.prepare('GET', 'https://httpbin.org/get')
print(f"Method: {response.method}")
print(f"URL: {response.url}")
print(f"Headers: {response.headers}")

# Construct POST request with JSON data
data = {'user': 'john', 'pass': 'secret'}
response = crawlpy.prepare('POST', 'https://httpbin.org/post', json=data)
print(f"Body: {response.body}")

# Build request with custom headers and parameters
headers = {'Auth': 'Bearer token123'}
params = {'limit': 10, 'page': 1}
response = crawlpy.prepare('GET', 'https://api.com/data', 
                     headers=headers, params=params)

# Execute prepared request
persons = await crawlpy.send(response)
print(f"Status: {persons.status}")

# Modify prepared request before execution
response.headers['User-Agent'] = 'CrawlPy/1.0'
response.url = 'https://httpbin.org/headers'
persons = await crawlpy.send(response)
```

## Sessions

Sessions maintain cookies and connection pools across requests.

```python
from crawlpy import Session

# Create session
async with Session() as session:
    # Set default headers
    session.headers.update({'User-Agent': 'CrawlPy/2.0'})
    
    # Make request with session
    persons = await session.get('https://httpbin.org/get')
    
    # Set base URL
    session.base = 'https://api.example.com/v1'
    profile = await session.get('/user/123')

# Manual session management
session = Session(timeout=30.0)
persons = await session.get('https://httpbin.org/get')
await session.close()
```

## Proxy Support

CrawlPy provides comprehensive proxy support for anonymous browsing, geo-location spoofing, and load distribution.

```python
# Configure single proxy for request
persons = await crawlpy.get(
    'https://httpbin.org/ip',
    proxy='http://proxy.example.com:8080'
)

# Use authenticated proxy
auth = 'http://user:pass@proxy.example.com:8080'
persons = await crawlpy.get('https://httpbin.org/ip', proxy=auth)

# Configure proxy pool for automatic rotation
pool = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://proxy3.example.com:8080'
]

# Execute request with automatic proxy rotation
persons = await crawlpy.get('https://httpbin.org/ip', proxies=pool)
print(f"Response: {persons.json()}")
```

## Error Handling

CrawlPy provides specific exception types for different error conditions, enabling appropriate handling of network issues, timeouts, and HTTP errors.

```python
import crawlpy
from crawlpy import HTTPError, Timeout, ConnectionError

try:
    # Execute request with timeout specification
    persons = await crawlpy.get('https://httpbin.org/status/404', timeout=10.0)
    # Validate status code for success (200-299)
    persons.raise_for_status()
    return persons.json()
    
except HTTPError as error:
    # Handle HTTP errors (4xx client errors, 5xx server errors)
    status = error.response.status
    url = error.response.url
    print(f"HTTP Error {status} for URL: {url}")
    
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
