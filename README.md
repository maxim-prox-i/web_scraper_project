# 🕷️ Web Scraper - Guide Super Simple

**Récupérez automatiquement des informations de sites web, sans être informaticien !**

## 🤔 À quoi ça sert ?

Imaginez que vous voulez :
- Récupérer tous les articles d'un journal des 2 dernières années
- Avoir la liste de tous les communiqués d'une entreprise
- Analyser ce qui se dit sur un sujet précis

Au lieu de copier-coller manuellement pendant des semaines, cet outil le fait automatiquement en quelques minutes !

---

# 🚀 INSTALLATION EN 4 ÉTAPES SIMPLES

> **⏰ Temps total :** 15 minutes  
> **💾 Espace nécessaire :** Un peu de place sur votre ordinateur  
> **🌐 Internet :** Obligatoire pendant l'installation

## ÉTAPE 1 : Ouvrir la "ligne de commande"

**C'est quoi ?** Une fenêtre noire où on tape des instructions à l'ordinateur.

**Comment faire :**
1. Sur votre clavier, appuyez **en même temps** sur `Windows` + `R`
2. Une petite fenêtre s'ouvre
3. Tapez `cmd` dans la case
4. Appuyez sur `Entrée`

**Résultat :** Une fenêtre noire s'ouvre avec du texte blanc. **Ne la fermez pas !**

---

## ÉTAPE 2 : Aller dans le bon dossier

**Dans la fenêtre noire, copiez-collez cette ligne :**
```
cd %USERPROFILE%\Documents
```

**Comment copier-coller dans la fenêtre noire :**
- Sélectionnez le texte ci-dessus → `Ctrl + C`
- **Clic droit** dans la fenêtre noire → **Coller**
- Appuyez sur `Entrée`

---

## ÉTAPE 3 : Installer Git (l'assistant de téléchargement)
Dans la fenêtre noir taper la commande suivante puis Entrée
**Testez d'abord si vous l'avez déjà :**
```
git --version
```

**Si ça affiche un numéro de version :** Parfait, passez à l'ÉTAPE 4 !

**Si ça affiche une erreur :** Installez Git :
1. Ouvrez votre navigateur internet
2. Allez sur : https://git-scm.com/download/win
3. Téléchargez le fichier qui s'affiche
4. Ouvrez le fichier téléchargé
5. **Cliquez toujours sur "Suivant"** sauf sur cet écran :
   - Quand vous voyez "Adjusting your PATH environment"
   - Choisissez "Git from the command line..."
6. Continuez jusqu'à la fin
7. **Fermez la fenêtre noire et refaites les ÉTAPES 1 et 2**

---

## ÉTAPE 4 : Installer Python (le moteur du programme)
Dans la fenêtre noir taper la commande suivante puis Entrée
**Testez d'abord si vous l'avez déjà :**
```
python --version
```

**Si ça affiche un numéro de version :** Parfait, passez à l'ÉTAPE 5 !

**Si ça affiche une erreur :** Installez Python :
1. Ouvrez votre navigateur internet
2. Allez sur : https://www.python.org/downloads/
3. Cliquez sur le gros bouton jaune "Download Python..."
4. Ouvrez le fichier téléchargé
5. **⚠️ IMPORTANT :** Cochez la case "Add Python to PATH" en bas
6. Cliquez sur "Install Now"
7. Attendez la fin (5-10 minutes)
8. **Fermez la fenêtre noire et refaites les ÉTAPES 1 et 2**

---

## ÉTAPE 5 : Télécharger l'outil Web Scraper

**Dans la fenêtre noire, tapez :**
```
git clone https://github.com/maxim-prox-i/web_scraper_project.git
```

**Ça va télécharger plein de fichiers. C'est normal !**

---

## ÉTAPE 6 : Installation finale automatique

1. **Fermez la fenêtre noire**
2. **Ouvrez l'explorateur de fichiers** (icône dossier dans la barre des tâches)
3. **Allez dans Documents**
4. **Ouvrez le dossier "web_scraper_project"**
5. **Double-cliquez sur le fichier "0_install.bat"**

**Une fenêtre va s'ouvrir et installer tout automatiquement. Attendez qu'elle se ferme.**

**✅ Installation terminée !**

---

# 🎯 COMMENT UTILISER L'OUTIL

## Premier démarrage

**Dans le dossier "web_scraper_project", double-cliquez sur "1_start.bat"**

Une interface avec 5 onglets s'ouvre. C'est votre tableau de bord !

---

## Test simple pour commencer

**Suivez exactement ces étapes :**

### 1. Onglet "Scraper"
- Dans "URL du site", tapez : `https://example.com`
- Dans "Limite d'URLs", tapez : `10`
- Cliquez sur "Démarrer le scraping"
- Attendez que ça finisse

### 2. Onglet "Dates"
- Cliquez sur "Parcourir" et choisissez le fichier qui vient d'être créé
- Cliquez sur "Démarrer l'extraction"
- Attendez que ça finisse

### 3. Onglet "Export"
- Laissez "Export direct" sélectionné
- Cliquez sur "Démarrer l'export"

### 4. Voir le résultat
**Un fichier Excel s'ouvre automatiquement avec vos résultats !**

---

# 📁 OÙ TROUVER VOS FICHIERS

Tous vos résultats sont dans :
**Documents → web_scraper_project → data**

Chaque site analysé aura son propre dossier avec :
- La liste des pages trouvées
- Un fichier Excel avec tout organisé
- Les dates de publication

---

# ❌ EN CAS DE PROBLÈME

## L'installation a échoué

**Double-cliquez sur "test.bat"** dans le dossier web_scraper_project.
Ce fichier va vous dire exactement ce qui ne va pas.

**Solutions les plus courantes :**
- Redémarrez votre ordinateur
- Désactivez temporairement votre antivirus
- Vérifiez que vous avez une connexion internet

## L'outil ne démarre pas

1. **Double-cliquez sur "test.bat"** pour voir le problème
2. **Si ça ne marche toujours pas, double-cliquez sur "0_install.bat"** pour réinstaller

## Les résultats sont bizarres

**Conseils pour de meilleurs résultats :**
- Commencez avec de petits nombres (50-100 pages maximum)
- Testez d'abord sur des sites simples comme des blogs
- Évitez les sites comme Amazon ou Facebook (trop protégés)

---

# 🎯 EXEMPLES CONCRETS D'UTILISATION

## Analyser un journal en ligne
1. **URL :** https://lemonde.fr
2. **Limite :** 500 pages
3. **Résultat :** Tous les articles récents avec leurs dates

## Suivre une entreprise
1. **URL :** Site de l'entreprise + section actualités
2. **Limite :** 200 pages
3. **Résultat :** Tous les communiqués organisés par date

## Recherche sur un sujet
1. Faites d'abord le scraping normal
2. Allez dans l'onglet "Recherche"
3. Tapez vos mots-clés (ex: "écologie", "intelligence artificielle")
4. **Résultat :** Seulement les pages qui parlent de votre sujet

---

# 🔄 METTRE À JOUR L'OUTIL

**Double-cliquez sur "2_update.bat"** de temps en temps pour avoir les dernières améliorations.

---

# ✅ AIDE-MÉMOIRE

**Pour utiliser l'outil :**
1. Double-clik sur "1_start.bat"
2. Onglet Scraper → URL + limite → Démarrer
3. Onglet Dates → Choisir fichier → Démarrer  
4. Onglet Export → Démarrer
5. Ouvrir le fichier Excel créé !

**En cas de problème :**
1. Double-clik sur "test.bat"
2. Suivre les instructions affichées

**Pour les mises à jour :**
1. Double-clik sur "2_update.bat"

---

# 🎉 FÉLICITATIONS !

**Vous savez maintenant récupérer automatiquement les informations de n'importe quel site web !**

**Commencez par de petits tests, puis lancez-vous sur de plus gros projets.**

**L'outil va vous faire gagner des heures de travail !**