from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.events import Mount
from textual.widgets import Footer, Header, Pretty, SelectionList
from textual.widgets.selection_list import Selection

import rdflib

# ------------------------------------------------------------------------------
# Textual App (the TUI)

class BlueprintConfigurator(App[None]):
    CSS_PATH = "layout.tcss"
    items: list[str]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield SelectionList[str](*self.items,)
            yield Pretty([])
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Items found"
        self.query_one(Pretty).border_title = "Selected items"

    def set_items(self, items: list[str]) -> None:
        selections = []
        for item in items:
            selections.append(Selection(item, item, True))
        self.items = selections

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.query_one(Pretty).update(self.query_one(SelectionList).selected)

# ------------------------------------------------------------------------------
# Methods for fetching items from the ttl files

def fetch_items() -> list[str]:
    rdf = rdflib.Graph()
    rdf.parse("_classes.ttl", format="ttl")

    items = []
    for s, p, o in rdf.triples((None, None, None)):
        label = rdflib.term.URIRef('http://schema.example.org/blueprint-ui-config-initializer/label')

        if p == label:
            items.append(str(o))
    
    return items

if __name__ == "__main__":
    items = fetch_items()

    app = BlueprintConfigurator()
    app.set_items(items)
    app.run()
