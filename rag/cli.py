#!/usr/bin/env python3
"""
RAG CLI Tool
Allows indexing and searching the codebase from the command line.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict

# Add the project root directory to sys.path to allow imports from rag package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.rag_system import create_rag_system

# Configuration
PROJECT_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
RAG_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CODEBASE_JSON_PATH = RAG_DIR / "codebase.json"

# Files and directories to ignore
IGNORE_DIRS = {
    '.git', '.venv', 'venv', 'node_modules', '__pycache__', 
    'dist', 'build', 'coverage', '.idea', '.vscode', 
    'rag', 'vectorstore_cache', 'uploads', 'logs', 'storage'
}
IGNORE_FILES = {
    '.DS_Store', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 
    'poetry.lock', 'Gemfile.lock', 'codebase.json', 'file_metadata.db'
}
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', 
    '.md', '.json', '.sh', '.yaml', '.yml', '.sql', '.rb', '.go', '.java', '.c', '.cpp'
}

def should_process(path: Path) -> bool:
    """Check if a file or directory should be processed"""
    if path.name in IGNORE_FILES:
        return False
    if path.name.startswith('.'):
        return False
    if path.is_dir():
        return path.name not in IGNORE_DIRS
    return path.suffix in ALLOWED_EXTENSIONS

def scan_codebase(root_dir: Path) -> List[Dict]:
    """Scan the codebase and return a list of file objects"""
    files_data = []
    
    print(f"🔍 Scanning codebase at: {root_dir}")
    
    for path in root_dir.rglob('*'):
        # Check if any parent directory is ignored
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
            
        if path.is_file() and should_process(path):
            try:
                # Skip files in the RAG directory itself to avoid recursion/bloat
                if RAG_DIR in path.parents:
                    continue
                    
                relative_path = path.relative_to(root_dir)
                
                try:
                    content = path.read_text(encoding='utf-8')
                    files_data.append({
                        "path": str(relative_path),
                        "content": content
                    })
                except UnicodeDecodeError:
                    # Skip binary files
                    pass
            except Exception as e:
                print(f"⚠️ Error processing {path}: {e}")
                
    print(f"✅ Found {len(files_data)} files")
    return files_data

def generate_codebase_json():
    """Generate codebase.json from the project files"""
    files = scan_codebase(PROJECT_ROOT)
    
    data = {
        "files": files
    }
    
    with open(CODEBASE_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"💾 Saved codebase to {CODEBASE_JSON_PATH}")
    return CODEBASE_JSON_PATH

def index_command():
    """Execute the index command"""
    print("🚀 Starting Indexing Process...")
    
    # 1. Generate codebase.json
    json_path = generate_codebase_json()
    
    # 2. Run RAG indexing
    print("🧠 Indexing content...")
    try:
        qa_chain, num_chunks = create_rag_system(str(json_path))
        print(f"✨ Indexing complete! Created {num_chunks} chunks.")
        print("💡 You can now query the codebase using: python rag/cli.py query 'your question'")
    except Exception as e:
        print(f"❌ Indexing failed: {e}")
        sys.exit(1)

def query_command(question: str):
    """Execute the query command"""
    if not CODEBASE_JSON_PATH.exists():
        print("❌ Codebase not indexed yet. Please run 'python rag/cli.py index' first.")
        sys.exit(1)
        
    try:
        # We pass the path to create_rag_system, which handles cache loading
        qa_chain, _ = create_rag_system(str(CODEBASE_JSON_PATH))
        
        print(f"\n❓ Question: {question}")
        print("⏳ Thinking...")
        
        result = qa_chain.invoke({"query": question})
        answer = result['result']
        
        print("\n🤖 Answer:")
        print("-" * 50)
        print(answer)
        print("-" * 50)
        
        # Show sources
        if 'source_documents' in result:
            print("\n📚 Sources:")
            for i, doc in enumerate(result['source_documents'][:3]):
                source = doc.metadata.get('source', 'unknown')
                print(f"  {i+1}. {source}")
                
    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)

def chat_command():
    """Execute the chat command"""
    if not CODEBASE_JSON_PATH.exists():
        print("❌ Codebase not indexed yet. Please run 'python rag/cli.py index' first.")
        sys.exit(1)
        
    try:
        print("🔄 Loading RAG system...")
        qa_chain, _ = create_rag_system(str(CODEBASE_JSON_PATH))
        
        print("\n💬 Interactive Chat Mode")
        print("Type 'exit', 'quit', or 'q' to stop.")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n👉 You: ").strip()
                if not question:
                    continue
                    
                if question.lower() in ('exit', 'quit', 'q'):
                    print("👋 Goodbye!")
                    break
                
                print("⏳ Thinking...")
                result = qa_chain.invoke({"query": question})
                print(f"\n🤖 AI: {result['result']}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="RAG Codebase Search CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Index command
    subparsers.add_parser('index', help='Scan and index the codebase')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Ask a question about the codebase')
    query_parser.add_argument('question', help='The question to ask')
    
    # Chat command
    subparsers.add_parser('chat', help='Start an interactive chat session')
    
    args = parser.parse_args()
    
    if args.command == 'index':
        index_command()
    elif args.command == 'query':
        query_command(args.question)
    elif args.command == 'chat':
        chat_command()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
