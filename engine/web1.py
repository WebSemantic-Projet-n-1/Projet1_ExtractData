#!/usr/bin/env python3
"""
WEB 1.0 SEARCH ENGINE
Script that contains the functions to respond to the 12 questions/requests 
"""

import engine.engine_utils as searchUtils

BASE_WEB1_DIR = "web_1.0_output"

# Teams ("equipe_*.html" files)
EQUIPE_FILES = [
    'equipe_Arsenal.html',
    'equipe_Aston_Villa.html',
    'equipe_Chelsea.html',
    'equipe_Everton.html',
    'equipe_Fulham.html',
    'equipe_Liverpool.html',
    'equipe_Manchester_City.html',
    'equipe_Manchester_United.html',
    'equipe_Tottenham_Hotspur.html',
    'equipe_West_Ham_United.html',
]

# Réponse R1
def getFirstTeamInClassment():
    url = BASE_WEB1_DIR + '/classement.html'

    soup = searchUtils.getContentByUrl(url)

    firstRow = searchUtils.getFirstRowInArray(soup)

    nameOfTheTeam = firstRow.find_all('td')[1].string

    if nameOfTheTeam is not None:
        print('nameOfTheTeam: ' + nameOfTheTeam)
        return nameOfTheTeam

    return None


# Réponse R2
def getNumberOfMatchesPlayedThisSeason():
    url = BASE_WEB1_DIR + '/statistiques.html'

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
    url = BASE_WEB1_DIR + '/statistiques.html'

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
    url = BASE_WEB1_DIR + '/statistiques.html'
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
    url = BASE_WEB1_DIR + '/classement.html'
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
        goals = cols[7].get_text(strip=True)

        # Vérifie que goals est un nombre et > 70
        try:
            if int(goals) > 70:
                teams.append(team_name)
        except ValueError:
            continue

    return teams if teams else None


# Réponse R6
def getMatchesNovember2008():
    url = BASE_WEB1_DIR + '/calendrier.html'
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


# Réponse R7
def getManchesterUnitedHomeWins():
    url = BASE_WEB1_DIR + '/equipe_Manchester_United.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return None
    divs = searchUtils.getMatchResultDivs(soup)
    count = 0
    for div in divs:
        text = div.get_text()
        if "Domicile" in text and "Victoire" in text:
            count += 1
    return count

# Réponse R8
def getRankingByAwayWins():
    base = BASE_WEB1_DIR
    results = []
    for filename in EQUIPE_FILES:
        path = base + '/' + filename
        soup = searchUtils.getContentByUrl(path)
        if soup is None:
            continue
        h1 = soup.find('h1')
        team_name = h1.get_text(strip=True) if h1 else "Inconnu"
        divs = searchUtils.getMatchResultDivs(soup)
        away_wins = 0
        for d in divs:
            text = d.get_text()
            if "Extérieur" in text and "Victoire" in text:
                away_wins += 1
        results.append((team_name, away_wins))
    results.sort(key=lambda x: x[1], reverse=True)
    return [f"{i + 1}. {name} - {n} victoires" for i, (name, n) in enumerate(results)]

def getTop6Teams():
    url = BASE_WEB1_DIR + '/classement.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return []

    rows = searchUtils.getTableRows(soup)
    teams = []

    for row in rows[:6]:  # les 6 premières lignes du tableau
        tds = row.find_all('td')
        if len(tds) < 2:
            continue
        team_name = tds[1].get_text(strip=True)
        teams.append(team_name)

    return teams

# Réponse R9
def getAwayGoalsForTop6():
    top6 = getTop6Teams()
    url = BASE_WEB1_DIR + '/calendrier.html'
    soup = searchUtils.getContentByUrl(url)
    if soup is None:
        return ''

    rows = searchUtils.getTableRows(soup)

    away_goals = {team: 0 for team in top6}

    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 4:
            continue

        score_el = tds[2].find(class_='score')
        score = score_el.get_text(strip=True) if score_el else tds[2].get_text(strip=True)
        away = tds[3].get_text(strip=True)

        if "-" not in score:
            continue

        home_goals, away_goals_nb = score.split("-")
        away_goals_nb = int(away_goals_nb.strip())

        if away in away_goals:
            away_goals[away] += away_goals_nb

    # Calculate average
    avg = sum(away_goals.values()) / len(top6) if top6 else 0

    result_lines = [
        "Buts marqués à l'extérieur par les équipes du Top 6 :",
        f"Moyenne (sur 6 équipes) : {avg:.2f} buts"
    ]
    for team, goals in away_goals.items():
        result_lines.append(f"{team} : {goals} buts")

    return "\n".join(result_lines)


def getConfrontationsFirstVsThird():
    url_rank = BASE_WEB1_DIR + '/classement.html'
    soup_rank = searchUtils.getContentByUrl(url_rank)
    if soup_rank is None:
        return "Erreur : classement introuvable."

    rows = searchUtils.getTableRows(soup_rank)
    if len(rows) < 3:
        return "Erreur : classement incomplet."

    first_team = rows[0].find_all('td')[1].get_text(strip=True)
    third_team = rows[2].find_all('td')[1].get_text(strip=True)

    url_cal = 'web_1.0_output/calendrier.html'
    soup_cal = searchUtils.getContentByUrl(url_cal)
    if soup_cal is None:
        return "Erreur : calendrier introuvable."

    rows_cal = searchUtils.getTableRows(soup_cal)

    confrontations = []

    for row in rows_cal:
        tds = row.find_all('td')
        if len(tds) < 4:
            continue

        date = tds[0].get_text(strip=True)
        home = tds[1].get_text(strip=True)
        score_el = tds[2].find(class_='score')
        score = score_el.get_text(strip=True) if score_el else tds[2].get_text(strip=True)
        away = tds[3].get_text(strip=True)

        teams = {home, away}
        if first_team in teams and third_team in teams:
            if "-" in score:
                home_goals, away_goals = score.split("-")
                home_goals = int(home_goals.strip())
                away_goals = int(away_goals.strip())

                if home == first_team:
                    if home_goals > away_goals:
                        result = "Victoire du premier"
                    elif home_goals < away_goals:
                        result = "Défaite du premier"
                    else:
                        result = "Match nul"
                else:  # first_team est à l'extérieur
                    if away_goals > home_goals:
                        result = "Victoire du premier"
                    elif away_goals < home_goals:
                        result = "Défaite du premier"
                    else:
                        result = "Match nul"
            else:
                result = "Score invalide"

            confrontations.append(f"{date} | {home} | {score} | {away} | {result}")

    if not confrontations:
        return f"Aucune confrontation trouvée entre {first_team} et {third_team}."

    return "\n".join(confrontations)
