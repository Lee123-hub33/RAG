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
    """
    
    findings = []
    chunk_lower = chunk_text.lower()
    
    # Define violation keywords for each rule
    # These look for RED FLAGS (things that shouldn't be there or are missing)
    violation_keywords = {
        1: {  # NDA rule
            "keywords": ["nda", "confidential", "proprietary", "secret"],
            "red_flags": ["no confidential", "undefined confidential", "no definition"],
            "severity": "HIGH",
            "description": "NDA clause needs clearer confidential information definition"
        },
        2: {  # Employment rule
            "keywords": ["employment", "employee", "work", "salary", "compensation", "payment"],
            "red_flags": ["no salary", "no compensation", "without pay", "unpaid", "no benefits"],
            "severity": "HIGH",
            "description": "Employment contract should specify salary and benefits"
        },
        3: {  # SLA rule
            "keywords": ["service level", "sla", "uptime", "availability", "response time"],
            "red_flags": ["no uptime", "no sla", "no service level", "no response time"],
            "severity": "MEDIUM",
            "description": "Service agreement needs defined SLA and uptime guarantees"
        },
        4: {  # Data rule
            "keywords": ["data", "processing", "privacy", "gdpr", "protection"],
            "red_flags": ["no data protection", "no gdpr", "no privacy"],
            "severity": "HIGH",
            "description": "Data processing agreement should include GDPR compliance"
        },
        5: {  # Service rule
            "keywords": ["liability", "indemnity", "damage", "limitation"],
            "red_flags": ["unlimited liability", "no liability cap", "no limit"],
            "severity": "MEDIUM",
            "description": "Service agreement should cap liability exposure"
        },
    }
    
    # Check each rule
    for rule_id, rule_config in violation_keywords.items():
        # First check if red flags exist (explicit violations)
        for red_flag in rule_config["red_flags"]:
            if red_flag in chunk_lower:
                keyword_pos = chunk_lower.find(red_flag)
                start = max(0, keyword_pos - 80)
                end = min(len(chunk_text), keyword_pos + len(red_flag) + 80)
                evidence = chunk_text[start:end].strip()
                
                finding = ComplianceFinding(
                    rule_id=rule_id,
                    severity=rule_config["severity"],
                    description=rule_config["description"],
                    evidence=evidence
                )
                findings.append(finding)
                break
    
    return ComplianceReport(findings=findings)