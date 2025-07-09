import os
import re
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import torch
# Importation nécessaire pour le LLM local
from llama_cpp import Llama
# NOUVELLE IMPORTATION pour lire les PDFs
import fitz  # PyMuPDF

# --- Configuration ---
PERSIST_DIRECTORY = "chroma_db_climate_facts"
COLLECTION_NAME = "climate_facts_chunks"
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
NUM_RESULTS_TO_RETRIEVE = 7
PDF_PATH = "climate_articles.pdf"
# MODIFIÉ: Dossier pour sauvegarder les analyses
ANALYSIS_OUTPUT_DIR = "result"

# --- Configuration du LLM Local (Llama 3) ---
MODEL_PATH = "/home/benoit_v/Documents/models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"

# Mettre 0 pour utiliser uniquement le CPU
N_GPU_LAYERS = 0
N_CTX = 8192  # Llama 3 supporte un contexte plus large
N_BATCH = 512

# --- Initialisation des modèles et de la base de données ---
print("--- Initialisation du système de Fact-Checking ---")

# Initialisation du Modèle d'Embedding
print(f"\n1. Chargement du modèle d'embedding: '{MODEL_NAME}'")
embedding_model = None
try:
    device_embed = 'cuda' if torch.cuda.is_available() and N_GPU_LAYERS > 0 else 'cpu'
    print(f"   Utilisation du périphérique pour l'embedding: {device_embed.upper()}")
    embedding_model = SentenceTransformer(MODEL_NAME, device=device_embed)
    print("   -> Modèle d'embedding chargé.")
except Exception as e:
    print(f"   Erreur critique lors du chargement du modèle d'embedding: {e}")
    exit()

# Initialisation de ChromaDB
print(f"\n2. Connexion à la base de données vectorielle ChromaDB...")
collection = None
try:
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"   -> Connecté à la collection '{COLLECTION_NAME}' ({collection.count()} documents).")
except Exception as e:
    print(f"   Erreur critique lors de la connexion à ChromaDB: {e}")
    exit()

# Initialisation du LLM Local
print(f"\n3. Chargement du Large Language Model (LLM) local...")
llm_model = None
if not os.path.exists(MODEL_PATH):
    print(f"   Erreur: Fichier modèle GGUF non trouvé à '{MODEL_PATH}'.")
    print("   Le script fonctionnera sans l'analyse IA.")
else:
    try:
        llm_model = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=N_GPU_LAYERS,
            n_ctx=N_CTX,
            n_batch=N_BATCH,
            verbose=False
        )
        print("   -> Modèle LLM local chargé avec succès.")
    except Exception as e:
        print(f"   Erreur lors du chargement du LLM local: {e}")
        print("   Vérifiez le chemin du modèle et les paramètres. Le script continuera sans IA.")

print("\n--- Initialisation terminée ---")


# --- FONCTIONS ---

def load_and_split_articles(pdf_path: str) -> list[dict]:
    """Charge un PDF, extrait le texte et le sépare en articles numérotés."""
    articles = []
    if not os.path.exists(pdf_path):
        print(f"Erreur: Le fichier PDF '{pdf_path}' n'a pas été trouvé.")
        return articles
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        # Regex pour trouver les articles commençant par un numéro suivi de ":"
        raw_articles = re.split(r'\n(\d+):\s', full_text)
        if raw_articles[0].strip().lower() == "climate articles":
            raw_articles.pop(0)
        i = 0
        while i < len(raw_articles) - 1:
            num = raw_articles[i]
            content = raw_articles[i + 1]
            title = content.split('\n')[0].strip()
            articles.append({
                "number": int(num),
                "title": title,
                "text": content.strip()
            })
            i += 2
        print(f"\n{len(articles)} articles chargés depuis le PDF.")
        return articles
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF: {e}")
        return []


def analyze_article(article: dict):
    """Analyse un article pour déterminer sa crédibilité."""
    print(f"\nAnalyse de l'article n°{article['number']}: '{article['title']}'")
    if not llm_model:
        return "Analyse impossible: le LLM n'a pas été chargé."
    search_query = article['title'] + "\n" + " ".join(article['text'].split()[:100])
    print("  -> Recherche de contexte scientifique pertinent dans ChromaDB...")
    try:
        query_embedding = embedding_model.encode(search_query, device=device_embed).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=NUM_RESULTS_TO_RETRIEVE,
            include=['documents']
        )
        context_chunks = results.get('documents', [[]])[0]
        if not context_chunks:
            return "❓ **INFORMATION INSUFFISANTE** - Aucune source scientifique fiable trouvée pour évaluer cet article."
        context_string = "\n\n---\n\n".join(context_chunks)
        print(f"  -> {len(context_chunks)} extraits de contexte scientifique trouvés.")
    except Exception as e:
        print(f"  -> Erreur lors de la recherche: {e}")
        return "Impossible d'accéder aux sources scientifiques (erreur base de données)."

    system_prompt = """You are a meticulous and impartial climate science fact-checker. Your mission is to analyze the 'ARTICLE TO ANALYZE' and determine its credibility by comparing its claims against the provided 'SCIENTIFIC CONTEXT'. Base your entire analysis ONLY on the provided context. Do not use any external knowledge.

Your output must be structured in the following format:
1.  **VERDICT:** [Choose ONE: Factual and Credible / Disinformation or Hoax]
2.  **CONFIDENCE:** [High / Medium / Low]
3.  **ARTICLE SUMMARY:** [Briefly summarize the main argument of the article in 2-3 sentences.]
4.  **FACT-CHECK ANALYSIS:** [Provide a point-by-point analysis. Compare the article's claims to the provided scientific context. If the article is misleading or false, explain exactly why, citing the scientific context.]"""
    user_prompt = f"""**SCIENTIFIC CONTEXT:**
---
{context_string}
---
**ARTICLE TO ANALYZE:**
---
{article['text']}
---

Provide your fact-check analysis based on the instructions."""
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
    print("  -> L'IA analyse l'article... (cela peut prendre un moment)")
    try:
        output = llm_model(
            prompt,
            max_tokens=800,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            temperature=0.1,
            echo=False
        )
        analysis = output['choices'][0]['text'].strip()
        return analysis
    except Exception as e:
        print(f"  -> Erreur lors de l'analyse par l'IA: {e}")
        return "Erreur lors de la génération de la réponse par l'IA."


def save_analysis_to_file(filename: str, content: str):
    """Sauvegarde le contenu de l'analyse dans un fichier texte."""
    if not os.path.exists(ANALYSIS_OUTPUT_DIR):
        os.makedirs(ANALYSIS_OUTPUT_DIR)
        print(f"Dossier '{ANALYSIS_OUTPUT_DIR}' créé.")
    filepath = os.path.join(ANALYSIS_OUTPUT_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Analyse sauvegardée avec succès dans: {filepath}")
    except Exception as e:
        print(f"\n❌ Erreur lors de la sauvegarde du fichier: {e}")


# --- Boucle Principale Modifiée ---
if __name__ == "__main__":
    articles = load_and_split_articles(PDF_PATH)
    if not articles:
        print("Impossible de continuer sans articles à analyser. Fin du programme.")
        exit()

    while True:
        print("\n" + "=" * 60)
        print("📰 MENU DE FACT-CHECKING")
        print("=" * 60)
        for article in articles:
            print(f"  {article['number']}: {article['title']}")
        print("-" * 60)
        print("  'all': Analyser TOUS les articles et sauvegarder les résultats.")
        print("=" * 60)
        print("Entrez le numéro de l'article à analyser, 'all', ou 'quit'.")

        user_input = input("\nVotre choix: ")

        if user_input.lower() in ['quit', 'exit']:
            break

        # --- NOUVELLE LOGIQUE POUR ANALYSER TOUS LES ARTICLES ---
        if user_input.lower() == 'all':
            print("\n--- Lancement de l'analyse de tous les articles ---")
            for article in articles:
                analysis_result = analyze_article(article)
                header = f"🔎 RÉSULTAT DE L'ANALYSE - ARTICLE {article['number']}: {article['title']}"

                # Afficher le résultat dans la console
                print("\n" + "#" * len(header))
                print(header)
                print("#" * len(header))
                print(analysis_result)
                print("#" * len(header))

                # Sauvegarder automatiquement le fichier pour chaque article
                filename = f"analyse_article_{article['number']}.txt"
                file_content = f"{header}\n\n{analysis_result}"
                save_analysis_to_file(filename, file_content)

            print("\n--- Analyse de tous les articles terminée. ---")
            continue  # Revenir au menu principal

        try:
            choice = int(user_input)
            selected_article = next((a for a in articles if a['number'] == choice), None)

            if selected_article:
                analysis_result = analyze_article(selected_article)
                header = f"🔎 RÉSULTAT DE L'ANALYSE - ARTICLE {selected_article['number']}: {selected_article['title']}"

                print("\n" + "#" * len(header))
                print(header)
                print("#" * len(header))
                print(analysis_result)
                print("#" * len(header))

                # Sauvegarder automatiquement le fichier
                filename = f"analyse_article_{selected_article['number']}.txt"
                file_content = f"{header}\n\n{analysis_result}"
                save_analysis_to_file(filename, file_content)
            else:
                print(f"Erreur: Le numéro d'article '{choice}' n'est pas valide.")

        except ValueError:
            print("Erreur: Veuillez entrer un numéro valide ou 'all'.")
        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")

    print("\n🌍 Fin du programme de fact-checking.")
