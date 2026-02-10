#!/usr/bin/env python3
"""
WEB 3.0 SEARCH ENGINE
Exploits RDFa markup in enriched HTML to answer requests.
"""

import engine.engine_utils as utils


# Request R1: first team in classement using RDFa
def getFirstTeamInClassment():
    url = 'web_3.0_rdfa_output/classement_enrichi.html'

    soup = utils.getContentByUrl(url)
    if not soup:
        return None

    # Exploit RDFa: find the first row typed as SportsTeam (schema.org)
    first_team_row = soup.find('tr', attrs={'typeof': 'SportsTeam'})
    if not first_team_row:
        return None

    # Get the team name from the cell with property="name"
    name_cell = first_team_row.find(attrs={'property': 'name'})
    if not name_cell:
        return None

    name = name_cell.get_text(strip=True)
    if name:
        print('nameOfTheTeam:', name)
        return name
    return None
