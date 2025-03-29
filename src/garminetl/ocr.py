from docling.document_converter import DocumentConverter
import os

def extract_markdown_from_pdf(pdf_path: str) -> str:
    """
    Uses Docling to convert a PDF (with or without OCR) into structured Markdown.
    
    Parameters:
        pdf_path (str): Full path to the PDF file.

    Returns:
        str: Markdown content extracted from the PDF.
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except Exception as e:
        print(f"Error while processing with Docling: {e}")
        return ""
