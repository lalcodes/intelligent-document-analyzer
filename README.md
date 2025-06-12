# DocChat AI: Intelligent Document Q&A

DocChat is a full-stack web application that allows you to upload documents (images or PDFs) and have a conversation about their content. It uses a powerful local AI pipeline to understand the documents and answer your questions.

## Features

### **Advanced Document Handling**
* **Smart Upload:** Supports flexible document uploads, including multiple images or a single PDF per session.
* **Hybrid PDF Processing:** Automatically detects if a PDF is text-based (for fast, direct text extraction) or scanned (for automatic conversion to images and OCR).

### **Core AI Engine**
* **Powerful OCR:** Leverages the Together AI API for accurate text recognition from images and scanned documents.
* **Intelligent Q&A:** Uses a local RAG (Retrieval-Augmented Generation) pipeline with a Llama 2 model to provide context-aware answers.

---

---

## Tech Stack

| Category      | Technology                                             |
|---------------|--------------------------------------------------------|
| **Frontend** | React.js                         |
| **Backend** | FastAPI (Python)                                       |
| **AI / ML** | LangChain, Llama.cpp, Hugging Face, Together AI API    |
| **Database** | ChromaDB (Vector Store)                                |
| **PDF Tools** | PyMuPDF, pdf2image                                     |

---


---

## Getting Started

Follow these steps to set up and run the project locally using Docker.

### Prerequisites
* Docker and Docker Compose installed.
* Git installed.
* An API key from [Together AI](https://www.together.ai/).

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone <https://github.com/lalcodes/intelligent-document-analyzer.git>
    cd <repository-name>
    ```

2.  **Create your environment file:**
    * Inside the `docchat-backend/` directory, create a file named `Key_config.env`.
    * Add your API key to this file:
        ```
        TOGETHER_API_KEY="your_actual_api_key_here"
        ```

3.  **Build and run with Docker Compose:**
    * From the root directory of the project, run the following command:
        ```bash
        docker-compose up --build
        ```
    * **Note:** The first time you run this, it will take a significant amount of time to download the base images and the local language models (several gigabytes). Please be patient.

### Accessing the Application
-   **Frontend:** `http://localhost:3000`
-   **Backend API:** `http://localhost:8000`

---

## Usage

1.  Open the application in your browser.
2.  Click the paperclip icon to select and upload multiple images or a single PDF.
3.  Wait for the "Document processed" message to appear in the chat.
4.  Type your question into the input box and press Enter or click the send icon.
5.  Model responses in the chat window.
