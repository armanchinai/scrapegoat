"""
"""

import uuid


class HTMLNode:
    """
    """
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, raw: str, tag_type: str, has_data: bool = False, html_attributes: dict[str, any] = None, body: str = "", parent=None):
        """
        """
        self.id = str(uuid.uuid4())
        self.raw = raw
        self.tag_type = tag_type
        self.has_data = has_data
        self.html_attributes = {"@"+k: v for k, v in (html_attributes or {}).items()}
        self.body = body
        self.children = []
        self.retrieval_instructions = ""
        self.parent = parent
        self.extract_fields = None
        self.extract_flags = {"ignore_children": False, "ignore_grandchildren": False, "table": False}
    
    def to_dict(self, ignore_children=False) -> str:
        """
        """
        if self.extract_flags["table"]:
            if self.tag_type != "table":
                raise ValueError("Table extraction requested on a non-table node")
            return self._handle_table_extract()
        ignore_children = self.extract_flags["ignore_children"] or ignore_children
        for child in self.children:
            child.set_extract_instructions(fields=self.extract_fields, ignore_children=self.extract_flags["ignore_grandchildren"])
        if self.extract_fields:
            return self._handle_extract_fields(ignore_children)
        if ignore_children:
            return self._handle_ignore_children()
        return {
            "id": self.id,
            "raw": self.raw,
            "tag_type": self.tag_type,
            "has_data": self.has_data,
            "html_attributes": self.html_attributes,
            "body": self.body,
            "children": [child.to_dict() for child in self.children],
            "retrieval_instructions": self.retrieval_instructions,
            "parent": self.parent.id if self.parent else None,
            "extract_fields": self.extract_fields,
            "extract_flags": self.extract_flags,
        }    
    
    def _handle_extract_fields(self, ignore_children: bool) -> dict  :
        """
        """
        dict_representation = {}
        for field in self.extract_fields:
            if field[0] == "@":
                dict_representation[field] = self.html_attributes.get(field, None)
            else:
                if field == "id":
                    dict_representation["id"] = self.id
                elif field == "tag_type":
                    dict_representation["tag_type"] = self.tag_type
                elif field == "has_data":
                    dict_representation["has_data"] = self.has_data
                elif field == "html_attributes":
                    dict_representation["html_attributes"] = self.html_attributes
                elif field == "body":
                    dict_representation["body"] = self.body
                elif field == "children" and not ignore_children:
                    dict_representation["children"] = [child.to_dict() for child in self.children]
                elif field == "retrieval_instructions":
                    dict_representation["retrieval_instructions"] = self.retrieval_instructions
                elif field == "parent":
                    dict_representation["parent"] = self.parent.id if self.parent else None
                elif field == "extract_fields":
                    dict_representation["extract_fields"] = self.extract_fields
                elif field == "extract_flags":
                    dict_representation["extract_flags"] = self.extract_flags
        return dict_representation
    
    def _handle_ignore_children(self) -> dict:
        """
        """
        return {
            "id": self.id,
            "raw": self.raw,
            "tag_type": self.tag_type,
            "has_data": self.has_data,
            "html_attributes": self.html_attributes,
            "body": self.body,
            "retrieval_instructions": self.retrieval_instructions,
            "parent": self.parent.id if self.parent else None,
            "extract_fields": self.extract_fields,
            "extract_flags": self.extract_flags,
        }
    
    def _handle_table_extract(self) -> list:
        """
        Convert the <table> into a list of row JSON objects.
        Each row is a dict: {header: cell_value}
        """
        trows = self.get_descendants(tag_type="tr")

        if not trows:
            return []

        # Extract header row
        header_row = trows[0]
        headers = []

        header_cells = (
            header_row.get_descendants(tag_type="th") +
            header_row.get_descendants(tag_type="td")
        )

        for cell in header_cells:
            # Hoist descendant text
            for child in cell.get_descendants():
                cell.body += " " + child.body
            headers.append(cell.body.strip())

        # Extract data rows
        result = []

        for tr in trows[1:]:
            cells = tr.get_descendants(tag_type="td") + tr.get_descendants(tag_type="th")
            row = {}

            for col_index, header in enumerate(headers):
                if col_index < len(cells):
                    cell = cells[col_index]

                    for child in cell.get_descendants():
                        cell.body += " " + child.body

                    row[header] = cell.body.strip()
                else:
                    row[header] = ""

            result.append(row)
        return result



    def to_string(self) -> str:
        """
        """
        return str(self.to_dict())
    
    def __repr__(self):
        """
        """
        return self.to_string()

    def to_html(self, indent=0) -> str:
        """
        """
        html_attribute_string = " ".join(f'{k}="{v}"' for k, v in self.html_attributes.items())
        if html_attribute_string:
            opening = f"<{self.tag_type} {html_attribute_string}"
        else:
            opening = f"<{self.tag_type}"

        if self.tag_type in self.VOID_TAGS:
            opening += " />"
        else:
            opening += ">"

        text = f" {self.body}" if self.has_data else ""

        pad = "  " * indent
        result = f"{pad}{opening}{text}\n"

        for child in self.children:
            result += child.to_html(indent + 1)

        if self.tag_type not in self.VOID_TAGS:
            result += f"{pad}</{self.tag_type}>\n"
        return result

    def __str__(self):
        return self.to_string()
    
    def get_parent(self):
        """
        """
        return self.parent
    
    def get_children(self):
        """
        """
        return self.children
    
    def get_ancestors(self):
        """
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_descendants(self, tag_type: str = None, **html_attributes) -> list:
        """
        """
        descendants = []
        for child in self.children:
            if (tag_type is None or child.tag_type == tag_type) and all(child.html_attributes.get(k) == v for k, v in html_attributes.items()):
                descendants.append(child)
            descendants.extend(child.get_descendants(tag_type, **html_attributes))
        return descendants
    
    def preorder_traversal(self):
        """
        """
        yield self
        for child in self.children:
            yield from child.preorder_traversal()

    def has_html_attribute(self, key, value=None) -> bool:
        """
        """
        if value is None:
            return key in self.html_attributes
        if self.html_attributes.get(key) is None:
            return False
        return value in self.html_attributes.get(key)
    
    def has_attribute(self, key, value=None) -> bool:
        """
        """
        if key == "tag_type":
            if value is None:
                return self.tag_type is not None
            return self.tag_type == value
        if key == "id":
            if value is None:
                return self.id is not None
            return str(self.id) == value
        if key == "has_data":
            if value is None:
                return self.has_data
            return self.has_data == value
        if key == "body":
            if value is None:
                return self.body is not None
            return self.body == value
        if key == "retrieval_instructions":
            if value is None:
                return self.retrieval_instructions is not None
            return self.retrieval_instructions == value
        if key == "extract_fields":
            if value is None:
                return self.extract_fields is not None
            return self.extract_fields == value
        if key == "extract_flags":
            if value is None:
                return self.extract_flags is not None
            return self.extract_flags == value
        if key == "parent":
            if value is None:
                return self.parent is not None
            return self.parent and str(self.parent.id) == value
        if key == "children":
            if value is None:
                return len(self.children) > 0
            return any(str(child.id) == value for child in self.children)
        if key == "raw":
            if value is None:
                return self.raw is not None
            return self.raw == value
        return False
    
    def is_descendant_of(self, tag_type) -> bool:
        """
        """
        return any(ancestor.tag_type == tag_type for ancestor in self.get_ancestors())
    
    def set_retrieval_instructions(self, instruction: str):
        """
        """
        self.retrieval_instructions = instruction

    def set_extract_instructions(self, fields: list=None, ignore_children=False, ignore_grandchildren=False, table=False):
        """
        """
        self.extract_fields = fields or None
        self.extract_flags = {"ignore_children": ignore_children, "ignore_grandchildren": ignore_grandchildren, "table": table}

    def clear_extract_instructions(self):
        """
        """
        self.extract_fields = None
        self.extract_flags = None
        self.table = False


def main():
    """
    """
    pass


if __name__ == "__main__":
    main()
