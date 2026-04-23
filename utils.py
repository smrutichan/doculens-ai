from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import re

from pypdf import PdfReader


def read_pdf_text(pdf_path: Path) -> str:
    """Read and combine text from all pages in a PDF file."""
    reader = PdfReader(str(pdf_path))
    pages: List[str] = []

    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except:
            text = ""

        if text.strip():
            pages.append(text)

    full_text = "\n".join(pages)

    # Extra cleaning (VERY IMPORTANT)
    full_text = re.sub(r"\s+", " ", full_text)  # normalize spaces
    full_text = re.sub(r"[^\x00-\x7F]+", " ", full_text)  # remove weird chars

    return full_text.strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 250,
    overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks.
    Overlap improves search accuracy significantly.
    """
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        if len(chunk_words) < 50:
            break  # ignore very small chunks

        chunk = " ".join(chunk_words).strip()
        chunks.append(chunk)

        # move forward with overlap
        start += (chunk_size - overlap)

    return chunks


def extract_pdfs_from_folder(folder_path: str) -> List[Dict[str, Any]]:
    """Read all PDFs in a folder and return searchable chunk records."""
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise ValueError("The provided folder path is invalid.")

    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        raise ValueError("No PDF files were found in the selected folder.")

    documents: List[Dict[str, Any]] = []

    for pdf_file in pdf_files:
        try:
            text = read_pdf_text(pdf_file)
        except Exception as exc:
            raise RuntimeError(f"Could not read {pdf_file.name}: {exc}") from exc

        chunks = split_text_into_chunks(text)

        # DEBUG (helps you understand what's happening)
        print(f"{pdf_file.name} → {len(chunks)} chunks")

        for chunk_index, chunk in enumerate(chunks, start=1):
            documents.append(
                                {
                                    "file_name": pdf_file.name,
                                    "file_path": str(pdf_file.resolve()),  # FULL PATH
                                    "chunk_index": chunk_index,
                                    "text": chunk,
                                }
            )

    return documents