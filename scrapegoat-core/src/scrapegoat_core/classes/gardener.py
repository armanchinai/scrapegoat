"""
"""

# IMPORTS
from html.parser import HTMLParser
from .node import HTMLNode
from scrapegoat_core.exceptions import ScrapegoatParseException


class Gardener(HTMLParser):
    """
    The Gardener class is responsible for parsing raw HTML into a tree structure composed of HTMLNodes.
    
    Info:
        Under the hood, the Gardener class extends Python's built-in HTMLParser to handle HTML tags, attributes, and text content.
        When an inline tag is encountered, its text content is bubbled up to its parent node to ensure proper representation of text as it would appear on the DOM.

    Attributes:
        VOID_TAGS (set): A set of HTML tags that do not require closing tags.
        AUTO_CLOSE (dict): A mapping of tags to sets of tags that should trigger auto-closing of the current tag.
        INLINE_TAGS (set): A set of HTML tags that are considered inline elements.
    """
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    AUTO_CLOSE = {
        "li": {"li"},
        "p": {"address", "article", "aside", "blockquote", "div", "dl", "fieldset", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "main", "nav", "ol", "p", "pre", "section", "table", "ul"},
        "dt": {"dt", "dd"},
        "dd": {"dt", "dd"},
        "tr": {"tr"},
        "td": {"td", "th"},
        "th": {"td", "th"}
    }
    INLINE_TAGS = {"b", "i", "strong", "em", "u", "small", "mark", "sub", "sup", "a", "span", "img", "br", "code", "s", "q", "cite"}

    def __init__(self):
        """
        Initializes an instance of the Gardener class.
        """
        super().__init__()
        self.tag_counts = {}
        self.root = None
        self.stack = []

    def _auto_close_before(self, new_tag: str):
        """
        """
        while self.stack:
            current_node = next((n for n in reversed(self.stack) if n is not None), None)
            if current_node is None:
                break

            current_tag = current_node.tag_type
            if current_tag in self.AUTO_CLOSE and new_tag in self.AUTO_CLOSE[current_tag]:
                while self.stack:
                    popped = self.stack.pop()
                    if popped is current_node:
                        break
            else:
                break

    def handle_starttag(self, tag_type: str, html_attributes: list[tuple[str, str]]) -> None:
        """
        """
        self._auto_close_before(tag_type)

        node = HTMLNode(raw=self.get_starttag_text(), tag_type=tag_type, html_attributes=dict(html_attributes))

        node.is_inline = tag_type in self.INLINE_TAGS

        self.tag_counts[tag_type] = self.tag_counts.get(tag_type, 0) + 1
        node.set_retrieval_instructions(f"SCRAPE 1 {tag_type} IN POSITION={self.tag_counts[tag_type]};")

        if self.root is None:
            self.root = node
            if tag_type not in self.VOID_TAGS:
                self.stack.append(node)
            return

        parent = next((n for n in reversed(self.stack) if n is not None), self.root)
        parent.children.append(node)
        node.parent = parent

        if tag_type not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag_type: str) -> None:
        """
        """
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i].tag_type == tag_type:
                del self.stack[i:]
                break
        return

    def handle_data(self, data: str) -> None:
        """
        """
        stripped = data.strip()
        if not stripped:
            return

        current = next((n for n in reversed(self.stack) if n is not None), self.root)

        # Add text to current node
        if current.body:
            current.body += " " + stripped
        else:
            current.body = stripped
        current.has_data = True

        # Bubble text up if inline
        if getattr(current, "is_inline", False) and current.parent is not None:
            if current.parent.body:
                current.parent.body += " " + stripped
            else:
                current.parent.body = stripped
            current.parent.has_data = True
    
    def _append_root_tag(self, raw_html: str) -> str:
        """
        """
        html_lower = raw_html.lower()

        if "<html" not in html_lower:
            raw_html = f"<html>{raw_html}</html>"

        if "<body" not in html_lower:
            raw_html = raw_html.replace("<html>", "<html><body>", 1)
            raw_html = raw_html.replace("</html>", "</body></html>", 1)
        return raw_html
    
    def grow_tree(self, raw_html: str) -> HTMLNode:
        """
        Creates an HTMLNode tree from raw HTML input.

        Args:
            raw_html (str): The raw HTML string to be parsed.

        Returns:
            HTMLNode: The root node of the constructed HTMLNode tree.

        Usage:
            ```python
            root_node = Gardener().grow_tree("<html><body><p>Hello, World!</p></body></html>")
            ```

        Warning:
            Raises ScrapegoatParseException if the HTML cannot be parsed.
        """
        self.root = None
        self.stack = []
        self.tag_counts = {}
        self.reset()

        wrapped_html = self._append_root_tag(raw_html)
        try:
            self.feed(wrapped_html)
        except Exception as e:
            raise ScrapegoatParseException(f"Failed to parse HTML: {str(e)}")
        return self.root

    def get_root(self) -> HTMLNode:
        """
        Returns the root HTMLNode of the parsed HTML tree.

        Returns:
            HTMLNode: The root node of the HTMLNode tree.

        Usage:
            ```python
            gardener = Gardener()
            # grow a tree first, else root will be None.
            root_node = gardener.get_root()
            ```
        """
        return self.root


def main():
    """
    """
    pass


if __name__ == "__main__":
    main()
