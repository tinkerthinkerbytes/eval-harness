# Runbook — Phishing Investigation and Response
**ID:** RB-SOC-011
**Applies to:** Severity 2 and 3 phishing alerts
**Owner:** SOC Tier 2

## Detection Signals
- Email gateway alert: external sender with SSO or credential-harvesting template detected
- User report via phishing button or helpdesk ticket
- SIEM correlation: multiple users receiving identical subject line within short time window
- Proxy log: user navigation to known phishing domain or newly registered lookalike domain

## Step 1 — Triage
1. Retrieve the reported email from quarantine or user mailbox.
2. Extract header fields: sender address, reply-to, originating IP, received chain.
3. Extract all URLs from the email body — defang before logging (replace `http` with `hxxp`).
4. Check originating IP and sender domain against threat intel feeds (VirusTotal, AlienVault OTX).
5. Classify: credential harvesting, malware delivery, or BEC. Assign severity.

## Step 2 — Scope
1. Query email gateway for all recipients of the same sender domain or subject pattern (last 7 days).
2. Query proxy logs for any user navigation to the identified phishing URLs.
3. Query SIEM for any authentication events from users who clicked, within 30 minutes post-click.
4. Identify users who may have submitted credentials (look for POST requests to phishing domain).

## Step 3 — Containment
1. Block sender domain at email gateway — global rule, all mailboxes.
2. Block phishing URLs at web proxy.
3. Recall or quarantine the email from all recipient mailboxes if the platform supports it.
4. For users who submitted credentials: force password reset and MFA re-enrolment immediately.
5. For users who only clicked: monitor authentication logs for 72 hours.

## Step 4 — Evidence Collection
- Export email headers and raw message source.
- Screenshot the phishing page (use isolated VM or sandboxed browser).
- Preserve proxy and authentication logs for affected users.
- Submit phishing URL and sender domain to threat intel sharing platform.

## Step 5 — Notification
- Notify all affected users with instructions (do not reply to the email, change password if credentials entered).
- Notify line managers of users who submitted credentials.
- Update incident log with scope, containment actions, and evidence collected.
