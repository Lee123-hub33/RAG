from app.celery_app import celery_app
from app.pdf_extractor import extract_text_from_pdf, chunk_text
from app.embeddings import find_similar_rules
from app.llm import analyze_chunk_rule_based
from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models import Document, AuditFinding, DocumentChunk, Base
from datetime import datetime

# Create database engine
engine = create_engine(settings.DATABASE_URL)

@celery_app.task(bind=True)
def process_document(self, document_id: int, file_path: str):
    """
    Background job to process PDF and generate findings.
    
    Args:
        document_id: ID of document in database
        file_path: Path to uploaded PDF
    """
    
    db = Session(engine)
    
    try:
        # Get document
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        # Update status to PROCESSING
        doc.status = "PROCESSING"
        db.commit()
        print(f"✓ Processing document {document_id}")
        
        # Step 1: Extract text from PDF
        print(f"  Extracting text...")
        full_text = extract_text_from_pdf(file_path)
        
        # Step 2: Chunk text
        print(f"  Chunking text...")
        chunks = chunk_text(full_text, chunk_size=800, overlap=150)
        
        # Save chunks to database
        for i, chunk in enumerate(chunks):
            chunk_obj = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                chunk_text=chunk
            )
            db.add(chunk_obj)
        db.commit()
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Step 3: Analyze each chunk
        all_findings = []
        for i, chunk in enumerate(chunks):
            print(f"  Analyzing chunk {i+1}/{len(chunks)}...")
            
            # Find similar rules
            similar_rules = find_similar_rules(chunk, limit=5)
            
            # Analyze with rule-based matching
            report = analyze_chunk_rule_based(chunk, similar_rules)
            
            # Save findings to database
            for finding in report.findings:
                audit = AuditFinding(
                    document_id=document_id,
                    rule_id=finding.rule_id,
                    severity=finding.severity,
                    description=finding.description,
                    evidence=finding.evidence
                )
                db.add(audit)
                all_findings.append(finding)
        
        db.commit()
        print(f"  ✓ Found {len(all_findings)} violations")
        
        # Update document status to COMPLETED
        doc.status = "COMPLETED"
        doc.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"✓ Document {document_id} processing complete!")
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks),
            "findings_count": len(all_findings)
        }
    
    except Exception as e:
        print(f"✗ Error processing document {document_id}: {e}")
        doc = db.query(Document).filter_by(id=document_id).first()
        if doc:
            doc.status = "FAILED"
            doc.error_message = str(e)
            db.commit()
        raise
    
    finally:
        db.close()