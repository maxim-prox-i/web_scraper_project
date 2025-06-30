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
    echo ❌ ERREUR: Python n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer Python depuis https://python.org
    echo N'oubliez pas de cocher "Add Python to PATH"
    echo.
    pause
    exit /b 1
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