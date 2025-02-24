# CrawlPy
CrawlPy is a powerful and efficient Python library designed for web crawling and scraping. Whether you're collecting data, monitoring websites, or exploring the web programmatically, CrawlPy simplifies the process with its intuitive API and robust features.

## Installation
To get started with CrawlPy, install it using pip:
```bash
pip install crawlpy
```

## Features
CrawlPy offers a range of features to enhance your web crawling experience:
- **Asynchronous Requests**: Perform multiple requests simultaneously for faster crawling
- **Cookie Management**: Handle sessions and authentication seamlessly
- **Proxy Support**: Use proxies to stay anonymous and access geo-restricted content
- **Custom Headers**: Configure request headers for enhanced control and customization
- **Event System**: React to crawler events in real-time with simple decorators
- **Chainable API**: Build your crawler with fluent, chainable methods
- **Middleware Hooks**: Customize request/response processing
- **Simplified Authentication**: Built-in support for common authentication methods

## Basic Usage
Here are some examples to demonstrate how you can use CrawlPy for various tasks.

### Making HTTP Requests
CrawlPy supports all major HTTP methods, making it easy to interact with web servers:
```python
from crawlpy import Crawler

# Create a crawler instance
crawler = Crawler()

# Fetch a page using GET
url = "http://httpbin.org/get"
response = await crawler.get(url)

# Send data using POST
data = {"key": "value"}
response = await crawler.post(url, json=data)

# Delete a resource using DELETE
response = await crawler.delete(url)

# Update a resource using PUT
data = {"update": "info"}
response = await crawler.put(url, json=data)
```

### Managing Headers
CrawlPy allows you to customize request headers for various purposes such as authentication, user agent specification, or content type negotiation:
```python
# Set headers for your request
headers = {
    "User-Agent": "CrawlPy/1.0",
    "Accept": "application/json",
    "Authorization": "Bearer your_token_here"
}

# Use headers in a single request
response = await crawler.get(url, headers=headers)

# Or set headers globally for all requests
crawler.headers = headers
response = await crawler.get(url)  # Uses the preset headers
```

### Managing Cookies
CrawlPy makes cookie handling straightforward:
```python
# Send cookies with your request
cookies = {"session_id": "abc123"}
response = await crawler.get(url, cookies=cookies)

# Set cookies globally
crawler.cookies = cookies

# Server cookies are automatically managed for subsequent requests
```

### Using Proxies
CrawlPy supports proxies to help you stay anonymous and bypass geo-restrictions:
```python
# Use a proxy for your request
proxy = "http://your_proxy:port"
response = await crawler.get(url, proxy=proxy)

# Or set a global proxy
crawler.proxy = proxy
```

## Event System
CrawlPy provides a robust event system that allows you to react to various crawler events:

```python
from crawlpy import Crawler

crawler = Crawler()

# Register event handlers with simple decorators
@crawler.on("request")
async def handle_request(request):
    print(f"Making request to: {request.url}")

@crawler.on("response")
async def handle_response(response):
    print(f"Received response: {response.status_code}")

@crawler.on("error")
async def handle_error(error, request):
    print(f"Error occurred while processing {request.url}: {error}")

# Events can also be registered using the chaining API
crawler.request(handle_request).response(handle_response).error(handle_error)
```

## Middleware Hooks
Middleware hooks allow you to customize the request/response pipeline:

```python
from crawlpy import Crawler

crawler = Crawler()

# Request middleware
@crawler.on("before")
async def modify_request(request):
    request.headers["Custom-Header"] = "Value"
    return request

# Response middleware
@crawler.on("after")
async def process_response(response):
    if response.status_code == 200:
        # Process successful responses
        pass
    return response

# Error middleware
@crawler.on("error")
async def handle_error(error, request):
    if isinstance(error, ConnectionError):
        # Retry the request
        return await request.retry()
    raise error

# Middleware can also be added using the chaining API
crawler.before(modify_request).after(process_response).handle(handle_error)
```

## Authentication
CrawlPy provides built-in support for common authentication methods:

### Basic Authentication
```python
from crawlpy import Crawler

crawler = Crawler()

# Using basic authentication with simplified method
crawler.auth.basic(username="user", password="pass")

# Make authenticated requests
response = await crawler.get("https://api.example.com/protected")

# Or use a context manager for temporary authentication
async with crawler.auth.basic("user", "pass"):
    response = await crawler.get("https://api.example.com/protected")
```

### OAuth2 Authentication
```python
from crawlpy import Crawler

crawler = Crawler()

# Configure OAuth2 authentication with simplified method
crawler.auth.oauth2(
    id="your_client_id",
    secret="your_client_secret",
    endpoint="https://api.example.com/oauth/token",
    scope=["read", "write"]
)

# Make authenticated requests
response = await crawler.get("https://api.example.com/protected")

# Or use a context manager
async with crawler.auth.oauth2(id="id", secret="secret"):
    response = await crawler.get("https://api.example.com/user/profile")
```

## Rule-Based Crawling
CrawlPy offers an intuitive rule system for controlling crawl behavior:

```python
from crawlpy import Crawler

crawler = Crawler()

# Define rules for URLs to follow or ignore
crawler.rule("*.example.com", follow=True)
crawler.rule("login", ignore=True)
crawler.rule(lambda url: "admin" in url, priority=10)

# Start crawling with a single command
results = await crawler.start(
    urls=["https://example.com"],
    depth=3,
    requests=100,
    concurrency=10
)

for result in results:
    print(f"Crawled {result.url}: {len(result.text)} bytes")
```

## License
CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
