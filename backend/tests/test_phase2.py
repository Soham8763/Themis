import pytest
from app.rag.vector_store import VectorPolicyStore
from app.rag.ingest import ingest_policies

def test_vector_store_policy_search():
    store = VectorPolicyStore(persist_dir="./test_chroma_db")
    sample_policies = [
        {
            "policy_id": "POL-SNC-004",
            "category": "Sanctions",
            "title": "Sanctioned & High-Risk Jurisdictions Policy",
            "version": "4.2",
            "content": "Transactions involving OFAC comprehensive sanctions countries (Iran, North Korea, Syria) are prohibited."
        },
        {
            "policy_id": "POL-LMT-003",
            "category": "Limits",
            "title": "Transaction Thresholds Policy",
            "version": "1.4",
            "content": "Single outbound wire transfers exceeding $100,000 USD require dual-sign-off authorization."
        }
    ]
    store.add_policies(sample_policies)
    
    results = store.search_policies(query="wire transfer over 100k limit", top_k=2)
    assert len(results) >= 1
    top_policy = results[0]
    assert top_policy["policy_id"] in ["POL-LMT-003", "POL-SNC-004"]
    assert "relevance_score" in top_policy
