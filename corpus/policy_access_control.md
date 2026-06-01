# Access Control Policy — POL-SEC-003
**Version:** 2.4
**Owner:** Information Security
**Last Reviewed:** 2024-01-15
**Next Review:** 2025-01-15

## Purpose
This policy defines the minimum requirements for controlling access to systems, data, and infrastructure across the organisation.

## Scope
Applies to all employees, contractors, and third-party vendors with access to any company-owned or company-managed system.

## Principles

### Least Privilege
All accounts must be provisioned with the minimum permissions required to perform the assigned role. Elevated permissions must be time-bound and approved by the system owner and the requesting user's line manager.

### Multi-Factor Authentication (MFA)
MFA is mandatory for all accounts. Acceptable MFA methods are hardware security keys (FIDO2), authenticator app (TOTP), and push notification via approved MDM-enrolled device. SMS-based authentication is not permitted for privileged accounts. All remote access sessions must authenticate with MFA regardless of network location.

### Privileged Access
Privileged accounts (domain admin, server admin, database admin) must not be used for day-to-day tasks. Privileged access must be obtained via a PAM solution with session recording enabled. Shared privileged accounts are prohibited.

### Access Reviews
Access rights must be reviewed quarterly for privileged accounts and annually for standard accounts. Line managers are responsible for certifying that reported access rights are correct. Stale accounts (no login in 90 days) must be disabled automatically.

## Joiner/Mover/Leaver
Access provisioning must be completed within 1 business day of an approved onboarding request. Access must be fully revoked within 4 hours of a leaver notification, regardless of notice period. Role changes must trigger an access re-certification within 5 business days.
