"""
Module contenant la classe SiteScraper pour explorer et récupérer les URLs d'un site web.
"""
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from collections import deque
import xml.etree.ElementTree as ET
import logging


class SiteScraper:
    def __init__(self, start_url, output_file='urls.txt', max_urls=None):
        """
        Initialise le scraper de site web.
        
        Args:
            start_url (str): URL de départ pour le scraping
            output_file (str, optional): Fichier où enregistrer les URLs trouvées
            max_urls (int, optional): Nombre maximum d'URLs à scraper (None = illimité)
        """
        self.start_url = start_url
        self.output_file = output_file
        self.max_urls = max_urls  # Nombre maximum d'URLs à scraper (None = illimité)
        
        # Extraire le domaine de base
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        self.base_url = f"{parsed_url.scheme}://{self.base_domain}"
        
        self.session = requests.Session()
        self.visited = set()  # URLs déjà visitées
        self.found_urls = set()  # Toutes les URLs trouvées
        self.queue = deque([start_url])  # File d'attente pour le BFS
        
        # Fichiers à ignorer
        self.ignored_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.tif', '.tiff',
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods', '.odp',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.wav', '.ogg', '.webm',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.css', '.js', '.json', '.xml', '.rss'
        }
        
        # Proxy rotator (à configurer si nécessaire)
        self.proxies = []
        
        # Configuration du logger
        self.logger = self._setup_logger()
        
        # Désactiver les avertissements SSL
        requests.packages.urllib3.disable_warnings(
            requests.packages.urllib3.exceptions.InsecureRequestWarning
        )
        
        self.normalize_cache = {}  # Cache pour les URLs normalisées
        
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
    
    def normalize_url(self, url):
        """Normalise une URL pour éviter les duplications avec cache"""
        if url in self.normalize_cache:
            return self.normalize_cache[url]
            
        parsed = urlparse(url)
        # Supprimer les fragments
        cleaned_url = parsed._replace(fragment='').geturl()
        # Décoder les caractères URL encodés
        cleaned_url = unquote(cleaned_url)
        # Supprimer les slashes finaux (sauf si c'est la racine)
        if cleaned_url.endswith('/') and len(cleaned_url.rstrip('/')) > len(parsed.scheme) + 3:
            cleaned_url = cleaned_url.rstrip('/')
        
        self.normalize_cache[url] = cleaned_url
        return cleaned_url

    def _setup_logger(self):
        """Configure le logger pour cette classe"""
        logger = logging.getLogger("SiteScraper")
        logger.setLevel(logging.INFO)
        
        # Vérifier si des handlers sont déjà configurés
        if not logger.handlers:
            # Créer le handler pour fichier
            file_handler = logging.FileHandler("scraper.log")
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
    
    def is_valid_url(self, url):
        """Vérifie si une URL est valide et doit être crawlée"""
        try:
            parsed = urlparse(url)
            
            # Vérifier si c'est une URL valide avec un schéma et un domaine
            if not (parsed.scheme and parsed.netloc):
                return False
            
            # Vérifier si c'est dans le même domaine
            if parsed.netloc != self.base_domain:
                return False
            
            # Ignorer les extensions à ne pas crawler
            if any(url.lower().endswith(ext) for ext in self.ignored_extensions):
                return False
            
            # Ignorer les ancres dans la même page
            if '#' in url and url.split('#')[0] in self.found_urls:
                return False
                
            # Éviter certains schémas comme mailto:, tel:, etc.
            if parsed.scheme not in ('http', 'https'):
                return False
                
            return True
        except Exception:
            return False
    
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
                'Cache-Control': 'max-age=0',
                'TE': 'Trailers',
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
    
    def get_random_proxy(self):
        """Retourne un proxy aléatoire s'il y en a de disponibles"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def make_request(self, url):
        """Effectue une requête HTTP avec gestion des erreurs et des tentatives"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers()
                proxy = self.get_random_proxy()
                proxies = {'http': proxy, 'https': proxy} if proxy else None
                
                response = self.session.get(
                    url, 
                    headers=headers,
                    proxies=proxies,
                    verify=False,
                    timeout=10,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    sleep_time = random.uniform(1, 3) * (attempt + 1)
                    self.logger.warning(f"Tentative {attempt+1} échouée pour {url}: {e}. Nouvel essai dans {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"Échec de la requête pour {url} après {max_retries} tentatives: {e}")
                    return None
    
    def normalize_url(self, url):
        """Normalise une URL pour éviter les duplications"""
        parsed = urlparse(url)
        # Supprimer les fragments
        cleaned_url = parsed._replace(fragment='').geturl()
        # Décoder les caractères URL encodés
        cleaned_url = unquote(cleaned_url)
        # Supprimer les slashes finaux (sauf si c'est la racine)
        if cleaned_url.endswith('/') and len(cleaned_url.rstrip('/')) > len(parsed.scheme) + 3:
            cleaned_url = cleaned_url.rstrip('/')
        return cleaned_url
    
    def save_url(self, url):
        """Enregistre une URL dans le fichier de sortie"""
        # Vérifier si on a atteint le nombre maximum d'URLs avant d'ajouter
        if self.max_urls and len(self.found_urls) >= self.max_urls:
            self.logger.info(f"Nombre maximum d'URLs atteint ({self.max_urls}). Arrêt du scraping.")
            return True
            
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(url + '\n')
        
        self.found_urls.add(url)
        self.logger.info(f"URL sauvegardée ({len(self.found_urls)}/{self.max_urls if self.max_urls else 'illimité'}): {url}")
        
        # Vérifier à nouveau après l'ajout
        if self.max_urls and len(self.found_urls) >= self.max_urls:
            self.logger.info(f"Nombre maximum d'URLs atteint ({self.max_urls}). Arrêt du scraping.")
            return True
        return False
    
    def extract_urls_from_html(self, html_content, base_url):
        """Extrait toutes les URLs d'une page HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = set()
        
        # Extraire les liens <a href>
        for a_tag in soup.find_all('a', href=True):
            urls.add(urljoin(base_url, a_tag['href']))
        
        # Extraire les liens de <link>
        for link_tag in soup.find_all('link', href=True):
            urls.add(urljoin(base_url, link_tag['href']))
        
        # Extraire les URLs de <script src>
        for script_tag in soup.find_all('script', src=True):
            urls.add(urljoin(base_url, script_tag['src']))
        
        # Extraire les URLs de <img src>
        for img_tag in soup.find_all('img', src=True):
            urls.add(urljoin(base_url, img_tag['src']))
        
        # Extraire les URLs de <iframe src>
        for iframe_tag in soup.find_all('iframe', src=True):
            urls.add(urljoin(base_url, iframe_tag['src']))
        
        # Extraire les URLs de <area href>
        for area_tag in soup.find_all('area', href=True):
            urls.add(urljoin(base_url, area_tag['href']))
        
        # Extraire les URLs des attributs data
        for tag in soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs)):
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and (value.startswith('http') or value.startswith('/')):
                    urls.add(urljoin(base_url, value))
        
        # Rechercher les URLs dans les scripts
        for script in soup.find_all('script'):
            if script.string:
                # Recherche d'URLs dans le texte du script
                matches = re.findall(r'(https?://[^\s\'\"]+)', script.string)
                for match in matches:
                    urls.add(match)
                
                # Recherche d'URLs relatives dans le texte du script
                matches = re.findall(r'[\'\"](/[^\s\'\"]+)[\'\"]', script.string)
                for match in matches:
                    urls.add(urljoin(base_url, match))
        
        # Rechercher les URLs dans le CSS
        for style in soup.find_all('style'):
            if style.string:
                # Recherche d'URLs dans le CSS
                matches = re.findall(r'url\([\'"]?([^\)]+)[\'"]?\)', style.string)
                for match in matches:
                    if not match.startswith('data:'):  # Ignorer les data URLs
                        urls.add(urljoin(base_url, match))
        
        return urls

    def extract_sitemap_urls(self, progress_callback=None):
        """Extrait les URLs des sitemaps"""
        sitemap_urls = []
        
        # Emplacements communs des sitemaps
        sitemap_locations = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/sitemap.php",
            f"{self.base_url}/sitemap/",
            f"{self.base_url}/sitemaps/"
        ]
        
        # Informer sur le nombre total d'étapes
        total_steps = len(sitemap_locations) + 1  # +1 pour robots.txt
        current_step = 0
        
        if progress_callback:
            progress_callback(current_step, total_steps, 
                            f"Étape {current_step}/{total_steps}: Initialisation de la recherche des sitemaps...")
        
        # Vérifier robots.txt pour les sitemaps
        try:
            current_step += 1
            robots_url = f"{self.base_url}/robots.txt"
            
            if progress_callback:
                progress_callback(current_step, total_steps, 
                                f"Étape {current_step}/{total_steps}: Vérification de robots.txt ({robots_url})...")
            
            self.logger.info(f"Vérification de robots.txt: {robots_url}")
            
            response = self.make_request(robots_url)
            if response and response.status_code == 200:
                robots_content = response.text
                # Rechercher les lignes Sitemap: URL
                sitemap_matches = re.findall(r'Sitemap:\s*(\S+)', robots_content, re.IGNORECASE)
                sitemap_locations.extend(sitemap_matches)
                
                if progress_callback:
                    progress_callback(current_step, total_steps, 
                                    f"Étape {current_step}/{total_steps}: Trouvé {len(sitemap_matches)} sitemaps dans robots.txt")
                
                self.logger.info(f"Trouvé {len(sitemap_matches)} références de sitemaps dans robots.txt")
            else:
                if progress_callback:
                    progress_callback(current_step, total_steps, 
                                    f"Étape {current_step}/{total_steps}: Aucun fichier robots.txt trouvé")
        except Exception as e:
            if progress_callback:
                progress_callback(current_step, total_steps, 
                                f"Étape {current_step}/{total_steps}: Erreur lors de l'accès à robots.txt: {str(e)[:50]}...")
            self.logger.error(f"Erreur lors de l'accès à robots.txt: {e}")
        
        # Mettre à jour le nombre total d'étapes
        total_steps = current_step + len(sitemap_locations)
        
        # Vérifier chaque emplacement potentiel de sitemap
        for i, sitemap_url in enumerate(sitemap_locations):
            try:
                current_step += 1
                
                if progress_callback:
                    progress_callback(current_step, total_steps, 
                                    f"Étape {current_step}/{total_steps}: Vérification du sitemap {sitemap_url}...")
                
                self.logger.info(f"Vérification du sitemap: {sitemap_url}")
                response = self.make_request(sitemap_url)
                
                if not response or response.status_code != 200:
                    if progress_callback:
                        progress_callback(current_step, total_steps, 
                                        f"Étape {current_step}/{total_steps}: Sitemap non trouvé à {sitemap_url}")
                    continue
                
                # Vérifier si c'est un sitemap XML valide
                if 'xml' not in response.headers.get('Content-Type', '').lower() and not sitemap_url.endswith(('.xml', '.xml.gz')):
                    if progress_callback:
                        progress_callback(current_step, total_steps, 
                                        f"Étape {current_step}/{total_steps}: Format non XML à {sitemap_url}")
                    continue
                
                # Parser le XML
                try:
                    root = ET.fromstring(response.content)
                    
                    # Espaces de noms courants dans les sitemaps
                    namespaces = {
                        'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                        'xhtml': 'http://www.w3.org/1999/xhtml'
                    }
                    
                    # Extraire les URLs des éléments <url>
                    url_count = 0
                    for url_elem in root.findall('.//sm:url/sm:loc', namespaces) or root.findall('.//url/loc'):
                        if url_elem.text:
                            url = url_elem.text.strip()
                            if self.is_valid_url(url):
                                sitemap_urls.append(url)
                                url_count += 1
                    
                    if progress_callback:
                        progress_callback(current_step, total_steps, 
                                        f"Étape {current_step}/{total_steps}: Trouvé {url_count} URLs dans {sitemap_url}")
                    
                    # Vérifier s'il s'agit d'un sitemap index et traiter les sous-sitemaps
                    sitemap_index_count = 0
                    sub_sitemaps = root.findall('.//sm:sitemap/sm:loc', namespaces) or root.findall('.//sitemap/loc')
                    
                    if sub_sitemaps:
                        if progress_callback:
                            progress_callback(current_step, total_steps, 
                                            f"Étape {current_step}/{total_steps}: Trouvé {len(sub_sitemaps)} sous-sitemaps dans {sitemap_url}")
                    
                    for sitemap_elem in sub_sitemaps:
                        sitemap_index_count += 1
                        if sitemap_elem.text:
                            sub_sitemap_url = sitemap_elem.text.strip()
                            
                            if progress_callback:
                                progress_callback(current_step, total_steps, 
                                                f"Étape {current_step}/{total_steps}: Traitement du sous-sitemap {sitemap_index_count}/{len(sub_sitemaps)}: {sub_sitemap_url}")
                            
                            self.logger.info(f"Traitement du sous-sitemap: {sub_sitemap_url}")
                            
                            # Requête pour le sous-sitemap
                            sub_response = self.make_request(sub_sitemap_url)
                            if sub_response and sub_response.status_code == 200:
                                try:
                                    sub_root = ET.fromstring(sub_response.content)
                                    # Extraire les URLs des éléments <url>
                                    sub_url_count = 0
                                    for url_elem in sub_root.findall('.//sm:url/sm:loc', namespaces) or sub_root.findall('.//url/loc'):
                                        if url_elem.text:
                                            url = url_elem.text.strip()
                                            if self.is_valid_url(url):
                                                sitemap_urls.append(url)
                                                sub_url_count += 1
                                    
                                    if progress_callback:
                                        progress_callback(current_step, total_steps, 
                                                        f"Étape {current_step}/{total_steps}: Trouvé {sub_url_count} URLs dans le sous-sitemap {sitemap_index_count}/{len(sub_sitemaps)}")
                                    
                                except ET.ParseError:
                                    if progress_callback:
                                        progress_callback(current_step, total_steps, 
                                                        f"Étape {current_step}/{total_steps}: Erreur de parsing du sous-sitemap {sitemap_index_count}/{len(sub_sitemaps)}")
                                    self.logger.error(f"Erreur de parsing du sous-sitemap: {sub_sitemap_url}")
                
                except ET.ParseError:
                    if progress_callback:
                        progress_callback(current_step, total_steps, 
                                        f"Étape {current_step}/{total_steps}: Erreur de parsing du sitemap {sitemap_url}")
                    self.logger.error(f"Erreur de parsing du sitemap: {sitemap_url}")
            
            except Exception as e:
                if progress_callback:
                    progress_callback(current_step, total_steps, 
                                    f"Étape {current_step}/{total_steps}: Erreur lors du traitement du sitemap {sitemap_url}: {str(e)[:50]}...")
                self.logger.error(f"Erreur lors du traitement du sitemap {sitemap_url}: {e}")
        
        if progress_callback:
            progress_callback(total_steps, total_steps, 
                            f"Recherche des sitemaps terminée. Trouvé {len(sitemap_urls)} URLs au total.")
        
        self.logger.info(f"Extrait un total de {len(sitemap_urls)} URLs des sitemaps")
        return sitemap_urls

    def scrape(self, progress_callback=None):
        """
        Exécute le scraping complet du site
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
                Retourne True si le scraping doit être interrompu, False sinon
        """
        self.logger.info(f"Début du scraping pour {self.start_url}")
        self.logger.info(f"Limite d'URLs définie à: {self.max_urls if self.max_urls else 'illimité'}")
        
        # Propriété pour permettre l'interruption
        self.stop_requested = False
        
        if progress_callback:
            should_stop = progress_callback(0, 1, f"Initialisation du scraping pour {self.start_url}...")
            if should_stop:
                return self.found_urls  # Interruption demandée
        
        # Créer le fichier de sortie s'il n'existe pas ou le vider s'il existe
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Extraire d'abord les URLs des sitemaps
        if progress_callback:
            should_stop = progress_callback(0, 1, "Recherche des sitemaps et extraction des URLs...")
            if should_stop:
                return self.found_urls  # Interruption demandée
        
        # Passer le callback de progression à la fonction d'extraction des sitemaps
        sitemap_urls = self.extract_sitemap_urls(progress_callback)
        
        # Vérifier si on a atteint la limite avant de continuer
        limit_reached = False
        
        # Cache pour les URLs normalisées
        if not hasattr(self, 'normalize_cache'):
            self.normalize_cache = {}
        
        # Ajouter les URLs des sitemaps à la queue et aux URLs trouvées
        for url in sitemap_urls:
            # Vérifier si une interruption a été demandée
            if self.stop_requested:
                self.logger.info("Interruption du scraping demandée")
                break
                
            normalized_url = self.normalize_url(url)
            if normalized_url not in self.found_urls:
                if self.save_url(normalized_url):
                    limit_reached = True
                    break
                self.queue.append(normalized_url)
        
        # Exécuter le BFS si la limite n'est pas atteinte
        last_progress_update = time.time()
        progress_update_interval = 0.5  # Réduire les mises à jour de progression
        
        while self.queue and not limit_reached:
            # Vérifier si une interruption a été demandée
            if self.stop_requested:
                self.logger.info("Interruption du scraping demandée")
                break
                
            # Vérifier à nouveau la limite avant chaque itération
            if self.max_urls and len(self.found_urls) >= self.max_urls:
                self.logger.info(f"Limite d'URLs atteinte avant de traiter la prochaine URL: {len(self.found_urls)}/{self.max_urls}")
                break
            
            # Mettre à jour la progression si un callback est fourni (moins fréquemment)
            current_time = time.time()
            if progress_callback and (current_time - last_progress_update >= progress_update_interval):
                last_progress_update = current_time
                
                status_message = f"URLs trouvées: {len(self.found_urls)}"
                if self.max_urls:
                    should_stop = progress_callback(len(self.found_urls), self.max_urls, 
                                    f"{status_message}/{self.max_urls}, Visitées: {len(self.visited)}, En file: {len(self.queue)}")
                else:
                    should_stop = progress_callback(len(self.found_urls), 0, 
                                    f"{status_message}, Visitées: {len(self.visited)}, En file: {len(self.queue)}")
                
                if should_stop:
                    self.logger.info("Interruption du scraping demandée via callback")
                    break
                
            current_url = self.queue.popleft()
            
            # Vérifier si l'URL a déjà été visitée
            if current_url in self.visited:
                continue
            
            # Marquer l'URL comme visitée
            self.visited.add(current_url)
            
            # Afficher la progression (moins fréquemment)
            if len(self.visited) % 50 == 0:  # Réduit de 10 à 50
                self.logger.info(f"Progression: {len(self.found_urls)}/{self.max_urls if self.max_urls else 'illimité'} URLs trouvées, {len(self.visited)} visitées, {len(self.queue)} en attente")
            
            # Délai aléatoire entre les requêtes (réduit pour plus de rapidité)
            time.sleep(random.uniform(0.1, 0.3))  # Réduit de 0.2-0.5 à 0.1-0.3
            
            # Faire la requête
            response = self.make_request(current_url)
            if not response:
                continue
            
            # Vérifier si l'URL doit être sauvegardée
            normalized_url = self.normalize_url(current_url)
            if normalized_url not in self.found_urls:
                # Vérifier si on a atteint le nombre maximum d'URLs
                if self.save_url(normalized_url):
                    self.logger.info("Limite d'URLs atteinte. Arrêt du scraping.")
                    limit_reached = True
                    break
            
            # Si on a atteint la limite, sortir de la boucle
            if self.max_urls and len(self.found_urls) >= self.max_urls:
                self.logger.info("Limite d'URLs atteinte après sauvegarde. Arrêt du scraping.")
                break
                
            # Vérifier le type de contenu
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                continue
            
            # Extraire les URLs de la page - utiliser directement un set
            new_urls = set(self.extract_urls_from_html(response.text, current_url))
            
            # Traitement par lots des nouvelles URLs pour plus d'efficacité
            new_valid_urls = []
            
            # Filtrer et ajouter les nouvelles URLs à la queue
            for url in new_urls:
                normalized_url = self.normalize_url(url)
                if self.is_valid_url(normalized_url) and normalized_url not in self.visited and normalized_url not in self.queue:
                    new_valid_urls.append(normalized_url)
            
            # Ajouter les URLs en une seule fois pour réduire les opérations sur la queue
            self.queue.extend(new_valid_urls)
            
            # Vérifier si on a atteint la limite d'URLs
            if self.max_urls and len(self.found_urls) >= self.max_urls:
                limit_reached = True
                break
        
        # Mise à jour finale du statut
        if progress_callback:
            status_message = f"Terminé! {len(self.found_urls)}"
            if self.max_urls:
                progress_callback(len(self.found_urls), self.max_urls, 
                                f"{status_message}/{self.max_urls} URLs trouvées")
            else:
                progress_callback(len(self.found_urls), len(self.found_urls), 
                                f"{status_message} URLs trouvées")
                
        self.logger.info(f"Scraping terminé. {len(self.found_urls)} URLs trouvées et enregistrées dans {self.output_file}")
        return self.found_urls



#region  Main

if __name__ == "__main__":
    print("=== SCRAPER DE SITE WEB COMPLET ===")
    print("Ce script va explorer un site web et extraire toutes les URLs.")
    
    start_url = input("Entrez l'URL du site à scraper (ex: https://example.com): ")
    output_file = input("Entrez le nom du fichier de sortie (défaut: urls.txt): ") or "urls.txt"
    
    max_urls_input = input("Nombre maximum d'URLs à scraper (laissez vide pour illimité): ")
    max_urls = int(max_urls_input) if max_urls_input.strip() else None
    
    if not output_file.endswith('.txt'):
        output_file += '.txt'
    
    print(f"\nDémarrage du scraping de {start_url}")
    print(f"Les URLs seront enregistrées dans {output_file}")
    
    scraper = SiteScraper(start_url, output_file, max_urls)
    try:
        urls = scraper.scrape()
        print(f"\nScraping terminé avec succès!")
        print(f"Nombre total d'URLs trouvées: {len(urls)}")
        print(f"Les URLs ont été enregistrées dans {output_file}")
    except KeyboardInterrupt:
        print("\nScraping interrompu par l'utilisateur.")
        print(f"Nombre d'URLs trouvées avant l'interruption: {len(scraper.found_urls)}")
        print(f"Les URLs ont été enregistrées dans {output_file}")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
        print(f"Consultez le fichier scraper.log pour plus de détails.")