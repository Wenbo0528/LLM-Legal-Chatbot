# Import necessary libraries 
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Text splitting
from langchain.schema import Document  # Document structure
from langchain_core.retrievers import BaseRetriever  # Base retriever
from langchain_community.llms import OpenAI  # OpenAI LLM
import PyPDF2  # PDF text extraction
from typing import List  # Type annotation
from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document
from typing import List
from pydantic import BaseModel, Field


def extract_text_from_file(file):
    """Extract text only from PDF files."""
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    else:
        raise ValueError("Unsupported file type. Please upload a PDF.")


def split_text_into_chunks(text: str) -> List[str]:
    """Split text into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)


def store_chunks(chunks: List[str], knowledge_base: List[str]):
    """Store text chunks in the knowledge base."""
    knowledge_base.extend(chunks)


class SimpleRetriever(BaseRetriever):
    """A simple retriever for fetching relevant documents."""

    def __init__(self, knowledge_base: List[str]):
        super().__init__()
        self.knowledge_base = knowledge_base

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve documents containing the query."""
        return [Document(page_content=doc) for doc in self.knowledge_base if query in doc]


# Define simple similarity search for relevant chunks
def get_similarity_score(query: str, chunk: str) -> float:
    """Simple keyword-based similarity scoring"""
    # Convert to lowercase for case-insensitive matching
    query_words = set(query.lower().split())
    chunk_words = set(chunk.lower().split())

    # Calculate intersection of words
    common_words = query_words.intersection(chunk_words)

    # Calculate similarity score - can be enhanced with better algorithms
    if len(query_words) == 0:
        return 0
    return len(common_words) / len(query_words)


def generate_response_with_knowledge_base(
    query: str, api_key: str, model_choice: str, sub_model_choice: str, knowledge_base: List[str]
) -> str:
    # Find relevant chunks based on similarity
    relevant_chunks = []
    for chunk in knowledge_base:
        score = get_similarity_score(query, chunk)
        if score > 0.1:  # Threshold for relevance
            relevant_chunks.append((chunk, score))

    # Sort chunks by relevance score in descending order
    relevant_chunks.sort(key=lambda x: x[1], reverse=True)

    # Take top 3 most relevant chunks (or fewer if less available)
    top_chunks = [chunk for chunk, _ in relevant_chunks[:3]]

    # Prepare system prompt with relevant context
    if top_chunks:
        context = "\n\n".join(top_chunks)
        system_prompt = f"""You are a helpful assistant. Answer the user's question based on the following information:

CONTEXT:
{context}

If the question cannot be answered using the information provided, acknowledge that you don't have enough information rather than making up an answer. Use the context information to provide accurate and helpful responses."""
    else:
        # If no relevant context found
        system_prompt = "You are a helpful assistant. Answer the user's question based on your knowledge. If you don't know the answer, please acknowledge that."

    return system_prompt
