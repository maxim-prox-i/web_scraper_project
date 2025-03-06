"""
Module contenant les classes pour exporter les URLs organisées vers des fichiers CSV.
"""
import os
import csv
import re
import time
import datetime
import json
import glob
from tqdm import tqdm


class URLToCSVExporter:
    """Classe pour exporter les URLs d'une année spécifique vers un fichier CSV."""
    
    def __init__(self, base_dir, year, output_file=None):
        """
        Initialise l'exporteur d'URLs vers CSV.
        
        Args:
            base_dir (str): Répertoire contenant les dossiers organisés par année
            year (str/int): Année à exporter
            output_file (str, optional): Nom du fichier CSV de sortie
        """
        self.base_dir = base_dir
        self.year = str(year)  # Convertir en string pour assurer la compatibilité
        
        # Définir le fichier de sortie
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = f"urls_{self.year}.csv"
        
        # Statistiques
        self.stats = {
            "year": self.year,
            "total_urls": 0,
            "months_found": [],
            "start_time": datetime.datetime.now().isoformat()
        }
        
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        if seconds == float('inf'):
            return "Inconnu"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def extract_urls_for_year(self, progress_callback=None):
        """
        Extrait toutes les URLs de l'année spécifiée
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
                
        Returns:
            bool: True si l'extraction a réussi, False sinon
        """
        start_time = time.time()
        
        # Vérifier si le dossier de l'année existe
        year_dir = os.path.join(self.base_dir, self.year)
        if not os.path.exists(year_dir):
            error_msg = f"Erreur : Le dossier pour l'année {self.year} n'existe pas dans {self.base_dir}"
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False
        
        # Trouver tous les fichiers .urls.txt dans les sous-dossiers de l'année
        url_files = []
        for month_dir in glob.glob(os.path.join(year_dir, "*")):
            if os.path.isdir(month_dir):
                month_name = os.path.basename(month_dir)
                self.stats["months_found"].append(month_name)
                
                # Chercher les fichiers d'URLs dans ce mois
                for url_file in glob.glob(os.path.join(month_dir, "*.urls.txt")):
                    url_files.append((month_name, url_file))
        
        if not url_files:
            error_msg = f"Aucun fichier d'URLs trouvé pour l'année {self.year}"
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False
        
        # Compter le nombre total d'URLs à traiter
        total_urls = 0
        for _, url_file in url_files:
            with open(url_file, 'r', encoding='utf-8') as f:
                total_urls += sum(1 for _ in f)
        
        self.stats["total_urls"] = total_urls
        
        if progress_callback:
            progress_callback(0, total_urls, f"Démarrage de l'export pour l'année {self.year} ({total_urls} URLs)")
        
        # Préparer le fichier CSV
        with open(self.output_file, 'w', encoding='utf-8', newline='') as csvfile:
            # Définir les en-têtes
            fieldnames = ["_id", "Name", "type", "Data", "Metadata", "Url", "Page", "Train status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            
            # Écrire l'en-tête
            writer.writeheader()
            
            # Initialiser la barre de progression
            pbar = tqdm(total=total_urls, desc=f"Export des URLs de {self.year}", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
            
            # Compteur pour le callback de progression
            processed_urls = 0
            
            # Parcourir tous les fichiers d'URLs
            for month_name, url_file in url_files:
                # Extraire le mois depuis le nom du fichier
                month_match = re.search(r'(\d{4})-(\d{2})\.urls\.txt', os.path.basename(url_file))
                month = month_match.group(2) if month_match else "00"
                
                # Lire les URLs du fichier
                with open(url_file, 'r', encoding='utf-8') as f:
                    for url in f:
                        url = url.strip()
                        if url:
                            # Conformément à l'exemple fourni, mettre l'URL dans Data
                            # et laisser vide _id, Name, Metadata, Url et Train status
                            writer.writerow({
                                "_id": "",
                                "Name": "",
                                "type": "web-site",
                                "Data": url,
                                "Metadata": "",
                                "Url": "",
                                "Page": url,
                                "Train status": ""
                            })
                            
                            # Mettre à jour la barre de progression
                            pbar.update(1)
                            
                            # Mettre à jour le compteur et le callback
                            processed_urls += 1
                            if progress_callback and processed_urls % 100 == 0:
                                progress_callback(processed_urls, total_urls, 
                                                f"Export {self.year}: {processed_urls}/{total_urls} URLs")
            
            # Fermer la barre de progression
            pbar.close()
        
        # Temps écoulé
        elapsed_time = time.time() - start_time
        
        # Mettre à jour les statistiques
        self.stats["elapsed_time"] = elapsed_time
        self.stats["elapsed_time_formatted"] = self.format_time(elapsed_time)
        self.stats["end_time"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder les statistiques
        stats_file = f"stats_export_{self.year}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        # Message final
        final_status = f"Export terminé en {self.format_time(elapsed_time)}\n" \
                      f"URLs exportées: {self.stats['total_urls']}\n" \
                      f"Fichier CSV créé: {self.output_file}"
        
        print(final_status)
        print(f"Statistiques sauvegardées dans: {stats_file}")
        
        # Mise à jour finale du callback de progression
        if progress_callback:
            progress_callback(total_urls, total_urls, final_status)
        
        return True


class MultiYearURLExporter:
    """Classe pour exporter les URLs de plusieurs années vers des fichiers CSV."""
    
    def __init__(self, base_dir, years=None, output_file=None, combine_into_one=False):
        """
        Initialise l'exporteur multi-années.
        
        Args:
            base_dir (str): Répertoire contenant les dossiers organisés par année
            years (list, optional): Liste des années à exporter
            output_file (str, optional): Nom du fichier CSV de sortie (pour l'export combiné)
            combine_into_one (bool, optional): Option pour combiner toutes les années dans un seul fichier
        """
        self.base_dir = base_dir
        self.years = years if years else []  # Liste des années à exporter
        self.output_file = output_file
        self.combine_into_one = combine_into_one  # Option pour combiner toutes les années dans un seul fichier
        
        # Statistiques
        self.stats = {
            "years": {},
            "total_urls": 0,
            "start_time": datetime.datetime.now().isoformat()
        }
    
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_available_years(self):
        """Récupère la liste des années disponibles dans le répertoire de base"""
        available_years = []
        for item in os.listdir(self.base_dir):
            if os.path.isdir(os.path.join(self.base_dir, item)) and item.isdigit():
                available_years.append(item)
        return sorted(available_years)
    
    def get_urls_for_year(self, year):
        """Récupère toutes les URLs pour une année donnée"""
        year_dir = os.path.join(self.base_dir, year)
        if not os.path.exists(year_dir):
            print(f"Avertissement : Le dossier pour l'année {year} n'existe pas")
            return []
        
        url_files = []
        for month_dir in glob.glob(os.path.join(year_dir, "*")):
            if os.path.isdir(month_dir):
                for url_file in glob.glob(os.path.join(month_dir, "*.urls.txt")):
                    url_files.append(url_file)
        
        # Aussi vérifier les URLs sans date si elles existent
        undated_dir = os.path.join(self.base_dir, "Sans_Date")
        if os.path.exists(undated_dir):
            for url_file in glob.glob(os.path.join(undated_dir, "*.txt")):
                url_files.append(url_file)
        
        # Lire toutes les URLs
        urls = []
        for url_file in url_files:
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url:
                        urls.append(url)
        
        return urls
    
    def export_to_csv(self, year, urls, output_file, progress_callback=None):
        """
        Exporte les URLs dans un fichier CSV au format spécifié
        
        Args:
            year (str): Année des URLs
            urls (list): Liste des URLs à exporter
            output_file (str): Nom du fichier CSV de sortie
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
        """
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            # Définir les en-têtes
            fieldnames = ["_id", "Name", "type", "Data", "Metadata", "Url", "Page", "Train status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            
            # Écrire l'en-tête
            writer.writeheader()
            
            # Initialiser la barre de progression
            total_urls = len(urls)
            pbar = tqdm(total=total_urls, desc=f"Écriture dans {output_file}", 
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            # Écrire chaque URL
            for i, url in enumerate(urls):
                writer.writerow({
                    "_id": "",
                    "Name": "",
                    "type": "web-site",
                    "Data": url,
                    "Metadata": "",
                    "Url": "",
                    "Page": url,
                    "Train status": ""
                })
                
                # Mettre à jour la barre de progression
                pbar.update(1)
                
                # Mettre à jour le callback de progression
                if progress_callback and i % 100 == 0:
                    progress_callback(i, total_urls, 
                                    f"Export {year}: {i}/{total_urls} URLs vers {output_file}")
            
            # Fermer la barre de progression
            pbar.close()
    
    def run(self, progress_callback=None):
        """
        Exécute l'export pour toutes les années sélectionnées
        
        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)
                
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        start_time = time.time()
        
        # Si aucune année n'est spécifiée, utiliser toutes les années disponibles
        if not self.years:
            self.years = self.get_available_years()
        
        # Vérifier qu'il y a des années à exporter
        if not self.years:
            error_msg = "Aucune année à exporter."
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False
        
        print(f"Exportation des années : {', '.join(self.years)}")
        if progress_callback:
            progress_callback(0, len(self.years), f"Préparation de l'export pour {len(self.years)} année(s)")
        
        # Si on combine tout dans un fichier
        if self.combine_into_one:
            combined_urls = []
            
            # Récupérer toutes les URLs
            for i, year in enumerate(self.years):
                if progress_callback:
                    progress_callback(i, len(self.years), f"Collecte des URLs pour l'année {year}")
                
                year_urls = self.get_urls_for_year(year)
                combined_urls.extend(year_urls)
                self.stats["years"][year] = len(year_urls)
                self.stats["total_urls"] += len(year_urls)
            
            # Exporter dans un seul fichier
            output_file = self.output_file or f"urls_combinees_{'-'.join(self.years)}.csv"
            self.export_to_csv("combined", combined_urls, output_file, progress_callback)
            
            print(f"\nExport combiné terminé. {len(combined_urls)} URLs exportées vers {output_file}")
        
        # Sinon, créer un fichier par année
        else:
            # Initialiser la barre de progression pour les années
            pbar = tqdm(total=len(self.years), desc="Traitement des années", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
            
            # Compteur pour le callback de progression
            processed_years = 0
            
            for year in self.years:
                if progress_callback:
                    progress_callback(processed_years, len(self.years), f"Export des URLs pour l'année {year}")
                
                year_urls = self.get_urls_for_year(year)
                
                if year_urls:
                    output_file = f"urls_{year}.csv" if not self.output_file else f"{os.path.splitext(self.output_file)[0]}_{year}.csv"
                    self.export_to_csv(year, year_urls, output_file, progress_callback)
                    
                    self.stats["years"][year] = len(year_urls)
                    self.stats["total_urls"] += len(year_urls)
                    
                    print(f"Année {year} : {len(year_urls)} URLs exportées vers {output_file}")
                
                # Mettre à jour la barre de progression
                pbar.update(1)
                processed_years += 1
            
            # Fermer la barre de progression
            pbar.close()
        
        # Temps écoulé
        elapsed_time = time.time() - start_time
        
        # Compléter les statistiques
        self.stats["elapsed_time"] = elapsed_time
        self.stats["elapsed_time_formatted"] = self.format_time(elapsed_time)
        self.stats["end_time"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder les statistiques
        stats_file = f"stats_export_{'combined' if self.combine_into_one else 'multi'}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        # Message final
        final_status = f"Export terminé en {self.format_time(elapsed_time)}\n" \
                      f"Total d'URLs exportées: {self.stats['total_urls']}"
                      
        for year, count in self.stats["years"].items():
            final_status += f"\n  - {year}: {count} URLs"
            
        print(final_status)
        print(f"Statistiques sauvegardées dans: {stats_file}")
        
        # Mise à jour finale du callback de progression
        if progress_callback:
            progress_callback(len(self.years), len(self.years), final_status)
        
        return True


if __name__ == "__main__":
    print("=== EXTRACTEUR D'URLs MULTI-ANNÉES VERS CSV ===")
    print("Ce script permet d'exporter les URLs de plusieurs années dans des fichiers CSV.")
    
    # Demander le répertoire contenant les dossiers organisés par année
    base_dir = input("Répertoire contenant les dossiers par année: ")
    if not os.path.exists(base_dir):
        print(f"Erreur: Le répertoire {base_dir} n'existe pas.")
        exit(1)
    
    # Récupérer les années disponibles
    available_years = []
    for item in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, item)) and item.isdigit():
            available_years.append(item)
    
    available_years.sort()
    
    if not available_years:
        print(f"Aucun dossier d'année trouvé dans {base_dir}")
        exit(1)
    
    # Afficher les années disponibles
    print("\nAnnées disponibles:")
    for year in available_years:
        print(f"  - {year}")
    
    # Options d'exportation
    print("\nOptions d'exportation:")
    print("1. Exporter toutes les années (un fichier CSV par année)")
    print("2. Exporter une sélection d'années (un fichier CSV par année)")
    print("3. Combiner toutes les années dans un seul fichier CSV")
    print("4. Combiner une sélection d'années dans un seul fichier CSV")
    
    option = input("\nChoisissez une option (1-4): ")
    
    years_to_export = []
    combine_into_one = False
    
    if option == "1":
        years_to_export = available_years
    elif option == "2":
        year_input = input("Entrez les années à exporter, séparées par des virgules (ex: 2022,2023): ")
        years_to_export = [year.strip() for year in year_input.split(",") if year.strip() in available_years]
    elif option == "3":
        years_to_export = available_years
        combine_into_one = True
    elif option == "4":
        year_input = input("Entrez les années à combiner, séparées par des virgules (ex: 2022,2023): ")
        years_to_export = [year.strip() for year in year_input.split(",") if year.strip() in available_years]
        combine_into_one = True
    else:
        print("Option non valide.")
        exit(1)
    
    if not years_to_export:
        print("Aucune année valide sélectionnée.")
        exit(1)
    
    # Demander le nom du fichier de sortie pour l'option combinée
    output_file = None
    if combine_into_one:
        output_file = input(f"Nom du fichier CSV combiné (par défaut: urls_combinees_{'-'.join(years_to_export)}.csv): ") or None
    
    # Exécuter l'exportation
    print(f"\nDémarrage de l'export pour {len(years_to_export)} année(s): {', '.join(years_to_export)}")
    
    try:
        exporter = MultiYearURLExporter(base_dir, years_to_export, output_file, combine_into_one)
        exporter.run()
    except KeyboardInterrupt:
        print("\nExport interrompu par l'utilisateur.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
        import traceback
        traceback.print_exc()