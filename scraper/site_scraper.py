"""
Module contenant la classe SiteScraper pour explorer et récupérer les URLs d'un site web.
"""

import os, re, time, random, requests, sys
import queue  # Ajoutez cette ligne
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from collections import deque
import xml.etree.ElementTree as ET
import logging
from utils.common_utils import extract_domain, ensure_data_directory


class SiteScraper:
    def __init__(self, url, output_file=None, max_urls=None):
        """
        Initialise le scraper de site web avec une approche simplifiée.

        Args:
            url (str): URL de départ pour le scraping
            output_file (str, optional): Fichier où enregistrer les URLs trouvées
            max_urls (int, optional): Nombre maximum d'URLs à scraper (None = illimité)
        """
        self.start_url = url

        # Extraire le domaine pour créer le dossier de données
        parsed_url = urlparse(url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.base_domain = parsed_url.netloc

        # Extraire le domaine simple (sans www)
        self.domain = self.base_domain
        if self.domain.startswith("www."):
            self.domain = self.domain[4:]

        # Créer le dossier pour les données
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.domain_dir = os.path.join(self.data_dir, self.domain)
        if not os.path.exists(self.domain_dir):
            os.makedirs(self.domain_dir)

        # Définir le fichier de sortie
        if output_file:
            if os.path.isabs(output_file):
                self.output_file = output_file
            else:
                self.output_file = os.path.join(self.domain_dir, output_file)
        else:
            self.output_file = os.path.join(self.domain_dir, "urls.txt")

        # Initialiser les variables de base
        self.max_urls = max_urls
        self.found_urls = set()  # URLs déjà trouvées et enregistrées
        self.visited_urls = set()  # URLs déjà visitées
        self.to_visit = [
            self.start_url
        ]  # URLs à visiter (liste simple au lieu d'une queue)

        # Configuration du logger
        self.logger = self._setup_logger()

        # Liste des extensions à ignorer
        self.ignored_extensions = [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "bmp",
            "svg",
            "webp",
            "css",
            "js",
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "zip",
            "rar",
            "tar",
            "gz",
            "mp3",
            "mp4",
            "avi",
            "mov",
        ]

    def _setup_logger(self):
        """Configure un logger basique pour cette classe"""
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
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Ajouter les handlers au logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def normalize_url(self, url):
        """Normalise une URL pour éviter les duplications"""
        parsed = urlparse(url)

        # Supprimer les fragments (partie après #)
        cleaned_url = parsed._replace(fragment="").geturl()

        # Décoder les caractères URL encodés
        cleaned_url = unquote(cleaned_url)

        # Supprimer les slashes finaux (sauf si c'est la racine)
        if (
            cleaned_url.endswith("/")
            and len(cleaned_url.rstrip("/")) > len(parsed.scheme) + 3
        ):
            cleaned_url = cleaned_url.rstrip("/")

        return cleaned_url

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
            if any(url.lower().endswith("." + ext) for ext in self.ignored_extensions):
                return False

            # Éviter certains schémas comme mailto:, tel:, etc.
            if parsed.scheme not in ("http", "https"):
                return False

            return True
        except Exception:
            return False

    def make_request(self, url):
        """Effectue une requête HTTP simple avec gestion des erreurs"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                verify=False,  # Désactive la vérification SSL pour simplifier
                timeout=10,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la requête pour {url}: {e}")
            return None

    def save_url(self, url):
        """Enregistre une URL dans le fichier de sortie et dans l'ensemble des URLs trouvées"""
        # Vérifier si l'URL n'est pas déjà dans l'ensemble
        if url in self.found_urls:
            return False

        # Ajouter l'URL au fichier
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(url + "\n")

        # Ajouter l'URL à l'ensemble
        self.found_urls.add(url)
        self.logger.info(f"URL #{len(self.found_urls)} sauvegardée: {url}")

        # Vérifier si on a atteint le nombre maximum d'URLs
        if self.max_urls and len(self.found_urls) >= self.max_urls:
            return True  # Limite atteinte
        return False

    def extract_urls_from_html(self, html_content, base_url):
        """Extrait toutes les URLs d'une page HTML"""
        soup = BeautifulSoup(html_content, "html.parser")
        urls = set()

        # Extraire les liens <a href>
        for a_tag in soup.find_all("a", href=True):
            urls.add(urljoin(base_url, a_tag["href"]))

        # Extraire les liens de <link>
        for link_tag in soup.find_all("link", href=True):
            urls.add(urljoin(base_url, link_tag["href"]))

        return urls

    def extract_sitemap_urls(self):
        """Extrait les URLs d'un sitemap de manière simplifiée"""
        sitemap_urls = set()

        # Sitemap standard
        sitemap_url = f"{self.base_url}/sitemap.xml"
        self.logger.info(f"Recherche du sitemap: {sitemap_url}")

        response = self.make_request(sitemap_url)
        if not response or response.status_code != 200:
            self.logger.info(f"Sitemap non trouvé à {sitemap_url}")
            # Vérifier robots.txt
            robots_url = f"{self.base_url}/robots.txt"
            response = self.make_request(robots_url)
            if response and response.status_code == 200:
                # Rechercher les lignes Sitemap: URL
                sitemap_matches = re.findall(
                    r"Sitemap:\s*(\S+)", response.text, re.IGNORECASE
                )
                if sitemap_matches:
                    sitemap_url = sitemap_matches[0]
                    self.logger.info(f"Sitemap trouvé via robots.txt: {sitemap_url}")
                    response = self.make_request(sitemap_url)
                else:
                    return sitemap_urls
            else:
                return sitemap_urls

        if not response or response.status_code != 200:
            return sitemap_urls

        # Parser le XML
        try:
            root = ET.fromstring(response.content)

            # Déterminer le namespace s'il existe
            namespace = ""
            if root.tag.startswith("{"):
                namespace = root.tag.split("}")[0] + "}"

            # Vérifier si c'est un sitemap index (contient d'autres sitemaps)
            sitemaps = root.findall(".//" + namespace + "sitemap")
            if sitemaps:
                self.logger.info(f"Sitemap index trouvé avec {len(sitemaps)} sitemaps.")

                # Récupérer les URLs de chaque sitemap référencé
                for sitemap in sitemaps:
                    loc = sitemap.find(namespace + "loc")
                    if loc is not None and loc.text:
                        sub_sitemap_url = loc.text.strip()
                        self.logger.info(
                            f"Traitement du sous-sitemap: {sub_sitemap_url}"
                        )

                        # Requête pour le sous-sitemap
                        sub_response = self.make_request(sub_sitemap_url)
                        if sub_response and sub_response.status_code == 200:
                            try:
                                sub_root = ET.fromstring(sub_response.content)

                                # Extraire les URLs des éléments <url>
                                for url_elem in sub_root.findall(
                                    ".//" + namespace + "url//" + namespace + "loc"
                                ) or sub_root.findall(".//url//loc"):
                                    if url_elem.text:
                                        url = url_elem.text.strip()
                                        normalized_url = self.normalize_url(url)
                                        if self.is_valid_url(normalized_url):
                                            sitemap_urls.add(normalized_url)

                                self.logger.info(
                                    f"Extrait {len(sitemap_urls)} URLs du sous-sitemap {sub_sitemap_url}"
                                )

                            except ET.ParseError as e:
                                self.logger.error(
                                    f"Erreur de parsing du sous-sitemap {sub_sitemap_url}: {e}"
                                )
            else:
                # C'est un sitemap standard
                for url_elem in root.findall(
                    ".//" + namespace + "url//" + namespace + "loc"
                ) or root.findall(".//url//loc"):
                    if url_elem.text:
                        url = url_elem.text.strip()
                        normalized_url = self.normalize_url(url)
                        if self.is_valid_url(normalized_url):
                            sitemap_urls.add(normalized_url)

                self.logger.info(
                    f"Extrait {len(sitemap_urls)} URLs du sitemap {sitemap_url}"
                )

        except ET.ParseError as e:
            self.logger.error(f"Erreur de parsing du sitemap {sitemap_url}: {e}")

        return sitemap_urls

    def scrape(self, progress_callback=None):
        """
        Exécute le scraping du site avec une approche simplifiée

        Args:
            progress_callback (callable, optional): Fonction callback pour la progression
                Signature: callback(current_progress, max_progress, status_message)
        """
        self.logger.info(f"Début du scraping pour {self.start_url}")

        # Réinitialiser le fichier de sortie
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("")

        # Extraire les URLs du sitemap en premier
        if progress_callback:
            progress_callback(0, 1, "Recherche des URLs dans le sitemap...")

        sitemap_urls = self.extract_sitemap_urls()

        # Ajouter les URLs trouvées dans le sitemap
        for url in sitemap_urls:
            normalized_url = self.normalize_url(url)
            if normalized_url not in self.found_urls:
                if progress_callback:
                    progress_callback(
                        len(self.found_urls),
                        self.max_urls or len(sitemap_urls),
                        f"Enregistrement de l'URL du sitemap: {normalized_url[:50]}...",
                    )

                if self.save_url(normalized_url):
                    self.logger.info(
                        "Limite d'URLs atteinte après traitement du sitemap."
                    )
                    return self.found_urls

                # Ajouter à la liste à visiter si pas déjà visitée
                if (
                    normalized_url not in self.visited_urls
                    and normalized_url not in self.to_visit
                ):
                    self.to_visit.append(normalized_url)

        # Traiter les URLs une par une avec une simple boucle
        while self.to_visit:
            # Vérifier si on a atteint la limite
            if self.max_urls and len(self.found_urls) >= self.max_urls:
                self.logger.info(
                    f"Limite d'URLs atteinte: {len(self.found_urls)}/{self.max_urls}"
                )
                break

            # Prendre la première URL à visiter
            current_url = self.to_visit.pop(0)

            # Vérifier si déjà visitée
            if current_url in self.visited_urls:
                continue

            # Marquer comme visitée
            self.visited_urls.add(current_url)

            # Log et mise à jour de progression
            if len(self.visited_urls) % 10 == 0:
                self.logger.info(
                    f"Progression: {len(self.found_urls)} URLs trouvées, {len(self.visited_urls)} visitées, {len(self.to_visit)} à visiter"
                )

            if progress_callback:
                progress_callback(
                    len(self.found_urls),
                    self.max_urls or 0,
                    f"Visite de {current_url[:50]}... ({len(self.found_urls)} trouvées)",
                )

            # Faire une pause pour ne pas surcharger le serveur
            time.sleep(random.uniform(0.2, 0.5))

            # Récupérer le contenu de la page
            response = self.make_request(current_url)
            if not response:
                continue

            # Enregistrer l'URL si pas déjà fait
            if current_url not in self.found_urls:
                if self.save_url(current_url):
                    self.logger.info("Limite d'URLs atteinte.")
                    break

            # Vérifier si c'est une page HTML
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
                continue

            # Extraire les URLs de la page
            page_urls = self.extract_urls_from_html(response.text, current_url)

            # Ajouter les nouvelles URLs à la liste à visiter
            for url in page_urls:
                normalized_url = self.normalize_url(url)
                if (
                    self.is_valid_url(normalized_url)
                    and normalized_url not in self.visited_urls
                    and normalized_url not in self.to_visit
                ):
                    self.to_visit.append(normalized_url)

        # Mise à jour finale
        if progress_callback:
            progress_callback(
                len(self.found_urls),
                len(self.found_urls),
                f"Terminé! {len(self.found_urls)} URLs trouvées",
            )

        self.logger.info(
            f"Scraping terminé. {len(self.found_urls)} URLs trouvées et enregistrées dans {self.output_file}"
        )
        return self.found_urls
