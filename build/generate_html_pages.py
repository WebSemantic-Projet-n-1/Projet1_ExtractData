#!/usr/bin/env python3
"""
Script de génération de pages HTML statiques (Web 1.0) pour un championnat de football
Auteur: T. E. G. - Web Sémantique
Usage: python generate_html_pages.py
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple

class HTMLPageGenerator:
    """Générateur de pages HTML statiques à partir de la base de données SQLite"""
    
    def __init__(self, db_path: str, championship: str, season: str, output_dir: str, num_teams: int = 6):
        """
        Initialise le générateur
        
        Args:
            db_path: Chemin vers database.sqlite
            championship: Nom du championnat (ex: "England Premier League")
            season: Saison (ex: "2008/2009")
            output_dir: Dossier de sortie pour les pages HTML
            num_teams: Nombre d'équipes à générer (par défaut: 6)
        """
        self.db_path = db_path
        self.championship = championship
        self.season = season
        self.output_dir = output_dir
        self.num_teams = num_teams
        self.conn = None
        
    def connect_db(self):
        """Établit la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"✓ Connexion établie à {self.db_path}")
        
    def close_db(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            print("✓ Connexion fermée")
    
    def create_output_directory(self):
        """Crée le dossier de sortie s'il n'existe pas"""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✓ Dossier de sortie créé/vérifié : {self.output_dir}")
    
    def get_league_and_country_ids(self) -> Tuple[int, int]:
        """Récupère les IDs de la ligue et du pays"""
        cursor = self.conn.cursor()
        
        # Trouver le pays et la ligue
        query = """
        SELECT DISTINCT l.id as league_id, c.id as country_id, l.name as league_name, c.name as country_name
        FROM League l
        JOIN Country c ON l.country_id = c.id
        WHERE l.name = ?
        """
        
        cursor.execute(query, (self.championship,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"Championnat '{self.championship}' non trouvé dans la base de données")
        
        print(f"✓ Championnat trouvé : {result['league_name']} ({result['country_name']})")
        return result['league_id'], result['country_id']
    
    def get_matches(self, league_id: int) -> List[Dict]:
        """Récupère tous les matchs du championnat pour la saison donnée"""
        cursor = self.conn.cursor()
        
        query = """
        SELECT 
            m.id,
            m.date,
            m.season,
            ht.team_long_name as home_team,
            ht.team_short_name as home_team_short,
            at.team_long_name as away_team,
            at.team_short_name as away_team_short,
            m.home_team_goal,
            m.away_team_goal,
            m.home_team_api_id,
            m.away_team_api_id
        FROM Match m
        JOIN Team ht ON m.home_team_api_id = ht.team_api_id
        JOIN Team at ON m.away_team_api_id = at.team_api_id
        WHERE m.league_id = ? AND m.season = ?
        ORDER BY m.date
        """
        
        cursor.execute(query, (league_id, self.season))
        matches = [dict(row) for row in cursor.fetchall()]
        print(f"✓ {len(matches)} matchs récupérés pour la saison {self.season}")
        return matches
    
    def calculate_standings(self, matches: List[Dict]) -> List[Dict]:
        """Calcule le classement à partir des matchs"""
        standings = {}
        
        for match in matches:
            home_team = match['home_team']
            away_team = match['away_team']
            home_goals = match['home_team_goal']
            away_goals = match['away_team_goal']
            
            # Initialiser les équipes si nécessaire
            for team in [home_team, away_team]:
                if team not in standings:
                    standings[team] = {
                        'team': team,
                        'played': 0,
                        'won': 0,
                        'drawn': 0,
                        'lost': 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'goal_difference': 0,
                        'points': 0
                    }
            
            # Mettre à jour les statistiques
            standings[home_team]['played'] += 1
            standings[away_team]['played'] += 1
            standings[home_team]['goals_for'] += home_goals
            standings[home_team]['goals_against'] += away_goals
            standings[away_team]['goals_for'] += away_goals
            standings[away_team]['goals_against'] += home_goals
            
            if home_goals > away_goals:  # Victoire domicile
                standings[home_team]['won'] += 1
                standings[home_team]['points'] += 3
                standings[away_team]['lost'] += 1
            elif home_goals < away_goals:  # Victoire extérieur
                standings[away_team]['won'] += 1
                standings[away_team]['points'] += 3
                standings[home_team]['lost'] += 1
            else:  # Match nul
                standings[home_team]['drawn'] += 1
                standings[away_team]['drawn'] += 1
                standings[home_team]['points'] += 1
                standings[away_team]['points'] += 1
        
        # Calculer la différence de buts
        for team in standings.values():
            team['goal_difference'] = team['goals_for'] - team['goals_against']
        
        # Trier par points, puis différence de buts, puis buts marqués
        sorted_standings = sorted(
            standings.values(),
            key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
            reverse=True
        )
        
        # Ajouter la position
        for i, team in enumerate(sorted_standings, 1):
            team['position'] = i
        
        return sorted_standings
    
    def get_top_teams(self, standings: List[Dict]) -> List[str]:
        """Retourne les noms des n meilleures équipes selon num_teams configuré"""
        return [team['team'] for team in standings[:self.num_teams]]
    
    def get_team_matches(self, matches: List[Dict], team_name: str) -> List[Dict]:
        """Récupère tous les matchs d'une équipe"""
        team_matches = []
        for match in matches:
            if match['home_team'] == team_name or match['away_team'] == team_name:
                team_matches.append(match)
        return team_matches
    
    def calculate_statistics(self, matches: List[Dict]) -> Dict:
        """Calcule les statistiques générales de la saison"""
        total_goals = sum(m['home_team_goal'] + m['away_team_goal'] for m in matches)
        
        # Équipe avec le plus de buts marqués
        goals_scored = {}
        goals_conceded = {}
        
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            
            goals_scored[home] = goals_scored.get(home, 0) + match['home_team_goal']
            goals_scored[away] = goals_scored.get(away, 0) + match['away_team_goal']
            goals_conceded[home] = goals_conceded.get(home, 0) + match['away_team_goal']
            goals_conceded[away] = goals_conceded.get(away, 0) + match['home_team_goal']
        
        top_scorer_team = max(goals_scored.items(), key=lambda x: x[1])
        top_conceded_team = max(goals_conceded.items(), key=lambda x: x[1])
        
        # Plus grande victoire
        biggest_win = max(matches, key=lambda m: abs(m['home_team_goal'] - m['away_team_goal']))
        
        # Match avec le plus de buts
        highest_scoring = max(matches, key=lambda m: m['home_team_goal'] + m['away_team_goal'])
        
        return {
            'total_matches': len(matches),
            'total_goals': total_goals,
            'avg_goals_per_match': round(total_goals / len(matches), 2),
            'top_scorer_team': top_scorer_team,
            'top_conceded_team': top_conceded_team,
            'biggest_win': biggest_win,
            'highest_scoring': highest_scoring
        }
    
    def generate_html_header(self, title: str) -> str:
        """Génère l'en-tête HTML commun"""
        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .nav {{
            background-color: #34495e;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            margin-right: 10px;
            display: inline-block;
        }}
        .nav a:hover {{
            background-color: #2c3e50;
            border-radius: 3px;
        }}
        .stat-box {{
            background-color: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .match-result {{
            padding: 10px;
            margin: 5px 0;
            background-color: white;
            border-left: 4px solid #3498db;
        }}
        .score {{
            font-weight: bold;
            font-size: 1.2em;
            color: #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">Accueil</a>
        <a href="classement.html">Classement</a>
        <a href="calendrier.html">Calendrier</a>
        <a href="statistiques.html">Statistiques</a>
    </div>
"""
    
    def generate_html_footer(self) -> str:
        """Génère le pied de page HTML commun"""
        return """
    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #7f8c8d;">
        <p>Généré pour INF6253 - Web Sémantique | UQO</p>
    </footer>
</body>
</html>"""
    
    def generate_index_page(self, standings: List[Dict], stats: Dict, top_teams: List[str]):
        """Génère la page d'accueil (index.html)"""
        html = self.generate_html_header(f"{self.championship} - Saison {self.season}")
        
        html += f"""
    <h1>{self.championship}</h1>
    <h2>Saison {self.season}</h2>
    
    <div class="stat-box">
        <h3>Vue d'ensemble de la saison</h3>
        <p><strong>Nombre total de matchs :</strong> {stats['total_matches']}</p>
        <p><strong>Nombre total de buts :</strong> {stats['total_goals']}</p>
        <p><strong>Moyenne de buts par match :</strong> {stats['avg_goals_per_match']}</p>
    </div>
    
    <h3>Top {self.num_teams} du classement</h3>
    <table>
        <tr>
            <th>Pos</th>
            <th>Équipe</th>
            <th>Pts</th>
            <th>J</th>
            <th>G</th>
            <th>N</th>
            <th>P</th>
            <th>Diff</th>
        </tr>
"""
        
        # Afficher tous les top N équipes
        for team in standings[:self.num_teams]:
            html += f"""
        <tr>
            <td>{team['position']}</td>
            <td><a href="equipe_{team['team'].replace(' ', '_')}.html">{team['team']}</a></td>
            <td><strong>{team['points']}</strong></td>
            <td>{team['played']}</td>
            <td>{team['won']}</td>
            <td>{team['drawn']}</td>
            <td>{team['lost']}</td>
            <td>{team['goal_difference']:+d}</td>
        </tr>
"""
        
        html += """
    </table>
    
    <h3>Pages disponibles</h3>
    <ul>
        <li><a href="classement.html">Classement complet</a></li>
        <li><a href="calendrier.html">Calendrier de tous les matchs</a></li>
        <li><a href="statistiques.html">Statistiques détaillées</a></li>
"""
        
        # Lister toutes les pages d'équipes générées
        for team_name in top_teams:
            team_file = f"equipe_{team_name.replace(' ', '_')}.html"
            html += f"        <li><a href=\"{team_file}\">Page de {team_name}</a></li>\n"
        
        html += "    </ul>\n"
        html += self.generate_html_footer()
        
        with open(os.path.join(self.output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Page générée : index.html")
    
    def generate_standings_page(self, standings: List[Dict]):
        """Génère la page de classement (classement.html)"""
        html = self.generate_html_header(f"Classement - {self.championship} {self.season}")
        
        html += f"""
    <h1>Classement</h1>
    <h2>{self.championship} - Saison {self.season}</h2>
    
    <table>
        <tr>
            <th>Pos</th>
            <th>Équipe</th>
            <th>Pts</th>
            <th>J</th>
            <th>G</th>
            <th>N</th>
            <th>P</th>
            <th>BP</th>
            <th>BC</th>
            <th>Diff</th>
        </tr>
"""
        
        for team in standings:
            html += f"""
        <tr>
            <td>{team['position']}</td>
            <td><a href="equipe_{team['team'].replace(' ', '_')}.html">{team['team']}</a></td>
            <td><strong>{team['points']}</strong></td>
            <td>{team['played']}</td>
            <td>{team['won']}</td>
            <td>{team['drawn']}</td>
            <td>{team['lost']}</td>
            <td>{team['goals_for']}</td>
            <td>{team['goals_against']}</td>
            <td>{team['goal_difference']:+d}</td>
        </tr>
"""
        
        html += "    </table>\n"
        html += self.generate_html_footer()
        
        with open(os.path.join(self.output_dir, 'classement.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Page générée : classement.html")
    
    def generate_calendar_page(self, matches: List[Dict]):
        """Génère la page de calendrier (calendrier.html)"""
        html = self.generate_html_header(f"Calendrier - {self.championship} {self.season}")
        
        html += f"""
    <h1>Calendrier des matchs</h1>
    <h2>{self.championship} - Saison {self.season}</h2>
    
    <table>
        <tr>
            <th>Date</th>
            <th>Équipe domicile</th>
            <th>Score</th>
            <th>Équipe extérieure</th>
        </tr>
"""
        
        for match in matches:
            date_obj = datetime.strptime(match['date'], '%Y-%m-%d %H:%M:%S')
            date_formatted = date_obj.strftime('%d/%m/%Y')
            
            html += f"""
        <tr>
            <td>{date_formatted}</td>
            <td>{match['home_team']}</td>
            <td class="score">{match['home_team_goal']} - {match['away_team_goal']}</td>
            <td>{match['away_team']}</td>
        </tr>
"""
        
        html += "    </table>\n"
        html += self.generate_html_footer()
        
        with open(os.path.join(self.output_dir, 'calendrier.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Page générée : calendrier.html")
    
    def generate_statistics_page(self, stats: Dict):
        """Génère la page de statistiques (statistiques.html)"""
        html = self.generate_html_header(f"Statistiques - {self.championship} {self.season}")
        
        html += f"""
    <h1>Statistiques de la saison</h1>
    <h2>{self.championship} - Saison {self.season}</h2>
    
    <div class="stat-box">
        <h3>Statistiques générales</h3>
        <p><strong>Nombre total de matchs :</strong> {stats['total_matches']}</p>
        <p><strong>Nombre total de buts :</strong> {stats['total_goals']}</p>
        <p><strong>Moyenne de buts par match :</strong> {stats['avg_goals_per_match']}</p>
    </div>
    
    <div class="stat-box">
        <h3>Meilleure attaque</h3>
        <p><strong>Équipe :</strong> {stats['top_scorer_team'][0]}</p>
        <p><strong>Buts marqués :</strong> {stats['top_scorer_team'][1]}</p>
    </div>
    
    <div class="stat-box">
        <h3>Pire défense</h3>
        <p><strong>Équipe :</strong> {stats['top_conceded_team'][0]}</p>
        <p><strong>Buts encaissés :</strong> {stats['top_conceded_team'][1]}</p>
    </div>
    
    <div class="stat-box">
        <h3>Plus grande victoire</h3>
        <p><strong>Match :</strong> {stats['biggest_win']['home_team']} vs {stats['biggest_win']['away_team']}</p>
        <p><strong>Score :</strong> {stats['biggest_win']['home_team_goal']} - {stats['biggest_win']['away_team_goal']}</p>
        <p><strong>Écart :</strong> {abs(stats['biggest_win']['home_team_goal'] - stats['biggest_win']['away_team_goal'])} buts</p>
    </div>
    
    <div class="stat-box">
        <h3>Match avec le plus de buts</h3>
        <p><strong>Match :</strong> {stats['highest_scoring']['home_team']} vs {stats['highest_scoring']['away_team']}</p>
        <p><strong>Score :</strong> {stats['highest_scoring']['home_team_goal']} - {stats['highest_scoring']['away_team_goal']}</p>
        <p><strong>Total de buts :</strong> {stats['highest_scoring']['home_team_goal'] + stats['highest_scoring']['away_team_goal']}</p>
    </div>
"""
        
        html += self.generate_html_footer()
        
        with open(os.path.join(self.output_dir, 'statistiques.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Page générée : statistiques.html")
    
    def generate_team_page(self, team_name: str, team_matches: List[Dict], standings: List[Dict]):
        """Génère une page pour une équipe spécifique"""
        # Trouver les stats de l'équipe
        team_stats = next((t for t in standings if t['team'] == team_name), None)
        
        html = self.generate_html_header(f"{team_name} - {self.championship} {self.season}")
        
        html += f"""
    <h1>{team_name}</h1>
    <h2>{self.championship} - Saison {self.season}</h2>
    
    <div class="stat-box">
        <h3>Classement et statistiques</h3>
        <p><strong>Position :</strong> {team_stats['position']}e</p>
        <p><strong>Points :</strong> {team_stats['points']}</p>
        <p><strong>Matchs joués :</strong> {team_stats['played']}</p>
        <p><strong>Victoires :</strong> {team_stats['won']}</p>
        <p><strong>Matchs nuls :</strong> {team_stats['drawn']}</p>
        <p><strong>Défaites :</strong> {team_stats['lost']}</p>
        <p><strong>Buts pour :</strong> {team_stats['goals_for']}</p>
        <p><strong>Buts contre :</strong> {team_stats['goals_against']}</p>
        <p><strong>Différence de buts :</strong> {team_stats['goal_difference']:+d}</p>
    </div>
    
    <h3>Tous les matchs</h3>
"""
        
        for match in team_matches:
            date_obj = datetime.strptime(match['date'], '%Y-%m-%d %H:%M:%S')
            date_formatted = date_obj.strftime('%d/%m/%Y')
            
            is_home = match['home_team'] == team_name
            
            if is_home:
                opponent = match['away_team']
                score_text = f"{match['home_team_goal']} - {match['away_team_goal']}"
                location = "Domicile"
                
                if match['home_team_goal'] > match['away_team_goal']:
                    result = "Victoire"
                    result_color = "#27ae60"
                elif match['home_team_goal'] < match['away_team_goal']:
                    result = "Défaite"
                    result_color = "#e74c3c"
                else:
                    result = "Nul"
                    result_color = "#f39c12"
            else:
                opponent = match['home_team']
                score_text = f"{match['away_team_goal']} - {match['home_team_goal']}"
                location = "Extérieur"
                
                if match['away_team_goal'] > match['home_team_goal']:
                    result = "Victoire"
                    result_color = "#27ae60"
                elif match['away_team_goal'] < match['home_team_goal']:
                    result = "Défaite"
                    result_color = "#e74c3c"
                else:
                    result = "Nul"
                    result_color = "#f39c12"
            
            html += f"""
    <div class="match-result" style="border-left-color: {result_color};">
        <p><strong>{date_formatted}</strong> - {location}</p>
        <p><strong>{team_name}</strong> vs <strong>{opponent}</strong></p>
        <p class="score">{score_text}</p>
        <p style="color: {result_color};"><strong>{result}</strong></p>
    </div>
"""
        
        html += self.generate_html_footer()
        
        filename = f"equipe_{team_name.replace(' ', '_')}.html"
        with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Page générée : {filename}")
    
    def generate_all_pages(self):
        """Génère toutes les pages HTML"""
        print("\n" + "="*60)
        print("GÉNÉRATION DES PAGES HTML - WEB 1.0")
        print("="*60 + "\n")
        
        # Connexion et préparation
        self.connect_db()
        self.create_output_directory()
        
        # Récupération des données
        league_id, country_id = self.get_league_and_country_ids()
        matches = self.get_matches(league_id)
        
        if not matches:
            print("Aucun match trouvé pour ce championnat et cette saison")
            self.close_db()
            return
        
        # Calculs
        standings = self.calculate_standings(matches)
        stats = self.calculate_statistics(matches)
        top_teams = self.get_top_teams(standings)
        
        print(f"\n{'='*60}")
        print("GÉNÉRATION DES PAGES")
        print(f"{'='*60}\n")
        
        # Génération des pages
        self.generate_index_page(standings, stats, top_teams)
        self.generate_standings_page(standings)
        self.generate_calendar_page(matches)
        self.generate_statistics_page(stats)
        
        # Pages des équipes sélectionnées
        for team_name in top_teams:
            team_matches = self.get_team_matches(matches, team_name)
            self.generate_team_page(team_name, team_matches, standings)
        
        self.close_db()
        
        total_pages = 4 + len(top_teams)
        print(f"\n{'='*60}")
        print("✓ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
        print(f"{'='*60}")
        print(f"\n{total_pages} pages HTML ont été générées dans : {self.output_dir}")
        print("Pages générées :")
        print("  1. index.html")
        print("  2. classement.html")
        print("  3. calendrier.html")
        print("  4. statistiques.html")
        print(f"  5-{total_pages}. Pages des {len(top_teams)} meilleures équipes :")
        for i, team in enumerate(top_teams, 5):
            print(f"      {i}. equipe_{team.replace(' ', '_')}.html")
        print(f"\nPour visualiser : ouvrez {os.path.join(self.output_dir, 'index.html')} dans un navigateur")


def main():
    """Fonction principale"""
    # Configuration
    DB_PATH = "database.sqlite"  # Chemin vers votre base de données
    CHAMPIONSHIP = "England Premier League"  # Nom du championnat
    SEASON = "2008/2009"  # Saison à générer
    OUTPUT_DIR = "web_1.0_output"  # Dossier de sortie
    NUM_TEAMS = 10  # Nombre d'équipes à générer (modifiable : 4, 6, 8, 10, etc.)
    
    # Vérifier que la base de données existe
    if not os.path.exists(DB_PATH):
        print(f"Erreur : Le fichier {DB_PATH} n'existe pas.")
        print("Veuillez placer database.sqlite dans le même dossier que ce script.")
        return
    
    # Génération
    generator = HTMLPageGenerator(DB_PATH, CHAMPIONSHIP, SEASON, OUTPUT_DIR, NUM_TEAMS)
    generator.generate_all_pages()


if __name__ == "__main__":
    main()