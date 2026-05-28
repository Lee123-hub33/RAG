from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from app.config import settings

# Load the embedding model (downloads ~80MB first time)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    """
    Convert text to vector (384 numbers).
    
    Args:
        text: Text to embed
    
    Returns:
        List of 384 floats
    
    Example:
        vector = embed_text("NDA must include definition")
        # [0.12, -0.45, 0.67, ..., 0.23]
    """
    
    # Get the vector
    embedding = model.encode(text)
    
    # Convert to list for storage
    return embedding.tolist()


def seed_rule_embeddings():
    """
    Generate embeddings for all compliance rules in database.
    Run this ONCE to populate embeddings.
    """
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all rules without embeddings
        result = conn.execute(text(
            "SELECT id, rule_text FROM compliance_rules WHERE embedding IS NULL"
        ))
        rules = result.fetchall()
        
        print(f"Embedding {len(rules)} rules...")
        
        # For each rule, generate embedding and store
        for rule_id, rule_text in rules:
            print(f"  Embedding rule {rule_id}...")
            
            # Generate embedding
            embedding = embed_text(rule_text)
            
            # Convert to string format for pgvector
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
            
            # Store in database using CAST
            conn.execute(text(
                "UPDATE compliance_rules SET embedding = CAST(:embedding AS vector) WHERE id = :id"
            ), {"embedding": embedding_str, "id": rule_id})
        
        conn.commit()
        print("✓ All rules embedded!")


def find_similar_rules(query_text: str, limit: int = 5) -> list[dict]:
    """
    Find compliance rules similar to query text.
    """
    
    # Generate embedding for query
    query_embedding = embed_text(query_text)
    
    # Convert list to string format for pgvector
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Search for similar rules using <=> operator
        result = conn.execute(text("""
            SELECT 
                id, 
                rule_text,
                (embedding <=> CAST(:embedding AS vector)) AS distance
            FROM compliance_rules
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """), {
            "embedding": embedding_str,
            "limit": limit
        })
        
        # Convert to list of dicts
        similar_rules = [
            {
                "id": row[0],
                "rule_text": row[1],
                "distance": float(row[2])
            }
            for row in result
        ]
        
        return similar_rules