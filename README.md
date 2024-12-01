# CrawlPy: Lightweight Web Crawling in Python

CrawlPy is the perfect Python library for easy and efficient web crawling. It's designed to be simple yet powerful, making it easy to fetch and process web content for a variety of tasks.

## Why Choose CrawlPy?

- **Minimalist Design**: Lightweight and uncluttered, focusing on the essentials of web crawling without unnecessary complexity.
- **Effortless API**: Intuitive API for making HTTP requests and processing responses easily.
- **Flexibility**: Adaptable for various needs, whether you're scraping data, monitoring websites, or conducting research.
- **Customization**: Full control over your requests with support for cookies and custom headers.

## Getting Started

You can start web crawling with CrawlPy in just a few simple steps:

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
    
    # Create a CrawlPy object
    crawler = CrawlPy()
    url = "http://example.com"
    
    # Get the event loop
    loop = asyncio.get_event_loop()
    
    html = loop.run_until_complete(crawler.get(url))
    print(html)
    ```

3. **Run Your Crawler**

    Run your crawler script:

    ```bash
    python crawler.py
    ```

    And watch CrawlPy fetch web content effortlessly!

## License

CrawlPy is licensed under the CC0-1.0 License. For details, see [LICENSE](LICENSE).
