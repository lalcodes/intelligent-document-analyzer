import os
import time
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain.document_loaders import TextLoader
from huggingface_hub import hf_hub_download

# --- Global Variable for the LLM ---
llm_instance = None
MODEL_DIR = "./models"
os.makedirs(MODEL_DIR, exist_ok=True)

def initialize_llm():
    """Initializes the main language model and stores it globally."""
    global llm_instance
    if llm_instance is None:
        try:
            print("   Loading RAG LLM into memory... (This can be slow on first run)")
            start_time = time.time()
            repo_id = "TheBloke/Llama-2-7B-Chat-GGUF"
            filename = "llama-2-7b-chat.Q4_K_M.gguf"
            model_path = hf_hub_download(
                repo_id=repo_id, filename=filename,
                local_dir=MODEL_DIR, local_dir_use_symlinks=False
            )
            llm_instance = LlamaCpp(
                model_path=model_path, n_ctx=2048, max_tokens=512,
                n_threads=4, n_batch=512, verbose=False, temperature=0.3
            )
            end_time = time.time()
            print(f"   RAG LLM initialized successfully in {end_time - start_time:.2f} seconds.")
        except Exception as e:
            print(f"Error in initializing RAG LLM: {str(e)}")
            llm_instance = None
    return llm_instance

# --- Individual Function 1: Load and Split ---
def load_and_split_documents(ocr_text: str):
    """Takes OCR text, saves it temporarily, loads it, and splits it into chunks."""
    print("      -> RAG Step 1/4: Loading and splitting document text...")
    try:
        with open("temp_ocr_text.txt", "w", encoding="utf-8") as f: f.write(ocr_text)
        loader = TextLoader("temp_ocr_text.txt",encoding="utf-8")
        documents = loader.load()

        # Dynamic chunk sizing
        text_length = len(ocr_text)
        chunk_size = text_length if text_length < 1000 else min(500, text_length // 10)
        chunk_overlap = 0 if text_length < 1000 else chunk_size // 5
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(documents)
        os.remove("temp_ocr_text.txt")
        print("         -> Step 1/4 Complete.")
        return texts
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return None

# --- Individual Function 2: Create Retriever ---
def create_retriever(texts: list, db_directory: str):
    """Creates a vector database from text chunks and returns a retriever."""
    print("      -> RAG Step 2/4: Creating and persisting vector database...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            cache_folder=MODEL_DIR
        )
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=db_directory 
        )
        print("         -> Step 2/4 Complete.")
        return vectorstore.as_retriever()
    except Exception as e:
        print(f"Error creating retriever: {e}")
        return None

# --- Individual Function 3: Setup QA Chain ---
def setup_qa_chain(retriever):
    """Sets up the final question-answering chain with a prompt template."""
    print("      -> RAG Step 3/4: Setting up QA chain...")
    try:
        RAG_template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Use three sentences maximum and keep the answer concise. If you don't know the answer, just say that you don't know. Don't try to make up an answer.
Question: {question}
Context: {context}
Answer:
"""
        RAG_prompt = ChatPromptTemplate.from_template(RAG_template)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_instance, chain_type="stuff", retriever=retriever,
            return_source_documents=False, chain_type_kwargs={"prompt": RAG_prompt}
        )
        print("         -> Step 3/4 Complete.")
        return qa_chain
    except Exception as e:
        print(f"Error setting up QA chain: {e}")
        return None

# --- Individual Function 4: Get Answer ---
def get_answer_from_chain(qa_chain: RetrievalQA, question: str) -> str:
    """Takes a pre-built RAG chain and a question, and returns the answer."""
    print("      -> RAG Step 4/4: Invoking QA chain to get answer...")
    try:
        start_time = time.time()
        result = qa_chain.invoke({"query": question})
        end_time = time.time()
        print(f"         -> Answer generated in {end_time - start_time:.2f} seconds.")
        return result["result"]
    except Exception as e:
        print(f"Error during question answering: {e}")
        return "Error: Failed to get an answer from the RAG pipeline."
