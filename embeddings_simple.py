import os
import json
from sentence_transformers import SentenceTransformer
import torch
import time


INPUT_CHUNKS_FILE = "climate_chunks_data.json"
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
OUTPUT_EMBEDDINGS_FILE = "climate_embeddings_data.json"

def load_chunks_from_json(chunks_file):
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)

    print(f"✅ {len(chunks_data)} chunks chargés avec succès")
    return chunks_data

def create_embeddings(chunks_data, model):
    texts = [chunk['text'] for chunk in chunks_data]
    batch_size = 32
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size

        batch_embeddings = model.encode(
            batch_texts,
            convert_to_tensor=False,
            show_progress_bar=False
        )

        batch_embeddings_list = [emb.tolist() for emb in batch_embeddings]
        all_embeddings.extend(batch_embeddings_list)

    return all_embeddings


def save_embeddings_data(chunks_data, embeddings, output_file):
    chunks_with_embeddings = []

    for i, chunk in enumerate(chunks_data):
        chunk_with_embedding = chunk.copy()
        chunk_with_embedding['embedding'] = embeddings[i]
        chunks_with_embeddings.append(chunk_with_embedding)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_with_embeddings, f, indent=2, ensure_ascii=False)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    return True

def main():


    chunks_data = load_chunks_from_json(INPUT_CHUNKS_FILE)


    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer(MODEL_NAME, device=device)
    start_time = time.time()
    embeddings = create_embeddings(chunks_data, model)

    

    save_embeddings_data(chunks_data, embeddings, OUTPUT_EMBEDDINGS_FILE)


if __name__ == "__main__":
    main()
