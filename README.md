# CrawlPy

CrawlPy is a powerful and efficient Python library designed for web crawling and scraping. Whether you're collecting data, monitoring websites, or exploring the web programmatically, CrawlPy simplifies the process with its intuitive API and robust features.

## Installation

To get started with CrawlPy, install it using pip:
```bash
pip install crawlpy
```

## Features

CrawlPy offers a range of features to enhance your web crawling experience:
- **Asynchronous Requests**: Perform multiple requests simultaneously for faster crawling.
- **Cookie Management**: Handle cookies and authentication seamlessly.
- **Proxy Support**: Use proxies to stay anonymous and access geo-restricted content.
- **Headers Handling**: Configure request headers for enhanced control and customization.
- **Data Extraction**: Extract structured data using built-in parsers.
- **Authentication**: Handle various authentication methods with ease.
- **Streaming**: Stream content efficiently with chunk processing.
- **Rate Limiting**: Configure automatic rate limiting to respect website policies.
- **Timeout Control**: Set and manage connection timeouts for reliability.
- **Redirects Management**: Control how redirects are handled during crawling.

## Basic Usage

Here are some examples to demonstrate how you can use CrawlPy for various tasks.

### Making HTTP Requests

CrawlPy supports all major HTTP methods, making it easy to interact with web servers:
```python
from crawlpy import Crawler

# Create a crawler instance
crawler = Crawler()

# Fetch a page using GET
response = await crawler.get(url="http://httpbin.org/get")

# Send data using POST
response = await crawler.post(url="http://httpbin.org/post", json={"key": "value"})

# Delete a resource
response = await crawler.delete(url="http://httpbin.org/delete")

# Update a resource
response = await crawler.put(url="http://httpbin.org/put", json={"update": "info"})
```

## API Reference

### Streaming Functionality

```python
# Download a file in chunks
async with crawler.stream(url="https://example.com/file.zip", path="download.zip") as stream:
    async for chunk in stream.chunks(size=8192):
        print(f"Downloaded {stream.done}%")

# Upload a file in chunks
async with crawler.stream.upload(url="https://example.com/upload", path="file.pdf") as stream:
    async for chunk in stream.chunks():
        print(f"Uploaded {stream.done}%")
        
# Stream large API responses
async with crawler.stream(url="https://api.example.com/large-dataset") as stream:
    async for chunk in stream.chunks():
        # Process each chunk as JSON
        items = json.loads(chunk)
        for item in items:
            process(item)
            
# Resume interrupted download
async with crawler.stream.resume(url="https://example.com/large-file.zip", path="partial.zip") as stream:
    async for chunk in stream.chunks():
        print(f"Downloaded {stream.done}%")
```

### Data Extraction

```python
# Extract structured data with CSS selectors
data = await crawler.extract.css(url="https://example.com", selectors={
    "title": "h1",
    "price": ".product-price",
    "images": ["img.product-image", "src"],
    "description": ".product-description"
})

# Extract with XPath
data = await crawler.extract.xpath(url="https://example.com", paths={
    "title": "//h1/text()",
    "links": "//a/@href"
})
```

### Header Management

```python
# Set headers with one line
crawler.header.set(headers={"User-Agent": "CrawlPy/1.0", "Accept": "application/json"})

# Use a preset user agent
crawler.header.agent(preset="chrome")  # Preset Chrome user agent

# Clear all headers
crawler.header.clear()

# Get current headers
headers = crawler.header.get()

# Set headers for a selection domains
crawler.header.domains(
    endpoints=["api.example.com", "api.another.com"],
    headers={"Authorization": "Bearer token"}
)
```

### Rate Limiting

```python
# Set global rate limit (requests per second)
crawler.limit.rate(seconds=5)  # 5 requests per second

# Set domain-specific rate limits
crawler.limit.domain(endpoints={
    "api.example.com": 2,  # 2 requests per second
    "images.example.com": 10  # 10 requests per second
})

# Temporary pause all requests
await crawler.limit.pause(seconds=60)

# Resume normal request rate
crawler.limit.resume()

# Set concurrency limit 
crawler.limit.concurrency(limit=10)  # Maximum 10 concurrent requests

# Set bandwidth limit
crawler.limit.bandwidth(kilobytes=500)  # 500 KB/s
```

### Timeout Management

```python
# Set global timeout for all requests
crawler.timeout.set(seconds=30)  # 30 seconds

# Set per-domain timeouts
crawler.timeout.domain(timeouts={
    "api.example.com": 60,
    "images.example.com": 10
})

# Disable timeout for specific requests
response = await crawler.get(url="https://example.com", timeout=None)

# Set timeout for specific request types
crawler.timeout.method(timeouts={
    "GET": 30,
    "POST": 60,
    "PUT": 90
})

# Set idle timeout (for maintaining connections)
crawler.timeout.idle(seconds=120)
```

### Proxy Configuration

```python
# Set a single proxy
crawler.proxy.set(proxy="http://proxy:port")

# Set multiple proxies (automatically rotates through them)
crawler.proxy.set(proxies=["http://proxy1:port", "http://proxy2:port", "http://proxy3:port"])

# Set proxy with authentication
crawler.proxy.set(proxy="http://user:pass@proxy:port")

# Set proxy for specific protocol
crawler.proxy.set(protocols={"http": "http://proxy1:port", "https": "https://proxy2:port"})

# Disable proxy
crawler.proxy.clear()

# Get current proxy
current = crawler.proxy.get()
```

### Authentication Methods

```python
# Basic authentication
crawler.auth.basic(username="user", password="pass")

# OAuth2 authentication
crawler.auth.oauth2(
    id="client_id",
    secret="client_secret",
    endpoint="https://api.example.com/token"
)

# API key authentication
crawler.auth.key(value="apikey", name="X-API-Key")

# JWT authentication
crawler.auth.jwt(token="token")

# Clear authentication
crawler.auth.clear()
```

## License

CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
