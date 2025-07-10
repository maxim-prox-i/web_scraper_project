@echo off

echo ATTENTION: DESINSTALLATION DU PROJET
echo ======================================
echo.
echo CETTE ACTION VA SUPPRIMER:
echo - L'environnement virtuel Python
echo - Tous les dossiers data et scripts
echo - Tous les fichiers de configuration
echo - L'historique Git local
echo.
echo ATTENTION: CETTE ACTION EST IRREVERSIBLE
echo.
set /p confirm="Etes-vous sur de vouloir desinstaller ? (tapez OUI): "
if /i not "%confirm%"=="OUI" (
    echo Desinstallation annulee
    pause
    exit /b 0
)
echo.
echo Desinstallation en cours...

if exist "venv" (
    echo Suppression environnement virtuel...
    rmdir /s /q venv
)

if exist "data" (
    echo Suppression dossier data...
    rmdir /s /q data
)

if exist "scripts" (
    echo Suppression dossier scripts...
    rmdir /s /q scripts
)

if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /q *.pyc
if exist "temp_*" del /q temp_*
if exist ".git" rmdir /s /q .git

del /q requirements.txt 2>nul
del /q start.bat 2>nul
del /q test.bat 2>nul
del /q install_simple.bat 2>nul
del /q update_simple.bat 2>nul

echo.
echo Desinstallation terminee
echo Pour supprimer completement : supprimez ce dossier
pause