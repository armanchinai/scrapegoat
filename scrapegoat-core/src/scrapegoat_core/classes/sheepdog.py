"""
"""

from typing import Union
import requests

from .command import FetchCommand
from scrapegoat_core.exceptions import ScrapegoatPlaywrightException, ScrapegoatFetchException


class Sheepdog:
    """
    The Sheepdog class is responsible for fetching HTML content from the web. By default, it uses the requests library to perform HTTP GET requests, and has its own default headers to mimic a standard web browser.

    Hint:
        This is one of Scrapegoat's highly extendable classes. You can extend this class to implement custom fetching behavior, such as using headless browsers or handling specific authentication mechanisms. Alternatively, a custom getter function can be passed into the constructor to override the default fetching behavior.

    Attributes:
        DEFAULT_HEADERS (dict): A dictionary of default HTTP headers to use for requests.
    """
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Scrapegoat)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
    }

    def __init__(self, getter: callable=None):
        """
        Initializes an instance of the Sheepdog class. Accepts an optional custom getter function. 

        Args:
            getter (callable, optional): A custom function to fetch HTML content. Defaults to None, which uses the default getter method.
        """
        self.getter = getter or self.getter

    def fetch(self, fetch_command: Union[str, FetchCommand]) -> str:
        """
        Fetches HTML content using the provided fetch command or URL string.

        Args:
            fetch_command (Union[str, FetchCommand]): A FetchCommand object or a URL string to fetch HTML content from.

        Returns:
            str: The fetched HTML content.

        Usage:
            ```python
            html_content = Sheepdog().fetch("http://example.com")
            ```
        """
        if not isinstance(fetch_command, FetchCommand):
            fetch_command = FetchCommand(fetch_command)
        fetch_command.set_getter(self.getter)
        return fetch_command.execute()
    
    def getter(self, url: str, **kwargs) -> str:
        """
        Fetches HTML content from the given URL using the requests library.

        Args:
            url (str): The URL to fetch HTML content from.
            **kwargs: Additional keyword arguments to pass to the requests.get() method.

        Returns:
            str: The fetched HTML content.

        Warning:
            Raises ScrapegoatFetchException if the fetch operation fails.
        """
        try:
            headers = kwargs.pop('headers', self.DEFAULT_HEADERS)
            response = requests.get(url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise ScrapegoatFetchException(f"Failed to fetch URL {url}: {str(e)}")


class HeadlessSheepdog(Sheepdog):
    """
    The HeadlessSheepdog class extends the Sheepdog class to fetch HTML content using a headless browser via the Playwright library. This class uses a very simple implementation that will wait for the DOM content to load before returning the HTML.
    """
    def __init__(self, getter=None):
        """
        Initializes an instance of the HeadlessSheepdog class. Accepts an optional custom getter function.

        Args:
            getter (callable, optional): A custom function to fetch HTML content. Defaults to None, which uses the default Playwright-based getter method.
        """
        super().__init__(getter)

    def getter(self, url: str, **kwargs) -> str:
        """
        Fetches HTML content from the given URL using a headless browser via Playwright.

        Args:
            url (str): The URL to fetch HTML content from.
            **kwargs: Additional keyword arguments (not used in this implementation).

        Returns:
            str: The fetched HTML content.

        Usage:
            ```python
            html_content = HeadlessSheepdog().fetch("http://example.com")
            ```

        Warning:
            The Playwright library must be installed separately. If it is not installed, a ScrapegoatPlaywrightException will be raised when attempting to fetch content. To install Playwright, run 'pip install playwright' in your terminal.

        Warning:
            A headless browser must be installed on the local device. If one is not installed, a ScrapegoatPlaywrightException will be raised when attempting to fetch content. To install the executables, run 'playwright install' in your terminal.
        
        Warning:
            Raises ScrapegoatFetchException if the fetch operation fails.
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ScrapegoatPlaywrightException("Playwright is not installed. Please install it with 'pip install playwright'")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                return page.content()
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                raise ScrapegoatPlaywrightException("Playwright browser executables are not installed. Please run 'playwright install' to install them.")
            else:
                raise ScrapegoatFetchException(f"Failed to fetch URL {url} using Playwright: {str(e)}")


def main():
    """
    """
    pass


if __name__ == "__main__":
    main()
