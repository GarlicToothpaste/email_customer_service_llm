from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


WATCH_PATH = Path("./knowledge_base")

def index_folder(vectorstore):
    """Index files, skipping already-indexed ones"""
    files = list(WATCH_PATH.glob("*.pdf"))
    
    if not files:
        return "No Files in ./knowledge_base folder"
    
    total_chunks = 0

    for file in files:
        try:
            # Check if this file is already in the vectorstore
            existing = vectorstore.similarity_search(
                f"source:{file.name}", 
                k=1, 
                filter={"source": file.name}  # If your vectorstore supports metadata filtering
            )
            if existing:
                continue  # Skip already-indexed file
            
            if file.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file))

            docs = loader.load()
            if not docs: 
                continue
        
            # Add source metadata to each chunk
            for doc in docs:
                doc.metadata["source"] = file.name
        
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100
            )

            chunks = splitter.split_documents(docs)
            vectorstore.add_documents(chunks)
            total_chunks += len(chunks)

        except Exception as e:
            return f"Error Processing {file.name}: {str(e)}"
    
    return f"Indexed {len(files)} files -> {total_chunks} chunks"

