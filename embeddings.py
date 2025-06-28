import os
import json # Pour sauvegarder les résultats facilement
from sentence_transformers import SentenceTransformer
import torch # Pour vérifier la disponibilité du GPU
# Assurez-vous que langchain est installé si vous utilisez le chunking ici
# pip install langchain sentence-transformers torch
from langchain.text_splitter import RecursiveCharacterTextSplitter


# --- Configuration ---
# Chemin vers le dossier contenant les fichiers .txt scrapés
INPUT_DIR_CHUNKS = "wiki_content" # Ou "wiki_content_fr" si vous avez tout scrapé
# Nom du modèle d'embedding à utiliser (depuis Hugging Face Hub)
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
# Fichier où sauvegarder les chunks avec leurs embeddings
OUTPUT_EMBEDDINGS_FILE = "embeddings_data.json" # Le fichier sera recréé

# Paramètres pour le découpage (si on le refait ici)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# --- Fonction pour charger et découper les fichiers ---
def load_and_chunk_files(input_dir):
    """Charge les fichiers .txt, les découpe et retourne une liste de chunks avec ID."""
    all_chunks_with_id = []
    print(f"Chargement et découpage des fichiers depuis '{input_dir}'...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " ", ""]
    )

    try:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
        if not txt_files:
             print(f"Erreur: Aucun fichier .txt trouvé dans '{input_dir}'.")
             return None # Retourne None en cas d'erreur

        total_files = len(txt_files)
        print(f"Trouvé {total_files} fichier(s) .txt à traiter.")

        for i_file, filename in enumerate(txt_files):
            filepath = os.path.join(input_dir, filename)
            print(f"  [{i_file+1}/{total_files}] Traitement: {filename}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                if not file_content.strip():
                    print("    -> Fichier vide, ignoré.")
                    continue

                # Découper le contenu du fichier
                chunks_from_file = text_splitter.split_text(file_content)
                print(f"    -> Découpé en {len(chunks_from_file)} morceau(x).")

                # *** CORRECTION CLÉ : S'assurer que l'ID est ajouté ici ***
                for i_chunk, chunk_text in enumerate(chunks_from_file):
                    # Créer l'ID unique pour ce morceau
                    chunk_id = f"{filename}_{i_chunk}"
                    # Ajouter le dictionnaire complet à la liste
                    all_chunks_with_id.append({
                        "id": chunk_id,         # ID unique
                        "source": filename,     # Nom du fichier source
                        "text": chunk_text      # Texte du morceau
                        # L'embedding sera ajouté plus tard
                    })

            except Exception as e:
                print(f"    -> Erreur lors du traitement du fichier {filename}: {e}")

        print(f"\nDécoupage terminé. Nombre total de chunks générés: {len(all_chunks_with_id)}")
        return all_chunks_with_id # Retourne la liste des chunks

    except FileNotFoundError:
        print(f"Erreur: Le dossier d'entrée '{input_dir}' n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur générale est survenue lors du chargement/découpage: {e}")
        return None

# --- Script Principal ---

if __name__ == "__main__":
    # 1. Charger et découper les fichiers
    #    Cette fonction s'assure que chaque chunk a un 'id', 'source', et 'text'
    chunks_data = load_and_chunk_files(INPUT_DIR_CHUNKS)

    if not chunks_data:
        print("Erreur: Échec du chargement ou du découpage des fichiers. Arrêt.")
        exit()

    # 2. Création des Embeddings
    print(f"\nChargement du modèle d'embedding: '{MODEL_NAME}'")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Utilisation du périphérique: {device.upper()}")
    try:
        model = SentenceTransformer(MODEL_NAME, device=device)
        print("Modèle chargé.")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle SentenceTransformer: {e}")
        print("Assurez-vous que les bibliothèques torch et sentence-transformers sont correctement installées.")
        exit()


    print(f"\nCréation des embeddings pour {len(chunks_data)} chunks...")
    texts_to_embed = [chunk['text'] for chunk in chunks_data]

    try:
        embeddings = model.encode(texts_to_embed, show_progress_bar=True, device=device, batch_size=32) # batch_size peut être ajusté
        print(f"Embeddings créés. Dimension du vecteur: {embeddings.shape[1]}")
    except Exception as e:
        print(f"Erreur lors du calcul des embeddings: {e}")
        exit()


    # 3. Ajouter les embeddings aux données des chunks
    #    On itère sur la liste chunks_data et on ajoute la clé 'embedding'
    try:
        for i, chunk in enumerate(chunks_data):
            if i < len(embeddings):
                 chunk['embedding'] = embeddings[i].tolist() # Convertir l'array numpy en liste pour JSON
            else:
                 print(f"Avertissement: Moins d'embeddings ({len(embeddings)}) que de chunks ({len(chunks_data)}). Problème à l'index {i}.")
                 # Décider quoi faire: ignorer le chunk, mettre un embedding vide, etc.
                 # Pour l'instant, on ignore pour éviter une erreur lors de la sauvegarde
                 # On pourrait aussi supprimer le chunk de la liste: del chunks_data[i] (attention à l'indexation)

        # Filtrer les chunks qui n'ont pas reçu d'embedding (si le problème ci-dessus s'est produit)
        chunks_data_final = [chunk for chunk in chunks_data if 'embedding' in chunk]
        if len(chunks_data_final) != len(chunks_data):
             print(f"Avertissement: {len(chunks_data) - len(chunks_data_final)} chunks ont été retirés car leur embedding n'a pas pu être ajouté.")

    except Exception as e:
        print(f"Erreur lors de l'ajout des embeddings aux données des chunks: {e}")
        exit()


    # 4. Sauvegarde des Résultats (avec id, source, text, embedding)
    print(f"\nSauvegarde de {len(chunks_data_final)} chunks avec leurs embeddings dans '{OUTPUT_EMBEDDINGS_FILE}'...")
    try:
        with open(OUTPUT_EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(chunks_data_final, f, ensure_ascii=False, indent=4)
        print("Sauvegarde terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier JSON: {e}")

    # Affichage d'un exemple pour vérification
    if chunks_data_final:
        print("\nExemple du premier chunk sauvegardé:")
        first_chunk = chunks_data_final[0]
        print(f"ID: {first_chunk.get('id', 'N/A')}")
        print(f"Source: {first_chunk.get('source', 'N/A')}")
        print(f"Texte (début): {first_chunk.get('text', '')[:100]}...")
        embedding_preview = first_chunk.get('embedding', [])[:5]
        print(f"Embedding (début): {embedding_preview}...")
        print(f"Dimension totale de l'embedding: {len(first_chunk.get('embedding', []))}")

