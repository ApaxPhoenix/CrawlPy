# CrawlPy: Lightweight Web Crawling in Python

CrawlPy is your go-to Python library for effortless web crawling. Designed to be simple yet powerful, it empowers you to efficiently fetch and process web content for various tasks.

## What Makes CrawlPy Special?

- **Minimalist Design**: CrawlPy is lightweight and uncluttered, focusing on the essentials of web crawling without unnecessary complexity.

- **Effortless API**: With CrawlPy's intuitive API, making HTTP requests and processing responses becomes a breeze.

- **Flexibility**: Whether you're scraping data, monitoring websites, or conducting research, CrawlPy adapts to your needs with ease.

- **Customization**: Tailor your crawling experience with support for cookies and custom headers, giving you full control over your requests.

## Getting Started

Dive into web crawling with CrawlPy in just a few simple steps:

1. **Installation**

    Install CrawlPy via pip:

    ```bash
    pip install crawlpy
    ```

2. **Write Your Crawler**

    Create a Python file for your crawler, like `crawler.py`, and let run wildly with CrawlPy:

    ```python
    import asyncio
    from crawlpy.crawlpy import CrawlPy
    
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

CrawlPy is licensed under the GPL-3.0 License. For details, see [LICENSE](LICENSE).
