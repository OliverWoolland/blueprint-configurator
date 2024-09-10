from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.events import Mount
from textual.widgets import Footer, Header, Pretty, SelectionList, TabPane, TabbedContent, Static, Log
from textual.widgets.selection_list import Selection
from textual import log

import rdflib

# ------------------------------------------------------------------------------
# Textual App (the TUI)

class BlueprintConfigurator(App[None]):
    CSS_PATH = "layout.tcss"
    BINDINGS = [
        ("c", "show_tab('classes')", "Show classes tab"),
        ("l", "show_tab('links')", "Show links tab"),
        ("d", "show_tab('details')", "Show details tab"),
    ]

    graph = None

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent(initial="classes"):
            with TabPane("Classes", id="classes"):
                yield Static("## Classes")
            with TabPane("Links", id="links"):
                yield Static("## Links")
            with TabPane("Details", id="details"):
                yield Static("## Details")

        items = self.fetch_items("classes")
        with Horizontal():
            yield SelectionList[str](*items,)
            yield Pretty([])
            #yield Log()
            #log = self.query_one(Log)

        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Items found"
        self.query_one(Pretty).border_title = "Selected items"

    def action_show_tab(self, tab: str) -> None:
        
        # ----------------------------------------------------------------------
        # Write out config as user has specified

        # get selected items
        selected_items = self.query_one(SelectionList).selected

        # get the current tab
        current_tab = self.get_child_by_type(TabbedContent).active

        # write out the selected items (i.e. items in graph which a :label which is in selected_items)
        with open(f"{current_tab}.ttl", "w") as f:
            for item in selected_items:
                triples_maching_label = self.graph.triples((rdflib.term.URIRef(item), None, None))
                for triple in triples_maching_label:
                    f.write(f"{triple[0]} {triple[1]} {triple[2]} .\n")

        # write out config file to configure preselection of items
        with open(f"{current_tab}.conf", "w") as f:
            for item in selected_items:
                f.write(f"{item}\n")
        # ----------------------------------------------------------------------
        # Switch to the new tab, and update the selection list

        # Switch to the new tab
        self.get_child_by_type(TabbedContent).active = tab

        # Update SelectionList
        items = self.fetch_items(tab)

        items_list = self.query_one(SelectionList)
        items_list.clear_options()
        items_list.add_options(items)

        
    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.query_one(Pretty).update(self.query_one(SelectionList).selected)

    # --------------------------------------------------------------------------
    # Methods for fetching items from the ttl files

    def fetch_items(self, filename) -> list[str]:
        self.graph = rdflib.Graph()
        self.graph.parse(f"_{filename}.ttl", format="ttl")

        # Read config file (if existing)
        preselected_items = []
        try:
            with open(filename + ".conf", "r") as f:
                preselected_items = f.read().splitlines()
        except FileNotFoundError:
            pass
        # Fetch all items
        selections = []
        for s, p, o in self.graph.triples((None, None, None)):
            label = None
            if filename == "classes":
                predicate_filter = "label"
                display = str(o)
                value = str(s)
            if filename == "links":
                predicate_filter = "link"
                display = f'{s} -> {o}'
                value = str(s)
            if filename == "details":
                predicate_filter = "label"
                display = f'{s} -> {o}'
                value = str(s)

            base_uri = 'http://schema.example.org/blueprint-ui-config-initializer/'
            predicate = rdflib.term.URIRef(f'{base_uri}{predicate_filter}')
            if p == predicate:
                preselected = str(s) in preselected_items
                selection = Selection(display, value, preselected)
                selections.append(selection)
                
        return selections

if __name__ == "__main__":
    app = BlueprintConfigurator()
    app.run()
