import os
import gradio as gr
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")

# --- Import Gemini client ---
# import google.generativeai as genai
import PyPDF2
from src.prompts import GEMINI_SYSTEM_PROMPT

# Initialize Gemini client
from google import genai

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- PDF Text Extraction ---
def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file using PyPDF2."""
    text = []
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text) if text else "⚠️ No extractable text found in PDF."


# --- Chat Function ---
def chat_interface(message, pdf_file=None, history=None):
    # Build context
    context = extract_text_from_pdf(pdf_file) if pdf_file else ""

    # Construct prompt
    prompt = f"""{GEMINI_SYSTEM_PROMPT}
Context:
{context}

User: {message}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        answer = getattr(response, "text", str(response))
    except Exception as e:
        answer = f"❌ Error while generating response: {e}"

    return answer


# --- Gradio UI ---
demo = gr.ChatInterface(
    fn=chat_interface,
    title="📄 Gemini 2.5 Flash-Lite PDF Chatbot",
    description="Ask me anything. Optionally upload a PDF for context-based answers.",
    additional_inputs=[gr.File(label="Upload a PDF (optional)", file_types=[".pdf"])],
    theme="soft",  # makes UI prettier
)

if __name__ == "__main__":
    demo.launch()
