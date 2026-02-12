"""
RDF database operations
"""

import rdflib

g = rdflib.Graph()
g.parse("knowledge_graph.ttl", format="turtle")

def getFirstTeamInClassment():
    """R1 - First team in ranking using Knowledge Graph SPARQL query.

    Executes a SPARQL query over the global RDF graph to retrieve the name
    of the sports team whose position is "1" in the ranking.

    Returns:
        str | None: The name of the first-ranked team if found, otherwise None.
    """
    query = """
    PREFIX schema1: <http://schema.org/>
    SELECT ?teamName ?position
    WHERE {
        ?sportsTeam a schema1:SportsTeam .
        ?sportsTeam schema1:position ?position .
        ?sportsTeam schema1:name ?teamName .
        FILTER(?position = "1").
    }
    LIMIT 1
    """
    results = g.query(query)
    
    for row in results:
       return row.teamName
    
    return None