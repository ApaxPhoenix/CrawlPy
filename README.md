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
- **JavaScript Rendering**: Execute JavaScript and scrape dynamically loaded content.
- **Automatic Throttling**: Prevent IP bans by managing request rates automatically.
- **Data Extraction**: Extract structured data using built-in parsers and schema validation.

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
CrawlPy organizes related functionality into logical groups for easy access.

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
crawler.proxy.for("http://example.com", "http://proxy:port")

# Use proxy rotation
crawler.proxy.rotate(["http://proxy1:port", "http://proxy2:port", "http://proxy3:port"])
```

### JavaScript Rendering
```python
# Enable JavaScript execution
await crawler.render.enable()

# Set a timeout for JavaScript rendering
await crawler.render.timeout("10s")

# Capture a screenshot of a rendered page
await crawler.render.screenshot("https://example.com", output="screenshot.png")
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

## License
CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.

