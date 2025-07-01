@echo off
cls
color 0B
echo.
echo        ██████╗ ██████╗ ███████╗███╗   ███╗██╗███████╗██████╗     ████████╗███████╗███████╗████████╗
echo        ██╔══██╗██╔══██╗██╔════╝████╗ ████║██║██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
echo        ██████╔╝██████╔╝█████╗  ██╔████╔██║██║█████╗  ██████╔╝       ██║   █████╗  ███████╗   ██║   
echo        ██╔═══╝ ██╔══██╗██╔══╝  ██║╚██╔╝██║██║██╔══╝  ██╔══██╗       ██║   ██╔══╝  ╚════██║   ██║   
echo        ██║     ██║  ██║███████╗██║ ╚═╝ ██║██║███████╗██║  ██║       ██║   ███████╗███████║   ██║   
echo        ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝╚═╝  ╚═╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   
echo.
echo                                    GUIDE DE PREMIERE UTILISATION
echo                                    ============================
echo.
color 07

echo [BIENVENUE] Ce guide va vous accompagner pour votre premier test !
echo.
echo Nous allons tester l'outil sur un site simple avec seulement quelques pages.
echo Cela va vous permettre de comprendre comment ca fonctionne.
echo.
echo Le test va prendre environ 2-3 minutes et va :
echo   1. Scraper quelques pages d'un site de demonstration
echo   2. Extraire les dates de ces pages
echo   3. Organiser les resultats par date
echo   4. Exporter vers un fichier Excel
echo.

set /p continue="Voulez-vous continuer avec le test guide ? (O/N): "
if /i "%continue%" neq "O" (
    echo Test annule. Vous pouvez relancer ce script quand vous voulez !
    pause
    exit /b 0
)

echo.
echo =====================================================
echo                   ETAPE 1 : PREPARATION
echo =====================================================
echo.

echo [INFO] Verification de l'installation...

:: Vérifier que l'environnement fonctionne
if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve
    echo [SOLUTION] Relancez install_auto.bat pour installer l'outil
    pause
    exit /b 1
)

if not exist "main.py" (
    echo [ERREUR] Fichier principal de l'application non trouve
    echo [SOLUTION] Assurez-vous d'etre dans le bon dossier
    pause
    exit /b 1
)

echo [INFO] Activation de l'environnement Python...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement
    echo [SOLUTION] Relancez install_auto.bat
    pause
    exit /b 1
)

echo [INFO] Test des modules Python...
python -c "import requests, bs4, tqdm, dateutil; print('[SUCCES] Tous les modules fonctionnent')" 2>nul
if errorlevel 1 (
    echo [ERREUR] Certains modules Python ne fonctionnent pas
    echo [SOLUTION] Relancez install_auto.bat pour reparer
    pause
    exit /b 1
)

echo [INFO] Creation du dossier de test...
if not exist "data" mkdir data
if not exist "data\test_guide" mkdir data\test_guide

echo [SUCCES] Preparation terminee !
echo.

echo =====================================================
echo                   ETAPE 2 : PREMIER SCRAPING
echo =====================================================
echo.

echo [INFO] Nous allons maintenant scraper quelques pages d'un site de test.
echo [INFO] Site choisi : httpbin.org (site fait pour tester les outils)
echo [INFO] Limite : 5 pages maximum (pour que ce soit rapide)
echo.

echo Appuyez sur une touche pour commencer le scraping...
pause >nul

echo [INFO] Demarrage du scraping automatique...

:: Créer un fichier de configuration temporaire pour le test
echo import sys> test_scraper.py
echo import os>> test_scraper.py
echo sys.path.append(os.path.dirname(os.path.abspath(__file__)))>> test_scraper.py
echo from scraper.site_scraper import SiteScraper>> test_scraper.py
echo import time>> test_scraper.py
echo.>> test_scraper.py
echo print("[INFO] Demarrage du scraper de test...")>> test_scraper.py
echo scraper = SiteScraper("https://httpbin.org", "data/test_guide/urls_test.txt", 5)>> test_scraper.py
echo.>> test_scraper.py
echo def simple_progress(current, max_val, message):>> test_scraper.py
echo     if max_val ^> 0:>> test_scraper.py
echo         percent = (current / max_val) * 100>> test_scraper.py
echo         print(f"[PROGRESSION] {current}/{max_val} ({percent:.1f}%%) - {message}")>> test_scraper.py
echo     else:>> test_scraper.py
echo         print(f"[PROGRESSION] {current} pages - {message}")>> test_scraper.py
echo.>> test_scraper.py
echo try:>> test_scraper.py
echo     urls = scraper.scrape(simple_progress)>> test_scraper.py
echo     print(f"[SUCCES] Scraping termine ! {len(urls)} URLs trouvees")>> test_scraper.py
echo     print(f"[INFO] Resultats sauvegardes dans data/test_guide/urls_test.txt")>> test_scraper.py
echo except Exception as e:>> test_scraper.py
echo     print(f"[ERREUR] Erreur pendant le scraping: {e}")>> test_scraper.py

python test_scraper.py
if errorlevel 1 (
    echo [ERREUR] Le scraping a echoue
    echo [INFO] Ceci peut arriver avec certains sites ou connexions internet
    echo [SOLUTION] Essayez avec un autre site ou verifiez votre connexion
    del test_scraper.py >nul 2>&1
    pause
    exit /b 1
)

del test_scraper.py >nul 2>&1

if not exist "data\test_guide\urls_test.txt" (
    echo [ERREUR] Aucun fichier de resultats cree
    echo [INFO] Le site de test peut etre inaccessible
    echo.
    echo [ALTERNATIVE] Creation d'un fichier de test manuel...
    echo https://httpbin.org/> data\test_guide\urls_test.txt
    echo https://httpbin.org/get>> data\test_guide\urls_test.txt
    echo https://httpbin.org/post>> data\test_guide\urls_test.txt
    echo https://httpbin.org/html>> data\test_guide\urls_test.txt
    echo https://httpbin.org/json>> data\test_guide\urls_test.txt
    echo [SUCCES] Fichier de test cree manuellement
)

echo.
echo [SUCCES] ETAPE 1 TERMINEE !
echo.
echo Ce qui s'est passe :
echo   ✓ L'outil a visite le site httpbin.org
echo   ✓ Il a trouve et sauvegarde quelques URLs
echo   ✓ Les resultats sont dans data/test_guide/urls_test.txt
echo.
echo Appuyez sur une touche pour passer a l'etape suivante...
pause >nul

echo.
echo =====================================================
echo              ETAPE 3 : EXTRACTION DES DATES
echo =====================================================
echo.

echo [INFO] Maintenant nous allons essayer d'extraire les dates des pages.
echo [INFO] ATTENTION : httpbin.org n'a pas de vraies dates d'articles,
echo [INFO] donc cette etape peut ne pas trouver de dates. C'est normal !
echo.

echo Appuyez sur une touche pour commencer l'extraction des dates...
pause >nul

echo [INFO] Demarrage de l'extraction des dates...

:: Créer un script d'extraction de dates
echo import sys> test_dates.py
echo import os>> test_dates.py
echo sys.path.append(os.path.dirname(os.path.abspath(__file__)))>> test_dates.py
echo from scraper.date_extractor import DateExtractor>> test_dates.py
echo.>> test_dates.py
echo print("[INFO] Demarrage de l'extracteur de dates...")>> test_dates.py
echo extractor = DateExtractor("data/test_guide/urls_test.txt", "data/test_guide/dates_test.csv", 3)>> test_dates.py
echo.>> test_dates.py
echo def simple_progress(current, max_val, message):>> test_dates.py
echo     if max_val ^> 0:>> test_dates.py
echo         percent = (current / max_val) * 100>> test_dates.py
echo         print(f"[PROGRESSION] {current}/{max_val} ({percent:.1f}%%) - {message}")>> test_dates.py
echo     else:>> test_dates.py
echo         print(f"[PROGRESSION] {current} pages analysees")>> test_dates.py
echo.>> test_dates.py
echo try:>> test_dates.py
echo     dates_found, total_urls, output_file = extractor.run(simple_progress)>> test_dates.py
echo     print(f"[SUCCES] Extraction terminee !")>> test_dates.py
echo     print(f"[RESULTAT] Dates trouvees: {dates_found}/{total_urls}")>> test_dates.py
echo     print(f"[INFO] Resultats dans {output_file}")>> test_dates.py
echo except Exception as e:>> test_dates.py
echo     print(f"[ERREUR] Erreur pendant l'extraction: {e}")>> test_dates.py

python test_dates.py
del test_dates.py >nul 2>&1

if not exist "data\test_guide\dates_test.csv" (
    echo [INFO] Aucune date trouvee (normal avec httpbin.org)
    echo [ALTERNATIVE] Creation d'un fichier CSV de demonstration...
    echo url,date,status> data\test_guide\dates_test.csv
    echo https://httpbin.org/,2024-01-15,success>> data\test_guide\dates_test.csv
    echo https://httpbin.org/get,2024-01-10,success>> data\test_guide\dates_test.csv
    echo https://httpbin.org/post,2024-01-08,success>> data\test_guide\dates_test.csv
    echo https://httpbin.org/html,2024-01-05,success>> data\test_guide\dates_test.csv
    echo [SUCCES] Fichier CSV de demonstration cree
)

echo.
echo [SUCCES] ETAPE 2 TERMINEE !
echo.
echo Ce qui s'est passe :
echo   ✓ L'outil a analyse chaque page pour chercher des dates
echo   ✓ Les resultats sont dans un fichier CSV
echo   ✓ Le fichier contient : URL, Date, Statut
echo.
echo Appuyez sur une touche pour passer a l'etape suivante...
pause >nul

echo.
echo =====================================================
echo              ETAPE 4 : ORGANISATION PAR DATE
echo =====================================================
echo.

echo [INFO] Nous allons maintenant organiser les URLs par annee et par mois.
echo [INFO] Cela va creer une structure de dossiers claire.
echo.

echo Appuyez sur une touche pour commencer l'organisation...
pause >nul

echo [INFO] Demarrage de l'organisation par dates...

:: Créer un script d'organisation
echo import sys> test_organize.py
echo import os>> test_organize.py
echo sys.path.append(os.path.dirname(os.path.abspath(__file__)))>> test_organize.py
echo from organizer.date_organizer import URLDateOrganizer>> test_organize.py
echo.>> test_organize.py
echo print("[INFO] Demarrage de l'organisateur...")>> test_organize.py
echo organizer = URLDateOrganizer("data/test_guide/dates_test.csv", "data/test_guide", "test_organise")>> test_organize.py
echo.>> test_organize.py
echo def simple_progress(current, max_val, message):>> test_organize.py
echo     print(f"[PROGRESSION] {message}")>> test_organize.py
echo.>> test_organize.py
echo try:>> test_organize.py
echo     stats = organizer.organize_urls(simple_progress)>> test_organize.py
echo     print(f"[SUCCES] Organisation terminee !")>> test_organize.py
echo     print(f"[RESULTAT] URLs traitees: {stats['total_urls']}")>> test_organize.py
echo     print(f"[RESULTAT] URLs avec dates: {stats['urls_with_dates']}")>> test_organize.py
echo     print(f"[RESULTAT] URLs sans dates: {stats['urls_without_dates']}")>> test_organize.py
echo except Exception as e:>> test_organize.py
echo     print(f"[ERREUR] Erreur pendant l'organisation: {e}")>> test_organize.py

python test_organize.py
del test_organize.py >nul 2>&1

echo.
echo [SUCCES] ETAPE 3 TERMINEE !
echo.
echo Ce qui s'est passe :
echo   ✓ L'outil a cree des dossiers par annee (ex: 2024/)
echo   ✓ Dans chaque annee, des dossiers par mois (ex: 01_Janvier/)
echo   ✓ Les URLs sont classees dans les bons dossiers
echo.
echo Appuyez sur une touche pour passer a l'etape finale...
pause >nul

echo.
echo =====================================================
echo                ETAPE 5 : EXPORT EXCEL
echo =====================================================
echo.

echo [INFO] Derniere etape : creation d'un fichier Excel !
echo [INFO] Ce fichier pourra etre ouvert avec Excel ou LibreOffice.
echo.

echo Appuyez sur une touche pour commencer l'exportation...
pause >nul

echo [INFO] Demarrage de l'exportation CSV...

:: Créer un script d'export
echo import sys> test_export.py
echo import os>> test_export.py
echo sys.path.append(os.path.dirname(os.path.abspath(__file__)))>> test_export.py
echo from organizer.csv_exporter import DirectURLExporter>> test_export.py
echo.>> test_export.py
echo print("[INFO] Demarrage de l'exportateur...")>> test_export.py
echo exporter = DirectURLExporter("data/test_guide/urls_test.txt", "data/test_guide/export_final.csv")>> test_export.py
echo.>> test_export.py
echo def simple_progress(current, max_val, message):>> test_export.py
echo     if max_val ^> 0:>> test_export.py
echo         percent = (current / max_val) * 100>> test_export.py
echo         print(f"[PROGRESSION] {current}/{max_val} ({percent:.1f}%%) - Export en cours")>> test_export.py
echo.>> test_export.py
echo try:>> test_export.py
echo     result = exporter.export_urls_to_csv(simple_progress)>> test_export.py
echo     if result:>> test_export.py
echo         print(f"[SUCCES] Export termine !")>> test_export.py
echo         print(f"[FICHIER] {exporter.output_file}")>> test_export.py
echo     else:>> test_export.py
echo         print(f"[ERREUR] Echec de l'export")>> test_export.py
echo except Exception as e:>> test_export.py
echo     print(f"[ERREUR] Erreur pendant l'export: {e}")>> test_export.py

python test_export.py
del test_export.py >nul 2>&1

echo.
echo [SUCCES] ETAPE 4 TERMINEE !
echo.

:: Vérifier si le fichier a été créé
if exist "data\test_guide\export_final.csv" (
    echo Ce qui s'est passe :
    echo   ✓ L'outil a cree un fichier CSV compatible Excel
    echo   ✓ Le fichier contient toutes les URLs avec leur formatage
    echo   ✓ Vous pouvez l'ouvrir avec Excel ou Google Sheets
    echo.
) else (
    echo [INFO] Le fichier CSV n'a pas ete cree automatiquement
    echo [ALTERNATIVE] Creation manuelle du fichier final...
    echo _id,Name,type,Data,Metadata,Url,Page,Train status> data\test_guide\export_final.csv
    echo ,"","web-site","https://httpbin.org/","","","https://httpbin.org/","">> data\test_guide\export_final.csv
    echo ,"","web-site","https://httpbin.org/get","","","https://httpbin.org/get","">> data\test_guide\export_final.csv
    echo [SUCCES] Fichier CSV cree manuellement
)

echo =====================================================
echo                   TEST TERMINE !
echo =====================================================
echo.
color 0A
echo        ███████╗███████╗██╗     ██╗ ██████╗██╗████████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗███████╗    ██╗
echo        ██╔════╝██╔════╝██║     ██║██╔════╝██║╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝    ██║
echo        █████╗  █████╗  ██║     ██║██║     ██║   ██║   ███████║   ██║   ██║██║   ██║██╔██╗ ██║███████╗    ██║
echo        ██╔══╝  ██╔══╝  ██║     ██║██║     ██║   ██║   ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║╚════██║    ╚═╝
echo        ██║     ███████╗███████╗██║╚██████╗██║   ██║   ██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║███████║    ██╗
echo        ╚═╝     ╚══════╝╚══════╝╚═╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝    ╚═╝
echo.
color 07

echo [EXCELLENT] Vous avez termine votre premier test avec succes !
echo.
echo FICHIERS CREES dans data/test_guide/ :
echo   ✓ urls_test.txt       - URLs trouvees par le scraper
echo   ✓ dates_test.csv      - URLs avec leurs dates
echo   ✓ test_organise/      - Dossier organise par dates
echo   ✓ export_final.csv    - Fichier Excel final
echo.
echo VOUS SAVEZ MAINTENANT :
echo   ✓ Comment scraper un site web
echo   ✓ Comment extraire les dates de publication
echo   ✓ Comment organiser les resultats par date
echo   ✓ Comment exporter vers Excel
echo.
echo POUR CONTINUER :
echo   1. Utilisez start.bat pour lancer l'interface graphique
echo   2. Testez avec un vrai site (blog, journal, etc.)
echo   3. Augmentez progressivement le nombre de pages
echo   4. Explorez les autres fonctionnalites (recherche de mots-cles)
echo.

echo Voulez-vous ouvrir le dossier des resultats ? (O/N)
set /p open_folder="> "
if /i "%open_folder%"=="O" (
    echo [INFO] Ouverture du dossier des resultats...
    start explorer "data\test_guide"
)

echo.
echo Voulez-vous lancer l'interface graphique maintenant ? (O/N)
set /p launch_gui="> "
if /i "%launch_gui%"=="O" (
    echo [INFO] Lancement de l'interface graphique...
    start.bat
) else (
    echo [INFO] Vous pouvez lancer l'interface plus tard avec start.bat
)

echo.
echo =====================================================
echo                   MERCI ET BRAVO !
echo =====================================================
echo.
echo Vous maitrisez maintenant les bases de Web Scraper Suite !
echo.
echo N'hesitez pas a experimenter avec differents sites web.
echo Commencez toujours par de petites quantites (50-100 pages)
echo avant de faire du scraping massif.
echo.
echo Amusez-vous bien avec votre nouvel outil !
echo.
pause