# CrawlPy: Lightweight Web Crawling in Python

CrawlPy is your go-to Python library for effortless web crawling. Designed to be simple yet powerful, it empowers you to efficiently fetch and process web content for various tasks.

## What Makes CrawlPy Special?

- **Minimalist Design**: Lightweight and uncluttered, focusing on the essentials of web crawling without unnecessary complexity.
- **Effortless API**: Intuitive API for making HTTP requests and processing responses easily.
- **Flexibility**: Adapts to various needs, whether you're scraping data, monitoring websites, or conducting research.
- **Customization**: Full control over your requests with support for cookies and custom headers.

## Getting Started

Dive into web crawling with CrawlPy in just a few simple steps:

1. **Installation**

    Install CrawlPy via pip:

    ```bash
    pip install crawlpy
    ```

2. **Write Your Crawler**

    Create a Python file for your crawler, like `crawler.py`:

    ```python
    import asyncio
    from crawlpy import CrawlPy
    
    # Instantiate the CrawlPy object
    crawler = CrawlPy()
    url = "http://example.com"
    
    # Get the event loop
    loop = asyncio.get_event_loop()
    
    # Define the asynchronous code block directly
    try:
        # Fetch the HTML content asynchronously
        html_content = loop.run_until_complete(crawler.get(url))
        print(html_content)
    finally:
        # Close the crawler session
        loop.run_until_complete(crawler.close())
    
    # Close the event loop
    loop.close()
    ```

3. **Run Your Crawler**

    Execute your crawler script:

    ```bash
    python crawler.py
    ```

    Watch as CrawlPy fetches web content effortlessly!

## License

CrawlPy is licensed under the MIT License. For details, see [LICENSE](LICENSE).
