"""
File Manager Module
Handles file metadata tracking and management using SQLite
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# Database file path
DB_PATH = Path("./file_metadata.db")


def init_database():
    """Initialize SQLite database with files table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL UNIQUE,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            cache_key TEXT,
            num_chunks INTEGER,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_upload_time 
        ON uploaded_files(upload_time DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_active 
        ON uploaded_files(is_active)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def add_file(
    original_filename: str,
    stored_filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    cache_key: str = None,
    num_chunks: int = None
) -> int:
    """
    Add new file metadata to database
    
    Returns:
        file_id: ID of the inserted file
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO uploaded_files 
            (original_filename, stored_filename, file_path, file_size, file_type, cache_key, num_chunks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (original_filename, stored_filename, file_path, file_size, file_type, cache_key, num_chunks))
        
        file_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Added file metadata: {original_filename} (ID: {file_id})")
        return file_id
    
    except sqlite3.IntegrityError:
        # File already exists, update instead
        cursor.execute("""
            UPDATE uploaded_files 
            SET original_filename = ?, file_path = ?, file_size = ?, 
                file_type = ?, cache_key = ?, num_chunks = ?, 
                upload_time = CURRENT_TIMESTAMP, is_active = 1
            WHERE stored_filename = ?
        """, (original_filename, file_path, file_size, file_type, cache_key, num_chunks, stored_filename))
        
        cursor.execute("SELECT id FROM uploaded_files WHERE stored_filename = ?", (stored_filename,))
        file_id = cursor.fetchone()[0]
        conn.commit()
        print(f"✅ Updated file metadata: {original_filename} (ID: {file_id})")
        return file_id
    
    finally:
        conn.close()


def get_all_files(active_only: bool = True) -> List[Dict]:
    """
    Get all uploaded files
    
    Args:
        active_only: If True, only return active (not deleted) files
    
    Returns:
        List of file metadata dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute("""
            SELECT * FROM uploaded_files 
            WHERE is_active = 1 
            ORDER BY upload_time DESC
        """)
    else:
        cursor.execute("""
            SELECT * FROM uploaded_files 
            ORDER BY upload_time DESC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        files.append({
            'id': row['id'],
            'original_filename': row['original_filename'],
            'stored_filename': row['stored_filename'],
            'file_path': row['file_path'],
            'file_size': row['file_size'],
            'file_type': row['file_type'],
            'cache_key': row['cache_key'],
            'num_chunks': row['num_chunks'],
            'upload_time': row['upload_time'],
            'last_used': row['last_used'],
            'is_active': row['is_active']
        })
    
    return files


def get_file_by_id(file_id: int) -> Optional[Dict]:
    """Get file metadata by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM uploaded_files WHERE id = ? AND is_active = 1", (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'original_filename': row['original_filename'],
            'stored_filename': row['stored_filename'],
            'file_path': row['file_path'],
            'file_size': row['file_size'],
            'file_type': row['file_type'],
            'cache_key': row['cache_key'],
            'num_chunks': row['num_chunks'],
            'upload_time': row['upload_time'],
            'last_used': row['last_used'],
            'is_active': row['is_active']
        }
    
    return None


def update_last_used(file_id: int):
    """Update last_used timestamp when file is selected"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE uploaded_files 
        SET last_used = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (file_id,))
    
    conn.commit()
    conn.close()


def delete_file(file_id: int, physical_delete: bool = False) -> bool:
    """
    Delete file (soft delete by default)
    
    Args:
        file_id: ID of the file to delete
        physical_delete: If True, also delete physical file and cache
    
    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get file info first
        cursor.execute("SELECT * FROM uploaded_files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        if physical_delete:
            # Delete physical file
            file_path = row[3]  # file_path column
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted physical file: {file_path}")
            
            # Delete cache directory
            cache_key = row[6]  # cache_key column
            if cache_key:
                from pathlib import Path
                import shutil
                cache_dir = Path("./vectorstore_cache") / cache_key
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                    print(f"🗑️ Deleted cache: {cache_dir}")
            
            # Delete from database
            cursor.execute("DELETE FROM uploaded_files WHERE id = ?", (file_id,))
        else:
            # Soft delete
            cursor.execute("UPDATE uploaded_files SET is_active = 0 WHERE id = ?", (file_id,))
        
        conn.commit()
        print(f"✅ Deleted file (ID: {file_id})")
        return True
    
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return False
    
    finally:
        conn.close()


def get_storage_stats() -> Dict:
    """Get storage statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total files
    cursor.execute("SELECT COUNT(*) FROM uploaded_files WHERE is_active = 1")
    total_files = cursor.fetchone()[0]
    
    # Total size
    cursor.execute("SELECT SUM(file_size) FROM uploaded_files WHERE is_active = 1")
    total_size = cursor.fetchone()[0] or 0
    
    # Total chunks
    cursor.execute("SELECT SUM(num_chunks) FROM uploaded_files WHERE is_active = 1")
    total_chunks = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_files': total_files,
        'total_size': total_size,
        'total_chunks': total_chunks
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_datetime(dt_string: str) -> str:
    """Format datetime string to human readable format"""
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string


# Initialize database on module import
init_database()

