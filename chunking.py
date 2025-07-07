import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
# Chemin vers le dossier contenant les fichiers .txt scrapés
INPUT_DIR = "climate_facts_content_from_pdfs" # Dossier avec les PDFs extraits
# Fichier de sortie pour sauvegarder les chunks
OUTPUT_CHUNKS_FILE = "climate_chunks_data.json"
# Paramètres pour le découpage (à ajuster selon vos besoins)
CHUNK_SIZE = 1200  # Légèrement plus grand pour les textes scientifiques
CHUNK_OVERLAP = 200 # Plus de chevauchement pour préserver le contexte scientifique

# --- Initialisation du Text Splitter ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len, # Fonction pour mesurer la taille (standard: len)
    # Séparateurs essayés dans l'ordre (le premier est le plus prioritaire)
    separators=["\n\n", "\n", ". ", ", ", " ", ""]
)

# --- Traitement des fichiers ---
all_chunks = [] # Liste pour stocker tous les morceaux de tous les fichiers

print(f"Début du découpage des fichiers dans '{INPUT_DIR}'...")

try:
    # Lister tous les fichiers .txt dans le dossier d'entrée
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    if not txt_files:
        print(f"Erreur: Aucun fichier .txt trouvé dans le dossier '{INPUT_DIR}'.")
        exit()

    total_files = len(txt_files)
    print(f"Trouvé {total_files} fichier(s) .txt à traiter.")

    for i, filename in enumerate(txt_files):
        filepath = os.path.join(INPUT_DIR, filename)
        print(f"\n[{i+1}/{total_files}] Traitement du fichier: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()

            if not file_content.strip():
                print("  -> Fichier vide, ignoré.")
                continue

            # Découper le contenu du fichier
            chunks = text_splitter.split_text(file_content)
            num_chunks = len(chunks)
            print(f"  -> Découpé en {num_chunks} morceau(x).")

            # Optionnel: Afficher le premier morceau pour vérifier
            # if chunks:
            #     print("  -> Premier morceau (aperçu):")
            #     print(chunks[0][:200] + "...") # Affiche les 200 premiers caractères

            # Ajouter les morceaux à la liste globale avec ID unique
            for j, chunk in enumerate(chunks):
                chunk_id = f"{filename}_{i+1}_{j+1}"  # ID unique pour chaque chunk
                all_chunks.append({
                    "id": chunk_id,
                    "source": filename,
                    "text": chunk,
                    "chunk_index": j,
                    "total_chunks_in_file": num_chunks
                })


        except Exception as e:
            print(f"  -> Erreur lors du traitement du fichier {filename}: {e}")

    print("\n--- Découpage Terminé ---")
    print(f"Nombre total de morceaux créés pour tous les fichiers: {len(all_chunks)}")

    # Sauvegarder les chunks en JSON
    print(f"\n💾 Sauvegarde des chunks dans: {OUTPUT_CHUNKS_FILE}")
    try:
        with open(OUTPUT_CHUNKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        print(f"✅ Chunks sauvegardés avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")

    # Statistiques détaillées
    total_chars = sum(len(chunk['text']) for chunk in all_chunks)
    avg_chunk_size = total_chars / len(all_chunks) if all_chunks else 0
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   📁 Fichiers traités: {total_files}")
    print(f"   🧩 Total chunks: {len(all_chunks)}")
    print(f"   📝 Total caractères: {total_chars:,}")
    print(f"   📏 Taille moyenne par chunk: {avg_chunk_size:.0f} caractères")
    print(f"   💾 Données sauvées dans: {OUTPUT_CHUNKS_FILE}")

    # Exemple: Afficher le nombre de morceaux et le début du premier
    if all_chunks:
         print(f"\nExemple du premier morceau généré:")
         print(f"ID: {all_chunks[0]['id']}")
         print(f"Source: {all_chunks[0]['source']}")
         print(f"Texte (début): {all_chunks[0]['text'][:300]}...")
         
    print(f"\n🎯 PROCHAINE ÉTAPE: python embeddings.py")


except FileNotFoundError:
    print(f"Erreur: Le dossier d'entrée '{INPUT_DIR}' n'a pas été trouvé.")
except Exception as e:
    print(f"Une erreur générale est survenue: {e}")