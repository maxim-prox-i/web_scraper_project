@echo off
cls
echo.
echo =====================================================
echo      WEB SCRAPER SUITE - DIAGNOSTIC COMPLET
echo =====================================================
echo.
echo Ce script teste tous les composants de l'installation
echo.

:: Variables pour stocker les résultats
set git_status=ECHEC
set python_status=ECHEC
set pip_status=ECHEC
set venv_status=ECHEC
set modules_status=ECHEC
set mainpy_status=ECHEC
set data_status=ECHEC

:: ===============================================
:: TEST 1: VERIFICATION DE GIT
:: ===============================================
echo [TEST 1/7] Verification de Git...

git --version >nul 2>&1
if errorlevel 1 (
    echo [ECHEC] Git n'est pas installe ou pas dans le PATH
    echo         Solution: Installez Git depuis https://git-scm.com/download/win
    echo         OU relancez install_auto.bat
) else (
    echo [SUCCES] Git detecte
    git --version
    set git_status=SUCCES
)
echo.

:: ===============================================
:: TEST 2: VERIFICATION DE PYTHON
:: ===============================================
echo [TEST 2/7] Verification de Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ECHEC] Python n'est pas installe ou pas dans le PATH
    echo         Solution: Installez Python depuis https://python.org/downloads
    echo         IMPORTANT: Cochez "Add Python to PATH" lors de l'installation
    echo         OU relancez install_auto.bat
) else (
    echo [SUCCES] Python detecte
    python --version
    set python_status=SUCCES
)
echo.

:: ===============================================
:: TEST 3: VERIFICATION DE PIP
:: ===============================================
echo [TEST 3/7] Verification de pip...

pip --version >nul 2>&1
if errorlevel 1 (
    echo [ECHEC] pip n'est pas disponible
    echo         pip est normalement inclus avec Python
    echo         Solution: Reinstallez Python ou relancez install_auto.bat
) else (
    echo [SUCCES] pip detecte
    pip --version
    set pip_status=SUCCES
)
echo.

:: ===============================================
:: TEST 4: VERIFICATION ENVIRONNEMENT VIRTUEL
:: ===============================================
echo [TEST 4/7] Verification de l'environnement virtuel...

if not exist "venv" (
    echo [ECHEC] Dossier venv introuvable
    echo         L'environnement virtuel n'a pas ete cree
    echo         Solution: Relancez install_auto.bat
    goto test_mainpy
)

if not exist "venv\Scripts\activate.bat" (
    echo [ECHEC] Fichier d'activation introuvable
    echo         L'environnement virtuel est corrompu
    echo         Solution: Supprimez le dossier venv et relancez install_auto.bat
    goto test_mainpy
)

echo [SUCCES] Environnement virtuel present
set venv_status=SUCCES

:: Test d'activation
echo [INFO] Test d'activation de l'environnement...
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo [ECHEC] Impossible d'activer l'environnement virtuel
    echo         L'environnement peut etre corrompu
    echo         Solution: Supprimez le dossier venv et relancez install_auto.bat
    set venv_status=ECHEC
) else (
    echo [SUCCES] Environnement virtuel activable
)
echo.

:: ===============================================
:: TEST 5: VERIFICATION DES MODULES PYTHON
:: ===============================================
echo [TEST 5/7] Verification des modules Python critiques...

if "%venv_status%"=="ECHEC" (
    echo [IGNORE] Test des modules ignore (environnement virtuel non fonctionnel)
    goto test_mainpy
)

:: Activer l'environnement pour les tests
call venv\Scripts\activate.bat >nul 2>&1

echo [INFO] Test des modules essentiels...
echo.

:: Test requests
python -c "import requests; print('  [OK] requests - version:', requests.__version__)" 2>nul
if errorlevel 1 (
    echo   [MANQUE] requests - requetes HTTP
    set modules_missing=1
) else (
    echo   [OK] requests detecte
)

:: Test beautifulsoup4
python -c "import bs4; print('  [OK] beautifulsoup4 - version:', bs4.__version__)" 2>nul
if errorlevel 1 (
    echo   [MANQUE] beautifulsoup4 - analyse HTML
    set modules_missing=1
) else (
    echo   [OK] beautifulsoup4 detecte
)

:: Test lxml
python -c "import lxml; print('  [OK] lxml detecte')" 2>nul
if errorlevel 1 (
    echo   [MANQUE] lxml - parser XML/HTML
    set modules_missing=1
) else (
    echo   [OK] lxml detecte
)

:: Test tqdm
python -c "import tqdm; print('  [OK] tqdm - version:', tqdm.__version__)" 2>nul
if errorlevel 1 (
    echo   [MANQUE] tqdm - barres de progression
    set modules_missing=1
) else (
    echo   [OK] tqdm detecte
)

:: Test python-dateutil
python -c "import dateutil; print('  [OK] python-dateutil detecte')" 2>nul
if errorlevel 1 (
    echo   [MANQUE] python-dateutil - gestion des dates
    set modules_missing=1
) else (
    echo   [OK] python-dateutil detecte
)

:: Test fake-useragent
python -c "import fake_useragent; print('  [OK] fake-useragent detecte')" 2>nul
if errorlevel 1 (
    echo   [MANQUE] fake-useragent - simulation navigateurs
    set modules_missing=1
) else (
    echo   [OK] fake-useragent detecte
)

:: Test urllib3
python -c "import urllib3; print('  [OK] urllib3 - version:', urllib3.__version__)" 2>nul
if errorlevel 1 (
    echo   [MANQUE] urllib3 - requetes HTTP avancees
    set modules_missing=1
) else (
    echo   [OK] urllib3 detecte
)

:: Test tkinter
python -c "import tkinter; print('  [OK] tkinter - interface graphique')" 2>nul
if errorlevel 1 (
    echo   [MANQUE] tkinter - interface graphique
    set modules_missing=1
) else (
    echo   [OK] tkinter detecte
)

if defined modules_missing (
    echo.
    echo [ECHEC] Un ou plusieurs modules manquent
    echo         Solution: pip install -r requirements.txt
    echo         OU relancez install_auto.bat
) else (
    echo.
    echo [SUCCES] Tous les modules critiques sont installes
    set modules_status=SUCCES
)
echo.

:test_mainpy
:: ===============================================
:: TEST 6: VERIFICATION DU FICHIER PRINCIPAL
:: ===============================================
echo [TEST 6/7] Verification du fichier principal...

if not exist "main.py" (
    echo [ECHEC] Fichier main.py introuvable
    echo         Le fichier principal de l'application est manquant
    echo         Solution: Telechargez le projet complet depuis GitHub
) else (
    echo [SUCCES] Fichier main.py present
    
    :: Test basique de syntaxe Python
    if "%python_status%"=="SUCCES" (
        echo [INFO] Test de syntaxe du fichier principal...
        python -m py_compile main.py >nul 2>&1
        if errorlevel 1 (
            echo [AVERTISSEMENT] Erreur de syntaxe dans main.py
            echo                 Le fichier peut etre corrompu
        ) else (
            echo [SUCCES] Syntaxe du fichier principale valide
            set mainpy_status=SUCCES
        )
    )
)
echo.

:: ===============================================
:: TEST 7: VERIFICATION DES DOSSIERS
:: ===============================================
echo [TEST 7/7] Verification des dossiers de travail...

set folder_issues=0

if not exist "data" (
    echo [AVERTISSEMENT] Dossier data absent
    echo [INFO] Creation du dossier data...
    mkdir data
    echo [SUCCES] Dossier data cree
) else (
    echo [SUCCES] Dossier data present
)

if not exist "scripts" (
    echo [AVERTISSEMENT] Dossier scripts absent
    echo [INFO] Creation du dossier scripts...
    mkdir scripts
    echo [SUCCES] Dossier scripts cree
) else (
    echo [SUCCES] Dossier scripts present
)

if not exist "start.bat" (
    echo [AVERTISSEMENT] Fichier start.bat absent a la racine
    set folder_issues=1
) else (
    echo [SUCCES] start.bat present a la racine
)

if !folder_issues! equ 0 (
    set data_status=SUCCES
)

echo.

:: ===============================================
:: RESUME FINAL
:: ===============================================
echo =====================================================
echo                  RESUME DU DIAGNOSTIC
echo =====================================================
echo.

echo Composant                    Status
echo ------------------------     ----------------
echo Git                          %git_status%
echo Python                       %python_status%
echo pip                          %pip_status%
echo Environnement virtuel        %venv_status%
echo Modules Python               %modules_status%
echo Fichier principal (main.py)  %mainpy_status%
echo Structure dossiers          %data_status%

echo.

:: Compter les succès
set success_count=0
if "%git_status%"=="SUCCES" set /a success_count+=1
if "%python_status%"=="SUCCES" set /a success_count+=1
if "%pip_status%"=="SUCCES" set /a success_count+=1
if "%venv_status%"=="SUCCES" set /a success_count+=1
if "%modules_status%"=="SUCCES" set /a success_count+=1
if "%mainpy_status%"=="SUCCES" set /a success_count+=1
if "%data_status%"=="SUCCES" set /a success_count+=1

echo =====================================================
echo                    CONCLUSION
echo =====================================================
echo.

if %success_count% equ 7 (
    echo [EXCELLENT] Tous les tests sont passes ! (%success_count%/7)
    echo [INFO] Votre installation est parfaitement fonctionnelle
    echo.
    echo VOUS POUVEZ:
    echo 1. Lancer l'application avec: start.bat
    echo 2. OU executer directement: python main.py
    echo 3. Tester avec: scripts\premier_test.bat
    echo.
) else if %success_count% geq 5 (
    echo [BON] La plupart des tests sont passes (%success_count%/7)
    echo [INFO] L'application devrait fonctionner avec quelques limitations
    echo.
    echo ACTIONS RECOMMANDEES:
    echo 1. Corrigez les problemes mentionnes ci-dessus
    echo 2. OU relancez install_auto.bat pour reparer
    echo.
) else if %success_count% geq 3 (
    echo [MOYEN] Certains composants manquent (%success_count%/7)
    echo [INFO] L'installation est incomplete
    echo.
    echo ACTIONS REQUISES:
    echo 1. Relancez install_auto.bat
    echo 2. Suivez les solutions mentionnees pour chaque echec
    echo.
) else (
    echo [PROBLEMATIQUE] Installation largement incomplete (%success_count%/7)
    echo [INFO] L'application ne peut pas fonctionner correctement
    echo.
    echo ACTIONS URGENTES:
    echo 1. Relancez completement install_auto.bat
    echo 2. Verifiez votre connexion internet
    echo 3. Verificz les permissions (execution en administrateur?)
    echo 4. Consultez le README.md pour plus de details
    echo.
)

:: ===============================================
:: INFORMATIONS SYSTEME SUPPLEMENTAIRES
:: ===============================================
echo =====================================================
echo              INFORMATIONS SYSTEME
echo =====================================================
echo.

echo Version de Windows:
ver

echo.
echo Variables d'environnement PATH importantes:
echo PATH contient-il Python?
echo %PATH% | findstr /i python >nul
if errorlevel 1 (
    echo [NON] Python n'est pas dans le PATH
) else (
    echo [OUI] Python est dans le PATH
)

echo PATH contient-il Git?
echo %PATH% | findstr /i git >nul
if errorlevel 1 (
    echo [NON] Git n'est pas dans le PATH
) else (
    echo [OUI] Git est dans le PATH
)

echo.
echo Structure du projet:
echo Dossier actuel: %CD%
echo Fichiers racine:
if exist "main.py" echo   [OK] main.py
if exist "start.bat" echo   [OK] start.bat
if exist "test.bat" echo   [OK] test.bat
if exist "install_auto.bat" echo   [OK] install_auto.bat
if exist "requirements.txt" echo   [OK] requirements.txt
echo Dossiers:
if exist "data" echo   [OK] data/
if exist "scripts" echo   [OK] scripts/
if exist "venv" echo   [OK] venv/

echo.

:: ===============================================
:: SUGGESTIONS FINALES
:: ===============================================
if %success_count% lss 7 (
    echo =====================================================
    echo                    SUGGESTIONS
    echo =====================================================
    echo.
    echo Pour resoudre les problemes:
    echo.
    echo 1. SOLUTION SIMPLE: Relancez install_auto.bat
    echo    Cette commande repare automatiquement la plupart des problemes
    echo.
    echo 2. SOLUTION MANUELLE:
    if "%python_status%"=="ECHEC" (
        echo    - Installez Python: https://python.org/downloads
        echo      IMPORTANT: Cochez "Add Python to PATH"
    )
    if "%git_status%"=="ECHEC" (
        echo    - Installez Git: https://git-scm.com/download/win
    )
    if "%venv_status%"=="ECHEC" (
        echo    - Recreez l'environnement: rmdir /s /q venv puis install_auto.bat
    )
    if "%modules_status%"=="ECHEC" (
        echo    - Installez les modules: pip install -r requirements.txt
    )
    echo.
    echo 3. EN CAS DE PROBLEME PERSISTANT:
    echo    - Redemarrez votre ordinateur
    echo    - Verifiez votre antivirus (ajoutez le dossier aux exceptions)
    echo    - Executez en tant qu'administrateur
    echo    - Consultez le README.md pour plus de details
    echo.
)

echo =====================================================
echo               DIAGNOSTIC TERMINE
echo =====================================================
echo.

if %success_count% equ 7 (
    echo [PARFAIT] Installation completement fonctionnelle !
    echo.
    echo PROCHAINES ETAPES RECOMMANDEES:
    echo 1. Lancez scripts\premier_test.bat pour apprendre
    echo 2. Utilisez start.bat pour l'application principale
    echo 3. Consultez le README.md pour plus d'informations
) else (
    echo [ACTION REQUISE] Consultez les suggestions ci-dessus
)

echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul