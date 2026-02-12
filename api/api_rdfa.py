from fastapi import APIRouter
from api.api_commons import normalize
import engine.rdfa as rdfaEngine
import time

router = APIRouter()

@router.get("/api/rdfa/{request_question}")
def read_request(request_question: str):
    t0 = time.perf_counter()
    datas = []

    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': rdfaEngine.getFirstTeamInClassment
        },
        {
            'keywords': ['matchs', 'joués', 'saison'],
            'title': "Question 2",
            'answer': rdfaEngine.getNumberOfMatchesPlayedThisSeason
        },
        {
            'keywords': ['nombre', 'total', 'buts', 'saison'],
            'title': "Question 3",
            'answer': rdfaEngine.getNumberOfGoals
        },
        {
            'keywords': ['équipe', 'marqué', 'le plus de buts'],
            'title': "Question 4",
            'answer': rdfaEngine.getTeamWithMostGoals
        },
        {
            'keywords': ['équipes', 'marqué', 'plus de 70 buts', 'saison'],
            'title': "Question 5",
            'answer': rdfaEngine.getTeamsOver70Goals
        },
        {
            'keywords': ['matchs', 'novembre 2008'],
            'title': "Question 6",
            'answer':  rdfaEngine.getMatchesNovember2008
        },
        {
            'keywords': ['victoires', 'domicile', 'Manchester', 'United'],
            'title': "Question 7",
            'answer': rdfaEngine.getManchesterUnitedHomeWins
        },
        {
            'keywords': ['classement', 'équipes', 'nombre', 'victoires', 'extérieur'],
            'title': "Question 8",
            'answer': rdfaEngine.getRankingByAwayWins
        },
        {
            'keywords': ['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'],
            'title': "Question 9",
            'answer': rdfaEngine.getAwayGoalsForTop6
        },
        {
            'keywords': ['confrontations', 'historiques', 'championnat'],
            'title': "Question 10",
            'answer': rdfaEngine.getConfrontationsFirstVsThird
        },
    ]
   
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