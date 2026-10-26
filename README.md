# Legacy Modernization POV

**AI-Powered Legacy Application Analysis, Dependency GraphRAG, Migration Disposition, and Guardian Validation**

## 1. Project Overview

This project is a local Proof of Value (POV) that demonstrates how AI and graph-based dependency analysis can support enterprise legacy application modernization.

The system analyzes synthetic legacy SQL Server schemas, table mappings, and account data to identify potential migration issues. It then enriches those findings with application dependencies, uses Google Gemini to recommend remediation actions, and applies deterministic Guardian checks before generating a modernization assessment report.

The project is designed as a learning and demonstration environment. It does not connect to production systems or execute database migrations.

## 2. Objectives

- Identify legacy database schema differences and migration risks.
- Detect cross-tenant identifier overlaps.
- Analyze source-to-target table and column mappings.
- Build a dependency graph of database objects, applications, and ETL jobs.
- Use GraphRAG-style evidence retrieval to enrich migration findings.
- Generate AI-assisted modernization recommendations.
- Validate recommendations using deterministic Guardian rules.
- Require human review for unresolved risks.
- Generate a consolidated migration assessment report.

## 3. High-Level Architecture

```text
         LEGACY APPLICATION DATA
                   |
       +-----------+-----------+
       |           |           |
   SQL Schemas   CSV Data   Table Mappings
       |           |           |
       +-----------+-----------+
                   |
                   v
          DETECTION ENGINE
                   |
          Migration Findings
                   |
                   v
          DEPENDENCY GRAPH
             (NetworkX)
                   |
                   v
          EVIDENCE RETRIEVAL
           (GraphRAG-style)
                   |
                   v
          GEMINI LLM REASONER
                   |
          Risks + Dispositions
                   |
                   v
          GUARDIAN VALIDATOR
                   |
       +-----------+-----------+
       |                       |
  Basic Checks Passed     Review Required
       |                       |
       +-----------+-----------+
                   |
                   v
          ASSESSMENT REPORT
                   |
                   v
             HUMAN REVIEW
```

The Guardian does not authorize migration execution. All findings remain subject to appropriate human review.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Development environment | VS Code, macOS Terminal |
| Schema analysis | Python-based SQL parsing |
| Dependency graph | NetworkX |
| Graph evidence retrieval | Custom Python retriever |
| LLM | Google Gemini API |
| LLM SDK | `google-genai` |
| Structured responses | Pydantic |
| Guardian | Python deterministic validation |
| Testing | Python `unittest` |
| Output formats | JSON, Markdown |
| Future graph database | Amazon Neptune |

## 5. Project Structure

```text
legacy-modernization-pov/
|
|-- sample_legacy/
|   |-- legacy_schema.sql
|   |-- target_schema.sql
|   |-- accounts.csv
|   |-- table_mappings.json
|   |-- dependencies.json
|
|-- src/
|   |-- main.py
|   |-- schema_scanner.py
|
|-- graph/
|   |-- __init__.py
|   |-- graph_builder.py
|
|-- rag/
|   |-- __init__.py
|   |-- retriever.py
|
|-- reasoning/
|   |-- __init__.py
|   |-- disposition_engine.py
|
|-- llm/
|   |-- __init__.py
|   |-- test_gemini.py
|   |-- migration_reasoner.py
|
|-- guardian/
|   |-- __init__.py
|   |-- validator.py
|   |-- llm_validator.py
|
|-- reports/
|   |-- generate_report.py
|   |-- modernization_assessment.md
|
|-- outputs/
|   |-- findings.json
|   |-- enriched_findings.json
|   |-- dispositions.json
|   |-- validated_dispositions.json
|   |-- llm_recommendations.json
|   |-- validated_llm_recommendations.json
|
|-- tests/
|   |-- test_retriever.py
|
|-- .venv/
|-- README.md
```

Some local backup files may also be present.

## 6. Processing Stages

### Stage 1 — Legacy Data and Schema Scanning

**Module:** `src/main.py`

The Detection Engine analyzes source and target database schemas, table mappings, and sample account data.

It identifies:

- `CROSS_TENANT_ID_OVERLAP`
- `COLUMN_TYPE_DRIFT`
- `SOURCE_COLUMN_UNMAPPED`
- `SOURCE_ONLY_TABLE`, when no matching target table or declared mapping exists

The source-only detection logic was updated to account for renamed tables.

Example mappings:

```text
CustomerAccounts   -> Accounts
LegacyTransactions -> Transactions
```

**Output:** `outputs/findings.json`

### Stage 2 — Dependency Graph Construction

**Module:** `graph/graph_builder.py`

NetworkX represents relationships among database tables, stored procedures, ETL jobs, and applications.

Example:

```text
CustomerAccounts
    |
    +-- GetCustomerAccounts
    |
    +-- AccountService
    |
    +-- AccountLoadJob
```

The graph supports dependency impact analysis, helping identify components that may be affected by schema changes.

The current implementation uses an in-memory NetworkX graph rather than a managed graph database.

### Stage 3 — GraphRAG-Style Evidence Retrieval

**Module:** `rag/retriever.py`

The retriever combines detection findings with relevant graph dependencies.

Example:

```text
Finding: COLUMN_TYPE_DRIFT
Object: CustomerAccounts

Graph Status: EVIDENCE_FOUND

Impacted Components:
- AccountLoadJob
- AccountService
- GetCustomerAccounts
```

If a finding lacks sufficient table context, the retriever reports that limitation rather than inventing dependencies.

**Output:** `outputs/enriched_findings.json`

### Stage 4 — Rule-Based Migration Disposition

**Module:** `reasoning/disposition_engine.py`

The rule-based engine assigns review actions based on finding categories.

| Finding type | Disposition |
|---|---|
| Cross-tenant ID overlap | `REVIEW_ID_NAMESPACE_POLICY` |
| Column type drift | `REVIEW_SCHEMA_TRANSFORMATION` |
| Unmapped source column | `REVIEW_COLUMN_MAPPING` |
| Source-only table | `REVIEW_MIGRATION_MAPPING` |

**Output:** `outputs/dispositions.json`

This deterministic component provides a baseline for comparison with LLM recommendations.

### Stage 5 — Gemini LLM Migration Reasoning

**Module:** `llm/migration_reasoner.py`

Google Gemini analyzes enriched findings and produces structured recommendations.

Each recommendation contains:

```json
{
  "disposition": "REVIEW_SCHEMA_TRANSFORMATION",
  "reason": "Explanation based on supplied evidence",
  "risks": [
    "Potential application compatibility issue"
  ],
  "next_steps": [
    "Validate the schema transformation",
    "Perform regression testing"
  ],
  "human_approval_required": true
}
```

The LLM is instructed to use supplied evidence, avoid inventing dependencies, and require human approval.

The integration includes retry handling for temporary API errors such as HTTP 503 and HTTP 429, with delays between requests.

**Output:** `outputs/llm_recommendations.json`

### Stage 6 — Guardian Validation

**Modules:**
- `guardian/validator.py`
- `guardian/llm_validator.py`

The Guardian performs deterministic checks on proposed migration dispositions.

Checks include:

- Allowed disposition for each finding type
- Required human approval
- Selected graph dependency consistency
- Conflicts between source-only findings and explicit table mappings
- Missing target ID namespace policy
- Missing or invalid LLM recommendations

Guardian statuses include:

- `BASIC_CHECKS_PASSED`
- `REVIEW_REQUIRED`

A basic check pass is not a migration approval. The Guardian does not independently verify every natural-language claim made by Gemini.

All generated recommendations retain:

```json
{
  "execution_authorized": false
}
```

**Output:** `outputs/validated_llm_recommendations.json`

### Stage 7 — Modernization Assessment Report

**Module:** `reports/generate_report.py`

The report generator produces a Markdown document containing:

- Executive summary
- Finding categories and counts
- AI-recommended dispositions
- Dependency evidence
- Migration risks
- Recommended next steps
- Guardian validation outcomes
- Human-review requirements
- Known limitations

**Output:** `reports/modernization_assessment.md`

## 7. Current POV Results

The latest completed run produced:

| Metric | Result |
|---|---:|
| Total findings | 7 |
| Cross-tenant ID overlaps | 1 |
| Column type drift findings | 4 |
| Unmapped source column findings | 2 |
| Findings with graph evidence | 6 |
| Gemini analyses completed | 7 |
| Guardian basic checks passed | 6 |
| Guardian review required | 1 |
| Migration executions authorized | 0 |

The cross-tenant finding involves account ID `1001`, which appears in the synthetic `LPL` and `PARTNER` tenant records.

The Guardian flagged:

```text
TARGET_ID_POLICY_NOT_VERIFIED
```

The system correctly requires human review because the target ID namespace policy is unknown.

## 8. Local Setup

### Prerequisites

- macOS, Linux, or another environment capable of running Python
- Python 3.11 or later recommended
- Git
- VS Code or another editor
- Google Gemini API key
- Internet connection for Gemini API calls

### Open the project

```bash
cd ~/Documents/lpl-practice/legacy-modernization-pov
```

### Activate the virtual environment

```bash
source .venv/bin/activate
```

The existing development environment uses Python 3.9 and may display end-of-life and LibreSSL warnings. Upgrading to a supported Python version is recommended.

### Install Python dependencies

For a fresh compatible virtual environment:

```bash
python -m pip install networkx google-genai pydantic
```

### Configure Gemini

Obtain an API key from Google AI Studio and configure it in your Terminal session.

For macOS zsh:

```bash
read -s "GEMINI_API_KEY?Paste Gemini API key: "
echo
export GEMINI_API_KEY
```

Do not hardcode API keys in source files or commit them to Git.

Model availability, rate limits, and pricing depend on the Google account and API configuration.

## 9. Run the Complete Pipeline

Run these commands from the project root.

### 1. Run the Detection Engine

```bash
python -m src.main
```

### 2. Enrich Findings with Graph Evidence

```bash
python -m rag.retriever
```

### 3. Generate Rule-Based Dispositions

```bash
python -m reasoning.disposition_engine
```

### 4. Run the Rule-Based Guardian

```bash
python -m guardian.validator
```

### 5. Test the Gemini Connection

```bash
python -u -m llm.test_gemini
```

### 6. Run Gemini on Migration Findings

```bash
python -u -m llm.migration_reasoner
```

### 7. Validate LLM Recommendations

```bash
python -m guardian.llm_validator
```

### 8. Generate the Assessment Report

```bash
python -m reports.generate_report
```

### 9. Open the Report

On macOS:

```bash
open -a "Visual Studio Code" reports/modernization_assessment.md
```

Use `Command + Shift + V` in VS Code for Markdown preview.

## 10. Run Tests

Execute the existing unit tests:

```bash
python -m unittest discover -s tests -v
```

The initial retriever test suite contains two tests. Additional unit and integration tests are recommended before extending the project.

## 11. Example Migration Scenario

**Scenario:** Migrating the legacy `CustomerAccounts` table to the target `Accounts` table.

The modernization process identifies schema differences and retrieves related dependencies.

**Dependency evidence:**

```text
CustomerAccounts
    |
    +-- AccountLoadJob
    +-- AccountService
    +-- GetCustomerAccounts
```

The AI reasoner evaluates risks involving ETL compatibility, application behavior, stored procedures, and schema transformations.

The Guardian checks whether the recommended disposition follows the permitted review policy.

A migration engineer then reviews the evidence, confirms the transformation strategy, and determines the required testing and approval process.

No database modification occurs automatically.

## 12. Known Limitations

This is a synthetic learning POV, not a production migration platform.

Current limitations include:

- Simplified SQL parsing instead of a full SQL Server parser.
- Mapping existence checks do not fully validate target-table compatibility.
- NetworkX graph data is loaded locally.
- Graph relationships depend on the supplied dependency metadata.
- The cross-tenant ID finding lacks verified target namespace policy.
- The Guardian does not independently validate all LLM-generated statements.
- LLM outputs may vary between executions.
- API availability and quotas may affect reasoning.
- No automated migration deployment or rollback is implemented.
- No production-grade authentication, monitoring, or audit infrastructure is implemented.

Do not submit proprietary source code, customer records, or regulated information to an external LLM API without organizational authorization.

## 13. Future Enhancements

### Phase 1 — Detection Quality

- Validate mapped target tables and columns.
- Improve SQL parsing.
- Add stored procedure and view scanning.
- Add schema compatibility tests.
- Introduce finding severity and confidence levels.

### Phase 2 — Enterprise GraphRAG

- Migrate graph storage from NetworkX to Amazon Neptune.
- Model repositories, applications, tables, stored procedures, and ETL pipelines.
- Add multi-hop dependency traversal.
- Retrieve source-code and metadata evidence.
- Track graph provenance and source references.

### Phase 3 — AI and Guardian Improvements

- Add evidence-grounded LLM evaluation.
- Validate recommendation claims against retrieved evidence.
- Implement model fallback and rate-limit handling.
- Add structured audit records.
- Support human-in-the-loop approvals.
- Track reasoning quality and hallucination rates.

### Phase 4 — Production Engineering

- Containerize the services with Docker.
- Add REST APIs using FastAPI.
- Add CI/CD using GitHub Actions.
- Add unit and integration test coverage.
- Introduce observability and dashboards.
- Add versioned migration plans and rollback procedures.

## 14. Key Takeaway

This project demonstrates how a legacy modernization workflow can combine:

**Code and schema scanning → Dependency graph → GraphRAG evidence retrieval → LLM reasoning → Guardian validation → Human review → Modernization assessment**

The core principle is that AI recommendations must be grounded in verifiable evidence and reviewed before any migration action is authorized.

---

**Project type:** Local Proof of Value  
**Domain:** Legacy application and database modernization  
**Current state:** Working synthetic end-to-end assessment pipeline  
**Execution mode:** Analysis and recommendations only
