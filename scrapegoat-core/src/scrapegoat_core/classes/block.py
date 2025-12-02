"""
"""

class GoatspeakBlock:
    """
    A block of goatspeak commands, including a fetch command and a list of queries to be executed on the fetched HTML.
    
    Info:
        GoatspeakBlocks group together a fetch command with one or more queries that operate on the fetched HTML content.
        Each block represents a complete unit of work in a goatspeak script.
        For example, a GoatspeakBlock may fetch HTML from a URL and then execute several queries to scrape different pieces of data from that HTML.
        Each query in the block can have its own graze, churn, and deliver commands.

        ```python
        print(goatspeak_block.__repr__())
        # Output: GoatspeakBlock(fetch_command=FetchCommand(...), query_list=[Query(...), Query(...)])
        ```

    """
    def __init__(self, fetch_command: "FetchCommand", query_list: list["Query"]): # type: ignore
        """
        Initializes the GoatspeakBlock.

        Args:
            fetch_command (FetchCommand): The command to fetch HTML content.
            query_list (list): A list of Query objects to be executed on the fetched HTML.
        """
        self.fetch_command = fetch_command
        self.query_list = query_list

    def __repr__(self):
        """
        """
        return f"GoatspeakBlock(fetch_command={self.fetch_command}, query_list={self.query_list})"


class Query:
    """
    A query consisting of graze commands to be executed on an HTMLNode tree, along with optional fetch, churn, and deliver commands to control the data flow and representation.

    Info:
        Queries encapsulate the instructions for scraping data from HTML content.
        Each Query includes graze commands to select and scrape data, and may also include fetch commands to retrieve HTML, churn commands to extract data, and deliver commands to output results.
        This structure allows for flexible and modular scraping operations within a goatspeak script.

        ```python
        print(query.__repr__())
        # Output: Query(graze_commands=GrazeCommand(...), fetch_command=FetchCommand(...), churn_command=ChurnCommand(...), deliver_command=DeliverCommand(...))
        ```
    """
    def __init__(self, graze_commands: "GrazeCommand", fetch_command: "FetchCommand"=None, churn_command:"ChurnCommand"=None, deliver_command:"DeliverCommand"=None): # type: ignore
        """
        Initializes the Query.

        Args:
            graze_commands (GrazeCommand): The graze commands to be executed.
            fetch_command (FetchCommand): The command to fetch HTML content. Defaults to None.
            churn_command (ChurnCommand): The command to extract data from scraped nodes. Defaults to None.
            deliver_command (DeliverCommand): The command to deliver the results. Defaults to None.
        """
        self.fetch_command = fetch_command
        self.graze_commands = graze_commands
        self.churn_command = churn_command
        self.deliver_command = deliver_command

    def __repr__(self):
        """
        """
        return f"Query(graze_commands={self.graze_commands}, fetch_command={self.fetch_command}, churn_command={self.churn_command}, deliver_command={self.deliver_command})"


def main():
    """
    """
    pass


if __name__ == "__main__":
    """
    """
    main()
