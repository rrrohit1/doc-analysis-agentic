
# doc-analysis-agentic

An agentic document analysis chatbot powered by Gemini 2.5 Flash-Lite, with PDF upload, chat memory, and a modern Gradio UI.

---

## Folder Structure

```
├── app.py                # Main Gradio app entry point
├── environment.yaml      # Conda environment file 
├── README.md             # Project documentation
├── src/
    ├── config.py         # Configuration utilities
    ├── dummy.py          # Example/experimental code
    ├── memory.py         # Chat memory manager
    └── prompts.py        # System prompt for Gemini
```

---

## Usage

### 1. Clone the repository

```bash
git clone https://github.com/rrrohit1/doc-analysis-agentic.git
cd doc-analysis-agentic
```

### 2. Set up the environment

Create a Conda environment (recommended):

```bash
conda env create -f environment.yaml
conda activate doc-analysis-agentic
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

### 3. Set your Google API Key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the app

```bash
python app.py
```

The Gradio web UI will open in your browser.

---

## Features

- **Chat with Gemini 2.5 Flash-Lite**: Ask questions and get answers powered by Google's latest Gemini model.
- **PDF Upload**: Optionally upload a PDF; the bot will use its content for context-aware answers.
- **Chat Memory**: Remembers the last 10 exchanges for more coherent conversations.
- **Modern Gradio UI**: Clean, interactive chat interface with memory controls.
- **Clear & Inspect Memory**: Easily clear chat history or check memory usage from the UI.
  
---

## Customization

- **System Prompt**: Edit `src/prompts.py` to change the assistant's behavior.
- **Memory Settings**: Adjust `max_messages` in `app.py` or `src/memory.py` for longer/shorter memory.
- **Model Version**: Change the `model` parameter in `app.py` to use a different Gemini variant if available.

---

## Example Usage

**Ask a question:**

> "Summarize the main points of this PDF."

**Upload a PDF:**

> Click "Upload PDF (optional)", select your file, and ask a question about its content.

**Clear memory:**

> Click the 🗑️ button to reset chat history.

---

## How it Works

1. User sends a message (optionally with a PDF).
2. The app extracts text from the PDF (if provided).
3. The last 10 chat messages are included as context.
4. A prompt is constructed and sent to Gemini 2.5 Flash-Lite via the Google Generative AI API.
5. The response is displayed in the chat and stored in memory.

---

## License

This project is licensed under the MIT License.
