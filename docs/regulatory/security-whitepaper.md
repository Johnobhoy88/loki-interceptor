# LOKI Security Whitepaper

**Highland AI Ltd Security Architecture**
**Version:** 1.0
**Published:** November 2025
**Classification:** Public

---

## Executive Summary

LOKI Interceptor employs defense-in-depth security architecture protecting customer data through encryption, access controls, network segmentation, and continuous monitoring. This whitepaper details our security measures for technical evaluation and regulatory due diligence.

**Key Security Highlights:**
- AES-256 encryption at rest, TLS 1.3 in transit
- Zero-trust architecture with MFA and RBAC
- SOC 2 Type II compliant (target Q2 2026)
- UK GDPR compliant data processing
- 24/7 security monitoring and incident response
- Annual penetration testing

---

## 1. Security Architecture Overview

### 1.1 Defense-in-Depth Model

```
┌─────────────────────────────────────────────┐
│  Layer 7: Application Security             │
│  - Input validation, CSRF protection       │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 6: Data Security                     │
│  - Encryption at rest/transit              │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 5: Identity & Access Management      │
│  - MFA, RBAC, SSO                          │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 4: Network Security                  │
│  - Firewalls, IDS, VPN                     │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 3: Host Security                     │
│  - OS hardening, endpoint protection       │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 2: Physical Security                 │
│  - AWS data center controls                │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│  Layer 1: Monitoring & Response             │
│  - 24/7 SIEM, incident response            │
└─────────────────────────────────────────────┘
```

### 1.2 Zero-Trust Principles

- **Never Trust, Always Verify:** Every request authenticated and authorized
- **Least Privilege Access:** Users granted minimum necessary permissions
- **Assume Breach:** Defense measures assume perimeter may be compromised
- **Explicit Verification:** Every transaction validated (no implicit trust)

---

## 2. Data Security

### 2.1 Encryption

**At Rest (AES-256):**
- Database encryption: AWS RDS encryption (AES-256)
- File storage: AWS S3 server-side encryption (SSE-S3)
- Backups: Encrypted with AWS KMS customer-managed keys
- Audit logs: Encrypted in SQLite database (AES-256)

**In Transit (TLS 1.3):**
- All API traffic: HTTPS only (HTTP → HTTPS redirect)
- Database connections: TLS 1.3 enforced
- Internal services: mTLS (mutual TLS authentication)
- Minimum TLS version: 1.2 (deprecated, upgrade to 1.3 mandatory)

**Key Management:**
- AWS Key Management Service (KMS)
- Customer-managed keys (CMK) for Enterprise
- Automatic key rotation every 90 days
- No hardcoded keys (secrets in AWS Secrets Manager)

### 2.2 Data Classification

| Classification | Description | Examples | Security Controls |
|----------------|-------------|----------|-------------------|
| **Public** | Publicly available | Marketing materials | No special controls |
| **Internal** | Internal use only | Employee emails | Access controls, encryption |
| **Confidential** | Sensitive business data | Customer data, API keys | Encryption, MFA, audit logging |
| **Restricted** | Highly sensitive | PII, payment data | Encryption, DLP, strict access control |

**Data Handling Requirements:**
- Confidential: Encrypted at rest and in transit, MFA required
- Restricted: Encrypted, MFA, access logged, DLP monitoring

### 2.3 Data Minimization

**LOKI Privacy-by-Design:**
- Document content processed in-memory (not stored)
- Only validation results stored (not full document text)
- Audit logs configurable (30-365 days retention, default 90)
- No sensitive data in logs (API keys, passwords redacted)

**Personal Data Processing:**
- Only collect data necessary for Service provision
- Data anonymized where possible (IP addresses hashed)
- Data deletion on request (GDPR Right to Erasure)

### 2.4 Data Residency

**Primary Storage:** AWS London (eu-west-2) region
- All production data stored in UK
- Backups stored in UK (same region)
- No cross-border data transfers within UK/EU

**Third-Party Processing:**
- Anthropic (US): Document text for AI analysis (Standard Contractual Clauses)
- Stripe (EU): Payment processing (GDPR-compliant)

---

## 3. Application Security

### 3.1 Secure Development Lifecycle (SDLC)

**Phase 1: Requirements**
- Security requirements defined (threat modeling)
- Data flow diagrams created
- Risk assessment conducted

**Phase 2: Design**
- Security architecture review
- Principle of least privilege enforced
- Defense-in-depth design

**Phase 3: Development**
- Secure coding standards (OWASP Top 10)
- Code reviews for security issues
- Static analysis (SAST) in CI/CD pipeline

**Phase 4: Testing**
- Dynamic analysis (DAST) on staging
- Penetration testing (annually)
- Vulnerability scanning (weekly)

**Phase 5: Deployment**
- Immutable infrastructure (no manual changes)
- Secrets management (AWS Secrets Manager)
- Rollback procedures tested

**Phase 6: Operations**
- 24/7 monitoring and alerting
- Incident response procedures
- Security patch management

### 3.2 OWASP Top 10 Mitigation

| Vulnerability | Mitigation |
|---------------|------------|
| **A01: Broken Access Control** | RBAC, authorization checks on every request, session management |
| **A02: Cryptographic Failures** | TLS 1.3, AES-256, no weak ciphers, secure key storage |
| **A03: Injection** | Parameterized queries, input validation, ORM usage |
| **A04: Insecure Design** | Threat modeling, security architecture review |
| **A05: Security Misconfiguration** | Infrastructure as Code (Terraform), configuration management |
| **A06: Vulnerable Components** | Dependency scanning (Snyk), automatic updates |
| **A07: Authentication Failures** | MFA, strong password policy, session timeout |
| **A08: Data Integrity Failures** | Digital signatures, integrity checks, audit logging |
| **A09: Logging Failures** | Centralized logging, SIEM monitoring, log retention |
| **A10: SSRF** | Input validation, whitelist approach, network segmentation |

### 3.3 API Security

**Authentication:**
- API key-based (Bearer token)
- API keys hashed in database (bcrypt)
- Keys rotated every 90 days (automatic notification)

**Authorization:**
- Role-based access control (RBAC)
- Scoped API keys (read-only, write, admin)
- Rate limiting per API key (30-300 req/min based on plan)

**Input Validation:**
- JSON schema validation (rejects malformed requests)
- Max payload size: 10MB (prevents DoS)
- Character encoding validation (UTF-8 only)

**Rate Limiting:**
```
Starter: 10 requests/minute
Professional: 30 requests/minute
Enterprise: 300 requests/minute (custom limits available)
```

**Error Handling:**
- Generic error messages (no sensitive details leaked)
- Stack traces disabled in production
- Errors logged securely (not sent to client)

---

## 4. Infrastructure Security

### 4.1 Cloud Provider (AWS)

**Why AWS:**
- ISO 27001, SOC 2 Type II certified
- UK data residency (London region)
- 99.99% SLA for compute and storage
- Shared responsibility model clearly defined

**AWS Services Used:**

| Service | Purpose | Security Features |
|---------|---------|-------------------|
| **EC2** | Application servers | Security groups, encrypted EBS volumes |
| **RDS** | PostgreSQL database | Encryption at rest, automated backups, multi-AZ |
| **S3** | File storage | Encryption, versioning, lifecycle policies |
| **KMS** | Key management | HSM-backed, automatic rotation |
| **CloudWatch** | Monitoring | Centralized logging, alerting |
| **IAM** | Access management | Least privilege, MFA enforcement |

### 4.2 Network Security

**Network Segmentation:**
```
┌──────────────────────────────────────────┐
│  Public Subnet                           │
│  - Load Balancer                         │
│  - Bastion Host (emergency access)       │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Private Subnet                          │
│  - Application Servers (EC2)             │
│  - No direct internet access             │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Database Subnet                         │
│  - RDS PostgreSQL                        │
│  - No internet access                    │
└──────────────────────────────────────────┘
```

**Firewall Rules (Security Groups):**
- **Load Balancer:** Allow 443 (HTTPS) from internet
- **App Servers:** Allow 443 from load balancer only
- **Database:** Allow 5432 from app servers only
- **Bastion:** Allow 22 (SSH) from office IP only (MFA required)

**Intrusion Detection:**
- AWS GuardDuty (threat detection)
- VPC Flow Logs (network traffic analysis)
- AWS WAF (web application firewall)

**DDoS Protection:**
- AWS Shield Standard (automatic)
- Cloudflare (rate limiting, bot protection)
- Auto-scaling to absorb traffic spikes

### 4.3 Endpoint Security (Employee Devices)

**Managed Endpoints:**
- All employee laptops enrolled in MDM (Mobile Device Management)
- Full-disk encryption required (BitLocker/FileVault)
- Endpoint protection (CrowdStrike EDR)
- Automatic OS updates enforced

**BYOD Policy:**
- Not permitted for accessing production systems
- Personal devices can access office Wi-Fi (guest network only)
- No sensitive data on personal devices

**Remote Access:**
- VPN required for accessing internal systems (OpenVPN)
- MFA required for VPN authentication
- Split-tunnel (only internal traffic via VPN)

---

## 5. Identity and Access Management

### 5.1 Authentication

**Multi-Factor Authentication (MFA):**
- Required for all employee accounts
- Required for Enterprise customer admin accounts
- TOTP-based (Google Authenticator, Authy)
- SMS fallback available (not recommended)

**Password Policy:**
- Minimum 12 characters
- Must include uppercase, lowercase, number, symbol
- No common passwords (10M password blacklist)
- Password expiration: 90 days (employees), no expiration (customers)
- Hashed with bcrypt (cost factor: 12)

**Single Sign-On (SSO):**
- Available for Enterprise customers
- SAML 2.0 support (Okta, Azure AD, Google Workspace)
- Just-in-Time (JIT) provisioning

### 5.2 Authorization (RBAC)

**User Roles:**

| Role | Permissions | Target Users |
|------|-------------|--------------|
| **Viewer** | Read documents, view reports | Auditors, managers |
| **Analyst** | Validate, correct, export documents | Compliance officers, analysts |
| **Admin** | Manage users, billing, settings | IT administrators |
| **API User** | API access only (programmatic) | Developers, automation |

**Principle of Least Privilege:**
- Users granted minimum permissions needed
- Temporary privilege escalation (time-limited)
- Access reviews quarterly

### 5.3 Session Management

**Session Security:**
- Session tokens: Cryptographically random (256-bit)
- Session timeout: 30 minutes inactivity (customizable)
- Concurrent session limit: 3 per user
- Session invalidation on password change/logout

**Cookie Security:**
- HttpOnly flag (prevents XSS access)
- Secure flag (HTTPS only)
- SameSite=Strict (prevents CSRF)

---

## 6. Monitoring and Incident Response

### 6.1 Security Monitoring

**24/7 SIEM (Security Information and Event Management):**
- Centralized log aggregation (AWS CloudWatch)
- Real-time alerting on suspicious activity
- Log retention: 90 days (compliance), 365 days (security events)

**Monitored Events:**
- Failed login attempts (>5 in 10 minutes → alert)
- API rate limit violations
- Privilege escalation
- Database access from unusual IPs
- Large data exports (>10GB → alert)
- Configuration changes

**Alerting Channels:**
- PagerDuty (24/7 on-call engineer)
- Email (security team)
- Slack (#security-alerts channel)

### 6.2 Incident Response Plan

**Phase 1: Detection (Minutes)**
- Automated alerts trigger
- On-call engineer notified (PagerDuty)
- Initial triage (severity assessment)

**Phase 2: Containment (Hours)**
- Isolate affected systems
- Disable compromised accounts
- Block malicious IPs
- Preserve evidence (logs, snapshots)

**Phase 3: Eradication (Hours-Days)**
- Identify root cause
- Remove malware/backdoors
- Patch vulnerabilities
- Reset credentials

**Phase 4: Recovery (Days)**
- Restore services from clean backups
- Verify system integrity
- Gradual rollout (canary deployment)

**Phase 5: Lessons Learned (Week)**
- Post-incident review
- Update runbooks
- Implement preventive measures
- Notify affected parties (if data breach)

### 6.3 Data Breach Response

**UK GDPR Compliance:**
- **Notification to ICO:** Within 72 hours of becoming aware
- **Notification to Data Subjects:** Without undue delay (if high risk)
- **Documentation:** Breach register maintained

**Notification Includes:**
- Nature of breach (what data affected)
- Likely consequences
- Measures taken to address breach
- Recommendations for data subjects

**Contact:** security@highlandai.com

---

## 7. Compliance and Auditing

### 7.1 Regulatory Compliance

**UK GDPR (Data Protection):**
- Data processing agreements with all customers
- Privacy by design and default
- Data subject rights supported (access, erasure, portability)
- Breach notification procedures

**PCI DSS (Payment Card Industry):**
- Payment processing via Stripe (PCI DSS Level 1 compliant)
- Highland AI does not store card data (Stripe tokenization)
- Quarterly vulnerability scans

**ISO 27001 (Information Security):**
- Target certification: Q2 2026
- 114 controls implemented (Annex A)
- Annual surveillance audits

**SOC 2 Type II (Service Organization Control):**
- Target certification: Q2 2026
- Security, Availability, Confidentiality criteria
- 6-month observation period

### 7.2 Auditing

**Internal Audits:**
- Quarterly security audits (self-assessment)
- Semi-annual compliance audits
- Findings tracked in Jira (remediation SLA: 30 days)

**External Audits:**
- Annual penetration testing (third-party firm)
- ISO 27001 surveillance audits (annual, post-certification)
- SOC 2 audit (annual, post-certification)

**Customer Audits:**
- Enterprise customers may request audit (reasonable notice: 30 days)
- Scope: Security controls, data processing activities
- Frequency: Once per year (or as required by customer's regulators)

### 7.3 Audit Logs

**What We Log:**
- User authentication (login, logout, failed attempts)
- API requests (endpoint, user, timestamp, response code)
- Data access (who accessed what, when)
- Configuration changes (who changed what settings)
- Security events (alerts, incidents)

**What We Don't Log:**
- Document content (privacy)
- Passwords (never logged, even hashed)
- API keys (only key ID logged, not full key)

**Log Protection:**
- Immutable (append-only, cannot be modified)
- Encrypted at rest (AES-256)
- Access restricted (security team only)
- Retained for 90 days (configurable for Enterprise: 30-365 days)

---

## 8. Third-Party Security

### 8.1 Vendor Risk Management

**Vendor Selection Criteria:**
- ISO 27001 or SOC 2 certified
- GDPR-compliant (for EU/UK vendors)
- Data processing agreement signed
- Regular security assessments

**Approved Vendors:**

| Vendor | Service | Certifications | DPA Signed |
|--------|---------|----------------|------------|
| **AWS** | Cloud infrastructure | ISO 27001, SOC 2, PCI DSS | ✓ |
| **Anthropic** | AI (Claude API) | SOC 2 Type II | ✓ |
| **Stripe** | Payment processing | PCI DSS Level 1, ISO 27001 | ✓ |
| **Intercom** | Customer support | ISO 27001, SOC 2 | ✓ |
| **Cloudflare** | CDN, DDoS protection | ISO 27001, SOC 2 | ✓ |

**Vendor Review:**
- Annual vendor risk assessment
- Quarterly compliance checks (certificate expiry)
- Incident notification requirements in contracts

### 8.2 Supply Chain Security

**Software Dependencies:**
- Automated dependency scanning (Snyk)
- Vulnerable dependency alerts
- Automatic patch PRs (Dependabot)
- SBOM (Software Bill of Materials) generated

**Third-Party Code:**
- Open-source libraries vetted (license, security)
- No unmaintained libraries (last commit <1 year)
- Private npm/pip repository (caching, malware scanning)

---

## 9. Business Continuity and Disaster Recovery

### 9.1 Backup Strategy

**3-2-1 Rule:**
- **3 copies** of data (production + 2 backups)
- **2 different media** (disk + snapshot)
- **1 offsite** copy (different AWS region for Enterprise)

**Backup Schedule:**
- Database: Every 6 hours (automated RDS snapshots)
- Files: Continuous (S3 versioning enabled)
- Configuration: Daily (Terraform state backups)

**Backup Retention:**
- Daily backups: 30 days
- Weekly backups: 90 days
- Monthly backups: 365 days

**Backup Testing:**
- Quarterly restore tests (verify backups work)
- Annual disaster recovery drill

### 9.2 Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 6 hours (data loss tolerance)

**DR Scenarios:**

**Scenario 1: Database Corruption**
- Restore from latest snapshot (6 hours old)
- Replay transaction logs (if available)
- Verify data integrity
- **Expected RTO:** 2 hours

**Scenario 2: AWS Region Failure**
- Failover to backup region (eu-west-1 for Enterprise)
- DNS update to new region (Route 53)
- Customer notification
- **Expected RTO:** 4 hours

**Scenario 3: Ransomware Attack**
- Isolate infected systems
- Restore from clean backups (30 days retention)
- Forensic investigation
- **Expected RTO:** 8 hours

### 9.3 Business Continuity

**Key Personnel:**
- On-call rotation (24/7 coverage)
- Cross-training (no single points of failure)
- Contact list maintained (phone, email, Slack)

**Communication Plan:**
- Status page updates (status.loki-compliance.com)
- Customer email notifications (if >1 hour downtime)
- Social media updates (Twitter @lokicompliance)

---

## 10. Employee Security

### 10.1 Background Checks

**Pre-Employment:**
- Criminal record check (DBS Basic Disclosure for UK)
- Employment verification (past 5 years)
- Reference checks (2 professional references)

**Ongoing:**
- Security clearance renewal every 3 years (for employees with production access)

### 10.2 Security Training

**Onboarding (Week 1):**
- Information security policies
- GDPR training
- Phishing awareness
- Password management (LastPass)

**Ongoing:**
- Annual security refresher training
- Quarterly phishing simulations
- Incident response drills (semi-annually)

**Specialized Training:**
- Secure coding (for engineers)
- Social engineering awareness (for support team)
- GDPR deep-dive (for customer success)

### 10.3 Acceptable Use Policy

**Employees Must:**
- Use company-issued devices for work
- Enable full-disk encryption
- Use password manager (LastPass)
- Report security incidents immediately

**Employees Must Not:**
- Share passwords or API keys
- Use personal email for work
- Store sensitive data on personal devices
- Access production without VPN and MFA

**Violations:**
- First offense: Warning
- Second offense: Final warning
- Third offense: Termination

---

## 11. Physical Security

### 11.1 Data Center Security (AWS)

**Physical Controls:**
- 24/7 security guards
- Biometric access controls
- CCTV surveillance
- Locked server racks

**Environmental Controls:**
- Redundant power (UPS + generators)
- Fire suppression (FM-200)
- Climate control (cooling, humidity)

**Compliance:**
- ISO 27001 certified facilities
- SOC 2 Type II audited

### 11.2 Office Security (Highland AI)

**Edinburgh Office:**
- Key card access (employees only)
- Visitor log (sign-in/sign-out)
- Locked server room (no production systems - cloud-only)
- Clean desk policy (no sensitive documents left out)

**Remote Work:**
- Encrypted laptops (full-disk encryption)
- VPN required for internal systems
- Locked screens when unattended

---

## 12. Penetration Testing

### 12.1 Annual Penetration Test

**Scope:**
- Web application (LOKI portal)
- REST API
- Desktop application (limited scope)
- Infrastructure (AWS configuration)

**Methodology:**
- OWASP Testing Guide
- PTES (Penetration Testing Execution Standard)
- Black-box testing (no insider knowledge)

**Findings:**
- Categorized by severity (Critical, High, Medium, Low)
- Remediation plan with SLAs:
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days
  - Low: Best effort

**Re-Test:**
- Critical and High findings re-tested within 30 days

### 12.2 Bug Bounty Program

**Planned:** Q2 2026
**Platform:** HackerOne or Bugcrowd
**Rewards:** £100 - £5,000 based on severity
**Scope:** Web app, API, desktop app (not infrastructure)

---

## 13. Incident History

**Since Launch (November 2025):**
- Security incidents: 0
- Data breaches: 0
- Unplanned downtime: 0
- Customer-reported vulnerabilities: 0

**Transparency:**
- Incident history published at: https://status.loki-compliance.com
- Data breach notifications (if any) sent within 72 hours per GDPR

---

## 14. Security Contact

**Report Security Vulnerability:**
- Email: security@highlandai.com
- PGP Key: https://loki-compliance.com/pgp-key
- Response SLA: 24 hours

**Request Security Information:**
- Email: compliance@highlandai.com
- Request SOC 2 report (NDA required)
- Request pen-test summary (redacted)

---

## 15. Conclusion

Highland AI takes security seriously. We employ industry-leading practices, undergo regular audits, and maintain transparency with customers. This whitepaper is updated quarterly. Last update: November 8, 2025.

**Questions?** security@highlandai.com

---

**Highland AI Ltd**
Registered in Scotland: SC123456
**Security Whitepaper Version 1.0**
**Last Updated:** November 8, 2025
