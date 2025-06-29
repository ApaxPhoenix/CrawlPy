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
json = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=json)

# Form data
data = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=data)
```

### Other Methods
```python
response = await crawlpy.put('https://httpbin.org/put', json=json)
response = await crawlpy.delete('https://httpbin.org/delete')
response = await crawlpy.patch('https://httpbin.org/patch', json=json)
```

## Request Options

```python
# Custom headers
headers = {'User-Agent': 'MyApp/1.0'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Query parameters
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', params=params)

# Timeout in seconds
response = await crawlpy.get('https://httpbin.org/get', timeout=30.0)
```

## Response Object

```python
response = await crawlpy.get('https://httpbin.org/json')

# Response properties
print(response.status)    # HTTP status code (200, 404, etc.)
print(response.text)      # Response body as text
print(response.json())    # Parse JSON response
print(response.headers)   # Response headers dict
print(response.url)       # Final URL after redirects
print(response.type)      # Content type (e.g., 'application/json', 'text/html')
print(response.content)   # Raw bytes
print(response.encoding)  # Character encoding
print(response.elapsed)   # Request duration as timedelta object
```

## Sessions

```python
# Use sessions to persist cookies and headers
async with crawlpy.Session() as session:
    # Set session-wide headers
    session.headers.update({'Authorization': 'Bearer token123'})
    
    # Make requests with persistent session
    response1 = await session.get('https://api.example.com/user')
    response2 = await session.get('https://api.example.com/data')
```

## Proxy Support

```python
# Use a proxy server
response = await crawlpy.get('https://httpbin.org/ip', proxy='http://proxy.com:8080')

# Proxy with authentication
proxy = 'http://username:password@proxy.com:8080'
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)
```

## Authentication

```python
# Basic authentication
response = await crawlpy.get('https://httpbin.org/basic-auth/user/pass', 
                           auth=('user', 'pass'))

# Bearer token
headers = {'Authorization': 'Bearer your-token-here'}
response = await crawlpy.get('https://api.example.com/data', headers=headers)
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
# Disable SSL verification (not recommended for production)
response = await crawlpy.get('https://httpbin.org/get', verify=False)

# Custom SSL certificate
response = await crawlpy.get('https://httpbin.org/get', cert='/path/to/cert.pem')
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
