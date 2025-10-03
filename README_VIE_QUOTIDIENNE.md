# 🏠 Application Vie Quotidienne - RAG System en Français

Application intelligente de gestion de la vie quotidienne en français, utilisant PostgreSQL et un LLM local pour interpréter les demandes en langage naturel.

## 📋 Fonctionnalités

- **🍽️ Gestion de recettes** : Ajout, recherche et suppression de recettes de cuisine
- **💡 Astuces ménagères** : Organisation, nettoyage, économies
- **📅 Routines quotidiennes** : Gestion des habitudes et routines
- **💬 Interface en français naturel** : Interaction conversationnelle avec l'assistant
- **🤖 LLM local** : Interprétation des intentions utilisateur avec un modèle français
- **🗄️ Base PostgreSQL** : Stockage structuré et performant

## 🚀 Installation

### Prérequis

1. **Python 3.8+**
2. **PostgreSQL 12+**
3. **Un modèle LLM français en format GGUF** (voir section Modèles recommandés)

### Étapes d'installation

#### 1. Installer PostgreSQL

**Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS :**
```bash
brew install postgresql
brew services start postgresql
```

**Windows :**
Téléchargez l'installateur depuis [postgresql.org](https://www.postgresql.org/download/windows/)

#### 2. Créer la base de données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE vie_quotidienne;

# Créer un utilisateur (optionnel)
CREATE USER mon_user WITH PASSWORD 'mon_password';
GRANT ALL PRIVILEGES ON DATABASE vie_quotidienne TO mon_user;

# Quitter
\q
```

Ou avec la commande directe :
```bash
sudo -u postgres createdb vie_quotidienne
```

#### 3. Installer les dépendances Python

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install psycopg2-binary llama-cpp-python
```

#### 4. Télécharger un modèle LLM français

Voir la section **Modèles LLM recommandés** ci-dessous.

## 🤖 Modèles LLM recommandés

### Option 1 : Vigogne (Recommandé pour le français)
- **Nom** : Vigogne-2-7B-Instruct
- **Description** : Modèle français basé sur Llama 2, optimisé pour le français
- **URL** : https://huggingface.co/bofenghuang/vigogne-2-7b-instruct
- **Fichier GGUF** : `vigogne-2-7b-instruct.Q4_K_M.gguf`
- **Taille** : ~4 GB

### Option 2 : Mistral (Excellent multilingue)
- **Nom** : Mistral-7B-Instruct-v0.2
- **Description** : Excellent modèle multilingue avec bon support du français
- **URL** : https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- **Fichier GGUF** : `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- **Taille** : ~4 GB

### Option 3 : CroissantLLM
- **Nom** : CroissantLLM
- **Description** : Modèle français natif développé par des chercheurs français
- **URL** : https://huggingface.co/croissantllm/CroissantLLMBase
- **Taille** : ~3.5 GB

### Comment télécharger un modèle GGUF

1. Visitez le lien HuggingFace du modèle choisi
2. Allez dans l'onglet **Files and versions**
3. Téléchargez le fichier `.gguf` (format `Q4_K_M` recommandé pour le meilleur ratio qualité/taille)
4. Placez le fichier dans un dossier `models/` à la racine du projet :

```bash
mkdir models
# Déplacez votre fichier .gguf téléchargé dans ce dossier
mv ~/Downloads/mistral-7b-instruct-v0.2.Q4_K_M.gguf models/
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Configuration PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vie_quotidienne
DB_USER=postgres
DB_PASSWORD=postgres

# Chemin du modèle LLM
LLM_MODEL_PATH=./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

Ou modifiez directement les valeurs dans `app_vie_quotidienne.py`.

## 📚 Utilisation

### 1. Initialiser la base de données avec des exemples

```bash
python examples_vie_quotidienne.py
```

Cela créera les tables et ajoutera des données d'exemple (recettes et astuces).

### 2. Lancer l'application

```bash
python app_vie_quotidienne.py
```

### 3. Exemples d'utilisation

#### Rechercher une recette
```
💬 Votre demande : Donne-moi une recette de crêpes
```

#### Ajouter une recette
```
💬 Votre demande : Ajoute une recette de gâteau au chocolat
```
L'application vous guidera pour saisir les détails.

#### Rechercher des astuces
```
💬 Votre demande : Trouve des astuces de nettoyage
```

#### Supprimer une entrée
```
💬 Votre demande : Supprime la recette numéro 5
```
Une confirmation sera demandée pour la sécurité.

#### Obtenir de l'aide
```
💬 Votre demande : aide
```

#### Quitter
```
💬 Votre demande : quitter
```

## 🏗️ Architecture

### Structure du projet

```
MinecraftRag/
├── database.py                 # Gestion PostgreSQL
├── llm_french.py              # Intégration LLM français
├── app_vie_quotidienne.py     # Application principale
├── examples_vie_quotidienne.py # Données d'exemple
├── README_VIE_QUOTIDIENNE.md  # Documentation
└── models/                    # Modèles LLM (à créer)
    └── *.gguf
```

### Schéma de base de données

#### Table `recettes`
- `id` : Identifiant unique
- `titre` : Nom de la recette
- `description` : Description courte
- `ingredients` : Liste des ingrédients
- `instructions` : Étapes de préparation
- `temps_preparation` : Temps de préparation (minutes)
- `temps_cuisson` : Temps de cuisson (minutes)
- `nombre_portions` : Nombre de portions
- `difficulte` : Niveau de difficulté (facile/moyen/difficile)
- `categorie` : Type de plat (entrée/plat/dessert)
- `date_creation` : Date de création
- `date_modification` : Date de dernière modification

#### Table `astuces_menageres`
- `id` : Identifiant unique
- `titre` : Titre de l'astuce
- `description` : Description détaillée
- `categorie` : Catégorie (nettoyage/organisation/économie)
- `materiel_necessaire` : Liste du matériel
- `etapes` : Étapes à suivre
- `conseils` : Conseils supplémentaires
- `date_creation` : Date de création
- `date_modification` : Date de dernière modification

#### Table `routines`
- `id` : Identifiant unique
- `titre` : Nom de la routine
- `description` : Description
- `type_routine` : Type (matinale/soirée/hebdomadaire)
- `duree_estimee` : Durée estimée (minutes)
- `etapes` : Étapes de la routine
- `conseils` : Conseils
- `date_creation` : Date de création
- `date_modification` : Date de dernière modification

#### Table `conseils`
- `id` : Identifiant unique
- `titre` : Titre du conseil
- `contenu` : Contenu détaillé
- `categorie` : Catégorie (santé/bien-être/productivité)
- `tags` : Mots-clés
- `date_creation` : Date de création
- `date_modification` : Date de dernière modification

## 🔄 Flux de travail

1. **Utilisateur** : Saisit une demande en français naturel
2. **LLM** : Analyse la demande et identifie l'intention (ajouter/rechercher/supprimer) et le type de contenu
3. **Application** : Exécute l'action appropriée sur la base de données PostgreSQL
4. **Résultat** : Affiche les résultats formatés en français

## 🛠️ Fonctions principales

### `database.py`
- `DatabaseManager` : Gestion de la connexion PostgreSQL
- `create_tables()` : Création des tables
- `add_recette()` : Ajout d'une recette
- `search_recettes()` : Recherche de recettes
- `delete_recette()` : Suppression d'une recette
- `add_astuce_menagere()` : Ajout d'une astuce
- `search_astuces()` : Recherche d'astuces
- `delete_astuce()` : Suppression d'une astuce

### `llm_french.py`
- `FrenchLLMManager` : Gestionnaire du LLM
- `classify_intent()` : Classification de l'intention utilisateur
- `extract_recipe_details()` : Extraction des détails d'une recette
- `format_search_results()` : Formatage des résultats
- `generate_response()` : Génération de réponses en français

### `app_vie_quotidienne.py`
- `VieQuotidienneApp` : Application principale
- `handle_search()` : Gestion des recherches
- `handle_add()` : Gestion des ajouts
- `handle_delete()` : Gestion des suppressions (avec confirmation)
- `run()` : Boucle principale

## 🔒 Sécurité

- **Suppression avec confirmation** : Pour supprimer une entrée, l'utilisateur doit taper exactement "SUPPRIMER"
- **Validation des entrées** : Les IDs sont validés avant les opérations
- **Gestion des erreurs** : Toutes les opérations de base de données sont protégées par try/except

## 🐛 Dépannage

### Erreur de connexion PostgreSQL

**Problème** : `Impossible de se connecter à PostgreSQL`

**Solutions** :
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Démarrer PostgreSQL si nécessaire
sudo systemctl start postgresql

# Vérifier que la base existe
sudo -u postgres psql -l | grep vie_quotidienne

# Créer la base si elle n'existe pas
sudo -u postgres createdb vie_quotidienne
```

### Modèle LLM non trouvé

**Problème** : `Le modèle LLM n'a pas été trouvé`

**Solution** :
1. Téléchargez un modèle GGUF (voir section Modèles recommandés)
2. Placez-le dans le dossier `models/`
3. Mettez à jour le chemin dans `.env` ou `app_vie_quotidienne.py`

### Erreur d'importation psycopg2

**Problème** : `ModuleNotFoundError: No module named 'psycopg2'`

**Solution** :
```bash
pip install psycopg2-binary
```

### Mode démonstration

Si le modèle LLM n'est pas disponible, l'application peut fonctionner en mode démonstration avec une classification d'intention basique par mots-clés.

## 📈 Améliorations futures

- [ ] Support des routines quotidiennes (déjà préparé dans la base)
- [ ] Support des conseils généraux
- [ ] Recherche sémantique avec embeddings
- [ ] Export des recettes en PDF
- [ ] API REST pour intégration externe
- [ ] Interface web avec Flask/FastAPI
- [ ] Catégorisation automatique par le LLM
- [ ] Suggestions de recettes basées sur les ingrédients disponibles
- [ ] Planification de menus hebdomadaires

## 📝 Licence

Ce projet est fourni comme exemple éducatif. Utilisez-le librement.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Support

Pour toute question ou problème, créez une issue sur GitHub.

---

**Bon appétit et bon ménage ! 🍽️💡**
