"""
RDF database operations
"""

import rdflib

g = rdflib.Graph()
g.parse("knowledge_graph.ttl", format="turtle")

def getFirstTeamInClassment():
    """R1 - First team in ranking using Knowledge Graph SPARQL query.

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


def getNumberOfMatchesPlayedThisSeason():
    """R2 - Number of matches played this season using Knowledge Graph SPARQL query.

    Returns:
        int: The total count of SportsEvent entries (matches) in the knowledge graph.
    """

    query = """
    PREFIX schema1: <http://schema.org/>
    SELECT (COUNT(?event) AS ?numberOfMatches)
    WHERE {
        ?event a schema1:SportsEvent .
    }
    """
    results = g.query(query)
    for row in results:
        return int(row.numberOfMatches)
    return 0


def getNumberOfGoals():
    """R3 - Number of goals using Knowledge Graph SPARQL query.

    Returns:
        int: The total count of goals scored by all teams in the knowledge graph.
    """

    query = """
    PREFIX schema1: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT (SUM(xsd:integer(?goals)) AS ?numberOfGoals)
    WHERE {
        ?sportsTeam a schema1:SportsTeam .
        ?sportsTeam schema1:goalsScored ?goals .
    }
    """
    results = g.query(query)
    for row in results:
        return int(row.numberOfGoals) if row.numberOfGoals else 0
    return 0