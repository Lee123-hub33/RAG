from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
        
        result = conn.execute(text("SELECT COUNT(*) FROM compliance_rules"))
        count = result.scalar()
        print(f"✓ Found {count} compliance rules")
        
        result = conn.execute(text("SELECT id, rule_text FROM compliance_rules LIMIT 3"))
        print("\n✓ Sample rules:")
        for row in result:
            print(f"  - {row[0]}: {row[1][:50]}...")
            
except Exception as e:
    print(f"✗ Error: {e}")