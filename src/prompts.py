"""
System Prompts

Contains system prompts and prompt templates for the AI assistant.
"""

SYSTEM_PROMPT = """You are a helpful and knowledgeable AI assistant powered by Gemini 2.5 Flash-Lite. 

Your capabilities include:
- Answering questions on a wide range of topics
- Analyzing and discussing PDF documents when provided
- Maintaining conversation context and continuity
- Providing clear, accurate, and helpful responses

Guidelines for responses:
1. Be concise yet comprehensive in your answers
2. When PDF context is provided, prioritize information from the document
3. Clearly indicate when you're referencing the uploaded PDF
4. If information conflicts between your knowledge and the PDF, acknowledge both perspectives
5. Ask clarifying questions when the user's request is ambiguous
6. Maintain a friendly and professional tone
7. If you cannot find relevant information in a provided PDF, clearly state this

Response formatting:
- Use clear headings and bullet points when helpful
- Quote specific passages from PDFs when relevant (use quotation marks)
- Provide page references when possible for PDF content
- Break down complex topics into digestible parts

Remember: You have access to conversation history, so you can reference previous exchanges to provide more contextual and relevant responses."""

PDF_ANALYSIS_PROMPT = """When analyzing PDF content, please:

1. **Summarize key points**: Provide a brief overview of the main topics or arguments
2. **Extract important details**: Highlight specific facts, figures, or claims
3. **Identify structure**: Note how the document is organized (sections, chapters, etc.)
4. **Quote relevant passages**: Use direct quotes when they support your analysis
5. **Cross-reference with questions**: Focus on parts most relevant to the user's query

If the PDF content is unclear, incomplete, or seems corrupted, please mention this limitation."""

CONVERSATION_CONTEXT_PROMPT = """Based on our previous conversation:
- Continue naturally from where we left off
- Reference earlier points when relevant
- Build upon previously established context
- Clarify if there are any contradictions with earlier statements"""

ERROR_HANDLING_PROMPT = """If you encounter any issues:
- Clearly explain what went wrong
- Suggest alternative approaches if possible
- Ask for clarification if the request is unclear
- Provide partial answers if some information is available"""

# Prompt templates for specific use cases
def create_pdf_context_prompt(pdf_text: str, user_question: str) -> str:
    """
    Create a prompt that incorporates PDF content with a user question.
    
    Args:
        pdf_text (str): Extracted text from PDF
        user_question (str): User's question
        
    Returns:
        str: Formatted prompt with PDF context
    """
    return f"""Based on the following PDF content, please answer the user's question:

PDF Content:
{pdf_text}

User Question: {user_question}

Please provide a comprehensive answer using the PDF content. If the answer isn't fully contained in the PDF, clearly indicate what parts come from your general knowledge."""

def create_summary_prompt(content: str) -> str:
    """
    Create a prompt for summarizing content.
    
    Args:
        content (str): Content to summarize
        
    Returns:
        str: Formatted summary prompt
    """
    return f"""Please provide a clear and concise summary of the following content:

{content}

Include:
- Main topics or themes
- Key points and important details  
- Overall structure or organization
- Any notable conclusions or recommendations"""

def create_analysis_prompt(content: str, analysis_type: str = "general") -> str:
    """
    Create a prompt for analyzing content.
    
    Args:
        content (str): Content to analyze
        analysis_type (str): Type of analysis to perform
        
    Returns:
        str: Formatted analysis prompt
    """
    analysis_instructions = {
        "general": "Provide a comprehensive analysis covering main themes, arguments, and conclusions.",
        "technical": "Focus on technical details, methodologies, and specifications.",
        "academic": "Analyze structure, arguments, evidence, and academic rigor.",
        "business": "Examine business implications, strategies, and practical applications."
    }
    
    instruction = analysis_instructions.get(analysis_type, analysis_instructions["general"])
    
    return f"""Please analyze the following content:

{content}

Analysis focus: {instruction}

Provide insights on:
- Key findings or arguments
- Strengths and potential weaknesses
- Relevant context or implications
- Any questions or areas for further exploration"""

# Specialized prompts for different document types
RESEARCH_PAPER_PROMPT = """This appears to be a research paper or academic document. When analyzing:
- Identify the research question/hypothesis
- Summarize methodology and findings  
- Note limitations and future research directions
- Evaluate the significance of contributions"""

BUSINESS_DOCUMENT_PROMPT = """This appears to be a business document. When analyzing:
- Extract key business metrics and objectives
- Identify strategic initiatives and recommendations
- Note financial implications and projections
- Summarize action items and next steps"""

LEGAL_DOCUMENT_PROMPT = """This appears to be a legal document. When analyzing:
- Identify key legal provisions and requirements
- Note important dates, parties, and obligations
- Highlight potential risks or compliance issues
- Summarize main legal implications
Note: This is for informational purposes only and not legal advice."""

TECHNICAL_MANUAL_PROMPT = """This appears to be a technical manual or documentation. When analyzing:
- Extract key procedures and instructions
- Identify technical specifications and requirements
- Note safety considerations and warnings
- Summarize operational guidelines and best practices"""

def get_document_type_prompt(content_preview: str) -> str:
    """
    Determine appropriate prompt based on document content.
    
    Args:
        content_preview (str): Preview of document content
        
    Returns:
        str: Appropriate specialized prompt
    """
    content_lower = content_preview.lower()
    
    # Check for research paper indicators
    if any(term in content_lower for term in ['abstract', 'methodology', 'references', 'hypothesis', 'research']):
        return RESEARCH_PAPER_PROMPT
    
    # Check for business document indicators  
    elif any(term in content_lower for term in ['revenue', 'profit', 'strategy', 'market', 'business plan']):
        return BUSINESS_DOCUMENT_PROMPT
    
    # Check for legal document indicators
    elif any(term in content_lower for term in ['contract', 'agreement', 'legal', 'clause', 'terms']):
        return LEGAL_DOCUMENT_PROMPT
    
    # Check for technical manual indicators
    elif any(term in content_lower for term in ['procedure', 'manual', 'installation', 'configuration', 'technical']):
        return TECHNICAL_MANUAL_PROMPT
    
    # Default to general analysis
    return ""