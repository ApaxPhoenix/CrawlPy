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

## License

CrawlPy is open source and available under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.