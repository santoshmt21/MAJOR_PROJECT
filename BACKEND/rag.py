import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers.utils import logging as transformers_logging

# Suppress warnings
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
transformers_logging.set_verbosity_error()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class RAGService:
    """Retrieval-Augmented Generation service for document question answering."""
    
    def __init__(self, artifacts_path: str = "./Artifacts", max_docs: int = 20):
        """
        Initialize the RAG service.
        
        Args:
            artifacts_path: Path to the directory containing PDF documents
            max_docs: Maximum number of documents to process
        """
        self.artifacts_path = artifacts_path
        self.max_docs = max_docs
        self.vectors = None
        self.embeddings = None
        self.llm = None
        self.retrieval_chain = None
        
        # Initialize LLM
        groq_api_key = os.getenv('API_KEY')
        if not groq_api_key:
            raise ValueError("API_KEY not found in environment variables. Please set it in .env file")
        
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant"
        )
        
        # Define prompt template
        self.prompt_template = """
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question.

<context>
{context}
</context>

Question: {input}
"""
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)
        
        logger.info("RAG Service initialized")
    
    def ingest_data(self) -> bool:
        """
        Load PDF documents from Artifacts folder and create vector embeddings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.vectors is not None:
                logger.info("Vector store already exists. Skipping ingestion.")
                return True
            
            logger.info(f"Loading documents from {self.artifacts_path}...")
            
            # Check if artifacts directory exists
            if not os.path.exists(self.artifacts_path):
                logger.warning(f"Artifacts directory not found at {self.artifacts_path}")
                return False
            
            # Initialize embeddings
            logger.info("Initializing embeddings...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Load documents
            loader = PyPDFDirectoryLoader(self.artifacts_path)
            docs = loader.load()
            
            if not docs:
                logger.warning(f"No PDF documents found in {self.artifacts_path}")
                return False
            
            logger.info(f"Loaded {len(docs)} documents from PDFs")
            
            # Split documents into chunks
            logger.info("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            final_documents = text_splitter.split_documents(docs[:self.max_docs])
            logger.info(f"Created {len(final_documents)} document chunks")
            
            # Create vector store
            logger.info("Creating vector store...")
            self.vectors = FAISS.from_documents(
                final_documents,
                self.embeddings
            )
            
            # Create retrieval chain
            document_chain = create_stuff_documents_chain(self.llm, self.prompt)
            retriever = self.vectors.as_retriever()
            self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            logger.info("Data ingestion completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error during data ingestion: {str(e)}")
            return False
    
    def answer_question(self, question: str) -> Optional[str]:
        """
        Answer a question based on ingested documents.
        
        Args:
            question: The question to answer
            
        Returns:
            str: The answer, or None if vector store is not initialized
        """
        try:
            if self.vectors is None:
                logger.warning("Vector store not initialized. Please ingest data first.")
                return None
            
            if not question or not question.strip():
                return "Please provide a valid question."
            
            logger.info(f"Processing question: {question}")
            
            # If retrieval chain not created, create it now
            if self.retrieval_chain is None:
                document_chain = create_stuff_documents_chain(self.llm, self.prompt)
                retriever = self.vectors.as_retriever()
                self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            # Get response
            response = self.retrieval_chain.invoke({'input': question})
            answer = response.get('answer', 'No answer generated')
            
            logger.info(f"Generated answer successfully")
            return answer
        
        except Exception as e:
            logger.error(f"Error while answering question: {str(e)}")
            return f"Error processing question: {str(e)}"
    
    def is_data_ingested(self) -> bool:
        """Check if data has been ingested."""
        return self.vectors is not None


# Global RAG service instance
rag_service = None


def initialize_rag_service():
    """Initialize the RAG service (call this at app startup)."""
    global rag_service
    try:
        rag_service = RAGService(artifacts_path="./Artifacts")
        logger.info("RAG service created")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {str(e)}")
        rag_service = None


def get_rag_service() -> Optional[RAGService]:
    """Get the RAG service instance."""
    if rag_service is None:
        initialize_rag_service()
    return rag_service
