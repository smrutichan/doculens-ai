# 🔎 DocuLens  
### AI-Powered Semantic Search for PDFs

DocuLens is a smart document search engine that enables users to find relevant information across multiple PDFs using **semantic understanding**, not just keyword matching.

---

## ❗ Problem Statement

Searching for specific information within multiple PDF documents is often inefficient and frustrating.  
Traditional search methods rely on exact keyword matching, which fails when the wording differs from the query.  

This becomes especially challenging for:
- Students navigating large sets of notes and textbooks  
- Researchers dealing with multiple documents  
- Users trying to quickly locate specific concepts or topics  

As a result, users spend significant time manually scanning documents to find relevant information.

## 🚀 Overview

DocuLens solves this by using **AI-based semantic search** to retrieve the most relevant content from documents.

---

## ✨ Features

- 🔍 **Semantic Search** using Sentence Transformers  
- ⚡ **TF-IDF Fallback** for reliability  
- 📄 **Chunk-based Indexing** for efficient retrieval  
- 🎯 **Relevance Ranking** (semantic + keyword frequency)  
- 🖍️ **Highlighted Results** for better readability  
- 📂 **Direct PDF Access** (opens at relevant page)  
- ⚡ **Caching for Faster Performance**  

---

## 🧠 How It Works

1. PDFs are read and split into smaller chunks  
2. Each chunk is converted into vector embeddings  
3. User query is also converted into an embedding  
4. Similarity scores are computed  
5. Results are ranked and displayed with highlights  

---

## 🛠️ Tech Stack

| Category | Tools |
|--------|------|
| Language | Python |
| UI | Streamlit |
| NLP | Sentence Transformers |
| Fallback Search | Scikit-learn (TF-IDF) |
| PDF Processing | PyPDF |
| Computation | NumPy |

---

## 🧪 Example Use Cases
- Searching through study notes
- Finding specific topics in textbooks
- Quickly locating concepts across multiple PDFs
- Academic and research document exploration

---

## 📸 Demo

(Add your demo video or GIF here)

---

## 🚀 Future Improvements
- 💬 Chat with PDFs (LLM integration)
- ⚡ Faster search using FAISS / vector DB
- 📊 Better ranking & summarization
- 🌐 Web deployment
