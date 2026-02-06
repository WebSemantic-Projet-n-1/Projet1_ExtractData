#!/usr/bin/env python3
"""
Script that contains the functions to respond to the 12 questions/requests
"""

import engine.searchUtils as searchUtils


# Réponse R1
def getFirstTeamInClassment():
    url = 'web_1.0_output/classement.html'

    soup = searchUtils.getContentByUrl(url)

    firstRow = searchUtils.getFirstRowInArray(soup)

    nameOfTheTeam = firstRow.find_all('td')[1].string

    if nameOfTheTeam is not None:
        print('nameOfTheTeam: ' + nameOfTheTeam)
        return nameOfTheTeam

    return None


# Réponse R2
def getNumberOfMatchesPlayedThisSeason():
    url = 'web_1.0_output/statistiques.html'

    soup = searchUtils.getContentByUrl(url)

    sentences = searchUtils.getParagrapheFromDiv(soup, 'stat-box', 0)

    sentence = sentences[0]

    strong = sentence.find("strong").get_text(strip=True)
    numberOfMatchesPlayedThisSeason = sentence.get_text(strip=True).replace(strong, "").strip()

    if numberOfMatchesPlayedThisSeason is not None:
        print(numberOfMatchesPlayedThisSeason)
        return numberOfMatchesPlayedThisSeason
    else:
        return None


# Réponse R3
def getNumberOfGoals():
    url = 'web_1.0_output/statistiques.html'

    soup = searchUtils.getContentByUrl(url)

    sentences = searchUtils.getParagrapheFromDiv(soup, 'stat-box', 0)

    sentence = sentences[1]

    strong = sentence.find("strong").get_text(strip=True)
    numberOfGoalsThisSeason = sentence.get_text(strip=True).replace(strong, "").strip()

    if numberOfGoalsThisSeason is not None:
        print(numberOfGoalsThisSeason)
        return numberOfGoalsThisSeason
    else:
        return None


# Réponse R4
def getTeamWithMostGoals():
    url = 'web_1.0_output/statistiques.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return None
    paras = searchUtils.getParagrapheFromDiv(soup, 'stat-box', 1)
    if not paras or len(paras) < 2:
        return None
    team_p = paras[0]
    goals_p = paras[1]
    team_strong = team_p.find("strong")
    goals_strong = goals_p.find("strong")
    if team_strong is None or goals_strong is None:
        return None
    team = team_p.get_text(strip=True).replace(team_strong.get_text(strip=True), "").strip().strip(":")
    goals = goals_p.get_text(strip=True).replace(goals_strong.get_text(strip=True), "").strip().strip(":")
    if team and goals:
        return f"{team} ({goals} buts)"
    return None


# Réponse R5
def getTeamsOver70Goals():
    url = 'web_1.0_output/classement.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return None

    table = soup.find('table')
    if table is None:
        return None

    rows = table.find_all('tr')

    # On ignore la première ligne (header)
    teams = []

    for row in rows[1:]:  # toutes les lignes sauf l'entête
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        team_name = cols[1].get_text(strip=True)
        goals = cols[2].get_text(strip=True)

        # Vérifie que goals est un nombre et > 70
        try:
            if int(goals) > 70:
                teams.append(team_name)
        except ValueError:
            continue

    return teams if teams else None


# Réponse R6
def getMatchesNovember2008():
    url = 'web_1.0_output/calendrier.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return []
    rows = searchUtils.getTableRows(soup)
    matches = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 4:
            continue
        date = tds[0].get_text(strip=True)
        if "/11/2008" not in date:
            continue
        home = tds[1].get_text(strip=True)
        score_el = tds[2].find(class_='score')
        score = score_el.get_text(strip=True) if score_el else tds[2].get_text(strip=True)
        away = tds[3].get_text(strip=True)
        matches.append(f"{date} | {home} | {score} | {away}")
    return matches


