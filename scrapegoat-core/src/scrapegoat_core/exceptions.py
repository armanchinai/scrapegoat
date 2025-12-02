"""
"""

class ScrapegoatCoreException(Exception):
    """
    Base exception class for Scrapegoat Core-related errors.

    Note:
        This class serves as the base for all custom exceptions in the Scrapegoat Core module. All other exception classes should inherit from this class to ensure consistency and proper error handling within the Scrapegoat Core module.
    """
    pass

class ScrapegoatPlaywrightException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat Playwright-related errors. 

    Note:
        These exceptions can only be encountered when using HeadlessSheepdog or another implementation of the Sheepdog class that relies on Playwright for browser automation.

    Example:
        ```python
        HeadlessSheepdog.fetch("https://example.com")
            ScrapegoatPlaywrightException: Playwright is not installed. Please install it with 'pip install playwright'
        ```

    Example:
        ```python
        HeadlessSheepdog.fetch("https://example.com")
            ScrapegoatPlaywrightException: Playwright browser executables are not installed. Please run 'playwright install' to install them.
        ```
    """
    pass

class ScrapegoatIOException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat I/O-related errors.

    Example:
        ```python
        HeadlessSheepdog.fetch("file:///non_existent_file.html")
            ScrapegoatIOException: File not found: /non_existent_file.html
        ```
    """
    pass

class ScrapegoatParseException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat HTML parsing-related errors.
    
    Note:
        Raised when there is an issue parsing HTML content into a tree of HTMLNodes.

    Example:
        ```python
        html_content = "SomeMalformedHTMLString"
        Gardener.grow_tree(html_content)
            ScrapegoatParseException: Failed to parse HTML content: Unexpected end tag
        ```
    """
    pass

class ScrapegoatMissingFieldException(ScrapegoatCoreException):
    """
    Exception class for missing tag errors in Scrapegoat.
    
    Note:
        Raised when a command required extra information that was not provided in the goatspeak query. This can only happen with conditions, and needs to be forcefully done. May occur when manually constructing commands.
    """
    pass

class ScrapegoatFetchException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat fetching-related errors.

    Example:
        ```python
        HeadlessSheepdog.fetch("https://nonexistentwebsite.example")
            ScrapegoatFetchException: Failed to fetch URL 'https://nonexistentwebsite.example': DNS resolution failed
        ```
    """
    pass

class GoatspeakInterpreterException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat Goatspeak interpreter-related errors.
    
    Note:
        Raised when there is an error interpreting or executing Goatspeak commands. This could be due to syntax, semantic, or runtime issues within the Goatspeak language.
    
    Example:
        ```python
        Shepherd.herd(""VISIT 'https://example.com';SCRAPE p")
            GoatspeakInterpreterException: Missing semicolon at the end of the command.
        ```

    Example:
        ```python
        Shepherd.herd("VISIT 'https://example.com';SCRAPE p IN POSITION;")
            GoatspeakInterpreterException: Error parsing command starting with token Token(type=TokenType.ACTION, value='scrape'): Expected '=' after IN POSITION at Token(type=TokenType.SEMICOLON, value=';')
        ```
    """
    pass