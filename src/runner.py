"""
Evaluation runner — orchestrates the full eval loop.

For each test case:
  1. Run the RAG pipeline  →  response + retrieved chunks
  2. Score all four dimensions
  3. Record pass/fail + failure reason per dimension

After all cases:
  - Print a per-case console summary with dimension results
  - Print an aggregate summary with per-dimension pass rates
  - Write a full machine-readable JSON report
  - Return the report dict so callers can inspect results or enforce a gate

The gate (--gate flag in main.py) causes the process to exit non-zero if the
overall pass rate falls below gate_threshold. This lets the harness act as a
quality checkpoint in CI — a model swap or retrieval config change that drops
quality below the threshold fails the build before it reaches production.
"""
import json

from .dimensions import check_completeness, check_structural_validity
from .judge import judge_coherence, judge_faithfulness
from .pipeline import generate, retrieve

DIMENSIONS = ["completeness", "structural_validity", "coherence", "faithfulness"]


def run_eval(
    test_cases: list[dict],
    top_k: int = 3,
    gate_threshold: float = 1.0,
    report_path: str = "eval_report.json",
) -> dict:
    """
    Run all test cases and return the full report dict.

    gate_threshold: fraction of test cases that must pass all four dimensions.
      1.0 = every case must pass (strictest).
      0.0 = gate always passes.
    """
    results = []
    print(f"Running {len(test_cases)} eval cases (top_k={top_k})...\n")

    for tc in test_cases:
        chunks = retrieve(tc["query"], top_k=top_k)
        gen = generate(tc["query"], chunks)
        response = gen["response"]

        dims = {
            "completeness":        check_completeness(response, tc["expected_keywords"]),
            "structural_validity": check_structural_validity(response, chunks),
            "coherence":           judge_coherence(tc["query"], response),
            "faithfulness":        judge_faithfulness(response, chunks),
        }
        all_passed = all(d["passed"] for d in dims.values())

        record = {
            "id":               tc["id"],
            "description":      tc.get("description", ""),
            "query":            tc["query"],
            "dimensions":       dims,
            "passed":           all_passed,
            "sources_used":     gen["sources_used"],
            "response_preview": response[:300],
        }
        results.append(record)

        # Per-case console output
        status = "PASS" if all_passed else "FAIL"
        print(f"[{status}] {tc['id']}: {tc['query'][:65]}...")
        for dim_name, dim in dims.items():
            mark = "✓" if dim["passed"] else "✗"
            extra = ""
            if dim_name == "coherence":
                extra = f"  (score: {dim['score']}/5)"
            elif not dim["passed"] and dim.get("reason"):
                extra = f"  ← {dim['reason'][:80]}"
            print(f"    {mark} {dim_name:<24}{extra}")
        print(f"      sources: {', '.join(gen['sources_used'])}")
        print()

    # Aggregate stats
    total = len(results)
    overall_passed = sum(1 for r in results if r["passed"])
    pass_rate = overall_passed / total if total else 0.0

    dim_stats: dict[str, dict] = {}
    for dim in DIMENSIONS:
        n = sum(1 for r in results if r["dimensions"][dim]["passed"])
        dim_stats[dim] = {"passed": n, "total": total, "rate": round(n / total, 2)}

    gate_passed = pass_rate >= gate_threshold

    report = {
        "summary": {
            "total_cases":    total,
            "overall_passed": overall_passed,
            "pass_rate":      round(pass_rate, 2),
            "gate_threshold": gate_threshold,
            "gate_passed":    gate_passed,
            "dimensions":     dim_stats,
        },
        "results": results,
    }

    # Summary console block
    print("=" * 60)
    print("EVAL SUMMARY")
    print("=" * 60)
    for dim in DIMENSIONS:
        n = dim_stats[dim]["passed"]
        bar = "#" * n + "-" * (total - n)
        print(f"  {dim:<26} {n}/{total}  [{bar}]")
    print()
    bar = "#" * overall_passed + "-" * (total - overall_passed)
    print(f"  {'overall_pass':<26} {overall_passed}/{total}  [{bar}]")
    print()
    gate_label = "PASS" if gate_passed else "FAIL"
    gate_suffix = f"  — {overall_passed}/{total} cases passed" if not gate_passed else ""
    print(f"Gate (threshold={gate_threshold:.0%}): {gate_label}{gate_suffix}")
    print()

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Full report written to: {report_path}")

    return report
