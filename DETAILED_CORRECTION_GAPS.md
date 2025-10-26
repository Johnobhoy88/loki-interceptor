# DETAILED CORRECTION PATTERN GAPS - COMPLETE MAPPING

## FCA_UK - 20 Gaps (80% of module)

### CRITICAL GAPS (4)

#### 1. client_money_segregation (CRITICAL)
**Current Status:** No correction pattern
**Suggestions:**
- "CASS 7 requires client money to be held in segregated client bank accounts separate from firm money with daily reconciliation."
- "CASS 7 MANDATORY: Client money must be held in segregated client bank accounts, not mixed with firm money. This is a fundamental regulatory requirement."
- "CASS 7 requires explicit statement that client money is held in segregated client bank accounts separate from firm money."
- "Explicitly state that client money is held in segregated accounts per CASS 7."

**Pattern Recommendation:** Template for CASS 7 segregated account disclosure statement

---

#### 2. complaint_route_clock (CRITICAL)
**Current Status:** No correction pattern
**Suggestion:**
- "FCA DISP rules require stating: 'We will send you a final response within 8 weeks of receiving your complaint.'"

**Pattern Recommendation:** Template for 8-week complaint response timeline

---

#### 3. cross_cutting_rules (CRITICAL)
**Current Status:** No correction pattern
**Suggestions:**
- "Remove language that may mislead, cause harm, or create barriers to customer objectives. Act in good faith."
- "Demonstrate: (1) acting in good faith, (2) avoiding foreseeable harm, (3) enabling customers to pursue their financial objectives."

**Pattern Recommendation:** Regex patterns for identifying misleading/harmful language

---

#### 4. no_implicit_advice (CRITICAL)
**Current Status:** No correction pattern
**Suggestions:**
- "Remove blanket suitability claims or provide suitability assessments and clear 'not advice' disclaimers before urging clients to act."
- "Providing personal recommendations without assessing suitability breaches COBS 9. Either: (1) Add 'This is not financial advice' disclaimer and 'Seek professional advice' or (2) Conduct suitability assessment and maintain files."
- "Add clear disclaimer or establish proper advised status with suitability."

**Pattern Recommendation:** Template for advice disclaimers and suitability statements

---

### HIGH GAPS (7)

#### 5. conflicts_declaration (HIGH)
**Suggestion:**
- "SYSC 10 requires disclosure of conflicts. If you receive commission, are part of provider group, or have restricted panel, you cannot claim to be independent."
- "Include conflicts of interest policy. Disclose any commissions, ownership relationships, or panel restrictions."

**Pattern Recommendation:** Template for conflicts of interest disclosure

---

#### 6. fair_value (HIGH)
**Suggestions:**
- "Consumer Duty requires firms to demonstrate that products represent fair value. Include rationale showing fees are reasonable relative to benefits."
- "Where guaranteed returns are claimed, explain how fees remain fair value (breakdown, costs vs. benefits, Consumer Duty assessment)."
- "Describe what customers receive for the fees charged to support fair value assessment."

**Pattern Recommendation:** Template for Consumer Duty fair value assessment

---

#### 7. inducements_referrals (HIGH)
**Suggestion:**
- "COBS 2.3 requires disclosure of inducements. State: (1) that you receive a fee/commission, (2) from whom, (3) the amount or how it's calculated, (4) that it doesn't increase customer cost."

**Pattern Recommendation:** Template for inducement disclosure

---

#### 8. support_journey (HIGH)
**Suggestions:**
- "Consumer Duty prohibits creating barriers. Make cancellation and complaints as easy as purchase. Remove unnecessary friction."
- "Provide multiple easy contact routes. Make cancellation/complaints as easy as sign-up."

**Pattern Recommendation:** Structural rules for simplifying customer support processes

---

#### 9. target_audience (HIGH)
**Suggestions:**
- "Product governance requires defined target markets. No product is suitable for everyone. Specify who the product IS and ISN't for."
- "Define target market with specific characteristics (age, risk tolerance, experience, needs) and/or exclusions."

**Pattern Recommendation:** Template for target market definition

---

#### 10. third_party_banks (HIGH)
**Suggestions:**
- "CASS 7.13 requires identifying approved banks, documenting selection criteria, and confirming segregation/monitoring arrangements."
- "CASS 7.13 requires firms to exercise due diligence in selecting banks. State that banks are FCA/PRA authorised and subject to selection criteria and ongoing review."
- "CASS 7.13 requires ongoing monitoring of third-party banks, not just initial selection."

**Pattern Recommendation:** Template for third-party bank approval and monitoring disclosure

---

#### 11. vulnerability_identification (HIGH)
**Suggestions:**
- "FG21/1 requires firms to identify vulnerable customers. Acknowledge vulnerabilities and offer appropriate support."
- "Offer reasonable adjustments, additional support, alternative formats, or flexible arrangements."

**Pattern Recommendation:** Template for vulnerability support and reasonable adjustments

---

### MEDIUM GAPS (9)
- comprehension_aids
- defined_roles
- distribution_controls
- fair_value_assessment_ref
- personal_dealing
- reasonable_adjustments
- (3 more)

---

## GDPR_UK - 7 Gaps (35% of module)

### CRITICAL GAPS (6)

#### 1. automated_decisions (CRITICAL)
**Suggestion:**
- "Add: 'You have the right to request human review of this decision, obtain an explanation, and challenge it.'"

**Pattern Recommendation:** Template for automated decision-making disclosure

---

#### 2. children_data (CRITICAL)
**Suggestion:**
- "State: 'Users under 13 require parental consent. We verify age through...'"

**Pattern Recommendation:** Template for children's data parental consent language

---

#### 3. consent (CRITICAL)
**Suggestions:**
- "Explicitly state the Article 9 lawful basis (e.g. explicit consent) and safeguards for special category data (health, biometric, lifestyle)."
- "Consent must be: (1) Freely given (not forced), (2) Specific (separate for each purpose), (3) Informed (clear info), (4) Unambiguous (clear affirmative action), (5) Easy to withdraw"
- "Include information about how users can withdraw consent"

**Pattern Recommendation:** Regex for forced/implied consent patterns, template for consent statement

---

#### 4. lawful_basis (CRITICAL)
**Suggestion:**
- "State lawful basis: consent, contract, legal obligation, legitimate interest, vital interest, or public task."

**Pattern Recommendation:** Template for lawful basis specification

---

#### 5. purpose (CRITICAL)
**Suggestions:**
- "Specify exact purposes: e.g., 'to process orders', 'to send newsletters', 'to improve website functionality'"
- "State the specific purposes for which personal data is processed and confirm it will not be used for incompatible purposes."

**Pattern Recommendation:** Template for specific purpose limitation

---

#### 6. rights (CRITICAL)
**Suggestion:**
- "List the rights to access, rectification, erasure, portability, restriction, objection, and how to contact the ICO or the DPO."

**Pattern Recommendation:** Template for GDPR data subject rights disclosure

---

### HIGH GAPS (5)

#### 7. dpo_contact (HIGH)
**Suggestion:**
- "Provide DPO contact: 'Contact our Data Protection Officer at dpo@company.com'"

**Pattern Recommendation:** Template for DPO contact information

---

#### 8. international_transfer (HIGH)
**Suggestion:**
- "State safeguards: adequacy decisions, standard contractual clauses, or other legal mechanisms."

**Pattern Recommendation:** Template for international transfer safeguards

---

#### 9. retention (HIGH)
**Suggestions:**
- "Specify exact retention periods (e.g., '6 years for tax records', '2 years for marketing data')"
- "Specify how long personal data is retained and the criteria used to determine retention periods."

**Pattern Recommendation:** Template for data retention period specification

---

#### 10. security (HIGH)
**Suggestion:**
- "Describe encryption, access controls, and organisational measures to protect personal data."

**Pattern Recommendation:** Template for technical security measures

---

#### 11. third_party_sharing (HIGH)
**Suggestions:**
- "Marketing requires explicit consent. Add: 'We will only share your data for marketing with your explicit consent, which you can provide/withdraw at any time.'"
- "List specific third parties or categories: 'We share data with: [service providers]'"

**Pattern Recommendation:** Template for third-party sharing and marketing consent

---

---

## TAX_UK - 12 Gaps (80% of module)

### CRITICAL GAPS (6)

#### 1. payment_method_validation (CRITICAL)
**Suggestion:**
- "Only pay HMRC via official methods: Direct Debit, HMRC online services, or verified HMRC bank accounts."

**Pattern Recommendation:** Regex for detecting invalid payment method claims

---

#### 2. tax_deadline_accuracy (CRITICAL)
**Suggestion:**
- "Key deadlines: Self-assessment paper 31 Oct, online 31 Jan, payment 31 Jan; Corporation Tax payment 9 months + 1 day, return 12 months"

**Pattern Recommendation:** Template for accurate tax deadline statements

---

#### 3. vat_invoice_integrity (CRITICAL)
**Suggestions:**
- "Per HMRC VAT Notice 700/21, a valid VAT invoice must include: (1) unique invoice number, (2) invoice date, (3) supplier name and address, (4) supplier VAT number, (5) customer details, (6) description of goods/services, (7) net amount, (8) VAT amount, (9) total amount"
- "Verify arithmetic: Net + VAT should equal Total"

**Pattern Recommendation:** Regex for VAT invoice element validation

---

#### 4. vat_number_format (CRITICAL)
**Suggestions:**
- "Provide a valid UK VAT number: GB123456789 (or XI123456789 for NI)"
- "UK VAT numbers: GB + 9 digits (or 12 for branch traders), or XI + 9 digits for NI"

**Pattern Recommendation:** Regex for VAT number format validation

---

#### 5. hmrc_scam_detection (CRITICAL)
**Suggestion:**
- "HMRC NEVER: requests payment via gift cards/crypto, threatens arrest, uses non-gov emails, offers refunds via email/text. Report to phishing@hmrc.gov.uk"

**Pattern Recommendation:** Already HAS pattern (hmrc_scam) - but may need enhancement

---

#### 6. vat_threshold (CRITICAL)
**Suggestion:**
- "Current VAT registration threshold is £90,000 (effective April 2024). Must register if turnover exceeds £90k in rolling 12 months OR expects to exceed in next 30 days."

**Pattern Recommendation:** Already HAS pattern (vat_threshold) - but may need updating

---

### HIGH GAPS (5)

#### 7. allowable_expenses (HIGH)
**Suggestions:**
- "Expenses must be 'wholly and exclusively' for business. Not allowable: client entertainment, commuting, personal clothing, fines, gifts over £50."

**Pattern Recommendation:** Regex for non-deductible expense patterns

---

#### 8. capital_revenue_distinction (HIGH)
**Suggestion:**
- "Capital expenditure (vehicles, equipment, buildings) cannot be fully expensed. Use capital allowances/AIA. Depreciation is added back for tax."

**Pattern Recommendation:** Template for capital allowance guidance

---

#### 9. company_limited_suffix (HIGH)
**Suggestion:**
- "Limited companies must display full registered name including 'Limited', 'Ltd', 'LLP', or 'PLC' on all business documents."

**Pattern Recommendation:** Regex for company name validation

---

#### 10. invoice_legal_requirements (HIGH)
**Suggestion:**
- "UK invoices require: unique number, business name & address, customer name & address, date, description of goods/services, amounts."

**Pattern Recommendation:** Template for invoice requirements checklist

---

#### 11. mtd_compliance (HIGH)
**Suggestion:**
- "MTD for VAT: Mandatory for all VAT-registered businesses. Must keep digital records and file via MTD-compatible software."

**Pattern Recommendation:** Already HAS pattern (mtd) - may need enhancement

---

---

## NDA_UK - 7 Gaps (50% of module)

### CRITICAL GAPS (7)

#### 1. consideration (CRITICAL)
**Suggestion:**
- "Either: (1) Execute as a deed with witness, or (2) State nominal consideration: 'In consideration of £1 and other valuable consideration'"

**Pattern Recommendation:** Template for consideration clause

---

#### 2. definition_specificity (CRITICAL)
**Suggestions:**
- "Define: 'Confidential Information means [specific categories] but excludes [standard exclusions]'"
- "Define specific categories (e.g., 'trade secrets, financial data, customer lists, technical specifications') AND exclude information that is: (1) Public domain, (2) Already known, (3) Independently developed, (4) Required by law to disclose"
- "Add: (1) Specific categories of confidential information, (2) Clear exclusions for public/known information"
- "List specific types of information AND standard exclusions"

**Pattern Recommendation:** Template for confidential information definition

---

#### 3. governing_law (CRITICAL)
**Suggestion:**
- "Add: 'This Agreement shall be governed by the laws of England and Wales' (or Scotland/Northern Ireland as appropriate)"

**Pattern Recommendation:** Already HAS pattern (governing_law) - verify implementation

---

#### 4. parties_identified (CRITICAL)
**Suggestion:**
- "State full legal names, registered office addresses, and company numbers for all parties"

**Pattern Recommendation:** Template for party identification

---

#### 5. protected_crime_reporting (CRITICAL)
**Suggestion:**
- "Remove prohibition. Add: 'Nothing prevents reporting criminal offences to police or seeking support from lawyers, medical professionals, or family.'"

**Pattern Recommendation:** Already HAS pattern (crime_reporting) - verify implementation

---

#### 6. protected_harassment (CRITICAL)
**Suggestion:**
- "Add: 'Nothing prevents disclosure of conduct that may constitute harassment or discrimination under the Equality Act 2010.'"

**Pattern Recommendation:** Already HAS pattern (harassment) - verify implementation

---

#### 7. protected_whistleblowing (CRITICAL)
**Suggestion:**
- "Add: 'Nothing in this Agreement prevents the disclosure of information protected under the Public Interest Disclosure Act 1998.'"

**Pattern Recommendation:** Already HAS pattern (whistleblowing) - verify implementation

---

### HIGH GAPS (5)

#### 8. duration_reasonableness (HIGH)
**Suggestion:**
- "Apply fixed term (3-5 years) for general information; perpetual only for genuine trade secrets"

**Pattern Recommendation:** Already HAS pattern (duration) - verify implementation

---

#### 9. gdpr_compliance (HIGH)
**Suggestion:**
- "Add: 'Where Confidential Information includes Personal Data, Recipient shall process such data in compliance with UK GDPR and only for the Permitted Purpose.'"

**Pattern Recommendation:** Already HAS pattern (nda_gdpr) - verify implementation

---

#### 10. permitted_disclosures (HIGH)
**Suggestion:**
- "Add: 'Recipient may disclose Confidential Information to the extent required by law, court order, or regulatory authority.'"

**Pattern Recommendation:** Template for legal disclosure exceptions

---

#### 11. permitted_purpose (HIGH)
**Suggestion:**
- "Narrow purpose: 'solely for evaluating a potential acquisition of...' rather than 'general business purposes'"

**Pattern Recommendation:** Template for narrow purpose definition

---

#### 12. prior_knowledge_exclusion (HIGH)
**Suggestion:**
- "Add: 'Excludes information (a) lawfully known to Recipient prior to disclosure; (b) independently developed without reference to Confidential Information.'"

**Pattern Recommendation:** Template for prior knowledge carve-out

---

---

## HR_SCOTTISH - 13 Gaps (52% of module)

### CRITICAL GAPS (5)

#### 1. disclosure (CRITICAL)
**Suggestion:**
- "Confirm the evidence and documents will be provided in advance of the hearing."

**Pattern Recommendation:** Template for evidence disclosure statement

---

#### 2. dismissal (CRITICAL)
**Suggestion:**
- "Add: 'Please note that a potential outcome of this hearing could be summary dismissal.'"

**Pattern Recommendation:** Template for summary dismissal warning

---

#### 3. informal_threats (CRITICAL)
**Suggestion:**
- "Use formal disciplinary procedure: arrange proper meeting, provide specific allegations, notify of right to accompaniment, allow time to prepare, conduct fair hearing."

**Pattern Recommendation:** Template for formal disciplinary procedure requirements

---

#### 4. accompaniment (CRITICAL)
**Suggestion:**
- "Add: 'You have the statutory right to be accompanied at this meeting by a work colleague or trade union representative. Please inform us in advance if you wish to be accompanied and provide the name of your companion.'"

**Pattern Recommendation:** Already HAS pattern (accompaniment) - verify implementation

---

#### 5. appeal (CRITICAL)
**Suggestions:**
- "Add: 'You have the right to appeal this decision. Please submit your appeal in writing within [X] days.'"
- "ACAS recommends 5-10 working days for appeals."
- "State: 'If you wish to appeal, you must submit your appeal in writing within [5-10] working days to [appropriate person].'"

**Pattern Recommendation:** Already HAS pattern (appeal) - verify implementation

---

### HIGH GAPS (6)

#### 6. allegations (HIGH)
**Suggestions:**
- "Include: (1) Specific dates and times, (2) Exact locations, (3) Clear description of what was said/done, (4) Names of witnesses, (5) Specific examples of conduct/behavior."
- "Add more specific details: dates, times, locations, and concrete examples."

**Pattern Recommendation:** Template for specific allegation statement

---

#### 7. evidence (HIGH)
**Suggestion:**
- "Refer to the evidence relied upon and state what is attached/enclosed."

**Pattern Recommendation:** Already HAS pattern (evidence) - verify implementation

---

#### 8. impartial_chair (HIGH)
**Suggestion:**
- "State that the hearing will be chaired by someone impartial and not previously involved."

**Pattern Recommendation:** Already HAS pattern (impartial_chair) - verify implementation

---

#### 9. investigation (HIGH)
**Suggestion:**
- "Reference investigation: 'Following an investigation into the allegations...'"

**Pattern Recommendation:** Template for investigation reference

---

#### 10. meeting_notice (HIGH)
**Suggestion:**
- "Provide at least 48 hours notice for disciplinary meetings. Specify date, time, and location clearly."

**Pattern Recommendation:** Already HAS pattern (notice) - verify implementation

---

#### 11. outcome_reasons (HIGH)
**Suggestion:**
- "State: 'Following investigation, we found that... Our decision is based on...'"

**Pattern Recommendation:** Template for decision reasoning

---

#### 12. postponement (HIGH)
**Suggestion:**
- "State that the meeting may be postponed if the companion is unavailable on the proposed date."

**Pattern Recommendation:** Template for meeting postponement statement

---

#### 13. previous_warnings (HIGH)
**Suggestion:**
- "For non-gross misconduct, reference prior warnings: 'Following your final written warning...'"

**Pattern Recommendation:** Template for prior warnings reference

---

---

## APPENDIX: SUGGESTED PATTERN IMPLEMENTATION STRATEGY

### By Regulatory Domain

**FCA_UK (20 gaps):** Implement templates for financial promotions, Consumer Duty disclosures, and client money protections first (CASS 7, financial promotion approval, risk/benefit balance)

**GDPR_UK (7 gaps):** Prioritize data subject rights, consent, and automated decision-making templates for GDPR compliance

**TAX_UK (12 gaps):** Focus on payment validation, invoice requirements, and deadline accuracy to prevent fraud and compliance failures

**NDA_UK (7 gaps):** Implement protective provisions (whistleblowing, harassment, crime reporting) and definition/purpose carve-outs

**HR_SCOTTISH (13 gaps):** Add disciplinary procedure templates and evidence disclosure to ensure employment law compliance

### By Severity

**CRITICAL (31):** Complete within 2 weeks - these are regulatory blockers
**HIGH (35):** Complete within 1 month - required for compliance
**MEDIUM (16):** Complete within 3 months - good practice

### By Pattern Type

**Templates (majority):** Start here - highest impact and easiest to implement
**Regex Patterns (secondary):** For language validation and fraud detection
**Structural Rules (few):** For document reordering and process improvements

