from fastapi import APIRouter
import engine.web1 as web1Engine
import unicodedata
import time

# Normalizes text (accents, case, etc.)
def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text

router = APIRouter()

@router.get("/api/v1/{request_question}")
def read_request(request_question: str):
    t0 = time.perf_counter() # start
    datas = []

    # region Rules
    # List of rule definitions with function references (not calls, that's important for benchmark)
    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': web1Engine.getFirstTeamInClassment
        },
        {
            'keywords': ['matchs', 'joués', 'saison'],
            'title': "Question 2",
            'answer': web1Engine.getNumberOfMatchesPlayedThisSeason
        },
        {
            'keywords': ['nombre', 'total', 'buts', 'saison'],
            'title': "Question 3",
            'answer': web1Engine.getNumberOfGoals
        },
        {
            'keywords': ['équipe', 'marqué', 'le plus de buts'],
            'title': "Question 4",
            'answer': web1Engine.getTeamWithMostGoals
        },
        {
            'keywords': ['équipes', 'marqué', 'plus de 70 buts', 'saison'],
            'title': "Question 5",
            'answer': web1Engine.getTeamsOver70Goals
        },
        {
            'keywords': ['matchs', 'novembre 2008'],
            'title': "Question 6",
            'answer': web1Engine.getMatchesNovember2008
        },
        {
            'keywords': ['victoires', 'domicile', 'Manchester', 'United'],
            'title': "Question 7",
            'answer': web1Engine.getManchesterUnitedHomeWins
        },
        {
            'keywords': ['classement', 'équipes', 'nombre', 'victoires', 'extérieur'],
            'title': "Question 8",
            'answer': web1Engine.getRankingByAwayWins
        },
        {
            'keywords': ['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'],
            'title': "Question 9",
            'answer': web1Engine.getAwayGoalsForTop6
        },
        {
            'keywords': ['confrontations', 'historiques', 'championnat'],
            'title': "Question 10",
            'answer': web1Engine.getConfrontationsFirstVsThird
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
    
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "request_question": request_normalized,
        "datas": datas,
        "processing_ms": round(elapsed_ms, 2),
    }