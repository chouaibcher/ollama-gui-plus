"""
Document processing utilities for RAG functionality.
Supports PDF, TXT, DOCX, and other document formats.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import json
from datetime import datetime

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class DocumentProcessor:
    """Process documents for RAG functionality."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = ['.txt', '.md', '.py', '.js', '.html', '.css']
        
        if PDF_AVAILABLE:
            self.supported_formats.append('.pdf')
        if DOCX_AVAILABLE:
            self.supported_formats.append('.docx')
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return self.supported_formats.copy()
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from a file based on its format."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension == '.docx':
                return self._extract_from_docx(file_path)
            elif extension in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                return self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        except Exception as e:
            raise Exception(f"Error extracting text from {file_path.name}: {str(e)}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            raise Exception("PyPDF2 not installed. Please install with: pip install PyPDF2")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise Exception("python-docx not installed. Please install with: pip install python-docx")
        
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from plain text files."""
        encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        
        raise Exception(f"Could not decode file {file_path.name} with any supported encoding")
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split text into chunks for processing."""
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_data = {
                'text': chunk_text,
                'chunk_index': len(chunks),
                'word_count': len(chunk_words),
                'char_count': len(chunk_text),
                'metadata': metadata or {}
            }
            
            chunks.append(chunk_data)
        
        return chunks
    
    def process_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a document and return structured data."""
        file_path = Path(file_path)
        
        # Extract text
        text = self.extract_text_from_file(file_path)
        
        # Create document metadata
        doc_metadata = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'extension': file_path.suffix.lower(),
            'size_bytes': file_path.stat().st_size,
            'processed_at': datetime.now().isoformat(),
            'text_length': len(text),
            'word_count': len(text.split())
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Create chunks
        chunks = self.chunk_text(text, doc_metadata)
        
        # Create document hash for deduplication
        content_hash = hashlib.md5(text.encode()).hexdigest()
        doc_metadata['content_hash'] = content_hash
        
        return {
            'metadata': doc_metadata,
            'text': text,
            'chunks': chunks,
            'chunk_count': len(chunks)
        }


class DocumentStore:
    """Simple document store for managing processed documents."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            self.storage_dir = Path.home() / ".ollama-gui-plus" / "documents"
        else:
            self.storage_dir = Path(storage_dir)
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "document_index.json"
        self.processor = DocumentProcessor()
        
        # Load existing index
        self.document_index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load document index from file."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading document index: {e}")
        
        return {'documents': {}, 'last_updated': None}
    
    def _save_index(self):
        """Save document index to file."""
        try:
            self.document_index['last_updated'] = datetime.now().isoformat()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.document_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving document index: {e}")
    
    def add_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document to the store."""
        # Process the document
        doc_data = self.processor.process_document(file_path, metadata)
        
        # Check for duplicates
        content_hash = doc_data['metadata']['content_hash']
        if content_hash in self.document_index['documents']:
            existing_doc = self.document_index['documents'][content_hash]
            raise ValueError(f"Document already exists: {existing_doc['metadata']['filename']}")
        
        # Store document data
        doc_file = self.storage_dir / f"{content_hash}.json"
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.document_index['documents'][content_hash] = {
            'metadata': doc_data['metadata'],
            'storage_file': str(doc_file),
            'added_at': datetime.now().isoformat()
        }
        
        self._save_index()
        return content_hash
    
    def get_document(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get a document by its content hash."""
        if content_hash not in self.document_index['documents']:
            return None
        
        doc_info = self.document_index['documents'][content_hash]
        storage_file = doc_info['storage_file']
        
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading document {content_hash}: {e}")
            return None
    
    def remove_document(self, content_hash: str) -> bool:
        """Remove a document from the store."""
        if content_hash not in self.document_index['documents']:
            return False
        
        doc_info = self.document_index['documents'][content_hash]
        storage_file = Path(doc_info['storage_file'])
        
        try:
            if storage_file.exists():
                storage_file.unlink()
            
            del self.document_index['documents'][content_hash]
            self._save_index()
            return True
        except Exception as e:
            print(f"Error removing document {content_hash}: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the store."""
        documents = []
        for content_hash, doc_info in self.document_index['documents'].items():
            doc_summary = {
                'content_hash': content_hash,
                'filename': doc_info['metadata']['filename'],
                'size_bytes': doc_info['metadata']['size_bytes'],
                'word_count': doc_info['metadata']['word_count'],
                'added_at': doc_info['added_at']
            }
            documents.append(doc_summary)
        
        return sorted(documents, key=lambda x: x['added_at'], reverse=True)
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Simple text-based search through document chunks."""
        results = []
        query_lower = query.lower()
        
        for content_hash in self.document_index['documents']:
            doc_data = self.get_document(content_hash)
            if not doc_data:
                continue
            
            # Search through chunks
            for chunk in doc_data['chunks']:
                chunk_text = chunk['text'].lower()
                if query_lower in chunk_text:
                    # Calculate simple relevance score
                    relevance = chunk_text.count(query_lower) / len(chunk_text.split())
                    
                    result = {
                        'document_hash': content_hash,
                        'filename': doc_data['metadata']['filename'],
                        'chunk_index': chunk['chunk_index'],
                        'text': chunk['text'],
                        'relevance': relevance,
                        'metadata': chunk['metadata']
                    }
                    results.append(result)
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]
    
    def get_context_for_query(self, query: str, max_chunks: int = 3) -> str:
        """Get relevant context for a query."""
        search_results = self.search_documents(query, max_chunks)
        
        if not search_results:
            return ""
        
        context_parts = []
        for result in search_results:
            context_parts.append(f"[From: {result['filename']}]\n{result['text']}")
        
        return "\n\n---\n\n".join(context_parts)


# Global document store instance
document_store = DocumentStore()
