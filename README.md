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
```python
import crawlpy

response = await crawlpy.get('https://httpbin.org/get')
```

### POST Requests
```python
import crawlpy

# JSON data
data = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=data)

# Form data
form = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=form)
```

### Other HTTP Methods
```python
import crawlpy

response = await crawlpy.put('https://httpbin.org/put', json=data)
response = await crawlpy.delete('https://httpbin.org/delete')
response = await crawlpy.patch('https://httpbin.org/patch', json=data)
response = await crawlpy.head('https://httpbin.org/get')
response = await crawlpy.options('https://httpbin.org/get')
```

## Headers and Parameters

Control request headers and URL parameters to customize how your requests are sent.

```python
import crawlpy

# Custom headers
headers = {'User-Agent': 'CrawlPy'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Query parameters
parameters = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', parameters=parameters)
```

## Timeouts

Configure timeouts to control how long requests wait for responses and connections.

```python
import crawlpy
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
import crawlpy
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
import crawlpy
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

## Session Management

Sessions allow you to persist settings across multiple requests and maintain state.

### Basic Session Usage

Configure sessions with custom timeout, retry, and connection settings.

```python
import crawlpy
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

### Session Adapters

Use adapters to customize how sessions handle specific protocols or domains.

```python
import crawlpy
from crawlpy import Session, HTTPAdapter, Retry

# Custom adapter for specific domain
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

### Single Proxy

Configure and use a single proxy for your requests.

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

### Multiple Proxies

Use different proxies for different protocols or requirements.

```python
import crawlpy
from crawlpy import Proxy

# Multiple proxies for different protocols
proxies = {
    'http': Proxy('http://proxy1.com:8080'),
    'https': Proxy('https://proxy2.com:8080', username='user', password='pass')
}
response = await crawlpy.get('https://api.example.com/data', proxies=proxies)
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
from crawlpy import HTTPError, TimeoutError, ConnectionError, RequestError

try:
    response = await crawlpy.get('https://httpbin.org/status/404')
    response.raise_for_status()  # Raises exception for 4xx/5xx status codes
    
except HTTPError as error:
    print(f"HTTP error: {error.response.status}")
    
except TimeoutError as error:
    print(f"Request timed out: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except RequestError as error:
    print(f"Request error: {error}")
```
