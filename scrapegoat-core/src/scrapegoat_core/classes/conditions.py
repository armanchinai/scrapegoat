"""
"""

from abc import ABC, abstractmethod

from scrapegoat_core.exceptions import ScrapegoatMissingFieldException


class Condition(ABC):
    """
    The base Condition class for defining conditions used in scrape and select commands.
    """
    def __init__(self, negated: bool = False):
        """
        Initializes the Condition.

        Args:
            negated (bool): Whether the condition is negated. Defaults to False.
        """
        self.negated = negated

    @abstractmethod
    def matches(self, node: "HTMLNode", root: "HTMLNode") -> bool: # type: ignore
        """
        Determines if the condition matches the given node. Must be implemented by subclasses.

        Args:
            node (HTMLNode): The HTMLNode to evaluate the condition against.
            root (HTMLNode): The root HTMLNode of the tree.

        Returns:
            bool: True if the condition matches, False otherwise.
        """
        pass

    def evaluate(self, node: "HTMLNode", root: "HTMLNode") -> bool: # type: ignore
        """
        Evaluates the condition against the given node, taking into account negation.

        Args:
            node (HTMLNode): The HTMLNode to evaluate the condition against.
            root (HTMLNode): The root HTMLNode of the tree.

        Returns:
            bool: The result of the condition evaluation, considering negation.
        """
        result = self.matches(node, root)
        return not result if self.negated else result


class IfCondition(Condition):
    """
    The IfCondition class for defining attribute-based conditions used in scrape and select commands. Supports both exact and like matching. Returns true if the specified attribute matches the given value or if the specified attribute is present when no value is provided.
    """
    def __init__(self, key: str, value: str, negated: bool = False, query_tag: str = None, like: bool = False):
        """
        Initializes the IfCondition.

        Args:
            key (str): The attribute key to check. Prefix with "@" for HTML attributes.
            value (str): The attribute value to match.
            negated (bool): Whether the condition is negated. Defaults to False.
            query_tag (str): The HTML tag to which the condition applies. If None, applies to all tags. Defaults to None.
            like (bool): Whether to use like matching (True) or exact matching (False). Defaults to False.
        """
        super().__init__(negated)
        self.key = key
        self.value = value
        self.query_tag = query_tag
        self.like = like

    def matches(self, node: "HTMLNode", _:"HTMLNode"=None) -> bool: # type: ignore
        """
        Determines if the condition matches the given node.

        Args:
            node (HTMLNode): The HTMLNode to evaluate the condition against.
            _ (HTMLNode): The root HTMLNode of the tree (not used in this condition). Defaults to None.

        Returns:
            bool: True if the condition matches, False otherwise.
        """
        if self.query_tag is None:
            raise ScrapegoatMissingFieldException("query_tag must be specified for IfCondition")
        if self.like:
            return self._like_match(node)
        else:
            return self._exact_match(node)
    
    def _like_match(self, node) -> bool:
        """
        """
        if self.key[0] == "@":
            return node.like_html_attribute(self.key, self.value) and node.tag_type == self.query_tag
        else:
            return node.like_attribute(self.key, self.value) and node.tag_type == self.query_tag
        
    def _exact_match(self, node) -> bool:
        """
        """
        if self.key[0] == "@":
            return node.has_html_attribute(self.key, self.value) and node.tag_type == self.query_tag
        else:
            return node.has_attribute(self.key, self.value) and node.tag_type == self.query_tag

    def __str__(self):
        """
        """
        return f"IfCondition(key={self.key}, value={self.value}, negated={self.negated}, query_tag={self.query_tag})"
    

class InCondition(Condition):
    """
    The InCondition class for defining hierarchical conditions used in scrape and select commands. Supports checking if a node is a descendant of a target tag or if it is at a specific position relative to the entire tree with respect to elements of the same tag.
    """
    def __init__(self, target: str, value=None, negated: bool = False, query_tag: str = None):
        """
        Initializes the InCondition.

        Args:
            target (str): The target tag to check against or "POSITION" for position-based checks
            value (int): The position value to match when target is "POSITION". Defaults to None.
            negated (bool): Whether the condition is negated. Defaults to False.
            query_tag (str): The HTML tag to which the position condition applies. Required if target is "POSITION". Defaults to None.
        """
        super().__init__(negated)
        self.target = target
        self.value = value
        self.query_tag = query_tag

    def matches(self, node: "HTMLNode", root: "HTMLNode") -> bool: # type: ignore
        """
        Determines if the condition matches the given node.

        Args:
            node (HTMLNode): The HTMLNode to evaluate the condition against.
            root (HTMLNode): The root HTMLNode of the tree.

        Returns:
            bool: True if the condition matches, False otherwise.
        """
        if self.target == "POSITION":
            if not root:
                raise ScrapegoatMissingFieldException("root is required for POSITION condition")
            if not self.query_tag:
                raise ScrapegoatMissingFieldException("query_tag is required for POSITION condition")
            position = 1
            for n in root.preorder_traversal():
                if n.tag_type == self.query_tag:
                    if node == n:
                        return position == self.value
                    position += 1
            return False
        else:
            return node.is_descendant_of(self.target)
        
    def __str__(self):
        """
        """
        return f"InCondition(target={self.target}, value={self.value}, negated={self.negated}, query_tag={self.query_tag})"