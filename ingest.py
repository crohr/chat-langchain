"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle

from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import BSHTMLLoader
from dexem_loader import DexemLoader

def ingest_docs():
    """Get documents from web pages."""
    loader = DirectoryLoader('./sources', glob="**/*.html", show_progress=True, use_multithreading=True, loader_cls=DexemLoader)
    
    raw_documents = loader.load()
    print(len(raw_documents))
    print(raw_documents[0])
    for doc in raw_documents:
        print(doc.metadata)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
