# CrawlPy
**Async HTTP Client Library**

CrawlPy is an asynchronous HTTP client library for Python that provides a clean interface for making HTTP requests with async/await support.

## Installation

```bash
pip install crawlpy
```

## Basic Usage

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

### GET Request
```python
response = await crawlpy.get('https://httpbin.org/get')
```

### POST Request
```python
# JSON data
data = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=data)

# Form data
form = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=form)
```

### Other Methods
```python
response = await crawlpy.put('https://httpbin.org/put', json=data)
response = await crawlpy.delete('https://httpbin.org/delete')
response = await crawlpy.patch('https://httpbin.org/patch', json=data)
response = await crawlpy.head('https://httpbin.org/get')
response = await crawlpy.options('https://httpbin.org/get')
```

# Request Configuration

## Headers and Parameters

```python
# Custom headers
headers = {'User-Agent': 'CrawlPy'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', params=params)
```

## Timeout Configuration

```python
# Simple timeout
response = await crawlpy.get('https://httpbin.org/get', timeout=10.0)

# Advanced timeout settings
timeout = crawlpy.Timeout(connect=5.0, read=30.0, write=10.0, pool=60.0)
response = await crawlpy.get('https://httpbin.org/get', timeout=timeout)
```

## Retry Logic

```python
# Basic retry
retry = crawlpy.Retry(total=3)
response = await crawlpy.get('https://httpbin.org/get', retry=retry)

# Advanced retry with backoff
retry = crawlpy.Retry(total=5, backoff=1.5, status=[500, 502, 503, 504])
response = await crawlpy.get('https://httpbin.org/get', retry=retry)
```

## Connection Pooling

```python
# Custom connection limits
limits = crawlpy.Limits(max_connections=50, max_keepalive=10)
response = await crawlpy.get('https://httpbin.org/get', limits=limits)

# Per-host limits
limits = crawlpy.Limits(max_connections=100, max_per_host=20)
response = await crawlpy.get('https://httpbin.org/get', limits=limits)
```

## Response Object

```python
response = await crawlpy.get('https://httpbin.org/json')

# Status and basic info
print(response.status)          # 200
print(response.reason)          # 'OK'
print(response.url)             # Final URL after redirects
print(response.encoding)        # 'utf-8'
print(response.elapsed)         # Request duration as timedelta

# Content access
print(response.text)            # Response as text
print(response.content)         # Raw bytes
print(response.json())          # Parse JSON
print(response.headers)         # Headers dict-like object
print(response.type)            # Content type (e.g., 'application/json', 'text/html')
```

# Sessions

```python
# Session with persistent settings
async with crawlpy.Session() as session:
    # Configure session-wide settings
    session.headers.update({'Authorization': 'Bearer token123'})
    session.cookies.update({'session_id': 'abc123'})
    
    # All requests in this session will use these settings
    user = await session.get('https://api.example.com/user')
    data = await session.get('https://api.example.com/data')

# Session with configuration
session = crawlpy.Session(
    timeout=crawlpy.Timeout(connect=5.0, read=30.0),
    retry=crawlpy.Retry(total=3, backoff=2.0),
    limits=crawlpy.Limits(max_connections=100, max_keepalive=20),
    proxies={'https': 'http://proxy.example.com:8080'}
)

async with session:
    response = await session.get('https://api.example.com/data')
```

## Proxy Support

```python
# Use a proxy server
response = await crawlpy.get('https://httpbin.org/ip', proxy='http://proxy.com:8080')

# Proxy with authentication
proxy = 'http://user:pass@proxy.com:8080'
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)
```

# Authentication

## Basic Authentication

```python
# Basic authentication
auth = crawlpy.BasicAuth('username', 'password')
response = await crawlpy.get('https://api.example.com/secure', auth=auth)
```

## Digest Authentication

```python
# Digest authentication
auth = crawlpy.DigestAuth('username', 'password')
response = await crawlpy.get('https://api.example.com/secure', auth=auth)
```

## Bearer Token

```python
# Bearer token
auth = crawlpy.BearerAuth('your-jwt-token')
response = await crawlpy.get('https://api.example.com/secure', auth=auth)
```

## OAuth

```python
# OAuth authentication
auth = crawlpy.OAuth('consumer_key', 'consumer_secret', 'token', 'token_secret')
response = await crawlpy.get('https://api.example.com/secure', auth=auth)
```



## Cookies

```python
# Send cookies
cookies = {'session_id': 'abc123', 'user': 'john'}
response = await crawlpy.get('https://httpbin.org/cookies', cookies=cookies)

# Access response cookies
print(response.cookies)
```





## SSL Configuration

```python
import ssl

# Custom SSL context
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_REQUIRED
response = await crawlpy.get('https://example.com', ssl=context)

# Client certificate
context = ssl.create_default_context()
context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')
response = await crawlpy.get('https://example.com', ssl=context)
```



## Error Handling

```python
try:
    response = await crawlpy.get('https://httpbin.org/status/404')
    response.raise_for_status()  # Raises exception for 4xx/5xx status codes
    
except crawlpy.HTTPError as error:
    print(f"HTTP error: {error.response.status}")
    
except crawlpy.TimeoutError as error:
    print(f"Request timed out: {error}")
    
except crawlpy.ConnectionError as error:
    print(f"Connection failed: {error}")
    
except crawlpy.RequestError as error:
    print(f"Request error: {error}")
```
