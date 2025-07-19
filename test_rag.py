"""
Test script for RAG functionality
"""

from src.utils.document_processor import document_store
import tempfile
import os

def test_rag_functionality():
    print("Testing RAG functionality...")
    
    # Create a sample text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
Ollama is a powerful AI tool that allows you to run large language models locally.
It supports various models like Llama, Code Llama, and others.
You can use Ollama to create chatbots, assist with coding, and answer questions.
The tool is designed to be easy to use and efficient.
        """)
        temp_file = f.name
    
    try:
        # Test document processing
        print(f"Processing test document: {temp_file}")
        content_hash = document_store.add_document(temp_file)
        print(f"Document added with hash: {content_hash}")
        
        # Test document listing
        docs = document_store.list_documents()
        print(f"Documents in store: {len(docs)}")
        for doc in docs:
            print(f"  - {doc['filename']}: {doc['word_count']} words")
        
        # Test search
        query = "What is Ollama?"
        print(f"\nSearching for: '{query}'")
        results = document_store.search_documents(query)
        print(f"Found {len(results)} results")
        for result in results:
            print(f"  - {result['filename']}: {result['text'][:100]}...")
        
        # Test context generation
        context = document_store.get_context_for_query(query)
        print(f"\nGenerated context length: {len(context)} characters")
        print(f"Context preview: {context[:200]}...")
        
        # Clean up
        document_store.remove_document(content_hash)
        print(f"\nCleaned up test document")
        
        print("✅ RAG functionality test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing RAG functionality: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    test_rag_functionality()
