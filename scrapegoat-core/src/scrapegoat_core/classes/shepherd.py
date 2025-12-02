"""
"""

import os

from .gardener import Gardener
from .goat import Goat
from .interpreter import Interpreter
from .milkmaid import Milkmaid
from .milkman import Milkman
from .sheepdog import Sheepdog


class Shepherd:
    """
    The master class that orchestrates the query to data scraping process. This class delegates its job to subclasses like the Gardener, Sheepdog, Goat, Milkmaid, and Milkman. All subclasses can be extended and passed into the Shepherd constructor to customize its behavior.

    Users should primarily interact with this class to perform webscraping with Scrapegoat. It exposes methods to execute goatspeak queries from strings or files, starting from URLs, raw HTML, or existing HTMLNode trees.
    """
    def __init__(self, gardener:Gardener=None, sheepdog:Sheepdog=None, goat:Goat=None, milkmaid:Milkmaid=None, milkman:Milkman=None):
        """
        The Shepherd class constructor.

        Args:
            gardener (Gardener, optional): An instance of the Gardener class. Defaults to a new Gardener instance.
            sheepdog (Sheepdog, optional): An instance of the Sheepdog class. Defaults to a new Sheepdog instance.
            goat (Goat, optional): An instance of the Goat class. Defaults to a new Goat instance.
            milkmaid (Milkmaid, optional): An instance of the Milkmaid class. Defaults to a new Milkmaid instance.
            milkman (Milkman, optional): An instance of the Milkman class. Defaults to a new Milkman instance.
        """
        self.gardener = gardener if gardener else Gardener()
        self.interpreter = Interpreter()
        self.sheepdog = sheepdog if sheepdog else Sheepdog()
        self.goat = goat if goat else Goat()
        self.milkmaid = milkmaid if milkmaid else Milkmaid()
        self.milkman = milkman if milkman else Milkman()
    
    def herd(self, query: str) -> list["HTMLNode"]: # type: ignore
        """
        Executes the full data scraping process based on the provided goatspeak query. Accepts either a goatspeak string or a file path to a goatspeak file.

        Args:
            query (str): A goatspeak string or a file path to a goatspeak file.
        
        Returns:
            list: A list of scraped HTMLNode results.

        Usage:
            ```python
            results = Shepherd().herd("VISIT 'http://example.com'; SCRAPE 1 p;")
            ```
        """
        goatspeak = self._convert_query_to_goatspeak(query)

        results = []

        for block in goatspeak:
            html = self.sheepdog.fetch(block.fetch_command)
            root = self.gardener.grow_tree(html)
            self._query_list_handler(block.query_list, root, results)

        return list(dict.fromkeys(results))
    
    def _convert_query_to_goatspeak(self, query: str) -> None:
        """
        """
        if os.path.isfile(query):
            try:
                return self.interpreter.interpret(self.milkman.receive(query))
            except Exception as e:
                raise e
        try:
            return self.interpreter.interpret(query)
        except Exception as e:
            raise e                

    def _query_list_handler(self, query_list: str, root, results) -> list:
        """
        """
        for query in query_list:
            query_results = (self.goat.feast(root, query.graze_commands))
            if query.churn_command:
                self.milkmaid.churn(query_results, query.churn_command)

            results.extend(query_results)

            if query.deliver_command:
                self.milkman.deliver(results, query.deliver_command)
                results.clear()
        return
        
    def _local_herd(self, query: str, root) -> list:
        """
        """
        goatspeak = self._convert_query_to_goatspeak(query)

        results = []

        for block in goatspeak:
            self._query_list_handler(block.query_list, root, results)
                
        return list(dict.fromkeys(results))
    
    def herd_from_node(self, query: str, root: "HTMLNode") -> list["HTMLNode"]: # type: ignore
        """
        Executes a goatspeak query starting from a given HTMLNode.

        Args:
            query (str): A goatspeak string or a file path to a goatspeak file.
            root (HTMLNode): The starting HTMLNode from which to execute the query.

        Returns:
            list: A list of scraped HTMLNode results.

        Usage:
            ```python
            root_node = HTMLNode(...)  # Assume this is an initialized HTMLNode
            results = Shepherd().herd_from_node("SCRAPE 1 p;", root_node)
            ```
        """
        return self._local_herd(query, root=root)
    
    def herd_from_html(self, query: str, html: str) -> list["HTMLNode"]: # type: ignore
        """
        Grows an HTMLNode tree from raw HTML and executes a goatspeak query on it.

        Args:
            query (str): A goatspeak string or a file path to a goatspeak file.
            html (str): The raw HTML string to be parsed.

        Returns:
            list: A list of scraped HTMLNode results.

        Usage:
            ```python
            html_content = "<html><body><p>Hello, World!</p></body></html>"
            results = Shepherd().herd_from_html("SCRAPE 1 p;", html_content)
            ```
        """
        root = self.gardener.grow_tree(html)
        return self._local_herd(query, root=root)
    
    def herd_from_url(self, query: str, url: str) -> list["HTMLNode"]: # type: ignore
        """
        Fetches HTML from a URL, grows an HTMLNode tree, and executes a goatspeak query on it.

        Args:
            query (str): A goatspeak string or a file path to a goatspeak file.
            url (str): The URL from which to fetch HTML content.

        Returns:
            list: A list of scraped HTMLNode results.

        Usage:
            ```python
            results = Shepherd().herd_from_url("SCRAPE 1 p;", "http://example.com")
            ```
        """
        html = self.sheepdog.fetch(url)
        root = self.gardener.grow_tree(html)
        return self._local_herd(query, root=root)

def main():
    """
    """
    pass


if __name__ == "__main__":
    main()
