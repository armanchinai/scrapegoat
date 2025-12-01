"""
"""

class Goat:
    """
    The Goat class is responsible for executing graze commands on an HTMLNode tree to select and scrape data.

    Hint:
        This class is one of Scrapegoat's highly extendable classes. You can create your own Goat subclass to implement custom grazing behavior to use with the Shepherd master class.
    """
    def feast(self, root: "HTMLNode", graze_commands: ["GrazeCommand"]) -> list["HTMLNode"]: # type: ignore
        """
        Executes a series of graze commands starting from the given root node.

        Args:
            root (HTMLNode): The starting HTMLNode from which to execute the graze commands.
            graze_commands (["GrazeCommand"]): A list of GrazeCommand objects to be executed in sequence.

        Returns:
            A list of HTMLNode objects that are the result of executing the graze commands.

        Usage:
            ```python
            root_node = HTMLNode(...)  # Assume this is an initialized HTMLNode
            select_command = GrazeCommand(action="select", parameters=...) 
            scrape_command = GrazeCommand(action="scrape", parameters=...)

            results = Goat().feast(root_node, [select_command, scrape_command])
            ```
        """
        results = []
        i = 0
        while i < len(graze_commands):
            graze_command = graze_commands[i]
            if graze_command.action.lower() == "select":
                rebased_roots = graze_command.execute(root)
                graze_command_subset = graze_commands[i + 1:]
                for new_root in rebased_roots:
                    results.extend(self.feast(new_root, graze_command_subset))
                return results
            else:
                results.extend(graze_command.execute(root))
            i += 1
        return results
