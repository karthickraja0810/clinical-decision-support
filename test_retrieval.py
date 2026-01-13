import chromadb
import os

DB_DIR = "vector_db"

client = chromadb.PersistentClient(
    path=os.path.abspath(DB_DIR)
)

collection = client.get_or_create_collection(name="medical_guidelines")


print("Number of documents in DB:", collection.count())

results = collection.query(
    query_texts=["elevated TSH with normal T4"],
    n_results=3
)

print("Retrieved documents:")
for doc in results["documents"][0]:
    print("-" * 40)
    print(doc[:500])
