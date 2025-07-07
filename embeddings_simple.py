#!/usr/bin/env python3
"""
Script pour créer les embeddings depuis les chunks JSON
Version simplifiée qui utilise directement le JSON de chunking.py
"""

import os
import json
from sentence_transformers import SentenceTransformer
import torch
import time

# --- Configuration ---
# Fichier contenant les chunks sauvegardés
INPUT_CHUNKS_FILE = "climate_chunks_data.json"
# Nom du modèle d'embedding à utiliser (depuis Hugging Face Hub)
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
# Fichier où sauvegarder les chunks avec leurs embeddings
OUTPUT_EMBEDDINGS_FILE = "climate_embeddings_data.json"

def load_chunks_from_json(chunks_file):
    """Charge les chunks depuis le fichier JSON créé par chunking.py."""
    print(f"📥 Chargement des chunks depuis: {chunks_file}")
    
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        print(f"✅ {len(chunks_data)} chunks chargés avec succès")
        return chunks_data
        
    except FileNotFoundError:
        print(f"❌ Fichier {chunks_file} non trouvé.")
        print("💡 Exécutez d'abord chunking.py pour créer les chunks.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erreur de format JSON dans {chunks_file}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None

def create_embeddings(chunks_data, model):
    """Crée les embeddings pour tous les chunks."""
    
    print(f"🧮 Création des embeddings pour {len(chunks_data)} chunks...")
    
    # Extraire juste les textes pour le batch processing
    texts = [chunk['text'] for chunk in chunks_data]
    
    try:
        # Traitement par batch pour efficacité
        batch_size = 32  # Ajustez selon votre mémoire
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            print(f"  📦 Batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)")
            
            # Créer les embeddings pour ce batch
            batch_embeddings = model.encode(
                batch_texts, 
                convert_to_tensor=False,
                show_progress_bar=False
            )
            
            # Convertir en listes pour la sérialisation JSON
            batch_embeddings_list = [emb.tolist() for emb in batch_embeddings]
            all_embeddings.extend(batch_embeddings_list)
        
        print(f"✅ Embeddings créés avec succès!")
        return all_embeddings
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des embeddings: {e}")
        return None

def save_embeddings_data(chunks_data, embeddings, output_file):
    """Sauvegarde les chunks avec leurs embeddings."""
    
    print(f"💾 Sauvegarde dans: {output_file}")
    
    try:
        # Combiner chunks et embeddings
        chunks_with_embeddings = []
        for i, chunk in enumerate(chunks_data):
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding['embedding'] = embeddings[i]
            chunks_with_embeddings.append(chunk_with_embedding)
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_with_embeddings, f, indent=2, ensure_ascii=False)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✅ Sauvegarde réussie! Taille: {file_size_mb:.1f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def main():
    """Fonction principale."""
    
    print("🌍 CRÉATION DES EMBEDDINGS CLIMATIQUES")
    print("="*50)
    
    # 1. Charger les chunks
    chunks_data = load_chunks_from_json(INPUT_CHUNKS_FILE)
    if not chunks_data:
        return
    
    # 2. Initialiser le modèle d'embedding
    print(f"\n🤖 Chargement du modèle: {MODEL_NAME}")
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔧 Utilisation du périphérique: {device.upper()}")
        
        model = SentenceTransformer(MODEL_NAME, device=device)
        print("✅ Modèle chargé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle: {e}")
        return
    
    # 3. Créer les embeddings
    start_time = time.time()
    embeddings = create_embeddings(chunks_data, model)
    
    if not embeddings:
        return
    
    elapsed_time = time.time() - start_time
    print(f"⏱️  Temps de traitement: {elapsed_time:.1f} secondes")
    
    # 4. Sauvegarder les résultats
    if save_embeddings_data(chunks_data, embeddings, OUTPUT_EMBEDDINGS_FILE):
        print(f"\n🎯 PROCHAINE ÉTAPE: python vectorstore.py")
        
        # Statistiques finales
        total_chunks = len(chunks_data)
        avg_time_per_chunk = elapsed_time / total_chunks
        embedding_dim = len(embeddings[0]) if embeddings else 0
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   🧩 Chunks traités: {total_chunks}")
        print(f"   📐 Dimension des embeddings: {embedding_dim}")
        print(f"   ⚡ Vitesse moyenne: {avg_time_per_chunk:.3f}s par chunk")
        print(f"   💾 Fichier de sortie: {OUTPUT_EMBEDDINGS_FILE}")

if __name__ == "__main__":
    main()
