import json
import os
import time
import random
from pathlib import Path

from google import genai
from google.genai import errors
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs" / "enriched_findings.json"
OUTPUT = ROOT / "outputs" / "llm_recommendations.json"

MODEL = "gemini-3.8-flash"


class Recommendation(BaseModel):
    disposition: str
    reason: str
    risks: list[str]
    next_steps: list[str]
    human_approval_required: bool


def analyze_finding(client, finding):
    prompt = f"""
You are a senior legacy modernization engineer.

Analyze this synthetic migration finding and its
dependency graph evidence.

FINDING:
{json.dumps(finding, indent=2)}

Rules:
1. Use only the supplied evidence.
2. Do not invent dependencies, policies, or mappings.
3. Never recommend automatic deletion.
4. If evidence is incomplete, request human review.
5. Set human_approval_required to true.
6. Return a clear disposition, risks, and next steps.

For SOURCE_ONLY_TABLE, recommend REVIEW_MIGRATION_MAPPING.
For COLUMN_TYPE_DRIFT, recommend REVIEW_SCHEMA_TRANSFORMATION.
For SOURCE_COLUMN_UNMAPPED, recommend REVIEW_COLUMN_MAPPING.
For CROSS_TENANT_ID_OVERLAP, recommend REVIEW_ID_NAMESPACE_POLICY.

The disposition must be one of the above review actions.
"""

    response = None

    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Recommendation
                }
            )
            break

        except (errors.ServerError, errors.ClientError) as exc:
            status = getattr(exc, "code", None)

            if status not in (429, 503) or attempt == 3:
                raise

            delay = min(30, 2 ** (attempt + 1))
            delay += random.uniform(0, 1)

            print(
                f"Gemini temporarily unavailable ({status}). "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return Recommendation.model_validate_json(
        response.text
    ).model_dump()


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    if not INPUT.exists():
        raise FileNotFoundError(
            "Run 'python -m rag.retriever' first"
        )

    findings = json.loads(INPUT.read_text())

    client = genai.Client(api_key=api_key)

    results = []

    for index, finding in enumerate(findings, start=1):
        print(
            f"\\nAnalyzing {index}/{len(findings)}: "
            f"{finding['type']}",
            flush=True
        )

        try:
            recommendation = analyze_finding(client, finding)

            result = {
                "source_finding": finding,
                "llm_model": MODEL,
                "llm_recommendation": recommendation,
                "guardian_status": "NOT_VALIDATED"
            }

        except Exception as exc:
            print(f"Analysis failed: {exc}")
            result = {
                "source_finding": finding,
                "llm_model": MODEL,
                "llm_recommendation": None,
                "guardian_status": "LLM_ERROR",
                "error": str(exc)
            }

        results.append(result)
        OUTPUT.write_text(json.dumps(results, indent=2))

        print(f"Saved progress: {index}/{len(findings)}")

        if index < len(findings):
            time.sleep(5)

    print(f"\\nFinished. Results saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
