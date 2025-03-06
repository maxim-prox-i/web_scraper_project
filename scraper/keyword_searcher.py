"""
Module contenant la classe KeywordSearcher pour rechercher des mots-clés dans les pages web.
"""
import os
import re
import time
import requests
import threading
import logging
import csv
import tempfile
import datetime
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class KeywordSearcher:
    def __init__(self, input_file, keywords, case_sensitive=False, temp_dir=None, max_threads=10):
        """
        Initialise le chercheur de mots-clés.
        
        Args:
            input_file (str): Fichier contenant les URLs à analyser
            keywords (list): Liste de mots-clés à rechercher
            case_sensitive (bool): Si True, respecte la casse des mots-clés
            temp_dir (str, optional): Répertoire temporaire pour les résultats
            max_threads (int, optional): Nombre maximum de threads à utiliser
        """
        self.input_file = input_file
        self.keywords = keywords
        self.case_sensitive = case_sensitive
        self.max_threads = max_threads
        
        # Créer un répertoire temporaire pour les résultats
        if temp_dir:
            self.temp_dir = temp_dir
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="keyword_search_")
            
        # Nom de fichier de sortie basé sur la date et l'heure actuelles
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(self.temp_dir, f"keyword_results_{timestamp}.csv")
        self.stats_file = os.path.join(self.temp_dir, f"search_stats_{timestamp}.json")
        
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
        
        # Barre de progression
        self.pbar = None
        
        # Statistiques
        self.stats = {
            "keywords": self.keywords,
            "case_sensitive": self.case_sensitive,
            "total_urls": 0,
            "processed_urls": 0,
            "urls_with_matches": 0,
            "total_matches": 0,
            "matches_per_keyword": {keyword: 0 for keyword in self.keywords},
            "start_time": datetime.datetime.now().isoformat()
        }
        
        # Configuration du logger
        self.logger = self._setup_logger()

    def __del__(self):
        """Ferme les sessions HTTP lorsque l'objet est détruit"""
        if hasattr(self, 'session_pool'):
            for session in self.session_pool:
                try:
                    session.close()
                except:
                    pass
        elif hasattr(self, 'session'):
            try:
                self.session.close()
            except:
                pass

    def _setup_logger(self):
        """Configure le logger pour cette classe"""
        logger = logging.getLogger("KeywordSearcher")
        logger.setLevel(logging.INFO)
        
        # Vérifier si des handlers sont déjà configurés
        if not logger.handlers:
            # Créer le handler pour fichier
            file_handler = logging.FileHandler("keyword_searcher.log")
            file_handler.setLevel(logging.INFO)
            
            # Créer le handler pour console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Créer le format
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Ajouter les handlers au logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def __del__(self):
        """Ferme les sessions HTTP lorsque l'objet est détruit"""
        for session in self.session_pool:
            session.close()
    
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
    
    def search_keywords_in_text(self, text, url):
        """
        Recherche les mots-clés dans le texte et retourne les résultats.
        
        Args:
            text (str): Texte de la page web
            url (str): URL de la page web
        
        Returns:
            list: Liste des résultats pour chaque mot-clé trouvé
        """
        search_results = []
        soup = BeautifulSoup(text, 'html.parser')
        
        # Extraire le titre
        title = soup.title.string if soup.title else "Sans titre"
        
        # Extraire le texte de la page sans balises HTML
        page_content = soup.get_text(" ", strip=True)
        
        # Récupérer l'aperçu du contenu (premiers 200 caractères)
        content_preview = page_content[:200] + "..." if len(page_content) > 200 else page_content
        
        # Vérifier si nous avons des patterns précompilés, sinon les créer
        if not hasattr(self, 'keyword_patterns'):
            self.keyword_patterns = {}
            for keyword in self.keywords:
                if self.case_sensitive:
                    self.keyword_patterns[keyword] = re.compile(re.escape(keyword))
                else:
                    self.keyword_patterns[keyword] = re.compile(re.escape(keyword), re.IGNORECASE)
        
        # Recherche pour chaque mot-clé
        for keyword in self.keywords:
            # Utiliser le pattern précompilé
            pattern = self.keyword_patterns[keyword]
            
            matches = pattern.findall(page_content)
            match_count = len(matches)
            
            if match_count > 0:
                # Mettre à jour les statistiques
                with self.results_lock:
                    self.stats["total_matches"] += match_count
                    self.stats["matches_per_keyword"][keyword] += match_count
                
                # Extraire les contextes d'occurrence de manière plus efficace
                contexts = []
                # Limiter le nombre de contextes à extraire pour les performances
                matches_to_process = pattern.finditer(page_content)
                context_count = 0
                
                for match in matches_to_process:
                    if context_count >= 5:  # Limiter à 5 contextes max
                        break
                        
                    start = max(0, match.start() - 50)
                    end = min(len(page_content), match.end() + 50)
                    context = page_content[start:end].replace("\n", " ")
                    if start > 0:
                        context = "..." + context
                    if end < len(page_content):
                        context = context + "..."
                    
                    # Mettre en évidence le mot-clé dans le contexte (pour la lisibilité)
                    if self.case_sensitive:
                        highlighted = context.replace(keyword, f"**{keyword}**")
                    else:
                        # Pour respecter la casse originale même en mode insensible
                        original_match = match.group(0)
                        highlighted = context.replace(original_match, f"**{original_match}**")
                    
                    contexts.append(highlighted)
                    context_count += 1
                
                # Si plus de 5 correspondances, ajouter une note
                if match_count > 5:
                    contexts.append(f"...et {match_count - 5} autres occurrences")
                
                # Ajouter le résultat
                result = {
                    "url": url,
                    "title": title,
                    "keyword": keyword,
                    "matches": match_count,
                    "preview": content_preview,
                    "contexts": contexts
                }
                search_results.append(result)
        
        return search_results
    
    def process_url(self, url):
        """Traite une URL et cherche les mots-clés dans la page"""
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
                with self.results_lock:
                    self.stats["processed_urls"] += 1
                return {"url": url, "status": "not_html", "results": []}
            
            # Rechercher les mots-clés
            search_results = self.search_keywords_in_text(response.text, url)
            
            # Mettre à jour les statistiques
            with self.results_lock:
                self.stats["processed_urls"] += 1
                if search_results:
                    self.stats["urls_with_matches"] += 1
                    self.results.extend(search_results)
            
            # Mettre à jour la barre de progression
            self.pbar.update(1)
            
            # Pause aléatoire courte pour respect des robots
            time.sleep(0.2)
            
            return {"url": url, "status": "success", "results": search_results}
            
        except requests.RequestException as e:
            error_type = type(e).__name__
            self.pbar.update(1)
            with self.results_lock:
                self.stats["processed_urls"] += 1
            return {"url": url, "status": f"error_{error_type}", "results": []}
        
        except Exception as e:
            self.pbar.update(1)
            with self.results_lock:
                self.stats["processed_urls"] += 1
            return {"url": url, "status": "error", "results": []}
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier CSV"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'keyword', 'matches', 'preview', 'contexts']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                # Convertir la liste de contextes en une chaîne formatée
                contexts_str = " | ".join(result["contexts"])
                
                writer.writerow({
                    'url': result['url'],
                    'title': result['title'],
                    'keyword': result['keyword'],
                    'matches': result['matches'],
                    'preview': result['preview'],
                    'contexts': contexts_str
                })
    
    def save_stats(self):
        """Sauvegarde les statistiques dans un fichier JSON"""
        # Ajouter le temps de fin et la durée
        self.stats["end_time"] = datetime.datetime.now().isoformat()
        start = datetime.datetime.fromisoformat(self.stats["start_time"])
        end = datetime.datetime.fromisoformat(self.stats["end_time"])
        self.stats["duration_seconds"] = (end - start).total_seconds()
        
        # Sauvegarder le fichier
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def run(self, progress_callback=None):
        """
        Exécute la recherche de mots-clés sur toutes les URLs
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
        """
        start_time = time.time()
        
        # Lire les URLs depuis le fichier
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            error_msg = f"Erreur lors de la lecture du fichier {self.input_file}: {str(e)}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return None
        
        total_urls = len(urls)
        self.stats["total_urls"] = total_urls
        
        self.logger.info(f"Recherche de mots-clés dans {total_urls} URLs depuis {self.input_file}")
        self.logger.info(f"Mots-clés: {', '.join(self.keywords)}")
        
        if progress_callback:
            progress_callback(0, total_urls, f"Démarrage de la recherche pour {total_urls} URLs")
        
        # Initialiser la barre de progression
        self.pbar = tqdm(total=total_urls, desc="Recherche de mots-clés", 
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
                
                # Mots-clés trouvés jusqu'à présent
                with self.results_lock:
                    matches_found = self.stats["total_matches"]
                    urls_with_matches = self.stats["urls_with_matches"]
                
                success_rate = f"{(urls_with_matches / processed * 100):.1f}%" if processed > 0 else "0.0%"
                
                # Mettre à jour la description de la barre
                self.pbar.set_description(f"Recherche - ETA: {eta_formatted} - Correspondances: {matches_found}")
                
                # Mise à jour du callback de progression
                if progress_callback:
                    progress_callback(processed, total_urls, 
                                     f"Progression: {processed}/{total_urls} - Correspondances: {matches_found} - ETA: {eta_formatted}")
                
                # Si tous les URLs sont traités, sortir de la boucle
                if processed >= total_urls:
                    break
        
        # Fermer la barre de progression
        self.pbar.close()
        
        # Sauvegarder les résultats
        self.save_results()
        
        # Sauvegarder les statistiques
        self.save_stats()
        
        # Statistiques finales
        elapsed_time = time.time() - start_time
        
        final_status = f"Recherche terminée en {self.format_time(elapsed_time)}\n" \
                      f"Correspondances trouvées: {self.stats['total_matches']} dans {self.stats['urls_with_matches']}/{total_urls} URLs"
        
        self.logger.info(final_status)
        self.logger.info(f"Résultats sauvegardés dans {self.output_file}")
        
        # Dernière mise à jour du callback de progression
        if progress_callback:
            progress_callback(total_urls, total_urls, final_status)
        
        return {
            "output_file": self.output_file,
            "stats_file": self.stats_file,
            "stats": self.stats,
            "temp_dir": self.temp_dir
        }


if __name__ == "__main__":
    print("=== RECHERCHE DE MOTS-CLÉS ===")
    print("Ce script parcourt une liste d'URLs et recherche des mots-clés spécifiques dans les pages web.")
    
    input_file = input("Fichier contenant les URLs (par défaut: urls.txt): ") or "urls.txt"
    keywords_input = input("Mots-clés à rechercher (séparés par des virgules): ")
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    case_sensitive = input("Respecter la casse? (o/n, par défaut: non): ").lower() == 'o'
    
    max_threads_input = input("Nombre de threads (par défaut: 10): ")
    max_threads = int(max_threads_input) if max_threads_input.strip() else 10
    
    print(f"\nDémarrage de la recherche de mots-clés à partir de {input_file}")
    print(f"Mots-clés recherchés: {', '.join(keywords)}")
    print(f"Casse respectée: {'Oui' if case_sensitive else 'Non'}")
    print(f"Utilisation de {max_threads} threads en parallèle")
    
    try:
        # Désactiver les avertissements SSL
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        searcher = KeywordSearcher(input_file, keywords, case_sensitive, max_threads=max_threads)
        result = searcher.run()
        
        if result:
            print(f"\nRecherche terminée avec succès!")
            print(f"Résultats enregistrés dans: {result['output_file']}")
            print(f"Statistiques enregistrées dans: {result['stats_file']}")
    
    except KeyboardInterrupt:
        print("\nRecherche interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
