# Installation Guide - Web Scraper Suite

## 🔧 Prérequis Windows

### Python
- **Version** : Python 3.8+ (recommandé 3.10+)
- **Architecture** : x64 recommandée
- **Téléchargement** : [python.org](https://www.python.org/downloads/windows/) ou Microsoft Store

### Installation Python
1. Télécharger l'installateur Windows x64
2. ⚠️ **Important** : Cocher "Add Python to PATH"
3. Choisir "Install for all users" (optionnel)
4. Vérifier l'installation :
```cmd
python --version
pip --version
```

## 📦 Installation

### Étapes d'Installation

```cmd
# 1. Créer un dossier pour le projet
mkdir C:\WebScraper
cd C:\WebScraper

# 2. Télécharger/extraire les fichiers du projet
# (placer tous les fichiers Python dans ce dossier)

# 3. Créer l'environnement virtuel
python -m venv venv

# 4. Activer l'environnement virtuel
venv\Scripts\activate

# 5. Mettre à jour pip
python -m pip install --upgrade pip

# 6. Installer les dépendances
pip install -r requirements.txt
```

## 📋 Requirements.txt

Créer un fichier `requirements.txt` avec ce contenu :

```txt
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
tqdm>=4.64.0
python-dateutil>=2.8.0
fake-useragent>=1.2.0
urllib3>=1.26.0
```

> **Note** : `tkinter` est inclus par défaut avec Python sur Windows

## ⚙️ Configuration

### Structure de Données
Le dossier `data` sera créé automatiquement au premier lancement :
```
C:\WebScraper\
├── data\
│   └── [les données seront créées ici]
├── venv\
├── main.py
└── [autres fichiers Python]
```

### Configuration Avancée (Optionnel)

Pour personnaliser les headers HTTP, modifier le fichier `utils/common_utils.py` :

```python
def get_random_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
```

## 🚀 Vérification Installation

### Test Simple

```cmd
# Test import des modules principaux
python -c "from scraper.site_scraper import SiteScraper; print('✅ Module scraper OK')"
python -c "from scraper.date_extractor import DateExtractor; print('✅ Module extracteur OK')"
python -c "from ui.modern_interface import ModernWebScraperApp; print('✅ Interface OK')"
```

### Test Complet

Créer un fichier `test_install.py` :

```python
import sys
import requests
from pathlib import Path

def test_modules():
    modules = [
        'scraper.site_scraper',
        'scraper.date_extractor', 
        'scraper.keyword_searcher',
        'organizer.date_organizer',
        'organizer.csv_exporter',
        'ui.modern_interface'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    return True

def test_network():
    try:
        response = requests.get('https://httpbin.org/get', timeout=5)
        print(f"✅ Connexion réseau OK")
        return True
    except:
        print("❌ Problème de connexion réseau")
        return False

def test_permissions():
    try:
        Path('data').mkdir(exist_ok=True)
        test_file = Path('data/test.txt')
        test_file.write_text('test')
        test_file.unlink()
        print("✅ Permissions dossier OK")
        return True
    except:
        print("❌ Problème de permissions")
        return False

if __name__ == "__main__":
    print("🔍 Test d'installation Web Scraper Suite")
    print("-" * 50)
    
    success = all([
        test_modules(),
        test_network(), 
        test_permissions()
    ])
    
    if success:
        print("\n🎉 Installation validée !")
    else:
        print("\n❌ Problèmes détectés")
```

Puis l'exécuter :
```cmd
python test_install.py
```

## 🏃 Démarrage

### Interface Graphique

```cmd
# S'assurer que l'environnement virtuel est activé
venv\Scripts\activate

# Lancer l'interface graphique
python main.py

# Alternative sans console (Windows)
python no_console_launcher.py
```

### Utilisation CLI

```cmd
# Activer l'environnement virtuel
venv\Scripts\activate

# Scraping direct
python scraper/site_scraper.py

# Extraction de dates
python scraper/date_extractor.py

# Recherche de mots-clés
python scraper/keyword_searcher.py

# Organisation par dates
python organizer/date_organizer.py

# Export CSV
python organizer/csv_exporter.py
```

### API Programmatique

Créer un script `exemple.py` :

```python
from scraper.site_scraper import SiteScraper
from scraper.date_extractor import DateExtractor

# Configuration
url = "https://example.com"
output_file = "data/urls.txt"

# Scraping
scraper = SiteScraper(url, output_file, max_urls=1000)
urls = scraper.scrape()
print(f"URLs trouvées: {len(urls)}")

# Extraction dates
extractor = DateExtractor("data/urls.txt", max_threads=10)
dates_found, total, output = extractor.run()
print(f"Dates extraites: {dates_found}/{total}")
```

## 🔧 Configuration Performance

### Optimisation Threading

Modifier dans les modules selon votre PC :

```python
# Pour PC moyens
max_threads = 5

# Pour PC puissants  
max_threads = 15

# Auto-détection (recommandé)
import os
max_threads = min(10, os.cpu_count() * 2)
```

### Délais entre Requêtes

```python
# Dans site_scraper.py - ligne ~200 environ
time.sleep(random.uniform(0.5, 1.0))  # Plus lent mais plus respectueux

# Dans date_extractor.py - ligne ~300 environ  
time.sleep(random.uniform(0.2, 0.5))  # Standard

# Pour sites rapides uniquement
time.sleep(random.uniform(0.1, 0.2))  # Plus rapide mais risqué
```

## 🐛 Problèmes Courants

### Erreur "Python n'est pas reconnu"
```cmd
# Ajouter Python au PATH Windows
# Panneau de configuration > Système > Variables d'environnement
# Ajouter à PATH : C:\Users\[nom]\AppData\Local\Programs\Python\Python310\
```

### Erreur SSL Certificate
```cmd
pip install --upgrade certifi requests urllib3
```

### Problème d'encodage
```cmd
# Dans l'invite de commande, avant de lancer :
chcp 65001
set PYTHONIOENCODING=utf-8
```

### Module tkinter non trouvé
Réinstaller Python en cochant "tcl/tk and IDLE" dans les options

### Erreurs de mémoire
```python
# Réduire le nombre de threads dans les modules
max_threads = 3  # Au lieu de 10+

# Réduire la taille des batches
batch_size = 100  # Au lieu de 1000
```

### Antivirus bloque l'exécution
Ajouter le dossier du projet aux exceptions de l'antivirus

## 📊 Utilisation

### Workflow Recommandé

1. **Lancer l'interface graphique**
```cmd
venv\Scripts\activate
python main.py
```

2. **Onglet "Scraper de Site"**
   - Entrer l'URL du site
   - Choisir le fichier de sortie
   - Définir une limite d'URLs (optionnel)
   - Cliquer "Démarrer le Scraping"

3. **Onglet "Extraction de Dates"**
   - Sélectionner le fichier d'URLs créé
   - Choisir le fichier CSV de sortie
   - Ajuster le nombre de threads
   - Cliquer "Démarrer l'Extraction"

4. **Onglet "Organisateur"**
   - Sélectionner le fichier CSV des dates
   - Choisir le dossier de sortie
   - Cliquer "Démarrer l'Organisation"

5. **Onglet "Exportation CSV"**
   - Sélectionner le mode d'export
   - Configurer les options
   - Cliquer "Démarrer l'Exportation"

### Conseils d'Utilisation

- **Commencer petit** : Tester avec 100-500 URLs max
- **Surveiller les performances** : Ajuster les threads selon votre PC
- **Respecter les sites** : Éviter de surcharger les serveurs
- **Sauvegarder régulièrement** : Les données sont dans le dossier `data/`

## 🔄 Désinstallation

```cmd
# Désactiver l'environnement virtuel
deactivate

# Supprimer le dossier complet
rmdir /s C:\WebScraper
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifier que Python 3.8+ est installé
2. S'assurer que l'environnement virtuel est activé
3. Relancer `pip install -r requirements.txt`
4. Tester avec le script `test_install.py`

**Installation Express**
```cmd
# Commandes rapides pour installation complète
mkdir C:\WebScraper && cd C:\WebScraper
python -m venv venv
venv\Scripts\activate
pip install requests beautifulsoup4 lxml tqdm python-dateutil fake-useragent urllib3
python main.py
```