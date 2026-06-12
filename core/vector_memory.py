import faiss
import numpy as np
import json
from openai import AzureOpenAI

# -----------------------------
# CONFIG (EMBEDDINGS MODEL)
# -----------------------------
client = AzureOpenAI(
    api_key="YOUR_KEY",
    api_version="YOUR_API_VERSION",
    azure_endpoint="YOUR_ENDPOINT"
)

EMBED_MODEL = "text-embedding-3-small"

# -----------------------------
# STORAGE
# -----------------------------
dimension = 1536
index = faiss.IndexFlatL2(dimension)

memory_store = []

# -----------------------------
# GET EMBEDDING
# -----------------------------
def get_embedding(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# -----------------------------
# ADD MEMORY
# -----------------------------
def add_memory(question, answer):
    text = f"Q: {question}\nA: {answer}"
    vector = get_embedding(text)

    index.add(np.array([vector]))
    memory_store.append(text)

# -----------------------------
# SEARCH MEMORY
# -----------------------------
def search_memory(query, k=3):

    if len(memory_store) == 0:
        return []

    query_vec = get_embedding(query)

    distances, indices = index.search(np.array([query_vec]), k)

    results = []

    for i in indices[0]:
        if i < len(memory_store):
            results.append(memory_store[i])

    return results

# -----------------------------
# CONTEXT BUILDER
# -----------------------------
def build_context(question):

    results = search_memory(question)

    return f"""
RELEVANT PAST KNOWLEDGE:
{results}

CURRENT QUESTION:
{question}
"""