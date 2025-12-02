"""
"""

from abc import ABC, abstractmethod
import os
import json
import csv
import requests

from .conditions import InCondition


class Command(ABC):
    """
    The base Command class for defining various commands used in goatspeak.

    Important:
        This is an abstract base class and should not be instantiated directly.
        Subclasses must implement the execute method to define specific command behaviors.
    """
    @abstractmethod
    def __init__(self, action: str):
        """
        Initializes the Command.

        Args:
            action (str): The action type of the command.
        """
        self.action = action

    @abstractmethod
    def execute(self, root: "HTMLNode") -> any: # type: ignore
        """
        Executes the command.
        
        Args:
            root: The root HTMLNode on which to execute the command.
        """
        pass


class GrazeCommand(Command):
    """
    The GrazeCommand class for defining commands to parse HTMLNodes from tree structures.
    
    Info:
        A GrazeCommand can either be a select, which rebases the root node for subsequent commands, or a scrape, which extracts the entire set of matching nodes.
        GrazeCommands can also include conditions to filter the nodes they operate on.
        All conditions must be met for a node to be selected by a GrazeCommand.
    """
    def __init__(self, action: str, count: int, element: str, conditions: list["Condition"]=None, flags: list=None): # type: ignore
        """
        Initializes the GrazeCommand.

        Args:
            action (str): The action type of the command ("select" or "scrape").
            count (int): The maximum number of elements to return. Use 0 for no limit.
            element (str): The HTML tag to target.
            conditions (list, optional): A list of Condition objects to filter the nodes. Defaults to None.
            flags (list, optional): A list of flags to modify command behavior. Defaults to None.
        """
        super().__init__(action=action)
        self.count = count
        self.element = element
        self.conditions = conditions or []
        self.flags = flags or []

        for cond in self.conditions:
            if isinstance(cond, InCondition) and cond.target == "POSITION" and cond.query_tag is None:
                cond.query_tag = self.element
    
    def _evaluate(self, node, root) -> bool:
        """
        """
        if node.tag_type != self.element:
            return False
        return all(cond.evaluate(node, root) for cond in self.conditions)
    
    def execute(self, root: "HTMLNode") -> list["HTMLNode"]: # type: ignore
        """
        Executes the GrazeCommand on the given root HTMLNode.

        Args:
            root (HTMLNode): The root HTMLNode from which to execute the command.

        Returns:
            list: A list of HTMLNode objects that match the command criteria.
        """
        results = []
        for node in root.preorder_traversal():
            if self._evaluate(node, root):
                results.append(node)
                if self.count > 0 and len(results) >= self.count:
                    break
        return results
    

class ChurnCommand(Command):
    """
    The ChurnCommand class for defining how an HTMLNode is to be represented after being scraped.
    
    Info:
        This command is used to extract specific data from the scraped nodes.
        To do this, the ChurnCommand takes in a list of fields to extract, as well as flags to ignore children or grandchildren nodes during extraction.
        If scraping a table, the table flag can be set to True to represent the table as it would appear on a webpage.
    """
    def __init__(self, fields: list[str] = None, ignore_children: bool = False, ignore_grandchildren: bool = False, table: bool = False):
        """
        Initializes the ChurnCommand.

        Args:
            fields (list, optional): A list of fields to extract from the node. Defaults to None.
            ignore_children (bool, optional): Whether to ignore child nodes during extraction. Defaults to False.
            ignore_grandchildren (bool, optional): Whether to ignore grandchild nodes during extraction. Defaults to False.
            table (bool, optional): Whether to represent the node as a table. Defaults to False.
        """
        super().__init__(action="extract")
        self.fields = fields
        self.ignore_children = ignore_children
        self.ignore_grandchildren = ignore_grandchildren
        self.table = table
    
    def execute(self, node: "HTMLNode") -> None: # type: ignore
        """
        Executes the ChurnCommand on the given HTMLNode.

        Args:
            node (HTMLNode): The HTMLNode to extract data from.
        """
        node.set_extract_instructions(self.fields, self.ignore_children, self.ignore_grandchildren, self.table)
        

class DeliverCommand(Command):
    """
    The DeliverCommand class for defining how scraped HTMLNode results are to be exported to a file.
    
    Info:
        The DeliverCommand currently only supports exports to CSV and JSON file formats.
        By default, if no filepath is provided, the file will be saved in the current working directory.
        If no filename is provided, a default name of "output" with the appropriate file extension will be used.

    Attributes:
        VALID_TYPES (set): A set of valid file types for delivery ("csv", "json").
    """
    VALID_TYPES = {"csv", "json"}

    def __init__(self, file_type: str, filepath: str = None, filename: str = None):
        """
        Initializes the DeliverCommand.

        Args:
            file_type (str): The type of file to deliver the results to ("csv" or "json").
            filepath (str, optional): The directory path where the file will be saved. Defaults to the current working directory.
            filename (str, optional): The name of the file. If not provided, a default name will be used. Defaults to None.
        """
        super().__init__(action="output")
        self.file_type = file_type
        self.filepath = filepath or os.getcwd()
        base, ext = os.path.splitext(filename or f"output.{file_type}")
        self.filename = base + (ext if ext else f".{file_type}")
        self.full_path = os.path.join(self.filepath, self.filename)

    def execute(self, nodes: list["HTMLNode"]) -> str: # type: ignore
        """
        Executes the DeliverCommand to save the scraped HTMLNode results to a file.

        Args:
            nodes (list): A list of scraped HTMLNode results.

        Returns:
            str: The full path to the saved file.
        """
        os.makedirs(self.filepath, exist_ok=True)

        if self.file_type.lower() == "csv":
            self._to_csv(nodes)
        elif self.file_type.lower() == "json":
            self._to_json(nodes)
        return self.full_path
        
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        """
        items = {}
        for k, v in d.items():
            new_key = f"{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    def _collect_nodes(self, node_dict: dict, all_nodes: list) -> dict:
        """
        """
        if type(node_dict) is not dict:
            for item in node_dict:
                self._collect_nodes(item, all_nodes)
            return
        node_copy = node_dict.copy()

        had_children = "children" in node_copy
        children = node_copy.pop("children", [])
        child_ids = []

        for child in children:
            child_flat = self._collect_nodes(child, all_nodes)
            child_ids.append(child_flat.get("id"))
        
        flattened = self._flatten_dict(node_copy)
        if had_children:
            if child_ids == [] or all(cid is None for cid in child_ids):
                flattened["children"] = None
            else:
                flattened["children"] = child_ids

        all_nodes.append(flattened)
        return node_copy

    def _to_csv(self, nodes: list) -> None:
        """
        """
        all_nodes = []
        for node in nodes:
            # check if node is a list:
            node_dict = node.to_dict()
            self._collect_nodes(node_dict, all_nodes)

        fieldnames = set()
        for nd in all_nodes:
            fieldnames.update(nd.keys())
        fieldnames = list(fieldnames)

        os.makedirs(self.filepath, exist_ok=True)
        with open(self.full_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for nd in all_nodes:
                writer.writerow(nd)

    def _to_json(self, nodes: list) -> None:
        """
        """
        nodes_as_dicts = [node.to_dict() for node in nodes]
        with open(self.full_path, mode='w', encoding='utf-8') as jsonfile:
            json.dump(nodes_as_dicts, jsonfile, indent=4)


class FetchCommand(Command):
    """
    The FetchCommand class executes the getter function from its attributes to retrieve HTML content from a specified URL.
    
    Info:
        By default, the FetchCommand uses the requests.get method, but this can be overridden by providing a custom getter function.
        Through the Sheepdog class, the getter can be easily overwritten, either by passing in a custom function or by extending the Sheepdog class itself, with a new implementation of the getter method.
    """
    def __init__(self, url: str, **kwargs):
        """
        Initializes the FetchCommand.

        Args:
            url (str): The URL to fetch HTML content from.
            **kwargs: Additional keyword arguments to pass to the getter function.
        """
        super().__init__(action="visit")
        self.getter = requests.get
        self.url = url
        self.kwargs = kwargs
    
    def execute(self) -> str:
        """
        Executes the FetchCommand to retrieve HTML content from the specified URL.

        Returns:
            str: The fetched HTML content.
        """
        return self.getter(self.url, **self.kwargs)
    
    def set_getter(self, getter: callable) -> None:
        """
        Sets a custom getter function for fetching HTML content.

        Args:
            getter (callable): A custom function that takes a URL and returns HTML content.
        """
        self.getter = getter
    
    def __eq__(self, other):
        """
        """
        return isinstance(other, FetchCommand) and self.url == other.url


def main():
    """
    """
    pass


if __name__ == "__main__":
    main()
