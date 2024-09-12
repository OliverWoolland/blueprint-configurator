from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, SelectionList, Static, Log
from textual.widgets.selection_list import Selection

import argparse
import rdflib

import queries

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
            yield Log()
        yield Footer()

    # --------------------------------------------------------------------------
    # Events
    
    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Items retrieved from the database"

        log = self.query_one(Log)
        log.write_line("Welcome to the Blueprint Configurator!")

    # --------------------------------------------------------------------------
    # Actions
        
    def action_quit(self) -> None:

        log = self.query_one(Log)
        
        # ----------------------------------------------------------------------
        # Write out config as user has specified

        # Get selected items and produce a space seperated string with them
        selected_items = self.query_one(SelectionList).selected

        # Fetch the query based on the item type
        query = ""
        if self.item_type == "classes":
            query = queries.get_class_construct(selected_items)
        elif self.item_type == "links":
            query = queries.get_link_construct(selected_items)
        elif self.item_type == "details":
            query = queries.get_detail_construct(selected_items)

        log.write_line(query)

        # Execute the query and write out the result
        result = self.graph.query(query)

        # Make graph from result and serialize it to a file
        result.serialize(f"{self.item_type}.ttl", format="turtle")

        serial = result.serialize(format="turtle").decode("utf-8")
        log.write_line(serial)
        # ----------------------------------------------------------------------
        # Write out config file to configure preselection of items
        
        with open(f"{self.item_type}.conf", "w") as f:
           for item in selected_items:
               f.write(f"{item}\n")

        # ----------------------------------------------------------------------
        # Quit the app        
              
        #self.exit()

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
        # Configure the display and query based on the item type
        
        query = queries.get_display_query(self.item_type)

        # ----------------------------------------------------------------------
        # Fetch the items
        
        result = self.graph.query(query)

        selections = []
        for s, p, o in result:
            # if any of s p or o are None then cast to empty string
            s = s if s else ""
            p = p if p else ""
            o = o if o else ""
            
            display = f'{s : <150} {p : ^100} {o : >30}'

            preselected = str(o) in preselected_items
            selection = Selection(display, str(o), preselected)
            selections.append(selection)
                        
        return selections

if __name__ == "__main__":
    # --------------------------------------------------------------------------
    # Parse command line arguments

    # Create the parser
    parser = argparse.ArgumentParser(description='Blueprint Configurator')

    # Add the arguments
    arg_choices = ['classes', 'links', 'details']
    parser.add_argument('--item-type', choices=arg_choices, help='The type of items to fetch', requried=True)

    # Parse the arguments
    args = parser.parse_args()

    # --------------------------------------------------------------------------
    # Launch the Blueprint Configurator
    
    app = BlueprintConfigurator(item_type=args.item_type)
    app.run()
