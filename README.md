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
- **Chainable API**: Build your crawler with fluent, chainable methods
- **Simplified Authentication**: Built-in support for common authentication methods
- **Change Detection**: Monitor websites for important changes and trigger actions
- **Content Filtering**: Filter crawled content based on custom criteria
- **Cache Management**: Intelligently cache responses to improve performance
- **Advanced Rule System**: Fine-grained control over crawl behavior with powerful rules
- **Download & Upload**: Transfer files to and from remote servers with ease
- **Streaming Support**: Process crawled data in real-time
- **Schema Validation**: Validate extracted data against defined schemas
- **Retry Strategies**: Smart retry logic for failed requests
- **Resource Limits**: Control CPU, memory and bandwidth usage
- **Interactive Sessions**: Maintain state across multiple requests
- **Pagination Handling**: Automatically navigate through paginated content
- **Page Actions**: Simulate user actions like clicking and form submission

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

## Organized API Groups
CrawlPy organizes related functionality into logical groups for easy access:

### Headers Group
```python
# Set headers for your request
crawler.header.set({
    "User-Agent": "CrawlPy/1.0",
    "Accept": "application/json",
    "Authorization": "Bearer your_token_here"
})

# Add a single header
crawler.header.add("Referer", "https://example.com")

# Use a preset user agent
crawler.header.agent("chrome")  # Preset Chrome user agent
```

### Cookies Group
```python
# Set cookies for all requests
crawler.cookie.set({"id": "abc123"})

# Add a single cookie
crawler.cookie.add("preference", "dark-mode")

# Clear all cookies
crawler.cookie.clear()

# Export cookies to a file
await crawler.cookie.save("~./cookies.json")

# Import cookies from a file
await crawler.cookie.load("~./cookies.json")
```

### Proxy Group
```python
# Set a proxy for all requests
crawler.proxy.set("http://proxy:port")

# Use a proxy for specific domains
crawler.proxy.unique("http://example.com", "http://proxy:port")

# Use proxy rotation
crawler.proxy.rotate(["http://proxy1:port", "http://proxy2:port", "http://proxy3:port"])
```

### Auth Group
```python
# Basic authentication
crawler.auth.basic("username", "password")

# OAuth2 authentication
crawler.auth.oauth("id", "secret", "https://api.example.com/token")

# API key authentication
crawler.auth.key("key")

# Custom auth scheme
crawler.auth.custom(lambda request: request.header.add("X-Token", "token"))
```

### Cache Group
```python
# Enable caching
crawler.cache.on()

# Configure cache settings
crawler.cache.setup(
    path="~./cache",
    limit="500MB",
    ttl="4h"
)

# Set expiration rules
crawler.cache.expire({
    "html": "1h",
    "json": "30m",
    "image": "7d"
})

# Clear cache
crawler.cache.clear()
```

### Filter Group
```python
# Filter by status code
crawler.filter.status(200)

# Filter by content type
crawler.filter.type("image/*")

# Filter by content
crawler.filter.item(".item")

# Combine filters
crawler.filter.all([
    crawler.filter.status(200),
    crawler.filter.item(".item")
])
```

### Rule Group
```python
# Follow specific URLs
crawler.rule.follow("*.example.com/product/*")

# Ignore specific URLs
crawler.rule.skip("login", "admin", "logout")

# Set priority for certain paths
crawler.rule.boost("/sale/*", level=10)

# Limit crawl depth for certain paths
crawler.rule.depth("/forum/*", max=2)
```

### Monitor Group
```python
# Monitor a page for any changes
watcher = crawler.monitor.page("https://example.com/prices")

# React to changes
@watcher.on_change(".price")
async def price_updated(old, new, url):
    print(f"Price changed from {old} to {new}")
    
# Check for changes manually
changes = await watcher.check()

# Start automatic monitoring
await watcher.start(every="15m")

# Stop monitoring
await watcher.stop()
```

## File Operations

### Download Support
```python
# Download a file to disk
await crawler.download("https://example.com/file.pdf", "local_file.pdf")

# Download with progress callback
await crawler.download(
    "https://example.com/large-file.zip",
    "local-file.zip",
    progress=lambda done, total: print(f"Downloaded {done/total*100:.1f}%")
)

# Download multiple files
files = [
    "https://example.com/file1.pdf",
    "https://example.com/file2.pdf"
]
await crawler.download.batch(files, "./downloads/")

# Resume partial downloads
await crawler.download.resume("https://example.com/large-file.zip", "partial-file.zip")
```

### Upload Support
```python
# Upload a file
await crawler.upload("local-file.pdf", "https://example.com/upload")

# Upload with custom form field name
await crawler.upload(
    "profile.jpg",
    "https://example.com/profile-picture",
    field="avatar"
)

# Upload multiple files
files = [
    "document1.pdf",
    "document2.pdf"
]
await crawler.upload.batch(files, "https://example.com/documents")

# Upload with progress tracking
await crawler.upload(
    "large-file.zip",
    "https://example.com/upload",
    progress=lambda sent, total: print(f"Uploaded {sent/total*100:.1f}%")
)
```

## Streaming Support
Process data as it's crawled, ideal for handling large datasets:

```python
# Stream results as they are crawled
async for page in crawler.stream("https://example.com"):
    print(f"Crawled: {page.url}")
    
# Stream with filtering
async for product in crawler.stream("https://store.example.com", filter=".product"):
    print(f"Found product: {product.text('.title')}")
    
# Stream with transformation
async for item in crawler.stream("https://api.example.com/items", transform=lambda x: x.json()):
    save_to_database(item)

# Paginated streaming
async for result in crawler.stream.pages(
    "https://api.example.com/search",
    next_page=".pagination .next",
    max_pages=5
):
    process_search_result(result)
```

## Schema Validation
Define and validate data structures with simple schema definitions:

```python
# Define a schema
product_schema = crawler.schema({
    "name": "string:required",
    "price": "number:required",
    "description": "string",
    "in_stock": "boolean:required",
    "variants": ["object"],
    "tags": ["string"]
})

# Extract data with schema validation
products = await crawler.get("https://store.example.com").extract(".product", schema=product_schema)

# Handle validation errors
try:
    products = await crawler.get("https://store.example.com").extract(".product", schema=product_schema)
except crawler.SchemaError as e:
    print(f"Validation failed: {e.errors}")
    
# Transform data during validation
size_schema = crawler.schema({
    "value": "string:required",
    "unit": "string:required"
}, transform=lambda data: {
    "value": data.split()[0],
    "unit": data.split()[1]
})
```

## Session Management
Maintain state across multiple requests:

```python
# Create a session
session = crawler.session()

# Login to a website
await session.login(
    "https://example.com/login",
    username="user",
    password="pass"
)

# Make authenticated requests
profile = await session.get("https://example.com/profile")

# Check if logged in
if await session.check(".logout-button"):
    print("Successfully logged in")
    
# Save session for later
await session.save("my-session.json")

# Load a previously saved session
await session.load("my-session.json")
```

## Retry Strategies
Smart handling of request failures:

```python
# Set up retry behavior
crawler.retry.setup(
    attempts=3,
    wait="2s",
    codes=[500, 502, 503, 504]
)

# Use exponential backoff
crawler.retry.backoff(
    base="1s",
    factor=2,
    max="30s"
)

# Retry with custom condition
crawler.retry.when(lambda response: "try again later" in response.text)

# Disable retries for specific requests
await crawler.get("https://example.com/noretry", retry=False)
```

## Resource Limits
Control how CrawlPy uses system resources:

```python
# Set global limits
crawler.limit.requests(per_second=5)
crawler.limit.memory("500MB")
crawler.limit.connections(max=20)

# Set domain-specific limits
crawler.limit.domain("example.com", per_second=2)

# Automatically pause when reaching limits
crawler.limit.auto_pause(True)

# Monitor resource usage
stats = await crawler.limit.stats()
print(f"Memory usage: {stats.memory_used}/{stats.memory_limit}")
```

## Page Actions
Simulate user interactions with web pages:

```python
# Click elements
await crawler.page("https://example.com").click(".button")

# Fill forms
await crawler.page("https://example.com/contact").fill({
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello, world!"
})

# Submit forms
await crawler.page("https://example.com/login").submit(
    "#login-form",
    {
        "username": "user",
        "password": "pass"
    }
)

# Scroll the page
await crawler.page("https://example.com/feed").scroll(to=".load-more")

# Wait for elements or conditions
await crawler.page("https://example.com/app").wait(".content-loaded")
```

## License
CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
