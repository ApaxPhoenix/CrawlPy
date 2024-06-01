import re


class Retriever:
    """Class for retrieving elements from HTML content."""

    @staticmethod
    def get_urls(html_content):
        """
        Retrieve all URLs from the HTML content.

        Args:
            html_content (str): The HTML content.

        Returns:
            list: A list of URLs found in the HTML content.
        """
        pattern = r'href="([^"]+)"'
        matches = re.findall(pattern, html_content)
        return matches

    @staticmethod
    def get_fragments(html_content):
        """
        Retrieve all URL fragments from the HTML content.

        Args:
            html_content (str): The HTML content.

        Returns:
            list: A list of URL fragments found in the HTML content.
        """
        fragment_pattern = r'href="[^#]+#([^"]+)"'
        fragment_matches = re.findall(fragment_pattern, html_content)
        return fragment_matches

    @staticmethod
    def get_query_params(url):
        """
        Extract query parameters from the given URL.

        Args:
            url (str): The URL to extract query parameters from.

        Returns:
            dict: A dictionary containing the extracted query parameters.
        """
        query_params = {}
        # Find the query string in the URL
        query_string_match = re.search(r'\?(.*)', url)
        if query_string_match:
            query_string = query_string_match.group(1)
            # Split the query string into key-value pairs
            params = query_string.split('&')
            for param in params:
                # Split each key-value pair into key and value
                key_value = param.split('=')
                if len(key_value) == 2:
                    key, value = key_value
                    query_params[key] = value
        return query_params


class Selector:
    """Class for selecting elements from HTML content."""

    @staticmethod
    def get_elements_by_tag(html_content, tag_name):
        """
        Retrieve elements from HTML content by tag name using regular expressions.

        Args:
            html_content (str): The HTML content.
            tag_name (str): The tag name to search for (e.g., 'a', 'p', 'body').

        Returns:
            list: A list of strings containing the content of elements matching the given tag name.
        """
        pattern = r"<{0}.*?>(.*?)<\/{0}>".format(tag_name)
        matches = re.findall(pattern, html_content, re.DOTALL)
        return matches

    @staticmethod
    def get_elements_by_class(html_content, class_name):
        """
        Retrieve elements from HTML content by CSS class name using regular expressions.

        Args:
            html_content (str): The HTML content.
            class_name (str): The CSS class name to search for.

        Returns:
            list: A list of strings containing the content of elements with the given CSS class.
        """
        pattern = r'class="{}"[^>]*?>(.*?)<\/[^>]+>'.format(class_name)
        matches = re.findall(pattern, html_content, re.DOTALL)
        return matches

    @staticmethod
    def get_elements_by_id(html_content, element_id):
        """
        Retrieve elements from HTML content by element ID using regular expressions.

        Args:
            html_content (str): The HTML content.
            element_id (str): The ID of the element to search for.

        Returns:
            list: A list of strings containing the content of elements with the given ID.
        """
        pattern = r'id="{}"[^>]*?>(.*?)<\/[^>]+>'.format(element_id)
        matches = re.findall(pattern, html_content, re.DOTALL)
        return matches

    @staticmethod
    def get_elements_by_css_selector(html_content, css_selector):
        """
        Retrieve elements from HTML content by CSS selector using regular expressions.

        Args:
            html_content (str): The HTML content.
            css_selector (str): The CSS selector to search for.

        Returns:
            list: A list of strings containing the content of elements matching the CSS selector.
        """
        selector_parts = css_selector.split()
        pattern = r"[\s>]+".join([r"({})".format(part) for part in selector_parts])
        pattern = pattern.replace("#", r"id=\"([^\"]*)\"").replace(".", r'class=\"([^\"]*)\"')
        pattern = r"<{}.*?>(.*?)<\/{}>".format(pattern, selector_parts[-1])
        matches = re.findall(pattern, html_content, re.DOTALL)
        return matches
