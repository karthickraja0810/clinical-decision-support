# retrieval.py

import os

# chromadb is an optional runtime dependency; if unavailable, provide a safe
# fallback so the reasoning layer can still be executed for testing/local runs.
try:
    import chromadb

    def retrieve_guidelines(query, domain, n_results=3):
        client = chromadb.PersistentClient(
            path=os.path.abspath("vector_db")
        )

        collection = client.get_collection("medical_guidelines")

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"domain": domain}
        )

        # Return first document or empty string if none
        return results.get("documents", [[]])[0]

except Exception:
    # Fallback when chromadb isn't installed or vector DB isn't present.
    def retrieve_guidelines(query, domain, n_results=3):
        return []
