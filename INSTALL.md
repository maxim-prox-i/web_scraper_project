# Web Scraper Suite - Guide d'Installation

## Prérequis

- Python 3.8+
- pip
- Connexion Internet

## Installation

### 1. Cloner/Télécharger le projet

```bash
git clone <repository-url>
cd web-scraper-suite
```

### 2. Environnement virtuel (recommandé)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Structure de données

Le projet crée automatiquement la structure :
```
data/
└── [domaine]/
    ├── urls.txt
    ├── urls-dates.csv
    └── [année]/
        └── [mois]/
            └── *.urls.txt
```

## Lancement

### Interface Graphique

```bash
python main.py
```

### Sans Console (Windows)

```bash
python no_console_launcher.py
```

### CLI Direct

```bash
# Scraping
python scraper/site_scraper.py

# Extraction dates
python scraper/date_extractor.py

# Recherche mots-clés
python scraper/keyword_searcher.py

# Organisation
python organizer/date_organizer.py

# Export CSV
python organizer/csv_exporter.py
```

## Configuration

### Headers HTTP

Modifiez `utils/common_utils.py` pour personnaliser les headers :
```python
def get_random_headers():
    return {
        'User-Agent': 'Your-Bot/1.0',
        'Accept': 'text/html,application/xhtml+xml',
        # ...
    }
```

### Logging

Configuration dans `utils/logger_config.py` :
```python
setup_logger("MyLogger", "custom.log", logging.DEBUG)
```

### Délais et Limites

Dans chaque module :
```python
# site_scraper.py
time.sleep(random.uniform(0.2, 0.5))  # Délai entre requêtes

# date_extractor.py
max_threads = 10  # Threads concurrents

# keyword_searcher.py
timeout = 15  # Timeout requêtes
```

## Utilisation Rapide

### 1. Workflow Complet (GUI)

1. **Scraper** : URL → `urls.txt`
2. **Date Extractor** : `urls.txt` → `urls-dates.csv`
3. **Organizer** : `urls-dates.csv` → Structure organisée
4. **CSV Exporter** : Structure → `export.csv`

### 2. Workflow CLI

```bash
# 1. Scraping
python scraper/site_scraper.py
# Input: https://example.com
# Output: data/example.com/urls.txt

# 2. Extraction dates
python scraper/date_extractor.py
# Input: data/example.com/urls.txt
# Output: data/example.com/urls-dates.csv

# 3. Organisation
python organizer/date_organizer.py
# Input: data/example.com/urls-dates.csv
# Output: data/example.com/urls_organisees/

# 4. Export
python organizer/csv_exporter.py
# Input: data/example.com/urls_organisees/
# Output: data/example.com/export.csv
```

### 3. API Programmatique

```python
from scraper.site_scraper import SiteScraper
from scraper.date_extractor import DateExtractor

# Scraping
scraper = SiteScraper("https://example.com", max_urls=1000)
urls = scraper.scrape()

# Extraction dates
extractor = DateExtractor("urls.txt", max_threads=5)
dates_found, total, output = extractor.run()
```

## Optimisations

### Performance

```python
# Augmenter les threads
max_threads = 20

# Buffer lecture/écriture
buffering = 1024 * 1024  # 1MB

# Batch processing
batch_size = 1000
```

### Mémoire

```python
# Traitement par chunks
for chunk in pd.read_csv(file, chunksize=10000):
    process(chunk)

# Générateurs
def read_urls():
    with open(file) as f:
        for line in f:
            yield line.strip()
```

## Troubleshooting

### SSL/TLS Errors
```python
verify=False  # Désactive vérification SSL
```

### Rate Limiting
```python
time.sleep(random.uniform(1, 3))  # Augmenter délais
```

### Encoding Issues
```python
encoding='utf-8'  # Forcer UTF-8
```

### Memory Issues
```python
# Réduire batch_size et max_threads
batch_size = 100
max_threads = 5
```

## Logs et Debug

```bash
# Activer logs détaillés
export PYTHONPATH="."
python -v main.py

# Logs spécifiques
tail -f scraper.log
tail -f date_extractor.log
tail -f keyword_searcher.log
```

## Extensions

### Nouveaux Extracteurs

```python
class CustomExtractor:
    def __init__(self, input_file):
        self.input_file = input_file
    
    def run(self, progress_callback=None):
        # Votre logique
        pass
```

### Nouveaux Formats Export

```python
class JSONExporter(BaseExporter):
    def export(self, data):
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
```

### UI Personnalisée

```python
# Nouveau module dans ui/
class CustomTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
```