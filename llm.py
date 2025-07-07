import os
import json
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import torch
# Importation nécessaire pour le LLM local
from llama_cpp import Llama

# --- Configuration ---
# Chemin vers le dossier de la base ChromaDB persistante
PERSIST_DIRECTORY = "chroma_db_climate_facts"
# Nom de la collection dans ChromaDB
COLLECTION_NAME = "climate_facts_chunks"
# Nom du modèle d'embedding (DOIT être le même que celui utilisé pour créer les embeddings)
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
# Nombre de chunks pertinents à récupérer de ChromaDB
NUM_RESULTS_TO_RETRIEVE = 5 # Plus de contexte pour l'analyse des fake news

# --- Configuration du LLM Local (llama-cpp-python) ---
# *** MODIFIEZ CECI: Chemin vers votre fichier modèle GGUF téléchargé ***
MODEL_PATH = "/home/benoitv/Documents/Software/Phi-3-mini-4k-instruct-q4.gguf" # EXEMPLE: "/home/user/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Paramètres pour llama-cpp-python
N_GPU_LAYERS = 30   # Nombre de couches à décharger sur le GPU.
                    # À AJUSTER pour votre RTX 3060 Ti 8GB !
                    # Commencez vers 30-35 pour un modèle 7B Q4/Q5.
                    # Si vous avez des erreurs "CUDA out of memory", réduisez cette valeur.
                    # Si c'est trop lent, essayez d'augmenter (si la VRAM le permet).
                    # Mettre 0 pour utiliser uniquement le CPU (très lent).
N_CTX = 2048        # Taille maximale du contexte (tokens) que le modèle peut gérer.
                    # Vérifiez la taille supportée par le modèle GGUF choisi. 2048 est souvent sûr.
N_BATCH = 512       # Taille du batch pour le traitement du prompt (peut influencer la VRAM).

# --- Initialisation du Modèle d'Embedding (inchangé) ---
print(f"\nChargement du modèle d'embedding local: '{MODEL_NAME}'")
try:
    device_embed = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Utilisation du périphérique pour l'embedding: {device_embed.upper()}")
    embedding_model = SentenceTransformer(MODEL_NAME, device=device_embed)
    print("Modèle d'embedding chargé.")
except Exception as e:
    print(f"Erreur critique lors du chargement du modèle d'embedding: {e}")
    exit()

# --- Initialisation de ChromaDB (inchangé) ---
print(f"\nConnexion à la base de données ChromaDB persistante: '{PERSIST_DIRECTORY}'")
try:
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    default_ef = embedding_functions.DefaultEmbeddingFunction() # Juste pour obtenir la collection
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=default_ef
    )
    print(f"Connecté à la collection '{COLLECTION_NAME}' contenant {collection.count()} éléments.")
except Exception as e:
    print(f"Erreur critique lors de la connexion à ChromaDB ou à la collection: {e}")
    exit()

# --- Initialisation du LLM Local ---
print(f"\nChargement du LLM local depuis: '{MODEL_PATH}'")
llm_model = None # Initialiser à None
if not os.path.exists(MODEL_PATH):
    print(f"Erreur: Le fichier modèle GGUF '{MODEL_PATH}' n'a pas été trouvé.")
    print("Veuillez vérifier le chemin dans la configuration MODEL_PATH.")
else:
    try:
        llm_model = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=N_GPU_LAYERS,
            n_ctx=N_CTX,
            n_batch=N_BATCH,
            verbose=True # Mettre à False pour moins de messages de llama.cpp
        )
        print("Modèle LLM local chargé avec succès.")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle LLM local: {e}")
        print("Vérifiez le chemin du modèle, les paramètres (n_gpu_layers) et l'installation de llama-cpp-python avec support GPU.")
        # Le script continuera sans LLM si le chargement échoue

def analyze_climate_claim(claim: str):
    """
    Analyse une affirmation sur le climat pour détecter les fake news.
    Retourne une évaluation basée sur les sources scientifiques fiables.
    """
    print(f"\nAnalyse de l'affirmation: '{claim}'")

    # 1. Créer l'embedding de l'affirmation
    print("  -> Création de l'embedding pour l'affirmation...")
    try:
        claim_embedding = embedding_model.encode(claim, device=device_embed).tolist()
        print("  -> Embedding de l'affirmation créé.")
    except Exception as e:
        print(f"  -> Erreur lors de la création de l'embedding: {e}")
        return "Impossible d'analyser cette affirmation (erreur technique)."

    # 2. Rechercher dans les sources scientifiques fiables
    print(f"  -> Recherche dans les sources scientifiques fiables...")
    try:
        results = collection.query(
            query_embeddings=[claim_embedding],
            n_results=NUM_RESULTS_TO_RETRIEVE,
            include=['documents', 'metadatas', 'distances']
        )
        print(f"  -> Trouvé {len(results.get('ids', [[]])[0])} source(s) pertinente(s).")
    except Exception as e:
        print(f"  -> Erreur lors de la recherche: {e}")
        return "Impossible d'accéder aux sources scientifiques (erreur base de données)."

    context_chunks = results.get('documents', [[]])[0]
    if not context_chunks:
        return "❓ **INFORMATION INSUFFISANTE** - Aucune source scientifique fiable trouvée pour évaluer cette affirmation."

    sources = [meta.get('source', 'Inconnue') for meta in results.get('metadatas', [[]])[0]]
    distances = results.get('distances', [[]])[0]
    
    # 3. Construire le prompt spécialisé pour la détection de fake news
    context_string = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""You are a climate science fact-checker. Based ONLY on the provided scientific sources (IPCC reports, Environmental Defense Fund), analyze the following claim:

CLAIM TO ANALYZE: "{claim}"

SCIENTIFIC SOURCES:
---
{context_string}
---

Provide a fact-check analysis in the following format:
1. VERDICT: [TRUE/FALSE/PARTIALLY TRUE/INSUFFICIENT DATA]
2. CONFIDENCE: [HIGH/MEDIUM/LOW]
3. EXPLANATION: Brief explanation based on the scientific sources
4. SOURCES: Which sources support your verdict

Be precise and cite specific scientific evidence. If the claim contradicts established science, clearly explain why.
"""

    print("\n  -> Analyse en cours par l'IA...")

    # 4. Générer l'analyse avec le LLM
    if llm_model:
        try:
            output = llm_model(
                prompt,
                max_tokens=500,
                stop=["CLAIM TO ANALYZE:", "\n\n---", "SCIENTIFIC SOURCES:"],
                echo=False,
                temperature=0.2  # Plus déterministe pour les fact-checks
            )
            analysis = output['choices'][0]['text'].strip()
            
            # Ajouter les métadonnées des sources
            sources_info = "\n\n**Sources consultées:**\n"
            for src, dist in zip(sources, distances):
                sources_info += f"- {src} (pertinence: {(1-dist)*100:.1f}%)\n"
            
            return analysis + sources_info

        except Exception as e:
            print(f"  -> Erreur lors de l'analyse: {e}")
            return "Erreur lors de l'analyse par l'IA."
    else:
        # Version de secours sans LLM
        return f"🔍 **SOURCES TROUVÉES** (LLM non disponible):\n\n{context_string}\n\n**Sources:** {', '.join(set(sources))}"


# --- Fonction pour gérer une requête RAG (adaptée pour LLM local) ---

def answer_query_rag(query: str):
    """
    Prend une question, trouve le contexte pertinent dans ChromaDB,
    et génère une réponse en utilisant le LLM local configuré.
    """
    print(f"\nTraitement de la question: '{query}'")

    # 1. Créer l'embedding de la question (inchangé)
    print("  -> Création de l'embedding pour la question...")
    try:
        # Utiliser le même device que pour le chargement du modèle d'embedding
        query_embedding = embedding_model.encode(query, device=device_embed).tolist()
        print("  -> Embedding de la question créé.")
    except Exception as e:
        print(f"  -> Erreur lors de la création de l'embedding de la question: {e}")
        return "Désolé, je n'ai pas pu traiter votre question (erreur d'embedding)."

    # 2. Interroger ChromaDB pour trouver les chunks pertinents (inchangé)
    print(f"  -> Recherche des {NUM_RESULTS_TO_RETRIEVE} chunks pertinents dans ChromaDB...")
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=NUM_RESULTS_TO_RETRIEVE,
            include=['documents', 'metadatas', 'distances']
        )
        print(f"  -> Recherche terminée. Trouvé {len(results.get('ids', [[]])[0])} résultat(s).")
    except Exception as e:
        print(f"  -> Erreur lors de la recherche dans ChromaDB: {e}")
        return "Désolé, je n'ai pas pu rechercher les informations pertinentes (erreur base de données)."

    context_chunks = results.get('documents', [[]])[0]
    if not context_chunks:
        print("  -> Aucun chunk pertinent trouvé dans la base de données.")
        return "Désolé, je n'ai trouvé aucune information pertinente dans ma base de connaissances pour répondre à votre question."

    sources = [meta.get('source', 'Inconnue') for meta in results.get('metadatas', [[]])[0]]
    distances = results.get('distances', [[]])[0]
    print("  -> Sources récupérées (distances):")
    for src, dist in zip(sources, distances):
        print(f"    - {src} (distance: {dist:.4f})")

    # 3. Construire le prompt pour le LLM (potentiellement à adapter au format du modèle)
    context_string = "\n\n---\n\n".join(context_chunks)

    # *** MODIFICATION: Prompt en Anglais ***
    # Simple English prompt format often suitable for Instruct GGUF models.
    # Some models might prefer specific formats (Alpaca, ChatML...).
    # Check the model's page on Hugging Face if needed.
    prompt = f"""Context:
---
{context_string}
---
Question: {query}

Answer based solely on the provided context:
"""
    # *** Fin de la modification ***

    print("\n  -> Prompt construit pour le LLM local (début):")
    print(prompt[:500] + "...")

    # 4. Générer la réponse avec le LLM local (si chargé)
    if llm_model:
        print("\n  -> Envoi de la requête au LLM local...")
        try:
            # Appel à llama-cpp-python pour la génération
            output = llm_model(
                prompt,
                max_tokens=300,  # Limite le nombre de tokens générés pour la réponse
                stop=["Question:", "\n", "Context:"], # Arrête la génération si le modèle commence à poser une autre question, saute une ligne ou répète le contexte
                echo=False      # Ne répète pas le prompt dans la sortie
            )
            # Extraire le texte de la réponse
            final_answer = output['choices'][0]['text'].strip()
            print("  -> Réponse reçue du LLM local.")
            return final_answer

        except Exception as e:
            print(f"  -> Erreur lors de la génération de la réponse par le LLM local: {e}")
            return "Désolé, une erreur s'est produite lors de la génération de la réponse par l'IA locale."
    else:
        print("\n  -> Le LLM local n'est pas chargé. Retour du contexte brut.")
        return f"Le LLM local n'est pas disponible. Voici le contexte trouvé:\n\n{context_string}"


# --- Boucle Principale pour poser des questions (inchangée) ---

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌍 SYSTÈME DE DÉTECTION DE FAKE NEWS CLIMATIQUES")
    print("Basé sur les sources: IPCC, Environmental Defense Fund")
    print("="*60)
    print("\nCommandes disponibles:")
    print("- 'analyze: [affirmation]' : Analyser une affirmation climatique")
    print("- 'question: [question]' : Poser une question générale sur le climat")
    print("- 'quit' ou 'exit' : Quitter")
    print("="*60)

    while True:
        user_input = input("\nVotre entrée: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        if not user_input.strip():
            continue

        # Déterminer le type de requête
        if user_input.lower().startswith('analyze:'):
            claim = user_input[8:].strip()  # Supprimer 'analyze:'
            if claim:
                analysis = analyze_climate_claim(claim)
                print("\n" + "="*50)
                print("📊 ANALYSE DE L'AFFIRMATION")
                print("="*50)
                print(analysis)
                print("="*50)
            else:
                print("Veuillez fournir une affirmation à analyser après 'analyze:'")
                
        elif user_input.lower().startswith('question:'):
            question = user_input[9:].strip()  # Supprimer 'question:'
            if question:
                answer = answer_query_rag(question)
                print("\n" + "="*50)
                print("💬 RÉPONSE")
                print("="*50)
                print(answer)
                print("="*50)
            else:
                print("Veuillez fournir une question après 'question:'")
        else:
            # Par défaut, traiter comme une analyse de fake news
            analysis = analyze_climate_claim(user_input)
            print("\n" + "="*50)
            print("📊 ANALYSE DE L'AFFIRMATION")
            print("="*50)
            print(analysis)
            print("="*50)

    print("\n🌍 Merci d'avoir utilisé le détecteur de fake news climatiques !")