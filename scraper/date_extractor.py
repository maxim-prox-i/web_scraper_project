"""
Module contenant la classe DateExtractor pour extraire les dates de publication des pages web.
"""
import requests
import re
import time
import random
import json
import csv
import os
import logging
import threading
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from dateutil.parser import parse as parse_date
from fake_useragent import UserAgent
from tqdm import tqdm


class DateExtractor:
    def __init__(self, input_file, output_file=None, max_threads=10):
        """
        Initialise l'extracteur de dates.
        
        Args:
            input_file (str): Fichier contenant les URLs à traiter
            output_file (str, optional): Fichier de sortie pour les résultats
            max_threads (int, optional): Nombre maximum de threads à utiliser
        """
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}-dates.csv"
        self.max_threads = max_threads
        
        # Threads et synchronisation
        self.lock = threading.RLock()
        self.session_pool = []
        for _ in range(max_threads):
            session = requests.Session()
            self.session_pool.append(session)
        
        self.session_lock = threading.Lock()
        self.session_index = 0
        
        # Date patterns
        self.date_patterns = [
            # Formats ISO et similaires
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO 8601
            r'\d{4}-\d{2}-\d{2}',                    # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',                    # MM/DD/YYYY ou DD/MM/YYYY
            r'\d{2}\.\d{2}\.\d{4}',                  # DD.MM.YYYY
            r'\d{2}-\d{2}-\d{4}',                    # DD-MM-YYYY ou MM-DD-YYYY
            
            # Formats pour certains attributs HTML
            r'publishedDate[\"\']\?\s*:\s*[\"\']\?([^\"\']+)[\"\']\?',
            r'datePublished[\"\']\?\s*:\s*[\"\']\?([^\"\']+)[\"\']\?',
            r'dateCreated[\"\']\?\s*:\s*[\"\']\?([^\"\']+)[\"\']\?',
            r'date[\"\']\?\s*:\s*[\"\']\?([^\"\']+)[\"\']\?',
        ]
        
        # Attributs HTML et meta tags pour les dates
        self.date_attributes = [
            'datetime', 'pubdate', 'date', 'published', 'published_time',
            'article:published_time', 'datePublished', 'datepublished',
            'datecreated', 'date-created', 'article:published',
            'og:published_time', 'release_date', 'date_published',
            'created', 'modified'
        ]
        
        # Noms des mois en français
        self.french_months = {
            'janvier': 'January', 'fevrier': 'February', 'février': 'February',
            'mars': 'March', 'avril': 'April', 'mai': 'May',
            'juin': 'June', 'juillet': 'July', 'aout': 'August', 'août': 'August',
            'septembre': 'September', 'octobre': 'October',
            'novembre': 'November', 'decembre': 'December', 'décembre': 'December'
        }
        
        # Résultats
        self.results = []
        self.results_lock = threading.Lock()
        
        # Barre de progression
        self.pbar = None
        
        # Configuration du logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configure le logger pour cette classe"""
        logger = logging.getLogger("DateExtractor")
        logger.setLevel(logging.INFO)
        
        # Vérifier si des handlers sont déjà configurés
        if not logger.handlers:
            # Créer le handler pour fichier
            file_handler = logging.FileHandler("date_extractor.log")
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
    
    def normalize_date(self, date_str):
        """Normalise une date trouvée dans différents formats"""
        try:
            # Remplacer les noms de mois français
            for fr_month, en_month in self.french_months.items():
                if fr_month in date_str.lower():
                    date_str = date_str.lower().replace(fr_month, en_month)
            
            # Nettoyer la chaîne
            date_str = date_str.strip()
            date_str = re.sub(r'[^\w\s\-:/.]', '', date_str)
            
            # Parser la date
            dt = parse_date(date_str, fuzzy=True)
            
            # Vérifier si l'année est raisonnable
            if dt.year < 1990 or dt.year > datetime.datetime.now().year + 1:
                return None
            
            # Format ISO
            return dt.strftime('%Y-%m-%d')
        
        except (ValueError, OverflowError, TypeError):
            return None
    
    def extract_date_from_url(self, url):
        """Extrait une date de l'URL elle-même"""
        url_date_patterns = [
            r'/(\d{4}/\d{1,2}/\d{1,2})/',           # /2023/05/15/
            r'/(\d{4}-\d{1,2}-\d{1,2})/',           # /2023-05-15/
            r'/(\d{4}/\d{1,2})/',                   # /2023/05/
            r'(\d{4}-\d{2}-\d{2})',                 # 2023-05-15 n'importe où dans l'URL
        ]
        
        for pattern in url_date_patterns:
            match = re.search(pattern, url)
            if match:
                date_str = match.group(1).replace('/', '-')
                normalized_date = self.normalize_date(date_str)
                if normalized_date:
                    return normalized_date
        
        return None
    
    def extract_date_from_html(self, html, url):
        """Extrait la date de publication d'une page HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        possible_dates = []
        
        # 1. META tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            for attr in self.date_attributes:
                if meta.get('name') == attr or meta.get('property') == attr or meta.get('itemprop') == attr:
                    content = meta.get('content')
                    if content:
                        normalized_date = self.normalize_date(content)
                        if normalized_date:
                            possible_dates.append((normalized_date, 0.9))
        
        # 2. Time elements
        time_elements = soup.find_all(['time', 'span', 'div', 'p'])
        for element in time_elements:
            for attr in self.date_attributes:
                if element.get(attr):
                    normalized_date = self.normalize_date(element.get(attr))
                    if normalized_date:
                        possible_dates.append((normalized_date, 0.8))
            
            if element.string:
                for pattern in self.date_patterns:
                    matches = re.findall(pattern, str(element.string))
                    for match in matches:
                        normalized_date = self.normalize_date(match)
                        if normalized_date:
                            possible_dates.append((normalized_date, 0.7))
        
        # 3. Classes et IDs liés aux dates
        date_elements = soup.select('[class*=date], [class*=time], [id*=date], [id*=time], [class*=publish], [id*=publish]')
        for element in date_elements:
            text = element.get_text().strip()
            if text:
                normalized_date = self.normalize_date(text)
                if normalized_date:
                    possible_dates.append((normalized_date, 0.6))
        
        # 4. JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            if script.string:
                try:
                    data = json.loads(script.string)
                    # Fonction récursive pour JSON
                    def find_date_in_json(obj):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key.lower() in ['datepublished', 'datecreated', 'datemodified', 'date', 'published', 'created']:
                                    if isinstance(value, str):
                                        normalized_date = self.normalize_date(value)
                                        if normalized_date:
                                            possible_dates.append((normalized_date, 0.95))
                                
                                find_date_in_json(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_date_in_json(item)
                    
                    find_date_in_json(data)
                except json.JSONDecodeError:
                    pass
        
        # 5. HTML brut avec regex
        html_str = str(soup)
        for pattern in self.date_patterns:
            matches = re.findall(pattern, html_str)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                normalized_date = self.normalize_date(match)
                if normalized_date:
                    possible_dates.append((normalized_date, 0.5))
        
        # 6. URL en dernier recours
        url_date = self.extract_date_from_url(url)
        if url_date:
            possible_dates.append((url_date, 0.4))
            
        if not possible_dates:
            return None
            
        # Tri par confiance puis par date
        possible_dates.sort(key=lambda x: (-x[1], -int(x[0].replace('-', ''))))
        
        return possible_dates[0][0] if possible_dates else None
    
    def process_url(self, url):
        """Traite une URL et extrait sa date de publication"""
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
                timeout=10,
                allow_redirects=True
            )
            
            response.raise_for_status()
            
            # Vérifier si c'est du HTML
            if 'text/html' not in response.headers.get('Content-Type', '').lower():
                self.pbar.update(1)
                return {"url": url, "date": None, "status": "not_html"}
            
            # Extraire la date
            publication_date = self.extract_date_from_html(response.text, url)
            status = "success" if publication_date else "no_date_found"
            
            # Ajouter le résultat
            result = {"url": url, "date": publication_date, "status": status}
            
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
            return {"url": url, "date": None, "status": f"error_{error_type}"}
        
        except Exception as e:
            self.pbar.update(1)
            return {"url": url, "date": None, "status": "error"}
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier CSV"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'date', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow(result)
    
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def run(self, progress_callback=None):
        """
        Exécute l'extraction des dates sur toutes les URLs
        
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
            return
        
        total_urls = len(urls)
        self.logger.info(f"Traitement de {total_urls} URLs depuis {self.input_file}")
        
        if progress_callback:
            progress_callback(0, total_urls, f"Démarrage de l'extraction des dates pour {total_urls} URLs")
        
        # Initialiser la barre de progression
        self.pbar = tqdm(total=total_urls, desc="Extraction des dates", 
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
                
                # Dates trouvées jusqu'à présent
                dates_found = sum(1 for r in self.results if r.get('date'))
                success_rate = f"{(dates_found / processed * 100):.1f}%" if processed > 0 else "0.0%"
                
                # Mettre à jour la description de la barre
                self.pbar.set_description(f"Extraction des dates - ETA: {eta_formatted} - Taux: {success_rate}")
                
                # Mise à jour du callback de progression
                if progress_callback:
                    progress_callback(processed, total_urls, 
                                     f"Progression: {processed}/{total_urls} - Taux: {success_rate} - ETA: {eta_formatted}")
                
                # Si tous les URLs sont traités, sortir de la boucle
                if processed >= total_urls:
                    break
        
        # Fermer la barre de progression
        self.pbar.close()
        
        # Sauvegarder les résultats
        self.save_results()
        
        # Statistiques finales
        elapsed_time = time.time() - start_time
        dates_found = sum(1 for result in self.results if result.get('date'))
        success_rate = (dates_found / total_urls) * 100 if total_urls > 0 else 0
        
        final_status = f"Extraction terminée en {self.format_time(elapsed_time)}\n" \
                      f"Dates trouvées: {dates_found}/{total_urls} ({success_rate:.1f}%)"
        
        self.logger.info(final_status)
        self.logger.info(f"Résultats sauvegardés dans {self.output_file}")
        
        # Dernière mise à jour du callback de progression
        if progress_callback:
            progress_callback(total_urls, total_urls, final_status)

        # Sauvegarder les statistiques
        stats = {
            "input_file": self.input_file,
            "output_file": self.output_file,
            "total_urls": total_urls,
            "dates_found": dates_found,
            "success_rate": success_rate,
            "elapsed_time": elapsed_time,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        stats_file = f"{os.path.splitext(self.output_file)[0]}-stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
            
        self.logger.info(f"Statistiques sauvegardées dans {stats_file}")
        return dates_found, total_urls, self.output_file


if __name__ == "__main__":
    print("=== EXTRACTEUR DE DATES DE PUBLICATION ===")
    print("Ce script parcourt une liste d'URLs et extrait les dates de publication des pages web.")
    
    input_file = input("Fichier contenant les URLs (par défaut: urls.txt): ") or "urls.txt"
    output_file = input("Fichier de sortie (par défaut: [nom_du_fichier_d'entrée]-dates.csv): ") or None
    
    max_threads_input = input("Nombre de threads (par défaut: 10): ")
    max_threads = int(max_threads_input) if max_threads_input.strip() else 10
    
    print(f"\nDémarrage de l'extraction des dates à partir de {input_file}")
    print(f"Utilisation de {max_threads} threads en parallèle")
    
    try:
        # Désactiver les avertissements SSL
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
        
        extractor = DateExtractor(input_file, output_file, max_threads)
        extractor.run()
        
    except KeyboardInterrupt:
        print("\nExtraction interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")