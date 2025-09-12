import os
import gradio as gr
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")

# --- Import Gemini client ---
import PyPDF2
from src.prompts import SYSTEM_PROMPT

# Initialize Gemini client
from google import genai
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- PDF Text Extraction ---
def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file using PyPDF2."""
    if not pdf_file:
        return ""
    
    try:
        # Handle different Gradio file input formats
        if isinstance(pdf_file, list):
            # If it's a list, take the first file path
            file_path = pdf_file[0] if pdf_file else None
        elif hasattr(pdf_file, 'name'):
            # If it's a file object with a name attribute
            file_path = pdf_file.name
        else:
            # If it's already a string path
            file_path = pdf_file
            
        if not file_path:
            return "⚠️ No PDF file provided."
            
        # Open and read the PDF file
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
                    
            return "\n".join(text) if text else "⚠️ No extractable text found in PDF."
            
    except Exception as e:
        return f"⚠️ Error reading PDF: {str(e)}"

# --- Chat Function ---
def chat_interface(message, pdf_file=None, history=None):
    """Handle chat interface with optional PDF context."""
    try:
        # Build context from PDF if provided (PDF is completely optional)
        context = extract_text_from_pdf(pdf_file) if pdf_file else ""
        
        # Construct prompt - only include context section if we have PDF content
        if context:
            prompt = f"""{SYSTEM_PROMPT}

Context: {context}

User: {message}"""
        else:
            prompt = f"""{SYSTEM_PROMPT}

User: {message}"""

        # Generate response using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        
        # Extract text from response
        answer = getattr(response, "text", str(response))
        return answer
        
    except Exception as e:
        return f"❌ Error while generating response: {str(e)}"

# --- Gradio UI ---
demo = gr.ChatInterface(
    fn=chat_interface,
    title="📄 Gemini 2.5 Flash-Lite PDF Chatbot",
    description="Ask me anything. Optionally upload a PDF for context-based answers.",
    additional_inputs=[
        gr.File(
            label="Upload a PDF (optional)", 
            file_types=[".pdf"],
            type="filepath"  # This ensures we get file paths instead of file objects
        )
    ],
    theme="soft",
    type="messages"  # Use the new messages format to avoid deprecation warning
)

if __name__ == "__main__":
    demo.launch()