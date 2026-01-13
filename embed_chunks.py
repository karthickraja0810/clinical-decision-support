import os
import json
import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_ROOT = "chunks"
DB_DIR = "vector_db"

# Load embedding model (use ONLY this model)
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(
    path=os.path.abspath(DB_DIR)
)


collection = client.get_or_create_collection(
    name="medical_guidelines"
)

print("DEBUG: Embedding started")

for domain in os.listdir(CHUNKS_ROOT):
    domain_path = os.path.join(CHUNKS_ROOT, domain)

    if not os.path.isdir(domain_path):
        continue

    for file in os.listdir(domain_path):
        if file.endswith("_chunks.json"):
            file_path = os.path.join(domain_path, file)

            with open(file_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            for chunk in chunks:
                text = chunk["text"]

                embedding = model.encode(text).tolist()

                collection.add(
                    ids=[chunk["chunk_id"]],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[{
                        "domain": chunk["domain"],
                        "source_file": chunk["source_file"],
                        "chunk_index": chunk["chunk_index"]
                    }]
                )

            print(f"✅ Embedded: {domain}/{file}")


print("✅ Embedding completed & saved")
