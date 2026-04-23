import os
from pathlib import Path

import streamlit as st

from search import SearchEngine
from utils import extract_pdfs_from_folder


st.set_page_config(
    page_title="DocuLens - AI File Search",
    page_icon="🔎",
    layout="wide"
)


# -------- CUSTOM CSS --------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

.result-card {
    background-color: #161b22;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #30363d;
}

.file-title {
    font-size: 18px;
    font-weight: bold;
    color: #58a6ff;
}

.score-badge {
    background-color: #238636;
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
    margin-right: 10px;
}

.chunk-badge {
    background-color: #30363d;
    color: #c9d1d9;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
}

.preview-text {
    color: #c9d1d9;
    margin-top: 10px;
}

a {
    text-decoration: none;
    color: #58a6ff;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def build_search_engine(folder_path: str, folder_signature: tuple[str, ...]):
    documents = extract_pdfs_from_folder(folder_path)

    if not documents:
        raise ValueError("No readable PDF content found.")

    engine = SearchEngine()
    engine.index_documents(documents)
    return engine, documents


def get_folder_signature(folder_path: str) -> tuple[str, ...]:
    pdf_files = sorted(Path(folder_path).glob("*.pdf"))
    return tuple(f"{pdf.name}:{pdf.stat().st_mtime_ns}:{pdf.stat().st_size}" for pdf in pdf_files)


def main():
    # ---------- HEADER ----------
    st.markdown("## 🔎 DocuLens")
    st.caption("Smart semantic search across your PDFs")

    st.divider()

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("⚙️ Settings")

        folder_path = st.text_input(
            "📂 PDF Folder",
            placeholder="Enter folder path..."
        )

        top_k = st.slider(
            "📊 Results to show",
            min_value=1,
            max_value=10,
            value=5
        )

    # ---------- SEARCH BAR ----------
    query = st.text_input(
        "🔍 Search your files",
        placeholder="e.g. chemical equilibrium notes"
    )

    # ---------- VALIDATION ----------
    if not folder_path:
        st.warning("📁 Enter a folder path to begin")
        return

    if not os.path.isdir(folder_path):
        st.error("❌ Invalid folder path")
        return

    # ---------- LOAD DATA ----------
    try:
        with st.spinner("📚 Indexing documents..."):
            folder_signature = get_folder_signature(folder_path)
            engine, documents = build_search_engine(folder_path, folder_signature)

        col1, col2 = st.columns(2)
        col1.success(f"✅ {len(documents)} chunks indexed")
        col2.info(f"⚙️ Mode: {engine.backend_name}")

    except Exception as exc:
        st.error(f"Error: {exc}")
        return

    # ---------- SEARCH ----------
    if not query:
        st.info("💡 Enter a query to start searching")
        return

    try:
        results = engine.search(query, top_k=top_k)
    except Exception as exc:
        st.error(f"Search failed: {exc}")
        return

    if not results:
        st.warning("😕 No results found")
        return

    # ---------- RESULTS ----------
    st.divider()
    st.subheader("📄 Results")

    st.write(f"🔍 Found {len(results)} results")

    for i, result in enumerate(results, start=1):

        # Safe score
        try:
            score = f"{float(result['score']):.4f}"
        except:
            score = "N/A"

        file_path = result.get("file_path", "")

        with st.expander(f"{i}. 📄 {result['file_name']}"):

            col1, col2 = st.columns(2)
            col1.metric("Score", score)
            col2.metric("Chunk", result["chunk_index"])

            st.markdown(result["text_preview"], unsafe_allow_html=True)

            if file_path and os.path.exists(file_path):
                if st.button(f"📂 Open file", key=f"open_{i}"):
                    os.startfile(file_path)

if __name__ == "__main__":
    main()