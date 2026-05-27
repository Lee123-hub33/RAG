from app.llm import analyze_chunk_rule_based
from app.embeddings import find_similar_rules

# Sample contract with violations
chunk = """
EMPLOYMENT AGREEMENT

This agreement is between Company XYZ and Employee ABC.

The employee agrees to work 50 hours per week without pay.
No health insurance benefits are provided.
The employee may not work for any competitor for 5 years.

CONFIDENTIALITY: This agreement does not define what "confidential information" means.

SERVICE LEVEL AGREEMENT: No uptime or response time guarantees provided.
"""

print("=" * 60)
print("RULE-BASED COMPLIANCE ANALYSIS")
print("=" * 60)

print("\n1. Finding similar rules (vector search)...")
rules = find_similar_rules(chunk, limit=5)
print(f"   Found {len(rules)} similar rules")

print("\n2. Analyzing with keyword matching...")
report = analyze_chunk_rule_based(chunk, rules)

print(f"\n3. Results: {len(report.findings)} violations found\n")

if report.findings:
    for i, finding in enumerate(report.findings, 1):
        print(f"Violation {i}:")
        print(f"  Rule ID: {finding.rule_id}")
        print(f"  Severity: {finding.severity}")
        print(f"  Issue: {finding.description}")
        print(f"  Evidence: \"{finding.evidence}\"")
        print()
else:
    print("No violations found")

print("=" * 60)