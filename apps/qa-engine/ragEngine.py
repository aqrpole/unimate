from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import uvicorn
from typing import Optional

app = FastAPI(title="RAG Q&A API", version="1.0.0")

class QuestionRequest(BaseModel):
    question: str
    ollama_host: Optional[str] = "http://unimate-ollama-1:11434"#ip change req172.18.0.2

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list
    processing_time: float
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    status: str = "error"

class SimpleRAGQA:
    def __init__(self, chroma_db_path: str = "/home/unimate/chroma_db"):
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

        print("✅ RAG Q&A initialized! Ollama connection will be established per request.")

    def _create_qa_chain(self, ollama_host: str):
        """Create RAG chain with specific Ollama host"""
        # Connect to Ollama running in Docker
        llm = Ollama(
            base_url=ollama_host,
            model="mistral",
            temperature=0.1,
            num_predict=512,
            timeout=300 #timout was 60, waiting more to 5min
        )

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
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def ask_question(self, question: str, ollama_host: str):
        """Ask a single question and return answer with sources"""
        start_time = time.time()

        try:
            # Create chain with specific Ollama host for this request
            qa_chain = self._create_qa_chain(ollama_host)
            result = qa_chain({"query": question})

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

# Initialize RAG system once at startup
rag_system = SimpleRAGQA()

@app.put("/ask", response_model=QuestionResponse, responses={400: {"model": ErrorResponse}})
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the RAG system and get an answer with sources.

    - **question**: The question to ask
    - **ollama_host**: Optional Ollama host URL (default: http://localhost:11434)
    """
    try:
        result = rag_system.ask_question(request.question, request.ollama_host)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return QuestionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RAG Q&A API"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG Q&A API",
        "endpoints": {
            "POST /ask": "Ask a question to the RAG system",
            "GET /health": "Health check",
            "GET /": "API information"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
