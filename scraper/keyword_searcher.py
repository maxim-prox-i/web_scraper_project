"""
Module contenant la classe KeywordSearcher pour rechercher des mots clés dans des pages web.
"""
import re
import time
import random
import requests
import threading
import datetime
import json
import os
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class KeywordSearcher:
    def __init__(self, input_file, output_file=None, max_threads=10):
        """
        Initialise le chercheur de mots clés.
        
        Args:
            input_file (str): Fichier contenant les URLs à analyser
            output_file (str, optional): Fichier de sortie pour les résultats
            max_threads (int, optional): Nombre maximum de threads à utiliser
        """
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}-keywords.csv"
        self.max_threads = max_threads
        
        # Threads et synchronisation
        self.lock = threading.RLock()
        self.session_pool = []
        for _ in range(max_threads):
            session = requests.Session()
            self.session_pool.append(session)
        
        self.session_lock = threading.Lock()
        self.session_index = 0
        
        # Résultats
        self.results = []
        self.results_lock = threading.Lock()
        
        # Pour stocker les mots clés
        self.keywords = []
        self.exact_matches = []  # Pour les mots entre guillemets
        
        # Barre de progression
        self.pbar = None
        
        # Désactiver les avertissements SSL
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
    
    def __del__(self):
        """Ferme les sessions HTTP lorsque l'objet est détruit"""
        for session in self.session_pool:
            session.close()
    
    def set_keywords(self, keywords_string):
        """
        Définit les mots clés à rechercher à partir d'une chaîne.
        
        Args:
            keywords_string (str): Chaîne contenant les mots clés, potentiellement entre guillemets
        """
        self.keywords = []
        self.exact_matches = []
        
        # Trouver les termes entre guillemets
        exact_pattern = r'"([^"]+)"'
        exact_matches = re.findall(exact_pattern, keywords_string)
        for exact in exact_matches:
            self.exact_matches.append(exact)
            # Remplacer les termes exacts par des espaces pour éviter de les traiter deux fois
            keywords_string = keywords_string.replace(f'"{exact}"', ' ')
        
        # Traiter les mots clés restants
        remaining_keywords = [k.strip().lower() for k in keywords_string.split() if k.strip()]
        self.keywords = remaining_keywords
        
        return len(self.keywords) + len(self.exact_matches)
    
    def get_random_headers(self):
        """Génère des en-têtes HTTP aléatoires qui imitent un navigateur"""
        try:
            from fake_useragent import UserAgent
            ua = UserAgent()
            return {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1'
            }
        except:
            # Fallback
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
    
    def get_session(self):
        """Obtient une session du pool de manière thread-safe"""
        with self.session_lock:
            session = self.session_pool[self.session_index]
            self.session_index = (self.session_index + 1) % len(self.session_pool)
            return session
    
    def check_keywords_in_text(self, text):
        """
        Vérifie si le texte contient les mots clés recherchés.
        
        Args:
            text (str): Le texte à analyser
            
        Returns:
            dict: Dictionnaire avec les mots clés trouvés et leur nombre d'occurrences
        """
        results = {}
        
        # Traiter le texte pour les recherches non sensibles à la casse
        text_lower = text.lower()
        
        # Vérifier les mots clés normaux (non sensibles à la casse)
        for keyword in self.keywords:
            count = text_lower.count(keyword.lower())
            if count > 0:
                results[keyword] = count
        
        # Vérifier les correspondances exactes (sensibles à la casse)
        for exact in self.exact_matches:
            count = text.count(exact)  # Pas de conversion en minuscules ici
            if count > 0:
                results[f'"{exact}"'] = count
        
        return results
    
    def process_url(self, url):
        """
        Traite une URL, vérifie si elle contient les mots clés recherchés.
        
        Args:
            url (str): L'URL à analyser
            
        Returns:
            dict: Résultat de l'analyse
        """
        url = url.strip()
        if not url:
            return None
            
        try:
            session = self.get_session()
            headers = self.get_random_headers()
            
            # Ajouter un referer plausible
            parsed_url = urlparse(url)
            headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}/"
            
            # Requête
            response = session.get(
                url,
                headers=headers,
                verify=False,
                timeout=15,
                allow_redirects=True
            )
            
            response.raise_for_status()
            
            # Vérifier si c'est du HTML
            if 'text/html' not in response.headers.get('Content-Type', '').lower():
                self.pbar.update(1)
                return {"url": url, "keywords_found": {}, "status": "not_html"}
            
            # Parser le HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire le texte visible
            text = soup.get_text(" ", strip=True)
            
            # Vérifier les mots clés
            keywords_found = self.check_keywords_in_text(text)
            status = "keywords_found" if keywords_found else "no_keywords_found"
            
            # Créer le résultat
            result = {
                "url": url,
                "keywords_found": keywords_found,
                "status": status,
                "title": soup.title.string if soup.title else "No title"
            }
            
            # Si des mots clés ont été trouvés, ajouter le résultat
            if keywords_found:
                with self.results_lock:
                    self.results.append(result)
            
            # Mettre à jour la barre de progression
            self.pbar.update(1)
            
            # Pause aléatoire courte pour respect des robots
            time.sleep(random.uniform(0.2, 0.5))
            
            return result
            
        except requests.RequestException as e:
            error_type = type(e).__name__
            self.pbar.update(1)
            return {"url": url, "keywords_found": {}, "status": f"error_{error_type}"}
        
        except Exception as e:
            self.pbar.update(1)
            return {"url": url, "keywords_found": {}, "status": f"error: {str(e)}"}
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier CSV"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'keywords', 'occurrences', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                for keyword, occurrences in result['keywords_found'].items():
                    writer.writerow({
                        'url': result['url'],
                        'title': result.get('title', 'No title'),
                        'keywords': keyword,
                        'occurrences': occurrences,
                        'status': result['status']
                    })
    
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def run(self, progress_callback=None):
        """
        Exécute la recherche de mots clés sur toutes les URLs
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
                
        Returns:
            tuple: (nombre d'URLs avec mots clés, nombre total d'URLs, fichier de sortie)
        """
        if not self.keywords and not self.exact_matches:
            error_msg = "Aucun mot clé défini pour la recherche"
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return 0, 0, self.output_file
        
        start_time = time.time()
        
        # Lire les URLs depuis le fichier
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            error_msg = f"Erreur lors de la lecture du fichier {self.input_file}: {str(e)}"
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return 0, 0, self.output_file
        
        total_urls = len(urls)
        keyword_str = ', '.join(self.keywords + [f'"{ex}"' for ex in self.exact_matches])
        
        if progress_callback:
            progress_callback(0, total_urls, 
                            f"Démarrage de la recherche de {len(self.keywords) + len(self.exact_matches)} mot(s) clé(s) ({keyword_str}) dans {total_urls} URLs")
        
        # Initialiser la barre de progression
        self.pbar = tqdm(total=total_urls, desc="Recherche de mots clés", 
                         bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Soumettre toutes les URLs
            future_to_url = {executor.submit(self.process_url, url): url for url in urls}
            
            # Mise à jour de la barre de progression avec ETA formaté
            processed = 0
            while processed < total_urls:
                time.sleep(0.5)  # Mise à jour toutes les 0.5 secondes
                processed = sum(1 for future in future_to_url if future.done())
                
                # Calculer et formater l'ETA
                elapsed = time.time() - start_time
                urls_per_second = processed / elapsed if elapsed > 0 else 0
                remaining = total_urls - processed
                eta_seconds = remaining / urls_per_second if urls_per_second > 0 else 0
                
                # Formater en HH:MM:SS
                eta_formatted = self.format_time(eta_seconds)
                
                # Mise à jour du callback de progression
                if progress_callback:
                    keywords_found = len(self.results)
                    found_percent = f"{(keywords_found / processed * 100):.1f}%" if processed > 0 else "0.0%"
                    status_msg = f"Progression: {processed}/{total_urls} - Trouvés: {keywords_found} ({found_percent}) - ETA: {eta_formatted}"
                    progress_callback(processed, total_urls, status_msg)
                
                # Si tous les URLs sont traités, sortir de la boucle
                if processed >= total_urls:
                    break
        
        # Fermer la barre de progression
        self.pbar.close()
        
        # Sauvegarder les résultats
        self.save_results()
        
        # Statistiques finales
        elapsed_time = time.time() - start_time
        keywords_found = len(self.results)
        success_rate = (keywords_found / total_urls) * 100 if total_urls > 0 else 0
        
        final_status = f"Recherche terminée en {self.format_time(elapsed_time)}\n" \
                      f"URLs avec mots clés: {keywords_found}/{total_urls} ({success_rate:.1f}%)"
        
        # Dernière mise à jour du callback de progression
        if progress_callback:
            progress_callback(total_urls, total_urls, final_status)

        # Sauvegarder les statistiques
        stats = {
            "input_file": self.input_file,
            "output_file": self.output_file,
            "total_urls": total_urls,
            "keywords_searched": self.keywords + [f'"{ex}"' for ex in self.exact_matches],
            "urls_with_keywords": keywords_found,
            "success_rate": success_rate,
            "elapsed_time": elapsed_time,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        stats_file = f"{os.path.splitext(self.output_file)[0]}-stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
            
        return keywords_found, total_urls, self.output_file