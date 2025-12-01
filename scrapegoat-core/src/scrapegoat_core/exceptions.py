"""
"""

class ScrapegoatCoreException(Exception):
    """
    Base exception class for Scrapegoat Core-related errors.
    """
    pass

class ScrapegoatPlaywrightException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat Playwright-related errors.
    """
    pass

class ScrapegoatIOException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat file reading-related errors.
    """
    pass

class ScrapegoatParseException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat HTML parsing-related errors.
    """
    pass

class ScrapegoatMissingFieldException(ScrapegoatCoreException):
    """
    Exception class for missing tag errors in Scrapegoat.
    """
    pass

class ScrapegoatFetchException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat fetching-related errors.
    """
    pass

class GoatspeakInterpreterException(ScrapegoatCoreException):
    """
    Exception class for Scrapegoat Goatspeak interpreter-related errors.
    """
    pass