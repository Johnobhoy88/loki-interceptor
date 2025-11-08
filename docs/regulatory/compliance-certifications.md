# LOKI Compliance Certifications Roadmap

**Highland AI Ltd** | November 2025

---

## Executive Summary

LOKI's roadmap targets three critical certifications for RegTech trust and market access:
1. **ISO 27001** (Information Security) - Q2 2026
2. **SOC 2 Type II** (Security, Availability, Confidentiality) - Q2 2026
3. **Cyber Essentials Plus** (UK Government Security) - Q1 2026

---

## 1. ISO 27001 - Information Security Management

**Target Date:** June 2026
**Certification Body:** BSI (British Standards Institution)
**Scope:** LOKI SaaS platform, API, desktop application

### What is ISO 27001?

International standard for Information Security Management Systems (ISMS). Demonstrates systematic approach to managing sensitive company and customer information.

### Why ISO 27001?

- **Customer Requirement:** 67% of Enterprise buyers require ISO 27001 (Gartner)
- **Regulatory Alignment:** FCA, ICO expect robust security frameworks
- **Competitive Advantage:** BrightHR and Peninsula not ISO 27001 certified
- **Risk Management:** Systematic approach to identifying and mitigating security risks

### Certification Process

**Phase 1: Gap Analysis (Q4 2025 - 1 month)**
- Audit current security practices
- Identify gaps vs. ISO 27001:2022 requirements
- Prioritize remediation efforts

**Phase 2: Implementation (Q1 2026 - 3 months)**
- Establish ISMS governance (policies, procedures)
- Implement missing controls (114 controls in Annex A)
- Train employees on information security
- Conduct internal audits

**Phase 3: Stage 1 Audit (May 2026)**
- BSI reviews documentation
- Assess readiness for Stage 2
- Identify any gaps requiring remediation

**Phase 4: Stage 2 Audit (June 2026)**
- BSI conducts on-site/remote audit
- Test controls implementation
- Interview employees
- Review evidence

**Phase 5: Certification (June 2026)**
- BSI issues ISO 27001 certificate (3-year validity)
- Surveillance audits annually
- Recertification audit after 3 years

### Key Controls Implemented

**A.5 - Information Security Policies**
- Information Security Policy published and reviewed annually
- Executive management approval and communication

**A.8 - Asset Management**
- Asset register maintained (hardware, software, data)
- Data classification scheme (Public, Internal, Confidential, Restricted)
- Acceptable use policy for IT assets

**A.9 - Access Control**
- Access control policy (least privilege, need-to-know)
- User access reviews quarterly
- MFA required for all employees and Enterprise customers

**A.10 - Cryptography**
- Cryptographic controls policy
- AES-256 encryption at rest, TLS 1.3 in transit
- Key management via AWS KMS

**A.12 - Operations Security**
- Change management procedures
- Capacity management and monitoring
- Malware protection (endpoint, email, web)

**A.13 - Communications Security**
- Network security controls (firewall, IDS/IPS)
- Secure communication channels (VPN, TLS)
- Network segmentation (production, staging, development)

**A.14 - System Acquisition, Development and Maintenance**
- Secure development lifecycle (SDLC)
- Security testing in CI/CD pipeline (SAST, DAST)
- Secure coding standards

**A.16 - Information Security Incident Management**
- Incident response plan documented and tested
- Incident classification and escalation procedures
- Post-incident review and lessons learned

**A.17 - Business Continuity**
- Business continuity plan (BCP)
- Disaster recovery plan (DRP)
- Backup and restore procedures tested quarterly

**A.18 - Compliance**
- Legal and regulatory compliance register
- Independent security audits annually
- Data protection compliance (UK GDPR)

### Investment Required

| Item | Cost | Timeline |
|------|------|----------|
| Gap analysis consultant | £5,000 | Q4 2025 |
| ISMS implementation | £15,000 | Q1 2026 |
| BSI certification audit | £8,000 | Q2 2026 |
| Employee training | £2,000 | Q1 2026 |
| **Total Year 1** | **£30,000** | |
| **Annual surveillance audits** | **£4,000/year** | Ongoing |

---

## 2. SOC 2 Type II - Service Organization Control

**Target Date:** July 2026
**Auditor:** Deloitte or PwC
**Trust Service Criteria:** Security, Availability, Confidentiality

### What is SOC 2?

US-based audit framework for service providers storing customer data. Type II report evaluates controls over time (6-12 months), not just design (Type I).

### Why SOC 2?

- **US Market Entry:** Required by US Enterprise customers (60% demand SOC 2)
- **SaaS Standard:** Industry expectation for cloud software vendors
- **Customer Confidence:** Third-party validation of security controls
- **Competitive Advantage:** LawGeex has SOC 2, we need parity

### Trust Service Criteria Covered

**1. Security (Required)**
- Access controls, MFA, encryption
- Network security (firewalls, IDS)
- Vulnerability management
- Incident response

**2. Availability (Included)**
- 99.9% uptime SLA
- Disaster recovery and business continuity
- Capacity planning and monitoring
- Redundancy and failover

**3. Confidentiality (Included)**
- Encryption of sensitive data
- Data classification and handling
- NDA agreements with employees and vendors
- Secure disposal of data

**Not Included:** Processing Integrity, Privacy (optional criteria)

### Audit Process

**Phase 1: Readiness Assessment (Q1 2026 - 1 month)**
- Gap analysis vs. SOC 2 requirements
- Identify control weaknesses
- Remediation plan

**Phase 2: Control Implementation (Q2 2026 - 3 months)**
- Implement missing controls
- Document policies and procedures
- Evidence collection system

**Phase 3: Observation Period (Q2-Q3 2026 - 6 months)**
- Auditor observes controls in operation
- Collect evidence (logs, screenshots, interviews)
- Minimum 6 months for Type II

**Phase 4: Audit and Report (July 2026)**
- Auditor tests controls (sampling approach)
- Interviews key personnel
- Reviews evidence
- Issues SOC 2 Type II report

**Phase 5: Remediation (if needed)**
- Address any control failures identified
- Re-audit affected controls
- Final report issuance

### Key Controls Implemented

**CC1 - Control Environment**
- Code of conduct and ethics policy
- Organizational structure and reporting lines
- Background checks for employees with data access

**CC2 - Communication and Information**
- Communication of security policies to all employees
- Incident communication procedures
- Change management communication

**CC3 - Risk Assessment**
- Risk assessment process (identify, assess, mitigate)
- Quarterly risk reviews
- Threat modeling for new features

**CC4 - Monitoring Activities**
- Continuous monitoring of security events
- Quarterly access reviews
- Annual penetration testing
- Internal audits semi-annually

**CC5 - Control Activities**
- Change management procedures
- Segregation of duties
- Configuration management
- Patch management

**CC6 - Logical and Physical Access Controls**
- MFA for all user accounts
- Password policy (complexity, rotation)
- Physical access controls (AWS data centers)
- Privileged access management (PAM)

**CC7 - System Operations**
- Monitoring and alerting (24/7)
- Incident response procedures
- Capacity planning
- Job scheduling and automation

**CC8 - Change Management**
- Change approval process
- Testing in staging environment
- Rollback procedures
- Change log maintained

**CC9 - Risk Mitigation**
- Firewall rules and network segmentation
- Vulnerability scanning and patching
- Malware protection
- DDoS mitigation (Cloudflare)

**A1 - Availability**
- 99.9% uptime monitoring
- Disaster recovery plan tested quarterly
- Redundant infrastructure (multi-AZ)
- Backup and restore procedures

**C1 - Confidentiality**
- AES-256 encryption at rest
- TLS 1.3 encryption in transit
- Data classification policy
- Confidentiality agreements with employees

### Investment Required

| Item | Cost | Timeline |
|------|------|----------|
| Readiness assessment | £10,000 | Q1 2026 |
| Control implementation | £20,000 | Q2 2026 |
| SOC 2 Type II audit | £35,000 | Q3 2026 |
| Remediation (if needed) | £5,000 | Q3 2026 |
| **Total Year 1** | **£70,000** | |
| **Annual re-audit** | **£30,000/year** | Ongoing |

---

## 3. Cyber Essentials Plus - UK Government Security

**Target Date:** March 2026
**Certification Body:** IASME (UK Government approved)
**Scope:** Highland AI corporate IT infrastructure

### What is Cyber Essentials Plus?

UK Government-backed scheme certifying basic cybersecurity hygiene. "Plus" level includes technical verification (vulnerability scans, penetration testing).

### Why Cyber Essentials Plus?

- **UK Government Contracts:** Required for public sector contracts (>£5M)
- **Cyber Insurance:** Reduces premiums (10-30% discount)
- **Customer Confidence:** UK-specific, recognized by UK businesses
- **Low Cost, High Value:** £2K certification, significant credibility boost

### Five Technical Controls

**1. Firewalls and Internet Gateways**
- AWS Security Groups configured correctly
- Deny-all-except-necessary rules
- No public access to databases
- VPN for employee remote access

**2. Secure Configuration**
- Hardened OS images (AWS AMI)
- Unnecessary services disabled
- Default passwords changed
- Configuration management (Terraform)

**3. User Access Control**
- Unique user accounts (no shared accounts)
- Guest accounts disabled
- MFA enabled for all users
- Privileged accounts limited and monitored

**4. Malware Protection**
- Endpoint protection on all laptops (CrowdStrike)
- Email malware scanning (Microsoft 365 ATP)
- Web content filtering
- Automatic updates enabled

**5. Security Update Management**
- OS patches applied within 14 days of release
- Critical patches applied within 48 hours
- Application patches managed (dependency scanning)
- Patch testing in staging before production

### Certification Process

**Phase 1: Self-Assessment (January 2026)**
- Complete Cyber Essentials questionnaire
- Document current security controls
- Identify gaps and remediate

**Phase 2: External Assessment (February 2026)**
- IASME-approved assessor conducts vulnerability scan
- Reviews evidence of security controls
- Conducts penetration testing (web app, infrastructure)

**Phase 3: Certification (March 2026)**
- Assessor issues Cyber Essentials Plus certificate (1-year validity)
- Certificate valid for 12 months
- Annual renewal required

### Investment Required

| Item | Cost | Timeline |
|------|------|----------|
| Internal preparation | £1,000 | Jan 2026 |
| CE Plus certification | £2,000 | Feb-Mar 2026 |
| **Total Year 1** | **£3,000** | |
| **Annual renewal** | **£2,000/year** | Ongoing |

---

## Certification Timeline

```
2025 Q4: ISO 27001 Gap Analysis
         Cyber Essentials Preparation

2026 Q1: ISO 27001 Implementation
         Cyber Essentials Certification (March)
         SOC 2 Readiness Assessment

2026 Q2: ISO 27001 Audit (June)
         SOC 2 Control Implementation
         SOC 2 Observation Period Begins

2026 Q3: SOC 2 Observation Period
         SOC 2 Audit (July)

2026 Q4: All three certifications achieved
         Surveillance/Renewal planning
```

---

## Total Investment Summary

| Certification | Year 1 Cost | Annual Cost (Ongoing) |
|---------------|-------------|---------------------|
| ISO 27001 | £30,000 | £4,000 |
| SOC 2 Type II | £70,000 | £30,000 |
| Cyber Essentials Plus | £3,000 | £2,000 |
| **TOTAL** | **£103,000** | **£36,000/year** |

**ROI Justification:**
- Unlock Enterprise market (50% of prospects require certifications)
- Increase deal velocity (reduce security questionnaire time by 80%)
- Command premium pricing (+20% for certified vendors)
- Reduce cyber insurance premiums (-20%)

**Break-Even:** 5 Enterprise customers (£24K/year each) = £120K revenue offsets £103K investment

---

## Compliance Dashboard

Once certified, Highland AI will provide public-facing compliance dashboard:

**https://compliance.loki-compliance.com**

- ISO 27001 certificate (PDF download)
- SOC 2 Type II report (NDA required)
- Cyber Essentials Plus certificate
- Penetration test summary (redacted)
- Security policies (public versions)
- Incident history (last 12 months)

---

## Customer Benefits

**For Enterprise Customers:**
- Faster security due diligence (pre-answered questionnaires)
- Confidence in security posture (third-party validated)
- Regulatory compliance (trickle-down requirement satisfaction)
- Reduced vendor risk

**For All Customers:**
- Enhanced data protection
- Increased service reliability (availability controls)
- Transparent security practices
- Competitive credibility

---

## Contact

**Compliance Questions:** compliance@highlandai.com
**Request SOC 2 Report:** soc2@highlandai.com (NDA required)
**Security Inquiries:** security@highlandai.com

---

**Highland AI Ltd**
Registered in Scotland: SC123456
**Last Updated:** November 8, 2025
