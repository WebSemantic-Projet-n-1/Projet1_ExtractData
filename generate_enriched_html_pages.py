#!/usr/bin/env python3
"""
Script d'enrichissement des pages HTML avec métadonnées sémantiques
Transforme les pages HTML statiques (Web 1.0) en pages enrichies (Web 3.0)
Supporte RDFa et JSON-LD
"""

import os
from bs4 import BeautifulSoup
import json
from typing import Dict, List

class HTMLEnricher:
    """Enrichit les pages HTML avec des métadonnées sémantiques"""
    
    def __init__(self, input_dir: str, output_dir: str, format: str = "rdfa"):
        """
        Initialise l'enrichisseur
        
        Args:
            input_dir: Dossier contenant les pages HTML statiques
            output_dir: Dossier de sortie pour les pages enrichies
            format: Format d'enrichissement ('rdfa' ou 'jsonld')
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.format = format.lower()
        
        if self.format not in ['rdfa', 'jsonld']:
            raise ValueError("Format doit être 'rdfa' ou 'jsonld'")
    
    def create_output_directory(self):
        """Crée le dossier de sortie"""
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✓ Dossier de sortie créé : {self.output_dir}")
    
    def update_links(self, soup):
        """
        Met à jour tous les liens href pour pointer vers les pages enrichies
        
        Args:
            soup: Objet BeautifulSoup de la page
        """
        # Trouver tous les liens <a>
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            
            # Ne modifier que les liens vers fichiers HTML locaux (pas les URLs externes)
            if href.endswith('.html') and not href.startswith('http'):
                # Remplacer .html par _enrichi.html
                new_href = href.replace('.html', '_enrichi.html')
                link['href'] = new_href
    
    def update_internal_links(self, soup):
        """
        Met à jour tous les liens internes pour pointer vers les pages enrichies
        Par exemple : equipe_Chelsea.html -> equipe_Chelsea_enrichi.html
        """
        # Trouver tous les liens <a>
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Si c'est un lien vers une page HTML locale (pas externe)
            if href.endswith('.html') and not href.startswith('http'):
                # Ajouter '_enrichi' avant '.html'
                new_href = href.replace('.html', '_enrichi.html')
                link['href'] = new_href
        
        return soup
    
    def enrich_all_pages(self):
        """Enrichit toutes les pages HTML du dossier d'entrée"""
        print("\n" + "="*60)
        print("ENRICHISSEMENT DES PAGES HTML")
        print(f"Format : {self.format.upper()}")
        print("="*60 + "\n")
        
        self.create_output_directory()
        
        html_files = [f for f in os.listdir(self.input_dir) if f.endswith('.html')]
        
        for filename in html_files:
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, filename.replace('.html', '_enrichi.html'))
            
            print(f"Traitement de {filename}...")
            
            if 'classement' in filename:
                self.enrich_classement_page(input_path, output_path)
            elif 'calendrier' in filename:
                self.enrich_calendrier_page(input_path, output_path)
            elif 'statistiques' in filename:
                self.enrich_statistiques_page(input_path, output_path)
            elif 'equipe_' in filename:
                self.enrich_equipe_page(input_path, output_path)
            elif 'index' in filename:
                self.enrich_index_page(input_path, output_path)
            else:
                # Copier avec mise à jour des liens
                with open(input_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                # Mettre à jour les liens même sans enrichissement
                self.update_links(soup)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
            
            print(f"  ✓ Créé : {os.path.basename(output_path)}")
        
        print(f"\n{'='*60}")
        print("✓ ENRICHISSEMENT TERMINÉ")
        print(f"{'='*60}")
        print(f"\n{len(html_files)} pages enrichies dans : {self.output_dir}")
    
    def enrich_classement_page(self, input_path: str, output_path: str):
        """Enrichit la page de classement avec métadonnées sur les équipes"""
        with open(input_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Ajouter le vocabulaire Schema.org dans le <head> si RDFa
        if self.format == 'rdfa':
            html_tag = soup.find('html')
            if html_tag:
                html_tag['vocab'] = "http://schema.org/"
        
        # Trouver le tableau de classement
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Ignorer l'en-tête
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 10:
                    if self.format == 'rdfa':
                        # Enrichir avec RDFa
                        row['typeof'] = "SportsTeam"
                        
                        # Position
                        cols[0]['property'] = "position"
                        
                        # Nom de l'équipe
                        cols[1]['property'] = "name"
                        
                        # Points
                        cols[2]['property'] = "points"
                        
                        # Matchs joués
                        cols[3]['property'] = "gamesPlayed"
                        
                        # Victoires
                        cols[4]['property'] = "wins"
                        
                        # Nuls
                        cols[5]['property'] = "draws"
                        
                        # Défaites
                        cols[6]['property'] = "losses"
                        
                        # Buts pour
                        cols[7]['property'] = "goalsScored"
                        
                        # Buts contre
                        cols[8]['property'] = "goalsConceded"
                        
                        # Différence
                        cols[9]['property'] = "goalDifference"
        
        # Si JSON-LD, ajouter un script structuré
        if self.format == 'jsonld':
            structured_data = self._create_jsonld_classement(soup)
            script_tag = soup.new_tag('script', type='application/ld+json')
            script_tag.string = json.dumps(structured_data, indent=2, ensure_ascii=False)
            soup.head.append(script_tag)
        
        # Mettre à jour les liens pour pointer vers les pages enrichies
        self.update_links(soup)
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    def enrich_calendrier_page(self, input_path: str, output_path: str):
        """Enrichit la page calendrier avec métadonnées sur les matchs"""
        with open(input_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        if self.format == 'rdfa':
            html_tag = soup.find('html')
            if html_tag:
                html_tag['vocab'] = "http://schema.org/"
        
        # Trouver le tableau de calendrier
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Ignorer l'en-tête
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    if self.format == 'rdfa':
                        # Enrichir avec RDFa
                        row['typeof'] = "SportsEvent"
                        
                        # Date
                        cols[0]['property'] = "startDate"
                        
                        # Équipe domicile
                        cols[1]['property'] = "homeTeam"
                        cols[1]['typeof'] = "SportsTeam"
                        
                        # Score
                        cols[2]['property'] = "score"
                        
                        # Équipe extérieure
                        cols[3]['property'] = "awayTeam"
                        cols[3]['typeof'] = "SportsTeam"
        
        if self.format == 'jsonld':
            structured_data = self._create_jsonld_calendrier(soup)
            script_tag = soup.new_tag('script', type='application/ld+json')
            script_tag.string = json.dumps(structured_data, indent=2, ensure_ascii=False)
            soup.head.append(script_tag)
        
        # Mettre à jour les liens pour pointer vers les pages enrichies
        self.update_links(soup)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    def enrich_statistiques_page(self, input_path: str, output_path: str):
        """Enrichit la page statistiques"""
        with open(input_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        if self.format == 'rdfa':
            html_tag = soup.find('html')
            if html_tag:
                html_tag['vocab'] = "http://schema.org/"
            
            # Enrichir les stat-box
            stat_boxes = soup.find_all('div', class_='stat-box')
            for box in stat_boxes:
                box['typeof'] = "SportsOrganization"
                
                # Enrichir les paragraphes <p>
                paragraphs = box.find_all('p')
                for p in paragraphs:
                    text = p.get_text()
                    if 'Nombre total de matchs' in text:
                        strong = p.find('strong')
                        if strong and strong.next_sibling:
                            # Entourer le nombre avec une balise span
                            number_text = strong.next_sibling.strip()
                            new_span = soup.new_tag('span', property='numberOfGames')
                            new_span.string = number_text
                            strong.next_sibling.replace_with(new_span)
        
        if self.format == 'jsonld':
            structured_data = self._create_jsonld_statistiques(soup)
            script_tag = soup.new_tag('script', type='application/ld+json')
            script_tag.string = json.dumps(structured_data, indent=2, ensure_ascii=False)
            soup.head.append(script_tag)
        
        # Mettre à jour les liens pour pointer vers les pages enrichies
        self.update_links(soup)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    def enrich_equipe_page(self, input_path: str, output_path: str):
        """Enrichit les pages d'équipes"""
        with open(input_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        if self.format == 'rdfa':
            html_tag = soup.find('html')
            if html_tag:
                html_tag['vocab'] = "http://schema.org/"
            
            # Enrichir le h1 avec le nom de l'équipe
            h1 = soup.find('h1')
            if h1:
                h1['property'] = "name"
                h1['typeof'] = "SportsTeam"
            
            # Enrichir les stat-box
            stat_boxes = soup.find_all('div', class_='stat-box')
            for box in stat_boxes:
                paragraphs = box.find_all('p')
                for p in paragraphs:
                    text = p.get_text()
                    if 'Position' in text:
                        self._add_property_to_value(soup, p, 'position')
                    elif 'Points' in text:
                        self._add_property_to_value(soup, p, 'points')
                    elif 'Victoires' in text:
                        self._add_property_to_value(soup, p, 'wins')
                    elif 'Buts pour' in text:
                        self._add_property_to_value(soup, p, 'goalsScored')
            
            # Enrichir les matchs
            match_divs = soup.find_all('div', class_='match-result')
            for div in match_divs:
                div['typeof'] = "SportsEvent"
                
                paragraphs = div.find_all('p')
                if len(paragraphs) >= 3:
                    # Date
                    paragraphs[0]['property'] = "startDate"
                    # Score
                    score_p = div.find('p', class_='score')
                    if score_p:
                        score_p['property'] = "score"
        
        if self.format == 'jsonld':
            structured_data = self._create_jsonld_equipe(soup)
            script_tag = soup.new_tag('script', type='application/ld+json')
            script_tag.string = json.dumps(structured_data, indent=2, ensure_ascii=False)
            soup.head.append(script_tag)
        
        # Mettre à jour les liens pour pointer vers les pages enrichies
        self.update_links(soup)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    def enrich_index_page(self, input_path: str, output_path: str):
        """Enrichit la page d'index"""
        # Pour l'instant, enrichir comme la page de classement
        self.enrich_classement_page(input_path, output_path)
    
    def _add_property_to_value(self, soup, paragraph, property_name):
        """Ajoute un attribut property à la valeur numérique dans un paragraphe"""
        strong = paragraph.find('strong')
        if strong and strong.next_sibling:
            value_text = strong.next_sibling.strip()
            # Extraire le nombre
            import re
            number_match = re.search(r'[-+]?\d+', value_text)
            if number_match:
                number_str = number_match.group()
                new_span = soup.new_tag('span', property=property_name)
                new_span.string = number_str
                # Remplacer dans le texte
                rest_text = value_text.replace(number_str, '')
                strong.next_sibling.replace_with(new_span)
                if rest_text.strip():
                    new_span.insert_after(rest_text)
    
    def _create_jsonld_classement(self, soup) -> Dict:
        """Crée les données structurées JSON-LD pour le classement"""
        table = soup.find('table')
        teams = []
        
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 10:
                    team = {
                        "@type": "SportsTeam",
                        "position": cols[0].get_text().strip(),
                        "name": cols[1].get_text().strip(),
                        "points": cols[2].get_text().strip(),
                        "gamesPlayed": cols[3].get_text().strip(),
                        "wins": cols[4].get_text().strip(),
                        "draws": cols[5].get_text().strip(),
                        "losses": cols[6].get_text().strip(),
                        "goalsScored": cols[7].get_text().strip(),
                        "goalsConceded": cols[8].get_text().strip(),
                        "goalDifference": cols[9].get_text().strip()
                    }
                    teams.append(team)
        
        return {
            "@context": "http://schema.org",
            "@type": "SportsOrganization",
            "name": "England Premier League",
            "teams": teams
        }
    
    def _create_jsonld_calendrier(self, soup) -> Dict:
        """Crée les données structurées JSON-LD pour le calendrier"""
        table = soup.find('table')
        matches = []
        
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    match = {
                        "@type": "SportsEvent",
                        "startDate": cols[0].get_text().strip(),
                        "homeTeam": {
                            "@type": "SportsTeam",
                            "name": cols[1].get_text().strip()
                        },
                        "awayTeam": {
                            "@type": "SportsTeam",
                            "name": cols[3].get_text().strip()
                        },
                        "score": cols[2].get_text().strip()
                    }
                    matches.append(match)
        
        return {
            "@context": "http://schema.org",
            "@type": "SportsOrganization",
            "name": "England Premier League - Calendrier",
            "events": matches
        }
    
    def _create_jsonld_statistiques(self, soup) -> Dict:
        """Crée les données structurées JSON-LD pour les statistiques"""
        # Extraire les statistiques des stat-box
        stats = {
            "@context": "http://schema.org",
            "@type": "SportsOrganization",
            "name": "England Premier League - Statistiques"
        }
        
        return stats
    
    def _create_jsonld_equipe(self, soup) -> Dict:
        """Crée les données structurées JSON-LD pour une page d'équipe"""
        h1 = soup.find('h1')
        team_name = h1.get_text().strip() if h1 else "Unknown Team"
        
        team_data = {
            "@context": "http://schema.org",
            "@type": "SportsTeam",
            "name": team_name
        }
        
        # Extraire les statistiques
        stat_boxes = soup.find_all('div', class_='stat-box')
        for box in stat_boxes:
            paragraphs = box.find_all('p')
            for p in paragraphs:
                text = p.get_text()
                if 'Position' in text:
                    import re
                    match = re.search(r':\s*(\d+)', text)
                    if match:
                        team_data['position'] = match.group(1)
                elif 'Points' in text:
                    import re
                    match = re.search(r':\s*(\d+)', text)
                    if match:
                        team_data['points'] = match.group(1)
        
        return team_data


def main():
    """Fonction principale"""
    # Configuration
    INPUT_DIR = "web_1.0_output"  # Dossier avec pages HTML statiques
    OUTPUT_DIR_RDFA = "web_3.0_rdfa_output"  # Dossier pour pages enrichies RDFa
    OUTPUT_DIR_JSONLD = "web_3.0_jsonld_output"  # Dossier pour pages enrichies JSON-LD
    
    print("\n" + "="*60)
    print("ENRICHISSEMENT DES PAGES HTML")
    print("Transformation Web 1.0 → Web 3.0")
    print("="*60)
    
    # Vérifier que le dossier d'entrée existe
    if not os.path.exists(INPUT_DIR):
        print(f"\n Erreur : Le dossier {INPUT_DIR} n'existe pas.")
        print("Veuillez d'abord générer les pages HTML avec generate_html_pages.py")
        return
    
    # Demander le format
    print("\nChoisissez le format d'enrichissement :")
    print("  1. RDFa (attributs dans les balises HTML)")
    print("  2. JSON-LD (script structuré dans <head>)")
    print("  3. Les deux")
    
    choice = input("\nVotre choix (1/2/3) [par défaut: 1] : ").strip() or "1"
    
    if choice in ["1", "3"]:
        print("\n" + "="*60)
        print("ENRICHISSEMENT AVEC RDFa")
        print("="*60)
        enricher_rdfa = HTMLEnricher(INPUT_DIR, OUTPUT_DIR_RDFA, format="rdfa")
        enricher_rdfa.enrich_all_pages()
    
    if choice in ["2", "3"]:
        print("\n" + "="*60)
        print("ENRICHISSEMENT AVEC JSON-LD")
        print("="*60)
        enricher_jsonld = HTMLEnricher(INPUT_DIR, OUTPUT_DIR_JSONLD, format="jsonld")
        enricher_jsonld.enrich_all_pages()
    
    print("\n" + "="*60)
    print("✓ ENRICHISSEMENT TERMINÉ")
    print("="*60)
    print("\nVous pouvez maintenant :")
    print("1. Comparer les pages enrichies avec les originales")
    print("2. Tester l'extraction avec les scripts de la Partie 2")
    print("3. Extraire les triplets RDF pour créer votre base de connaissances")


if __name__ == "__main__":
    main()