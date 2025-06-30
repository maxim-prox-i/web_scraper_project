@echo off
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - INSTALLATION AUTOMATIQUE
echo =====================================================
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [AVERTISSEMENT] Python n'est pas detecte
    echo.
    echo [INFO] Installation automatique de Python...
    echo.
    
    :: Essayer avec winget d'abord (Windows 10/11)
    winget --version >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Installation via Windows Package Manager...
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
        if not errorlevel 1 (
            echo [SUCCES] Python installe via winget
            echo [AVERTISSEMENT] Redemarrage requis pour mettre a jour le PATH
            echo    Relancez ce script apres redemarrage
            pause
            exit /b 0
        ) else (
            echo [AVERTISSEMENT] Echec installation winget, tentative alternative...
        )
    )
    
    :: Alternative: téléchargement direct
    echo [INFO] Telechargement de Python depuis python.org...
    
    :: Créer dossier temporaire
    if not exist "temp" mkdir temp
    
    :: Télécharger Python (version 3.11.x recommandée)
    powershell -Command "& {Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'temp\python-installer.exe'}"
    
    if not exist "temp\python-installer.exe" (
        echo [ERREUR] Impossible de telecharger Python
        echo.
        echo Installation manuelle requise:
        echo 1. Allez sur https://python.org/downloads
        echo 2. Telechargez Python 3.11+
        echo 3. Cochez "Add Python to PATH" lors de l'installation
        echo 4. Relancez ce script
        echo.
        pause
        exit /b 1
    )
    
    echo [SUCCES] Python telecharge
    echo [INFO] Installation en cours...
    echo    (Ceci peut prendre quelques minutes)
    
    :: Installer Python silencieusement avec PATH
    temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Nettoyer
    if exist "temp\python-installer.exe" del "temp\python-installer.exe"
    if exist "temp" rmdir "temp"
    
    echo [SUCCES] Installation Python terminee
    echo.
    echo [AVERTISSEMENT] REDEMARRAGE REQUIS
    echo    Python a ete installe mais le PATH doit etre actualise
    echo    Veuillez:
    echo    1. Redemarrer votre ordinateur
    echo    2. Relancer ce script
    echo.
    pause
    exit /b 0
)

echo [SUCCES] Python detecte
python --version

:: Vérifier si pip est disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] pip n'est pas disponible
    echo.
    pause
    exit /b 1
)

echo [SUCCES] pip detecte
echo.

:: Créer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [SUCCES] Environnement virtuel cree
) else (
    echo [SUCCES] Environnement virtuel existant trouve
)

:: Activer l'environnement virtuel
echo.
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

:: Mettre à jour pip
echo.
echo [INFO] Mise a jour de pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [AVERTISSEMENT] Impossible de mettre a jour pip
) else (
    echo [SUCCES] pip mis a jour
)

:: Vérifier si requirements.txt existe
if not exist "requirements.txt" (
    echo.
    echo [ERREUR] requirements.txt introuvable
    echo.
    echo [INFO] Creation d'un requirements.txt minimal...
    echo requests>=2.28.0> requirements.txt
    echo beautifulsoup4>=4.11.0>> requirements.txt
    echo lxml>=4.9.0>> requirements.txt
    echo tqdm>=4.64.0>> requirements.txt
    echo python-dateutil>=2.8.0>> requirements.txt
    echo fake-useragent>=1.2.0>> requirements.txt
    echo urllib3>=1.26.0>> requirements.txt
    echo [SUCCES] requirements.txt cree avec les dependances de base
)

:: Installer les dépendances
echo.
echo [INFO] Installation des dependances...
echo    (Ceci peut prendre quelques minutes)
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERREUR] Echec de l'installation des dependances
    echo.
    echo [INFO] Tentative d'installation une par une...
    pip install requests
    pip install beautifulsoup4
    pip install lxml
    pip install tqdm
    pip install python-dateutil
    pip install fake-useragent
    pip install urllib3
)

:: Vérifier l'installation
echo.
echo [INFO] Verification de l'installation...
python -c "import requests, bs4, tqdm, dateutil; print('[SUCCES] Toutes les dependances principales sont installees')" 2>nul
if errorlevel 1 (
    echo [AVERTISSEMENT] Certaines dependances peuvent ne pas etre installees correctement
    echo    Verifiez les messages d'erreur ci-dessus
) else (
    echo [SUCCES] Installation verifiee avec succes
)

:: Créer le dossier data s'il n'existe pas
if not exist "data" (
    mkdir data
    echo [SUCCES] Dossier 'data' cree
)

echo.
echo =====================================================
echo             INSTALLATION TERMINEE !
echo =====================================================
echo.
echo Pour demarrer l'application :
echo   1. Double-cliquez sur start.bat
echo   OU
echo   2. Tapez: python main.py
echo.
echo Pour activer manuellement l'environnement :
echo   venv\Scripts\activate
echo.

:: Créer un script de démarrage rapide
echo @echo off > start.bat
echo call venv\Scripts\activate >> start.bat
echo python main.py >> start.bat
echo pause >> start.bat
echo [SUCCES] Script de demarrage 'start.bat' cree

echo.
pause