"""
Common functions for the API
"""

import unicodedata

# Normalizes text (accents, case, etc.)
def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


REQUESTS_QUESTIONS = {
    "R1": "Quelle équipe est première au classement ?",
    "R2": "Combien de matchs ont été joués cette saison ?",
    "R3": "Quel est le nombre total de buts marqués cette saison ?",
    "R4": "Quelle équipe a marqué le plus de buts ?",
    "R5": "Quelles équipes ont marqué plus de 70 buts cette saison ?",
    "R6": "Quels matchs ont eu lieu en novembre 2008 ?",
    "R7": "Combien de victoires à domicile pour Manchester United ?",
    "R8": "Classement des équipes par nombre de victoires à l'extérieur",
    "R9": "Quelle est la moyenne de buts marqués à l'extérieur par les équipes du Top 6 ?",
    "R10": "Quelles sont les confrontations historiques entre le premier et le troisième du championnat (dates, scores, résultats) ?",
}