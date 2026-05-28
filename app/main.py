from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Document, Base
from app.tasks import process_document

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create FastAPI app
app = FastAPI(title="Compliance RAG - Async")

# Create uploads folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dependency: get database session
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF and queue for processing.
    Returns immediately with document_id.
    """
    
    db = Session(engine)
    
    try:
        # Step 1: Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"✓ File saved: {file_path}")
        
        # Step 2: Create document record
        doc = Document(
            filename=file.filename,
            file_path=file_path,
            status="PENDING"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        print(f"✓ Document {doc.id} created in database")
        
        # Step 3: Queue background job
        task = process_document.delay(doc.id, file_path)
        print(f"✓ Job queued with task_id: {task.id}")
        
        # Step 4: Return immediately (202 Accepted)
        return {
            "status": "ACCEPTED",
            "document_id": doc.id,
            "filename": file.filename,
            "message": "Processing started. Use GET /document/{id} to check status"
        }
    
    except Exception as e:
        print(f"✗ Error uploading file: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    finally:
        db.close()

@app.get("/document/{document_id}")
async def get_document(document_id: int):
    """
    Check document processing status and get findings.
    """
    
    db = Session(engine)
    
    try:
        # Get document
        doc = db.query(Document).filter_by(id=document_id).first()
        
        if not doc:
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
            )
        
        # Get findings (only if completed)
        findings = []
        if doc.status == "COMPLETED":
            from app.models import AuditFinding
            findings_data = db.query(AuditFinding).filter_by(document_id=document_id).all()
            findings = [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "description": f.description,
                    "evidence": f.evidence
                }
                for f in findings_data
            ]
        
        # Return status
        return {
            "document_id": document_id,
            "filename": doc.filename,
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "completed_at": doc.completed_at.isoformat() if doc.completed_at else None,
            "error_message": doc.error_message,
            "findings_count": len(findings),
            "findings": findings
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        db.close()

@app.get("/")
async def root():
    return {
        "message": "Compliance RAG API - Async Processing",
        "endpoints": {
            "POST /upload": "Upload PDF (returns immediately with document_id)",
            "GET /document/{id}": "Check status and get findings"
        }
    }