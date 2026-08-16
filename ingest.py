"""Builds the Chroma store from the PDFs in data/"""

import argparse
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DATA_DIR = Path("data")
PERSIST_DIR = Path("chroma_db")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def embeddings():
    return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)


def build(data_dir=DATA_DIR, persist_dir=PERSIST_DIR, rebuild=False):
    if rebuild and persist_dir.exists():
        shutil.rmtree(persist_dir)

    pdfs = sorted(data_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs in {data_dir}/")

    pages = []
    for pdf in pdfs:
        loaded = PyPDFLoader(str(pdf)).load()
        print(f"{pdf.name}: {len(loaded)} pages")
        pages.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)
    print(f"{len(chunks)} chunks")

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings(),
        persist_directory=str(persist_dir),
    )
    print(f"Written to {persist_dir}/")
    return store


def load(persist_dir=PERSIST_DIR):
    if not Path(persist_dir).exists():
        raise SystemExit("No store yet. Run: python ingest.py")
    return Chroma(persist_directory=str(persist_dir), embedding_function=embeddings())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true",
                        help="wipe the existing store first")
    build(rebuild=parser.parse_args().rebuild)