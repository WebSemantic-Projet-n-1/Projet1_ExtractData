from fastapi import APIRouter
from api.api_commons import normalize
import engine.rdfa as rdfaEngine
import time

router = APIRouter()

@router.get("/api/rdfa/{request_question}")
def read_request(request_question: str):

    rules = [
        {
            'keywords': ['première', 'classement'],
            'title': "Question 1",
            'answer': "Réponse 1"
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
   
    return {
        "request_question": "request_normalized",
        "datas": "datas",
        "processing_ms": 0,
    }