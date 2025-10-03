# 🏗️ Architecture du Système Vie Quotidienne

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                                  │
│                  💬 Interface en Français                            │
│                                                                       │
│  Exemples de commandes:                                              │
│  • "Donne-moi une recette de crêpes"                                │
│  • "Ajoute une recette de gâteau"                                   │
│  • "Supprime la recette numéro 5"                                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    app_vie_quotidienne.py                            │
│                  🎮 Application Principale                           │
│                                                                       │
│  VieQuotidienneApp:                                                  │
│  ├── display_welcome()        → Affiche message de bienvenue        │
│  ├── process_command()        → Traite la commande utilisateur      │
│  ├── handle_search()          → Gère les recherches                 │
│  ├── handle_add()             → Gère les ajouts interactifs         │
│  ├── handle_delete()          → Gère les suppressions sécurisées    │
│  └── run()                    → Boucle principale                   │
└───────────────┬───────────────────────────┬─────────────────────────┘
                │                           │
                │                           │
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│    llm_french.py          │   │       database.py                 │
│  🤖 Gestionnaire LLM      │   │    💾 Gestionnaire PostgreSQL     │
│                           │   │                                   │
│  FrenchLLMManager:        │   │  DatabaseManager:                 │
│  ├── classify_intent()    │   │  ├── create_tables()              │
│  │   ├─ Détecte action   │   │  ├── add_recette()                │
│  │   ├─ Détecte type     │   │  ├── search_recettes()            │
│  │   └─ Extrait détails  │   │  ├── delete_recette()             │
│  │                        │   │  ├── add_astuce_menagere()        │
│  ├── extract_recipe_      │   │  ├── search_astuces()             │
│  │   details()            │   │  └── delete_astuce()              │
│  ├── format_search_       │   │                                   │
│  │   results()            │   │  Connexion Pool (1-20)            │
│  └── generate_response()  │   │  Gestion des erreurs              │
│                           │   │  Transactions SQL                 │
└────────────┬──────────────┘   └───────────────┬──────────────────┘
             │                                   │
             ▼                                   ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│  Modèle LLM Local (.gguf) │   │      PostgreSQL Database         │
│  🧠 Intelligence Artificielle│   │      🗄️ Base de Données          │
│                           │   │                                   │
│  Options recommandées:    │   │  Tables:                          │
│  • Mistral-7B-Instruct    │   │  ├── recettes                     │
│  • Vigogne-2-7B           │   │  │   ├── id (serial)              │
│  • CroissantLLM           │   │  │   ├── titre (varchar)          │
│                           │   │  │   ├── ingredients (text)       │
│  Format: GGUF (Q4_K_M)    │   │  │   ├── instructions (text)      │
│  Taille: 3-4 GB           │   │  │   ├── temps_* (int)            │
│  CPU/GPU support          │   │  │   └── categorie (varchar)      │
│                           │   │  │                                │
│  Analyse en français      │   │  ├── astuces_menageres            │
│  Classification intent    │   │  │   ├── id (serial)              │
│  Extraction infos         │   │  │   ├── titre (varchar)          │
└───────────────────────────┘   │  │   ├── description (text)       │
                                │  │   ├── categorie (varchar)      │
                                │  │   └── etapes (text)            │
                                │  │                                │
                                │  ├── routines (préparée)          │
                                │  └── conseils (préparée)          │
                                └──────────────────────────────────┘
```

## Flux de Données Détaillé

### 1️⃣ Flux de Recherche

```
USER INPUT: "Donne-moi une recette de crêpes"
    │
    ▼
┌─────────────────────────────────────────┐
│ VieQuotidienneApp.process_command()     │
│ Reçoit la commande utilisateur          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ FrenchLLMManager.classify_intent()      │
│ Analyse le texte avec le LLM           │
│                                         │
│ Prompt système: Classification intent  │
│ Prompt utilisateur: Texte à analyser   │
│                                         │
│ Sortie JSON:                            │
│ {                                       │
│   "action": "RECHERCHER",               │
│   "type": "RECETTE",                    │
│   "query": "crêpes",                    │
│   "details": ""                         │
│ }                                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ VieQuotidienneApp.handle_search()       │
│ Dispatch vers la recherche appropriée  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ DatabaseManager.search_recettes()       │
│                                         │
│ SQL:                                    │
│ SELECT * FROM recettes                  │
│ WHERE titre ILIKE '%crêpes%'            │
│    OR ingredients ILIKE '%crêpes%'      │
│ ORDER BY date_creation DESC             │
└─────────────────┬───────────────────────┘
                  │
                  ▼ [Résultats en JSON]
┌─────────────────────────────────────────┐
│ FrenchLLMManager.format_search_results()│
│ Formate les résultats en français      │
│                                         │
│ Sortie formatée:                        │
│ 📋 1 résultat(s) trouvé(s) :            │
│                                         │
│ 🍽️  1. **Crêpes Françaises** (ID: 1)   │
│    Crêpes traditionnelles légères       │
│    ⏱️  Préparation: 15 min, Cuisson: 20│
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ USER OUTPUT                             │
│ Affichage des résultats formatés       │
│ + Option de voir les détails           │
└─────────────────────────────────────────┘
```

### 2️⃣ Flux d'Ajout Interactif

```
USER INPUT: "Ajoute une recette de gâteau au chocolat"
    │
    ▼
┌─────────────────────────────────────────┐
│ classify_intent()                       │
│ → action: "AJOUTER"                     │
│ → type: "RECETTE"                       │
│ → details: "gâteau au chocolat"         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ VieQuotidienneApp.handle_add()          │
│ → Dispatch vers add_recipe_interactive()│
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ FrenchLLMManager.extract_recipe_details()│
│ Tente d'extraire les infos du texte    │
│                                         │
│ Si détails suffisants:                  │
│ {                                       │
│   "titre": "Gâteau au chocolat",        │
│   "ingredients": "...",                 │
│   "instructions": "...",                │
│   ...                                   │
│ }                                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ Mode Interactif                         │
│                                         │
│ 📝 Création d'une nouvelle recette      │
│ ────────────────────────────────────    │
│                                         │
│ 📌 Titre de la recette : _              │
│ 📝 Description : _                      │
│ 🥕 Ingrédients (tapez 'fin') :          │
│   • _                                   │
│   • _                                   │
│ 👨‍🍳 Instructions (tapez 'fin') :         │
│   1. _                                  │
│   2. _                                  │
│ ⏱️  Temps de préparation (min) : _      │
│ ...                                     │
│                                         │
│ 💬 Confirmer l'ajout ? (oui/non) : _    │
└─────────────────┬───────────────────────┘
                  │ [Si confirmé]
                  ▼
┌─────────────────────────────────────────┐
│ DatabaseManager.add_recette()           │
│                                         │
│ SQL:                                    │
│ INSERT INTO recettes                    │
│ (titre, ingredients, instructions, ...) │
│ VALUES ($1, $2, $3, ...)                │
│ RETURNING id                            │
└─────────────────┬───────────────────────┘
                  │
                  ▼ [ID retourné]
┌─────────────────────────────────────────┐
│ USER OUTPUT                             │
│ ✅ Recette ajoutée (ID: 42)             │
└─────────────────────────────────────────┘
```

### 3️⃣ Flux de Suppression Sécurisée

```
USER INPUT: "Supprime la recette numéro 5"
    │
    ▼
┌─────────────────────────────────────────┐
│ classify_intent()                       │
│ → action: "SUPPRIMER"                   │
│ → type: "RECETTE"                       │
│ → details: "id:5"                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ VieQuotidienneApp.handle_delete()       │
│ Extraction de l'ID: 5                   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ ⚠️  CONFIRMATION DE SÉCURITÉ            │
│                                         │
│ ⚠️  ATTENTION :                         │
│ Vous êtes sur le point de supprimer    │
│ la RECETTE ID 5                         │
│                                         │
│ 💬 Êtes-vous sûr ?                      │
│ Tapez 'SUPPRIMER' pour confirmer : _    │
└─────────────────┬───────────────────────┘
                  │
                  ├─ [Si != "SUPPRIMER"]
                  │  └─→ ❌ Suppression annulée
                  │
                  └─ [Si == "SUPPRIMER"]
                     ▼
┌─────────────────────────────────────────┐
│ DatabaseManager.delete_recette(5)       │
│                                         │
│ SQL:                                    │
│ DELETE FROM recettes WHERE id = 5       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ USER OUTPUT                             │
│ ✅ Recette ID 5 supprimée               │
└─────────────────────────────────────────┘
```

## Structure des Fichiers

```
MinecraftRag/
│
├── 📄 database.py                    [14 KB]
│   ├── class DatabaseManager
│   ├── def create_tables()
│   ├── def add_recette()
│   ├── def search_recettes()
│   ├── def delete_recette()
│   ├── def add_astuce_menagere()
│   ├── def search_astuces()
│   └── def delete_astuce()
│
├── 🤖 llm_french.py                  [12 KB]
│   ├── class FrenchLLMManager
│   ├── def classify_intent()
│   ├── def extract_recipe_details()
│   ├── def format_search_results()
│   ├── def generate_response()
│   └── RECOMMENDED_MODELS (dict)
│
├── 🎮 app_vie_quotidienne.py         [22 KB]
│   ├── class VieQuotidienneApp
│   ├── def display_welcome()
│   ├── def handle_search()
│   ├── def handle_add()
│   ├── def handle_delete()
│   ├── def add_recipe_interactive()
│   ├── def add_astuce_interactive()
│   ├── def display_details()
│   └── def run()
│
├── 📊 examples_vie_quotidienne.py    [7 KB]
│   ├── def add_sample_data()
│   └── def main()
│
├── 🎪 demo_vie_quotidienne.py        [12 KB]
│   ├── class MockDatabase
│   ├── def demo_database_operations()
│   ├── def demo_llm_intent_classification()
│   ├── def demo_workflow()
│   └── def demo_security()
│
├── 🧪 test_database.py               [6 KB]
│   ├── def test_database_module()
│   ├── def test_llm_module()
│   ├── def test_app_module()
│   └── def test_examples_module()
│
├── 📚 README_VIE_QUOTIDIENNE.md      [11 KB]
├── 📝 IMPLEMENTATION_SUMMARY.md      [17 KB]
├── 🚀 QUICKSTART_FR.md               [5 KB]
├── 🏗️ ARCHITECTURE_DIAGRAM.md        [ce fichier]
│
├── 📦 requirements_vie_quotidienne.txt
│   ├── psycopg2-binary>=2.9.0
│   ├── llama-cpp-python>=0.2.0
│   └── python-dotenv>=1.0.0
│
├── 🗄️ models/                        [créer ce dossier]
│   └── *.gguf                        [télécharger depuis HuggingFace]
│
└── 🔧 .env                            [créer ce fichier]
    ├── DB_HOST=localhost
    ├── DB_PORT=5432
    ├── DB_NAME=vie_quotidienne
    ├── DB_USER=postgres
    ├── DB_PASSWORD=postgres
    └── LLM_MODEL_PATH=./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

## Technologies Utilisées

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| Langage | Python | 3.8+ | Base du système |
| Base de données | PostgreSQL | 12+ | Stockage structuré |
| Driver BD | psycopg2-binary | 2.9+ | Connexion PostgreSQL |
| LLM | llama-cpp-python | 0.2+ | Exécution modèle local |
| Modèle | Mistral/Vigogne | 7B Q4 | Intelligence artificielle |
| Format modèle | GGUF | Q4_K_M | Format optimisé CPU |

## Sécurité

```
┌──────────────────────────────────────────────────┐
│         MESURES DE SÉCURITÉ IMPLÉMENTÉES         │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. 🔒 Double Confirmation pour Suppression      │
│     • Avertissement clair                        │
│     • Mot exact requis ("SUPPRIMER")             │
│     • Annulation si incorrect                    │
│                                                  │
│  2. 🛡️ Requêtes SQL Paramétrées                  │
│     • Protection injection SQL                   │
│     • Utilisation de %s placeholders             │
│     • Échappement automatique                    │
│                                                  │
│  3. 🔐 Pool de Connexions                        │
│     • Limite : 1-20 connexions                   │
│     • Réutilisation des connexions               │
│     • Prévention des fuites                      │
│                                                  │
│  4. ⚠️ Gestion des Erreurs                       │
│     • Try/except sur toutes les opérations DB    │
│     • Messages utilisateur sécurisés             │
│     • Rollback automatique en cas d'erreur       │
│                                                  │
│  5. ✅ Validation des Entrées                     │
│     • IDs convertis et validés                   │
│     • Vérification des types                     │
│     • Contrôle de cohérence                      │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Performance

| Opération | Temps Moyen | Optimisation |
|-----------|-------------|--------------|
| Connexion DB | < 50ms | Pool de connexions |
| Recherche simple | < 100ms | Index sur titre |
| Ajout recette | < 200ms | Transaction unique |
| Classification LLM | 1-3s | Quantization Q4_K_M |
| Suppression | < 100ms | WHERE indexed |

## Extensibilité

```
┌─────────────────────────────────────────────────────┐
│           EXTENSIONS POSSIBLES                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Court terme (1-2 jours) :                         │
│  ✅ Routines quotidiennes (table déjà créée)       │
│  ✅ Conseils généraux (table déjà créée)           │
│  ✅ Export PDF/Markdown                            │
│  ✅ Import depuis fichiers                         │
│                                                     │
│  Moyen terme (1 semaine) :                         │
│  🔄 Embeddings + recherche sémantique              │
│  🔄 Suggestions intelligentes                      │
│  🔄 Interface web Flask/FastAPI                    │
│  🔄 API REST complète                              │
│                                                     │
│  Long terme (1 mois+) :                            │
│  🚀 Application mobile                             │
│  🚀 Système multi-utilisateurs                     │
│  🚀 Partage de recettes                            │
│  🚀 Assistant vocal                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

**Diagramme créé pour le projet MinecraftRag - Système Vie Quotidienne**
**Version : 1.0 - Date : 2024**
