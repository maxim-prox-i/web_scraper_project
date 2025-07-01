@echo off
setlocal enabledelayedexpansion
cls
echo.
echo =====================================================
echo    WEB SCRAPER SUITE - SYSTEME DE MISE A JOUR
echo =====================================================
echo.

:: ===============================================
:: VERIFICATION DE GIT
:: ===============================================
echo [VERIFICATION] Verification de Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Git n'est pas installe ou pas dans le PATH
    echo.
    echo SOLUTIONS:
    echo 1. Installez Git depuis https://git-scm.com/download/win
    echo 2. OU relancez install.bat pour une installation automatique
    echo.
    pause
    exit /b 1
)

echo [SUCCES] Git detecte
git --version
echo.

:: ===============================================
:: VERIFICATION REPOSITORY GIT
:: ===============================================
echo [VERIFICATION] Verification du repository Git...
if not exist ".git" (
    echo [ERREUR] Ce dossier n'est pas un repository Git
    echo.
    echo SOLUTIONS:
    echo 1. Clonez le projet: git clone https://github.com/maxim-prox-i/web_scraper_project.git
    echo 2. OU telechargez le ZIP depuis GitHub
    echo.
    pause
    exit /b 1
)

echo [SUCCES] Repository Git detecte
echo.

:: ===============================================
:: RECUPERATION INFORMATIONS DISTANTES
:: ===============================================
echo [INFO] Recuperation des informations distantes...
git fetch --all --quiet
if errorlevel 1 (
    echo [ERREUR] Impossible de recuperer les informations distantes
    echo.
    echo CAUSES POSSIBLES:
    echo 1. Pas de connexion internet
    echo 2. Repository distant inaccessible
    echo 3. Probleme d'authentification
    echo.
    echo Voulez-vous continuer sans mise a jour distante? (O/N)
    set /p continue_offline="> "
    if /i "!continue_offline!"=="N" (
        pause
        exit /b 1
    )
    echo [AVERTISSEMENT] Continuation en mode hors ligne
    echo.
)

:: ===============================================
:: ANALYSE DES BRANCHES
:: ===============================================
echo [INFO] Analyse des branches disponibles...

:: Récupérer la branche courante
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set current_branch=%%i
if "!current_branch!"=="" (
    echo [AVERTISSEMENT] Impossible de detecter la branche courante
    set current_branch=main
)
echo [INFO] Branche courante: !current_branch!
echo.

:: Créer fichier temporaire pour les branches
> temp_branches.txt (
    echo Branche;Statut;Commits_en_retard;Commits_en_avance
)

echo [INFO] Analyse des branches locales...

:: Analyser les branches locales de manière plus robuste
git branch --format="%(refname:short)" > temp_local_branches.txt 2>nul
if exist temp_local_branches.txt (
    for /f "usebackq delims=" %%i in ("temp_local_branches.txt") do (
        set "branch_name=%%i"
        set "branch_name=!branch_name: =!"
        if "!branch_name!" neq "" (
            call :analyze_branch "!branch_name!"
        )
    )
    del temp_local_branches.txt
) else (
    echo [AVERTISSEMENT] Impossible de lister les branches locales
    >> temp_branches.txt echo !current_branch!;INCONNUE;-;-
)

echo [INFO] Analyse des branches distantes...

:: Analyser les branches distantes non trackées localement
git branch -r --format="%(refname:short)" 2>nul | findstr /v HEAD > temp_remote_branches.txt 2>nul
if exist temp_remote_branches.txt (
    for /f "usebackq delims=" %%i in ("temp_remote_branches.txt") do (
        set "remote_branch=%%i"
        set "remote_branch=!remote_branch: =!"
        if "!remote_branch!" neq "" (
            for /f "tokens=2 delims=/" %%j in ("!remote_branch!") do (
                set "local_name=%%j"
                git show-ref --verify --quiet refs/heads/!local_name! 2>nul
                if errorlevel 1 (
                    call :analyze_remote_branch "!remote_branch!" "!local_name!"
                )
            )
        )
    )
    del temp_remote_branches.txt
)

:: ===============================================
:: AFFICHAGE DES BRANCHES
:: ===============================================
echo.
echo =====================================================
echo                  BRANCHES DISPONIBLES
echo =====================================================
echo.

if not exist temp_branches.txt (
    echo [ERREUR] Impossible d'analyser les branches
    echo [INFO] Tentative de mise a jour de la branche courante...
    goto update_current_simple
)

echo  #  ^| Branche              ^| Statut        ^| En retard ^| En avance ^|
echo -----+----------------------+---------------+-----------+-----------+

set branch_count=0
for /f "skip=1 tokens=1,2,3,4 delims=;" %%a in (temp_branches.txt) do (
    set /a branch_count+=1
    set branch_!branch_count!=%%a
    
    :: Marquer la branche courante
    if "%%a"=="!current_branch!" (
        echo  !branch_count!  ^| %%a [ACTUELLE]    ^| %%b      ^| %%c       ^| %%d       ^|
    ) else (
        echo  !branch_count!  ^| %%a                ^| %%b      ^| %%c       ^| %%d       ^|
    )
)

echo.
echo [ACTUELLE] = Branche courante
echo.

:: ===============================================
:: MENU DE CHOIX
:: ===============================================
echo =====================================================
echo                    OPTIONS
echo =====================================================
echo.
echo 1. Rester sur la branche courante et mettre a jour
echo 2. Changer de branche
echo 3. Creer une nouvelle branche
echo 4. Mise a jour simple (sans changement de branche)
echo 0. Annuler
echo.
set /p choice="Votre choix (0-4): "

if "!choice!"=="1" goto update_current
if "!choice!"=="2" goto change_branch
if "!choice!"=="3" goto create_branch
if "!choice!"=="4" goto update_current_simple
if "!choice!"=="0" goto end
echo [ERREUR] Choix invalide
goto menu

:update_current_simple
echo.
echo [INFO] Mise a jour simple de la branche courante (!current_branch!)...
git pull origin !current_branch! 2>nul
if errorlevel 1 (
    echo [AVERTISSEMENT] Echec de la mise a jour automatique
    echo [INFO] Tentative de mise a jour standard...
    git pull
    if errorlevel 1 (
        echo [ERREUR] Echec de la mise a jour
        echo           Il peut y avoir des conflits a resoudre
        echo.
        pause
        goto update_dependencies
    )
)
echo [SUCCES] Branche mise a jour
goto update_dependencies

:update_current
echo.
echo [INFO] Mise a jour de la branche courante (!current_branch!)...
git pull
if errorlevel 1 (
    echo [ERREUR] Echec de la mise a jour
    echo           Il peut y avoir des conflits a resoudre
    echo.
    echo Voulez-vous forcer la mise a jour? (ATTENTION: perte des modifications locales)
    echo O = Forcer la mise a jour
    echo N = Annuler
    set /p force_choice="> "
    if /i "!force_choice!"=="O" (
        echo [INFO] Reset force de la branche...
        git reset --hard origin/!current_branch!
        if errorlevel 1 (
            echo [ERREUR] Impossible de forcer la mise a jour
        ) else (
            echo [SUCCES] Mise a jour forcee reussie
        )
    ) else (
        echo [INFO] Mise a jour annulee
    )
)
echo [SUCCES] Branche mise a jour
goto update_dependencies

:change_branch
echo.
if !branch_count! equ 0 (
    echo [ERREUR] Aucune branche disponible pour changement
    goto end
)

echo [INFO] Choisissez la branche (numero 1-!branch_count!):
set /p branch_choice="> "

:: Validation du choix
if !branch_choice! lss 1 goto invalid_branch
if !branch_choice! gtr !branch_count! goto invalid_branch

call set selected_branch=%%branch_!branch_choice!%%
if "!selected_branch!"=="" goto invalid_branch

echo [INFO] Branche selectionnee: !selected_branch!

:: Vérifier si c'est une branche distante
echo !selected_branch! | findstr "origin/" >nul
if not errorlevel 1 (
    :: C'est une branche distante, créer une branche locale
    for /f "tokens=2 delims=/" %%j in ("!selected_branch!") do set local_name=%%j
    echo.
    echo [INFO] Creation de la branche locale et basculement...
    git checkout -b !local_name! !selected_branch!
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer la branche locale
        pause
        goto end
    )
    echo [SUCCES] Branche locale !local_name! creee et activee
) else (
    :: C'est une branche locale
    echo.
    echo [INFO] Basculement vers la branche !selected_branch!...
    git checkout !selected_branch!
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
    echo [SUCCES] Branche changee: !selected_branch!
)

goto update_dependencies

:invalid_branch
echo [ERREUR] Numero de branche invalide
pause
goto end

:create_branch
echo.
set /p new_branch_name="Nom de la nouvelle branche: "
if "!new_branch_name!"=="" (
    echo [ERREUR] Nom de branche requis
    pause
    goto end
)

echo [INFO] Creation de la branche !new_branch_name!...
git checkout -b !new_branch_name!
if errorlevel 1 (
    echo [ERREUR] Impossible de creer la branche
    echo           Le nom peut etre invalide ou la branche existe deja
    pause
    goto end
)

echo [SUCCES] Nouvelle branche creee: !new_branch_name!
goto update_dependencies

:: ===============================================
:: MISE A JOUR DES DEPENDANCES
:: ===============================================
:update_dependencies
echo.
echo =====================================================
echo           MISE A JOUR DES DEPENDANCES
echo =====================================================
echo.

:: Vérifier l'environnement virtuel
if not exist "venv" (
    echo [ERREUR] Environnement virtuel introuvable
    echo           Executez d'abord install.bat
    echo.
    pause
    goto end
)

echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    echo           L'environnement peut etre corrompu
    echo.
    echo Voulez-vous recreer l'environnement? (O/N)
    set /p recreate_choice="> "
    if /i "!recreate_choice!"=="O" (
        echo [INFO] Recreation de l'environnement virtuel...
        rmdir /s /q venv
        python -m venv venv
        call venv\Scripts\activate.bat
        if errorlevel 1 (
            echo [ERREUR] Impossible de recreer l'environnement
            pause
            goto end
        )
        echo [SUCCES] Environnement recree
    ) else (
        pause
        goto end
    )
)

echo [SUCCES] Environnement virtuel active

:: Mettre à jour les dépendances
if exist "requirements.txt" (
    echo [INFO] Mise a jour des dependances Python...
    echo         (Ceci peut prendre quelques minutes)
    pip install -r requirements.txt --upgrade --quiet
    if errorlevel 1 (
        echo [AVERTISSEMENT] Erreur lors de la mise a jour des dependances
        echo [INFO] Tentative d'installation standard...
        pip install -r requirements.txt --quiet
        if errorlevel 1 (
            echo [ERREUR] Impossible d'installer les dependances
        ) else (
            echo [SUCCES] Dependances installees (sans mise a jour)
        )
    ) else (
        echo [SUCCES] Dependances mises a jour avec succes
    )
) else (
    echo [AVERTISSEMENT] Fichier requirements.txt introuvable
    echo                 Les dependances ne peuvent pas etre verifiees
)

:: Mise à jour de start.bat si nécessaire
echo [INFO] Verification du script start.bat...
if not exist "start.bat" (
    echo [INFO] Recreation du script start.bat...
    call :create_start_bat
)

echo.
echo =====================================================
echo             MISE A JOUR TERMINEE !
echo =====================================================
echo.

:: Afficher la branche finale
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set final_branch=%%i
if "!final_branch!"=="" set final_branch=inconnue

echo [INFO] Branche actuelle: !final_branch!
echo [INFO] Derniers commits:
git log --oneline -5 2>nul
echo.

:: Proposer de démarrer l'application
echo Voulez-vous demarrer l'application maintenant? (O/N)
set /p start_choice="> "
if /i "!start_choice!"=="O" (
    echo.
    echo [INFO] Demarrage de l'application...
    if exist "start.bat" (
        call start.bat
    ) else (
        python main.py
    )
)

goto end

:: ===============================================
:: FONCTIONS D'ANALYSE DES BRANCHES
:: ===============================================
:analyze_branch
set "branch_name=%~1"
if "!branch_name!"=="" goto :eof

:: Vérifier si la branche a une remote
git rev-parse --verify origin/!branch_name! >nul 2>&1
if errorlevel 1 (
    >> temp_branches.txt echo !branch_name!;LOCAL SEULEMENT;-;-
    goto :eof
)

:: Comparer avec origin
for /f %%a in ('git rev-list --count !branch_name!..origin/!branch_name! 2^>nul') do set behind=%%a
for /f %%a in ('git rev-list --count origin/!branch_name!..!branch_name! 2^>nul') do set ahead=%%a

if "!behind!"=="" set behind=0
if "!ahead!"=="" set ahead=0

if !behind! equ 0 if !ahead! equ 0 (
    >> temp_branches.txt echo !branch_name!;A JOUR;0;0
) else if !behind! equ 0 (
    >> temp_branches.txt echo !branch_name!;EN AVANCE;0;!ahead!
) else if !ahead! equ 0 (
    >> temp_branches.txt echo !branch_name!;EN RETARD;!behind!;0
) else (
    >> temp_branches.txt echo !branch_name!;DIVERGEE;!behind!;!ahead!
)
goto :eof

:analyze_remote_branch
set "remote_branch=%~1"
set "local_name=%~2"
if "!remote_branch!"=="" goto :eof
if "!local_name!"=="" goto :eof

>> temp_branches.txt echo !remote_branch!;DISTANTE;-;-
goto :eof

:create_start_bat
echo @echo off> start.bat
echo cls>> start.bat
echo echo [INFO] Demarrage de Web Scraper Suite...>> start.bat
echo call venv\Scripts\activate.bat>> start.bat
echo if errorlevel 1 (>> start.bat
echo     echo [ERREUR] Environnement virtuel non trouve>> start.bat
echo     echo Relancez install.bat>> start.bat
echo     pause>> start.bat
echo     exit /b 1>> start.bat
echo )>> start.bat
echo pip install -r requirements.txt --quiet>> start.bat
echo python main.py>> start.bat
echo pause>> start.bat
goto :eof

:end
:: Nettoyer les fichiers temporaires
if exist temp_branches.txt del temp_branches.txt >nul 2>&1
if exist temp_local_branches.txt del temp_local_branches.txt >nul 2>&1
if exist temp_remote_branches.txt del temp_remote_branches.txt >nul 2>&1

echo.
echo Mise a jour terminee.
pause
exit /b 0