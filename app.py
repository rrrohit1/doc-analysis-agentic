import os
import gradio as gr
from dotenv import load_dotenv

from src.prompts import SYSTEM_PROMPT
from src.memory import ChatMemoryManager

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")

# --- Import dependencies ---
import PyPDF2
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize global memory manager
chat_memory = ChatMemoryManager(max_messages=10)

# --- PDF Text Extraction ---
def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file using PyPDF2. Returns empty string if no PDF provided."""
    if not pdf_file:
        return ""
    
    try:
        # Handle different Gradio file input formats
        if isinstance(pdf_file, list):
            file_path = pdf_file[0] if pdf_file else None
        elif hasattr(pdf_file, 'name'):
            file_path = pdf_file.name
        else:
            file_path = pdf_file
            
        if not file_path:
            return ""
            
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

# --- Enhanced Chat Function with Memory ---
def chat_interface(message, pdf_file=None, history=None):
    """Handle chat interface with optional PDF context and conversation memory."""
    try:
        # Build context from PDF if provided
        pdf_context = extract_text_from_pdf(pdf_file) if pdf_file else ""
        
        # Get conversation history for context
        chat_context = chat_memory.format_for_prompt()
        
        # Construct prompt with history and PDF context
        prompt_parts = [SYSTEM_PROMPT]
        
        if chat_context:
            prompt_parts.append(chat_context)
        
        if pdf_context:
            prompt_parts.append(f"PDF Context: {pdf_context}")
        
        prompt_parts.append(f"User: {message}")
        
        prompt = "\n\n".join(prompt_parts)

        # Generate response using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        
        # Extract text from response
        answer = getattr(response, "text", str(response))
        
        # Add both user message and assistant response to memory
        chat_memory.add_message("user", message)
        chat_memory.add_message("assistant", answer)
        
        return answer
        
    except Exception as e:
        error_msg = f"❌ Error while generating response: {str(e)}"
        # Still add the user message to memory even if there's an error
        chat_memory.add_message("user", message)
        chat_memory.add_message("assistant", error_msg)
        return error_msg

# --- Additional UI Functions ---
def clear_memory():
    """Clear chat memory and return confirmation message."""
    chat_memory.clear_history()
    return "✅ Chat history cleared!"

def get_memory_info():
    """Get information about current memory usage."""
    count = len(chat_memory.chat_history)
    return f"📊 Current chat history: {count}/{chat_memory.max_messages} messages"

# --- Gradio UI ---
with gr.Blocks(theme="soft", title="📄 Gemini PDF Chatbot with Memory") as demo:
    gr.Markdown("# 📄 Gemini 2.5 Flash-Lite PDF Chatbot")
    gr.Markdown("Ask me anything! Upload a PDF for context-based answers. I remember our last 10 exchanges.")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                type="messages",
                height=500,
                label="Chat"
            )
            msg = gr.Textbox(
                label="Your message",
                placeholder="Type your question here...",
                container=False
            )
            
        with gr.Column(scale=1):
            pdf_file = gr.File(
                label="Upload PDF (optional)",
                file_types=[".pdf"],
                type="filepath"
            )
            
            gr.Markdown("### Memory Controls")
            memory_info = gr.Textbox(
                label="Memory Status",
                value="📊 Current chat history: 0/10 messages",
                interactive=False
            )
            
            clear_btn = gr.Button("🗑️ Clear Memory", variant="secondary")
            refresh_btn = gr.Button("🔄 Refresh Info", variant="secondary")
    
    # Chat interface
    chat_interface_gr = gr.ChatInterface(
        fn=chat_interface,
        chatbot=chatbot,
        textbox=msg,
        additional_inputs=[pdf_file]
    )
    
    # Memory control events
    clear_btn.click(
        fn=clear_memory,
        outputs=[memory_info]
    )
    
    refresh_btn.click(
        fn=get_memory_info,
        outputs=[memory_info]
    )
    
    # Update memory info after each message
    msg.submit(
        fn=get_memory_info,
        outputs=[memory_info]
    )

if __name__ == "__main__":
    demo.launch()