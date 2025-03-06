"""
Module contenant la classe URLDateOrganizer pour organiser les URLs par date.
"""
import csv
import os
import re
import time
import datetime
import json
from tqdm import tqdm


class URLDateOrganizer:
    def __init__(self, input_file, output_dir=None, folder_name=None):
        """
        Initialise l'organisateur d'URLs par date.
        
        Args:
            input_file (str): Fichier CSV contenant les URLs et leurs dates
            output_dir (str, optional): Répertoire de sortie pour l'organisation
            folder_name (str, optional): Nom du dossier principal pour les données organisées
        """
        self.input_file = input_file
        self.folder_name = self.sanitize_filename(folder_name) if folder_name else "urls_organisees"
        
        # Définir le répertoire de sortie
        if output_dir:
            self.output_dir = os.path.join(output_dir, self.folder_name)
        else:
            parent_dir = os.path.dirname(os.path.abspath(input_file))
            self.output_dir = os.path.join(parent_dir, self.folder_name)
        
        # Pour stocker les statistiques
        self.stats = {
            "total_urls": 0,
            "urls_with_dates": 0,
            "urls_without_dates": 0,
            "years": {},
            "months": {}
        }
        
        # Pour stocker les URLs sans date
        self.undated_urls = []
        
        # Mapper des nombres de mois aux noms en français
        self.month_names = {
            "01": "Janvier",
            "02": "Février",
            "03": "Mars",
            "04": "Avril",
            "05": "Mai",
            "06": "Juin",
            "07": "Juillet",
            "08": "Août",
            "09": "Septembre",
            "10": "Octobre",
            "11": "Novembre",
            "12": "Décembre"
        }
    
    def sanitize_filename(self, filename):
        """Nettoie le nom de fichier/dossier en remplaçant les caractères spéciaux"""
        if not filename:
            return "urls_organisees"
            
        # Remplacer les caractères invalides par des underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # Supprimer les espaces en début/fin
        sanitized = sanitized.strip()
        # Si vide après nettoyage, utiliser un nom par défaut
        if not sanitized:
            return "urls_organisees"
        return sanitized
    
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def create_directory_structure(self):
        """Crée la structure de répertoires de base"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Créer un dossier pour les URLs sans date
        undated_dir = os.path.join(self.output_dir, "Sans_Date")
        if not os.path.exists(undated_dir):
            os.makedirs(undated_dir)
    
    def organize_urls(self, progress_callback=None):
        """
        Lit le fichier CSV et organise les URLs par date
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
        """
        start_time = time.time()
        
        # Vérifier si le fichier d'entrée existe
        if not os.path.exists(self.input_file):
            error_msg = f"Erreur : Le fichier {self.input_file} n'existe pas."
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return
        
        # Créer la structure de répertoires
        self.create_directory_structure()
        
        # Lire les URLs et les dates
        urls_by_date = {}
        total_rows = sum(1 for _ in open(self.input_file, 'r', encoding='utf-8')) - 1  # -1 pour l'en-tête
        
        if progress_callback:
            progress_callback(0, total_rows, f"Analyse du fichier {self.input_file}...")
        
        # Initialiser la barre de progression pour la lecture
        pbar = tqdm(total=total_rows, desc="Lecture des données", 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
        
        # Lire le fichier CSV
        with open(self.input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.stats["total_urls"] += 1
                url = row.get('url', '')
                date = row.get('date', '')
                
                if date:
                    # Format attendu: YYYY-MM-DD
                    match = re.match(r'(\d{4})-(\d{2})-\d{2}', date)
                    if match:
                        year, month = match.groups()
                        
                        # Mettre à jour les statistiques
                        self.stats["urls_with_dates"] += 1
                        self.stats["years"][year] = self.stats["years"].get(year, 0) + 1
                        self.stats["months"][month] = self.stats["months"].get(month, 0) + 1
                        
                        # Ajouter l'URL au dictionnaire par date
                        date_key = f"{year}-{month}"
                        if date_key not in urls_by_date:
                            urls_by_date[date_key] = []
                        
                        urls_by_date[date_key].append(url)
                    else:
                        # Si la date n'est pas au format attendu
                        self.stats["urls_without_dates"] += 1
                        self.undated_urls.append(url)
                else:
                    # Si pas de date
                    self.stats["urls_without_dates"] += 1
                    self.undated_urls.append(url)
                
                # Mettre à jour la barre de progression
                pbar.update(1)
                
                # Mettre à jour le callback de progression
                if progress_callback and self.stats["total_urls"] % 100 == 0:
                    progress_callback(self.stats["total_urls"], total_rows, 
                                     f"Lecture: {self.stats['total_urls']}/{total_rows} URLs")
        
        # Fermer la barre de progression
        pbar.close()
        
        # Calculer le nombre total d'entrées à écrire pour la nouvelle barre de progression
        total_entries = len(self.undated_urls) + sum(len(urls) for urls in urls_by_date.values())
        
        # Initialiser la barre de progression pour l'écriture
        pbar = tqdm(total=total_entries, desc="Organisation des URLs", 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
        
        # Nombre d'URLs traitées pour le callback de progression
        processed_entries = 0
        
        # Écrire les fichiers par année et par mois
        for date_key, urls in urls_by_date.items():
            year, month = date_key.split('-')
            
            # Créer le dossier de l'année s'il n'existe pas
            year_dir = os.path.join(self.output_dir, year)
            if not os.path.exists(year_dir):
                os.makedirs(year_dir)
            
            # Créer le dossier du mois s'il n'existe pas
            month_name = self.month_names.get(month, month)
            month_dir = os.path.join(year_dir, f"{month}_{month_name}")
            if not os.path.exists(month_dir):
                os.makedirs(month_dir)
            
            # Écrire les URLs dans un fichier
            filename = os.path.join(month_dir, f"{year}-{month}.urls.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
                    pbar.update(1)
                    processed_entries += 1
            
            # Mettre à jour le callback de progression
            if progress_callback and len(urls) > 0:
                progress_callback(processed_entries, total_entries, 
                                 f"Organisation: {processed_entries}/{total_entries} URLs")
        
        # Écrire les URLs sans date dans un fichier spécial
        if self.undated_urls:
            undated_file = os.path.join(self.output_dir, "Sans_Date", "urls_sans_date.txt")
            with open(undated_file, 'w', encoding='utf-8') as f:
                for url in self.undated_urls:
                    f.write(f"{url}\n")
                    pbar.update(1)
                    processed_entries += 1
            
            # Mettre à jour le callback de progression
            if progress_callback and len(self.undated_urls) > 0:
                progress_callback(total_entries, total_entries, 
                                 f"Organisation: {processed_entries}/{total_entries} URLs")
        
        # Fermer la barre de progression
        pbar.close()
        
        # Temps écoulé
        elapsed_time = time.time() - start_time
        
        # Compléter les statistiques
        self.stats["elapsed_time"] = elapsed_time
        self.stats["elapsed_time_formatted"] = self.format_time(elapsed_time)
        self.stats["timestamp"] = datetime.datetime.now().isoformat()
        self.stats["folder_name"] = self.folder_name
        
        # Sauvegarder les statistiques
        stats_file = os.path.join(self.output_dir, "stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        # Message final
        final_status = f"Organisation terminée en {self.format_time(elapsed_time)}\n" \
                      f"URLs traitées: {self.stats['total_urls']}\n" \
                      f"URLs avec date: {self.stats['urls_with_dates']}\n" \
                      f"URLs sans date: {self.stats['urls_without_dates']}"
        
        print(final_status)
        print(f"Structure organisée dans le dossier: {self.output_dir}")
        print(f"Statistiques détaillées dans: {stats_file}")
        
        # Mise à jour finale du callback de progression
        if progress_callback:
            progress_callback(total_entries, total_entries, final_status)
        
        # Afficher un résumé par année si des dates ont été trouvées
        if self.stats["urls_with_dates"] > 0:
            year_summary = "Distribution par année:\n"
            for year in sorted(self.stats["years"].keys()):
                count = self.stats["years"][year]
                percentage = (count / self.stats["urls_with_dates"]) * 100
                year_summary += f"  {year}: {count} URLs ({percentage:.1f}%)\n"
            
            print(year_summary)
            
            # Ajouter au callback de progression
            if progress_callback:
                progress_callback(total_entries, total_entries, final_status + "\n\n" + year_summary)
        
        return self.stats


if __name__ == "__main__":
    print("=== ORGANISATEUR D'URLs PAR DATE ===")
    print("Ce script organise les URLs en dossiers par année et par mois selon leurs dates de publication.")
    
    input_file = input("Fichier CSV des dates (par défaut: urls-dates.csv): ") or "urls-dates.csv"
    
    folder_name = input("Nom du dossier pour l'organisation des données: ")
    if folder_name:
        sanitized_name = re.sub(r'[\\/*?:"<>|]', '_', folder_name)
        if sanitized_name != folder_name:
            print(f"Note: Les caractères spéciaux dans le nom ont été remplacés. Nom utilisé: {sanitized_name}")
            folder_name = sanitized_name
    
    output_dir = input("Chemin complet du répertoire parent (laissez vide pour utiliser le répertoire actuel): ") or None
    
    print(f"\nDémarrage de l'organisation des URLs à partir de {input_file}")
    
    try:
        organizer = URLDateOrganizer(input_file, output_dir, folder_name)
        organizer.organize_urls()
    except KeyboardInterrupt:
        print("\nOrganisation interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")