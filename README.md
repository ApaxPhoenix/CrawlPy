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
- **Event System**: React to crawler events in real-time
- **Middleware Hooks**: Customize request/response processing
- **Authentication Handlers**: Built-in support for common authentication methods

## Basic Usage
Here are some examples to demonstrate how you can use CrawlPy for various tasks.

### Making HTTP Requests
CrawlPy supports all major HTTP methods, making it easy to interact with web servers:
```python
from crawlpy import crawler

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
```

### Managing Cookies
CrawlPy makes cookie handling straightforward:
```python
# Send cookies with your request
cookies = {"session_id": "abc123"}
response = await crawler.get(url, cookies=cookies)

# Server cookies are automatically managed for subsequent requests
```

### Using Proxies
CrawlPy supports proxies to help you stay anonymous and bypass geo-restrictions:
```python
# Use a proxy for your request
proxy = "http://your_proxy:port"
response = await crawler.get(url, proxy=proxy)
```

## Event System
CrawlPy provides a robust event system that allows you to react to various crawler events:

```python
from crawlpy import crawler, events

# Register event handlers
@events.on_request
async def handle_request(request):
    print(f"Making request to: {request.url}")

@events.on_response
async def handle_response(response):
    print(f"Received response: {response.status_code}")

@events.on_error
async def handle_error(error, request):
    print(f"Error occurred while processing {request.url}: {error}")

# Events can also be registered using the event emitter
crawler.events.on("request", handle_request)
crawler.events.on("response", handle_response)
crawler.events.on("error", handle_error)
```

## Middleware Hooks
Middleware hooks allow you to customize the request/response pipeline:

```python
from crawlpy import crawler, hooks

# Request middleware
@hooks.before_request
async def modify_request(request):
    request.headers["Custom-Header"] = "Value"
    return request

# Response middleware
@hooks.after_response
async def process_response(response):
    if response.status_code == 200:
        # Process successful responses
        pass
    return response

# Error middleware
@hooks.on_error
async def handle_error(error, request):
    if isinstance(error, ConnectionError):
        # Retry the request
        return await request.retry()
    raise error
```

## Authentication
CrawlPy provides built-in support for common authentication methods:

### Basic Authentication
```python
from crawlpy import crawler, auth

# Using basic authentication
handler = auth.BasicAuth(username="user", password="pass")
crawler.auth = handler

# Make authenticated requests
response = await crawler.get("https://api.example.com/protected")
```

### OAuth2 Authentication
```python
from crawlpy import crawler, auth

# Configure OAuth2 authentication
config = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "token_url": "https://api.example.com/oauth/token",
    "scope": ["read", "write"]
}

handler = auth.OAuth2(config)
crawler.auth = handler

# Make authenticated requests
response = await crawler.get("https://api.example.com/protected")
```

## License
CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
