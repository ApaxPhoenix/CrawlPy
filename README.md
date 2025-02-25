I'll update the CrawlPy documentation to simplify by removing the specified groups and making the Stream group more focused, while adding two more features from the requests library.

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
- **Cookie Management**: Handle sessions and authentication seamlessly.
- **Proxy Support**: Use proxies to stay anonymous and access geo-restricted content.
- **Custom Headers**: Configure request headers for enhanced control and customization.
- **Data Extraction**: Extract structured data using built-in parsers.
- **Authentication**: Handle various authentication methods with ease.
- **Streaming**: Stream content efficiently with chunk processing.

## Basic Usage
Here are some examples to demonstrate how you can use CrawlPy for various tasks.

### Making HTTP Requests
CrawlPy supports all major HTTP methods, making it easy to interact with web servers:
```python
from crawlpy import Crawler

# Create a crawler instance
crawler = Crawler()

# Fetch a page using GET
response = await crawler.get("http://httpbin.org/get")

# Send data using POST
response = await crawler.post("http://httpbin.org/post", json={"key": "value"})

# Delete a resource
response = await crawler.delete("http://httpbin.org/delete")

# Update a resource
response = await crawler.put("http://httpbin.org/put", json={"update": "info"})
```

## Organized API Groups

### Headers Group
```python
# Set headers with one line
crawler.header.set({"User-Agent": "CrawlPy/1.0", "Accept": "application/json"})

# Use a preset user agent
crawler.header.agent("chrome")  # Preset Chrome user agent

# Clear all headers
crawler.header.clear()

# Get current headers
headers = crawler.header.get()
```

### Cookies Group
```python
# Set cookies for all requests
crawler.cookie.set({"session": "abc123", "preference": "dark-mode"})

# Export/import cookies with one command
await crawler.cookie.save("cookies.json")
await crawler.cookie.load("cookies.json")

# Get a specific cookie
session = crawler.cookie.get("session")

# Delete a specific cookie
crawler.cookie.delete("preference")
```

### Proxy Group
```python
# Set a proxy with one line
crawler.proxy.set("http://proxy:port")

# Rotate through multiple proxies automatically
crawler.proxy.rotate(["http://proxy1:port", "http://proxy2:port"])

# Disable proxy
crawler.proxy.disable()

# Check current proxy
proxy = crawler.proxy.current()
```

### Data Extraction Group
```python
# Extract structured data with CSS selectors
data = await crawler.extract.css("https://example.com", {
    "title": "h1",
    "price": ".product-price",
    "images": ["img.product-image", "src"],
    "description": ".product-description"
})

# Extract with XPath
data = await crawler.extract.xpath("https://example.com", {
    "title": "//h1/text()",
    "links": "//a/@href"
})

# Extract data with JSON paths
json = await crawler.extract.json("https://api.example.com/products")
names = crawler.extract.path(json, "$.products[*].name")
```

### Auth Group
```python
# Basic authentication
crawler.auth.basic("user", "pass")

# OAuth2 authentication
crawler.auth.oauth2(
    id="client_id",
    secret="client_secret",
    url="https://api.example.com/token"
)

# API key authentication
crawler.auth.key("apikey", name="X-API-Key")

# JWT authentication
crawler.auth.jwt("token")
```

### Stream Group
```python
# Download a file in chunks
async with crawler.stream("https://example.com/file.zip", path="download.zip") as stream:
    async for chunk in stream.chunks(size=8192):
        print(f"Downloaded {stream.done}%")

# Upload a file in chunks
async with crawler.stream.upload("https://example.com/upload", path="file.pdf") as stream:
    async for chunk in stream.chunks():
        print(f"Uploaded {stream.done}%")
        
# Stream large API responses
async with crawler.stream("https://api.example.com/large-dataset") as stream:
    async for chunk in stream.chunks():
        # Process each chunk as JSON
        items = json.loads(chunk)
        for item in items:
            process(item)
```

## License
CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
