# 🛠️ Installation Simple - Web Scraper Suite

> **📝 Pour qui ?** Toute personne qui veut utiliser l'outil, même sans connaissances techniques !

## 🎯 Installation Super Rapide (5 minutes)

### **Option 1 : Installation Automatique** ⭐ *Recommandée*

1. **📥 Téléchargez** tous les fichiers du projet dans un dossier
2. **🖱️ Double-cliquez** sur le fichier `install.bat`
3. **☕ Attendez** que l'installation se fasse toute seule
4. **🎉 C'est fini !** 

> ✅ L'installation automatique s'occupe de **tout** : Python, les modules, la configuration...

### **Option 2 : Si vous avez déjà Python**

Si vous savez déjà que Python est installé sur votre PC :

1. **Ouvrez** l'invite de commande Windows
2. **Tapez** : `pip install requests beautifulsoup4 lxml tqdm python-dateutil fake-useragent urllib3`
3. **Attendez** que ça s'installe
4. **Lancez** l'outil avec : `python main.py`

## 🔍 Comment savoir si ça a marché ?

### **Test Simple**
1. **Double-cliquez** sur `start.bat` (créé automatiquement)
2. **Une fenêtre** doit s'ouvrir avec l'interface
3. **Si ça marche** = Installation réussie ! 🎉

### **Si ça ne marche pas**
1. **Double-cliquez** sur `test_install.py`
2. **Regardez** les messages qui s'affichent
3. **Suivez** les conseils donnés

## 📂 Que va-t-il se passer ?

### **Fichiers créés automatiquement**
```
📁 Votre Dossier/
  📁 venv/                    ← Environnement Python (ne pas toucher)
  📁 data/                    ← Vos données seront ici
  📄 start.bat               ← Pour lancer l'outil facilement
  📄 requirements.txt        ← Liste des modules (créé si absent)
  📄 ... autres fichiers Python
```

### **Ce qui se passe dans l'installation**
1. **Vérification** : Python est-il installé ?
2. **Installation Python** : Si absent, téléchargement automatique
3. **Création environnement** : Espace isolé pour l'outil
4. **Installation modules** : Tous les composants nécessaires
5. **Test final** : Vérification que tout fonctionne

## 🚀 Premier Démarrage

### **Étape 1 : Lancer l'outil**
- **Double-cliquez** sur `start.bat`
- **OU** tapez `python main.py` dans l'invite de commande

### **Étape 2 : Interface**
Une fenêtre s'ouvre avec **5 onglets** :
- 🕷️ **Scraper de Site** : Pour récupérer les liens
- 📅 **Extraction de Dates** : Pour trouver les dates
- 📂 **Organisateur** : Pour classer par année/mois  
- 📊 **Exportation CSV** : Pour créer des fichiers Excel
- 🔍 **Recherche Mots Clés** : Pour chercher des termes

### **Étape 3 : Premier test**
1. **Onglet "Scraper de Site"**
2. **Entrez** : `https://example.com` (site de test)
3. **Cliquez** : "Démarrer le Scraping"
4. **Regardez** : La barre de progression avancer

Si ça marche = **Tout est bon !** 🎉

## ❓ Questions Fréquentes

### **🤔 Python ? C'est quoi ?**
Python est un langage de programmation. L'outil d'installation le télécharge automatiquement pour vous.

### **💻 Ça marche sur quel Windows ?**
- Windows 10 ✅
- Windows 11 ✅  
- Windows 8 ⚠️ (peut-être)
- Windows 7 ❌ (trop ancien)

### **🔒 Mon antivirus bloque l'installation**
Normal ! Les outils automatiques sont parfois détectés. 
**Solution** : Ajoutez le dossier aux exceptions de votre antivirus.

### **📱 Ça marche sur Mac/téléphone ?**
L'outil est fait pour Windows. Pour Mac/Linux, il faut installer Python manuellement.

### **🌐 J'ai besoin d'internet ?**
Oui, pour :
- Télécharger Python (installation)
- Télécharger les modules (installation)  
- Utiliser l'outil (analyser des sites web)

### **💾 Ça prend combien de place ?**
- **Python** : ~100 MB
- **Modules** : ~50 MB
- **L'outil** : ~10 MB
- **Total** : ~160 MB

## 🔧 Si ça ne marche pas...

### **Problème 1 : "Python n'est pas reconnu"**
**Cause** : Python n'est pas dans le PATH Windows
**Solution** :
1. Réinstallez Python depuis python.org
2. **Cochez impérativement** "Add Python to PATH"
3. Redémarrez votre PC

### **Problème 2 : "Impossible de télécharger"**
**Cause** : Problème de connexion ou antivirus
**Solutions** :
1. Vérifiez votre connexion internet
2. Désactivez temporairement l'antivirus
3. Essayez depuis un autre réseau

### **Problème 3 : "Erreur SSL Certificate"**
**Cause** : Problème de certificats de sécurité
**Solution** :
```
pip install --upgrade certifi requests urllib3
```

### **Problème 4 : Fenêtre qui se ferme tout de suite**
**Cause** : Erreur dans le code Python
**Solution** :
1. Ouvrez l'invite de commande
2. Tapez : `python main.py`
3. Lisez le message d'erreur qui s'affiche

## 🎮 Utilisation Basique

### **Workflow simple en 4 étapes**

**1️⃣ Récupérer les liens**
- Onglet "Scraper de Site"  
- Entrez l'URL du site
- Cliquez "Démarrer"

**2️⃣ Extraire les dates**
- Onglet "Extraction de Dates"
- Sélectionnez le fichier créé à l'étape 1
- Cliquez "Démarrer"

**3️⃣ Organiser par date**
- Onglet "Organisateur" 
- Sélectionnez le fichier CSV de l'étape 2
- Cliquez "Démarrer"

**4️⃣ Exporter vers Excel**
- Onglet "Exportation CSV"
- Choisissez vos options
- Cliquez "Démarrer"

### **Paramètres recommandés pour débuter**
- **Limite d'URLs** : 100 (pour tester)
- **Nombre de threads** : 5 (pour ne pas surcharger)
- **Mode export** : "Export direct" (plus simple)

## 🔄 Mise à Jour

### **Méthode automatique**
1. **Double-cliquez** sur `update.bat`
2. **Choisissez** votre branche si demandé
3. **Attendez** que la mise à jour se fasse

### **Méthode manuelle**
Si vous avez téléchargé une nouvelle version :
1. **Remplacez** les fichiers Python
2. **Gardez** le dossier `venv/` et `data/`
3. **Relancez** `install.bat` si nécessaire

## 💡 Conseils pour Bien Commencer

### **🎯 Premiers tests**
1. **Commencez petit** : 50-100 URLs maximum
2. **Testez** sur des sites simples (blogs, sites d'actualités)
3. **Vérifiez** que vous avez des résultats avant de faire plus gros

### **⚡ Optimiser les performances**
- **PC lent** : Réduisez le nombre de threads (3-5)
- **PC rapide** : Augmentez le nombre de threads (10-15)
- **Gros sites** : Activez la limite d'URLs pour tester

### **🛡️ Respecter les sites**
- **Pas trop vite** : Laissez les délais par défaut
- **Pas trop gros** : Évitez de scraper 100,000 pages d'un coup
- **Vérifiez robots.txt** : L'outil le fait automatiquement

### **💾 Sauvegarder ses données**
- Le dossier `data/` contient tout votre travail
- **Sauvegardez-le** régulièrement
- Vous pouvez le copier sur une clé USB

## 🆘 Aide d'Urgence

### **🚨 Ça ne fonctionne vraiment pas ?**

**Diagnostic rapide** :
1. Votre Windows est-il à jour ?
2. Avez-vous les droits administrateur ?
3. Votre antivirus bloque-t-il quelque chose ?
4. Avez-vous une connexion internet stable ?

**Solutions d'urgence** :
1. **Redémarrez** votre PC
2. **Désactivez temporairement** l'antivirus
3. **Téléchargez Python** manuellement depuis python.org
4. **Lancez l'invite de commande en administrateur**

### **📞 Obtenir de l'aide**
- Lisez bien les messages d'erreur
- Notez le message exact qui s'affiche
- Vérifiez que votre PC répond aux prérequis

---

## 🎉 Félicitations !

**Si vous êtes arrivé jusqu'ici, vous êtes prêt !**

➡️ **Prochaine étape** : Lisez le README.md pour comprendre comment utiliser l'outil

➡️ **Premier projet** : Analysez un petit site pour vous familiariser

**Bonne analyse de données ! 🚀**