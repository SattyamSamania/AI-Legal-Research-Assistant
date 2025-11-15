import os
import json
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


CHUNK_DIR = "backend/chunks/"
VECTOR_DB_DIR = "backend/vector_store/chroma/"


# Load all chunks

def load_all_chunks():
    categories = ["bare_acts", "case_laws", "government_regulations"]
    all_chunks = []

    for cat in categories:
        file_path = os.path.join(CHUNK_DIR, f"{cat}.json")
        print(f" Loading: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_chunks.extend(data)

    print(f" Total chunks loaded: {len(all_chunks)}")
    return all_chunks


#  Convert chunks → LangChain Document format

def convert_to_documents(chunks):
    docs = []
    for c in chunks:
        docs.append(
            Document(
                page_content=c["text"],
                metadata={
                    "source_file": c["source_file"],
                    "id": c["id"],
                    "category": c["category"]
                }
            )
        )
    return docs


#  Store Embeddings in ChromaDB

def store_embeddings():
    print("Generating embeddings + storing in ChromaDB...")

    chunks = load_all_chunks()
    documents = convert_to_documents(chunks)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vectordb = Chroma(
        collection_name="legal_documents",
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    vectordb.add_documents(documents)
    vectordb.persist()

    print(f"Embeddings successfully stored at: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    store_embeddings()
