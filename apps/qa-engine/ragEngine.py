import time
from langchain.llms import Ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import sys

class SimpleRAGQA:
    def __init__(self, chroma_db_path: str = "/home/unimate/chroma_db", ollama_host: str = "http://localhost:11434"):
        print("🚀 Initializing RAG Q&A with Dockerized Ollama...")
        
        # 1. Initialize Local Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 2. Connect to ChromaDB
        self.vectorstore = Chroma(
            persist_directory=chroma_db_path,
            embedding_function=self.embeddings,
            collection_name="document_chunks"
        )
        
        # 3. Connect to Ollama running in Docker
        self.llm = Ollama(
            base_url=ollama_host,  # Connect to Ollama Docker container
            model="mistral",
            temperature=0.1,
            num_predict=512,
            timeout=60  # Increase timeout for Docker communication
        )
        
        # 4. Create RAG chain
        self.qa_chain = self._create_qa_chain()
        print(f"✅ RAG Q&A initialized with Ollama at {ollama_host}!")
    
    def _create_qa_chain(self):
        """Create simple RAG chain"""
        prompt_template = """Use the context to answer the question.

Context: {context}

Question: {question}

Answer clearly based on the context. If unsure, say you don't know.

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def ask_question(self, question: str):
        """Ask a single question and return answer with sources"""
        start_time = time.time()
        
        try:
            result = self.qa_chain({"query": question})
            
            response = {
                "question": question,
                "answer": result["result"],
                "sources": [
                    {
                        "document": doc.metadata.get("doc_id", "unknown"),
                        "page": doc.metadata.get("page", 0),
                        "content_preview": doc.page_content[:100] + "..." 
                    }
                    for doc in result["source_documents"]
                ],
                "processing_time": round(time.time() - start_time, 2)
            }
            
            return response
            
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}

def main():
    # Get question from command line argument
    if len(sys.argv) < 2:
        print("Usage: python rag_qa.py \"Your question here\"")
        print("Optional: python rag_qa.py \"Your question\" --host http://ollama-host:11434")
        sys.exit(1)
    
    # Parse command line arguments
    question = sys.argv[1]
    ollama_host = "http://localhost:11434"  # Default
    
    # Check for custom host argument
    if len(sys.argv) >= 4 and sys.argv[2] == "--host":
        ollama_host = sys.argv[3]
    
    print(f"❓ Question: {question}")
    print(f"🌐 Connecting to Ollama at: {ollama_host}")
    
    # Initialize and ask
    rag = SimpleRAGQA(ollama_host=ollama_host)
    result = rag.ask_question(question)
    
    # Display results
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Answer: {result['answer']}")
        print(f"⏱️ Time: {result['processing_time']}s")
        
        if result["sources"]:
            print("\n📚 Sources:")
            for source in result["sources"]:
                print(f"   - Document: {source['document']}, Page: {source['page']}")
                print(f"     Preview: {source['content_preview']}")

if __name__ == "__main__":
    main() 