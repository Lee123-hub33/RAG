from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from app.pdf_extractor import extract_text_from_pdf, chunk_text
from app.embeddings import find_similar_rules
from app.llm import analyze_chunk_rule_based

app = FastAPI(title="Compliance RAG")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Full RAG pipeline with rule-based matching:
    1. Extract PDF text
    2. Chunk text
    3. Find similar rules (vector search)
    4. Analyze with keyword matching
    5. Return findings
    """
    
    # Step 1: Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    print(f"✓ File saved: {file_path}")
    
    # Step 2: Extract text
    try:
        full_text = extract_text_from_pdf(file_path)
        print(f"✓ Extracted {len(full_text)} characters")
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"PDF extraction failed: {str(e)}"}
        )
    
    # Step 3: Chunk text
    chunks = chunk_text(full_text, chunk_size=800, overlap=150)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Step 4: Analyze each chunk
    all_findings = []
    for i, chunk in enumerate(chunks):
        print(f"  Analyzing chunk {i+1}/{len(chunks)}...")
        
        # Find similar rules (vector search)
        similar_rules = find_similar_rules(chunk, limit=5)
        
        # Analyze with rule-based matching (fast, free)
        report = analyze_chunk_rule_based(chunk, similar_rules)
        
        # Add findings
        all_findings.extend(report.findings)
    
    print(f"✓ Found {len(all_findings)} compliance issues")
    
    # Step 5: Return results
    return {
        "status": "success",
        "filename": file.filename,
        "file_size_chars": len(full_text),
        "chunks_processed": len(chunks),
        "findings_count": len(all_findings),
        "findings": [
            {
                "rule_id": f.rule_id,
                "severity": f.severity,
                "description": f.description,
                "evidence": f.evidence
            }
            for f in all_findings
        ]
    }

@app.get("/")
async def root():
    return {
        "message": "Compliance RAG API running",
        "method": "Rule-based keyword matching (free, fast, reliable)"
    }