import os
import gradio as gr
from dotenv import load_dotenv
from google import genai

from src.prompts import SYSTEM_PROMPT
from src.memory import ChatMemoryManager
from src.utils import format_file_size

# --- Configuration ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found. Please set it in your .env file.")

# --- Initialize Components ---
from src.process_pdf import extract_text_from_pdf

client = genai.Client(api_key=GOOGLE_API_KEY)
chat_memory = ChatMemoryManager(max_messages=10)


def chat_interface(message, pdf_file=None, history=None):
    """
    Handle chat interface with optional PDF context and conversation memory.
    
    Args:
        message (str): User's input message
        pdf_file (str, optional): Path to uploaded PDF file
        history (list, optional): Chat history from Gradio
        
    Returns:
        str: Assistant's response
    """
    try:
        # Extract PDF context if file is provided
        pdf_context = ""
        if pdf_file:
            pdf_context = extract_text_from_pdf(pdf_file)
            if pdf_context.startswith("⚠️"):
                return pdf_context  # Return error message if PDF extraction failed
        
        # Get conversation history for context
        chat_context = chat_memory.format_for_prompt()
        
        # Construct comprehensive prompt
        prompt_parts = [SYSTEM_PROMPT]
        
        if chat_context:
            prompt_parts.append(chat_context)
        
        if pdf_context:
            prompt_parts.append(f"PDF Context:\n{pdf_context}")
        
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


def clear_memory():
    """Clear chat memory and return confirmation."""
    chat_memory.clear_history()
    return "✅ Chat history cleared!"


def get_memory_info():
    """Get current memory usage information."""
    count = len(chat_memory.chat_history)
    return f"📊 Current chat history: {count}/{chat_memory.max_messages} messages"


def process_uploaded_pdf(pdf_file):
    """Process uploaded PDF and return preview text."""
    if not pdf_file:
        return "No PDF uploaded", ""
    
    try:
        extracted_text = extract_text_from_pdf(pdf_file)
        
        if extracted_text.startswith("⚠️") or extracted_text.startswith("🔒"):
            return extracted_text, ""
        
        # Create preview (first 500 characters)
        preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        status = f"✅ PDF processed successfully! Extracted {len(extracted_text)} characters from PDF."
        
        return status, preview
        
    except Exception as e:
        return f"❌ Error processing PDF: {str(e)}", ""


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
        
        # Header
        gr.Markdown("# 📄 Gemini 2.5 Flash-Lite PDF Chatbot")
        gr.Markdown(
            "💬 Ask me anything! Upload a PDF for context-based answers. "
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
                    label="📄 Upload PDF (Optional)",
                    file_types=[".pdf"],
                    type="filepath"
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
        
        # PDF upload processing
        pdf_file.change(
            fn=process_uploaded_pdf,
            inputs=[pdf_file],
            outputs=[pdf_status, pdf_preview]
        )
        
        # Set up chat interface
        chat_interface_gr = gr.ChatInterface(
            fn=chat_interface,
            chatbot=chatbot,
            textbox=msg,
            additional_inputs=[pdf_file],
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
    """Main application entry point."""
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )


if __name__ == "__main__":
    main()