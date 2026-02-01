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
        print('content: ' + soup.prettify())
        return soup
    else:
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
        return None

getTitleFromSoup(getContentByUrl('classement.html'))