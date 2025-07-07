import os
import json
import chromadb
from chromadb.utils import embedding_functions # Pour utiliser les embeddings pré-calculés

# --- Configuration ---
# Fichier contenant les chunks et leurs embeddings pré-calculés
INPUT_EMBEDDINGS_FILE = "climate_embeddings_data.json"
# Dossier où ChromaDB stockera ses fichiers (index, etc.)
PERSIST_DIRECTORY = "chroma_db_climate_facts"
# Nom de la collection dans ChromaDB (comme une table dans une BDD SQL)
COLLECTION_NAME = "climate_facts_chunks"

# --- Chargement des données pré-calculées ---
print(f"Chargement des données depuis '{INPUT_EMBEDDINGS_FILE}'...")
try:
    with open(INPUT_EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    print(f"Chargé {len(all_data)} chunks avec leurs embeddings.")
except FileNotFoundError:
    print(f"Erreur: Le fichier d'embeddings '{INPUT_EMBEDDINGS_FILE}' n'a pas été trouvé.")
    exit()
except json.JSONDecodeError:
    print(f"Erreur: Le fichier '{INPUT_EMBEDDINGS_FILE}' n'est pas un JSON valide.")
    exit()
except Exception as e:
    print(f"Erreur inattendue lors du chargement du fichier JSON: {e}")
    exit()

if not all_data:
    print("Erreur: Aucune donnée chargée depuis le fichier JSON.")
    exit()

# Vérifier si les données ont le format attendu (id, text, embedding, source)
if not all('id' in item and 'text' in item and 'embedding' in item and 'source' in item for item in all_data):
     print("Erreur: Le format des données dans le JSON est incorrect.")
     print("Chaque élément doit avoir les clés 'id', 'text', 'embedding', et 'source'.")
     # Optionnel: Afficher un exemple d'élément incorrect
     for i, item in enumerate(all_data):
         if not ('id' in item and 'text' in item and 'embedding' in item and 'source' in item):
             print(f"Élément incorrect à l'index {i}: {item}")
             break
     exit()


# --- Initialisation de ChromaDB ---
print(f"\nInitialisation de ChromaDB...")
print(f"Les données seront persistées dans le dossier: '{PERSIST_DIRECTORY}'")
# Crée un client ChromaDB qui sauvegarde les données sur disque
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

# Utiliser une fonction d'embedding "factice" car nous fournissons les nôtres
# ChromaDB a besoin d'une fonction d'embedding pour fonctionner, même si on ne l'utilise pas
# pour calculer les embeddings ici. On utilise celle par défaut (all-MiniLM-L6-v2)
# mais elle ne sera PAS appelée si on fournit les embeddings directement.
# Alternative: utiliser embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME_UTILISE_POUR_CREER_EMBEDDINGS)
# pour être cohérent, mais cela ne change rien si on fournit les embeddings.
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Accéder à la collection ou la créer si elle n'existe pas
# IMPORTANT: Si la collection existe déjà avec une fonction d'embedding différente,
# cela peut causer des erreurs. Il est plus sûr de la supprimer et la recréer si on change de modèle.
print(f"Accès/Création de la collection ChromaDB: '{COLLECTION_NAME}'")
# Utiliser get_or_create_collection pour éviter les erreurs si elle existe déjà
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=default_ef # Nécessaire même si on fournit les embeddings
    # metadata={"hnsw:space": "cosine"} # Optionnel: Spécifier la distance (cosine est souvent bon pour les embeddings textuels)
)
print("Collection prête.")

# --- Préparation des données pour ChromaDB ---
# ChromaDB attend des listes séparées pour les ids, documents (texte), metadatas, et embeddings
ids = [item['id'] for item in all_data]
documents = [item['text'] for item in all_data]
embeddings = [item['embedding'] for item in all_data]
metadatas = [{'source': item['source']} for item in all_data] # Créer les métadonnées

# --- Ajout des données à la collection ---
# Note: ChromaDB gère l'ajout par lots si la liste est grande.
# Si la collection contient déjà ces IDs, ChromaDB peut les mettre à jour (upsert) ou lever une erreur
# selon sa configuration. L'ajout simple (`add`) échouera si les IDs existent.
# Utilisons `upsert` pour ajouter ou mettre à jour si l'ID existe déjà.
print(f"\nAjout/Mise à jour de {len(ids)} éléments dans la collection ChromaDB...")
try:
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents # Le texte original est stocké comme 'document'
    )
    print("Données ajoutées/mises à jour avec succès dans ChromaDB.")
except Exception as e:
    # Des erreurs peuvent survenir ici (ex: format d'embedding incorrect, problème disque)
    print(f"\nErreur lors de l'ajout des données à ChromaDB: {e}")
    print("Vérifiez le format des embeddings et l'espace disque disponible.")
    exit()


# --- Vérification (Optionnel mais recommandé) ---
count = collection.count()
print(f"\nVérification: La collection '{COLLECTION_NAME}' contient maintenant {count} éléments.")

if count == len(all_data):
    print("Le nombre d'éléments correspond aux données chargées.")
else:
    print(f"Avertissement: Le nombre d'éléments ({count}) ne correspond pas aux données initiales ({len(all_data)}).")


# --- Exemple de Requête (Pour tester que ça fonctionne) ---
print("\nExemple de requête de similarité:")
# Pour faire une requête, il faut l'embedding de la question.
# Ici, on va tricher et utiliser l'embedding d'un des chunks existants
# pour voir s'il se retrouve lui-même ou des chunks similaires.
if embeddings:
    query_embedding = embeddings[0] # Utiliser l'embedding du premier chunk comme exemple
    query_text_preview = documents[0][:100] # Texte correspondant à cet embedding
    print(f"Utilisation de l'embedding du chunk commençant par: '{query_text_preview}...'")

    try:
        results = collection.query(
            query_embeddings=[query_embedding], # Doit être une liste d'embeddings
            n_results=3 # Demander les 3 résultats les plus similaires
            # include=['documents', 'metadatas', 'distances'] # Ce qu'on veut récupérer
        )

        print("\nRésultats de la requête de similarité (Top 3):")
        # L'objet results contient plusieurs listes (une par embedding de requête)
        if results and results.get('ids') and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                result_id = results['ids'][0][i]
                distance = results['distances'][0][i]
                metadata = results['metadatas'][0][i]
                document = results['documents'][0][i]
                print(f"\n  Résultat {i+1}:")
                print(f"    ID: {result_id}")
                print(f"    Distance: {distance:.4f}") # Plus la distance est faible, plus c'est similaire
                print(f"    Source: {metadata.get('source', 'N/A')}")
                print(f"    Texte (début): {document[:150]}...")
        else:
            print("La requête n'a retourné aucun résultat.")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête de test: {e}")

print("\n--- Indexation Terminée ---")
print(f"Votre base de données vectorielle est prête dans le dossier '{PERSIST_DIRECTORY}'.")