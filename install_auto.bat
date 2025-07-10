@echo off
setlocal

echo Installation Web Scraper - Automatique
echo =====================================

where winget >nul 2>&1 || (echo ERREUR: winget requis & pause & exit /b 1)
ping google.com -n 1 >nul 2>&1 || (echo ERREUR: connexion internet requise & pause & exit /b 1)

where git >nul 2>&1 || (
    echo Installation Git...
    winget install Git.Git -e --silent --accept-package-agreements --accept-source-agreements
)

where python >nul 2>&1 || (
    echo Installation Python...
    winget install Python.Python.3.11 -e --silent --accept-package-agreements --accept-source-agreements
)

if not exist "main.py" (
    echo Telechargement projet...
    git clone https://github.com/maxim-prox-i/web_scraper_project.git . 2>nul || (
        powershell -Command "Invoke-WebRequest 'https://github.com/maxim-prox-i/web_scraper_project/archive/main.zip' -OutFile 'temp.zip'; Expand-Archive 'temp.zip' -Force; Move-Item 'web_scraper_project-main\*' .; Remove-Item 'temp.zip','web_scraper_project-main' -Recurse -Force"
    )
)

if exist "venv" rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat

if not exist "requirements.txt" (
    echo requests^>=2.31.0>requirements.txt
    echo beautifulsoup4^>=4.12.0>>requirements.txt
    echo lxml^>=4.9.0>>requirements.txt
    echo tqdm^>=4.66.0>>requirements.txt
    echo fake-useragent^>=1.4.0>>requirements.txt
)

pip install -r requirements.txt --quiet

if not exist "data" mkdir data
if not exist "scripts" mkdir scripts

echo.
echo Installation terminee. Lancez: start.bat
pause