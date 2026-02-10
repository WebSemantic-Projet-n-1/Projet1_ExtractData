from fastapi import APIRouter
import engine.web3.engine as web3Engine
import unicodedata

# Normalizes text (accents, case, etc.)
def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text

router = APIRouter()

@router.get("/api/v3/{request_question}")
def read_request(request_question: str):
    datas = []

    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': web3Engine.getFirstTeamInClassment
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

    return {
        "request_question": request_normalized,
        "datas": datas,
    }