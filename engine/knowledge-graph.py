"""
RDF database operations
"""

import rdflib

g = rdflib.Graph()
g.parse("knowledge_graph.ttl", format="turtle")

# Print all the triples in the graph
for s, p, o in g:
    print(s, p, o)
