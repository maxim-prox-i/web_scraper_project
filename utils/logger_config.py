"""
Configuration du logger pour le projet
"""
import logging
import os


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configure un logger avec un format standardisé
    
    Args:
        name (str): Nom du logger
        log_file (str, optional): Chemin du fichier de log
        level (int, optional): Niveau de log (default: logging.INFO)
        
    Returns:
        logging.Logger: Instance du logger configuré
    """
    # Créer le répertoire de logs s'il n'existe pas et qu'un fichier est spécifié
    if log_file and not os.path.exists(os.path.dirname(log_file)) and os.path.dirname(log_file):
        os.makedirs(os.path.dirname(log_file))
    
    # Configuration des handlers
    handlers = []
    
    # Toujours ajouter le StreamHandler pour afficher les logs sur la console
    handlers.append(logging.StreamHandler())
    
    # Ajouter un FileHandler si un fichier est spécifié
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configuration de base
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    
    # Récupérer le logger
    logger = logging.getLogger(name)
    return logger