"""
RAG System module
Handles RAG system creation and document loading
"""
import os
import json
import hashlib
import pickle
import ollama
from pathlib import Path
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document

from .config import (
    USE_LOCAL_EMBEDDINGS, EMBEDDING_MODEL,
    USE_GLM, GLM_API_KEY, GLM_MODEL, GLM_BASE_URL, GLM_TEMPERATURE, GLM_MAX_TOKENS,
    USE_OLLAMA, OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_NUM_PREDICT
)
from .llm_models import OllamaLLM, GLMLLM
from .embeddings import LocalEmbeddings

# Cache directory for FAISS vectorstores
CACHE_DIR = Path("./vectorstore_cache")
CACHE_DIR.mkdir(exist_ok=True)


def load_repomix_json(file_path):
    """Load and parse repomix JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []
        processed_files = 0

        # Handle different repomix JSON structures
        if isinstance(data, dict):
            if 'files' in data:
                # Standard repomix format
                print(f"📂 Processing repomix JSON with {len(data['files'])} files")
                for file_info in data['files']:
                    content = file_info.get('content', '')
                    path = file_info.get('path', 'unknown')

                    if content and content.strip():
                        doc = Document(
                            page_content=content,
                            metadata={'source': path, 'file_type': 'repomix'}
                        )
                        documents.append(doc)
                        processed_files += 1

            elif 'chunks' in data:
                # Alternative repomix format
                print(f"📂 Processing repomix JSON with {len(data['chunks'])} chunks")
                for chunk in data['chunks']:
                    content = chunk.get('content', '')
                    path = chunk.get('path', 'unknown')

                    if content and content.strip():
                        doc = Document(
                            page_content=content,
                            metadata={'source': path, 'file_type': 'repomix'}
                        )
                        documents.append(doc)
                        processed_files += 1

            else:
                # Single file in dict format
                content = data.get('content', '')
                path = data.get('path', data.get('filename', 'unknown'))
                if content and content.strip():
                    doc = Document(
                        page_content=content,
                        metadata={'source': path, 'file_type': 'repomix'}
                    )
                    documents.append(doc)
                    processed_files = 1

        elif isinstance(data, list):
            # List format
            print(f"📂 Processing repomix JSON list with {len(data)} items")
            for item in data:
                if isinstance(item, dict):
                    content = item.get('content', '')
                    path = item.get('path', item.get('file', 'unknown'))

                    if content and content.strip():
                        doc = Document(
                            page_content=content,
                            metadata={'source': path, 'file_type': 'repomix'}
                        )
                        documents.append(doc)
                        processed_files += 1

        else:
            # Try to treat as raw content
            content = str(data)
            if content.strip():
                doc = Document(
                    page_content=content,
                    metadata={'source': 'raw_data', 'file_type': 'repomix'}
                )
                documents.append(doc)
                processed_files = 1

        print(f"✅ Successfully processed {processed_files} files from repomix JSON")
        return documents

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        # Fallback: try to load as regular text file
        try:
            loader = TextLoader(file_path)
            return loader.load()
        except Exception as fallback_error:
            raise Exception(f"Failed to parse as JSON and failed to load as text: {fallback_error}")

    except Exception as e:
        print(f"⚠️ Error processing repomix JSON, falling back to text loader: {e}")
        # Fallback: try to load as regular text file
        try:
            loader = TextLoader(file_path)
            return loader.load()
        except Exception as fallback_error:
            raise Exception(f"Failed to process repomix JSON: {e}, fallback also failed: {fallback_error}")


def get_cache_key(file_path, embedding_model):
    """Generate cache key based on file content and configuration"""
    # Create hash from file content
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    # Combine with embedding model to ensure cache invalidation when model changes
    cache_key = f"{file_hash}_{embedding_model}"
    return cache_key


def get_cache_path(cache_key):
    """Get cache directory path for a given cache key"""
    return CACHE_DIR / cache_key


def load_cached_vectorstore(cache_key, embeddings):
    """Load cached FAISS vectorstore if exists"""
    cache_path = get_cache_path(cache_key)
    
    if not cache_path.exists():
        return None
    
    try:
        # Load metadata
        metadata_file = cache_path / "metadata.pkl"
        if not metadata_file.exists():
            print(f"⚠️ Cache metadata not found, will rebuild")
            return None
        
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        # Load FAISS vectorstore
        print(f"📦 Loading cached vectorstore from {cache_path}")
        vectorstore = FAISS.load_local(
            str(cache_path),
            embeddings,
            allow_dangerous_deserialization=True  # Required for FAISS.load_local
        )
        
        print(f"✅ Successfully loaded cached vectorstore with {metadata['num_chunks']} chunks")
        return vectorstore, metadata['num_chunks']
    
    except Exception as e:
        print(f"⚠️ Failed to load cache: {e}, will rebuild")
        return None


def save_vectorstore_cache(cache_key, vectorstore, num_chunks):
    """Save FAISS vectorstore to cache"""
    cache_path = get_cache_path(cache_key)
    
    try:
        # Create cache directory
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS vectorstore
        print(f"💾 Saving vectorstore to cache: {cache_path}")
        vectorstore.save_local(str(cache_path))
        
        # Save metadata
        metadata = {
            'num_chunks': num_chunks,
            'cache_key': cache_key
        }
        
        metadata_file = cache_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Successfully cached vectorstore with {num_chunks} chunks")
    
    except Exception as e:
        print(f"⚠️ Failed to save cache: {e}")


def create_rag_system(file_path):
    """Create RAG system from uploaded file with caching support"""
    try:
        # Determine embedding configuration
        embedding_model_name = EMBEDDING_MODEL if USE_LOCAL_EMBEDDINGS else "openai"
        
        # Generate cache key
        cache_key = get_cache_key(file_path, embedding_model_name)
        
        # Initialize embeddings (needed for both cache loading and new creation)
        if USE_LOCAL_EMBEDDINGS:
            print(f"🔧 Using local embeddings: {EMBEDDING_MODEL}")
            embeddings = LocalEmbeddings(EMBEDDING_MODEL)
        else:
            print("🔧 Using OpenAI embeddings")
            embeddings = OpenAIEmbeddings()
        
        # Try to load from cache
        cached_result = load_cached_vectorstore(cache_key, embeddings)
        
        if cached_result is not None:
            vectorstore, num_chunks = cached_result
            print(f"🚀 Using cached vectorstore - skipping document processing")
        else:
            # No cache found, process document from scratch
            print(f"🔄 No cache found, processing document...")
            
            # Determine file type and load accordingly
            if file_path.endswith('.md'):
                loader = UnstructuredMarkdownLoader(file_path)
                documents = loader.load()
            elif file_path.endswith('.json'):
                # Handle repomix JSON files
                documents = load_repomix_json(file_path)
            else:
                loader = TextLoader(file_path)
                documents = loader.load()

            # Validate documents
            if not documents:
                raise Exception("No documents found in the uploaded file")

            print(f"📄 Loaded {len(documents)} documents from {file_path}")

            # Split documents into chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)

            if not texts:
                raise Exception("No text chunks created from documents")

            print(f"🔤 Created {len(texts)} text chunks")
            num_chunks = len(texts)

            # Create embeddings and vector store
            print(f"⚙️ Creating FAISS vectorstore with embeddings...")
            vectorstore = FAISS.from_documents(texts, embeddings)
            
            # Save to cache
            save_vectorstore_cache(cache_key, vectorstore, num_chunks)

        # Create retriever (no LLM needed - agents will process raw context)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

        print(f"✅ RAG retriever ready (no LLM summarization - agents process raw context)")

        # Return retriever instead of qa_chain for faster, direct access to documents
        return retriever, num_chunks

    except Exception as e:
        raise Exception(f"Error creating RAG system: {str(e)}")

