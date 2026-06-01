"""
Eval test cases — query + expected quality criteria.

Each test case defines:
  id                  Unique identifier for report tracing.
  description         Human-readable label — what scenario this tests.
  query               The question to run through the RAG pipeline.
  expected_keywords   Terms that must appear in the response (completeness check).
                      Case-insensitive, substring match. Use stemmed forms where
                      helpful — e.g. "isolat" matches isolate/isolated/isolation.

All queries are drawn from content present in the corpus, so a completeness
failure cannot be blamed on retrieval — the right content exists and should be
surfaced. A completeness miss therefore points to a generation problem.
"""

TEST_CASES = [
    {
        "id": "tc_001",
        "description": "Phishing IOC identification from incident report",
        "query": "What indicators of compromise were identified in the phishing campaign?",
        "expected_keywords": ["domain", "sender", "ip"],
    },
    {
        "id": "tc_002",
        "description": "Malware endpoint containment procedure",
        "query": "What are the containment steps for a malware-infected endpoint?",
        "expected_keywords": ["isolat", "network", "firewall"],
    },
    {
        "id": "tc_003",
        "description": "Severity 1 incident SLA requirements",
        "query": "What is the SLA for a Severity 1 incident?",
        "expected_keywords": ["15 minute", "1 hour", "4 hour"],
    },
    {
        "id": "tc_004",
        "description": "Permitted MFA methods under access control policy",
        "query": "What MFA methods are permitted under the access control policy?",
        "expected_keywords": ["fido2", "totp", "authenticator"],
    },
    {
        "id": "tc_005",
        "description": "Forensic evidence collection for malware response",
        "query": "What forensic evidence should be collected during a malware response?",
        "expected_keywords": ["memory", "log", "prefetch"],
    },
    {
        "id": "tc_006",
        "description": "Escalation path for a Severity 1 incident",
        "query": "What is the escalation path for a Severity 1 incident?",
        "expected_keywords": ["tier", "escalat", "ciso"],
    },
    {
        "id": "tc_007",
        "description": "Stale account handling under access control policy",
        "query": "How should stale accounts be handled under the access control policy?",
        "expected_keywords": ["90 day", "disabl", "stale"],
    },
    {
        "id": "tc_008",
        "description": "Response for users who submitted credentials in a phishing attack",
        "query": "What should be done for users who submitted credentials in a phishing attack?",
        "expected_keywords": ["password", "reset", "mfa"],
    },
]
