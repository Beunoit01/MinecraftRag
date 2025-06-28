import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
# Chemin vers le dossier contenant les fichiers .txt scrapés
INPUT_DIR = "wiki_content" # Assurez-vous que ce soit le bon dossier
# Paramètres pour le découpage (à ajuster selon vos besoins)
CHUNK_SIZE = 1000  # Taille cible pour chaque morceau (en caractères)
CHUNK_OVERLAP = 150 # Nombre de caractères de chevauchement entre morceaux consécutifs

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

            # Ajouter les morceaux à la liste globale
            # Vous pourriez vouloir stocker le nom du fichier source avec chaque morceau
            for chunk in chunks:
                 all_chunks.append({"source": filename, "text": chunk})


        except Exception as e:
            print(f"  -> Erreur lors du traitement du fichier {filename}: {e}")

    print("\n--- Découpage Terminé ---")
    print(f"Nombre total de morceaux créés pour tous les fichiers: {len(all_chunks)}")

    # À ce stade, `all_chunks` contient une liste de dictionnaires,
    # chaque dictionnaire représentant un morceau avec sa source et son texte.
    # L'étape suivante serait de créer les embeddings pour ces morceaux.

    # Exemple: Afficher le nombre de morceaux et le début du premier
    if all_chunks:
         print(f"\nExemple du premier morceau généré:")
         print(f"Source: {all_chunks[0]['source']}")
         print(f"Texte (début): {all_chunks[0]['text'][:300]}...")


except FileNotFoundError:
    print(f"Erreur: Le dossier d'entrée '{INPUT_DIR}' n'a pas été trouvé.")
except Exception as e:
    print(f"Une erreur générale est survenue: {e}")