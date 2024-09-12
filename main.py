from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, SelectionList, Static, Log
from textual.widgets.selection_list import Selection

import argparse
import rdflib

# ------------------------------------------------------------------------------
# Textual App (the TUI)

class BlueprintConfigurator(App[None]):
    CSS_PATH = "layout.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    graph = None

    def __init__(self, item_type: str) -> None:
        self.item_type = item_type
        super().__init__()

    # --------------------------------------------------------------------------
    # Render the TUI

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield SelectionList[str](*self.fetch_items(self.item_type))
        yield Footer()

    # --------------------------------------------------------------------------
    # Events
    
    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Items retrieved from the database"

    # --------------------------------------------------------------------------
    # Actions
        
    def action_quit(self) -> None:

        # ----------------------------------------------------------------------
        # Write out config as user has specified

        # Get selected items
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

        # ----------------------------------------------------------------------
        # Write out config file to configure preselection of items
        
        with open(f"{self.item_type}.conf", "w") as f:
            for item in selected_items:
                f.write(f"{item}\n")

        # ----------------------------------------------------------------------
        # Quit the app        
                
        self.exit()

    # --------------------------------------------------------------------------
    # Methods for fetching items from the ttl files

    def fetch_items(self, filename) -> list[str]:
        self.graph = rdflib.Graph()
        self.graph.parse(f"_{filename}.ttl", format="ttl")

        # ----------------------------------------------------------------------
        # Read config file (if existing)
        
        preselected_items = []
        try:
            with open(filename + ".conf", "r") as f:
                preselected_items = f.read().splitlines()
        except FileNotFoundError:
            pass

        # ----------------------------------------------------------------------
        # Configure the display and query based on the filename
        
        selections = []

        if filename == "classes":
            query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?s ?p ?o WHERE { ?s :label ?o . }"""
        if filename == "links":
            query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?path ?label ?to
WHERE {
    ?o :link ?link .
    ?link :label ?label ;
          :path ?path ;
          :to ?to .
}"""            
        if filename == "details":
            query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?o ?path ?label
WHERE {
    ?o :detail ?link .
    ?link :label ?label ;
          :path ?path .
}"""            

        # ----------------------------------------------------------------------
        # Fetch the items
        
        result = self.graph.query(query)
        for s, p, o in result:
            # if any of s p or o are None then cast to empty string
            s = s if s else ""
            p = p if p else ""
            o = o if o else ""
            
            display = f'{s : <150} {p : ^100} {o : >30}'

            preselected = str(s) in preselected_items
            selection = Selection(display, str(s), preselected)
            selections.append(selection)
                        
        return selections

if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # Parse command line arguments

    # Create the parser
    parser = argparse.ArgumentParser(description='Blueprint Configurator')

    # Add the arguments
    arg_choices = ['classes', 'links', 'details']
    parser.add_argument('--item-type', choices=arg_choices, help='The type of items to fetch', required=True)

    # Parse the arguments
    args = parser.parse_args()

    # --------------------------------------------------------------------------
    # Launch the Blueprint Configurator
    
    app = BlueprintConfigurator(item_type=args.item_type)
    app.run()
