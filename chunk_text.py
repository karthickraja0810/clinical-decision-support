import os
import json
import uuid

INPUT_ROOT = "extracted_text"
OUTPUT_ROOT = "chunks"

CHUNK_SIZE = 400      # words
CHUNK_OVERLAP = 80    # words

os.makedirs(OUTPUT_ROOT, exist_ok=True)

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        start = end - overlap
        if start < 0:
            start = 0

    return chunks

for root, dirs, files in os.walk(INPUT_ROOT):
    for file in files:
        if file.endswith(".txt"):
            input_path = os.path.join(root, file)

            # domain = folder name (diabetes, thyroid, etc.)
            domain = os.path.basename(root)

            output_folder = os.path.join(OUTPUT_ROOT, domain)
            os.makedirs(output_folder, exist_ok=True)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            if len(text.strip()) == 0:
                print(f"⚠️ Empty file skipped: {input_path}")
                continue

            chunks = chunk_text(text)

            chunk_records = []

            for idx, chunk in enumerate(chunks):
                record = {
                    "chunk_id": str(uuid.uuid4()),
                    "domain": domain,
                    "source_file": file,
                    "chunk_index": idx,
                    "text": chunk
                }
                chunk_records.append(record)

            output_file = file.replace(".txt", "_chunks.json")
            output_path = os.path.join(output_folder, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunk_records, f, indent=2)

            print(f"✅ Chunked: {input_path} → {output_path}")
