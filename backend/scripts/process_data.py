import os
import re
import json
import pdfplumber
from typing import List


# Extract text from PDF
def extract_pdf_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text() or ""
            text += extracted + "\n"
    return text


# Clean text (remove noise, footnotes)
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)                        # collapse whitespace
    text = re.sub(r"\b\d+\.\s*Subs.*?\)", "", text)         # remove footnotes like "1. Subs. ..)"
    text = text.replace("-\n", "")
    return text.strip()


# Split BARE ACTS by numbered sections
def split_sections_bare_act(text: str):
    pattern = r"(?=\n?\s*\d+[A-Za-z]?\.\s)"  # e.g., 1. , 3A.
    sections = re.split(pattern, text)
    cleaned = []

    for sec in sections:
        sec = sec.strip()
        if len(sec) < 40:
            continue

        # Extract section number and title
        match = re.match(r"(\d+[A-Za-z]?)\.\s*(.*)", sec)
        if match:
            sec_num = match.group(1)
            sec_title = match.group(2).split(".")[0][:120]
        else:
            sec_num = None
            sec_title = None

        cleaned.append({
            "section_number": sec_num,
            "section_title": sec_title,
            "text": sec
        })

    return cleaned


# Split CASE LAWS & REGULATIONS by uppercase headings
def split_by_headings(text: str):
    pattern = r"(?=\n[A-Z][A-Z\s]{4,}\n)"  # e.g., BACKGROUND, JUDGMENT
    parts = re.split(pattern, text)

    chunks = []
    for part in parts:
        part = part.strip()
        if len(part) < 60:
            continue
        chunks.append({
            "section_number": None,
            "section_title": part.split("\n")[0][:120],
            "text": part
        })

    return chunks


# Chunk into smaller 1.8k char chunks
def chunk_text(text: str, max_chars=1800):
    sentences = re.split(r"(?<=[.?!])\s", text)
    result = []

    current = ""
    for s in sentences:
        if len(current) + len(s) <= max_chars:
            current += " " + s
        else:
            result.append(current.strip())
            current = s

    if current:
        result.append(current.strip())

    return result


# Process each category folder
def process_category(category: str):
    input_dir = f"backend/data/{category}"
    output_file = f"backend/chunks/{category}.json"
    os.makedirs("backend/chunks/", exist_ok=True)

    final_chunks = []

    for file in os.listdir(input_dir):
        if not file.endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_dir, file)
        print(f"Processing: {pdf_path}")

        raw = extract_pdf_text(pdf_path)
        clean = clean_text(raw)

        if category == "bare_acts":
            sections = split_sections_bare_act(clean)
        else:
            sections = split_by_headings(clean)

        # Chunk each section
        chunk_id = 0
        for sec in sections:
            small_chunks = chunk_text(sec["text"])
            for ch in small_chunks:
                final_chunks.append({
                    "id": f"{file.replace('.pdf','')}_chunk_{chunk_id}",
                    "text": ch,
                    "source_file": file,
                    "category": category,
                    "section_number": sec["section_number"],
                    "section_title": sec["section_title"]
                })
                chunk_id += 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=2)

    print(f"✔ Finished {category} | Total chunks: {len(final_chunks)}")


# MAIN
def main():
    categories = ["bare_acts", "case_laws", "government_regulations"]
    for cat in categories:
        process_category(cat)

    print("\n PHASE 2 COMPLETED — Clean chunks ready for embeddings!\n")


if __name__ == "__main__":
    main()
