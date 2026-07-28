# System Architecture - THEMIS Compliance Engine

THEMIS (Automated Policy Compliance & Risk Auditing Engine) is designed as a distributed, agentic AI platform that processes high-throughput financial transactions against complex regulatory compliance frameworks (KYC, AML, Limits, Sanctions, PEP).

```
                                  +-----------------------+
                                  |   Client / Frontend   |
                                  |  Next.js + WebSocket  |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |    FastAPI Gateway    |
                                  |  (REST + WebSockets)  |
                                  +-----------+-----------+
                                              |
                                              v
                              +-------------------------------+
                              | LangGraph Multi-Agent Engine  |
                              +---------------+---------------+
                                              |
      +---------------------+-----------------+---------------------+---------------------+
      |                     |                 |                     |                     |
      v                     v                 v                     v                     v
+------------+       +------------+    +------------+        +------------+        +------------+
|  Agent 1   | ----> |  Agent 2   | -> |  Agent 3   | -----> |  Agent 4   | -----> |  Agent 5   |
|   Intake   |       | Policy RAG |    |Risk Analysis|       |  Decision  |        |Audit Logger|
+------------+       +------------+    +------------+        +------------+        +------------+
      |                     |                 |                     |                     |
      +---------------------+-----------------+---------------------+---------------------+
                                              |
                                              v
                              +-------------------------------+
                              |       Custom MCP Servers      |
                              | - Policy Retriever MCP        |
                              | - Email Alerter MCP           |
                              | - Audit Logger MCP            |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |   Storage & Cache Layer       |
                              | - SQLite/PostgreSQL Database  |
                              | - Chroma Vector Database      |
                              | - Redis / In-Memory Cache     |
                              +-------------------------------+
```

---

## 1. Multi-Agent Orchestration Layer

THEMIS uses **LangGraph** state graph routing to orchestrate 5 specialized autonomous AI agents:

1. **Intake Agent (Agent 1)**: Accepts raw JSON transaction payloads, validates schema completeness, extracts high-dimensional features (`is_high_value`, `is_sanctioned_country`, `is_unverified`, `is_new_account`, `pep_flag`), and tags risk vectors.
2. **Policy Retrieval Agent (Agent 2)**: Interrogates the RAG Vector DB store (ChromaDB) to retrieve exact policy sections and rules matching transaction attributes.
3. **Risk Analysis Agent (Agent 3)**: Synthesizes transaction attributes with retrieved policy guidelines using Claude / Gemini Generative AI reasoning to evaluate rule violations and severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
4. **Decision Engine Agent (Agent 4)**: Evaluates rule violation severity arrays, calculates confidence scores (0.0 to 1.0), and assigns final status (`APPROVED`, `REVIEW`, `ESCALATE`).
5. **Audit Logger Agent (Agent 5)**: Compiles end-to-end agent decision lineage into immutable compliance audit records (`AUD-xxxx`) persisted in the audit database.

---

## 2. RAG (Retrieval-Augmented Generation) Pipeline

- **Vector Database**: ChromaDB vector store persisting policy embeddings.
- **Embedding Model**: `SentenceTransformer("all-MiniLM-L6-v2")` with fallback feature hashing.
- **Ingestion Pipeline**: Processes policies, chunks content, attaches category tags (`KYC`, `AML`, `Limits`, `Sanctions`, `PEP`), and creates vector indices for sub-millisecond semantic retrieval.

---

## 3. Model Context Protocol (MCP) Servers

THEMIS exposes 3 modular MCP servers for tool orchestration:

1. **Policy Retriever MCP Server** (`port: 8001`): Exposes tool `search_policies(query, category, limit)` for semantic policy search over HTTP/JSON-RPC.
2. **Email Alerter MCP Server** (`port: 8002`): Exposes tool `send_violation_alert(transaction_id, violations, status)` for compliance notification dispatch.
3. **Audit Logger MCP Server** (`port: 8003`): Exposes tool `log_compliance_record(transaction_id, audit_data)` for structured audit record creation.
