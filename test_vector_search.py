from app.embeddings import find_similar_rules

# Test query
query = "employment contract salary compensation"

print(f"Searching for: '{query}'\n")

# Find similar rules
results = find_similar_rules(query, limit=3)

# Print results
for i, result in enumerate(results, 1):
    print(f"{i}. Rule {result['id']}")
    print(f"   Text: {result['rule_text'][:80]}...")
    print(f"   Distance: {result['distance']:.4f}")
    print()