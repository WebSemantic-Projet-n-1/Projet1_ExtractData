from fastapi import APIRouter
from api.api_commons import normalize
import engine.knowledge_graph as knowledgeGraphEngine
import time

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
            'answer': "Réponse 2"
        },
        {
            'keywords': ['nombre', 'total', 'buts', 'saison'],
            'title': "Question 3",
            'answer': "Réponse 3"
        },
        {
            'keywords': ['équipe', 'marqué', 'le plus de buts'],
            'title': "Question 4",
            'answer': "Réponse 4"
        },
        {
            'keywords': ['équipes', 'marqué', 'plus de 70 buts', 'saison'],
            'title': "Question 5",
            'answer': "Réponse 5"
        },
        {
            'keywords': ['matchs', 'novembre 2008'],
            'title': "Question 6",
            'answer':  "Réponse 6"
        },
        {
            'keywords': ['victoires', 'domicile', 'Manchester', 'United'],
            'title': "Question 7",
            'answer': "Réponse 7"
        },
        {
            'keywords': ['classement', 'équipes', 'nombre', 'victoires', 'extérieur'],
            'title': "Question 8",
            'answer': "Réponse 8"
        },
        {
            'keywords': ['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'],
            'title': "Question 9",
            'answer': "Réponse 9"
        },
        {
            'keywords': ['confrontations', 'historiques', 'championnat'],
            'title': "Question 10",
            'answer': "Réponse 10"
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
        # Call functions if they are callable, otherwise use string answers
        datas = []
        for m in matches:
            if m[0] == max_keywords:
                answer = m[2]() if callable(m[2]) else m[2]
                datas.append({"title": m[1], "answer": answer})
    
    elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "request_question": request_normalized,
        "datas": datas,
        "processing_ms": round(elapsed_ms, 2),
    }