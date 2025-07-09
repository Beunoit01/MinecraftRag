import json
import chromadb
from chromadb.utils import embedding_functions # Pour utiliser les embeddings pré-calculés

INPUT_EMBEDDINGS_FILE = "climate_embeddings_data.json"
PERSIST_DIRECTORY = "chroma_db_climate_facts"
COLLECTION_NAME = "climate_facts_chunks"



with open(INPUT_EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
    all_data = json.load(f)


client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

default_ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=default_ef
)

ids = [item['id'] for item in all_data]
documents = [item['text'] for item in all_data]
embeddings = [item['embedding'] for item in all_data]
metadatas = [{'source': item['source']} for item in all_data] # Créer les métadonnées



collection.upsert(
    ids=ids,
    embeddings=embeddings,
    metadatas=metadatas,
    documents=documents # Le texte original est stocké comme 'document'
)

