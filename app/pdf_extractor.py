import pypdf
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """
    Read a PDF file and extract all text.
    
    Args:
        file_path: Path to PDF file (e.g., "/uploads/contract.pdf")
    
    Returns:
        One big string with all text from all pages
    
    Example:
        text = extract_text_from_pdf("/uploads/contract.pdf")
        print(text)  # "This is page 1... This is page 2..."
    """
    
    # Open the PDF file in read-binary mode
    with open(file_path, "rb") as pdf_file:
        # Create a PDF reader object
        pdf_reader = pypdf.PdfReader(pdf_file)
        
        # Extract text from each page
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            # Get text from this page
            page_text = page.extract_text()
            
            # Add a marker showing which page this is from
            full_text += f"\n--- Page {page_num + 1} ---\n"
            full_text += page_text
        
        return full_text
    

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Split long text into smaller overlapping chunks.
    
    Args:
        text: The full text to chunk
        chunk_size: How many characters per chunk (800)
        overlap: How many characters to repeat in next chunk (150)
    
    Returns:
        List of text chunks
    
    Example:
        text = "The parties agree to... blah blah blah... terms and conditions..."
        chunks = chunk_text(text, chunk_size=800, overlap=150)
        # chunks[0] = "The parties agree to... [800 chars]"
        # chunks[1] = "... blah blah blah... [800 chars]" (starts 150 chars before chunk[0] ends)
    """
    
    chunks = []
    
    # Start from position 0, step by (chunk_size - overlap) each time
    for i in range(0, len(text), chunk_size - overlap):
        # Extract chunk_size characters starting at position i
        chunk = text[i:i + chunk_size]
        
        # Only add if chunk has meaningful content (not just spaces)
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

    


    

