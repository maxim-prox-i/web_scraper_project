@echo off
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - SYSTEME DE MISE A JOUR
echo =====================================================
echo.

:: Vérifier si git est installé
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Git n'est pas installe ou pas dans le PATH
    echo.
    echo Veuillez installer Git depuis https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [SUCCES] Git detecte
echo.

:: Vérifier si on est dans un repository git
if not exist ".git" (
    echo [ERREUR] Ce dossier n'est pas un repository Git
    echo.
    pause
    exit /b 1
)

:: Récupérer les informations distantes
echo [INFO] Recuperation des informations distantes...
git fetch --all --quiet
if errorlevel 1 (
    echo [ERREUR] Impossible de recuperer les informations distantes
    echo    Verifiez votre connexion internet
    echo.
    pause
    exit /b 1
)

:: Afficher la branche courante
for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
echo [INFO] Branche courante: %current_branch%
echo.

:: Analyser l'état des branches
echo [INFO] Analyse des branches disponibles...
echo.
echo =====================================================
echo                  ETAT DES BRANCHES
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
echo [INFO] BRANCHES DISPONIBLES:
echo.
echo  #  ^| Branche              ^| Statut        ^| En retard ^| En avance ^|
echo -----+----------------------+---------------+-----------+-----------+

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
        echo  !branch_count!  ^| %%a [ACTUELLE]    ^| %%b      ^| %%c       ^| %%d       ^|
    ) else (
        echo  !branch_count!  ^| %%a                ^| %%b      ^| %%c       ^| %%d       ^|
    )
)

echo.
echo [ACTUELLE] = Branche courante
echo.

:: Menu de choix
echo =====================================================
echo                    OPTIONS
echo =====================================================
echo.
echo 1. Rester sur la branche courante et mettre a jour
echo 2. Changer de branche
echo 3. Creer une nouvelle branche
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
echo [INFO] Mise a jour de la branche courante (%current_branch%)...
git pull
if errorlevel 1 (
    echo [ERREUR] Echec de la mise a jour
    echo    Il peut y avoir des conflits a resoudre
    pause
    goto end
)
echo [SUCCES] Branche mise a jour
goto update_dependencies

:change_branch
echo.
echo [INFO] Choisissez la branche (numero):
set /p branch_choice="> "

if not defined branch_%branch_choice% (
    echo [ERREUR] Numero de branche invalide
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
    echo [INFO] Creation de la branche locale et basculement...
    git checkout -b !local_name! %selected_branch%
) else (
    :: C'est une branche locale
    echo.
    echo [INFO] Basculement vers la branche %selected_branch%...
    git checkout %selected_branch%
    if errorlevel 1 (
        echo [ERREUR] Impossible de basculer vers la branche
        pause
        goto end
    )
    
    echo [INFO] Mise a jour de la branche...
    git pull
    if errorlevel 1 (
        echo [AVERTISSEMENT] Conflits possibles lors de la mise a jour
    )
)

echo [SUCCES] Branche changee: %selected_branch%
goto update_dependencies

:create_branch
echo.
set /p new_branch_name="Nom de la nouvelle branche: "
if "%new_branch_name%"=="" (
    echo [ERREUR] Nom de branche requis
    pause
    goto end
)

echo [INFO] Creation de la branche %new_branch_name%...
git checkout -b %new_branch_name%
if errorlevel 1 (
    echo [ERREUR] Impossible de creer la branche
    pause
    goto end
)

echo [SUCCES] Nouvelle branche creee: %new_branch_name%
goto update_dependencies

:update_dependencies
:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo.
    echo [ERREUR] Environnement virtuel introuvable
    echo    Executez d'abord install.bat
    pause
    goto end
)

:: Activer l'environnement virtuel
echo.
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    goto end
)

:: Mettre à jour les dépendances
if exist "requirements.txt" (
    echo [INFO] Mise a jour des dependances...
    pip install -r requirements.txt --upgrade --quiet
    if errorlevel 1 (
        echo [AVERTISSEMENT] Erreur lors de la mise a jour des dependances
    ) else (
        echo [SUCCES] Dependances mises a jour
    )
)

echo.
echo =====================================================
echo             MISE A JOUR TERMINEE !
echo =====================================================
echo.

:: Afficher la branche finale
for /f "tokens=*" %%i in ('git branch --show-current') do set final_branch=%%i
echo [INFO] Branche actuelle: %final_branch%
echo.

:: Proposer de démarrer l'application
echo Voulez-vous demarrer l'application maintenant? (O/N)
set /p start_choice="> "
if /i "%start_choice%"=="O" (
    echo.
    echo [INFO] Demarrage de l'application...
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
    >> temp_branches.txt echo %branch_name%;A JOUR;0;0
) else if "%behind%"=="0" (
    >> temp_branches.txt echo %branch_name%;EN AVANCE;0;%ahead%
) else if "%ahead%"=="0" (
    >> temp_branches.txt echo %branch_name%;EN RETARD;%behind%;0
) else (
    >> temp_branches.txt echo %branch_name%;DIVERGEE;%behind%;%ahead%
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