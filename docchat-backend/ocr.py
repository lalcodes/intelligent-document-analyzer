import os
import base64
import together
from dotenv import load_dotenv

# Load environment variables at the module level
load_dotenv('Key_config.env')

# Define the vision model to be used
# preferred_model = "meta-llama/Llama-Vision-Free"
backup_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo" # Using a more recent model
VISION_MODEL = backup_model

def encode_image(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_markdown(together_client, vision_llm: str, file_path: str) -> str:
    """Sends a request to the Together AI API to get Markdown from an image."""
    ocr_prompt = """Convert the provided image into Markdown format. Ensure that all content from the page is included, such as headers, footers, subtexts, images (with alt text if possible), tables, and any other elements.

    Requirements:
    - Output Only Markdown: Return only the Markdown content without extra explanations.
    - No Delimiters: Do not use code fences like ```markdown.
    - Complete Content: Include all parts of the page (headers, footers, etc.).
    """

    final_image_url = f"data:image/jpeg;base64,{encode_image(file_path)}"

    output = together_client.chat.completions.create(
        model=vision_llm,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": ocr_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": final_image_url}
                    }
                ]
            }
        ]
    )
    return output.choices[0].message.content

def perform_ocr(file_path: str):
    """
    Main function to perform OCR on a single image file.
    """
    try:
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in .env file. Please set it in Key_config.env.")

        together_client = together.Together(api_key=api_key)
        markdown_content = get_markdown(together_client, VISION_MODEL, file_path)
        return markdown_content

    except FileNotFoundError:
        return "Error: Image file not found. Please check the file path."
    except Exception as e:
        # It's good practice to log the full error for debugging
        print(f"An error occurred during OCR: {e}")
        return f"Error: Something went wrong during OCR. Details: {str(e)}"

