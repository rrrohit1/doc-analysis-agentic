import os
import gradio as gr
from dotenv import load_dotenv
from google import genai

from src.prompts import SYSTEM_PROMPT
from src.memory import ChatMemoryManager
from src.process_pdf import extract_text_from_pdf

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")

# --- Initialize Components ---
client = genai.Client(api_key=GOOGLE_API_KEY)
chat_memory = ChatMemoryManager(max_messages=10)

def get_memory_info():
    """Returns a string with the current memory usage information."""
    count = len(chat_memory.chat_history)
    return f"📊 Current chat history: {count}/{chat_memory.max_messages} messages"


def clear_memory():
    """Clears the chat memory."""
    chat_memory.clear()

def process_uploaded_pdf(pdf_file):
    """
    Process uploaded PDF and return preview text and full extracted text.
    
    Args:
        pdf_file (gradio.File): The uploaded PDF file object.
        
    Returns:
        tuple: (status_message, preview_text, extracted_text)
    """
    if not pdf_file:
        return "No PDF uploaded.", "", ""
    
    try:
        extracted_text = extract_text_from_pdf(pdf_file.name)
        
        if extracted_text.startswith("⚠️") or extracted_text.startswith("🔒"):
            return extracted_text, "", ""
        
        # Create a preview (first 500 characters)
        preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        status = f"✅ PDF processed successfully! Extracted {len(extracted_text)} characters from PDF."
        
        return status, preview, extracted_text
        
    except Exception as e:
        return f"❌ Error processing PDF: {str(e)}", "", ""

def chat_interface(message, history, pdf_context_state=""):
    """
    Handle chat interface with optional PDF context and conversation memory.
    
    Args:
        message (str): User's input message
        history (list): Chat history from Gradio
        pdf_context_state (str): Processed text from the PDF file (from state)
        
    Returns:
        str: Assistant's response
    """
    try:
        # Get conversation history for context
        chat_context = chat_memory.format_for_prompt()
        
        # Construct comprehensive prompt
        prompt_parts = [SYSTEM_PROMPT]
        
        if chat_context:
            prompt_parts.append(chat_context)
        
        # Use the context from the state variable
        if pdf_context_state:
            prompt_parts.append(f"PDF Context:\n{pdf_context_state}")
        
        prompt_parts.append(f"User: {message}")
        
        full_prompt = "\n\n".join(prompt_parts)

        # Generate response using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt,
        )
        
        # Extract response text
        answer = getattr(response, "text", str(response))
        
        # Update memory with the conversation
        chat_memory.add_message("user", message)
        chat_memory.add_message("assistant", answer)
        
        return answer
        
    except Exception as e:
        error_msg = f"❌ Error generating response: {str(e)}"
        # Log the error exchange to memory
        chat_memory.add_message("user", message)
        chat_memory.add_message("assistant", error_msg)
        return error_msg

def create_interface():
    """Create and configure the Gradio interface."""
    with gr.Blocks(
        theme="soft", 
        title="📄 Gemini PDF Chatbot with Memory",
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as demo:
        
        # --- State for PDF Context ---
        pdf_context_state = gr.State("")

        # Header
        gr.Markdown("# 📄 Gemini 2.5 Flash-Lite PDF Chatbot")
        gr.Markdown(
            "💬 Ask me anything! Upload a PDF and click 'Process' for context-based answers. "
            "I remember our last 10 exchanges for better continuity."
        )
        
        with gr.Row():
            # Main chat area
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    type="messages",
                    height=500,
                    label="💬 Chat History",
                    show_label=True
                )
                msg = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your question here...",
                    container=False,
                    scale=4
                )
                
            # Sidebar controls
            with gr.Column(scale=1):
                pdf_file = gr.File(
                    label="📄 Upload PDF",
                    file_types=[".pdf"],
                    type="filepath"
                )
                process_btn = gr.Button("🚀 Process PDF", variant="primary")
                pdf_status_text = gr.Textbox(
                    label="PDF Processing Status",
                    interactive=False
                )
                pdf_preview_text = gr.Textbox(
                    label="PDF Content Preview",
                    interactive=False,
                    lines=5
                )

                gr.Markdown("### 🧠 Memory Controls")
                memory_info = gr.Textbox(
                    label="Memory Status",
                    value=get_memory_info(),
                    interactive=False
                )
                
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary", scale=1)
        
        # --- Event Listeners ---
        
        # PDF upload and process
        process_btn.click(
            fn=process_uploaded_pdf,
            inputs=[pdf_file],
            outputs=[pdf_status_text, pdf_preview_text, pdf_context_state]
        )
        
        # Set up chat interface
        chat_interface_gr = gr.ChatInterface(
            fn=chat_interface,
            chatbot=chatbot,
            textbox=msg,
            additional_inputs=[pdf_context_state], # Pass the state variable here
            type="messages"
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
        
    return demo

def main():
    """Main application entry  point."""
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )

if __name__ == "__main__":
    main()
