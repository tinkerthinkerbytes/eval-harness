# Incident Report — INC-2024-0203
**Date:** 2024-04-28
**Severity:** 1
**Status:** Resolved
**Analyst:** M. Okonkwo

## Summary
An endpoint (hostname: WS-FIN-044, user: t.nguyen) was found running a Cobalt Strike beacon after EDR telemetry flagged unusual outbound C2 traffic to 91.108.4.200 on port 443.

## Indicators of Compromise
- C2 IP: 91.108.4.200 (port 443)
- Malware family: Cobalt Strike (beacon variant CS-4.7)
- Process: svchost.exe (spoofed, running from %APPDATA%)
- Persistence: scheduled task named "WindowsDefenderSync"
- File hash (beacon DLL): a3f2e1d9c8b7a6e5f4d3c2b1a0e9f8d7

## Containment Actions
1. Endpoint isolated from network within 8 minutes of alert triage.
2. Network block applied to C2 IP across all perimeter firewalls.
3. Scheduled task and beacon DLL removed.
4. Endpoint reimaged after forensic image captured.

## Forensic Evidence Collected
- Full memory dump captured prior to isolation.
- EDR telemetry logs exported (72-hour window).
- Prefetch files and Windows event logs preserved.
- Network flow logs from SIEM for the affected endpoint (48-hour window).

## Root Cause
Initial access via a malicious macro-enabled document received by email 6 days prior. The document bypassed attachment scanning because it was delivered inside a password-protected ZIP container.

## Lessons Learned
Password-protected archives should be quarantined for manual review regardless of content scan result. Policy updated and gateway rule deployed 2024-05-02.
