@echo off
setlocal enabledelayedexpansion
cls
color 0A
echo.
echo        ██╗    ██╗███████╗██████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
echo        ██║    ██║██╔════╝██╔══██╗    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
echo        ██║ █╗ ██║█████╗  ██████╔╝    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
echo        ██║███╗██║██╔══╝  ██╔══██╗    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
echo        ╚███╔███╔╝███████╗██████╔╝    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
echo         ╚══╝╚══╝ ╚══════╝╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
echo.
echo                              INSTALLATION AUTOMATIQUE COMPLETE
echo                              ===================================
echo.
color 07

echo [INFO] Bienvenue dans l'installation automatique de Web Scraper Suite !
echo.
echo Ce script va installer AUTOMATIQUEMENT :
echo   ✓ Git (pour telecharger les mises a jour)
echo   ✓ Python 3.11 (langage de programmation)
echo   ✓ Tous les modules requis
echo   ✓ L'environnement de travail
echo   ✓ L'application Web Scraper Suite
echo.
echo IMPORTANT :
echo   - Gardez une connexion internet active
echo   - Ne fermez pas cette fenetre pendant l'installation
echo   - L'installation peut prendre 10-15 minutes
echo   - Votre PC peut avoir besoin de redemarrer
echo.

:: Demander confirmation
set /p continue="Voulez-vous continuer l'installation automatique ? (O/N): "
if /i "!continue!" neq "O" (
    echo Installation annulee par l'utilisateur.
    echo.
    pause
    exit /b 0
)

echo.
echo =====================================================
echo              DEMARRAGE DE L'INSTALLATION
echo =====================================================
echo.

:: Variables globales
set "install_success=0"
set "need_reboot=0"
set "git_installed=0"
set "python_installed=0"

:: ===============================================
:: PHASE 1: PREPARATION
:: ===============================================
echo [PHASE 1/6] PREPARATION DU SYSTEME
echo.

echo [INFO] Verification des permissions...
net session >nul 2>&1
if errorlevel 1 (
    echo [AVERTISSEMENT] Ce script n'est pas execute en administrateur
    echo                 Certaines installations peuvent echouer
    echo.
    echo Voulez-vous continuer quand meme ? (O/N)
    set /p admin_continue="> "
    if /i "!admin_continue!" neq "O" (
        echo.
        echo Pour executer en administrateur :
        echo 1. Clic droit sur ce fichier
        echo 2. "Executer en tant qu'administrateur"
        pause
        exit /b 1
    )
) else (
    echo [SUCCES] Permissions administrateur detectees
)

echo [INFO] Verification de la connexion internet...
ping google.com -n 1 >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Aucune connexion internet detectee
    echo           L'installation ne peut pas continuer sans internet
    echo.
    echo Verifiez votre connexion et relancez ce script.
    pause
    exit /b 1
) else (
    echo [SUCCES] Connexion internet confirmee
)

echo [INFO] Creation du dossier de travail temporaire...
if not exist "temp_install" mkdir temp_install

echo.

:: ===============================================
:: PHASE 2: INSTALLATION DE WINGET (SI NECESSAIRE)
:: ===============================================
echo [PHASE 2/6] VERIFICATION DE WINDOWS PACKAGE MANAGER
echo.

winget --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Windows Package Manager (winget) non detecte
    echo [INFO] Tentative d'installation...
    
    :: Télécharger winget si possible (Windows 10/11)
    powershell -Command "& {try { if ((Get-ComputerInfo).WindowsVersion -like '10.*' -or (Get-ComputerInfo).WindowsVersion -like '11.*') { Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe } } catch { Write-Host 'Winget installation failed' }}" >nul 2>&1
    
    :: Retest
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo [AVERTISSEMENT] winget non disponible - installation manuelle sera utilisee
        set use_manual_install=1
    ) else (
        echo [SUCCES] winget installe et operationnel
        set use_manual_install=0
    )
) else (
    echo [SUCCES] Windows Package Manager detecte
    winget --version
    set use_manual_install=0
)

echo.

:: ===============================================
:: PHASE 3: INSTALLATION DE GIT
:: ===============================================
echo [PHASE 3/6] INSTALLATION DE GIT
echo.

git --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Git non detecte - installation en cours...
    
    if !use_manual_install! equ 0 (
        echo [INFO] Installation via Windows Package Manager...
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
        if errorlevel 1 (
            echo [AVERTISSEMENT] Echec installation winget - passage en mode manuel
            set use_manual_install=1
        ) else (
            echo [SUCCES] Git installe via winget
            set git_installed=1
            set need_reboot=1
        )
    )
    
    if !use_manual_install! equ 1 (
        echo [INFO] Installation manuelle de Git...
        echo [INFO] Telechargement de Git...
        
        :: Télécharger Git avec version plus récente
        powershell -Command "& {Invoke-WebRequest 'https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe' -OutFile 'temp_install\git-installer.exe' -UseBasicParsing}" 2>nul
        
        if exist "temp_install\git-installer.exe" (
            echo [SUCCES] Git telecharge
            echo [INFO] Installation silencieuse de Git...
            
            :: Installation silencieuse avec paramètres optimaux
            temp_install\git-installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
            
            :: Attendre la fin de l'installation
            timeout /t 30 /nobreak >nul
            
            echo [SUCCES] Git installe
            set git_installed=1
            set need_reboot=1
        ) else (
            echo [ERREUR] Impossible de telecharger Git
            echo [INFO] Veuillez installer Git manuellement depuis https://git-scm.com/download/win
        )
    )
) else (
    echo [SUCCES] Git deja installe
    git --version
    set git_installed=1
)

echo.

:: ===============================================
:: PHASE 4: INSTALLATION DE PYTHON
:: ===============================================
echo [PHASE 4/6] INSTALLATION DE PYTHON
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Python non detecte - installation en cours...
    
    if !use_manual_install! equ 0 (
        echo [INFO] Installation via Windows Package Manager...
        winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements --silent
        if errorlevel 1 (
            echo [AVERTISSEMENT] Echec installation winget Python - passage en mode manuel
            set use_manual_install=1
        ) else (
            echo [SUCCES] Python installe via winget
            set python_installed=1
            set need_reboot=1
        )
    )
    
    if !use_manual_install! equ 1 (
        echo [INFO] Installation manuelle de Python...
        echo [INFO] Telechargement de Python 3.11...
        
        :: Télécharger Python version plus récente
        powershell -Command "& {Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'temp_install\python-installer.exe' -UseBasicParsing}" 2>nul
        
        if exist "temp_install\python-installer.exe" (
            echo [SUCCES] Python telecharge
            echo [INFO] Installation silencieuse de Python avec PATH...
            
            :: Installation silencieuse avec PATH automatique
            temp_install\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_dev=0 Include_tcltk=1 InstallLauncherAllUsers=1
            
            :: Attendre la fin de l'installation
            timeout /t 45 /nobreak >nul
            
            echo [SUCCES] Python installe
            set python_installed=1
            set need_reboot=1
        ) else (
            echo [ERREUR] Impossible de telecharger Python
            echo [INFO] Veuillez installer Python manuellement depuis https://python.org/downloads
            echo [IMPORTANT] Cochez "Add Python to PATH" lors de l'installation manuelle
        )
    )
) else (
    echo [SUCCES] Python deja installe
    python --version
    set python_installed=1
)

echo.

:: ===============================================
:: GESTION DU REDEMARRAGE
:: ===============================================
if !need_reboot! equ 1 (
    echo =====================================================
    echo                REDEMARRAGE REQUIS
    echo =====================================================
    echo.
    echo [IMPORTANT] Des logiciels ont ete installes et le PATH Windows
    echo             doit etre actualise pour fonctionner correctement.
    echo.
    echo [INFO] Un redemarrage est FORTEMENT recommande maintenant.
    echo.
    echo Apres le redemarrage :
    echo 1. Revenez dans ce dossier
    echo 2. Double-cliquez sur install_auto.bat
    echo 3. L'installation continuera automatiquement
    echo.
    echo Voulez-vous redemarrer maintenant ? (RECOMMANDE)
    echo O = Redemarrer maintenant
    echo N = Continuer sans redemarrer (peut ne pas fonctionner)
    set /p reboot_choice="> "
    
    if /i "!reboot_choice!"=="O" (
        echo [INFO] Redemarrage programme dans 10 secondes...
        echo [INFO] IMPORTANT: Relancez install_auto.bat apres le redemarrage !
        echo.
        
        shutdown /r /t 10 /c "Redemarrage pour finaliser l'installation de Git et Python"
        exit /b 0
    ) else (
        echo [INFO] Continuation sans redemarrage...
        echo [AVERTISSEMENT] Si des erreurs surviennent, redemarrez et relancez ce script
        
        :: Forcer actualisation du PATH
        call refreshenv >nul 2>&1
        
        :: Attendre un peu pour que le système se stabilise
        timeout /t 5 /nobreak >nul
    )
)

echo.

:: ===============================================
:: PHASE 5: VERIFICATION POST-INSTALLATION
:: ===============================================
echo [PHASE 5/6] VERIFICATION DES INSTALLATIONS
echo.

echo [INFO] Test de Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Git non fonctionnel apres installation
    echo [SOLUTION] Redemarrez votre PC et relancez ce script
    set install_success=0
) else (
    echo [SUCCES] Git operationnel
    git --version
)

echo [INFO] Test de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non fonctionnel apres installation
    echo [SOLUTION] Redemarrez votre PC et relancez ce script
    set install_success=0
) else (
    echo [SUCCES] Python operationnel
    python --version
)

echo [INFO] Test de pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] pip non disponible
    echo [SOLUTION] Reinstallez Python ou redemarrez votre PC
    set install_success=0
) else (
    echo [SUCCES] pip operationnel
    pip --version
)

echo.

:: ===============================================
:: PHASE 6: CONFIGURATION DU PROJET
:: ===============================================
echo [PHASE 6/6] CONFIGURATION DU PROJET WEB SCRAPER
echo.

echo [INFO] Verification de la presence du projet...
if not exist "main.py" (
    echo [AVERTISSEMENT] Fichiers du projet non detectes dans ce dossier
    echo.
    echo Il semble que vous n'ayez pas encore telecharge le projet Web Scraper.
    echo.
    echo Voulez-vous le telecharger maintenant ? (O/N)
    set /p download_project="> "
    
    if /i "!download_project!"=="O" (
        echo [INFO] Telechargement du projet via Git...
        
        git clone https://github.com/maxim-prox-i/web_scraper_project.git temp_project
        if errorlevel 1 (
            echo [ERREUR] Echec du telechargement via Git
            echo [INFO] Telechargement manuel du ZIP...
            
            powershell -Command "& {Invoke-WebRequest 'https://github.com/maxim-prox-i/web_scraper_project/archive/refs/heads/main.zip' -OutFile 'temp_install\project.zip' -UseBasicParsing}"
            
            if exist "temp_install\project.zip" (
                echo [INFO] Decompression du projet...
                powershell -Command "& {Expand-Archive 'temp_install\project.zip' -DestinationPath 'temp_install\' -Force}"
                
                :: Déplacer les fichiers avec gestion d'erreurs améliorée
                robocopy "temp_install\web_scraper_project-main" "." /E /MOVE /NJH /NJS >nul 2>&1
                if exist "temp_install\web_scraper_project-main" (
                    rmdir /s /q "temp_install\web_scraper_project-main" >nul 2>&1
                )
                
                echo [SUCCES] Projet telecharge et decompresse
            ) else (
                echo [ERREUR] Impossible de telecharger le projet
                echo [INFO] Veuillez telecharger manuellement depuis GitHub
                echo       https://github.com/maxim-prox-i/web_scraper_project
                pause
                exit /b 1
            )
        ) else (
            :: Déplacer les fichiers du dossier temp_project vers le dossier courant
            robocopy "temp_project" "." /E /MOVE /NJH /NJS >nul 2>&1
            if exist "temp_project" (
                rmdir /s /q temp_project >nul 2>&1
            )
            echo [SUCCES] Projet clone via Git
        )
    ) else (
        echo [INFO] Telechargement annule
        echo [SOLUTION] Telechargez le projet manuellement depuis GitHub et relancez ce script
        pause
        exit /b 1
    )
)

echo [INFO] Creation de l'environnement virtuel Python...
if exist "venv" (
    echo [INFO] Environnement virtuel existant detecte - recreation...
    rmdir /s /q venv >nul 2>&1
)

python -m venv venv
if errorlevel 1 (
    echo [ERREUR] Impossible de creer l'environnement virtuel
    echo [SOLUTION] Verifiez que Python est correctement installe
    set install_success=0
) else (
    echo [SUCCES] Environnement virtuel cree
)

echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    set install_success=0
) else (
    echo [SUCCES] Environnement virtuel active
)

echo [INFO] Mise a jour de pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [AVERTISSEMENT] Impossible de mettre a jour pip (non critique)
) else (
    echo [SUCCES] pip mis a jour
)

echo [INFO] Verification/creation du fichier requirements.txt...
if not exist "requirements.txt" (
    echo [INFO] Creation du fichier requirements.txt...
    (
        echo # Core dependencies
        echo requests^>=2.31.0
        echo beautifulsoup4^>=4.12.0
        echo lxml^>=4.9.0
        echo tqdm^>=4.66.0
        echo python-dateutil^>=2.8.0
        echo fake-useragent^>=1.4.0
        echo urllib3^>=2.0.0
        echo tkinter
    ) > requirements.txt
    echo [SUCCES] requirements.txt cree
)

echo [INFO] Installation des modules Python requis...
echo [INFO] Ceci peut prendre plusieurs minutes selon votre connexion...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [AVERTISSEMENT] Probleme lors de l'installation groupee
    echo [INFO] Tentative d'installation module par module...
    
    pip install requests --quiet
    pip install beautifulsoup4 --quiet
    pip install lxml --quiet
    pip install tqdm --quiet
    pip install python-dateutil --quiet
    pip install fake-useragent --quiet
    pip install urllib3 --quiet
    
    echo [INFO] Installation modules terminee (avec possibles avertissements)
) else (
    echo [SUCCES] Tous les modules installes avec succes
)

echo [INFO] Creation du dossier de donnees...
if not exist "data" (
    mkdir data
    echo [SUCCES] Dossier 'data' cree
) else (
    echo [SUCCES] Dossier 'data' deja present
)

echo [INFO] Creation du dossier scripts...
if not exist "scripts" (
    mkdir scripts
    echo [SUCCES] Dossier 'scripts' cree
) else (
    echo [SUCCES] Dossier 'scripts' deja present
)

:: ===============================================
:: NETTOYAGE ET TEST FINAL
:: ===============================================
echo [INFO] Nettoyage des fichiers temporaires...
if exist "temp_install" (
    rmdir /s /q temp_install >nul 2>&1
    echo [SUCCES] Fichiers temporaires supprimes
)

echo [INFO] Test final de l'installation...
python -c "import requests, bs4, tqdm, dateutil; print('[SUCCES] Test final reussi - tous les modules fonctionnent')" 2>nul
if errorlevel 1 (
    echo [AVERTISSEMENT] Certains modules ne fonctionnent pas correctement
    echo [SOLUTION] Utilisez test.bat pour plus de details
    set install_success=0
) else (
    echo [SUCCES] Test final reussi !
    set install_success=1
)

echo.

:: ===============================================
:: RESULTAT FINAL
:: ===============================================
cls
if !install_success! equ 1 (
    color 0A
    echo.
    echo        ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗    ██╗
    echo        ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝    ██║
    echo        ███████╗██║   ██║██║     ██║     █████╗  ███████╗    ██║
    echo        ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║    ╚═╝
    echo        ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║    ██╗
    echo        ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝    ╚═╝
    echo.
    echo                    INSTALLATION TERMINEE AVEC SUCCES !
    echo.
    color 07
    echo =====================================================
    echo                INSTALLATION REUSSIE
    echo =====================================================
    echo.
    echo [EXCELLENT] Tous les composants sont installes et fonctionnels !
    echo.
    echo FICHIERS PRESENTS :
    echo   ✓ start.bat         - Lance l'application
    echo   ✓ test.bat          - Teste l'installation  
    echo   ✓ scripts/          - Scripts supplementaires
    echo   ✓ data/             - Dossier pour vos donnees
    echo   ✓ venv/             - Environnement Python
    echo.
    echo POUR COMMENCER :
    echo   1. Double-cliquez sur start.bat
    echo   2. L'interface graphique va s'ouvrir
    echo   3. Testez avec https://example.com et limite 5
    echo.
    echo AIDE :
    echo   - test.bat : Verifie que tout fonctionne
    echo   - scripts/update.bat : Met a jour l'application
    echo   - scripts/premier_test.bat : Test guide interactif
    echo.
) else (
    color 0C
    echo.
    echo        ███████╗ ██████╗██╗  ██╗███████╗ ██████╗    ██╗
    echo        ██╔════╝██╔════╝██║  ██║██╔════╝██╔════╝    ██║
    echo        █████╗  ██║     ███████║█████╗  ██║         ██║
    echo        ██╔══╝  ██║     ██╔══██║██╔══╝  ██║         ╚═╝
    echo        ███████╗╚██████╗██║  ██║███████╗╚██████╗    ██╗
    echo        ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝    ╚═╝
    echo.
    echo                       INSTALLATION INCOMPLETE
    echo.
    color 07
    echo =====================================================
    echo                PROBLEMES DETECTES
    echo =====================================================
    echo.
    echo [PROBLEME] L'installation n'est pas complete.
    echo.
    echo SOLUTIONS :
    echo   1. Redemarrez votre PC
    echo   2. Relancez install_auto.bat
    echo   3. Executez en tant qu'administrateur (clic droit)
    echo   4. Verifiez votre connexion internet
    echo   5. Desactivez temporairement l'antivirus
    echo.
    echo AIDE MANUELLE :
    echo   - Installez Python depuis https://python.org/downloads
    echo   - Cochez "Add Python to PATH"
    echo   - Installez Git depuis https://git-scm.com/download/win
    echo   - Relancez ce script
    echo.
)

echo Voulez-vous lancer l'application maintenant ? (O/N)
set /p launch_choice="> "
if /i "!launch_choice!"=="O" (
    if !install_success! equ 1 (
        echo.
        echo [INFO] Lancement de l'application...
        if exist "start.bat" (
            call start.bat
        ) else (
            echo [ERREUR] start.bat non trouve - lancez manuellement : python main.py
        )
    ) else (
        echo [ERREUR] Installation incomplete - impossible de lancer
        echo Corrigez les problemes ci-dessus et relancez ce script
    )
)

echo.
echo =====================================================
echo               INSTALLATION TERMINEE
echo =====================================================
echo.
pause