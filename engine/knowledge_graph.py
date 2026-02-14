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


def getTeamWithMostGoals():
    """R4 - Team with most goals using Knowledge Graph SPARQL query.
    
    Returns:
        str: The name of the team with most goals, or a message if no team found.
    """
    query = """
    PREFIX schema1: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?teamName ?goals
    WHERE {
        ?sportsTeam a schema1:SportsTeam .
        ?sportsTeam schema1:goalsScored ?goals .
        ?sportsTeam schema1:name ?teamName .
    }
    ORDER BY DESC(xsd:integer(?goals))
    LIMIT 1
    """
    results = g.query(query)
    for row in results:
        return f"{row.teamName} ({row.goals} buts)"
    return "Aucune équipe trouvée"


def getMatchesNovember2008():
    """R6 - Matches played in November 2008 using Knowledge Graph SPARQL query.

    Returns:
        str: A formatted string containing all matches played in November 2008,
             or a message if no matches found.
    """

    query = """
    PREFIX schema1: <http://schema.org/>
    SELECT ?matchDate ?homeTeamName ?score ?awayTeamName
    WHERE {
        ?event a schema1:SportsEvent .
        ?event schema1:startDate ?matchDate .
        ?event schema1:score ?score .
        ?event schema1:homeTeam ?homeTeam .
        ?event schema1:awayTeam ?awayTeam .
        ?homeTeam schema1:name ?homeTeamName .
        ?awayTeam schema1:name ?awayTeamName .
        FILTER(REGEX(STR(?matchDate), "/11/2008"))
    }
    ORDER BY ?matchDate
    """

    results = g.query(query)
    matches = []
    
    for row in results:
        match_info = f"{row.matchDate}: {row.homeTeamName} vs {row.awayTeamName} ({row.score})"
        matches.append(match_info)
    
    if matches:
        return f"{len(matches)} matchs en novembre 2008:\n" + "\n".join(matches)
    else:
        return "Aucun match trouvé en novembre 2008"



def getTeamsOver70Goals():
    """R5 - Teams over 70 goals using Knowledge Graph SPARQL query.

    Returns:
        str: A formatted string containing all teams with more than 70 goals,
             or a message if no teams found.
    """

    query = """
    PREFIX schema1: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?teamName
    WHERE {
        ?sportsTeam a schema1:SportsTeam .
        ?sportsTeam schema1:goalsScored ?goals .
        FILTER(xsd:integer(?goals) > 70)
        ?sportsTeam schema1:name ?teamName .
    }
    """
    results = g.query(query)
    teams = []
    for row in results:
        teams.append(row.teamName)
    return teams if teams else None



# Réponse R7
def getManchesterUnitedHomeWins():
    """R7 - Manchester United home wins using Knowledge Graph SPARQL query.

    Returns:
        int: The total number of wins for Manchester United at home.
    """

    query = """
    PREFIX schema1: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT (COUNT(?event) AS ?numberOfWins)
    WHERE {
        ?event a schema1:SportsEvent .
        ?event schema1:homeTeam ?homeTeam .
        ?homeTeam schema1:name "Manchester United" .
        ?event schema1:score ?score .
        BIND(xsd:integer(STRBEFORE(?score, " - ")) AS ?homeGoals)
        BIND(xsd:integer(STRAFTER(?score, " - ")) AS ?awayGoals)
        FILTER(?homeGoals > ?awayGoals)
    }
    """
   
    results = g.query(query)
    for row in results:
        return int(row.numberOfWins)
    return 0


def getAwayGoalsForTop6():
    """R9 - Average number of goals scored away by the Top 6 teams using Knowledge Graph SPARQL query.
    
    Returns:
        str: Formatted string with average and individual team statistics.
    """

    # Get top 6 teams
    top6_query = """
    PREFIX schema1: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?teamName ?position
    WHERE {
        ?team a schema1:SportsTeam .
        ?team schema1:name ?teamName .
        ?team schema1:position ?position .
        FILTER(xsd:integer(?position) <= 6)
    }
    ORDER BY xsd:integer(?position)
    LIMIT 6
    """
    
    top6_results = g.query(top6_query)
    top6_teams = {}
    
    for row in top6_results:
        team_name = str(row.teamName)
        position = int(row.position)
        top6_teams[team_name] = {"position": position, "goals": 0}
    
    if not top6_teams:
        return "Aucune donnée disponible pour le Top 6"
    
    # Get matches for each team
    for team_name in top6_teams.keys():
        matches_query = f"""
        PREFIX schema1: <http://schema.org/>
        
        SELECT ?score
        WHERE {{
            ?event a schema1:SportsEvent .
            ?event schema1:awayTeam ?awayTeamNode .
            ?awayTeamNode schema1:name "{team_name}" .
            ?event schema1:score ?score .
        }}
        """
        
        matches_results = g.query(matches_query)
        
        for row in matches_results:
            score_str = str(row.score)
            try:
                parts = score_str.split(' - ')
                if len(parts) == 2:
                    away_goals = int(parts[1].strip())
                    top6_teams[team_name]["goals"] += away_goals
            except (ValueError, IndexError):
                continue
    
    # Calculate average
    total_goals = sum(team["goals"] for team in top6_teams.values())
    avg = total_goals / len(top6_teams)
    
    # Format output
    result_lines = [
        "Buts marqués à l'extérieur par les équipes du Top 6 :",
        f"Moyenne (sur {len(top6_teams)} équipes) : {avg:.2f} buts"
    ]
    
    # Sort by position
    sorted_teams = sorted(top6_teams.items(), key=lambda x: x[1]["position"])
    for team_name, data in sorted_teams:
        result_lines.append(f"{team_name} : {data['goals']} buts")
    
    return "\n".join(result_lines)