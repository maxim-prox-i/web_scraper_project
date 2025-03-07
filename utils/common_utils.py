"""
Utilitaires communs utilisés dans différents modules du projet.
"""
import re, os
import time
import random
from fake_useragent import UserAgent


def format_time(seconds):
    """Formate les secondes en format HH:MM:SS"""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def sanitize_filename(filename):
    """Nettoie le nom de fichier/dossier en remplaçant les caractères spéciaux"""
    if not filename:
        return "default_filename"
        
    # Remplacer les caractères invalides par des underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Supprimer les espaces en début/fin
    sanitized = sanitized.strip()
    # Si vide après nettoyage, utiliser un nom par défaut
    if not sanitized:
        return "default_filename"
    return sanitized


def get_random_headers():
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

def extract_domain(url):
    """Extrait le nom de domaine d'une URL"""
    # Supprimer le protocole (http://, https://, etc.)
    domain = re.sub(r'^https?://', '', url)
    # Supprimer tout ce qui suit le premier slash
    domain = domain.split('/', 1)[0]
    # Supprimer tout paramètre ou port
    domain = domain.split('?', 1)[0].split(':', 1)[0]
    return domain

def ensure_data_directory(domain=None):
    """
    Assure que le répertoire data et le sous-répertoire du domaine existent
    
    Args:
        domain (str, optional): Nom de domaine pour lequel créer un sous-répertoire
        
    Returns:
        str: Chemin du répertoire créé
    """
    # Créer le répertoire data s'il n'existe pas
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Si un domaine est spécifié, créer son sous-répertoire
    if domain:
        domain_dir = os.path.join(data_dir, sanitize_filename(domain))
        if not os.path.exists(domain_dir):
            os.makedirs(domain_dir)
        return domain_dir
    
    return data_dir