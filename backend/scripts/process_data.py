import os
import re
import json
from pathlib import Path
import pdfplumber
from typing import List, Dict


# 1. Extract Text From PDF

def extract_pdf_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n\n"
    return text


# 2. Clean & Normalize Text

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"Page \d+ of \d+", "", text)
    text = re.sub(r"Page \d+", "", text)
    text = text.replace("-\n", "")
    text = text.strip()
    return text


# 3. Save Clean Text

def save_clean_text(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


# 4. Chunking (Legal-Aware)

def chunk_text(text: str, min_size=600, max_size=1200) -> List[str]:
    chunks = []
    current = ""

    sentences = re.split(r"(?<=[.?!])\s+", text)

    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


# 5. Process One Category (bare_acts/case_laws/etc)

def process_category(category: str):
    input_path = f"backend/data/{category}"
    output_text_path = f"backend/processed/{category}"
    output_chunk_file = f"backend/chunks/{category}.json"

    all_chunks = []

    for filename in os.listdir(input_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_path, filename)
            print(f"Processing: {pdf_path}")

            raw_text = extract_pdf_text(pdf_path)
            clean = clean_text(raw_text)

            # Save processed text
            clean_file = os.path.join(output_text_path, filename.replace(".pdf", ".txt"))
            save_clean_text(clean, clean_file)

            # Chunk the text
            chunks = chunk_text(clean)

            # Save metadata for citations later
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    "id": f"{filename.replace('.pdf', '')}_chunk_{idx}",
                    "text": chunk,
                    "source_file": filename,
                    "category": category
                })

    # Save chunks JSON
    os.makedirs("backend/chunks/", exist_ok=True)
    with open(output_chunk_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Completed category: {category}")
    print(f"Saved chunks: {output_chunk_file}")


# MAIN RUNNER

def main():
    categories = ["bare_acts", "case_laws", "government_regulations"]
    for cat in categories:
        process_category(cat)

    print("\nData processing complete! All cleaned text + chunks generated.\n")


if __name__ == "__main__":
    main()
