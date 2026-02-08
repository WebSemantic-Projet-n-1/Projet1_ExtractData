import engine.searchEngine as searchEngine
import unicodedata
from fastapi import APIRouter

# Normalizes text (accents, case, etc.)
def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text

router = APIRouter()

@router.get("/requests/{request_question}")
def read_request(request_question: str):

    datas = []

    # region Rules
    # List of rule definitions with function references (not calls, that's important for benchmark)
    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': searchEngine.getFirstTeamInClassment
        },
        {
            'keywords': ['matchs', 'joués', 'saison'],
            'title': "Question 2",
            'answer': searchEngine.getNumberOfMatchesPlayedThisSeason
        },
        {
            'keywords': ['nombre', 'total', 'buts', 'saison'],
            'title': "Question 3",
            'answer': searchEngine.getNumberOfGoals
        },
        {
            'keywords': ['équipe', 'marqué', 'le plus de buts'],
            'title': "Question 4",
            'answer': searchEngine.getTeamWithMostGoals
        },
        {
            'keywords': ['équipes', 'marqué', 'plus de 70 buts', 'saison'],
            'title': "Question 5",
            'answer': searchEngine.getTeamsOver70Goals
        },
        {
            'keywords': ['matchs', 'novembre 2008'],
            'title': "Question 6",
            'answer': searchEngine.getMatchesNovember2008
        },
        {
            'keywords': ['victoires', 'domicile', 'Manchester', 'United'],
            'title': "Question 7",
            'answer': searchEngine.getManchesterUnitedHomeWins
        },
        {
            'keywords': ['classement', 'équipes', 'nombre', 'victoires', 'extérieur'],
            'title': "Question 8",
            'answer': searchEngine.getRankingByAwayWins
        },
        {
            'keywords': ['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'],
            'title': "Question 9",
            'answer': searchEngine.getAwayGoalsForTop6 
        },
        {
            'keywords': ['confrontations', 'historiques', 'championnat'],
            'title': "Question 10",
            'answer': searchEngine.getConfrontationsFirstVsThird  
        },
    ]
    # endregion

    # Normalize rule & request
    rules_normalized = [{
        'keywords': [normalize(w) for w in rule['keywords']],
        'title': rule['title'],
        'answer': rule['answer']
    } for rule in rules]
    request_normalized = normalize(request_question)

    matches = []
    for rule in rules_normalized:
        if all(word in request_normalized for word in rule['keywords']):
            matches.append((len(rule['keywords']), rule['title'], rule['answer']))

    # Choose the rule with the most keywords
    if matches:
        max_keywords = max(m[0] for m in matches)
        datas = [{"title": m[1], "answer": m[2]()} for m in matches if m[0] == max_keywords]

    return {
        "request_question": request_normalized,
        "datas": datas,
    }