import re
from typing import List


class Retriever:
    """Class for retrieving elements from HTML content."""

    def __init__(self, html: str) -> None:
        """
        Initialize the Retriever with HTML content.

        Args:
            html (str): The HTML content to be processed.
        """
        self.html: str = html

    @property
    def urls(self) -> List[str]:
        """
        Retrieve all URLs from the HTML content.

        Returns:
            list: A list of URLs found in the HTML content.
        """
        # Regular expression to match href values
        pattern = r'href="([^"]+)"'
        # Find all matches for the pattern in the HTML content
        return re.findall(pattern, self.html)

    @property
    def fragments(self) -> List[str]:
        """
        Retrieve all URL fragments from the HTML content.

        Returns:
            list: A list of URL fragments found in the HTML content.
        """
        # Regular expression to match fragments after #
        fragment_pattern = r'href="[^#]+#([^"]+)"'
        # Find all matches for fragments in the HTML content
        return re.findall(fragment_pattern, self.html)


class Selector:
    """Class for selecting elements from HTML content using various filters."""

    def __init__(self, html: str) -> None:
        """
        Initialize the Selector with HTML content.

        Args:
            html (str): The HTML content to be processed.
        """
        self.html: str = html

    def get_elements_by_tag(self, tag: str) -> List[str]:
        """
        Retrieve elements from HTML content by tag name.

        Args:
            tag (str): The tag name to search for (e.g., 'a', 'p').

        Returns:
            List[str]: A list of strings containing the content of elements matching the given tag.
        """
        # Regular expression to match content between the specified tags
        pattern = r"<{0}.*?>(.*?)<\/{0}>".format(tag)
        # Find all elements matching the pattern
        return re.findall(pattern, self.html, re.DOTALL)

    def get_elements_by_classification(self, classification: str) -> List[str]:
        """
        Retrieve elements from HTML content by CSS class name.

        Args:
            classification (str): The CSS class name to search for.

        Returns:
            List[str]: A list of strings containing the content of elements with the given class.
        """
        # Regular expression to match elements with the specified class
        pattern = r'class="{}"[^>]*?>(.*?)<\/[^>]+>'.format(classification)
        # Find all elements matching the pattern
        return re.findall(pattern, self.html, re.DOTALL)

    def get_elements_by_identification(self, identification: str) -> List[str]:
        """
        Retrieve elements from HTML content by element identification (ID).

        Args:
            identification (str): The ID of the element to search for.

        Returns:
            List[str]: A list of strings containing the content of elements with the given ID.
        """
        # Regular expression to match elements with the specified ID
        pattern = r'id="{}"[^>]*?>(.*?)<\/[^>]+>'.format(identification)
        # Find all elements matching the pattern
        return re.findall(pattern, self.html, re.DOTALL)

    def get_elements_by_cascade(self, cascade: str) -> List[str]:
        """
        Retrieve elements from HTML content by CSS cascade selector.

        Args:
            cascade (str): The CSS selector to search for.

        Returns:
            List[str]: A list of strings containing the content of elements matching the CSS selector.
        """
        # Split the cascade into its parts (element, class, id)
        selector_parts = cascade.split()
        # Build a regex pattern to match each part of the cascade selector
        pattern = r"[\s>]+".join([r"({})".format(part) for part in selector_parts])
        # Replace # with regex to match IDs, and . to match classes
        pattern = pattern.replace("#", r"id=\"([^\"]*)\"").replace(".", r'class=\"([^\"]*)\"')
        # Final regex pattern to match the full CSS selector
        pattern = r"<{}.*?>(.*?)<\/{}>".format(pattern, selector_parts[-1])
        # Find all elements matching the pattern
        return re.findall(pattern, self.html, re.DOTALL)
