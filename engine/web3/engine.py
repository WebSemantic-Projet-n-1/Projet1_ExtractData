#!/usr/bin/env python3
"""
RDF SEARCH ENGINE
Exploits RDFa markup in enriched HTML to answer requests.
"""

import engine.engine_utils as utils
import re

BASE_RDFA_DIR = "web_3.0_rdfa_output"

EQUIPE_FILES = [
    "equipe_Arsenal_enrichi.html",
    "equipe_Aston_Villa_enrichi.html",
    "equipe_Chelsea_enrichi.html",
    "equipe_Everton_enrichi.html",
    "equipe_Fulham_enrichi.html",
    "equipe_Liverpool_enrichi.html",
    "equipe_Manchester_City_enrichi.html",
    "equipe_Manchester_United_enrichi.html",
    "equipe_Tottenham_Hotspur_enrichi.html",
    "equipe_West_Ham_United_enrichi.html",
]

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


"""
R2 - Number of matches played this season
Using the RDFa attribute numberOfGames from the stat-box div
"""

def getNumberOfMatchesPlayedThisSeason():
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
        if "Nombre total de matchs" in p.get_text():
            nb = _extract_first_int(p.get_text())
            return str(nb) if nb is not None else None
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

"""
R4 - Team with most goals
Find the team with most goals using goalsScored property from EQUIPE_FILES
"""
def getTeamWithMostGoals():
    best_team = None
    best_goals = -1

    for filename in EQUIPE_FILES:
        url = f"{BASE_RDFA_DIR}/{filename}"
        soup = utils.getContentByUrl(url)
        if not soup:
            continue

        name_el = soup.find(attrs={"property": "name"})
        goals_el = soup.find(attrs={"property": "goalsScored"})
        if name_el is None or goals_el is None:
            continue

        team_name = name_el.get_text(strip=True)
        goals = _extract_first_int(goals_el.get_text(strip=True))
        if team_name and goals is not None and goals > best_goals:
            best_goals = goals
            best_team = team_name

    if best_team is not None and best_goals >= 0:
        return f"{best_team} ({best_goals} buts)"
    return None

