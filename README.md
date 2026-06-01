# Eval Harness

Structured evaluation loop for LLM pipelines. Runs test cases through a RAG pipeline, scores each output across four named dimensions, and enforces a configurable pass/fail gate.

**Stack:** OpenAI `text-embedding-3-small` · Chroma · `gpt-4.1-nano` · Python

Companion to [rag-pipeline](https://github.com/tinkerthinkerbytes/rag-pipeline) and [langgraph-soc-pipeline](https://github.com/tinkerthinkerbytes/langgraph-soc-pipeline).

## Architecture

```
test_cases.py (8 queries + expected criteria)
      │
      ▼
  [runner.py]
  • retrieve() → top-k chunks from Chroma
  • generate() → grounded response
      │
      ├─ [dimensions.py] — deterministic
      │   • completeness:        expected keywords in response
      │   • structural_validity: length, source citation, no refusal
      │
      └─ [judge.py] — LLM-as-judge
          • coherence:    rated 1–5, pass ≥ 3
          • faithfulness: unsupported claims extracted
      │
      ▼
  per-case pass/fail + eval_report.json
```

## Setup

```bash
pip install -r requirements.txt
```

Create `.env` — on Windows (PowerShell):
```powershell
'OPENAI_API_KEY=sk-your-key-here' | Out-File -FilePath .env -Encoding utf8
```
On Mac/Linux:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

## Usage

```bash
# Ingest corpus (once, or after changes to corpus/)
python main.py ingest

# Run all eval cases
python main.py run

# Run with pass/fail gate — exits code 1 if pass rate < threshold
python main.py run --gate
python main.py run --gate --threshold 0.8

# Adjust retrieval depth
python main.py run --top-k 5
```

## Dimensions

| Dimension | Method | Measures |
|---|---|---|
| `completeness` | Deterministic | Expected keywords present in response |
| `structural_validity` | Deterministic | Min length, source cited, no refusal phrase |
| `coherence` | LLM-as-judge (1–5, pass ≥ 3) | Response clearly answers the question |
| `faithfulness` | LLM-as-judge | No claims outside the retrieved context |

A test case passes only if all four dimensions pass. The `--gate` flag fails the process (exit code 1) if the overall pass rate falls below `--threshold` (default: `1.0`).

## Sample Output

```
Running 8 eval cases (top_k=3)...

[PASS] tc_001: What indicators of compromise were identified...
    ✓ completeness
    ✓ structural_validity
    ✓ coherence           (score: 4/5)
    ✓ faithfulness
      sources: incident_001.md, runbook_phishing.md

============================================================
EVAL SUMMARY
============================================================
  completeness               8/8  [########]
  structural_validity        8/8  [########]
  coherence                  7/8  [#######-]
  faithfulness               8/8  [########]

  overall_pass               7/8  [#######-]

Gate (threshold=100%): FAIL  — 7/8 cases passed

Full report written to: eval_report.json
```

## Corpus

Six synthetic SOC documents — fabricated for demonstration, no real data.

| File | Type | Content |
|---|---|---|
| `incident_001.md` | Incident report | Phishing campaign, credential harvesting |
| `incident_002.md` | Incident report | Cobalt Strike beacon, Severity 1 |
| `policy_access_control.md` | Policy | MFA requirements, least privilege, access reviews |
| `policy_incident_response.md` | Policy | Severity tiers, SLAs, escalation paths |
| `runbook_phishing.md` | Runbook | Phishing triage, containment, evidence collection |
| `runbook_malware.md` | Runbook | Malware containment, forensics, remediation |
