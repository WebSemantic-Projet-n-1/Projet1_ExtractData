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
