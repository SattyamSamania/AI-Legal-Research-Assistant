from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

VECTOR_DB_DIR = "backend/vector_store/chroma/"

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

db = Chroma(
    collection_name="legal_documents",
    embedding_function=embeddings,
    persist_directory=VECTOR_DB_DIR
)

query = "Define electronic signature according to the IT Act."
results = db.similarity_search(query, k=3)

print("\n QUERY:", query)
for i, r in enumerate(results):
    print("\n------------------------")
    print(f"Result #{i+1}")
    print("Text:", r.page_content[:300], "...")
    print("Metadata:", r.metadata)
