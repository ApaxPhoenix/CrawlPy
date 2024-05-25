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

    Create a Python file for your crawler, like `crawler.py`, and let your imagination run wild with CrawlPy:

    ```python
    import asyncio
    from crawlpy import CrawlPy
    
    # Create an event loop
    loop = asyncio.get_event_loop()
    
    # Create a CrawlPy instance
    crawler = CrawlPy()
    
    # Directly run coroutines in the loop
    response = loop.run_until_complete(crawler.get('https://example.com'))
    print("Status Code:", response.status)
    
    content = response.read().decode('utf-8')
    print("Response Content:", content)
    
    # Close the crawler
    loop.run_until_complete(crawler.close())
    ```

3. **Run Your Crawler**

    Execute your crawler script:

    ```bash
    python crawler.py
    ```

    Watch as CrawlPy fetches web content effortlessly!

## Want to Contribute?

CrawlPy is an open-source project driven by the community. Join us in making web crawling simpler and more accessible for everyone. Check out our [contribution guidelines](CONTRIBUTING.md) to get started.

## Need Help?

Got questions or need assistance with CrawlPy? Head over to our [GitHub repository](https://github.com/crawlpy/crawlpy) or join our [community chat](https://discord.gg/jU5tpK2jqf) for support.

## License

CrawlPy is licensed under the GPL-3.0 License. For details, see [LICENSE](LICENSE).
