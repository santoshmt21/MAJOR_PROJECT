# ─────────────────────────────────────────────
# RAG ENDPOINTS - Add these to your app.py
# ─────────────────────────────────────────────

# 1. First, add this import at the top of app.py:
# from rag import RAGService, initialize_rag_service, get_rag_service

# 2. Add this to the startup event:
# @app.on_event("startup")
# async def startup_event():
#     global YOLO_MODEL, VIT_MODEL, CLASS_NAMES
#     try:
#         YOLO_MODEL = load_yolo_model()
#         VIT_MODEL = load_vit_model()
#         ...existing code...
#         
#         # Initialize RAG service
#         logger.info("Initializing RAG service...")
#         initialize_rag_service()
#         logger.info("✅ RAG service ready")


# 3. Add these endpoints after your existing endpoints:

from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class IngestResponse(BaseModel):
    status: str
    message: str

class AnswerResponse(BaseModel):
    question: str
    answer: str
    data_ingested: bool


@app.post("/rag/ingest", tags=["RAG"], response_model=IngestResponse)
def ingest_documents():
    """Ingest PDF documents from Artifacts folder into vector store."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return IngestResponse(
                status="error",
                message="RAG service not initialized"
            )
        
        success = rag_service.ingest_data()
        if success:
            return IngestResponse(
                status="success",
                message="Documents ingested successfully"
            )
        else:
            return IngestResponse(
                status="error",
                message="Failed to ingest documents. Check if Artifacts folder exists."
            )
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        return IngestResponse(
            status="error",
            message=f"Error: {str(e)}"
        )


@app.post("/rag/ask", tags=["RAG"], response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask a question based on ingested documents."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return AnswerResponse(
                question=request.question,
                answer="RAG service not initialized",
                data_ingested=False
            )
        
        if not rag_service.is_data_ingested():
            return AnswerResponse(
                question=request.question,
                answer="Please ingest documents first by calling /rag/ingest endpoint",
                data_ingested=False
            )
        
        answer = rag_service.answer_question(request.question)
        return AnswerResponse(
            question=request.question,
            answer=answer,
            data_ingested=True
        )
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return AnswerResponse(
            question=request.question,
            answer=f"Error processing question: {str(e)}",
            data_ingested=False
        )


@app.get("/rag/status", tags=["RAG"])
def rag_status():
    """Check if RAG service is ready and data is ingested."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "ready",
            "data_ingested": rag_service.is_data_ingested(),
            "artifacts_path": "./Artifacts"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
