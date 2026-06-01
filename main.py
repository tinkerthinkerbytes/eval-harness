"""
Evaluation Harness CLI

Commands:
    ingest                       Embed corpus and build the Chroma vector store
    run                          Run all eval cases; write eval_report.json
    run --gate                   Exit with code 1 if pass rate is below threshold
    run --threshold FLOAT        Gate threshold 0.0–1.0 (default: 1.0)
    run --top-k INT              Chunks retrieved per query (default: 3)
    run --report PATH            Output path for JSON report (default: eval_report.json)
"""
import argparse
import sys

from dotenv import load_dotenv

load_dotenv()


def cmd_ingest(args):
    from src.ingest import ingest
    ingest(corpus_dir=args.corpus)


def cmd_run(args):
    from src.runner import run_eval
    from test_cases import TEST_CASES

    report = run_eval(
        test_cases=TEST_CASES,
        top_k=args.top_k,
        gate_threshold=args.threshold,
        report_path=args.report,
    )

    if args.gate and not report["summary"]["gate_passed"]:
        print(
            f"\nGate FAILED — pass rate "
            f"{report['summary']['pass_rate']:.0%} < threshold {args.threshold:.0%}"
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Evaluation Harness — SOC RAG pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest
    p_ingest = sub.add_parser("ingest", help="Embed corpus into Chroma")
    p_ingest.add_argument(
        "--corpus", default="corpus", help="Path to corpus directory (default: corpus)"
    )
    p_ingest.set_defaults(func=cmd_ingest)

    # run
    p_run = sub.add_parser("run", help="Run evaluation harness")
    p_run.add_argument(
        "--gate", action="store_true",
        help="Exit with code 1 if overall pass rate is below --threshold",
    )
    p_run.add_argument(
        "--threshold", type=float, default=1.0, metavar="FLOAT",
        help="Gate pass rate threshold 0.0–1.0 (default: 1.0 — all cases must pass)",
    )
    p_run.add_argument(
        "--top-k", type=int, default=3, dest="top_k",
        help="Chunks to retrieve per query (default: 3)",
    )
    p_run.add_argument(
        "--report", default="eval_report.json", metavar="PATH",
        help="Output path for the JSON report (default: eval_report.json)",
    )
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
