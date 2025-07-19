"""
Document management view for RAG functionality.
Provides UI for uploading, managing, and searching documents.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from typing import List, Dict, Any, Optional
from ..utils.document_processor import document_store
from ..utils.modern_theme_manager import theme_manager


class DocumentManagementView:
    """Document management interface for RAG functionality."""
    
    def __init__(self, parent):
        self.parent = parent
        self.window: Optional[tk.Toplevel] = None
        self.document_tree: Optional[ttk.Treeview] = None
        self.search_var = tk.StringVar()
        self.search_results_text: Optional[tk.Text] = None
        
    def show_window(self):
        """Show the document management window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("📄 Document Management - RAG Context")
        self.window.geometry("900x700")
        
        # Apply theme
        if theme_manager.is_dark_mode():
            self.window.configure(bg='#2D2D2D')
        else:
            self.window.configure(bg='#FFFFFF')
        
        # Center window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._refresh_document_list()
    
    def _create_widgets(self):
        """Create the UI widgets."""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Documents tab
        docs_frame = ttk.Frame(notebook)
        notebook.add(docs_frame, text="📂 Documents")
        self._create_documents_tab(docs_frame)
        
        # Search tab
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="🔍 Search")
        self._create_search_tab(search_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        self._create_settings_tab(settings_frame)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="➕ Upload Document",
            command=self._upload_document
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="🗑️ Remove Selected",
            command=self._remove_selected_document
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self._refresh_document_list
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="❌ Close",
            command=self.window.destroy
        ).pack(side='right')
    
    def _create_documents_tab(self, parent):
        """Create the documents management tab."""
        # Info label
        info_label = ttk.Label(
            parent,
            text="Upload documents (PDF, TXT, DOCX, etc.) to provide context for your conversations.",
            font=('TkDefaultFont', 9)
        )
        info_label.pack(anchor='w', pady=(0, 10))
        
        # Document list frame
        list_frame = ttk.LabelFrame(parent, text="Uploaded Documents")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview for documents
        columns = ('filename', 'size', 'word_count', 'added_at')
        self.document_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.document_tree.heading('filename', text='Filename')
        self.document_tree.heading('size', text='Size')
        self.document_tree.heading('word_count', text='Words')
        self.document_tree.heading('added_at', text='Added')
        
        self.document_tree.column('filename', width=300)
        self.document_tree.column('size', width=100)
        self.document_tree.column('word_count', width=100)
        self.document_tree.column('added_at', width=150)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.document_tree.yview)
        self.document_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.document_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')
        
        # Bind double-click to view document
        self.document_tree.bind('<Double-1>', self._view_document_details)
        
        # Status label
        self.status_label = ttk.Label(parent, text="Ready")
        self.status_label.pack(anchor='w', pady=(5, 0))
    
    def _create_search_tab(self, parent):
        """Create the search tab."""
        # Search frame
        search_frame = ttk.LabelFrame(parent, text="Search Documents")
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_input_frame, text="Query:").pack(side='left')
        
        search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=(10, 5))
        search_entry.bind('<Return>', lambda e: self._search_documents())
        
        ttk.Button(
            search_input_frame,
            text="🔍 Search",
            command=self._search_documents
        ).pack(side='left')
        
        # Results frame
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill='both', expand=True)
        
        # Results text widget
        self.search_results_text = tk.Text(
            results_frame,
            wrap='word',
            height=15,
            font=('Consolas', 10)
        )
        
        results_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=self.search_results_text.yview)
        self.search_results_text.configure(yscrollcommand=results_scroll.set)
        
        self.search_results_text.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        results_scroll.pack(side='right', fill='y', pady=10, padx=(0, 10))
        
        # Apply theme to text widget
        theme_manager.style_tk_widget(self.search_results_text, "text")
    
    def _create_settings_tab(self, parent):
        """Create the settings tab."""
        # Supported formats info
        formats_frame = ttk.LabelFrame(parent, text="Supported Document Formats")
        formats_frame.pack(fill='x', pady=(0, 10))
        
        supported_formats = document_store.processor.get_supported_formats()
        formats_text = ", ".join(supported_formats)
        
        ttk.Label(
            formats_frame,
            text=f"Supported: {formats_text}",
            wraplength=600
        ).pack(anchor='w', padx=10, pady=10)
        
        # Processing settings
        settings_frame = ttk.LabelFrame(parent, text="Processing Settings")
        settings_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(settings_frame, text=f"Chunk Size: {document_store.processor.chunk_size} words").pack(anchor='w', padx=10, pady=5)
        ttk.Label(settings_frame, text=f"Chunk Overlap: {document_store.processor.chunk_overlap} words").pack(anchor='w', padx=10, pady=5)
        
        # Storage info
        storage_frame = ttk.LabelFrame(parent, text="Storage Information")
        storage_frame.pack(fill='x', pady=(0, 10))
        
        storage_path = str(document_store.storage_dir)
        ttk.Label(storage_frame, text=f"Storage Location: {storage_path}").pack(anchor='w', padx=10, pady=5)
        
        # Dependencies info
        deps_frame = ttk.LabelFrame(parent, text="Optional Dependencies")
        deps_frame.pack(fill='x')
        
        deps_info = []
        try:
            import PyPDF2
            deps_info.append("✅ PyPDF2 - PDF support available")
        except ImportError:
            deps_info.append("❌ PyPDF2 - Install for PDF support: pip install PyPDF2")
        
        try:
            from docx import Document
            deps_info.append("✅ python-docx - DOCX support available")
        except ImportError:
            deps_info.append("❌ python-docx - Install for DOCX support: pip install python-docx")
        
        for info in deps_info:
            ttk.Label(deps_frame, text=info).pack(anchor='w', padx=10, pady=2)
    
    def _upload_document(self):
        """Upload a new document."""
        supported_formats = document_store.processor.get_supported_formats()
        
        # Create file types for dialog
        file_types = [("All Supported", " ".join(f"*{fmt}" for fmt in supported_formats))]
        file_types.extend([(f"{fmt.upper()} files", f"*{fmt}") for fmt in supported_formats])
        file_types.append(("All files", "*.*"))
        
        file_path = filedialog.askopenfilename(
            title="Select Document to Upload",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.configure(text="Processing document...")
            self.window.update()
            
            # Process and add document
            content_hash = document_store.add_document(file_path)
            
            self.status_label.configure(text=f"Successfully added document: {content_hash[:8]}...")
            self._refresh_document_list()
            
            messagebox.showinfo(
                "Success",
                f"Document '{file_path.split('/')[-1]}' has been successfully processed and added to the knowledge base."
            )
            
        except ValueError as e:
            # Duplicate document
            messagebox.showwarning("Duplicate Document", str(e))
            self.status_label.configure(text="Document already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process document: {str(e)}")
            self.status_label.configure(text="Error processing document")
    
    def _remove_selected_document(self):
        """Remove the selected document."""
        selection = self.document_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a document to remove.")
            return
        
        item = selection[0]
        filename = self.document_tree.item(item, 'values')[0]
        
        response = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove '{filename}' from the knowledge base?"
        )
        
        if response:
            try:
                # Get content hash from item
                content_hash = self.document_tree.item(item, 'tags')[0] if self.document_tree.item(item, 'tags') else None
                
                if content_hash and document_store.remove_document(content_hash):
                    self.status_label.configure(text=f"Removed document: {filename}")
                    self._refresh_document_list()
                    messagebox.showinfo("Success", f"Document '{filename}' has been removed.")
                else:
                    messagebox.showerror("Error", "Failed to remove document.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove document: {str(e)}")
    
    def _refresh_document_list(self):
        """Refresh the document list."""
        # Clear existing items
        for item in self.document_tree.get_children():
            self.document_tree.delete(item)
        
        # Add documents
        documents = document_store.list_documents()
        for doc in documents:
            # Format size
            size_mb = doc['size_bytes'] / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{doc['size_bytes']} B"
            
            # Format date
            added_date = doc['added_at'][:10]  # Just the date part
            
            self.document_tree.insert(
                '',
                'end',
                values=(doc['filename'], size_str, doc['word_count'], added_date),
                tags=(doc['content_hash'],)
            )
        
        # Update status
        count = len(documents)
        self.status_label.configure(text=f"{count} document{'s' if count != 1 else ''} in knowledge base")
    
    def _view_document_details(self, event):
        """View details of the selected document."""
        selection = self.document_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        content_hash = self.document_tree.item(item, 'tags')[0] if self.document_tree.item(item, 'tags') else None
        
        if not content_hash:
            return
        
        doc_data = document_store.get_document(content_hash)
        if not doc_data:
            messagebox.showerror("Error", "Document data not found.")
            return
        
        # Create details window
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Document Details - {doc_data['metadata']['filename']}")
        details_window.geometry("600x500")
        
        # Apply theme
        if theme_manager.is_dark_mode():
            details_window.configure(bg='#2D2D2D')
        else:
            details_window.configure(bg='#FFFFFF')
        
        # Create text widget with document info
        text_widget = tk.Text(details_window, wrap='word', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(details_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Apply theme
        theme_manager.style_tk_widget(text_widget, "text")
        
        # Add document information
        metadata = doc_data['metadata']
        info_text = f"""Document: {metadata['filename']}
File Path: {metadata['filepath']}
Size: {metadata['size_bytes']} bytes
Word Count: {metadata['word_count']}
Processed: {metadata['processed_at']}
Chunks: {doc_data['chunk_count']}

--- Document Content Preview ---

{doc_data['text'][:2000]}{'...' if len(doc_data['text']) > 2000 else ''}
"""
        
        text_widget.insert('1.0', info_text)
        text_widget.configure(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
    
    def _search_documents(self):
        """Search through documents."""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query.")
            return
        
        try:
            results = document_store.search_documents(query, max_results=10)
            
            # Clear previous results
            self.search_results_text.delete('1.0', tk.END)
            
            if not results:
                self.search_results_text.insert('1.0', f"No results found for: {query}")
                return
            
            # Display results
            result_text = f"Search Results for: '{query}'\n"
            result_text += "=" * 50 + "\n\n"
            
            for i, result in enumerate(results, 1):
                result_text += f"{i}. From: {result['filename']}\n"
                result_text += f"   Relevance: {result['relevance']:.3f}\n"
                result_text += f"   Chunk: {result['chunk_index']}\n"
                result_text += f"   Text: {result['text'][:300]}{'...' if len(result['text']) > 300 else ''}\n"
                result_text += "-" * 40 + "\n\n"
            
            self.search_results_text.insert('1.0', result_text)
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search documents: {str(e)}")
    
    def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a query (called from main chat)."""
        return document_store.get_context_for_query(query)
    
    def search_documents_with_details(self, query: str, max_results: int = 3):
        """Search documents and return detailed results for RAG integration."""
        return document_store.search_documents(query, max_results)
    
    def has_documents(self) -> bool:
        """Check if any documents are available."""
        return len(document_store.list_documents()) > 0
