### Pipeline in 5 steps :

1. **`climate_scraper.py`** - Collect authoritarive scientific articles
2. **`chunking.py`** - Smart chunking of the articles
3. **`embeddings.py`** - Vectorisation of the chunks 
4. **`vectorstore.py`** - Vectoriel database with ChromaDB
5. **`llm.py`** - Fact-checking llm using llama3 with a RAG system
## Installation

```bash

pip install -r requirements.txt

# you also need to download llama3 to run the rag (from huggingface)
```

## 🔧 Launch

```bash
# 1. Scrape
python climate_scraper.py

# 2. cut the chunk
python chunking.py

# 3. Create embeddings
python embeddings.py

# 4. Index in ChromaDB
python vectorstore.py

# 5. Launch the LLM interface
python llm.py
```

###  fact-checking :

```
 When you run `llm.py`, you can choose an article or every article
 However it takes around 10 minutes to check each article
```
