# ------------------------------------------------------------------------------
# Constants

prefix = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX blueprintMetaShapes: <https://ld.flux.zazuko.com/shapes/metadata/>
PREFIX blueprintMetaLink: <https://ld.flux.zazuko.com/link/metadata/>
PREFIX blueprint: <https://flux.described.at/>
"""

# ------------------------------------------------------------------------------
# Construction queries

def get_construct_query(item_type, selected_items):
    if item_type == "classes":
        query = get_class_construct(selected_items)
    if item_type == "links":
        query = get_link_construct(selected_items)
    if item_type == "details":
        query = get_detail_construct(selected_items)
    return query

def get_class_construct(selected_items):
    selected_items_str = " ".join([f'"{item}"' for item in selected_items])

    query = f"""{prefix}    
CONSTRUCT {{
    ?subject rdf:type :Class ;
             :colorIndex ?colorIndex ;
             :icon ?icon ;
             :label ?label ;
             :searchPrio ?searchPrio .
}}
WHERE {{
    ?subject rdf:type :Class ;
             :colorIndex ?colorIndex ;
             :icon ?icon ;
             :label ?label ;
             :searchPrio ?searchPrio .
    VALUES ?label {{ {selected_items_str} }}
}}
"""
    return query
    

def get_link_construct(selected_items):
    selected_items_str = " ".join([f'<{item}>' for item in selected_items])

    query = f"""{prefix}    
CONSTRUCT {{
    ?subject :link [
        :label ?label ;
        :path ?path ;
        :to ?to
    ] .
}}
WHERE {{
    ?subject :link [
        :label ?label ;
        :path ?path ;
        :to ?to
    ] .
    VALUES ?path {{ {selected_items_str} }}
}}"""

    return query

def get_detail_construct(selected_items):
    selected_items_str = " ".join([f'<{item}>' for item in selected_items])
    
    query = f"""{prefix}
CONSTRUCT {{
    ?subject :detail [
        :label ?detailLabel ;
        :order ?detailOrder ;
        :path ?detailPath
    ] ;
    :label ?groupLabel ;
    :order ?groupOrder .
    ?classEntity :detailGroup ?subject .
}}
WHERE {{
    ?subject :detail ?detailNode ;
             :label ?groupLabel ;
             :order ?groupOrder .
             
    ?detailNode :label ?detailLabel ;
                :order ?detailOrder ;
                :path ?detailPath .
                
    VALUES ?detailPath {{ {selected_items_str} rdfs:label }}

    OPTIONAL {{
        ?classEntity :detailGroup ?subject .
    }}
}}
"""
    return query

# ------------------------------------------------------------------------------
# Display queries

def get_display_query(item_type):
    if item_type == "classes":
        query = get_class_display()
    if item_type == "links":
        query = get_link_display()
    if item_type == "details":
        query = get_detail_display()
    return query

def get_class_display():
    query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?s ?p ?o
WHERE {
    ?s :label ?o .
}"""
    return query

def get_link_display():
    query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?label ?to ?path
WHERE {
    ?o :link ?link .
    ?link :label ?label ;
          :path ?path ;
          :to ?to .
}"""
    return query

def get_detail_display():
    query = """PREFIX : <http://schema.example.org/blueprint-ui-config-initializer/>
SELECT ?path ?o ?label
WHERE {
    ?o :detail ?link .
    ?link :label ?label ;
          :path ?path .
}"""
    return query

