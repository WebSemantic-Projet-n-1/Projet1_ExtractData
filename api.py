import engine.searchEngine as searchEngine
from fastapi import APIRouter

router = APIRouter()

@router.get("/requests/{request_question}")
def read_request(request_question: str):

    datas = []

    rules = [
        (['première', 'classement'], "Question 1", searchEngine.getFirstTeamInClassment()),
        (['matchs', 'joués', 'saison'], "Question 2", searchEngine.getNumberOfMatchesPlayedThisSeason()),
        (['nombre', 'total', 'buts', 'saison'], "Question 3", "Réponse"),
        (['équipe', 'marqué', 'le plus de buts'], "Question 4", "Réponse"),
        (['équipes', 'marqué', 'plus de 70 buts', 'saison'], "Question 5", "Réponse"),
        (['matchs', 'novembre 2008'], "Question 6", "Réponse"),
        (['victoires', 'domicile', 'Manchester', 'United'], "Question 7", "Réponse"),
        (['classement', 'équipes', 'nombre', 'victoires', 'extérieur'], "Question 8", "Réponse"),
        (['moyenne', 'buts marqués', 'extérieur', 'équipes', 'top 6'], "Question 9", "Réponse"),
        (['confrontations', 'historiques', 'championnat'], "Question 10", "Réponse"),
    ]

    # Filtrage générique
    for words, title, answer in rules:
        if all(word in request_question for word in words):
            datas.append({
                "title": title,
                "answer": answer
            })

    return {
        "request_question": request_question,
        "datas": datas,
    }