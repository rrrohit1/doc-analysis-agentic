#!/usr/bin/env python3
"""
Standalone PDF Text Extraction Script
"""

import sys
import os
import argparse
from typing import Union

try:
    import PyPDF2
except ImportError:
    print("Error: PyPDF2 is required. Install it with: pip install PyPDF2")
    sys.exit(1)


def extract_text_from_pdf(pdf_input: Union[str, object]) -> str:
    """Extract text from PDF file handling various input types."""
    try:
        file_handle = None
        should_close = False
        
        # Handle different input types
        if isinstance(pdf_input, str):
            if not os.path.exists(pdf_input):
                return f"⚠️ PDF file not found: {pdf_input}"
            file_handle = open(pdf_input, 'rb')
            should_close = True
            
        elif hasattr(pdf_input, 'read'):
            file_handle = pdf_input
            
        elif hasattr(pdf_input, 'name'):
            if os.path.exists(pdf_input.name):
                file_handle = open(pdf_input.name, 'rb')
                should_close = True
            else:
                return f"⚠️ Gradio PDF file not found: {pdf_input.name}"
                
        elif isinstance(pdf_input, list) and len(pdf_input) > 0:
            first_file = pdf_input[0]
            if isinstance(first_file, str) and os.path.exists(first_file):
                file_handle = open(first_file, 'rb')
                should_close = True
            else:
                return "⚠️ Invalid PDF file in list"
        else:
            return "⚠️ Invalid PDF input format"
        
        try:
            reader = PyPDF2.PdfReader(file_handle)
            
            if reader.is_encrypted:
                return "🔒 PDF is encrypted and cannot be processed"
            
            if len(reader.pages) == 0:
                return "⚠️ PDF contains no pages"
            
            extracted_pages = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text().strip()
                    if page_text:
                        extracted_pages.append(f"--- Page {page_num} ---\n{page_text}")
                except Exception:
                    continue
            
            if not extracted_pages:
                return "⚠️ No extractable text found in PDF"
            
            result_text = "\n\n".join(extracted_pages)
            
            # Truncate if too long
            max_chars = 50000
            if len(result_text) > max_chars:
                result_text = result_text[:max_chars] + f"\n\n[Text truncated - original length: {len(result_text)} characters]"
            
            return result_text
            
        finally:
            if should_close and file_handle:
                file_handle.close()
                
    except PyPDF2.errors.PdfReadError as e:
        return f"⚠️ Invalid or corrupted PDF: {str(e)}"
    except Exception as e:
        return f"⚠️ Error reading PDF: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF files')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    if not args.pdf_path.lower().endswith('.pdf'):
        print("⚠️ Warning: File does not have .pdf extension")
    
    result = extract_text_from_pdf(args.pdf_path)
    print(result)


if __name__ == "__main__":
    main()