# 🚀 Guide de Démarrage Rapide - Vie Quotidienne

Guide rapide pour tester l'application en 5 minutes.

## Option 1 : Démonstration Sans Installation (Recommandé pour tester)

### Essayer immédiatement sans installer PostgreSQL ou LLM :

```bash
# Cloner le dépôt
git clone https://github.com/Beunoit01/MinecraftRag.git
cd MinecraftRag

# Lancer la démo
python demo_vie_quotidienne.py
```

**✅ C'est tout !** La démo vous montrera toutes les fonctionnalités sans nécessiter d'installation.

## Option 2 : Installation Complète (Pour utiliser l'application)

### Étape 1 : Installer PostgreSQL (5 minutes)

#### Sur Ubuntu/Debian :
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb vie_quotidienne
```

#### Sur macOS :
```bash
brew install postgresql
brew services start postgresql
createdb vie_quotidienne
```

#### Sur Windows :
Téléchargez depuis [postgresql.org](https://www.postgresql.org/download/windows/) et suivez l'installateur.

### Étape 2 : Installer les dépendances Python (2 minutes)

```bash
# Optionnel : créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# Installer les dépendances
pip install psycopg2-binary llama-cpp-python
```

### Étape 3 : Télécharger un modèle LLM français (10 minutes)

**Recommandation : Mistral-7B-Instruct (meilleur rapport qualité/compatibilité)**

1. Visitez : https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
2. Cliquez sur "Files and versions"
3. Téléchargez : `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (~4 GB)
4. Placez-le dans un dossier `models/` :

```bash
mkdir models
mv ~/Downloads/mistral-7b-instruct-v0.2.Q4_K_M.gguf models/
```

**Alternative : Modèles plus petits (2-3 GB)**
- Vigogne-2-7B : https://huggingface.co/bofenghuang/vigogne-2-7b-instruct
- Pour CPU uniquement, privilégiez les versions Q4_K_M

### Étape 4 : Configurer l'application (1 minute)

Créez un fichier `.env` :

```bash
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vie_quotidienne
DB_USER=postgres
DB_PASSWORD=postgres
LLM_MODEL_PATH=./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
EOF
```

Ou modifiez directement les valeurs dans `app_vie_quotidienne.py` (lignes 488-497).

### Étape 5 : Ajouter des données d'exemple (30 secondes)

```bash
python examples_vie_quotidienne.py
```

Cela créera :
- ✅ 3 recettes (crêpes, quiche, ratatouille)
- ✅ 4 astuces ménagères

### Étape 6 : Lancer l'application ! 🎉

```bash
python app_vie_quotidienne.py
```

## 💬 Exemples de Commandes

Une fois l'application lancée, essayez :

```
💬 Votre demande : Donne-moi une recette de crêpes
💬 Votre demande : Trouve des astuces de nettoyage
💬 Votre demande : aide
```

Pour ajouter une recette :
```
💬 Votre demande : Ajoute une recette de gâteau au chocolat
```
L'application vous guidera étape par étape.

Pour supprimer :
```
💬 Votre demande : Supprime la recette numéro 5
```
(Une confirmation sera demandée)

Pour quitter :
```
💬 Votre demande : quitter
```

## 🐛 Problèmes Courants

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Impossible de se connecter à PostgreSQL"
```bash
# Vérifier que PostgreSQL fonctionne
sudo systemctl status postgresql

# Démarrer si nécessaire
sudo systemctl start postgresql

# Créer la base si elle n'existe pas
sudo -u postgres createdb vie_quotidienne
```

### "Le modèle LLM n'a pas été trouvé"
1. Vérifiez le chemin dans `.env` ou `app_vie_quotidienne.py`
2. Téléchargez un modèle depuis HuggingFace (voir Étape 3)
3. Ou lancez en mode démonstration (l'app propose cette option)

### PostgreSQL refuse la connexion
Modifiez les identifiants dans `.env` :
```bash
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
```

## 📊 Vérification de l'Installation

Pour vérifier que tout fonctionne :

```bash
# Test 1 : Modules Python
python test_database.py

# Test 2 : Démo sans dépendances
python demo_vie_quotidienne.py

# Test 3 : Connexion PostgreSQL (nécessite PostgreSQL)
python -c "from database import init_database; db = init_database(); print('✅ PostgreSQL OK')"
```

## 📖 Documentation Complète

Pour plus de détails, consultez :
- **README_VIE_QUOTIDIENNE.md** : Documentation complète
- **IMPLEMENTATION_SUMMARY.md** : Détails techniques
- **demo_vie_quotidienne.py** : Démo interactive

## 🎯 Récapitulatif

| Temps | Action | Requis |
|-------|--------|--------|
| 0 min | Démo sans installation | ✅ Oui (pour tester) |
| 5 min | Installer PostgreSQL | ⚠️ Pour usage réel |
| 2 min | Installer dépendances Python | ⚠️ Pour usage réel |
| 10 min | Télécharger modèle LLM | ⚠️ Pour usage réel |
| 1 min | Configuration | ⚠️ Pour usage réel |
| 30 sec | Données d'exemple | ⚠️ Pour usage réel |
| **Total** | **~18 minutes** | **Pour installation complète** |

## 🚀 Prêt à Commencer ?

### Pour tester rapidement (maintenant) :
```bash
python demo_vie_quotidienne.py
```

### Pour l'installation complète (18 minutes) :
Suivez les étapes 1 à 6 ci-dessus.

---

**Besoin d'aide ?** Ouvrez une issue sur GitHub ou consultez la documentation complète.

**Bon appétit et bon ménage ! 🍽️💡**
