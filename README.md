# intelligent-document-analyzer
DocChat AI
DocChat AI
DocChat is a full-stack web application that allows you to upload documents (images or PDFs) and ask questions about their content using a powerful OCR and RAG pipeline.

Features
Smart Document Upload: Supports multiple image uploads or single PDF uploads.

Hybrid PDF Processing: Automatically detects if a PDF is text-based (for fast text extraction) or scanned (for image conversion and OCR).

Intelligent Q&A: Uses a local RAG (Retrieval-Augmented Generation) pipeline with a Llama 2 model to answer questions based on the document's content.

Interactive Frontend: A clean, modern, and responsive user interface built with React, featuring an image gallery viewer with zoom functionality.

Tech Stack
Frontend:

React.js

Backend:

FastAPI (Python web framework)

Together AI API (for Vision/OCR)

LangChain (for the RAG pipeline)

Llama.cpp & Hugging Face models (for local LLM inference)

ChromaDB (for vector storage)

PyMuPDF & pdf2image (for smart PDF processing)

Getting Started
Follow these steps to set up and run the project locally.

Prerequisites
Docker and Docker Compose installed.

Git installed.

A Key_config.env file in the docchat-backend directory with your TOGETHER_API_KEY.

Installation & Running
Clone the repository:

git clone <your-repository-url>
cd <your-repository-name>

Create your environment file:

Inside the docchat-backend/ directory, create a file named Key_config.env.

Add your API key to this file:

TOGETHER_API_KEY="your_actual_api_key_here"

Build and run with Docker Compose:

From the root directory of the project (docchat_project/), run:

docker-compose up --build

The first time you run this, it will take a long time to download the base images and the local language models.

Accessing the Application
Frontend: Open your web browser and navigate to http://localhost:3000

Backend API: The API will be running at http://localhost:8000

Usage
Open the application in your browser.

Click the paperclip icon to select and upload multiple images or a single PDF.

Wait for the "Document processed" message to appear in the chat.

Type your question into the input box and press Enter or click the send icon.

View the model's answer in the chat window.
