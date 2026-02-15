from fastapi import APIRouter
from api.api_commons import normalize
import engine.knowledge_graph as knowledgeGraphEngine
import time
# #region agent log
import json as _json
_DEBUG_LOG_PATH = "/home/kilo/Work/Cours - UQO/.cursor/debug.log"
def _dlog(location, message, data=None, hypothesisId=None):
    import time as _t
    entry = {"id": f"log_{int(_t.time()*1000)}","timestamp": int(_t.time()*1000),"location": location,"message": message,"data": data or {},"hypothesisId": hypothesisId}
    with open(_DEBUG_LOG_PATH, "a") as f:
        f.write(_json.dumps(entry) + "\n")
# #endregion

router = APIRouter()

@router.get("/api/knowledge-graph/{request_question}")
def read_request(request_question: str):
    t0 = time.perf_counter()
    datas = []

    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': knowledgeGraphEngine.getFirstTeamInClassment
        },
        {
            'keywords': ['matchs', 'joués', 'saison'],
            'title': "Question 2",
            'answer': knowledgeGraphEngine.getNumberOfMatchesPlayedThisSeason
        },
        {
            'keywords': ['nombre', 'total', 'buts', 'saison'],
            'title': "Question 3",
            'answer': knowledgeGraphEngine.getNumberOfGoals
        },
        {
            'keywords': ['équipe', 'marqué', 'le plus de buts'],
            'title': "Question 4",
            'answer': knowledgeGraphEngine.getTeamWithMostGoals
        },
        {
            'keywords': ['équipes', 'marqué', 'plus de 70 buts', 'saison'],
            'title': "Question 5",
            'answer': knowledgeGraphEngine.getTeamsOver70Goals
        },
        {
            'keywords': ['matchs', 'novembre 2008'],
            'title': "Question 6",
            'answer':  knowledgeGraphEngine.getMatchesNovember2008
        },
        {
            'keywords': ['victoires', 'domicile', 'Manchester', 'United'],
            'title': "Question 7",
            'answer': knowledgeGraphEngine.getManchesterUnitedHomeWins
        },
        {
            'keywords': ['classement', 'équipes', 'nombre', 'victoires', 'extérieur'],
            'title': "Question 8",
            'answer': knowledgeGraphEngine.getRankingByAwayWins
        },
        {
            'keywords': ['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'],
            'title': "Question 9",
            'answer': knowledgeGraphEngine.getAwayGoalsForTop6
        },
        {
            'keywords': ['confrontations', 'historiques', 'championnat'],
            'title': "Question 10",
            'answer': knowledgeGraphEngine.getConfrontationsFirstVsThird
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

    # #region agent log
    _dlog("api_knowledge_graph.py:read_request", "matched rules", {"request_normalized": request_normalized, "matched_titles": [m[1] for m in matches]}, hypothesisId="H4")
    # #endregion

    # Choose the rule with the most keywords
    if matches:
        max_keywords = max(m[0] for m in matches)
        # Call functions if they are callable, otherwise use string answers
        datas = []
        for m in matches:
            if m[0] == max_keywords:
                # #region agent log
                _dlog("api_knowledge_graph.py:read_request", "calling function", {"title": m[1], "func_name": m[2].__name__ if callable(m[2]) else "N/A"}, hypothesisId="H4")
                # #endregion
                answer = m[2]() if callable(m[2]) else m[2]
                datas.append({"title": m[1], "answer": answer})
    
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "request_question": request_normalized,
        "datas": datas,
        "processing_ms": round(elapsed_ms, 2),
    }