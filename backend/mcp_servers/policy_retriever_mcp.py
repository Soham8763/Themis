from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

from app.rag.vector_store import policy_vector_store
from app.rag.ingest import ingest_policies

mcp_app = FastAPI(title="Policy Retriever MCP Server", version="1.0.0")

class SearchPoliciesRequest(BaseModel):
    query: str
    category: Optional[str] = None
    limit: int = 3

@mcp_app.on_event("startup")
async def startup():
    ingest_policies()

@mcp_app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "search_policies",
                "description": "Perform semantic vector search to retrieve relevant regulatory compliance policies.",
                "parameters": {
                    "query": "string - search query or transaction context",
                    "category": "optional string - KYC, AML, Limits, Sanctions, PEP",
                    "limit": "integer - top K results (default 3)"
                }
            }
        ]
    }

@mcp_app.post("/tools/search_policies")
async def search_policies_tool(req: SearchPoliciesRequest):
    results = policy_vector_store.search_policies(
        query=req.query,
        category_filter=req.category,
        top_k=req.limit
    )
    return {
        "status": "success",
        "count": len(results),
        "policies": results
    }

if __name__ == "__main__":
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001)
