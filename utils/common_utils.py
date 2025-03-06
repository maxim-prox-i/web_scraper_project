"""
Utilitaires communs utilisés dans différents modules du projet.
"""
import re
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