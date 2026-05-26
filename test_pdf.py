from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a simple test PDF
pdf_path = "uploads/test_contract.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

# Write text to PDF
c.drawString(100, 750, "EMPLOYMENT CONTRACT")
c.drawString(100, 700, "")
c.drawString(100, 650, "This is a test employment contract.")
c.drawString(100, 600, "")
c.drawString(100, 550, "1. The employer agrees to pay the employee $50,000 per year.")
c.drawString(100, 500, "2. The employee agrees to work 40 hours per week.")
c.drawString(100, 450, "3. Either party may terminate with 2 weeks notice.")
c.drawString(100, 400, "4. The employee will receive health insurance benefits.")
c.drawString(100, 350, "5. Non-compete clause: Employee cannot work for competitors for 1 year.")

# Save the PDF
c.save()
print(f"✓ Created test PDF: {pdf_path}")