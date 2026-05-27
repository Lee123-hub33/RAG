from app.pdf_extractor import extract_text_from_pdf

text = extract_text_from_pdf("uploads/test_contract.pdf")
print(text)
print(f"\nTotal characters: {len(text)}")