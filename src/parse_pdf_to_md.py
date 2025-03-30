from docling.document_converter import DocumentConverter
import os

# Define the input and output directories
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
FILENAME = "Workout1.pdf"


def extract_markdown_from_pdf(pdf_path: str) -> str:
    """
    Uses Docling to convert a PDF file (scanned or native) into structured Markdown text.

    Args:
        pdf_path (str): Full path to the input PDF file.

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


if __name__ == "__main__":
    # Construct the full path to the input PDF
    pdf_path = os.path.join(RAW_DIR, FILENAME)

    # Extract Markdown content
    markdown = extract_markdown_from_pdf(pdf_path)

    # Define the output path for the Markdown file
    output_md_path = os.path.join(PROCESSED_DIR, FILENAME.replace(".pdf", ".md"))

    # Ensure the output directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Save the extracted Markdown content
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Markdown saved to: {output_md_path}")
