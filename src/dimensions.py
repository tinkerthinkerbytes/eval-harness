"""
Completeness and Structural Validity — deterministic dimension checks.

These require no LLM call: cheap, fast, and fully reproducible across runs.
They are the first line of evaluation — if these fail, there is no point
running the more expensive LLM-judge dimensions.

Completeness
    All expected keywords appear in the generated response (case-insensitive substring).
    A retrieval hit with a completeness miss isolates the failure to generation:
    the right content was retrieved but the generator dropped it.

Structural Validity
    Response meets three schema requirements:
      (1) Minimum substantive length — filters empty or near-empty outputs.
      (2) Source document cited — the response names at least one .md source file,
          confirming the model followed the citation instruction.
      (3) No refusal phrase — the response attempts to answer rather than deflect.
    In production, (2) would be replaced by a typed output parser enforcing a
    structured citation schema. Here it is a filename-in-text check.
"""

MIN_RESPONSE_CHARS = 40

REFUSAL_PHRASES = [
    "i don't know",
    "i cannot",
    "no information",
    "not provided",
    "context does not",
    "not mentioned",
    "i'm unable",
    "cannot find",
    "does not contain",
    "not available in",
]


def check_completeness(response: str, expected_keywords: list[str]) -> dict:
    """
    Case-insensitive substring match.
    Supports stemmed keywords — e.g. 'isolat' matches 'isolate', 'isolated', 'isolation'.
    """
    response_lower = response.lower()
    missing = [kw for kw in expected_keywords if kw.lower() not in response_lower]
    passed = len(missing) == 0
    return {
        "dimension": "completeness",
        "passed": passed,
        "missing_keywords": missing,
        "reason": f"Missing keywords: {missing}" if not passed else None,
    }


def check_structural_validity(response: str, retrieved_chunks: list[dict]) -> dict:
    """
    Three-part schema check: length, source citation, no refusal.
    All violations are collected before returning — not short-circuited.
    """
    violations = []

    # (1) Minimum length
    if len(response.strip()) < MIN_RESPONSE_CHARS:
        violations.append(
            f"Response too short ({len(response.strip())} chars, minimum {MIN_RESPONSE_CHARS})"
        )

    # (2) Source citation — at least one retrieved .md filename appears in the response
    sources = {c["source"] for c in retrieved_chunks}
    if not any(src in response for src in sources):
        violations.append(
            "No source document filename found in response (citation required)"
        )

    # (3) Refusal check
    response_lower = response.lower()
    detected = next(
        (phrase for phrase in REFUSAL_PHRASES if phrase in response_lower), None
    )
    if detected:
        violations.append(f"Refusal phrase detected: '{detected}'")

    passed = len(violations) == 0
    return {
        "dimension": "structural_validity",
        "passed": passed,
        "violations": violations,
        "reason": "; ".join(violations) if not passed else None,
    }
