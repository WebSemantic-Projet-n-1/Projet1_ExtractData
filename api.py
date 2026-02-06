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

    rules = [
        (['première', 'classement'], "Question 1", searchEngine.getFirstTeamInClassment()),
        (['matchs', 'joués', 'saison'], "Question 2", searchEngine.getNumberOfMatchesPlayedThisSeason()),
        (['nombre', 'total', 'buts', 'saison'], "Question 3", searchEngine.getNumberOfGoals()),
        (['équipe', 'marqué', 'le plus de buts'], "Question 4", searchEngine.getTeamWithMostGoals()),
        (['équipes', 'marqué', 'plus de 70 buts', 'saison'], "Question 5", searchEngine.getTeamsOver70Goals()),
        (['matchs', 'novembre 2008'], "Question 6", searchEngine.getMatchesNovember2008()),
        (['victoires', 'domicile', 'Manchester', 'United'], "Question 7", searchEngine.getManchesterUnitedHomeWins()),
        (['classement', 'équipes', 'nombre', 'victoires', 'extérieur'], "Question 8", searchEngine.getRankingByAwayWins()),
        (['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'], "Question 9", "Réponse"),
        (['confrontations', 'historiques', 'championnat'], "Question 10", "Réponse"),
    ]
    
    # Normalize rule & request
    rules_normalized = [([normalize(w) for w in words], title, answer) for words, title, answer in rules]
    request_normalized = normalize(request_question)

    matches = []  
    for words_norm, title, answer in rules_normalized:
        if all(word in request_normalized for word in words_norm):
            matches.append((len(words_norm), title, answer))

    # Chose the rule with the most keywords
    if matches:
        max_keywords = max(m[0] for m in matches)
        datas = [{"title": m[1], "answer": m[2]} for m in matches if m[0] == max_keywords]

    return {
        "request_question": request_normalized,
        "datas": datas,
    }