# Data Processing Agreement (DPA)

**Between Customer ("Data Controller") and Highland AI Ltd ("Data Processor")**

**Effective Date:** Upon Service commencement
**DPA Version:** 1.0 (November 2025)

---

## 1. Definitions

**Personal Data:** As defined in UK GDPR Article 4(1)
**Processing:** As defined in UK GDPR Article 4(2)
**Data Subject:** Individual whose Personal Data is processed
**UK GDPR:** UK General Data Protection Regulation and Data Protection Act 2018
**Service:** LOKI Interceptor compliance platform

---

## 2. Scope and Roles

**2.1 Data Controller:** Customer determines purposes and means of processing Personal Data.

**2.2 Data Processor:** Highland AI processes Personal Data on behalf of Customer per this DPA.

**2.3 Processing Activities:**
- Validating documents containing Personal Data against compliance rules
- Storing audit logs of validation results
- Providing API access to validation services
- Customer support (processing support ticket content)

**2.4 Types of Personal Data Processed:**
- Names, contact details (in documents uploaded for validation)
- User account information (Customer's employees using Service)
- IP addresses, device information (logs)

**2.5 Categories of Data Subjects:**
- Customer's employees (users of Service)
- Customer's clients (whose data appears in documents validated)
- Third parties mentioned in documents

---

## 3. Processor Obligations (UK GDPR Article 28)

Highland AI shall:

**3.1** Process Personal Data only on documented instructions from Customer (these Terms + DPA).

**3.2** Ensure persons authorized to process Personal Data have committed to confidentiality.

**3.3** Implement appropriate technical and organizational measures (see Annex A).

**3.4** Engage sub-processors only with Customer's consent (see Section 5).

**3.5** Assist Customer in responding to Data Subject rights requests (see Section 6).

**3.6** Assist Customer with Data Protection Impact Assessments (DPIAs) if requested.

**3.7** Notify Customer of personal data breaches within 48 hours of becoming aware.

**3.8** Delete or return Personal Data upon termination of Service (see Section 9).

**3.9** Make available all information necessary to demonstrate compliance with UK GDPR Article 28.

**3.10** Allow and contribute to audits by Customer or auditor mandated by Customer (reasonable notice required).

---

## 4. Customer Obligations (Data Controller)

Customer shall:

**4.1** Ensure lawful basis for processing Personal Data uploaded to Service.

**4.2** Provide necessary notices to Data Subjects (privacy policy, consent forms).

**4.3** Not upload special categories of Personal Data (Art. 9) or criminal data (Art. 10) without explicit written agreement.

**4.4** Ensure instructions to Highland AI comply with UK GDPR and other applicable laws.

**4.5** Notify Highland AI if Customer believes instructions violate UK GDPR.

---

## 5. Sub-Processors

**5.1 Approved Sub-Processors:**

Customer provides general authorization for Highland AI to engage following sub-processors:

| Sub-Processor | Service | Location | Safeguards |
|---------------|---------|----------|------------|
| **Anthropic Inc.** | AI analysis (Claude API) | USA | Standard Contractual Clauses (SCCs) |
| **Amazon Web Services (AWS)** | Cloud hosting, database | UK (London) | AWS GDPR DPA, ISO 27001 |
| **Stripe** | Payment processing | EU/UK | Stripe GDPR DPA, PCI DSS Level 1 |
| **Intercom** | Customer support | EU | Intercom GDPR DPA |

**5.2 New Sub-Processors:**
- Highland AI will notify Customer 30 days before engaging new sub-processor
- Customer may object in writing within 30 days
- If Customer objects, Highland AI will (a) not engage sub-processor, or (b) allow Customer to terminate contract with refund

**5.3 Sub-Processor Requirements:**
- Highland AI ensures sub-processors provide same data protection obligations as this DPA
- Highland AI remains liable to Customer for sub-processor performance

---

## 6. Data Subject Rights (UK GDPR Chapter III)

Highland AI will assist Customer in responding to Data Subject requests:

**6.1 Right to Access (Art. 15):**
- Highland AI will provide Customer with Personal Data in its possession within 72 hours

**6.2 Right to Rectification (Art. 16):**
- Highland AI will correct inaccurate Personal Data within 72 hours upon Customer instruction

**6.3 Right to Erasure (Art. 17):**
- Highland AI will delete Personal Data within 30 days upon Customer instruction

**6.4 Right to Restrict Processing (Art. 18):**
- Highland AI will restrict processing per Customer instruction

**6.5 Right to Data Portability (Art. 20):**
- Highland AI will provide Personal Data in JSON format within 30 days

**6.6 Right to Object (Art. 21):**
- Highland AI will cease processing if Customer instructs (may affect Service availability)

**Assistance Fee:**
- First 2 requests/year: No charge
- Additional requests: £500/request (covers engineering time)

---

## 7. Data Security (UK GDPR Article 32)

**Technical Measures (see Annex A for detail):**
- AES-256 encryption at rest
- TLS 1.3 encryption in transit
- Access controls (RBAC, MFA)
- Intrusion detection systems

**Organizational Measures:**
- Employee data protection training (annual)
- Background checks for data access roles
- Security incident response plan
- Annual penetration testing

**Data Breach Notification:**
- Highland AI will notify Customer within 48 hours of becoming aware
- Notification includes: nature of breach, affected data, likely consequences, mitigation measures
- Customer responsible for notifying ICO and Data Subjects per UK GDPR Art. 33-34

---

## 8. International Data Transfers

**8.1 Transfers to USA (Anthropic):**
- **Mechanism:** Standard Contractual Clauses (SCCs) - UK ICO Addendum
- **Safeguards:** Anthropic does not store data, processes only for immediate API response
- **Customer Consent:** By using Service, Customer consents to this transfer
- **Objection:** Customer may object (will limit Service functionality - no AI analysis)

**8.2 Transfers within UK/EU:**
- Primary data storage: AWS London (UK)
- No additional safeguards required (adequacy decision)

---

## 9. Data Retention and Deletion

**9.1 Retention Periods:**
- Account data: Account lifetime + 90 days
- Audit logs: 90 days (configurable by Customer: 30-365 days)
- Backup data: 30 days

**9.2 Deletion Upon Termination:**
- Within 30 days of contract termination, Highland AI will:
  - Delete all Personal Data from production systems
  - Delete all Personal Data from backups (or render inaccessible)
  - Provide written certification of deletion
- **Exception:** Data required for legal obligations (billing records: 7 years per HMRC)

**9.3 Data Return:**
- Customer may request data export before deletion
- Highland AI will provide JSON export within 30 days
- Fee: £500 for >10GB data exports

---

## 10. Audits and Compliance

**10.1 Customer Audit Rights:**
- Customer may audit Highland AI once per year (reasonable notice: 30 days)
- Audit scope: Data processing activities, security controls, compliance with DPA
- Audit conducted by Customer or independent auditor
- Audit during business hours, minimal disruption to operations

**10.2 Highland AI Certifications:**
- ISO 27001 (target: Q2 2026)
- SOC 2 Type II (target: Q2 2026)
- Cyber Essentials Plus (target: Q1 2026)

**10.3 Compliance Reports:**
- Highland AI will provide SOC 2 report annually upon request
- Fee: £250 (covers NDA execution and report provision)

---

## 11. Liability and Indemnification

**11.1 Highland AI Liability:**
- Highland AI liable for damages caused by violating UK GDPR Art. 28 obligations
- Liability capped at amount Customer paid in past 12 months (unless fraud/gross negligence)

**11.2 Customer Liability:**
- Customer liable for damages caused by unlawful instructions to Highland AI
- Customer indemnifies Highland AI for regulatory fines resulting from Customer's unlawful instructions

**11.3 Sub-Processor Liability:**
- Highland AI remains liable for sub-processor acts/omissions

---

## 12. Term and Termination

**12.1 Term:**
- This DPA effective upon Service commencement
- Continues until all Personal Data deleted per Section 9

**12.2 Termination for Breach:**
- Either party may terminate if other party materially breaches DPA
- 30 days' written notice required (unless breach not curable)

**12.3 Effect of Termination:**
- Highland AI ceases processing Personal Data immediately
- Highland AI deletes/returns Personal Data per Section 9
- Survival: Sections 9 (deletion), 10 (audits), 11 (liability) survive termination

---

## 13. Governing Law and Jurisdiction

- Governed by laws of Scotland
- Disputes subject to exclusive jurisdiction of Scottish courts
- Arbitration option available (Scottish Arbitration Rules)

---

## 14. Changes to DPA

- Highland AI may amend DPA with 90 days' notice
- Material changes require Customer consent
- Customer may terminate if objects to changes (pro-rated refund)

---

## 15. Contact

**DPA Questions:** dpa@highlandai.com
**Data Protection Officer:** dpo@highlandai.com
**Security Incidents:** security@highlandai.com

---

## ANNEX A: Technical and Organizational Measures

### A.1 Access Control

**Physical Access:**
- AWS data centers: Biometric access, 24/7 security guards
- Highland AI offices: Key card access, visitor logs

**Logical Access:**
- Multi-factor authentication (MFA) for all employees
- Role-based access control (RBAC) - principle of least privilege
- Access reviews quarterly
- Immediate revocation upon employee termination

### A.2 Encryption

**At Rest:**
- AES-256 encryption (AWS KMS managed keys)
- Database encryption enabled
- Backup encryption enabled

**In Transit:**
- TLS 1.3 for all API communication
- HTTPS enforced (HTTP redirected)
- Certificate validation required

### A.3 Pseudonymization

- Document content processed without linking to user account (where possible)
- Audit logs use hashed identifiers
- IP address anonymization in analytics

### A.4 Data Minimization

- Collect only Personal Data necessary for Service provision
- Document content not stored after processing (in-memory only)
- Audit logs configurable (Customer controls retention: 30-365 days)

### A.5 Availability and Resilience

- AWS multi-AZ deployment (high availability)
- Automated backups every 6 hours
- DDoS protection (Cloudflare)
- Load balancing across multiple servers

### A.6 Testing and Evaluation

- Annual penetration testing (third-party security firm)
- Quarterly vulnerability scans
- Continuous integration security testing (SAST, DAST)
- Bug bounty program (planned Q2 2026)

### A.7 Incident Response

- 24/7 automated monitoring (alerts for anomalies)
- Incident response plan documented and tested
- Data breach notification process (GDPR Art. 33-34)
- Post-incident review and remediation

### A.8 Employee Training

- Annual GDPR training for all employees
- Specialized training for engineers with data access
- Confidentiality agreements signed by all employees
- Background checks for data access roles

---

## ANNEX B: Sub-Processor Details

### Anthropic Inc.

**Service:** AI analysis via Claude API
**Data Processed:** Document text (anonymized)
**Location:** United States
**Transfer Mechanism:** Standard Contractual Clauses (UK ICO Addendum)
**Data Retention:** No retention (per Anthropic API terms - immediate processing, no storage)
**Certifications:** SOC 2 Type II

**Contact:** privacy@anthropic.com

---

### Amazon Web Services (AWS)

**Service:** Cloud hosting, database, backups
**Data Processed:** All Service data
**Location:** UK (London region - eu-west-2)
**Transfer Mechanism:** N/A (UK-based)
**Data Retention:** Per Highland AI instructions (automatic deletion per retention policies)
**Certifications:** ISO 27001, SOC 2 Type II, PCI DSS

**DPA:** https://aws.amazon.com/service-terms/ (Data Processing Addendum)

---

### Stripe

**Service:** Payment processing
**Data Processed:** Payment card details, billing address, email
**Location:** EU/UK
**Transfer Mechanism:** N/A (EU/UK-based)
**Data Retention:** Per PCI DSS requirements (cardholder data deleted after processing)
**Certifications:** PCI DSS Level 1, ISO 27001

**DPA:** https://stripe.com/gb/privacy (GDPR compliant)

---

### Intercom

**Service:** Customer support chat
**Data Processed:** Name, email, support messages
**Location:** EU (Dublin data center)
**Transfer Mechanism:** N/A (EU-based)
**Data Retention:** 3 years (support ticket history)
**Certifications:** ISO 27001, SOC 2 Type II

**DPA:** https://www.intercom.com/legal/dpa

---

**Highland AI Ltd**
Registered in Scotland: SC123456
VAT: GB999999999
**Last Updated:** November 8, 2025

---

**Customer Acceptance:**

By using LOKI Service, Customer accepts this Data Processing Agreement.

For executed counterpart, contact: dpa@highlandai.com
