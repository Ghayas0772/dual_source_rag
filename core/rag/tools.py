from core.rag.retriever import retrieve

def rag_tool(q):
    return retrieve(q)