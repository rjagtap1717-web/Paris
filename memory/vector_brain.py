import os
import time
import hashlib
from pathlib import Path
import threading

# Point this to a subfolder so SQLite has a place to write
DB_PATH = Path(__file__).resolve().parent / "chroma_db"

_collection = None
_lock = threading.Lock()

def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
        
    try:
        with _lock:
            if _collection is not None:
                return _collection
                
            # Only import chromadb when first used to prevent slow startup times
            import chromadb
            from chromadb.config import Settings
            
            # Use PersistentClient to keep memory on disk
            client = chromadb.PersistentClient(
                path=str(DB_PATH),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # The default embedding function is sentence-transformers/all-MiniLM-L6-v2
            _collection = client.get_or_create_collection(name="paris_long_term_memory")
            return _collection
    except ImportError:
        print("[Vector Brain] Error: chromadb is not installed. Run 'pip install chromadb'")
        return None
    except Exception as e:
        print(f"[Vector Brain] Failed to initialize: {e}")
        return None

def store_fact(fact: str) -> str:
    """Stores a fact semantically in the vector DB."""
    col = _get_collection()
    if not col:
        return "[ERROR] Vector database is offline or not installed."
        
    fact_id = hashlib.md5(fact.encode()).hexdigest()
    
    try:
        col.add(
            documents=[fact],
            metadatas=[{"timestamp": time.time()}],
            ids=[fact_id]
        )
        return f"Fact memorized permanently: '{fact}'"
    except Exception as e:
        return f"[ERROR] Failed to store fact: {e}"

def search_facts(query: str, n_results: int = 3) -> list[str]:
    """Semantically searches the vector DB for relevant facts."""
    col = _get_collection()
    if not col:
        return []
        
    try:
        # Avoid querying if DB is totally empty
        if col.count() == 0:
            return []
            
        results = col.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []
    except Exception as e:
        print(f"[Vector Brain] Search failed: {e}")
        return []
