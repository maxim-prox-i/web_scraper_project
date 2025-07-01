@echo off
cls
echo.
echo =====================================================
echo         WEB SCRAPER SUITE - DEMARRAGE
echo =====================================================
echo.
echo [INFO] Activation de l'environnement Python...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    echo          Relancez install.bat pour reparer
    pause
    exit /b 
)
echo [SUCCES] Environnement active
echo.
echo [INFO] Verification des dependances...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [AVERTISSEMENT] Probleme avec les dependances
    echo                  L'application peut ne pas fonctionner correctement
    echo.
)
echo [INFO] Lancement de l'application...
echo.
python main.py
if errorlevel 1 (
    echo.
    echo [ERREUR] Erreur lors du lancement de l'application
    echo          Verifiez que tous les fichiers sont presents
    echo.
)
echo.
pause
