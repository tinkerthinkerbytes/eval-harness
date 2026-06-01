# Incident Response Policy — POL-SEC-007
**Version:** 3.1
**Owner:** SOC Manager
**Last Reviewed:** 2024-02-01
**Next Review:** 2025-02-01

## Purpose
Define the response framework, severity classifications, escalation paths, and SLA commitments for security incidents.

## Severity Classification

### Severity 1 — Critical
Definition: Active threat with confirmed or imminent impact to business-critical systems, data exfiltration in progress, or ransomware execution detected.
SLA: Initial response within 15 minutes. Incident commander assigned within 30 minutes. Executive notification within 1 hour. Full containment target: 4 hours.

### Severity 2 — High
Definition: Confirmed malicious activity without confirmed data loss. Active phishing campaign, compromised credential with no evidence of lateral movement, or malware on a single non-critical endpoint.
SLA: Initial response within 1 hour. Analyst assigned within 2 hours. Management notification within 4 hours. Full containment target: 24 hours.

### Severity 3 — Medium
Definition: Suspicious activity requiring investigation. Anomalous login patterns, failed brute-force attempts, or policy violation without confirmed malicious intent.
SLA: Initial response within 4 hours. Investigation completed within 48 hours.

### Severity 4 — Low
Definition: Informational alerts, minor policy violations, or false positive review items.
SLA: Review and close within 5 business days.

## Escalation Path
Tier 1 analyst → Tier 2 analyst (if unresolved in SLA window) → SOC lead → CISO (Severity 1 and 2 only) → Executive team (Severity 1 only, data breach suspected).

## Communication Requirements
All Severity 1 and 2 incidents must have a running incident log updated at minimum every 30 minutes during active response. Post-incident reports are required for all Severity 1 and 2 incidents within 5 business days of closure.

## Legal and Regulatory
Any incident involving potential personal data breach must be escalated to the Data Protection Officer within 24 hours of confirmation. Regulatory notification (ICO) must be completed within 72 hours of a confirmed personal data breach.
