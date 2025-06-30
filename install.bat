@echo off
chcp 65001 >nul
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - INSTALLATION AUTOMATIQUE
echo =====================================================
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python n'est pas détecté
    echo.
    echo 🔄 Installation automatique de Python...
    echo.
    
    :: Essayer avec winget d'abord (Windows 10/11)
    winget --version >nul 2>&1
    if not errorlevel 1 (
        echo 📦 Installation via Windows Package Manager...
        winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
        if not errorlevel 1 (
            echo ✅ Python installé via winget
            echo ⚠️  Redémarrage requis pour mettre à jour le PATH
            echo    Relancez ce script après redémarrage
            pause
            exit /b 0
        ) else (
            echo ⚠️  Échec installation winget, tentative alternative...
        )
    )
    
    :: Alternative: téléchargement direct
    echo 📥 Téléchargement de Python depuis python.org...
    
    :: Créer dossier temporaire
    if not exist "temp" mkdir temp
    
    :: Télécharger Python (version 3.11.x recommandée)
    powershell -Command "& {Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'temp\python-installer.exe'}"
    
    if not exist "temp\python-installer.exe" (
        echo ❌ ERREUR: Impossible de télécharger Python
        echo.
        echo Installation manuelle requise:
        echo 1. Allez sur https://python.org/downloads
        echo 2. Téléchargez Python 3.11+
        echo 3. Cochez "Add Python to PATH" lors de l'installation
        echo 4. Relancez ce script
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ Python téléchargé
    echo 🔄 Installation en cours...
    echo    (Ceci peut prendre quelques minutes)
    
    :: Installer Python silencieusement avec PATH
    temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Nettoyer
    if exist "temp\python-installer.exe" del "temp\python-installer.exe"
    if exist "temp" rmdir "temp"
    
    echo ✅ Installation Python terminée
    echo.
    echo ⚠️  REDÉMARRAGE REQUIS
    echo    Python a été installé mais le PATH doit être actualisé
    echo    Veuillez:
    echo    1. Redémarrer votre ordinateur
    echo    2. Relancer ce script
    echo.
    pause
    exit /b 0
)

echo ✅ Python détecté
python --version

:: Vérifier si pip est disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: pip n'est pas disponible
    echo.
    pause
    exit /b 1
)

echo ✅ pip détecté
echo.

:: Créer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERREUR: Impossible de créer l'environnement virtuel
        pause
        exit /b 1
    )
    echo ✅ Environnement virtuel créé
) else (
    echo ✅ Environnement virtuel existant trouvé
)

:: Activer l'environnement virtuel
echo.
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR: Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

:: Mettre à jour pip
echo.
echo 🔄 Mise à jour de pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ⚠️  Avertissement: Impossible de mettre à jour pip
) else (
    echo ✅ pip mis à jour
)

:: Vérifier si requirements.txt existe
if not exist "requirements.txt" (
    echo.
    echo ❌ ERREUR: requirements.txt introuvable
    echo.
    echo Création d'un requirements.txt minimal...
    echo requests>=2.28.0> requirements.txt
    echo beautifulsoup4>=4.11.0>> requirements.txt
    echo lxml>=4.9.0>> requirements.txt
    echo tqdm>=4.64.0>> requirements.txt
    echo python-dateutil>=2.8.0>> requirements.txt
    echo fake-useragent>=1.2.0>> requirements.txt
    echo urllib3>=1.26.0>> requirements.txt
    echo ✅ requirements.txt créé avec les dépendances de base
)

:: Installer les dépendances
echo.
echo 📦 Installation des dépendances...
echo    (Ceci peut prendre quelques minutes)
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Échec de l'installation des dépendances
    echo.
    echo Tentative d'installation une par une...
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
echo 🔍 Vérification de l'installation...
python -c "import requests, bs4, tqdm, dateutil; print('✅ Toutes les dépendances principales sont installées')" 2>nul
if errorlevel 1 (
    echo ⚠️  Certaines dépendances peuvent ne pas être installées correctement
    echo    Vérifiez les messages d'erreur ci-dessus
) else (
    echo ✅ Installation vérifiée avec succès
)

:: Créer le dossier data s'il n'existe pas
if not exist "data" (
    mkdir data
    echo ✅ Dossier 'data' créé
)

echo.
echo =====================================================
echo             INSTALLATION TERMINÉE !
echo =====================================================
echo.
echo Pour démarrer l'application :
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
echo ✅ Script de démarrage 'start.bat' créé

echo.
pause