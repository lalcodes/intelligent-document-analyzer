import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FiPaperclip, FiSend, FiZoomIn, FiX, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import './App.css';

const UPLOAD_URL = 'http://127.0.0.1:8000/upload';
const ASK_URL = 'http://127.0.0.1:8000/ask';

function App() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previewUrl, setPreviewUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);
  const [isZoomed, setIsZoomed] = useState(false);
  const [currentPreviewIndex, setCurrentPreviewIndex] = useState(0);

  useEffect(() => {
    if (!selectedFiles || selectedFiles.length === 0) {
      setPreviewUrl('');
      return;
    }
    const objectUrl = URL.createObjectURL(selectedFiles[currentPreviewIndex]);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFiles, currentPreviewIndex]);


  /**
   * --- MODIFIED: Handles multiple file selection with validation. ---
   * This function now filters for allowed file types (images and PDFs).
   */
  const handleFileChange = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const filesArray = Array.from(files);

    // --- NEW VALIDATION LOGIC ---
    const hasPdfs = filesArray.some(file => file.type === 'application/pdf');

    // Rule: If a PDF is selected, it must be the ONLY file selected.
    if (hasPdfs && filesArray.length > 1) {
        alert("You can only upload a single PDF at a time. To upload multiple files, please select only images.");
        fileInputRef.current.value = ""; // Clear the file input
        return;
    }
    // --- END NEW VALIDATION LOGIC ---

    // Filter for allowed file types (this is a fallback)
    const filteredFiles = filesArray.filter(file => 
        file.type.startsWith('image/') || file.type === 'application/pdf'
    );

    if (filteredFiles.length === 0) {
        alert("Please select only image or PDF files.");
        fileInputRef.current.value = "";
        return;
    }
    
    
    // --- Proceed with the valid, filtered files ---
    setSelectedFiles(filteredFiles);
    setCurrentPreviewIndex(0);
    
    setMessages([]);
    setSessionId(null);
    setIsLoading(true);

    const formData = new FormData();
    filteredFiles.forEach(file => {
      formData.append('files', file); 
    });

    try {
      const response = await axios.post(UPLOAD_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSessionId(response.data.session_id);
      setMessages([{ sender: 'bot', text: `Processed ${filteredFiles.length} document(s). You can now ask questions.` }]);
    } catch (error) {
      console.error('Error uploading files:', error);
      const errorText = error.response?.data?.detail || 'Failed to process documents.';
      setMessages([{ sender: 'bot', text: `Error: ${errorText}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim() || !sessionId) {
      alert("Please upload document(s) and wait for them to process before asking a question.");
      return;
    }

    const userMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await axios.post(ASK_URL, {
        session_id: sessionId,
        question: query,
      });
      const botMessage = { sender: 'bot', text: response.data.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error asking question:', error);
      const errorText = error.response?.data?.detail || 'Failed to get an answer.';
      setMessages(prev => [...prev, { sender: 'bot', text: `Error: ${errorText}` }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const goToNextImage = () => {
    setCurrentPreviewIndex(prevIndex => (prevIndex + 1) % selectedFiles.length);
  };
  
  const goToPrevImage = () => {
    setCurrentPreviewIndex(prevIndex => (prevIndex - 1 + selectedFiles.length) % selectedFiles.length);
  };

  const renderPreview = () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      return (
        <div className="file-preview-placeholder">
          <p>File Preview</p>
        </div>
      );
    }

    // Use the currently selected file for the check
    const currentFile = selectedFiles[currentPreviewIndex];

    if (currentFile.type.startsWith('image/')) {
      return (
        <div className="image-preview-container">
          {selectedFiles.length > 1 && (
            <button onClick={goToPrevImage} className="nav-arrow prev-arrow" title="Previous Image">
              <FiChevronLeft size={32} />
            </button>
          )}

          <img src={previewUrl} alt="Preview" className="image-preview-fit" />

          {selectedFiles.length > 1 && (
            <div className="image-counter">
              {currentPreviewIndex + 1} / {selectedFiles.length}
            </div>
          )}

          <button onClick={() => setIsZoomed(true)} className="zoom-button" title="Zoom In">
            <FiZoomIn size={24} />
          </button>

          {selectedFiles.length > 1 && (
            <button onClick={goToNextImage} className="nav-arrow next-arrow" title="Next Image">
              <FiChevronRight size={32} />
            </button>
          )}
        </div>
      );
    }
    
    return <iframe src={previewUrl} title="File Preview" className="file-preview-frame" />;
  };

  return (
    <>
      <div className="app-container">
        <h1 className="app-title">Doc.ChatAI</h1>
        <div className="main-content">
          <div className="chat-section">
            <div className="chat-window">
               {messages.length === 0 && (
                  <div className="empty-chat-message">
                      {selectedFiles.length > 0 ? 'Processing document(s)...' : "Please attach document(s) to begin"}
                  </div>
               )}
               {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                      <p>{msg.text}</p>
                  </div>
               ))}
               {isLoading && (
                  <div className="message bot-message">
                      <p>Thinking...</p>
                  </div>
               )}
            </div>
            <form className="input-area" onSubmit={handleSubmit}>
              <input
                type="file"
                multiple 
                onChange={handleFileChange}
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept="image/*,application/pdf"
              />
              <button type="button" className="icon-button" onClick={handleAttachClick} title="Attach File" disabled={isLoading}>
                  <FiPaperclip size={20} />
              </button>
              <input
                type="text"
                className="query-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your query here..."
                disabled={!sessionId || isLoading}
              />
              <button type="submit" className="icon-button send-button" disabled={!query.trim() || !sessionId || isLoading} title="Send">
                  <FiSend size={20} />
              </button>
            </form>
          </div>
          <div className="file-preview-section">
            {renderPreview()}
          </div>
        </div>
        <footer className="footer-credit">
          Developed by Syamlal  | Powered by Llama 
        </footer>
      </div>

      {isZoomed && (
        <div className="zoom-modal" onClick={() => setIsZoomed(false)}>
          <button className="zoom-close-button" onClick={() => setIsZoomed(false)}>
            <FiX size={30} />
          </button>
          <img 
            src={previewUrl} 
            alt="Zoomed Preview" 
            className="zoom-modal-content"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}

export default App;
