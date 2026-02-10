#!/usr/bin/env python3
"""
WEB 3.0 SEARCH ENGINE
Exploits RDFa markup in enriched HTML to answer requests.
"""

import engine.engine_utils as utils
import re

BASE_RDFA_DIR = "web_3.0_rdfa_output"

def _extract_first_int(text):
    if text is None:
        return None
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None

# Request R1: first team in classement using RDFa
def getFirstTeamInClassment():
    url = f"{BASE_RDFA_DIR}/classement_enrichi.html"

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

# Réponse R3
def getNumberOfGoals():
    url = f"{BASE_RDFA_DIR}/statistiques_enrichi.html"
    soup = utils.getContentByUrl(url)
    if not soup:
        return None

    # No RDFa attribute for this
    boxes = soup.find_all("div", class_="stat-box")
    if not boxes:
        return None
    first_box = boxes[0]
    for p in first_box.find_all("p"):
        if "Nombre total de buts" in p.get_text():
            nb = _extract_first_int(p.get_text())
            return str(nb) if nb is not None else None

    return None