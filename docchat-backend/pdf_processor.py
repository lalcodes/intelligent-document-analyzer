import os
import fitz
from pdf2image import convert_from_path

def handle_pdf(pdf_path: str, upload_folder: str):

    try:
        doc = fitz.open(pdf_path)
        total_text = ""
        is_scanned = True

        print("      -> Analyzing PDF type...")
        for page in doc:
            # Extract text from each page
            text_from_page = page.get_text().strip()
            if len(text_from_page) > 100: # Heuristic: if a page has >100 chars, it's likely text-based
                is_scanned = False
            total_text += text_from_page + "\n"
        
        doc.close()

        # If the document is NOT scanned (i.e., we extracted a good amount of text)
        if not is_scanned:
            print("      -> Text-based PDF detected. Extracting text directly.")
            return total_text, None # Return the text and no image paths

        # If the document IS scanned
        else:
            print("      -> Scanned PDF detected. Converting to images.")
            # Convert PDF to a list of images
            images = convert_from_path(pdf_path)
            image_paths = []
            
            # Create a subfolder for the converted images to keep things organized
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_folder = os.path.join(upload_folder, pdf_name)
            os.makedirs(output_folder, exist_ok=True)
            
            for i, image in enumerate(images):
                image_path = os.path.join(output_folder, f'page_{i+1}.jpg')
                image.save(image_path, 'JPEG')
                image_paths.append(image_path)
                
            print(f"      -> Successfully converted PDF to {len(image_paths)} images.")
            return None, image_paths # Return no text, but a list of image paths

    except Exception as e:
        print(f"Error processing PDF file {pdf_path}: {e}")
        return f"Error: Failed to process PDF. Details: {e}", None
