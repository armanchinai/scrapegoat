from requests.exceptions import HTTPError, MissingSchema
from textual.app import App, SystemCommand
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Header, Footer, Tree, Button, Static, Select, Collapsible, Checkbox, Input, ListView, ListItem, RadioSet, ContentSwitcher, Label
from textual.widgets.tree import TreeNode
from textual.containers import HorizontalGroup, VerticalGroup, HorizontalScroll, Grid
from importlib.resources import files
from platform import system
from subprocess import Popen, PIPE
from pathlib import Path
import os

from scrapegoat_core import Gardener, Sheepdog, HTMLNode

NodeAttributes = (
	"tag_type", "id", "has_data", "body", "parent", "children"
)

ChurnFlags = (
	"ignore-children", "ignore-grandchildren"
)

def write_to_clipboard(string:str) -> None:
	os_name = system()
	match os_name:
		case "Windows":
			Popen("clip", env={'LANG': 'en_US.UTF-8'}, stdin=PIPE).communicate(string.encode("utf-8"))
		case "Darwin":
			Popen("pbcopy", env={'LANG': 'en_US.UTF-8'}, stdin=PIPE).communicate(string.encode("utf-8"))
		case "Linux":
			pass
		case _:
			pass

def save_to_file(file_path: str, script: str) -> None:
	with open(file_path, "w") as f:
		f.write(script)
		f.close()

def load_from_file(file_path: str) -> list[str]:
	pass # TODO: Implement

class NodeWrapper():
	def __init__(self, html_node: HTMLNode, branch: TreeNode):
		self.id = html_node.id
		self.tag_type = html_node.tag_type
		self.node = html_node
		self.branch = branch
		self.added_to_query = False
		self.extract_attributes = []
		self.flags = []

	def _update_branch_label(self, new_label: str):
		self.branch.label = new_label
		self.branch.refresh()

	def set_querying(self, value: bool):
		if self.added_to_query != value:
			if value == True:
				self.added_to_query = True

				node_text = f"*<{self.node.tag_type}>"
				if len(self.node.body.strip()) > 0:
					node_text += f" {self.node.body.strip()}"
				self._update_branch_label(node_text)

			elif value == False:
				self.added_to_query = False

				node_text = f"<{self.node.tag_type}>"
				if len(self.node.body.strip()) > 0:
					node_text += f" {self.node.body.strip()}"
				self._update_branch_label(node_text)

	def get_querying(self) -> bool:
		return self.added_to_query
	
	def get_retrieval_instructions(self) -> str:
		instructions = self.node.retrieval_instructions
		if len(self.extract_attributes) == 0 and len(self.flags) == 0:
			return instructions
		
		if len(self.extract_attributes) > 0:
			instructions = self.node.retrieval_instructions
			instructions += "\nEXTRACT "
			for attribute in self.extract_attributes:
				instructions += attribute
				if attribute != self.extract_attributes[-1]:
					instructions += ", "

		if len(self.flags) > 0:
			if len(self.extract_attributes) == 0:
				instructions += "\nEXTRACT"

			instructions += " "

			for flag in self.flags:
				instructions += f"--{flag}"
				if flag != self.flags[-1]:
					instructions += " "

		return instructions + ";"
	
	def append_attribute(self, attribute_name: str) -> None:
		if attribute_name not in self.extract_attributes:
			self.extract_attributes.append(attribute_name)

	def append_flag(self, flag: str) -> None:
		if flag not in self.flags:
			self.flags.append(flag)

	def remove_attribute(self, attribute_name: str) -> None:
		if attribute_name in self.extract_attributes:
			self.extract_attributes.remove(attribute_name)

	def remove_flag(self, flag: str) -> None:
		if flag in self.flags:
			self.flags.remove(flag)

	def check_query_attribute(self, attribute: str) -> bool:
		return attribute in self.extract_attributes
	
	def check_flag(self, flag: str) -> bool:
		return flag in self.flags
	
	def __contains__(self, item) -> bool:
		if type(item) != "str":
			return False

		if item in f"<{self.tag_type}>":
			return True
		
		if item in self.node.body:
			return True
		
		for html_attribute in self.node.html_attributes.keys():
			if item in f"@{html_attribute}={self.node.html_attributes[html_attribute]}":
				return True
			
		for node_attribute in NodeAttributes:
			if item in f"#{node_attribute}={self.node.to_dict()[node_attribute]}":
				return True
		
		return False

class QueryWrapper:
	def __init__(self, query):
		self.query = query
		self.query_item = ListItem(Static(query))

	def get_retrieval_instructions(self):
		return self.query
	
	def __eq__(self, other):
		if type(other) == QueryWrapper:
			return other.get_retrieval_instructions() == self.get_retrieval_instructions()
		elif type(other) == str:
			return other == self.get_retrieval_instructions()
		else:
			return False

class ControlPanel(VerticalGroup):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.current_node = None
		self.query_nodes = []

	def compose(self):
		self.node_details = {
			"node_desc": ListView(),
			"queried_attributes": HorizontalScroll(),
			"flags": HorizontalScroll()
		}

		with Collapsible(title="Node Details"):
			yield self.node_details["node_desc"]
			yield self.node_details["queried_attributes"]
			yield self.node_details["flags"]

		self.contextual_button = Button("<+>", id="node-add-remove", variant="success")
		self.copy_button = Button("<Copy>", id="copy-query", variant="primary")

		yield HorizontalGroup(
			self.contextual_button,
			self.copy_button,
			id="ctrl-buttons",
		)

		yield ListView(id="query-view")

	def update_node(self, node: NodeWrapper):
		self.node_details["node_desc"].clear()
		for child in list(self.node_details["queried_attributes"].children):
			child.remove()

		for child in list(self.node_details["flags"].children):
			child.remove()

		self.current_node = node
		if node is not None:
			if node.get_querying():
				self.contextual_button.label = "<->"
				self.contextual_button.variant = "error"
			else:
				self.contextual_button.label = "<+>"
				self.contextual_button.variant = "success"

			for node_attribute in NodeAttributes:
				index = f"node-attribute-{hash(f"{node.id}-{node_attribute}")}"

				if node.node.has_attribute(node_attribute):
					if node_attribute == "children":
						children = [child.id for child in node.node.children]
						self.node_details["node_desc"].append(ListItem(Static(f"{node_attribute}: {", ".join(children)}", classes="node-desc-item")))
					elif node_attribute != "body":
						self.node_details["node_desc"].append(ListItem(Static(f"{node_attribute}: {node.node.to_dict()[node_attribute]}"), classes="node-desc-item"))
					elif len(node.node.body) > 0:
						self.node_details["node_desc"].append(ListItem(Static(f"{node_attribute}: ...", classes="node-desc-item")))
					self.node_details["queried_attributes"].mount(
						Checkbox(f"{node_attribute}", id=index, value=self.current_node.check_query_attribute(node_attribute))
					)

			for html_attribute in node.node.html_attributes:
				index = f"html-attribute-{hash(f"{node.id}-{html_attribute.replace("@", "")}")}"

				self.node_details["node_desc"].append(ListItem(Static(f"{html_attribute}: {node.node.html_attributes[html_attribute]}")))
				self.node_details["queried_attributes"].mount(
					Checkbox(f"{html_attribute}", id=index, value=self.current_node.check_query_attribute(html_attribute))
				)

			for flag in ChurnFlags:
				index = f"flag-{hash(f"{node.id}-{flag}")}"

				self.node_details["flags"].mount(
					Checkbox(f"{flag}", id=index, value=self.current_node.check_flag(flag))
				)

	def update_url(self, url):
		self.reset()
		self.append_query(f"VISIT {url};")

	def append_query(self, query):
		self.loom.changes_saved = False
		wrapped = QueryWrapper(query)
		self.query_nodes.append(wrapped)
		self.query_one(ListView).append(wrapped.query_item)
	
	def add_node(self):
		if self.current_node and self.current_node not in self.query_nodes:
			self.loom.changes_saved = False
			self.query_nodes.append(self.current_node)
			query_list = self.query_one(ListView)

			self.current_node.set_querying(True)
			
			self.current_node.query_item = ListItem(Static(self.current_node.get_retrieval_instructions()))
			query_list.append(self.current_node.query_item)

			self.contextual_button.label = "<->"
			self.contextual_button.variant = "error"

	def append_attribute(self, attribute):
		self.loom.changes_saved = False
		self.current_node.append_attribute(attribute)
		new_instr = self.current_node.get_retrieval_instructions()

		list_item = self.current_node.query_item
		list_item.children[0].remove()
		list_item.mount(Static(new_instr))

	def append_flag(self, flag):
		self.loom.changes_saved = False
		self.current_node.append_flag(flag)
		new_instr = self.current_node.get_retrieval_instructions()

		list_item = self.current_node.query_item
		list_item.children[0].remove()
		list_item.mount(Static(new_instr))

	def remove_query(self, query):
		self.loom.changes_saved = False
		for item in self.query_nodes:
			if item.get_retrieval_instructions() == query:
				self.query_nodes.remove(item)
				item.query_item.remove()
				if type(item) == NodeWrapper:
					item.set_querying(False)
				return
	
	def remove_node(self):
		if self.current_node and self.current_node in self.query_nodes:
			self.loom.changes_saved = False
			self.query_nodes.remove(self.current_node)
			query_list = self.query_one(ListView)
			
			self.current_node.query_item.remove()

			self.current_node.set_querying(False)

			self.contextual_button.label = "<+>"
			self.contextual_button.variant = "success"

	def remove_attribute(self, attribute):
		self.loom.changes_saved = False
		self.current_node.remove_attribute(attribute)
		new_instr = self.current_node.get_retrieval_instructions()

		list_item = self.current_node.query_item
		list_item.children[0].remove()
		list_item.mount(Static(new_instr))

	def remove_flag(self, flag):
		self.loom.changes_saved = False
		self.current_node.remove_flag(flag)
		new_instr = self.current_node.get_retrieval_instructions()

		list_item = self.current_node.query_item
		list_item.children[0].remove()
		list_item.mount(Static(new_instr))

	def get_query(self):
		query = ""
		for i in range(0, len(self.query_nodes)):
			node = self.query_nodes[i]
			query += node.get_retrieval_instructions()
			if i != len(self.query_nodes) - 1:
				query += "\n"

		return query
	
	def reset(self):
		self.current_node = None
		self.query_nodes = []
		self.query_one(ListView).clear()

class FindModal(ModalScreen):
	BINDINGS = [
		("escape", "app.pop_screen", "Exit")
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def compose(self):
		yield Input(placeholder="Search...", id="find-node-input")
		yield Button("Next", id="find-node-next", variant="primary")
		yield Button("Prev", id="find-node-prev", variant="primary")

class SetURLModal(ModalScreen):
	BINDINGS = [
		("escape", "app.pop_screen", "Exit")
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.prev_url = ""
		self.curr_url = ""
		self.button = Button("Visit", id="url-confirm", variant="error")

	def compose(self):
		yield Input(placeholder="https://www.example.com/data", id="url-input")
		yield self.button
	
	def on_button_pressed(self, _):
		self.prev_url = self.curr_url
		self.button.variant = "error"
		self.app.pop_screen()

	def on_input_changed(self, event: Input.Changed):
		self.curr_url = event.input.value

		if self.curr_url == self.prev_url:
			self.button.variant = "error"
		else:
			self.button.variant = "success"

class AppendQueryModal(ModalScreen):
	BINDINGS = [
		("escape", "app.pop_screen", "Exit")
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.select_set = Select([(opt, opt) for opt in ("Universal Selector", "Output Statement")], allow_blank=False)
		self.enter_button = Button("Append Query", variant="success", id="append-query-enter")
		self.cur_selection = "selector" # or "output"
		self.clause = {}
		self.reset_clause()
		self.clause_preview = Label(f"SCRAPE {self.clause["target_tags"]};", id="append-query-preview")

		selector_node_attributes = HorizontalScroll(*[Checkbox(attr, id=f"selector-na-{attr}") for attr in NodeAttributes], id="selector-node-attributes")
		selector_flags = HorizontalScroll(*[Checkbox(flag, id=f"selector-fl-{flag}") for flag in ChurnFlags], id="selector-flags")

		#Universal Selector Options
		self.selector_options = (
			Input(placeholder="target tags", id="selector-tag-type"),
			selector_node_attributes,
			Input(placeholder="html attributes", id="selector-html-attributes"),
			selector_flags
		)
		#Output Statement Options
		self.output_options = (
			RadioSet("JSON", "CSV", id="output-file-type"),
			Input(placeholder="output directory", id="output-directory-path"),
			Input(placeholder="file name", id="output-file-name")
		)

	def compose(self):
		with HorizontalGroup(id="append-query-buttons"):
			yield Button("Universal Selector", id="append-query-selector")
			yield Button("Output Statement", id="append-query-output")

		with ContentSwitcher(initial="append-query-selector"):
			with VerticalGroup(id="append-query-selector"):
				for option in self.selector_options:
					yield option
			with VerticalGroup(id="append-query-output"):
				for option in self.output_options:
					yield option

		yield self.clause_preview
		yield self.enter_button

	def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
		if event.radio_set.id == "output-file-type":
			self.clause["file_type"] = "json" if event.pressed.label._text == "JSON" else "csv"
			self.update_clause()

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id in ("append-query-selector", "append-query-output"):
			self.query_one(ContentSwitcher).current = event.button.id
			if event.button.id == "append-query-selector":
				self.cur_selection = "selector"
			elif event.button.id == "append-query-output":
				self.cur_selection = "output"
			self.update_clause()
		elif event.button.id == "append-query-enter":
			self.dismiss(self.clause["raw"])
			self.reset_clause()
	
	def on_input_changed(self, event: Input.Changed) -> None:
		if event.input.id == "output-directory-path":
			self.clause["directory_path"] = event.value
		elif event.input.id == "output-file-name":
			self.clause["file_name"] = event.value
		elif event.input.id == "selector-tag-type":
			self.clause["target_tags"] = event.value
		elif event.input.id == "selector-html-attributes":
			self.clause["html_attributes"] = event.value.replace(" ", "").replace("@", "").split(",")
		self.update_clause()

	def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
		if event.checkbox.id[:12] == "selector-na-":
			if event.value:
				self.clause["node_attributes"].append(str(event.checkbox.label))
			else:
				self.clause["node_attributes"].remove(str(event.checkbox.label))
		elif event.checkbox.id[:12] == "selector-fl-":
			if event.value:
				self.clause["flags"].append(str(event.checkbox.label))
			else:
				self.clause["flags"].remove(str(event.checkbox.label))
		self.update_clause()

	def update_clause(self) -> None:
		new = ""
		if self.cur_selection == "selector":
			new = f"SCRAPE {self.clause["target_tags"]};"
			if len(self.clause["node_attributes"]) + len(self.clause["html_attributes"]) + len(self.clause["flags"]) > 0:
				new += f"\nEXTRACT {(", ".join(self.clause["node_attributes"]) + " ") if len(self.clause["node_attributes"]) > 0 else ""}"
				new += ("@" + ", @".join(self.clause["html_attributes"]) + " ") if len(self.clause["html_attributes"]) > 0 else ""
				new += ("--" + ", --".join(self.clause["flags"])) if len(self.clause["flags"]) > 0 else ""
				new += ";"
		elif self.cur_selection == "output":
			new = f"OUTPUT {self.clause["file_type"]} --filename \"{self.clause["file_name"]}\" --filepath \"{self.clause["directory_path"]}\";"
		
		self.clause["raw"] = new
		self.query_one(Label).update(new)

	def reset_clause(self) -> None:
		self.clause = {
			"file_name": "",
			"directory_path": "",
			"target_tags": "",
			"file_type": "json",
			"node_attributes": [],
			"html_attributes": [],
			"flags": [],
			"raw": ""
		}

class RemoveQueryModal(ModalScreen):
	BINDINGS = [
		("escape", "app.pop_screen", "Exit")
	]

	def __init__(self, *kwargs):
		super().__init__(*kwargs)

	def compose(self):
		yield Grid(
            Label("Are you sure you want remove the selected query?", id="question"),
            Button("Yes", variant="error", id="remove-query-yes"),
            Button("No", variant="primary", id="remove-query-no"),
            id="dialog",
        )
		
	def on_button_pressed(self, event: Button.Pressed):
		if event.button.id == "remove-query-yes":
			self.dismiss(True)
		elif event.button.id == "remove-query-no":
			self.dismiss(False)

class SaveAsModal(ModalScreen):
	BINDINGS = [
		("escape", "app.pop_screen", "Exit")
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def compose(self):
		yield Input(f"{str(Path.home())}{os.sep}script.goat", placeholder="file path", id="save-as-input")
		yield Button("Save", id="save-as-confirm", variant="primary")

	def on_button_pressed(self, _: Button.Pressed):
		self.app.pop_screen()

class Loom(App):
	CSS_PATH = str(files("scrapegoat_loom").joinpath("gui-styles/tapestry.tcss"))
	SCREENS = {"find": FindModal, "set-url": SetURLModal, "add-query": AppendQueryModal, "remove-query": RemoveQueryModal, "save-as": SaveAsModal}
	BINDINGS = [
		Binding("ctrl+f", "push_screen('find')", "Search Tree", tooltip="Shows the node search widget."),
		Binding("ctrl+u", "toggle_set_url", "Set URL", tooltip="Shows the URL input widget."),
		Binding("ctrl+a", "toggle_insert_query", "Append Query", tooltip="Appends a new scrape query."),
		Binding("ctrl+r", "toggle_remove_query", "Remove Query", tooltip="Removes a query."),
		Binding("ctrl+S", "toggle_save_as", "Save As", tooltip="Save the query to a new file."),
		Binding("ctrl+s", "save", "Save", tooltip="Save the query."),
	]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.sub_title = "untitled.goat"
		self.prev_url = ""
		self.url = ""
		self.has_tree = False
		self.nodes = {}
		self.current_search_nodes = []
		self.search_node_index = 0
		self.selected_query = ""
		self.save_path = ""
		self.changes_saved = False

	def get_system_commands(self, screen):
		yield from super().get_system_commands(screen)
		yield SystemCommand("Find", "Shows/Hides the node search widget.", self.toggle_search)
		yield SystemCommand("Set URL", "Sets the URL for the Tree Visualizer to pull from.", self.action_toggle_set_url)
		yield SystemCommand("Append Query", "Appends a new scrape query.", self.action_toggle_insert_query)
		yield SystemCommand("Save As", "Save the query to a new file.", self.action_toggle_save_as)
		yield SystemCommand("Save", "Save the query to a file.", self.action_save)

	def _create_tree_from_root_node(self, node) -> Tree:
		self.nodes = {}
		tree = None

		for child in node.preorder_traversal():
			if tree is None:
				tree = Tree(f"<{child.tag_type}>")
				tree.root._html_node_id = child.id
				self.nodes[child.id] = NodeWrapper(child, tree.root)
				continue

			node_label = f"<{child.tag_type}>"
			if len(child.body.strip()) > 0:
				node_label += f" {child.body}"

			branch = tree.root if child.parent is None else self.nodes[child.parent.id].branch
			branch.expand()
			branch.allow_expand = False
			
			if len(child.children) == 0:
				child_branch = branch.add_leaf(node_label)
			else:
				child_branch = branch.add(node_label)

			child_branch._html_node_id = child.id
			self.nodes[child.id] = NodeWrapper(child, child_branch)

		return tree
	
	def _create_placeholder_tree(self) -> Tree:
		tree = Tree("<No URL Set>")
		tree.root.allow_expand = False

		return tree
	
	def _search_tree(self, search_string:str) -> list[NodeWrapper]:
		return_list = []
		for node in self.nodes.values():
			if search_string in node:
				return_list.append(node)
		return return_list
	
	def _update(self):
		if len(self.save_path) > 0:
			self.sub_title = self.save_path.split(os.sep)[-1]
		if not self.changes_saved:
			if len(self.sub_title) > 0:
				if self.sub_title[-1] != "*":
					self.sub_title += "*"
	
	def action_add_remove_node(self) -> None:
		if self.has_tree:
			if self.control_panel and self.control_panel.current_node:
				if self.control_panel.current_node.get_querying() == False:
					self.control_panel.add_node()
				else:
					self.control_panel.remove_node()

	def toggle_search(self) -> None:
		self.push_screen("find")

	def action_toggle_set_url(self) -> None:
		self.push_screen("set-url")

	def action_toggle_insert_query(self) -> None:
		if self.has_tree:
			self.push_screen("add-query", lambda x: self.control_panel.append_query(x))

	def action_toggle_remove_query(self) -> None:
		if self.selected_query != None and self.selected_query[:5] != "VISIT" and self.has_tree:
			self.push_screen("remove-query", lambda x: self.remove_query(x))

	def action_toggle_save_as(self) -> None:
		self.push_screen("save-as")

	def action_save(self) -> None:
		if len(self.save_path) > 0:
			save_to_file(self.save_path, self.control_panel.get_query())
			self.changes_saved = True
		else:
			self.push_screen("save-as")

	def remove_query(self, confirm) -> None:
		if confirm:
			self.control_panel.remove_query(self.selected_query)
			self.selected_query = None

	def update_url(self) -> None:
		if self.url == self.prev_url:
			return

		try:
			html = Sheepdog().fetch(self.url)
			root = Gardener().grow_tree(html)

			prev_tree = self.query_one(Tree)
			new_tree = self._create_tree_from_root_node(root)

			prev_tree.root = new_tree.root
			self.has_tree = True
			self.control_panel.update_url(self.url)
			self.prev_url = self.url
			self.control_panel.update_node(self.nodes[new_tree.root._html_node_id])
		except HTTPError:
			self.notify("The URL you entered could not be reached. Please check your internet connection and try again.", title="Could Not Resolve URL", severity="warning", timeout=10)
		except MissingSchema:
			self.notify("The URL you entered is invalid. Please try again.", title="Could Not Resolve URL", severity="warning", timeout=10)
		except:
			self.notify("An unknown error occured. Please try again.", title="Unknown Error", severity="error", timeout=10)

	def on_mount(self) -> None:
		self.set_interval(0.3, self._update)

	def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
		if self.has_tree:
			if self.control_panel:
				self.control_panel.update_node(self.nodes.get(event.node._html_node_id, None))

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "url-confirm":
			self.update_url()
		elif event.button.id == "save-as-confirm":
			self.action_save()

		if self.has_tree:
			if event.button.id == "node-add-remove":
				self.action_add_remove_node()
			elif event.button.id == "copy-query":
				write_to_clipboard(self.control_panel.get_query())
			elif event.button.id == "find-node-next":
				if len(self.current_search_nodes) > 0:
					self.search_node_index += 1
					if self.search_node_index >= len(self.current_search_nodes):
						self.search_node_index = 0

					self.query_one(Tree).move_cursor(self.current_search_nodes[self.search_node_index].branch, True)
			elif event.button.id == "find-node-prev":
				if len(self.current_search_nodes) > 0:
					self.search_node_index -= 1
					if self.search_node_index < 0:
						self.search_node_index = len(self.current_search_nodes) - 1

					self.query_one(Tree).move_cursor(self.current_search_nodes[self.search_node_index].branch, True)

	def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
		if self.has_tree:
			if "flag" == event.checkbox.id[0:4]:
				if event.checkbox.value:
					self.control_panel.append_flag(str(event.checkbox.label))
				else:
					self.control_panel.remove_flag(str(event.checkbox.label))
			elif "html-attribute" == event.checkbox.id[0:14] or "node-attribute" == event.checkbox.id[0:14]:
				if event.checkbox.value:
					self.control_panel.append_attribute(str(event.checkbox.label))
				else:
					self.control_panel.remove_attribute(str(event.checkbox.label))

	def on_input_changed(self, event: Input.Changed) -> None:
		if event.input.id == "url-input":
			self.url = event.input.value
		elif event.input.id == "save-as-input":
			self.save_path = event.input.value

		if self.has_tree:
			if event.input.id == "find-node-input":
				self.current_search_nodes = self._search_tree(event.input.value)
				if len(self.current_search_nodes) > 0:
					self.search_node_index = 0
					self.query_one(Tree).move_cursor(self.current_search_nodes[self.search_node_index].branch, True)

	def on_list_view_selected(self, event: ListView.Selected):
		if event.list_view.id == "query-view":
			self.selected_query = event.item.query_one(Static).render()
		else:
			self.selected_query = None

	def compose(self):
		yield Header(name="ScrapeGoat", icon="🐐")
		dom_tree = self._create_placeholder_tree()
		ctrl = ControlPanel()
		self.control_panel = ctrl
		ctrl.loom = self

		yield dom_tree
		yield ctrl

		yield Footer()

	def weave(self):
		self.run()