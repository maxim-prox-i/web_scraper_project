@echo off
cls
echo.
echo =====================================================
echo         WEB SCRAPER SUITE - DEMARRAGE
echo =====================================================
echo.

echo [INFO] Demarrage de Web Scraper Suite...
echo.

:: Vérifier la présence de l'environnement virtuel
if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve
    echo.
    echo SOLUTIONS:
    echo 1. Relancez install_auto.bat pour installer l'outil
    echo 2. OU verifiez que vous etes dans le bon dossier
    echo.
    echo Dossier actuel: %CD%
    echo.
    pause
    exit /b 1
)

echo [INFO] Activation de l'environnement Python...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    echo [SOLUTION] Relancez install_auto.bat pour reparer
    echo.
    pause
    exit /b 1
)

echo [SUCCES] Environnement Python active

:: Vérifier la présence du fichier principal
if not exist "main.py" (
    echo [ERREUR] Fichier principal main.py non trouve
    echo.
    echo SOLUTIONS:
    echo 1. Verifiez que vous etes dans le bon dossier du projet
    echo 2. OU telechargez le projet complet depuis GitHub
    echo.
    echo Dossier actuel: %CD%
    echo.
    pause
    exit /b 1
)

echo [INFO] Verification des dependances...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [AVERTISSEMENT] Probleme avec les dependances
    echo [INFO] Tentative de reparation...
    pip install requests beautifulsoup4 lxml tqdm python-dateutil fake-useragent urllib3 --quiet
)

echo [INFO] Lancement de l'application...
echo.

:: Démarrer l'application principale
python main.py
if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors du lancement de l'application
    echo.
    echo DIAGNOSTICS POSSIBLES:
    echo 1. Modules Python manquants
    echo 2. Erreur dans le code principal
    echo 3. Probleme de permissions
    echo.
    echo SOLUTIONS:
    echo 1. Lancez test.bat pour diagnostiquer
    echo 2. OU relancez install_auto.bat pour reparer
    echo 3. OU consultez le README.md pour plus d'aide
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Application fermee normalement
echo.
pause