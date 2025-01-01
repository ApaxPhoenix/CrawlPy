# CrawlPy

A powerful and flexible Python library for web crawling and scraping with support for async operations, proxy management, and data extraction.

## Installation

Install CrawlPy using pip:

```bash
pip install crawlpy
```

## Features

- Async HTTP requests support
- Cookie management
- Proxy routing
- HTML parsing and data extraction
- Flexible selectors for element retrieval

## Basic Usage

### Making HTTP Requests

CrawlPy supports all standard HTTP methods (GET, POST, PUT, DELETE) through a unified async interface:

```python
from crawlpy import crawler

# GET request
url = "http://httpbin.org/get"
response = await crawler.request("GET", url)

# POST request with JSON data
data = {"key": "value"}
response = await crawler.request("POST", url, json=data)
```

### Working with Cookies

Manage cookies for session handling and authentication:

```python
# Send cookies with request
cookies = {"session_id": "abc123"}
response = await crawler.request("GET", url, cookies=cookies)

# Server-side cookies are automatically handled for subsequent requests
```

### Using Proxies

Route requests through a proxy server:

```python
proxy = "http://your_proxy:port"
response = await crawler.request("GET", url, proxy=proxy)
```

### Data Extraction

CrawlPy provides two powerful tools for parsing and extracting data:

#### Retriever

Extract URLs and HTML fragments:

```python
from crawlpy import Retriever

retriever = Retriever(response)
urls = retriever.urls
fragments = retriever.fragments
```

#### Selector

Extract specific elements using various selectors:

```python
from crawlpy import Selector

selector = Selector(response)
links = selector.get_elements_by_tag("a")
elements = selector.get_elements_by_classification("example")
```

## Advanced Usage

### Complete Request Example

```python
async def fetch_data():
    url = "http://example.com/api"
    headers = {"Authorization": "Bearer token123"}
    cookies = {"user_session": "abc123"}
    proxy = "http://proxy.example.com:8080"

    response = await crawler.request(
        method="POST",
        url=url,
        headers=headers,
        cookies=cookies,
        proxy=proxy,
        json={"query": "data"}
    )
    
    return response
```

### Error Handling

```python
try:
    response = await crawler.request("GET", url)
except ConnectionError:
    print("Failed to connect to server")
except TimeoutError:
    print("Request timed out")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
