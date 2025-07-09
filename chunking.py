import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter


INPUT_DIR = "climate_facts_content"

OUTPUT_CHUNKS_FILE = "climate_chunks_data.json"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", ", ", " ", ""]
)


all_chunks = []


try:
    txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]

    if not txt_files:
        print("no file found")
        exit()

    total_files = len(txt_files)

    for i, filename in enumerate(txt_files):
        filepath = os.path.join(INPUT_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()

        if not file_content.strip():
            continue

        chunks = text_splitter.split_text(file_content)
        num_chunks = len(chunks)
        print(f" split in {num_chunks} chunks")

        for j, chunk in enumerate(chunks):
            chunk_id = f"{filename}_{i+1}_{j+1}"
            all_chunks.append({
                "id": chunk_id,
                "source": filename,
                "text": chunk,
                "chunk_index": j,
                "total_chunks_in_file": num_chunks
            })

    with open(OUTPUT_CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    total_chars = sum(len(chunk['text']) for chunk in all_chunks)
    avg_chunk_size = total_chars / len(all_chunks) if all_chunks else 0



except FileNotFoundError:
    print(f"no input folder found")
