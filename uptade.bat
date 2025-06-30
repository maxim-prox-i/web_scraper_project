@echo off
chcp 65001 >nul
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - SYSTÈME DE MISE À JOUR
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
echo.

:: Vérifier si on est dans un repository git
if not exist ".git" (
    echo ❌ ERREUR: Ce dossier n'est pas un repository Git
    echo.
    pause
    exit /b 1
)

:: Récupérer les informations distantes
echo 🔄 Récupération des informations distantes...
git fetch --all --quiet
if errorlevel 1 (
    echo ❌ ERREUR: Impossible de récupérer les informations distantes
    echo    Vérifiez votre connexion internet
    echo.
    pause
    exit /b 1
)

:: Afficher la branche courante
for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
echo 📍 Branche courante: %current_branch%
echo.

:: Analyser l'état des branches
echo 🔍 Analyse des branches disponibles...
echo.
echo =====================================================
echo                  ÉTAT DES BRANCHES
echo =====================================================

:: Créer un fichier temporaire pour stocker les infos
> temp_branches.txt (
    echo Branche;Statut;Commits_en_retard;Commits_en_avance
)

:: Analyser chaque branche locale
for /f "tokens=*" %%i in ('git branch --format="%(refname:short)"') do (
    call :analyze_branch "%%i"
)

:: Analyser les branches distantes non trackées localement
for /f "tokens=*" %%i in ('git branch -r --format="%(refname:short)" ^| findstr /v HEAD') do (
    set remote_branch=%%i
    setlocal enabledelayedexpansion
    set local_name=!remote_branch:origin/=!
    git show-ref --verify --quiet refs/heads/!local_name! || call :analyze_remote_branch "!remote_branch!" "!local_name!"
    endlocal
)

:: Afficher le tableau des branches
echo.
echo 📋 BRANCHES DISPONIBLES:
echo.
echo  #  │ Branche              │ Statut        │ En retard │ En avance │
echo ─────┼──────────────────────┼───────────────┼───────────┼───────────┤

set branch_count=0
for /f "skip=1 tokens=1,2,3,4 delims=;" %%a in (temp_branches.txt) do (
    set /a branch_count+=1
    set branch_!branch_count!=%%a
    
    :: Formater l'affichage
    set name=%%a                    
    set status=%%b               
    set behind=%%c     
    set ahead=%%d      
    
    :: Marquer la branche courante
    if "%%a"=="%current_branch%" (
        echo  !branch_count!  │ %%a ⭐           │ %%b      │ %%c       │ %%d       │
    ) else (
        echo  !branch_count!  │ %%a                │ %%b      │ %%c       │ %%d       │
    )
)

echo.
echo ⭐ = Branche courante
echo.

:: Menu de choix
echo =====================================================
echo                    OPTIONS
echo =====================================================
echo.
echo 1. Rester sur la branche courante et mettre à jour
echo 2. Changer de branche
echo 3. Créer une nouvelle branche
echo 0. Annuler
echo.
set /p choice="Votre choix (0-3): "

if "%choice%"=="1" goto update_current
if "%choice%"=="2" goto change_branch
if "%choice%"=="3" goto create_branch
if "%choice%"=="0" goto end
goto menu

:update_current
echo.
echo 🔄 Mise à jour de la branche courante (%current_branch%)...
git pull
if errorlevel 1 (
    echo ❌ ERREUR: Échec de la mise à jour
    echo    Il peut y avoir des conflits à résoudre
    pause
    goto end
)
echo ✅ Branche mise à jour
goto update_dependencies

:change_branch
echo.
echo 📌 Choisissez la branche (numéro):
set /p branch_choice="> "

if not defined branch_%branch_choice% (
    echo ❌ Numéro de branche invalide
    pause
    goto end
)

call set selected_branch=%%branch_%branch_choice%%%

:: Vérifier si c'est une branche distante
echo %selected_branch% | findstr "origin/" >nul
if not errorlevel 1 (
    :: C'est une branche distante, créer une branche locale
    set local_name=%selected_branch:origin/=%
    echo.
    echo 🌿 Création de la branche locale et basculement...
    git checkout -b !local_name! %selected_branch%
) else (
    :: C'est une branche locale
    echo.
    echo 🔄 Basculement vers la branche %selected_branch%...
    git checkout %selected_branch%
    if errorlevel 1 (
        echo ❌ ERREUR: Impossible de basculer vers la branche
        pause
        goto end
    )
    
    echo 📥 Mise à jour de la branche...
    git pull
    if errorlevel 1 (
        echo ⚠️  Conflits possibles lors de la mise à jour
    )
)

echo ✅ Branche changée: %selected_branch%
goto update_dependencies

:create_branch
echo.
set /p new_branch_name="Nom de la nouvelle branche: "
if "%new_branch_name%"=="" (
    echo ❌ Nom de branche requis
    pause
    goto end
)

echo 🌿 Création de la branche %new_branch_name%...
git checkout -b %new_branch_name%
if errorlevel 1 (
    echo ❌ ERREUR: Impossible de créer la branche
    pause
    goto end
)

echo ✅ Nouvelle branche créée: %new_branch_name%
goto update_dependencies

:update_dependencies
:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo.
    echo ❌ Environnement virtuel introuvable
    echo    Exécutez d'abord install.bat
    pause
    goto end
)

:: Activer l'environnement virtuel
echo.
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERREUR: Impossible d'activer l'environnement virtuel
    pause
    goto end
)

:: Mettre à jour les dépendances
if exist "requirements.txt" (
    echo 📦 Mise à jour des dépendances...
    pip install -r requirements.txt --upgrade --quiet
    if errorlevel 1 (
        echo ⚠️  Erreur lors de la mise à jour des dépendances
    ) else (
        echo ✅ Dépendances mises à jour
    )
)

echo.
echo =====================================================
echo             MISE À JOUR TERMINÉE !
echo =====================================================
echo.

:: Afficher la branche finale
for /f "tokens=*" %%i in ('git branch --show-current') do set final_branch=%%i
echo 📍 Branche actuelle: %final_branch%
echo.

:: Proposer de démarrer l'application
echo Voulez-vous démarrer l'application maintenant? (O/N)
set /p start_choice="> "
if /i "%start_choice%"=="O" (
    echo.
    echo 🚀 Démarrage de l'application...
    python main.py
)

goto end

:analyze_branch
set branch_name=%~1
set branch_name=%branch_name: =%

:: Vérifier si la branche a une remote
git rev-parse --verify origin/%branch_name% >nul 2>&1
if errorlevel 1 (
    >> temp_branches.txt echo %branch_name%;LOCAL SEULEMENT;-;-
    goto :eof
)

:: Comparer avec origin
for /f %%a in ('git rev-list --count %branch_name%..origin/%branch_name% 2^>nul') do set behind=%%a
for /f %%a in ('git rev-list --count origin/%branch_name%..%branch_name% 2^>nul') do set ahead=%%a

if "%behind%"=="0" if "%ahead%"=="0" (
    >> temp_branches.txt echo %branch_name%;À JOUR;0;0
) else if "%behind%"=="0" (
    >> temp_branches.txt echo %branch_name%;EN AVANCE;0;%ahead%
) else if "%ahead%"=="0" (
    >> temp_branches.txt echo %branch_name%;EN RETARD;%behind%;0
) else (
    >> temp_branches.txt echo %branch_name%;DIVERGÉE;%behind%;%ahead%
)
goto :eof

:analyze_remote_branch
set remote_branch=%~1
set local_name=%~2
>> temp_branches.txt echo %remote_branch%;DISTANTE;-;-
goto :eof

:end
:: Nettoyer les fichiers temporaires
if exist temp_branches.txt del temp_branches.txt
echo.
pause