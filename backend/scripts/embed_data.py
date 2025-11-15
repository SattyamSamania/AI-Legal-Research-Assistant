import os
import json
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

CHUNK_DIR = "backend/chunks/"
VECTOR_DB_DIR = "backend/vector_store/chroma/"


# 1. Load chunks from chunk JSON files
def load_all_chunks():
    categories = ["bare_acts", "case_laws", "government_regulations"]
    all_chunks = []

    for cat in categories:
        chunk_file = os.path.join(CHUNK_DIR, f"{cat}.json")
        print(f" Loading chunks from: {chunk_file}")

        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        all_chunks.extend(chunks)

    print(f" Total chunks loaded: {len(all_chunks)}")
    return all_chunks


# 2. Convert JSON chunks → LangChain Document objects
def convert_to_documents(chunks):
    documents = []

    for c in chunks:
        documents.append(
            Document(
                page_content=c["text"],
                metadata={
                    "id": c["id"],
                    "source_file": c["source_file"],
                    "category": c["category"]
                }
            )
        )

    return documents


# 3. Generate embeddings + store inside ChromaDB
def store_embeddings():
    print(" Generating embeddings + storing into ChromaDB...")

    chunks = load_all_chunks()
    documents = convert_to_documents(chunks)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store = Chroma(
        collection_name="legal_documents",
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    vector_store.add_documents(documents)
    vector_store.persist()

    print(f" Embeddings stored successfully in: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    store_embeddings()
