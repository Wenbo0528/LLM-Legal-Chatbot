# Import necessary libraries 
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Text splitting
from langchain.schema import Document  # Document structure
from langchain_core.retrievers import BaseRetriever  # Base retriever
from langchain_community.llms import OpenAI  # OpenAI LLM
import pandas as pd  # CSV handling
import PyPDF2  # PDF text extraction
import docx  # DOCX text extraction
from typing import List  # Type annotation
from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document
from typing import List
from pydantic import BaseModel, Field

def extract_text_from_file(file):
    """Extract text from different file types."""
    if file.type == "text/csv":
        df = pd.read_csv(file)
        return df.to_string()
    elif file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

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
    
def retrieve_relevant_chunks(query: str, knowledge_base: List[str]) -> List[str]:
    """Retrieve relevant text chunks based on the query."""
    retriever = SimpleRetriever(knowledge_base)
    relevant_docs = retriever.get_relevant_documents(query)
    return [doc.page_content for doc in relevant_docs]

def generate_response_with_knowledge_base(prompt: str, client, model_choice, sub_model_choice, knowledge_base: List[str]) -> str:
    """Generate a response using the knowledge base and LLM."""

    relevant_chunks = retrieve_relevant_chunks(prompt, knowledge_base)
    context = " ".join(relevant_chunks)
    
    if model_choice == "OpenAI":
        response = client.chat.completions.create(
            model=sub_model_choice,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            stream=False,
        )
        response_content = response['choices'][0]['message']['content']
    elif model_choice == "DeepSeek":
        response = client.generate_response(
            model=sub_model_choice,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            stream=False,
        )
        response_content = response
    
    return response_content
