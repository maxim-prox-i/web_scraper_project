@echo off
chcp 65001 >nul
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - MISE À JOUR AUTOMATIQUE
echo =====================================================
echo.

:: Vérifier si git est installé
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Git n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer Git depuis https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo ✅ Git détecté
git --version
echo.

:: Vérifier si on est dans un repository git
if not exist ".git" (
    echo ❌ ERREUR: Ce dossier n'est pas un repository Git
    echo.
    echo Initialisation d'un repository Git...
    git init
    echo ✅ Repository Git initialisé
    echo.
)

:: Sauvegarder les changements locaux s'il y en a
echo 💾 Vérification des changements locaux...
git status --porcelain > temp_status.txt
set /p changes=<temp_status.txt
del temp_status.txt

if not "%changes%"=="" (
    echo ⚠️  Changements locaux détectés
    echo.
    echo Voulez-vous sauvegarder vos changements locaux? (O/N)
    set /p choice="> "
    
    if /i "%choice%"=="O" (
        echo 💾 Sauvegarde des changements locaux...
        git add .
        git commit -m "Sauvegarde automatique avant mise à jour - %date% %time%"
        echo ✅ Changements sauvegardés
    ) else (
        echo ⚠️  Attention: Les changements locaux pourraient être perdus
        echo.
        echo Continuer quand même? (O/N)
        set /p confirm="> "
        if /i not "%confirm%"=="O" (
            echo ❌ Mise à jour annulée
            pause
            exit /b 0
        )
    )
    echo.
)

:: Récupérer les dernières modifications
echo 🔄 Récupération des dernières modifications...
git fetch
if errorlevel 1 (
    echo ❌ ERREUR: Impossible de récupérer les modifications distantes
    echo    Vérifiez votre connexion internet et l'URL du repository
    pause
    exit /b 1
)

:: Afficher les changements disponibles
echo.
echo 📋 Changements disponibles:
git log HEAD..origin/main --oneline --no-merges 2>nul
if errorlevel 1 (
    echo    Aucun changement disponible ou branche main introuvable
    echo    Tentative avec master...
    git log HEAD..origin/master --oneline --no-merges 2>nul
    if errorlevel 1 (
        echo    Aucune mise à jour disponible
    )
)

:: Effectuer la mise à jour
echo.
echo 🔄 Application des mises à jour...
git pull
if errorlevel 1 (
    echo ❌ ERREUR: Échec de la mise à jour
    echo    Il peut y avoir des conflits à résoudre manuellement
    echo.
    pause
    exit /b 1
)

echo ✅ Code source mis à jour

:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo.
    echo ❌ Environnement virtuel introuvable
    echo    Exécutez d'abord install.bat
    pause
    exit /b 1
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

:: Vérifier si requirements.txt a changé
echo.
echo 🔍 Vérification des dépendances...
git diff HEAD~1 requirements.txt >nul 2>&1
if not errorlevel 1 (
    echo 📦 requirements.txt a été modifié - Mise à jour des dépendances...
    pip install -r requirements.txt --upgrade
    if errorlevel 1 (
        echo ⚠️  Erreur lors de la mise à jour des dépendances
        echo    Essayez de relancer install.bat
    ) else (
        echo ✅ Dépendances mises à jour
    )
) else (
    echo ✅ Aucune mise à jour de dépendances nécessaire
)

:: Nettoyer les fichiers temporaires git
echo.
echo 🧹 Nettoyage...
git gc --quiet 2>nul

:: Afficher le résumé
echo.
echo =====================================================
echo             MISE À JOUR TERMINÉE !
echo =====================================================
echo.
echo 📊 Résumé:
git log --oneline -5 --graph
echo.
echo 🏷️  Version actuelle:
git describe --tags --always 2>nul || git rev-parse --short HEAD

echo.
echo L'application est maintenant à jour.
echo Vous pouvez la démarrer avec: python main.py
echo.

:: Proposer de démarrer l'application
echo Voulez-vous démarrer l'application maintenant? (O/N)
set /p start_choice="> "
if /i "%start_choice%"=="O" (
    echo.
    echo 🚀 Démarrage de l'application...
    python main.py
)

echo.
pause