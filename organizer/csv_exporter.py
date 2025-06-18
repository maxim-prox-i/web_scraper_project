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
import sys

# Ajouter le répertoire racine du projet au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tqdm import tqdm
import subprocess
from utils.common_utils import extract_domain, ensure_data_directory


class DirectURLExporter:
    """Classe pour exporter directement un fichier d'URLs vers un fichier CSV."""

    def __init__(self, input_file, output_file=None):
        """
        Initialise l'exporteur direct d'URLs vers CSV.

        Args:
            input_file (str): Fichier contenant les URLs (format .txt)
            output_file (str, optional): Nom du fichier CSV de sortie
        """
        self.input_file = input_file

        # Déterminer le domaine à partir du fichier ou du contenu
        parent_dir = os.path.basename(os.path.dirname(os.path.abspath(input_file)))
        if parent_dir != "data" and not parent_dir.startswith("."):
            self.domain = parent_dir
        else:
            # Essayer de déterminer le domaine à partir de la première URL
            self.domain = "unknown_domain"
            try:
                with open(input_file, "r", encoding="utf-8") as f:
                    first_url = f.readline().strip()
                    if first_url:
                        self.domain = extract_domain(first_url)
            except:
                pass

        # Définir le fichier de sortie
        if output_file:
            if os.path.isabs(output_file):
                self.output_file = output_file
            else:
                domain_dir = ensure_data_directory(self.domain)
                self.output_file = os.path.join(domain_dir, output_file)
        else:
            domain_dir = ensure_data_directory(self.domain)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            self.output_file = os.path.join(domain_dir, f"{base_name}_export.csv")

        # Statistiques
        self.stats = {
            "input_file": self.input_file,
            "output_file": self.output_file,
            "total_urls": 0,
            "start_time": datetime.datetime.now().isoformat(),
        }

    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        if seconds == float("inf"):
            return "Inconnu"

        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def export_urls_to_csv(self, progress_callback=None):
        """
        Exporte directement les URLs d'un fichier texte vers un fichier CSV

        Args:
            progress_callback (callable, optional): Fonction callback pour mettre à jour la progression
                Signature: callback(current_progress, max_progress, status_message)

        Returns:
            bool: True si l'export a réussi, False sinon
        """
        start_time = time.time()

        # Vérifier si le fichier d'entrée existe
        if not os.path.exists(self.input_file):
            error_msg = f"Erreur : Le fichier {self.input_file} n'existe pas"
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False

        # Compter le nombre total d'URLs
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            error_msg = (
                f"Erreur lors de la lecture du fichier {self.input_file}: {str(e)}"
            )
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False

        total_urls = len(urls)
        self.stats["total_urls"] = total_urls

        if total_urls == 0:
            error_msg = "Aucune URL trouvée dans le fichier"
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False

        if progress_callback:
            progress_callback(
                0, total_urls, f"Démarrage de l'export direct pour {total_urls} URLs"
            )

        # Créer le fichier CSV
        try:
            with open(self.output_file, "w", encoding="utf-8", newline="") as csvfile:
                # Définir les en-têtes
                fieldnames = [
                    "_id",
                    "Name",
                    "type",
                    "Data",
                    "Metadata",
                    "Url",
                    "Page",
                    "Train status",
                ]
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=";",
                    quotechar='"',
                    quoting=csv.QUOTE_ALL,
                )

                # Écrire l'en-tête
                writer.writeheader()

                # Initialiser la barre de progression
                pbar = tqdm(
                    total=total_urls,
                    desc="Export direct des URLs",
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                )

                # Traitement par lots pour de meilleures performances
                batch_size = 1000
                rows_batch = []

                for i, url in enumerate(urls):
                    if url:  # Vérifier que l'URL n'est pas vide
                        row = {
                            "_id": "",
                            "Name": "",
                            "type": "web-site",
                            "Data": url,
                            "Metadata": "",
                            "Url": "",
                            "Page": url,
                            "Train status": "",
                        }
                        rows_batch.append(row)

                        # Si le lot atteint la taille maximale, écrire et réinitialiser
                        if len(rows_batch) >= batch_size:
                            writer.writerows(rows_batch)
                            pbar.update(len(rows_batch))
                            rows_batch = []

                            # Mettre à jour le callback
                            if progress_callback:
                                progress_callback(
                                    i + 1,
                                    total_urls,
                                    f"Export direct: {i + 1}/{total_urls} URLs",
                                )

                # Écrire le reste du lot
                if rows_batch:
                    writer.writerows(rows_batch)
                    pbar.update(len(rows_batch))

                    # Mettre à jour le callback
                    if progress_callback:
                        progress_callback(
                            total_urls,
                            total_urls,
                            f"Export direct: {total_urls}/{total_urls} URLs",
                        )

                # Fermer la barre de progression
                pbar.close()

        except Exception as e:
            error_msg = f"Erreur lors de l'écriture du fichier CSV: {str(e)}"
            print(error_msg)
            if progress_callback:
                progress_callback(0, 0, error_msg)
            return False

        # Temps écoulé
        elapsed_time = time.time() - start_time

        # Mettre à jour les statistiques
        self.stats["elapsed_time"] = elapsed_time
        self.stats["elapsed_time_formatted"] = self.format_time(elapsed_time)
        self.stats["end_time"] = datetime.datetime.now().isoformat()

        # Sauvegarder les statistiques
        stats_file = f"{os.path.splitext(self.output_file)[0]}_stats.json"
        try:
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Avertissement: Impossible de sauvegarder les statistiques: {e}")

        # Message final
        final_status = (
            f"Export direct terminé en {self.format_time(elapsed_time)}\n"
            f"URLs exportées: {self.stats['total_urls']}\n"
            f"Fichier CSV créé: {self.output_file}"
        )

        print(final_status)
        if os.path.exists(stats_file):
            print(f"Statistiques sauvegardées dans: {stats_file}")

        # Mise à jour finale du callback de progression
        if progress_callback:
            progress_callback(total_urls, total_urls, final_status)

        return True


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

        # Déterminer le domaine à partir du chemin
        path_parts = base_dir.split(os.sep)
        domain_index = -1
        for i, part in enumerate(path_parts):
            if part == "data" and i + 1 < len(path_parts):
                domain_index = i + 1
                break

        if domain_index >= 0 and domain_index < len(path_parts):
            self.domain = path_parts[domain_index]
        else:
            self.domain = "unknown_domain"

        # Définir le fichier de sortie
        if output_file:
            if os.path.isabs(output_file):
                self.output_file = output_file
            else:
                domain_dir = ensure_data_directory(self.domain)
                self.output_file = os.path.join(domain_dir, output_file)
        else:
            domain_dir = ensure_data_directory(self.domain)
            self.output_file = os.path.join(domain_dir, f"urls_{self.year}.csv")

        # Statistiques
        self.stats = {
            "year": self.year,
            "total_urls": 0,
            "months_found": [],
            "start_time": datetime.datetime.now().isoformat(),
        }

    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        if seconds == float("inf"):
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

        # Compter le nombre total d'URLs à traiter - utiliser wc -l sous Linux/Mac ou équivalent sous Windows
        total_urls = 0
        for _, url_file in url_files:
            # Méthode optimisée pour compter les lignes
            try:
                if os.name == "posix":  # Linux/Mac
                    result = subprocess.run(
                        ["wc", "-l", url_file], capture_output=True, text=True
                    )
                    total_urls += int(result.stdout.split()[0])
                else:  # Windows ou autre - méthode moins efficace mais fonctionnelle
                    with open(url_file, "rb") as f:
                        # Compter les retours à la ligne
                        total_urls += sum(
                            1 for _ in iter(lambda: f.read(1024 * 1024).count(b"\n"), 0)
                        )
            except Exception:
                # Fallback en cas d'erreur
                with open(url_file, "r", encoding="utf-8") as f:
                    total_urls += sum(1 for _ in f)

        self.stats["total_urls"] = total_urls

        if progress_callback:
            progress_callback(
                0,
                total_urls,
                f"Démarrage de l'export pour l'année {self.year} ({total_urls} URLs)",
            )

        # Préparer le fichier CSV - utiliser un buffer plus grand pour l'écriture
        with open(
            self.output_file, "w", encoding="utf-8", newline="", buffering=1024 * 1024
        ) as csvfile:
            # Définir les en-têtes
            fieldnames = [
                "_id",
                "Name",
                "type",
                "Data",
                "Metadata",
                "Url",
                "Page",
                "Train status",
            ]
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                delimiter=";",
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )

            # Écrire l'en-tête
            writer.writeheader()

            # Initialiser la barre de progression
            pbar = tqdm(
                total=total_urls,
                desc=f"Export des URLs de {self.year}",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            )

            # Compteur pour le callback de progression
            processed_urls = 0

            # Taille de buffer pour la lecture
            buffer_size = 8192  # 8KB buffer

            # Parcourir tous les fichiers d'URLs
            for month_name, url_file in url_files:
                # Extraire le mois depuis le nom du fichier
                month_match = re.search(
                    r"(\d{4})-(\d{2})\.urls\.txt", os.path.basename(url_file)
                )
                month = month_match.group(2) if month_match else "00"

                # Lire les URLs du fichier en utilisant un buffer
                with open(url_file, "r", encoding="utf-8") as f:
                    # Préparation du modèle de ligne pour réduire les allocations
                    row_template = {
                        "_id": "",
                        "Name": "",
                        "type": "web-site",
                        "Data": None,  # Sera remplacé par l'URL
                        "Metadata": "",
                        "Url": "",
                        "Page": None,  # Sera remplacé par l'URL
                        "Train status": "",
                    }

                    # Traitement par lots
                    batch_size = 1000
                    urls_batch = []

                    for url in f:
                        url = url.strip()
                        if url:
                            row = row_template.copy()
                            row["Data"] = url
                            row["Page"] = url
                            urls_batch.append(row)

                            # Si le lot atteint la taille maximale, écrire et réinitialiser
                            if len(urls_batch) >= batch_size:
                                writer.writerows(urls_batch)
                                processed_urls += len(urls_batch)
                                pbar.update(len(urls_batch))
                                urls_batch = []

                                # Mettre à jour le callback
                                if (
                                    progress_callback
                                    and processed_urls % (batch_size * 2) == 0
                                ):
                                    progress_callback(
                                        processed_urls,
                                        total_urls,
                                        f"Export {self.year}: {processed_urls}/{total_urls} URLs",
                                    )

                    # Écrire le reste du lot
                    if urls_batch:
                        writer.writerows(urls_batch)
                        processed_urls += len(urls_batch)
                        pbar.update(len(urls_batch))

                        # Mettre à jour le callback
                        if progress_callback:
                            progress_callback(
                                processed_urls,
                                total_urls,
                                f"Export {self.year}: {processed_urls}/{total_urls} URLs",
                            )

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
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

        # Message final
        final_status = (
            f"Export terminé en {self.format_time(elapsed_time)}\n"
            f"URLs exportées: {self.stats['total_urls']}\n"
            f"Fichier CSV créé: {self.output_file}"
        )

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

        # Déterminer le domaine à partir du chemin
        path_parts = base_dir.split(os.sep)
        domain_index = -1
        for i, part in enumerate(path_parts):
            if part == "data" and i + 1 < len(path_parts):
                domain_index = i + 1
                break

        if domain_index >= 0 and domain_index < len(path_parts):
            self.domain = path_parts[domain_index]
        else:
            self.domain = "unknown_domain"

        self.domain_dir = ensure_data_directory(self.domain)

        # Définir le fichier de sortie
        if output_file:
            if os.path.isabs(output_file):
                self.output_file = output_file
            else:
                self.output_file = os.path.join(self.domain_dir, output_file)
        else:
            self.output_file = None

        self.combine_into_one = combine_into_one  # Option pour combiner toutes les années dans un seul fichier

        # Statistiques
        self.stats = {
            "years": {},
            "total_urls": 0,
            "start_time": datetime.datetime.now().isoformat(),
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
            with open(url_file, "r", encoding="utf-8") as f:
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
        with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
            # Définir les en-têtes
            fieldnames = [
                "_id",
                "Name",
                "type",
                "Data",
                "Metadata",
                "Url",
                "Page",
                "Train status",
            ]
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                delimiter=";",
                quotechar='"',
                quoting=csv.QUOTE_ALL,
            )

            # Écrire l'en-tête
            writer.writeheader()

            # Initialiser la barre de progression
            total_urls = len(urls)
            pbar = tqdm(
                total=total_urls,
                desc=f"Écriture dans {output_file}",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            )

            # Écrire chaque URL
            for i, url in enumerate(urls):
                writer.writerow(
                    {
                        "_id": "",
                        "Name": "",
                        "type": "web-site",
                        "Data": url,
                        "Metadata": "",
                        "Url": "",
                        "Page": url,
                        "Train status": "",
                    }
                )

                # Mettre à jour la barre de progression
                pbar.update(1)

                # Mettre à jour le callback de progression
                if progress_callback and i % 100 == 0:
                    progress_callback(
                        i,
                        total_urls,
                        f"Export {year}: {i}/{total_urls} URLs vers {output_file}",
                    )

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
            progress_callback(
                0,
                len(self.years),
                f"Préparation de l'export pour {len(self.years)} année(s)",
            )

        # Si on combine tout dans un fichier
        if self.combine_into_one:
            combined_urls = []

            # Récupérer toutes les URLs
            for i, year in enumerate(self.years):
                if progress_callback:
                    progress_callback(
                        i, len(self.years), f"Collecte des URLs pour l'année {year}"
                    )

                year_urls = self.get_urls_for_year(year)
                combined_urls.extend(year_urls)
                self.stats["years"][year] = len(year_urls)
                self.stats["total_urls"] += len(year_urls)

            # Exporter dans un seul fichier
            output_file = (
                self.output_file or f"urls_combinees_{'-'.join(self.years)}.csv"
            )
            self.export_to_csv(
                "combined", combined_urls, output_file, progress_callback
            )

            print(
                f"\nExport combiné terminé. {len(combined_urls)} URLs exportées vers {output_file}"
            )

        # Sinon, créer un fichier par année
        else:
            # Initialiser la barre de progression pour les années
            pbar = tqdm(
                total=len(self.years),
                desc="Traitement des années",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            )

            # Compteur pour le callback de progression
            processed_years = 0

            for year in self.years:
                if progress_callback:
                    progress_callback(
                        processed_years,
                        len(self.years),
                        f"Export des URLs pour l'année {year}",
                    )

                year_urls = self.get_urls_for_year(year)

                if year_urls:
                    output_file = (
                        f"urls_{year}.csv"
                        if not self.output_file
                        else f"{os.path.splitext(self.output_file)[0]}_{year}.csv"
                    )
                    self.export_to_csv(year, year_urls, output_file, progress_callback)

                    self.stats["years"][year] = len(year_urls)
                    self.stats["total_urls"] += len(year_urls)

                    print(
                        f"Année {year} : {len(year_urls)} URLs exportées vers {output_file}"
                    )

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
        stats_file = (
            f"stats_export_{'combined' if self.combine_into_one else 'multi'}.json"
        )
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

        # Message final
        final_status = (
            f"Export terminé en {self.format_time(elapsed_time)}\n"
            f"Total d'URLs exportées: {self.stats['total_urls']}"
        )

        for year, count in self.stats["years"].items():
            final_status += f"\n  - {year}: {count} URLs"

        print(final_status)
        print(f"Statistiques sauvegardées dans: {stats_file}")

        # Mise à jour finale du callback de progression
        if progress_callback:
            progress_callback(len(self.years), len(self.years), final_status)

        return True


if __name__ == "__main__":
    print("=== EXTRACTEUR D'URLs VERS CSV ===")
    print("Ce script permet d'exporter des URLs dans des fichiers CSV.")
    print("1. Export direct d'un fichier texte d'URLs")
    print("2. Export multi-années depuis une structure organisée")

    choice = input("\nChoisissez le type d'export (1 ou 2): ")

    if choice == "1":
        # Export direct
        input_file = input("Fichier contenant les URLs (ex: urls.txt): ")
        if not os.path.exists(input_file):
            print(f"Erreur: Le fichier {input_file} n'existe pas.")
            exit(1)

        output_file = (
            input("Nom du fichier CSV de sortie (laissez vide pour auto): ") or None
        )

        print(f"\nDémarrage de l'export direct depuis {input_file}")

        try:
            exporter = DirectURLExporter(input_file, output_file)
            result = exporter.export_urls_to_csv()
            if result:
                print("Export terminé avec succès!")
            else:
                print("Erreur lors de l'export.")
        except Exception as e:
            print(f"Une erreur est survenue: {e}")

    elif choice == "2":
        # Export multi-années (code existant)
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
            year_input = input(
                "Entrez les années à exporter, séparées par des virgules (ex: 2022,2023): "
            )
            years_to_export = [
                year.strip()
                for year in year_input.split(",")
                if year.strip() in available_years
            ]
        elif option == "3":
            years_to_export = available_years
            combine_into_one = True
        elif option == "4":
            year_input = input(
                "Entrez les années à combiner, séparées par des virgules (ex: 2022,2023): "
            )
            years_to_export = [
                year.strip()
                for year in year_input.split(",")
                if year.strip() in available_years
            ]
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
            output_file = (
                input(
                    f"Nom du fichier CSV combiné (par défaut: urls_combinees_{'-'.join(years_to_export)}.csv): "
                )
                or None
            )

        # Exécuter l'exportation
        print(
            f"\nDémarrage de l'export pour {len(years_to_export)} année(s): {', '.join(years_to_export)}"
        )

        try:
            exporter = MultiYearURLExporter(
                base_dir, years_to_export, output_file, combine_into_one
            )
            exporter.run()
        except KeyboardInterrupt:
            print("\nExport interrompu par l'utilisateur.")
        except Exception as e:
            print(f"\nUne erreur est survenue: {e}")
            import traceback

            traceback.print_exc()

    else:
        print("Choix non valide.")
        exit(1)
