#!/usr/bin/env python3
"""
WEB 1.0 UTILS FUNCTIONS
Utils functions to navigate in the html pages
"""

from bs4 import BeautifulSoup

# GET = Content, WITH = open/soup
# Utilise open (native) avec le droit lecture (r)
# Utilise beautifulsoup permettant de filtrer avec les balises
# https://beautiful-soup-4.readthedocs.io/en/latest/#output
def getContentByUrl(url):
    with open(url, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    if soup is not None:
        return soup
    else:
        print('content echec ' + url)
        return None

# GET = Title, WITH = soup
# Utilise soup pour récupérer le titre de la page
# https://beautiful-soup-4.readthedocs.io/en/latest/#output
def getTitleFromSoup(soup):
    title = soup.title.string

    if title is not None:
        print('title: ' + title)
        return title
    else:
        print('title echec')
        return None


# GET = firstRow usually, WITH soup
# Récupère la première ligne utile (hors en tête) dans un table
# https://stackoverflow.com/questions/39440830/attributeerror-nonetype-object-has-no-attribute-find-all-many-of-the-other
def getFirstRowInArray(soup):
    rows = soup.find('table').find_all('tr')

    # On vérifie qu'il a bien récupéré au moins deux lignes
    if len(rows) >= 2:
        # on récupère la seconde ligne qu'on appelle firstRow car c'est la première de valeur
        firstRow = rows[1]

        return firstRow

    return None

# GET = balise P, WITH soup, className, Number
# ClassName de la DIV ; Number en array 0-1-2 etc...
# Sources : Reddit, google
def getParagrapheFromDiv(soup, className = 'NoClass', number = 0):
    statsbox = soup.find_all('div', class_=className)

    if statsbox is not None:
        return statsbox[number].find_all("p")
    else:
        return None

def getTableRows(soup):
    table = soup.find('table')
    if table is None:
        return []
    rows = table.find_all('tr')
    return rows[1:] if len(rows) >= 2 else []

def getMatchResultDivs(soup):
    """Return all div.match-result elements (for equipe pages)."""
    return soup.find_all('div', class_='match-result')
