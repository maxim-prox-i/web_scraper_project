# 🕷️ Web Scraper Suite

**L'outil tout-en-un pour récupérer et organiser automatiquement les données de sites web !**

> 🎯 **Idéal pour** : Journalistes, chercheurs, analystes, étudiants, entrepreneurs, ou toute personne qui veut récupérer facilement des informations sur internet.

## 🤔 Qu'est-ce que c'est ?

Web Scraper Suite est un **outil gratuit et facile** qui vous permet de :
- 📥 **Récupérer automatiquement** tous les liens d'un site web
- 📅 **Extraire les dates** de publication des articles
- 📂 **Organiser** tout par année et par mois
- 📊 **Exporter** vers Excel/CSV pour vos analyses
- 🔍 **Rechercher** des mots-clés spécifiques dans les pages

**Pas besoin d'être informaticien !** L'interface est simple avec des boutons et des étapes claires.

### 💡 **Exemples concrets d'utilisation**
```
🎯 Analyser 5 ans d'articles du Monde sur l'écologie
🎯 Récupérer tous les communiqués de presse d'une entreprise
🎯 Constituer une base de données d'articles scientifiques
🎯 Surveiller les mentions d'une marque sur différents sites
```

### **⏱️ Gain de temps : 15 minutes au lieu de plusieurs semaines !**

---

# 🚀 INSTALLATION COMPLÈTE ÉTAPE PAR ÉTAPE

> **👋 Nouveau ?** Suivez ce guide unique qui vous mène de zéro à un outil fonctionnel en 20 minutes !

## 🚨 AVANT DE COMMENCER

**⚠️ Ce que nous allons installer :**
- Git (pour télécharger et mettre à jour le projet)
- Python 3.11 (langage de programmation nécessaire)
- Web Scraper Suite (l'outil principal)

**💾 Espace requis :** 500 MB sur votre disque dur  
**⏱️ Temps requis :** 20 minutes maximum  
**🌐 Connexion internet :** Obligatoire pendant l'installation

---

## 📋 ÉTAPE 1 : Ouvrir l'invite de commande Windows

### **1.1 - Ouvrir la fenêtre "Exécuter"**
- Appuyez **en même temps** sur les touches `Windows` + `R` de votre clavier
- Une petite fenêtre s'ouvre en bas à gauche :

```
┌─ Exécuter ───────────────────────┐
│                                  │
│ Ouvrir: [_____________________]  │
│                                  │
│    [OK]  [Annuler]  [Parcourir]  │
└──────────────────────────────────┘
```

### **1.2 - Ouvrir l'invite de commande**
- Dans la case qui clignote, tapez exactement : **`cmd`**
- Appuyez sur `Entrée` ou cliquez sur `OK`

### **1.3 - Vérifier l'ouverture**
Une fenêtre noire s'ouvre avec du texte blanc :
```
Microsoft Windows [Version 10.0.19041.1234]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\VotreNom>_
```

**✅ Parfait ! Ne fermez PAS cette fenêtre, nous en aurons besoin.**

---

## 📂 ÉTAPE 2 : Aller dans le dossier Documents

### **2.1 - Naviguer vers Documents**
Dans la fenêtre noire, copiez-collez cette commande :
```
cd %USERPROFILE%\Documents
```

**Comment copier-coller :**
- Sélectionnez la commande ci-dessus → `Ctrl + C`
- **Clic droit** dans la fenêtre noire → **Coller**
- Appuyez sur `Entrée`

### **2.2 - Vérification**
Vous devriez voir :
```
C:\Users\VotreNom\Documents>_
```

**✅ Vous êtes maintenant dans le bon dossier !**

---

## 🌐 ÉTAPE 3 : Installation de Git (Gestionnaire de versions)

### **3.1 - Tester si Git est déjà installé**
Dans l'invite de commande, tapez :
```
git --version
```

**Si vous voyez quelque chose comme :**
```
git version 2.40.1.windows.1
```
**✅ Git est déjà installé ! Passez à l'ÉTAPE 4.**

**Si vous voyez :**
```
'git' n'est pas reconnu en tant que commande interne...
```
**→ Continuez ci-dessous pour installer Git.**

### **3.2 - Télécharger Git**
1. **Ouvrez votre navigateur** (Chrome, Firefox, Edge...)
2. **Allez sur** : https://git-scm.com/download/win
3. **Cliquez sur** : "Git for Windows/x64 Setup" (le téléchargement commence automatiquement)

### **3.3 - Installer Git**
1. **Ouvrez le fichier téléchargé** (`Git-X.X.X-64-bit.exe`)
2. **Suivez l'installation avec ces paramètres :**

**Écrans importants :**
- **"Select Components"** → ✅ Cochez **"Add a Git Bash Profile to Windows Terminal"** → Cliquer sur "next"
- **"Choosing the default editor used bt Git"** → Cliquer sur "next"
- **"Adjusting the name of the initial branch in the new repositories"** → Cliquer sur "next"
- **"Adjusting your PATH environment"** → ✅ Sélectionnez **"Git from the command line and also from 3rd-party software"** → Cliquer sur "next"
- **"Choosing the SSH executable"** → Cliquer sur "next"
- **"Choosing HTTPS transport Backend"** → Cliquer sur "next"
- **"Configuring the line ending conversions"** → Cliquer sur "next"
- **"Configuring the terminal emulator to use with Git Bash"** → Cliquer sur "next"
- **"Choose the default behavio of 'git pull'"** → Cliquer sur "next"
- **"Choose a crediential helper"** → Cliquer sur "next"
- **"Configuring extra option"** → Cliquer sur "Install" et attendre la fin de l'installation
- !! **Ne pas cocher la case "View Release Notes"**, pour ne pas avoir une page navigateur qui s'ouvre simplement
- Cliquer sur "finish"

### **3.4 - Redémarrer l'invite de commande**
- **Fermez** la fenêtre noire actuelle
- **Refaites l'ÉTAPE 1** pour rouvrir l'invite de commande
- **Refaites l'ÉTAPE 2** pour retourner dans Documents

### **3.5 - Vérifier l'installation de Git**
Tapez à nouveau :
```
git --version
```

**Vous devriez voir :**
```
git version 2.40.1.windows.1
```

**✅ Git est maintenant installé et fonctionnel !**

---

## 🐍 ÉTAPE 4 : Installation de Python

### **4.1 - Tester si Python est déjà installé**
Dans l'invite de commande, tapez :
```
python --version
```

**Si vous voyez quelque chose comme :**
```
Python 3.11.5
```
**✅ Python est déjà installé ! Passez à l'ÉTAPE 5.**

**Si vous voyez :**
```
'python' n'est pas reconnu en tant que commande interne...
```
**→ Continuez ci-dessous pour installer Python.**

### **4.2 - Télécharger Python**
1. **Ouvrez votre navigateur**
2. **Allez sur** : https://www.python.org/downloads/
3. **Cliquez sur le gros bouton jaune** : "Download Python 3.xx.x"

### **4.3 - Installer Python**
1. **Ouvrez le fichier téléchargé** (`python-3.xx.X-amd64.exe`)
2. **⚠️ IMPORTANT :** Cochez **"Add Python 3.xx to PATH"** en bas de la fenêtre
3. **Cliquez** : "Install Now"
4. **Attendez la fin** de l'installation (5-10 minutes)
5. **Cliquez** : "Close"

### **4.4 - Redémarrer l'invite de commande**
- **Fermez** la fenêtre noire actuelle
- **Refaites l'ÉTAPE 1** pour rouvrir l'invite de commande
- **Refaites l'ÉTAPE 2** pour retourner dans Documents

### **4.5 - Vérifier l'installation de Python**
Tapez :
```
python --version
```

**Vous devriez voir :**
```
Python 3.11.5
```

**✅ Python est maintenant installé et fonctionnel !**

---

## 📥 ÉTAPE 5 : Télécharger Web Scraper Suite

### **5.1 - Cloner le projet avec Git**
Dans l'invite de commande (dans Documents), tapez :
```
git clone https://github.com/maxim-prox-i/web_scraper_project.git
```

**Vous verrez :**
```
Cloning into 'web_scraper_project'...
remote: Enumerating objects: 150, done.
remote: Counting objects: 100% (150/150), done.
remote: Compressing objects: 100% (95/95), done.
remote: Total 150 (delta 45), reused 130 (delta 35), pack-reused 0
Receiving objects: 100% (150/150), 45.67 KiB | 1.14 MiB/s, done.
Resolving deltas: 100% (45/45), done.
```

### **5.2 - Aller dans le dossier du projet**
Tapez :
```
cd web_scraper_project
```

**Vous devriez voir :**
```
C:\Users\VotreNom\Documents\web_scraper_project>_
```

**✅ Vous êtes maintenant dans le dossier du projet !**

---

## ⚙️ ÉTAPE 6 : Installation automatique de Web Scraper Suite

### **6.1 - Lancer l'installation automatique**
Dans l'invite de commande, tapez :
```
install_auto.bat
```

### **6.2 - Suivre les instructions**
Le script vous posera des questions. **Répondez comme suit :**

**Question 1 :**
```
Voulez-vous continuer l'installation automatique ? (O/N):
```
**→ Tapez : `O` puis `Entrée`**

**Question 2 (si elle apparaît) :**
```
Voulez-vous redemarrer maintenant? (O/N)
```
**→ Tapez : `O` puis `Entrée`**

*Si votre PC redémarre, refaites les étapes 1, 2 et 5.2, puis relancez `install_auto.bat`*

**Question 3 (si elle apparaît) :**
```
Voulez-vous lancer l'application maintenant? (O/N)
```
**→ Tapez : `O` puis `Entrée`**

### **6.3 - Vérifier le succès de l'installation**
À la fin, vous devriez voir :
```
=====================================================
             INSTALLATION TERMINEE !
=====================================================

[EXCELLENT] Tous les composants sont installes et fonctionnels !

FICHIERS CREES :
  ✓ start.bat    - Lance l'application
  ✓ test.bat     - Teste l'installation
  ✓ data/        - Dossier pour vos donnees
  ✓ venv/        - Environnement Python
```

**✅ Installation réussie !**

---

## 🧪 ÉTAPE 7 : Premier test

### **7.1 - Test de l'installation**
Dans l'invite de commande, tapez :
```
test.bat
```

**Vous devriez voir :**
```
[EXCELLENT] Tous les tests sont passes ! (7/7)
[INFO] Votre installation est parfaitement fonctionnelle
```

### **7.2 - Premier test guidé**
Tapez :
```
premier_test.bat
```

**Ce script va :**
- Vous guider étape par étape
- Tester l'outil sur un site simple
- Créer vos premiers fichiers de résultats
- Vous apprendre toutes les fonctionnalités

**⏱️ Durée : 5-10 minutes**

### **7.3 - Lancer l'application principale**
Tapez :
```
start.bat
```

**→ Une fenêtre avec des onglets doit s'ouvrir !**

**✅ Félicitations ! Votre installation est terminée et fonctionnelle !**

---

# 🎮 GUIDE D'UTILISATION

## 📊 Interface Principale - Les 5 Onglets

Quand vous lancez `start.bat`, vous voyez une fenêtre avec 5 onglets :

### **🕷️ Onglet 1 : Scraper de Site**
**Ce qu'il fait :** Récupère tous les liens d'un site web

**Comment l'utiliser :**
1. **URL du site** : Collez l'adresse (ex: `https://lemonde.fr`)
2. **Limite** : Nombre max de pages (ex: `100`, laissez vide = illimité)
3. **Cliquez** : "▶️ Démarrer le Scraping"

**Résultat :** Fichier `urls.txt` avec tous les liens trouvés

### **📅 Onglet 2 : Extraction de Dates**
**Ce qu'il fait :** Trouve les dates de publication des articles

**Comment l'utiliser :**
1. **Fichier d'entrée** : Sélectionnez votre fichier `urls.txt`
2. **Processus** : 10 par défaut (plus = plus rapide)
3. **Cliquez** : "▶️ Démarrer l'Extraction"

**Résultat :** Fichier CSV avec liens + dates

### **📂 Onglet 3 : Organisation par Date**
**Ce qu'il fait :** Classe les articles par année et mois

**Comment l'utiliser :**
1. **Fichier CSV** : Sélectionnez votre fichier avec dates
2. **Nom du projet** : Donnez un nom (ex: "Articles_LeMonde")
3. **Cliquez** : "▶️ Démarrer l'Organisation"

**Résultat :** Dossiers organisés par année/mois

### **📊 Onglet 4 : Export Excel**
**Ce qu'il fait :** Crée un fichier Excel pour vos analyses

**Comment l'utiliser :**
1. **Mode** : "Export direct" (recommandé pour débuter)
2. **Format** : "Un seul fichier" (plus simple)
3. **Cliquez** : "▶️ Démarrer l'Export"

**Résultat :** Fichier Excel prêt pour analyse

### **🔍 Onglet 5 : Recherche de Mots-clés**
**Ce qu'il fait :** Trouve les articles contenant des mots spécifiques

**Comment l'utiliser :**
1. **Mots-clés** : Tapez les termes recherchés (ex: "intelligence artificielle")
2. **Options** : Cochez selon vos besoins
3. **Cliquez** : "▶️ Démarrer la Recherche"

**Résultat :** Articles filtrés par mots-clés

---

## 🎯 Workflow Recommandé pour Débuter

### **Premier test simple (5 minutes) :**
```
1. Onglet "Scraper" → URL: https://example.com → Limite: 10 → Démarrer
2. Onglet "Dates" → Sélectionner le fichier créé → Démarrer  
3. Onglet "Export" → Mode: Export direct → Démarrer
4. Ouvrir le fichier Excel créé !
```

### **Analyse complète d'un site :**
```
1. Scraper → URL du site → Limite: 500 → Démarrer
2. Dates → Fichier URLs → Démarrer
3. Organisation → Fichier CSV → Nom projet → Démarrer
4. Export → Mode avancé → Démarrer
5. Recherche → Mots-clés spécifiques → Démarrer
```

---

## 📁 Où Trouver Vos Résultats

Tous vos fichiers sont sauvegardés dans le dossier `data/` :

```
📁 web_scraper_project/
  📁 data/
    📄 urls.txt              (liens récupérés)
    📄 urls_with_dates.csv   (liens + dates)
    📄 export_final.csv      (fichier Excel)
    📁 VotreProjet_2024/     (organisation par date)
      📁 2024/
        📁 01_Janvier/
        📁 02_Février/
```

---

# 🛠️ RÉSOLUTION DE PROBLÈMES

## ❌ L'installation a échoué

### **Diagnostic automatique :**
```
test.bat
```
Ce script teste tous les composants et vous dit exactement quoi réparer.

### **Solutions courantes :**

**1. "git n'est pas reconnu"**
- Réinstallez Git depuis https://git-scm.com/download/win
- ⚠️ Cochez bien "Add Git to PATH" pendant l'installation
- Redémarrez votre PC

**2. "python n'est pas reconnu"**
- Réinstallez Python depuis https://python.org/downloads
- ⚠️ Cochez bien "Add Python to PATH" pendant l'installation  
- Redémarrez votre PC

**3. "L'installation s'interrompt"**
- Désactivez temporairement votre antivirus
- Exécutez l'invite de commande en administrateur (clic droit → "Exécuter en tant qu'administrateur")
- Relancez `install_auto.bat`

---

## ❌ L'application ne démarre pas

### **Solutions étape par étape :**

**1. Test rapide :**
```
cd %USERPROFILE%\Documents\web_scraper_project
test.bat
```

**2. Réparation automatique :**
```
install_auto.bat
```

**3. Réparation manuelle :**
```
rmdir /s /q venv
install_auto.bat
```

---

## ❌ Résultats incomplets ou erreurs

### **Optimisations :**

**1. Réduire la charge :**
- Diminuez le nombre de processus (de 10 à 3-5)
- Ajoutez des délais entre requêtes
- Limitez le nombre d'URLs (commencez par 50-100)

**2. Sites problématiques :**
- Évitez les sites e-commerce (protections anti-bot)
- Évitez les réseaux sociaux (restrictions)
- Privilégiez les blogs et sites d'actualités

**3. Paramètres recommandés pour débuter :**
- **Limite URLs :** 100
- **Processus :** 5
- **Délai :** 2 secondes

---

# 🔄 MAINTENANCE ET MISES À JOUR

## 🔄 Mettre à jour vers la dernière version

### **Mise à jour automatique :**
```
cd %USERPROFILE%\Documents\web_scraper_project
update.bat
```

Ce script :
- Télécharge les nouveautés
- Met à jour les modules Python
- Preserve vos données existantes

### **Mise à jour manuelle :**
Si `update.bat` ne fonctionne pas :

1. **Sauvegardez vos données :**
   ```
   xcopy data data_backup /e /i
   ```

2. **Téléchargez la nouvelle version :**
   ```
   git pull origin main
   ```

3. **Réinstallez :**
   ```
   install_auto.bat
   ```

---

## 🧹 Nettoyage et Optimisation

### **Libérer de l'espace :**
```
# Supprimer les fichiers temporaires
del /q temp_*
rmdir /s /q __pycache__

# Nettoyer les logs anciens (gardez les 10 derniers)
```

### **Réinitialisation complète :**
```
# Supprime tout sauf vos données
rmdir /s /q venv
del *.log
install_auto.bat
```

---

# 📈 ASTUCES ET OPTIMISATIONS

## 🎯 Sites Parfaits pour Commencer

### **✅ Sites faciles :**
- Blogs WordPress
- Sites d'actualités (LeMonde, LeFigaro)
- Sites gouvernementaux (.gouv.fr)
- Communiqués de presse d'entreprises

### **⚠️ Sites difficiles :**
- Sites e-commerce (Amazon, etc.)
- Réseaux sociaux (Facebook, Twitter)
- Sites avec CAPTCHA
- Sites 100% JavaScript

---

## ⚡ Optimisation des Performances

### **Paramètres recommandés par taille :**

**Petit site (< 1000 pages) :**
- Processus : 10
- Délai : 1 seconde
- Timeout : 30 secondes

**Site moyen (1000-10000 pages) :**
- Processus : 5
- Délai : 2 secondes  
- Timeout : 45 secondes

**Gros site (> 10000 pages) :**
- Processus : 3
- Délai : 5 secondes
- Timeout : 60 secondes

---

## 🔍 Recherches Avancées

### **Syntaxe des mots-clés :**
```
"intelligence artificielle"    # Expression exacte
intelligence, IA, robot       # L'un de ces mots
intelligence -artificielle    # Intelligence mais pas artificielle
```

### **Formats de dates reconnus :**
- Français : 15 janvier 2024, 15/01/2024
- Anglais : January 15, 2024, 01/15/2024  
- ISO : 2024-01-15
- URLs : /2024/01/15/

---

# 🎓 FORMATION ET SUPPORT

## 📚 Scripts d'Apprentissage Inclus

### **🧪 `premier_test.bat`**
- Test guidé interactif
- Apprend toutes les fonctionnalités
- Crée des exemples concrets
- **⏱️ Durée :** 10 minutes

### **🩺 `test.bat`**
- Diagnostic complet (7 tests)
- Identifie tous les problèmes
- Propose des solutions
- **⏱️ Durée :** 2 minutes

---

## 📞 Aide et Support

### **🆘 En cas de problème persistant :**

1. **Diagnostique automatique :**
   ```
   test.bat
   ```

2. **Informations système :**
   - Version Windows : `Win + R` → `winver`
   - Espace disque : Vérifiez qu'il reste > 1 GB
   - Antivirus : Ajoutez le dossier aux exceptions

3. **Réinstallation propre :**
   ```
   # Sauvegarde
   xcopy data data_backup /e /i
   
   # Suppression complète
   cd ..
   rmdir /s /q web_scraper_project
   
   # Reinstallation depuis le début
   git clone https://github.com/maxim-prox-i/web_scraper_project.git
   cd web_scraper_project
   install_auto.bat
   
   # Restauration des données
   xcopy ..\data_backup data /e /i
   ```

---

# 🌟 FONCTIONNALITÉS AVANCÉES

## 🤖 Automatisation

### **Scraping programmé :**
Créez un fichier `auto_scrape.bat` :
```batch
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python -c "
from scraper.site_scraper import SiteScraper
scraper = SiteScraper('https://votre-site.com', 'data/auto_urls.txt', 1000)
urls = scraper.scrape()
print(f'Scraping automatique: {len(urls)} URLs trouvées')
"
```

### **Planification Windows :**
1. Ouvrez "Planificateur de tâches" Windows
2. Créez une tâche qui lance votre script `auto_scrape.bat`
3. Programmez l'exécution (quotidienne, hebdomadaire...)

---

## 📊 Analyses Avancées

### **Export personnalisé :**
- Modifiez les templates dans `organizer/`
- Ajoutez vos propres colonnes Excel
- Créez des graphiques automatiques

### **Intégration avec d'autres outils :**
- Excel : Ouvrez directement les CSV
- Power BI : Importez pour des dashboards
- Python : Utilisez les modules directement

---

# ✅ CHECKLIST DE RÉUSSITE

## 🎯 Après Installation

**Vérifiez que vous pouvez :**
- [ ] Lancer `start.bat` sans erreur
- [ ] Voir l'interface avec 5 onglets
- [ ] Faire un scraping simple (exemple.com)
- [ ] Exporter vers Excel
- [ ] Ouvrir le fichier Excel créé

## 🚀 Après Premier Usage

**Vérifiez que vous savez :**
- [ ] Choisir les bons paramètres pour un site
- [ ] Organiser les résultats par date  
- [ ] Rechercher des mots-clés spécifiques
- [ ] Mettre à jour l'outil (`update.bat`)
- [ ] Diagnostiquer les problèmes (`test.bat`)

---

# 🎉 FÉLICITATIONS !

**Vous maîtrisez maintenant Web Scraper Suite !**

**Ce que vous pouvez faire maintenant :**
- ✅ Analyser n'importe quel site web public
- ✅ Organiser des milliers d'articles automatiquement  
- ✅ Créer des bases de données Excel professionelles
- ✅ Effectuer des veilles automatisées
- ✅ Gagner des heures de travail manuel

**🚀 Commencez dès maintenant :**
```
start.bat
```

**📈 Explorez, expérimentez, et découvrez tout ce que vous pouvez accomplir avec vos nouvelles données !**

---

*Développé avec ❤️ pour simplifier la vie de tous ceux qui travaillent avec des données web*

**Version :** 2024.1 | **Dernière mise à jour :** Juillet 2025