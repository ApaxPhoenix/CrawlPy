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

```python
import crawlpy

# Single request
response = await crawlpy.get('https://httpbin.org/get')
print(f"Status: {response.status}")
print(f"JSON: {response.parse()}")

# Multiple requests
urls = [
    'https://httpbin.org/get',
    'https://httpbin.org/ip',
    'https://httpbin.org/agent'
]
responses = await crawlpy.get(urls)

for response in responses:
    print(f"Status: {response.status}")
```

## HTTP Methods

### GET Requests

```python
# Basic GET
response = await crawlpy.get('https://httpbin.org/get')

# GET with params
params = {'page': 1, 'limit': 10}
response = await crawlpy.get('https://httpbin.org/get', params=params)

# GET with headers
headers = {'User-Agent': 'MyApp'}
response = await crawlpy.get('https://httpbin.org/get', headers=headers)

# Multiple GET
urls = ['https://httpbin.org/get', 'https://httpbin.org/ip']
responses = await crawlpy.get(urls)
```

### POST Requests

```python
# POST with JSON
json = {'name': 'John', 'email': 'john@example.com'}
response = await crawlpy.post('https://httpbin.org/post', json=json)

# POST with data
data = {'username': 'john', 'password': 'secret'}
response = await crawlpy.post('https://httpbin.org/post', data=data)

# POST with files
files = {'document': open('file.pdf', 'rb')}
response = await crawlpy.post('https://httpbin.org/post', files=files)
```

### Other Methods

```python
# PUT
json = {'status': 'updated'}
response = await crawlpy.put('https://httpbin.org/put', json=json)

# DELETE
response = await crawlpy.delete('https://httpbin.org/delete')

# PATCH
json = {'status': 'partial'}
response = await crawlpy.patch('https://httpbin.org/patch', json=json)

# HEAD
response = await crawlpy.head('https://httpbin.org/get')
```

## Response Objects

```python
response = await crawlpy.get('https://httpbin.org/json')

# Response properties
status = response.status
headers = response.headers
url = response.url
text = response.text
content = response.content
data = response.parse()
elapsed = response.elapsed
encoding = response.encoding

# Validate response
try:
    response.validate()
    print(f"Success: {status}")
except crawlpy.HTTPError as error:
    print(f"Error: {error}")
```

## Request Building

```python
# Build GET
request = crawlpy.build('GET', 'https://httpbin.org/get')
print(f"Method: {request.method}")
print(f"URL: {request.url}")

# Build POST
json = {'user': 'john', 'pass': 'secret'}
request = crawlpy.build('POST', 'https://httpbin.org/post', json=json)

# Build with headers
headers = {'Authorization': 'Bearer token'}
params = {'limit': 10}
request = crawlpy.build('GET', 'https://api.com/data', headers=headers, params=params)

# Execute request
response = await crawlpy.execute(request)
```

## Sessions

```python
from crawlpy import Session

# Basic session
async with Session() as session:
    headers = {'User-Agent': 'CrawlPy'}
    session.headers.update(headers)
    response = await session.get('https://httpbin.org/get')

# Session with config
timeout = 60.0
headers = {'User-Agent': 'MyApp'}
cookies = {'session': 'abc123'}

async with Session(timeout=timeout, headers=headers, cookies=cookies) as session:
    response = await session.get('https://api.example.com/data')
```

## Retry Mechanisms

```python
from crawlpy import Retry

# Basic retry
retries = 3
multiplier = 2.0
statuses = [429, 500, 502, 503, 504]
timeout = True
connect = True

retry = Retry(retries=retries, multiplier=multiplier, statuses=statuses, timeout=timeout, connect=connect)
response = await crawlpy.get('https://unstable-api.com/data', retry=retry)

# Advanced retry with jitter
retries = 5
multiplier = 1.5
maximum = 30.0
jitter = True
statuses = [408, 429, 500, 502, 503, 504]
timeout = True
connect = True

retry = Retry(retries=retries, multiplier=multiplier, maximum=maximum, jitter=jitter, statuses=statuses, timeout=timeout, connect=connect)

urls = [f'https://api.service.com/page/{i}' for i in range(1, 11)]
responses = await crawlpy.get(urls, retry=retry)

for i, response in enumerate(responses, 1):
    if response.status == 200:
        print(f"Page {i}: Success")
    else:
        print(f"Page {i}: Failed")

# Conditional retry
def condition(response):
    if response.status == 200:
        data = response.parse()
        return data.get('status') == 'processing'
    return response.status in [429, 500, 502, 503, 504]

retries = 10
multiplier = 1.2
minimum = 1.0
maximum = 60.0
backoff = 'linear'

retry = Retry(retries=retries, multiplier=multiplier, minimum=minimum, maximum=maximum, condition=condition, backoff=backoff)
response = await crawlpy.get('https://api.com/task/123', retry=retry)
```

## Rate Limiting

```python
from crawlpy import Rate

# Basic rate limiting
requests = 100
window = 3600
batch = 10
delay = 0.5

rate = Rate(requests=requests, window=window, batch=batch, delay=delay)
response = await crawlpy.get('https://api.example.com/data', rate=rate)

print(f"Remaining: {rate.remaining}")
print(f"Reset: {rate.reset}")

# Advanced rate limiting
requests = 1000
window = 3600
burst = 50
adaptive = True
headers = ['X-RateLimit-Remaining', 'X-RateLimit-Reset']

rate = Rate(requests=requests, window=window, burst=burst, adaptive=adaptive, headers=headers)

urls = [f'https://api.bigdata.com/records/{i}' for i in range(1, 2001)]
batch = 20
results = []

for i in range(0, len(urls), batch):
    batch_urls = urls[i:i+batch]
    responses = await crawlpy.get(batch_urls, rate=rate)
    
    for response in responses:
        if response.status == 200:
            results.append(response.parse())
    
    print(f"Processed {len(results)} records")

# Smart rate limiting with backoff
requests = 500
window = 3600
delay = 0.2
backoff = True
factor = 2.0
maximum = 10.0

rate = Rate(requests=requests, window=window, delay=delay, backoff=backoff, factor=factor, maximum=maximum)

urls = [f'https://social-api.com/posts/{i}' for i in range(1, 1001)]
posts = []

for url in urls:
    try:
        response = await crawlpy.get(url, rate=rate)
        if response.status == 200:
            posts.append(response.parse())
        elif response.status == 429:
            print("Rate limited, backing off")
    except crawlpy.Limited as error:
        print(f"Rate limit exceeded, wait {error.wait}s")
        break

print(f"Collected {len(posts)} posts")
```

## Proxy Support

```python
# Single proxy
proxy = 'http://proxy.com:8080'
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)

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

# Protocol proxies
proxy = {
    'http': 'http://fast-proxy.com:8080',
    'https': 'https://secure-proxy.com:8443'
}
response = await crawlpy.get('https://httpbin.org/ip', proxy=proxy)

# Geographic proxies
proxy = [
    'http://nyc.proxies.com:8080',
    'http://lax.proxies.com:8080',
    'http://mia.proxies.com:8080',
    'http://chi.proxies.com:8080'
]

urls = [
    'https://api.weather.com/forecast',
    'https://api.news.com/headlines',
    'https://api.finance.com/stocks'
]

responses = await crawlpy.get(urls, proxy=proxy)

for response in responses:
    print(f"Response time: {response.elapsed}s")
```

## Error Handling

```python
import crawlpy
from crawlpy import HTTPError, Timeout, ConnectionError, RetryError, Limited

try:
    timeout = 10.0
    response = await crawlpy.get('https://httpbin.org/status/404', timeout=timeout)
    response.validate()
    return response.parse()
    
except HTTPError as error:
    status = error.response.status
    url = error.response.url
    print(f"HTTP Error {status} for {url}")
    
except Limited as error:
    wait = error.wait
    print(f"Rate limited. Wait {wait}s")
    
except RetryError as error:
    retries = error.retries
    print(f"Failed after {retries} retries")
    
except Timeout as error:
    print(f"Timeout: {error}")
    
except ConnectionError as error:
    print(f"Connection failed: {error}")
    
except Exception as error:
    print(f"Error: {error}")
```
