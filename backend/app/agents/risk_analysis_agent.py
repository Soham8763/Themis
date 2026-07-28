import os
import json
import datetime
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.config import settings

def evaluate_deterministic_rules(features: Dict[str, Any], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    violations = []
    amount = features.get("amount", 0.0)
    kyc_level = features.get("kyc_level", 1)
    account_age = features.get("account_age_days", 0)
    tx_type = features.get("transaction_type", "").lower()
    dest_country = features.get("destination_country", "").lower()
    pep_flag = features.get("pep_flag", False)
    is_cross_border = features.get("is_cross_border", False)
    dual_approval = features.get("dual_approval", False)
    sow_verified = features.get("sow_verified", False)

    # 1. Sanctions Policy (POL-SNC-004)
    if dest_country in {"iran", "north korea", "syria", "cuba", "crimea"}:
        violations.append({
            "rule_id": "SNC-R1",
            "rule_name": "OFAC Comprehensive Sanctions Block",
            "category": "Sanctions",
            "severity": "CRITICAL",
            "reason": f"Destination country '{features.get('destination_country')}' is subject to OFAC comprehensive sanctions and asset block.",
            "confidence": 1.0
        })
    elif dest_country in {"myanmar", "yemen", "south sudan"}:
        violations.append({
            "rule_id": "SNC-R2",
            "rule_name": "FATF High-Risk Jurisdiction EDD",
            "category": "Sanctions",
            "severity": "HIGH",
            "reason": f"Destination country '{features.get('destination_country')}' is listed on FATF high-risk jurisdiction list requiring Enhanced Due Diligence.",
            "confidence": 0.95
        })

    # 2. KYC Policy (POL-KYC-001)
    if kyc_level == 0 and amount > 2500:
        violations.append({
            "rule_id": "KYC-R1",
            "rule_name": "Unverified Account High-Value Limit",
            "category": "KYC",
            "severity": "HIGH",
            "reason": f"Account has incomplete KYC verification (Level 0) but transaction amount (${amount:,.2f}) exceeds $2,500 threshold.",
            "confidence": 1.0
        })
    if account_age < 30 and tx_type == "wire_transfer" and amount > 10000:
        violations.append({
            "rule_id": "KYC-R2",
            "rule_name": "New Account Large Wire Threshold",
            "category": "KYC",
            "severity": "MEDIUM",
            "reason": f"Account age ({account_age} days) is under 30 days and outbound wire transfer (${amount:,.2f}) exceeds $10,000.",
            "confidence": 0.90
        })

    # 3. AML Policy (POL-AML-002)
    if amount >= 10000:
        violations.append({
            "rule_id": "AML-R1",
            "rule_name": "Mandatory CTR Threshold",
            "category": "AML",
            "severity": "LOW",
            "reason": f"Transaction amount (${amount:,.2f}) meets or exceeds $10,000 Currency Transaction Report (CTR) regulatory threshold.",
            "confidence": 1.0
        })
    if tx_type == "cash_deposit" and amount > 50000:
        violations.append({
            "rule_id": "AML-R2",
            "rule_name": "Excessive Cash Deposit Warning",
            "category": "AML",
            "severity": "HIGH",
            "reason": f"Cash deposit amount (${amount:,.2f}) exceeds $50,000 threshold requiring senior compliance approval.",
            "confidence": 0.95
        })

    # 4. Limits Policy (POL-LMT-003)
    if amount > 500000:
        violations.append({
            "rule_id": "LMT-R2",
            "rule_name": "Executive Review Threshold",
            "category": "Limits",
            "severity": "CRITICAL",
            "reason": f"Transaction amount (${amount:,.2f}) exceeds $500,000 threshold requiring Executive Committee Review.",
            "confidence": 1.0
        })
    elif amount > 100000 and not dual_approval:
        violations.append({
            "rule_id": "LMT-R1",
            "rule_name": "High Value Dual Authorization Required",
            "category": "Limits",
            "severity": "HIGH",
            "reason": f"Outbound wire transfer (${amount:,.2f}) exceeds $100,000 but lacks mandatory dual-sign-off authorization.",
            "confidence": 0.95
        })

    # 5. PEP Policy (POL-PEP-005)
    if pep_flag:
        if is_cross_border and amount > 25000 and not sow_verified:
            violations.append({
                "rule_id": "PEP-R1",
                "rule_name": "PEP Cross-Border SoW Check",
                "category": "PEP",
                "severity": "HIGH",
                "reason": f"Politically Exposed Person (PEP) cross-border transfer (${amount:,.2f}) lacks verified Source of Wealth documentation.",
                "confidence": 0.95
            })
        else:
            violations.append({
                "rule_id": "PEP-R2",
                "rule_name": "PEP Activity Flag",
                "category": "PEP",
                "severity": "MEDIUM",
                "reason": "Transaction initiated by Politically Exposed Person (PEP); requires mandatory compliance notification.",
                "confidence": 0.85
            })

    return violations

def call_gemini_ai_reasoning(features: Dict[str, Any], policies: List[Dict[str, Any]], rule_violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calls Gemini API to perform natural language risk evaluation and enhance reasoning.
    Falls back gracefully to rule-based evaluation if API key is missing or call fails.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return rule_violations

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        prompt = f"""You are a Senior Financial Compliance Auditor. Analyze the following transaction against company policies and evaluate risk violations.

Transaction Details:
{json.dumps(features, indent=2)}

Relevant Policies:
{json.dumps(policies, indent=2)}

Pre-calculated Deterministic Violations:
{json.dumps(rule_violations, indent=2)}

Task: Review the transaction against the policies. Return ONLY a JSON array of violations. Each object must have:
- "rule_id": string
- "rule_name": string
- "category": string
- "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
- "reason": detailed AI reasoning string explaining why this violates policy
- "confidence": float between 0.0 and 1.0

Output valid JSON only with no markdown formatting or commentary.
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        parsed_violations = json.loads(text)
        if isinstance(parsed_violations, list):
            return parsed_violations
    except Exception:
        pass

    return rule_violations

def risk_analysis_agent(state: AgentState) -> AgentState:
    """
    Agent 3: Risk Analysis Agent
    Applies policies using rule evaluation and optional Gemini AI reasoning to identify compliance violations.
    """
    features = state.get("extracted_features", {})
    policies = state.get("relevant_policies", [])
    logs = state.get("agent_logs", [])

    deterministic_violations = evaluate_deterministic_rules(features, policies)
    final_violations = call_gemini_ai_reasoning(features, policies, deterministic_violations)

    critical_count = sum(1 for v in final_violations if v.get("severity") == "CRITICAL")
    high_count = sum(1 for v in final_violations if v.get("severity") == "HIGH")

    log_entry = {
        "agent_id": "agent-3-analysis",
        "agent_name": "Risk Analysis Agent",
        "output": {
            "violations_found": len(final_violations),
            "critical_violations": critical_count,
            "high_violations": high_count,
            "violations": final_violations
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        **state,
        "violations": final_violations,
        "agent_logs": logs + [log_entry]
    }
