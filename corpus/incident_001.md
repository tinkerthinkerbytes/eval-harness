# Incident Report — INC-2024-0147
**Date:** 2024-03-12
**Severity:** 2
**Status:** Resolved
**Analyst:** J. Reeves

## Summary
A targeted phishing campaign was detected targeting 14 users in the Finance and HR departments. The campaign used a spoofed sender domain (finance-portal-secure[.]net) to distribute credential harvesting links mimicking the internal SSO portal.

## Indicators of Compromise
- Sender domain: finance-portal-secure[.]net
- Phishing URL: https://finance-portal-secure[.]net/auth/login
- Subject line pattern: "Action Required: Verify Your Account Access"
- Originating IP: 185.220.101.47 (Tor exit node)

## Affected Users
14 users received the email. 3 users clicked the link. 1 user submitted credentials before the page was taken down.

## Response Actions
1. Blocked sender domain at email gateway within 22 minutes of detection.
2. Reset credentials for all users who clicked the link.
3. Forced MFA re-enrolment for affected accounts.
4. Submitted phishing URL to threat intel feed.
5. Notified affected users and their line managers.

## Root Cause
Domain allow-listing rules in the email gateway were not enforced for externally-hosted SSO-themed templates.

## Lessons Learned
Email gateway rules should flag any external sender using "SSO", "verify", or "login" in subject lines for quarantine review. Updated rule set deployed 2024-03-14.
