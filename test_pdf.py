from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

os.makedirs("uploads", exist_ok=True)

pdf_path = "uploads/bad_contract.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

# Write VIOLATIONS in the PDF
c.drawString(100, 750, "EMPLOYMENT AGREEMENT")
c.drawString(100, 700, "")
c.drawString(100, 650, "This employment agreement has the following terms:")
c.drawString(100, 600, "")
c.drawString(100, 550, "1. Employee must work 60 hours per week")
c.drawString(100, 500, "2. No compensation is provided")
c.drawString(100, 450, "3. No benefits or insurance")
c.drawString(100, 400, "4. No termination clause specified")
c.drawString(100, 350, "5. Unlimited non-compete: Cannot work anywhere for 10 years")
c.drawString(100, 300, "")
c.drawString(100, 250, "DATA HANDLING:")
c.drawString(100, 200, "No data protection or privacy measures are included")

c.save()
print(f"✓ Created BAD contract: {pdf_path}")