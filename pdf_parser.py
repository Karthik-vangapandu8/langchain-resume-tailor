import pypdf
import io
import re

def extract_text_from_pdf(pdf_source) -> str:
    """
    Extracts raw text from a PDF file path or file-like bytes stream using PyPDF.
    """
    if isinstance(pdf_source, str):
        reader = pypdf.PdfReader(pdf_source)
    elif isinstance(pdf_source, (bytes, io.BytesIO)):
        if isinstance(pdf_source, bytes):
            pdf_source = io.BytesIO(pdf_source)
        reader = pypdf.PdfReader(pdf_source)
    else:
        raise ValueError("Unsupported PDF input type. Expected file path (str) or bytes stream.")

    extracted_text = []
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            extracted_text.append(text)

    full_text = "\n".join(extracted_text)
    
    # Basic cleaning (normalize multiple newlines & spaces)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    return full_text.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        text = extract_text_from_pdf(pdf_path)
        print(f"--- Extracted Text ({len(text)} characters) ---")
        print(text[:1000] + "\n..." if len(text) > 1000 else text)
    else:
        print("pdf_parser.py module ready.")
