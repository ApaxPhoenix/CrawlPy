# CrawlPy: Lightweight Web Crawling in Python

CrawlPy is a Python library designed for easy and efficient web crawling. Whether you are scraping data, monitoring websites, or conducting research, CrawlPy's lightweight and intuitive design makes web crawling a breeze.

## Features

- **Minimalist Design**: Focuses on the core functionality of web crawling without unnecessary complexity.
- **Effortless API**: Intuitive and user-friendly API for making HTTP requests and processing responses.
- **Flexibility**: Adaptable for a wide range of web crawling needs.
- **Customization**: Complete control over requests with support for cookies, custom headers, and more.

## Getting Started

Follow these simple steps to begin using CrawlPy:

### Installation

Install CrawlPy via pip:

```bash
pip install crawlpy
```

### Writing Your First Crawler

Below is an example of how to use CrawlPy to fetch and process web content:

```python
import asyncio
from crawlpy import CrawlPy, Retriever, Selector

async def main() -> None:
    """
    Main asynchronous function to initialize the CrawlPy client,
    fetch a webpage, and extract specific elements from its content.

    This function demonstrates:
        - Creating a web crawler instance
        - Fetching webpage content asynchronously
        - Extracting and printing specific elements from the HTML

    Returns:
        None: The function outputs the processing results to the console.
    """
    # Create an instance of the CrawlPy client
    crawler = CrawlPy()

    # Specify the URL to fetch
    url = "http://example.com"

    # Fetch the HTML content of the URL asynchronously
    html = await crawler.get(url)

    # Initialize Retriever and Selector instances
    retriever = Retriever(html)
    selector = Selector(html)

    # Extract and print all URLs from the HTML content
    print("URLs:", retriever.urls)

    # Extract and print all URL fragments (e.g., #section)
    print("Fragments:", retriever.fragments)

    # Extract and print all <a> tags (links) from the HTML
    print("Links:", selector.get_elements_by_tag("a"))

    # Extract and print elements with the specified class name
    print("Elements with class 'example':", selector.get_elements_by_classification("example"))

# Entry point of the script
if __name__ == "__main__":
    """
    Run the asynchronous main function in the event loop.

    This ensures the program executes the web crawling logic defined
    in the `main` function.
    """
    asyncio.run(main())
```

## License

CrawlPy is licensed under the [MIT License](LICENSE), making it free for both personal and commercial use.
