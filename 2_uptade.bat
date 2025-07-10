@echo off

echo Mise a jour automatique...

where git >nul || (echo ERREUR: Git requis & pause & exit /b 1)
if not exist ".git" (echo ERREUR: Pas un repository Git & pause & exit /b 1)

git fetch --all --quiet
git checkout main --quiet 2>nul
git reset --hard origin/main --quiet
git clean -fd --quiet

if exist "venv" (
    call venv\Scripts\activate.bat
    if exist "requirements.txt" pip install -r requirements.txt --upgrade --quiet
)

echo Mise a jour terminee - branche main
pause