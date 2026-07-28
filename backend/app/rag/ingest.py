import os
import json
from app.rag.vector_store import policy_vector_store

def ingest_policies():
    policies_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sample_policies.json")
    if os.path.exists(policies_path):
        with open(policies_path, "r", encoding="utf-8") as f:
            policies = json.load(f)
            policy_vector_store.add_policies(policies)
            print(f"Successfully ingested {len(policies)} policy documents into Vector Store.")

if __name__ == "__main__":
    ingest_policies()
