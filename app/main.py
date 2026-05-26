from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from app.pdf_extractor import extract_text_from_pdf, chunk_text

# Create the FastAPI app
app = FastAPI(title="Compliance RAG")

# Create uploads folder if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint: User uploads a PDF file
    
    1. Saves the PDF to disk
    2. Extracts text from PDF
    3. Chunks the text
    4. Returns the chunks
    
    Usage:
        curl -X POST -F "file=@contract.pdf" http://localhost:8000/upload
    """
    
    # Step 1: Save the uploaded file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()  # Read the file content
        f.write(content)  # Write to disk
    
    print(f"✓ File saved to: {file_path}")
    
    # Step 2: Extract text from PDF
    try:
        full_text = extract_text_from_pdf(file_path)
        print(f"✓ Extracted {len(full_text)} characters from PDF")
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to extract PDF: {str(e)}"}
        )
    
    # Step 3: Chunk the text
    chunks = chunk_text(full_text, chunk_size=800, overlap=150)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Step 4: Return response
    return {
        "status": "success",
        "filename": file.filename,
        "text_length": len(full_text),
        "chunks_count": len(chunks),
        "sample_chunk": chunks[0][:200] + "..." if chunks else "No chunks"
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Compliance RAG API is running"}