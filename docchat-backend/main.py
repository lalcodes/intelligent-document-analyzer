import os
import shutil
import uuid
import traceback
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import the new PDF processor
from pdf_processor import handle_pdf
from ocr import perform_ocr
from rag import (
    initialize_llm, 
    load_and_split_documents,
    create_retriever,
    setup_qa_chain,
    get_answer
)

session_cache = {}

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    session_id: str
    question: str

@app.on_event("startup")
async def startup_event():
    print("Application starting up...")
    # ---Cleanup logic for the Vector DB folder ---
    db_master_folder = "vector_DB"
    if os.path.exists(db_master_folder):
        print(f"Cleaning up old database files from '{db_master_folder}'..")
        try:
            shutil.rmtree(db_master_folder)
        except OSError as e:
            print(f"Error cleaning up directory {db_master_folder}: {e}")

    initialize_llm()
    os.makedirs("uploaded_files", exist_ok=True)
    os.makedirs("vector_DB", exist_ok=True)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    print(f"\n--- Received new UPLOAD request with {len(files)} file(s) ---")
    
    saved_file_paths = []
    final_ocr_text = ""
    
    try:
        upload_folder = "uploaded_files"
        #Save all uploaded files temporarily
        for file in files:
            file_path = os.path.join(upload_folder, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(file_path)
            print(f"File '{file.filename}' saved successfully.")

        #Process based on file type
        paths_for_ocr = []
        # If PDF was uploaded
        if len(saved_file_paths) == 1 and saved_file_paths[0].lower().endswith('.pdf'):
            pdf_path = saved_file_paths[0]
            print("PDF file detected. Processing...")
            text_from_pdf, image_paths_from_pdf = handle_pdf(pdf_path, upload_folder)
            
            # If text was extracted directly, use it and skip OCR
            if text_from_pdf:
                final_ocr_text = text_from_pdf
            # If it was a scanned PDF, add the converted images to the OCR list
            elif image_paths_from_pdf:
                paths_for_ocr.extend(image_paths_from_pdf)

        # If images were uploaded
        else:
            print("Image file(s) detected.")
            paths_for_ocr.extend(saved_file_paths)

        #Perform OCR
        if paths_for_ocr:
            print("Performing OCR on image files...")
            for file_path in sorted(paths_for_ocr):
                ocr_result = perform_ocr(file_path)
                if ocr_result.startswith("Error:"):
                    raise HTTPException(status_code=500, detail=ocr_result)
                final_ocr_text += ocr_result + "\n\n--- Page Break ---\n\n"
            print("OCR completed for all images.")
        
        if not final_ocr_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from the document(s).")
            
        #Run the RAG pipeline 
        print("--- RAG Pipeline Started ---")
        texts = load_and_split_documents(final_ocr_text)
        if texts is None:
            raise HTTPException(status_code=500, detail="Failed to split document text.")
        
        session_id = str(uuid.uuid4())
        db_directory = os.path.join("vector_DB", f"chroma_db_{session_id}")
        
        retriever = create_retriever(texts, db_directory)
        if retriever is None:
            raise HTTPException(status_code=500, detail="Failed to create retriever.")
            
        qa_chain = setup_qa_chain(retriever)
        if qa_chain is None:
            raise HTTPException(status_code=500, detail="Failed to create QA chain.")
        
        print("--- RAG Pipeline Finished ---")

        session_cache[session_id] = qa_chain
        # print(f"Conversation cached with Session ID: {session_id}")
        
        return {"session_id": session_id, "detail": "Files processed successfully."}

    except Exception as e:
        print(f"\nAn Error during upload !!!")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")
    finally:
        #Clean up all temporary files and folders
        print("Cleaning up temporary uploaded files...")
        for path in saved_file_paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        # Also clean up the main upload folder if there are converted image subfolders
        if any(os.path.isdir(os.path.join(upload_folder, item)) for item in os.listdir(upload_folder)):
            for item in os.listdir(upload_folder):
                item_path = os.path.join(upload_folder, item)
                if os.path.isdir(item_path):
                     shutil.rmtree(item_path)
        print("Cleanup complete.")

@app.post("/ask")
async def ask_question(request: AskRequest):
    print(f"\n--- Received new ASK request for Session ID: {request.session_id} ---")
    qa_chain = session_cache.get(request.session_id)
    if not qa_chain:
        raise HTTPException(status_code=404, detail="Session not found. Please upload the document again.")
    print(f"Question: '{request.question}'")
    answer = get_answer(qa_chain, request.question)
    return {"answer": answer}

@app.get("/")
def read_root():
    return {"message": "DocChat Backend is running!"}
