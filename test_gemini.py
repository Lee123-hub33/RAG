from app.llm import analyze_chunk_with_gemini
from app.embeddings import find_similar_rules

# Sample contract chunk
chunk = """
EMPLOYMENT AGREEMENT

This agreement is between Company XYZ and Employee ABC.

The employee agrees to work 50 hours per week without additional compensation.
No health insurance benefits are provided.
The employee may not work for any competitor for 5 years after termination.
"""

print("Finding similar rules...")
rules = find_similar_rules(chunk, limit=3)

print("\nAnalyzing with Gemini...")
report = analyze_chunk_with_gemini(chunk, rules)

print("\nFindings:")
if report.findings:
    for finding in report.findings:
        print(f"\n  Rule {finding.rule_id}: {finding.severity}")
        print(f"  Issue: {finding.description}")
        print(f"  Evidence: {finding.evidence}")
else:
    print("  No violations found")