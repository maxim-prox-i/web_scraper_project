# 🎯 Installation ULTRA Simple - Web Scraper Suite

> **👥 Pour qui ?** Débutants complets, personnes qui n'ont JAMAIS utilisé de code !

## 🚨 AVANT DE COMMENCER - IMPORTANT !

**⚠️ Vous allez installer :**
- Git (pour télécharger le projet)
- Python (le langage de programmation)
- L'outil Web Scraper Suite

**💾 Espace requis :** Environ 500 MB sur votre disque dur

**⏱️ Temps requis :** 15-20 minutes maximum

**🌐 Connexion internet :** Obligatoire pendant toute l'installation

---

## 📋 ÉTAPE 1 : Ouvrir l'invite de commande

### **1.1 - Appuyez sur les touches Win + R**
- Sur votre clavier, appuyez **en même temps** sur la touche `Windows` (logo Windows) + la touche `R`
- Une petite fenêtre va s'ouvrir en bas à gauche

```
┌─ Exécuter ───────────────────────┐
│                                  │
│ Ouvrir: [_____________________]  │
│                                  │
│    [OK]  [Annuler]  [Parcourir]  │
└──────────────────────────────────┘
```

### **1.2 - Tapez "cmd"**
- Dans la case qui clignote, tapez exactement : `cmd`
- Appuyez sur `Entrée` ou cliquez sur `OK`

### **1.3 - L'invite de commande s'ouvre**
Une fenêtre noire va s'ouvrir avec du texte blanc qui ressemble à ça :
```
Microsoft Windows [Version 10.0.19041.1234]
(c) Microsoft Corporation. Tous droits réservés.

C:\Users\VotreNom>_
```

**👀 C'est normal si ça fait peur ! Ne fermez PAS cette fenêtre.**

---

## 📂 ÉTAPE 2 : Aller dans le dossier Documents

### **2.1 - Copiez cette commande exactement**
```
cd %USERPROFILE%\Documents
```

### **2.2 - Collez dans l'invite de commande**
- **Clic droit** dans la fenêtre noire → **Coller**
- OU appuyez sur `Ctrl + V`
- Appuyez sur `Entrée`

### **2.3 - Vérifiez que vous êtes dans Documents**
Vous devriez voir quelque chose comme :
```
C:\Users\VotreNom\Documents>_
```

**✅ Parfait ! Vous êtes dans le bon dossier.**

---

## 🔽 ÉTAPE 3 : Télécharger le projet

### **3.1 - Choix A : Avec Git (Plus Simple pour les mises à jour)**

**Copiez et collez cette commande :**
```
git clone https://github.com/maxim-prox-i/web_scraper_project.git
```

**Si vous voyez une erreur comme "git n'est pas reconnu" :**
→ Passez au **Choix B** ci-dessous

**Si ça marche :**
- Vous verrez du texte défiler
- Une fois terminé, tapez : `cd web_scraper_project`
- Appuyez sur `Entrée`
- **→ Passez directement à l'ÉTAPE 4**

### **3.2 - Choix B : Sans Git (Téléchargement manuel)**

**Si le Choix A n'a pas marché :**

1. **Ouvrez votre navigateur internet** (Chrome, Firefox, Edge...)

2. **Allez sur cette adresse :**
   ```
   https://github.com/maxim-prox-i/web_scraper_project
   ```

3. **Cliquez sur le bouton vert "< > Code"**
   - C'est un gros bouton vert en haut à droite

4. **Cliquez sur "Download ZIP"**
   - En bas du menu qui s'ouvre

5. **Téléchargez le fichier**
   - Il va dans votre dossier Téléchargements
   - Le fichier s'appelle `web_scraper_project-main.zip`

6. **Décompressez le fichier :**
   - **Clic droit** sur le fichier ZIP → **"Extraire tout..."**
   - Changez le dossier de destination vers : `C:\Users\VotreNom\Documents\`
   - Cliquez sur **"Extraire"**

7. **Renommez le dossier :**
   - Le dossier créé s'appelle `web_scraper_project-main`
   - **Clic droit** → **"Renommer"**
   - Changez en : `web_scraper_project`

8. **Retournez dans l'invite de commande**
   - Tapez : `cd web_scraper_project`
   - Appuyez sur `Entrée`

---

## ⚙️ ÉTAPE 4 : Installation automatique

### **4.1 - Lancez l'installation**
**Tapez exactement :**
```
install.bat
```
**Appuyez sur `Entrée`**

### **4.2 - Suivez les instructions à l'écran**

**Le script va vous poser des questions. Voici quoi répondre :**

#### **Question possible 1 :**
```
Voulez-vous redemarrer maintenant? (O/N)
```
**→ Tapez `O` et appuyez sur `Entrée`**

**Votre PC va redémarrer. Après le redémarrage :**
1. Refaites l'ÉTAPE 1 et 2
2. Tapez : `cd web_scraper_project`
3. Tapez : `install.bat`

#### **Question possible 2 :**
```
Voulez-vous continuer sans Git? (O/N)
```
**→ Tapez `O` et appuyez sur `Entrée`**

#### **Question possible 3 :**
```
Voulez-vous lancer l'application maintenant? (O/N)
```
**→ Tapez `O` et appuyez sur `Entrée`**

### **4.3 - Que va-t-il se passer ?**

**Vous allez voir défiler :**

```
[ETAPE 1/6] Verification de Git...
[SUCCES] Git detecte

[ETAPE 2/6] Verification de Python...
[INFO] Installation Python via Windows Package Manager...
[SUCCES] Python installe

[ETAPE 3/6] Verification de pip...
[SUCCES] pip detecte

[ETAPE 4/6] Configuration de l'environnement virtuel...
[SUCCES] Environnement virtuel cree

[ETAPE 5/6] Installation des modules Python...
[SUCCES] Toutes les dependances installees

[ETAPE 6/6] Creation des scripts de demarrage...
[SUCCES] Script start.bat cree

=====================================================
             INSTALLATION TERMINEE !
=====================================================
```

**🎉 Si vous voyez ça, c'est gagné !**

---

## ✅ ÉTAPE 5 : Test de l'installation

### **5.1 - Test automatique**
**Dans l'invite de commande, tapez :**
```
test.bat
```

**Vous devriez voir :**
```
[EXCELLENT] Tous les tests sont passes ! (7/7)
[INFO] Votre installation est parfaitement fonctionnelle
```

### **5.2 - Premier lancement**
**Tapez :**
```
start.bat
```

**→ Une fenêtre avec des onglets doit s'ouvrir !**

---

## 🎮 ÉTAPE 6 : Premier test

### **6.1 - Interface utilisateur**
Vous devriez voir une fenêtre avec ces onglets :
```
[🕷️ Scraper de Site] [📅 Extraction de Dates] [📂 Organisateur] [📊 Exportation CSV] [🔍 Recherche Mots Clés]
```

### **6.2 - Premier test simple**

1. **Restez sur l'onglet "🕷️ Scraper de Site"**

2. **Dans le champ "URL du site à scraper" :**
   - Tapez : `https://example.com`

3. **Dans le champ "Nombre max d'URLs" :**
   - Tapez : `5`

4. **Cliquez sur le gros bouton "▶️ Démarrer le Scraping"**

5. **Vous devriez voir :**
   - Une barre de progression qui avance
   - Du texte qui défile dans la zone du bas

**🎉 Si ça marche, FÉLICITATIONS ! L'installation est réussie !**

---

## 🚨 PROBLÈMES COURANTS

### **❌ "git n'est pas reconnu"**
**→ PAS DE PANIQUE ! Utilisez le Choix B de l'ÉTAPE 3**

### **❌ "python n'est pas reconnu"**
**Solution :**
1. Fermez l'invite de commande
2. **Redémarrez votre PC**
3. Recommencez depuis l'ÉTAPE 1

### **❌ "L'installation a échoué"**
**Solution :**
1. **Désactivez temporairement votre antivirus**
2. Recommencez depuis l'ÉTAPE 4
3. **Réactivez votre antivirus après**

### **❌ "Une fenêtre noire s'ouvre et se ferme"**
**Solution :**
1. Dans l'invite de commande, tapez : `python main.py`
2. Lisez le message d'erreur qui s'affiche
3. Tapez : `install.bat` pour réparer

### **❌ "Rien ne se passe quand je clique sur start.bat"**
**Solution :**
1. **Clic droit** sur `start.bat`
2. **"Exécuter en tant qu'administrateur"**
3. Si Windows demande, cliquez **"Oui"**

---

## 🔄 POUR LES FOIS SUIVANTES

### **Comment relancer l'application ?**

**Méthode 1 : Double-clic**
- Dans votre dossier `Documents\web_scraper_project`
- **Double-cliquez** sur `start.bat`

**Méthode 2 : Invite de commande**
1. Ouvrez l'invite de commande (`Win + R`, `cmd`)
2. Tapez : `cd %USERPROFILE%\Documents\web_scraper_project`
3. Tapez : `start.bat`

### **Comment mettre à jour ?**
**Si vous avez utilisé Git (Choix A) :**
1. Ouvrez l'invite de commande dans le dossier du projet
2. Tapez : `update.bat`

**Si vous avez téléchargé le ZIP (Choix B) :**
1. Retéléchargez le nouveau ZIP depuis GitHub
2. Sauvegardez votre dossier `data/` s'il contient vos données
3. Remplacez tous les fichiers sauf le dossier `data/`

---

## 📞 AIDE D'URGENCE

### **🆘 Ça ne marche vraiment pas ?**

**Vérifications de base :**
1. **Avez-vous une connexion internet ?**
2. **Votre Windows est-il à jour ?**
3. **Avez-vous redémarré après l'installation ?**
4. **Votre antivirus bloque-t-il quelque chose ?**

**Réparation totale :**
```cmd
rmdir /s /q venv
install.bat
```

**Information système :**
- Notez votre version de Windows : `Win + R`, tapez `winver`
- Notez le message d'erreur exact (copier-coller)

---

## ✨ Workflow Simple une fois installé

```
1. Double-cliquez sur start.bat
   ↓
2. Onglet "Scraper" → Entrez une URL → Démarrer
   ↓
3. Onglet "Dates" → Sélectionnez le fichier créé → Démarrer
   ↓
4. Onglet "Organisateur" → Sélectionnez le CSV → Démarrer
   ↓
5. Onglet "Export" → Choisissez vos options → Démarrer
   ↓
6. Récupérez votre fichier Excel dans le dossier data/
```

**🎉 FÉLICITATIONS ! VOUS ÊTES MAINTENANT PRÊT À UTILISER L'OUTIL !**

---

*Guide créé pour les débutants complets. N'hésitez pas à prendre votre temps et à recommencer si nécessaire.*