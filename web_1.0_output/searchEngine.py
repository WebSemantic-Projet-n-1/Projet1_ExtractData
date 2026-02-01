from bs4 import BeautifulSoup

# GET = Content, WITH = open/soup
# Utilise open (native) avec le droit lecture (r)
# Utilise beautifulsoup permettant de filtrer avec les balises
# https://beautiful-soup-4.readthedocs.io/en/latest/#output
def getContentByUrl(url):

    print(url)

    with open(url, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    if soup is not None:
        print('content: ' + soup.prettify())
        return soup
    else:
        print('content echec')
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


# Réponse R1
def getFirstTeamInClassment():
    url = 'classement.html'

    soup = getContentByUrl(url)

    firstRow = getFirstRowInArray(soup)

    nameOfTheTeam = firstRow.find_all('td')[1].string

    if nameOfTheTeam is not None:
        print('nameOfTheTeam: ' + nameOfTheTeam)
        return nameOfTheTeam

    return None



# R1
# getFirstTeamInClassment()