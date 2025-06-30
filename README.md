# 🕷️ Web Scraper Suite

- [Guide Installation](INSTALL.md)

**L'outil tout-en-un pour récupérer et organiser automatiquement les données de sites web !**

> 🎯 **Idéal pour** : Journalistes, chercheurs, analystes, étudiants, entrepreneurs, ou toute personne qui veut récupérer facilement des informations sur internet.

## 🎮 Comment ça marche ?

### **Interface simple en 4 étapes**

```
1️⃣ SCRAPER          2️⃣ DATES           3️⃣ ORGANISATION    4️⃣ EXPORT
   📥                   📅                  📂                 📊
Récupérer          Extraire            Classer            Exporter
les liens          les dates           par année          vers Excel
```

### **Exemple concret : Analyser un blog**

1. **Je rentre l'adresse** : `https://blog.exemple.com`
2. **L'outil récupère** : 2,847 articles automatiquement
3. **Il extrait les dates** : 1,923 articles avec dates trouvées
4. **Il organise tout** : Par années (2018→2024) et par mois
5. **J'exporte** : Un beau fichier Excel prêt pour l'analyse

⏱️ **Temps total** : 15 minutes au lieu de plusieurs semaines !

## 🛠️ Installation Super Simple

### **Option 1 : Installation Automatique (Recommandée)**
1. 📥 Téléchargez les fichiers du projet
2. 🖱️ Double-cliquez sur `install.bat`
3. ☕ Attendez que tout s'installe automatiquement
4. ✅ C'est prêt !

### **Option 2 : Si vous avez déjà Python**
```
1. Ouvrez l'invite de commande
2. Tapez : pip install requests beautifulsoup4 lxml tqdm
3. Lancez : python main.py
```

> 💡 **Aucune expertise technique requise** - Les scripts d'installation font tout pour vous !

## 🚀 Guide de Démarrage

### **Premier lancement**
1. Double-cliquez sur `start.bat` (créé automatiquement)
2. Une fenêtre s'ouvre avec des onglets simples
3. Suivez les étapes dans l'ordre !

### **Onglet 1 : Scraper de Site** 🕷️
- **URL du site** : Collez l'adresse du site (ex: https://lemonde.fr)
- **Limite** : Combien de pages maximum ? (laissez vide = tout)
- **Cliquez** : "Démarrer le Scraping"

**Résultat** : Un fichier `urls.txt` avec tous les liens trouvés

### **Onglet 2 : Extraction de Dates** 📅
- **Fichier d'entrée** : Sélectionnez le fichier `urls.txt` créé avant
- **Nombre de processus** : 10 par défaut (plus = plus rapide)
- **Cliquez** : "Démarrer l'Extraction"

**Résultat** : Un fichier CSV avec les liens + leurs dates

### **Onglet 3 : Organisation** 📂
- **Fichier CSV** : Sélectionnez le fichier CSV créé avant
- **Nom du dossier** : Donnez un nom à votre projet
- **Cliquez** : "Démarrer l'Organisation"

**Résultat** : Dossiers organisés par année et mois

### **Onglet 4 : Export CSV** 📊
- **Mode** : Choisissez "Export direct" ou "Depuis structure"
- **Format** : Un fichier Excel ou plusieurs
- **Cliquez** : "Démarrer l'Exportation"

**Résultat** : Fichier Excel prêt pour vos analyses !

## 📊 Résultats Typiques

### **Ce que vous obtenez**
```
📁 Votre Projet/
  📁 2024/
    📁 01_Janvier/
      📄 2024-01.urls.txt (243 liens)
    📁 02_Février/
      📄 2024-02.urls.txt (189 liens)
  📁 2023/
    📁 12_Décembre/
      📄 2023-12.urls.txt (156 liens)
  📄 export_final.csv (fichier Excel)
```

### **Performance**
- ⚡ **5,000 pages** analysées en 10 minutes
- 📅 **80% de taux** de réussite pour les dates
- 📊 **Export Excel** en quelques secondes

## 🎯 Cas d'Usage Détaillés

### **📰 Journalisme & Média**
```
Objectif : Analyser 3 ans d'articles sur un sujet
Étapes :
1. Scraper le site du journal
2. Rechercher mot-clé "climat" dans tous les articles
3. Organiser par mois pour voir les tendances
4. Exporter pour faire des graphiques

Résultat : Évolution du traitement médiatique dans le temps
```

### **🎓 Recherche Académique**
```
Objectif : Constituer un corpus de thèse
Étapes :
1. Scraper plusieurs sites scientifiques
2. Extraire les dates de publication
3. Filtrer par période d'étude (ex: 2020-2024)
4. Organiser par année pour analyse temporelle

Résultat : Base de données structurée pour la recherche
```

### **💼 Business Intelligence**
```
Objectif : Surveiller la concurrence
Étapes :
1. Scraper les sites des concurrents
2. Rechercher mots-clés liés aux produits
3. Organiser par mois les communiqués
4. Analyser les tendances et annonces

Résultat : Veille concurrentielle automatisée
```

## 🔧 Options Avancées (Optionnel)

### **Paramètres de Performance**
- **Threads** : Plus = plus rapide (attention à ne pas surcharger les sites)
- **Délais** : Temps d'attente entre les requêtes (respect des sites)
- **Limites** : Nombre maximum de pages à traiter

### **Formats de Date Supportés**
- Français : 15 janvier 2024, 15/01/2024
- Anglais : January 15, 2024, 01/15/2024
- ISO : 2024-01-15
- Dans les URLs : /2024/01/15/

### **Recherche de Mots-clés**
- Expressions exactes : `"intelligence artificielle"`
- Mots séparés : `intelligence, artificielle, IA`
- Respect de la casse : optionnel

## ❓ Questions Fréquentes

### **🤔 C'est légal ?**
Oui ! L'outil respecte les règles :
- Lit le fichier `robots.txt` des sites
- Ajoute des délais entre les requêtes
- Ne surcharge pas les serveurs

### **💻 Ça marche sur Mac/Linux ?**
L'outil est développé pour Windows mais fonctionne sur tous les systèmes avec Python.

### **🔒 Mes données sont-elles sécurisées ?**
Tout reste sur votre ordinateur ! Rien n'est envoyé sur internet.

### **⚡ C'est vraiment gratuit ?**
Oui, complètement gratuit et open-source.

### **📞 J'ai un problème, qui peut m'aider ?**
- Lisez le guide INSTALL.md
- Utilisez le script `test_install.py` pour diagnostiquer
- Vérifiez que Python est bien installé

## 🎁 Bonus : Scripts Prêts à l'Emploi

### **Mise à jour automatique**
```cmd
update.bat  # Met à jour l'outil avec les dernières améliorations
```

### **Test de fonctionnement**
```cmd
test_install.py  # Vérifie que tout fonctionne correctement
```

### **Démarrage rapide**
```cmd
start.bat  # Lance l'interface directement
```

## 🌟 Prochaines Améliorations

- 🎨 Interface encore plus simple
- 📱 Version web (dans le navigateur)
- 🤖 Intelligence artificielle pour analyser le contenu
- 📈 Graphiques automatiques
- 🌍 Support multilingue complet

---

## 💡 **Vous êtes prêt à économiser des heures de travail ?**

1. 📥 **Téléchargez** les fichiers
2. 🖱️ **Double-cliquez** sur `install.bat`  
3. 🚀 **Lancez** votre première analyse !

**En 10 minutes, vous serez opérationnel !**

---

*Développé avec ❤️ pour simplifier la vie de tous ceux qui travaillent avec des données web*