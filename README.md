# AI-Legal-Research-Assistant

An AI-powered legal research assistant using multi-agent reasoning and RAG to provide evidence-linked responses from Bare Acts(statutes) and judgments.

---

## Overview

Before the AI system can answer legal questions, all legal documents are:

1. **Collected** (PDFs of bare acts, case laws, government regulations)
2. **Converted into clean text**
3. **Split into smaller chunks** for embeddings
4. **Stored as JSON** with metadata (source, category, id)

This pipeline is implemented in:

```
backend/scripts/process_data.py
```

---

Requirements:

- At least **5 Publicly accessible Bare Acts for IT domain**
- At least **5 Case Laws for required domain**
- A few **relevant government regulations**

These PDFs are the raw data source.

---

## Text Extraction

The script uses **pdfplumber** to extract text from each PDF:

- Reads every page
- Extracts text
- Concatenates everything into one large string per document

This step converts unreadable PDFs → raw text.

---

## Text Cleaning

Raw extracted text usually contains noise like:

- Page numbers
- Headers/footers
- Weird spacing
- Hyphenated broken words

The cleaning function:

- Normalizes whitespace
- Removes page markers
- Fixes hyphenation
- Produces readable, continuous text

Cleaned text is saved here:

```
backend/processed/bare_acts/*.txt
backend/processed/case_laws/*.txt
backend/processed/regulations/*.txt
```

These `.txt` files help verify extraction quality.

---

## Chunking (Preparing for RAG)

Large documents cannot be embedded directly.  
The script splits each cleaned text into **smaller, meaningful chunks**.

Chunking uses:

- Sentence-aware splitting
- Min/max character size (e.g., 600–1200 chars)

Each chunk represents a self-contained piece of information suitable for retrieval.

---

## JSON Generation

All chunks are structured into a final JSON format:

Example entry:

```json
{
  "id": "IT_Act_2000_chunk_0",
  "text": "Section 66A...",
  "source_file": "IT_Act_2000.pdf",
  "category": "bare_acts"
}
```

Each Category produces:

```
backend/chunks/
    ├── bare_acts.json
    ├── case_laws.json
    └── government_regulations.json
```

---

## Loading Preprocessed Text Chunks

We load already chunked legal text from:

- Bare Acts

- Case Laws

- Government Regulations

These are stored as .json files containing:

```
{
  "text": "...chunk...",
  "metadata": { "source_file": "...", "id": "...", "category": "..." }
}
```

---

## Embeddings Generation (OpenAI)

We use:

OpenAI Embeddings: text-embedding-3-small

```
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

Why this model?

- Lightweight

- Fast

- Very cheap

- High quality for semantic search

---

## Vector Store Setup, ChromaDB (new langchain-chroma package)

Vectors + metadata stored in:

```
backend/vector_store/chroma/
```

Using:

```
from langchain_chroma import Chroma
```

Chroma automatically:

- stores embeddings

- persists database

- reloads on next run

## Query Testing

`test_query.py` allows:

- load vector DB

- embed the query

- perform similarity search

- print retrieved chunks + metadata

Output example:

```
Result #1
Text: ....
Metadata: { "source_file": "...", "category": "...", "id": "..." }
```

## Run embeddings generation

`python backend/scripts/embed_data.py`

Expected:

```
Total chunks: 3009
Embeddings stored successfully in backend/vector_store/chroma/
```

## Run query test

`python backend/scripts/test_query.py`
