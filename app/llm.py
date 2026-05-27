import json
from pydantic import BaseModel, Field


class ComplianceFinding(BaseModel):
    """A single compliance finding"""
    rule_id: int = Field(..., description="ID of the compliance rule")
    severity: str = Field(..., description="HIGH, MEDIUM, or LOW")
    description: str = Field(..., description="What was violated")
    evidence: str = Field(..., description="Quote from contract showing violation")


class ComplianceReport(BaseModel):
    """Analysis report for a contract chunk"""
    findings: list[ComplianceFinding] = Field(
        ..., 
        description="List of compliance violations found"
    )


def analyze_chunk_rule_based(
    chunk_text: str, 
    applicable_rules: list[dict]
) -> ComplianceReport:
    """
    Analyze contract chunk using keyword matching (free, fast, reliable).
    
    Args:
        chunk_text: Contract text to analyze
        applicable_rules: Similar rules from vector search
    
    Returns:
        ComplianceReport with findings
    """
    
    findings = []
    chunk_lower = chunk_text.lower()
    
    # Define violation keywords for each rule
    violation_keywords = {
        1: {  # NDA rule
            "keywords": ["no nda", "no confidential", "no definition", "undefined confidential"],
            "severity": "HIGH",
            "description": "NDA missing required definition of confidential information"
        },
        2: {  # Employment rule
            "keywords": ["no compensation", "without pay", "unpaid", "no salary", "no benefits", "50 hours"],
            "severity": "HIGH",
            "description": "Employment contract missing compensation or benefits clause"
        },
        3: {  # SLA rule
            "keywords": ["no uptime", "no sla", "no service level", "no response time"],
            "severity": "MEDIUM",
            "description": "Service agreement missing SLA or uptime definitions"
        },
        4: {  # Data rule
            "keywords": ["no data protection", "no gdpr", "no privacy", "no data processing"],
            "severity": "HIGH",
            "description": "Data agreement missing GDPR or data protection compliance"
        },
        5: {  # Service rule
            "keywords": ["no liability", "unlimited liability", "no cap", "no limit"],
            "severity": "MEDIUM",
            "description": "Service agreement missing liability caps or limits"
        },
    }
    
    # Check each rule's keywords
    for rule_id, rule_config in violation_keywords.items():
        for keyword in rule_config["keywords"]:
            if keyword in chunk_lower:
                # Find the evidence (context around keyword)
                keyword_pos = chunk_lower.find(keyword)
                start = max(0, keyword_pos - 80)
                end = min(len(chunk_text), keyword_pos + len(keyword) + 80)
                evidence = chunk_text[start:end].strip()
                
                # Create finding
                finding = ComplianceFinding(
                    rule_id=rule_id,
                    severity=rule_config["severity"],
                    description=rule_config["description"],
                    evidence=evidence
                )
                
                findings.append(finding)
                break  # Only one violation per rule per chunk
    
    return ComplianceReport(findings=findings)