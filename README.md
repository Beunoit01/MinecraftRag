# 🌍 Climate Fact-Checker RAG System

Un système RAG (Retrieval-Augmented Generation) spécialisé dans la détection de fake news sur le réchauffement climatique, basé sur des sources scientifiques fiables comme l'IPCC et l'Environmental Defense Fund.

## 🎯 Objectif

Ce projet transforme les informations complexes des rapports scientifiques en un outil accessible pour :
- ✅ Vérifier la véracité d'affirmations climatiques
- 📚 Répondre à des questions sur le climat avec des sources fiables
- 🔍 Éduquer sur les faits scientifiques établis

## 🏗️ Architecture

### Pipeline en 5 étapes :

1. **`climate_scraper.py`** - Collecte des sources scientifiques fiables
2. **`chunking.py`** - Segmentation intelligente des textes scientifiques  
3. **`embeddings.py`** - Vectorisation des connaissances
4. **`vectorstore.py`** - Base de données vectorielle ChromaDB
5. **`llm.py`** - Interface de fact-checking avec LLM local

## 🚀 Installation

```bash
# Cloner et installer les dépendances
git clone [repo]
cd ClimateFactChecker
pip install -r requirements.txt

# Télécharger un modèle LLM local (GGUF format)
# Exemple: Phi-3, Mistral, Llama-2...
```

## 📊 Sources de données

- **IPCC AR6** : Rapports du Groupe d'experts intergouvernemental
- **IPCC SR15** : Rapport spécial 1.5°C  
- **Environmental Defense Fund** : Articles scientifiques sur le climat

## 🔧 Utilisation

```bash
# 1. Scraper les sources
python climate_scraper.py

# 2. Découper en chunks
python chunking.py

# 3. Créer les embeddings
python embeddings.py

# 4. Indexer dans ChromaDB
python vectorstore.py

# 5. Lancer le fact-checker
python llm.py
```

### Interface de fact-checking :

```
🌍 SYSTÈME DE DÉTECTION DE FAKE NEWS CLIMATIQUES

Commandes:
- analyze: Le réchauffement climatique a cessé depuis 1998
- question: Quelle est la cause principale du réchauffement climatique?
```

## 📈 Exemples de résultats

**Affirmation** : "Le réchauffement climatique a cessé depuis 1998"
**Verdict** : ❌ **FAUX**
**Confiance** : HAUTE
**Explication** : Les données IPCC montrent une augmentation continue...

## 🎯 Cas d'usage

- **Éducation** : Vérification d'informations pour étudiants/enseignants
- **Journalisme** : Fact-checking d'articles sur le climat
- **Recherche** : Accès rapide aux consensus scientifiques
- **Réseaux sociaux** : Lutte contre la désinformation climatique

## 🛠️ Configuration

Ajustez les paramètres dans `llm.py` :
- `MODEL_PATH` : Chemin vers votre modèle LLM local
- `N_GPU_LAYERS` : Optimisation GPU selon votre matériel
- `NUM_RESULTS_TO_RETRIEVE` : Nombre de sources à consulter

## ⚠️ Limitations

- Basé uniquement sur les sources indexées
- Qualité dépendante du modèle LLM utilisé  
- Nécessite une mise à jour périodique des sources

## 📜 Licence

Projet éducatif - Usage responsable des sources scientifiques