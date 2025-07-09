import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
import torch
from llama_cpp import Llama
import fitz

PERSIST_DIRECTORY = "chroma_db_climate_facts"
COLLECTION_NAME = "climate_facts_chunks"
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
NUM_RESULTS_TO_RETRIEVE = 7
PDF_PATH = "climate_articles.pdf"
ANALYSIS_OUTPUT_DIR = "result"

MODEL_PATH = "/home/benoit_v/Documents/models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"


N_GPU_LAYERS = 0 # 0 for only cpu
N_CTX = 8192
N_BATCH = 512

#embeddings
device_embed = 'cuda' if torch.cuda.is_available() and N_GPU_LAYERS > 0 else 'cpu'
embedding_model = SentenceTransformer(MODEL_NAME, device=device_embed)



#chromadb
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection(name=COLLECTION_NAME)



llm_model = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=N_GPU_LAYERS,
    n_ctx=N_CTX,
    n_batch=N_BATCH,
    verbose=False
)


def load_and_split_articles(pdf_path: str) -> list[dict]:
    articles = []
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

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
    return articles


def analyze_article(article: dict):
    search_query = article['title'] + "\n" + " ".join(article['text'].split()[:100])
    query_embedding = embedding_model.encode(search_query, device=device_embed).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=NUM_RESULTS_TO_RETRIEVE,
        include=['documents']
    )
    context_chunks = results.get('documents', [[]])[0]
    context_string = "\n\n---\n\n".join(context_chunks)

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
    print("  analyzing")
    output = llm_model(
        prompt,
        max_tokens=800,
        stop=["<|eot_id|>", "<|end_of_text|>"],
        temperature=0.1,
        echo=False
    )
    analysis = output['choices'][0]['text'].strip()
    return analysis



def save_analysis_to_file(filename: str, content: str):
    if not os.path.exists(ANALYSIS_OUTPUT_DIR):
        os.makedirs(ANALYSIS_OUTPUT_DIR)
    filepath = os.path.join(ANALYSIS_OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)




if __name__ == "__main__":
    articles = load_and_split_articles(PDF_PATH)

    while True:
        for article in articles:
            print(f"  {article['number']}: {article['title']}")
        print("  'all': analyse every article")
        print("Enter the number of the article you want to test, 'all', or 'quit'.")

        user_input = input("\ninput : ")

        if user_input.lower() in ['quit', 'exit']:
            break

        if user_input.lower() == 'all':
            for article in articles:
                analysis_result = analyze_article(article)
                header = f"🔎 Result of article number {article['number']}: {article['title']}"


                print("\n")
                print(header)
                print(analysis_result)


                filename = f"analyse_article_{article['number']}.txt"
                file_content = f"{header}\n\n{analysis_result}"
                save_analysis_to_file(filename, file_content)

            continue

        try:
            choice = int(user_input)
            selected_article = next((a for a in articles if a['number'] == choice), None)

            if selected_article:
                analysis_result = analyze_article(selected_article)
                header = f"result of the article {selected_article['number']}: {selected_article['title']}"

                print("\n")
                print(header)
                print(analysis_result)

                filename = f"analyse_article_{selected_article['number']}.txt"
                file_content = f"{header}\n\n{analysis_result}"
                save_analysis_to_file(filename, file_content)
            else:
                print(f"no valid number")

        except ValueError:
            print("no valid input")

    print("end")
