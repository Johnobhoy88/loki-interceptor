"""
Correction Patterns - Gate-Specific Correction Rules
Organized by regulatory module: FCA UK, GDPR UK, Tax UK, NDA UK, HR Scottish
"""
import re
from typing import Dict, List


class CorrectionPatternRegistry:
    """Registry of all correction patterns organized by gate"""

    def __init__(self):
        self.regex_patterns = {}
        self.templates = {}
        self.structural_rules = {}

        # Initialize patterns for all modules
        self._init_fca_uk_patterns()
        self._init_gdpr_uk_patterns()
        self._init_tax_uk_patterns()
        self._init_nda_uk_patterns()
        self._init_hr_scottish_patterns()

        # Initialize expanded patterns (100+ additional patterns)
        self._expand_fca_uk_patterns()
        self._expand_gdpr_uk_patterns()
        self._expand_tax_uk_patterns()
        self._expand_nda_uk_patterns()
        self._expand_hr_scottish_patterns()

    # ===========================================
    # FCA UK - Financial Conduct Authority
    # ===========================================

    def _init_fca_uk_patterns(self):
        """FCA UK compliance correction patterns"""

        # Risk/Benefit Balance corrections
        self.regex_patterns['risk_benefit'] = [
            {
                'pattern': r'(?:high|significant|attractive|strong)\s+(?:return|yield|performance)',
                'replacement': r'potential returns (capital at risk)',
                'reason': 'FCA COBS 4.2.3 - Balance benefits with risk warnings',
                'flags': re.IGNORECASE
            }
        ]

        self.templates['risk_benefit'] = [
            {
                'template': '⚠️ RISK WARNING: The value of investments can fall as well as rise and you may get back less than you invest. Past performance is not a reliable indicator of future results.',
                'position': 'after_header',
                'condition': r'(?:investment|return|profit|yield)'
            }
        ]

        # Generic risk warning corrections
        self.regex_patterns['risk_warning'] = [
            {
                'pattern': r'investments can go down as well as up',
                'replacement': 'The value of investments can fall as well as rise and you may get back less than you invest',
                'reason': 'FCA-compliant risk warning language',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:prices|values)\s+may\s+(?:fluctuate|vary)',
                'replacement': 'The value of investments can fall as well as rise and you may get back less than you invest',
                'reason': 'Strengthen risk warning to FCA standard',
                'flags': re.IGNORECASE
            }
        ]

        # Target market definition
        self.templates['target_market'] = [
            {
                'template': 'TARGET MARKET: This product is designed for [specify characteristics: knowledge level, financial situation, risk tolerance, investment objectives].',
                'position': 'after_header',
                'condition': r'(?:product|service|investment)'
            }
        ]

        # FOS (Financial Ombudsman Service) signposting
        self.templates['fos_signposting'] = [
            {
                'template': 'COMPLAINTS: If you have a complaint, please contact us. If we cannot resolve your complaint, you may refer it to the Financial Ombudsman Service (www.financial-ombudsman.org.uk).',
                'position': 'before_signature',
                'condition': r'(?:financial|service|product)'
            }
        ]

        # Fair, Clear, Not Misleading corrections
        self.regex_patterns['fair_clear'] = [
            {
                'pattern': r'guaranteed\s+(?:returns|profit|gains)',
                'replacement': 'potential returns (not guaranteed)',
                'reason': 'FCA COBS 4.2.1 - Remove misleading guarantees',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'risk-free\s+(?:investment|return)',
                'replacement': 'lower-risk investment (capital at risk)',
                'reason': 'No investment is risk-free - FCA compliance',
                'flags': re.IGNORECASE
            }
        ]

        # Promotions approval
        self.templates['promotions_approval'] = [
            {
                'template': 'This financial promotion has been approved by [FCA authorised firm name, FRN: XXXXXX].',
                'position': 'start',
                'condition': r'(?:investment|financial product|promotion)'
            }
        ]

        # Client Money Segregation (CASS 7)
        self.templates['client_money_segregation'] = [
            {
                'template': 'CLIENT MONEY PROTECTION: Your funds are held in segregated client bank accounts separate from our firm money, in accordance with FCA CASS 7 rules. Daily reconciliation is performed to ensure your money is protected.',
                'position': 'after_header',
                'condition': r'(?:client money|client funds|segregat|account)'
            }
        ]

        # Complaint Route Clock (8-week rule)
        self.templates['complaint_route_clock'] = [
            {
                'template': 'COMPLAINT RESPONSE TIMELINE: We will send you a final response within 8 weeks of receiving your complaint, as required by FCA DISP rules.',
                'position': 'before_signature',
                'condition': r'(?:complaint|grievance|dispute)'
            }
        ]

        # Cross-Cutting Rules (Consumer Duty - Act in Good Faith)
        self.regex_patterns['cross_cutting'] = [
            {
                'pattern': r'(?:mandatory|compulsory|you must|required to).*(?:purchase|buy|accept)',
                'replacement': 'you may choose to',
                'reason': 'Consumer Duty - Remove coercive language',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:automatically|by default).*(?:enrolled|signed up|subscribed)',
                'replacement': 'you can choose to enroll',
                'reason': 'Consumer Duty - Avoid foreseeable harm',
                'flags': re.IGNORECASE
            }
        ]

        # No Implicit Advice
        self.templates['no_implicit_advice'] = [
            {
                'template': '''IMPORTANT: This is not financial advice. This information is provided for general purposes only and does not constitute a personal recommendation. You should seek independent financial advice before making any investment decisions.''',
                'position': 'start',
                'condition': r'(?:invest|purchase|buy|recommend|suitable|should)'
            }
        ]

        self.regex_patterns['no_implicit_advice'] = [
            {
                'pattern': r'(?:you should|we recommend you|this is suitable for you)',
                'replacement': '[REMOVED - requires suitability assessment for personal recommendations]',
                'reason': 'FCA COBS 9 - Personal recommendations require suitability assessment',
                'flags': re.IGNORECASE
            }
        ]

        # Conflicts of Interest Declaration (SYSC 10)
        self.templates['conflicts_declaration'] = [
            {
                'template': '''CONFLICTS OF INTEREST: We maintain a conflicts of interest policy. [Specify: commission arrangements, ownership relationships, panel restrictions, or other conflicts]. We are committed to managing conflicts in your best interests.''',
                'position': 'before_signature',
                'condition': r'(?:financial|advice|recommend|product|service)'
            }
        ]

        # Fair Value Assessment (Consumer Duty)
        self.templates['fair_value'] = [
            {
                'template': '''FAIR VALUE ASSESSMENT: Under the Consumer Duty, we assess that this product represents fair value. Our fees are reasonable relative to the benefits provided, taking into account [specify: services, features, market comparison, costs].''',
                'position': 'after_header',
                'condition': r'(?:fee|charge|cost|price|payment)'
            }
        ]

        # Inducements and Referrals Disclosure (COBS 2.3)
        self.templates['inducements_referrals'] = [
            {
                'template': '''INDUCEMENTS DISCLOSURE: We receive [fee/commission] from [provider name] for this product. The amount is [specify amount or calculation method]. This does not increase the cost you pay.''',
                'position': 'before_signature',
                'condition': r'(?:commission|fee|referral|introducer)'
            }
        ]

        # Support Journey (Consumer Duty - No Barriers)
        self.templates['support_journey'] = [
            {
                'template': '''CUSTOMER SUPPORT: You can contact us via [phone/email/post/online]. Cancellation and complaints are as easy as sign-up. We do not create unnecessary barriers to customer service.''',
                'position': 'before_signature',
                'condition': r'(?:contact|support|help|cancel|complaint)'
            }
        ]

        # Target Audience (Product Governance)
        self.templates['target_audience'] = [
            {
                'template': '''TARGET AUDIENCE: This product is designed for customers with [specify: knowledge level, experience, risk tolerance, financial situation, objectives]. This product is NOT suitable for [specify exclusions].''',
                'position': 'after_header',
                'condition': r'(?:product|service|investment|suitable)'
            }
        ]

        # Third Party Banks (CASS 7.13)
        self.templates['third_party_banks'] = [
            {
                'template': '''APPROVED BANKS: Client money is held with FCA/PRA authorised banks selected under our due diligence criteria. Banks are subject to ongoing monitoring and review to ensure compliance with CASS 7 requirements.''',
                'position': 'end',
                'condition': r'(?:bank|client money|segregat)'
            }
        ]

        # Vulnerability Identification (Consumer Duty)
        self.templates['vulnerability_identification'] = [
            {
                'template': '''VULNERABLE CUSTOMERS: We recognize that customers may be in vulnerable circumstances. If you require additional support or reasonable adjustments, please contact us.''',
                'position': 'end',
                'condition': r'(?:customer|client|support|help)'
            }
        ]

        # Distribution Controls (Product Governance)
        self.templates['distribution_controls'] = [
            {
                'template': '''DISTRIBUTION: This product is distributed through [channels]. Our distribution strategy ensures it reaches the intended target market and is sold with appropriate advice/information.''',
                'position': 'end',
                'condition': r'(?:distribut|channel|platform|adviser)'
            }
        ]

        # Comprehension Aids (Consumer Duty)
        self.templates['comprehension_aids'] = [
            {
                'template': '''PLAIN LANGUAGE: This document uses clear, accessible language to ensure you can understand the information. [Key terms are explained / Glossary available / Summary provided].''',
                'position': 'after_header',
                'condition': r'(?:terms|glossary|definition|jargon)'
            }
        ]

        # Defined Roles (SMCR - Senior Managers & Certification Regime)
        self.templates['defined_roles'] = [
            {
                'template': '''REGULATORY RESPONSIBILITIES: This [function/service] is overseen by [Senior Manager/Certified Person name and title], who holds regulatory responsibility under the Senior Managers & Certification Regime.''',
                'position': 'end',
                'condition': r'(?:responsible|oversight|manager|director)'
            }
        ]

        # Finfluencer Controls
        self.regex_patterns['finfluencer'] = [
            {
                'pattern': r'#ad|#sponsored|paid partnership',
                'replacement': '[AD] This is a paid promotion - ',
                'reason': 'FCA finfluencer rules - Clear advertising disclosure',
                'flags': re.IGNORECASE
            }
        ]

        self.templates['finfluencer_controls'] = [
            {
                'template': '''ADVERTISEMENT: This is a financial promotion. It has been approved by [FCA authorised firm name, FRN: XXXXXX]. Not independent advice.''',
                'position': 'start',
                'condition': r'(?:#ad|#spon|influenc|social media|instagram|tiktok|youtube)'
            }
        ]

        # Outcomes Coverage (Consumer Duty Outcomes)
        self.templates['outcomes_coverage'] = [
            {
                'template': '''CONSUMER DUTY OUTCOMES: We monitor four key outcomes: (1) Products and services, (2) Price and value, (3) Consumer understanding, (4) Consumer support. We act to deliver good outcomes for customers.''',
                'position': 'end',
                'condition': r'(?:consumer duty|outcome|monitoring)'
            }
        ]

        # Personal Dealing (Market Abuse Prevention)
        self.templates['personal_dealing'] = [
            {
                'template': '''PERSONAL DEALING: Our staff are subject to personal account dealing rules. Employees must obtain approval before trading and are restricted from trading during closed periods.''',
                'position': 'end',
                'condition': r'(?:employee|staff|personal account|dealing)'
            }
        ]

        # Record Keeping (Regulatory Requirements)
        self.templates['record_keeping'] = [
            {
                'template': '''RECORD KEEPING: We maintain records of [transactions/advice/communications] for [specify period - typically 5-7 years] in accordance with FCA requirements.''',
                'position': 'end',
                'condition': r'(?:record|document|retain|archive)'
            }
        ]

        # Reasonable Adjustments (Equality Act 2010)
        self.templates['reasonable_adjustments'] = [
            {
                'template': '''REASONABLE ADJUSTMENTS: If you have a disability or require reasonable adjustments to access our services, please contact us. We are committed to making our services accessible.''',
                'position': 'end',
                'condition': r'(?:disabilit|access|adjustment|equality)'
            }
        ]

        # Structural rule: Move risk warnings to be more prominent
        self.structural_rules['risk_benefit_balance'] = [
            {
                'type': 'reorder_risk_warnings',
                'config': {}
            }
        ]

    # ===========================================
    # GDPR UK - Data Protection
    # ===========================================

    def _init_gdpr_uk_patterns(self):
        """GDPR UK compliance correction patterns"""

        # Consent corrections - remove forced consent
        self.regex_patterns['consent'] = [
            {
                'pattern': r'by\s+using\s+(?:this|our)\s+(?:website|service|app),?\s+you\s+(?:automatically\s+)?(?:agree|consent)(?:\s+to)?',
                'replacement': 'We request your explicit consent',
                'reason': 'GDPR Article 7 - Remove forced consent',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'continued\s+use.*constitutes.*(?:agreement|consent)',
                'replacement': 'You may provide your explicit consent by clicking "I agree"',
                'reason': 'GDPR Article 4(11) - Consent must be unambiguous affirmative action',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'by\s+(?:accessing|visiting)\s+(?:this|our)',
                'replacement': 'To use this service, we require your consent. You may provide consent by',
                'reason': 'GDPR - Remove implied consent from mere access',
                'flags': re.IGNORECASE
            }
        ]

        # Withdrawal of consent
        self.templates['withdrawal_consent'] = [
            {
                'template': 'WITHDRAWAL OF CONSENT: You may withdraw your consent at any time by contacting us at [contact details]. Withdrawal will not affect the lawfulness of processing based on consent before withdrawal.',
                'position': 'end',
                'condition': r'(?:consent|agree to)'
            }
        ]

        # Subject rights
        self.templates['rights'] = [
            {
                'template': '''YOUR RIGHTS: Under GDPR, you have the right to:
• Access your personal data
• Rectify inaccurate data
• Erase your data ("right to be forgotten")
• Restrict processing
• Data portability
• Object to processing
• Not be subject to automated decision-making

To exercise these rights, contact us at [contact details].''',
                'position': 'before_signature',
                'condition': r'(?:personal data|privacy|data protection)'
            }
        ]

        # Lawful basis
        self.templates['lawful_basis'] = [
            {
                'template': 'LAWFUL BASIS: We process your personal data based on [specify: consent / contract / legal obligation / vital interests / public task / legitimate interests].',
                'position': 'after_header',
                'condition': r'(?:process|collect|use).*(?:personal data|information)'
            }
        ]

        # Data retention
        self.templates['retention'] = [
            {
                'template': 'RETENTION: We will retain your personal data for [specify period] or as required by law. After this period, data will be securely deleted or anonymized.',
                'position': 'end',
                'condition': r'(?:personal data|information)'
            }
        ]

        # International transfers
        self.templates['international_transfer'] = [
            {
                'template': 'INTERNATIONAL TRANSFERS: We may transfer your data outside the UK/EEA. Where we do, we ensure appropriate safeguards are in place (adequacy decisions, standard contractual clauses, or binding corporate rules).',
                'position': 'end',
                'condition': r'(?:transfer|international|outside)'
            }
        ]

        # Cookies and tracking
        self.regex_patterns['cookies'] = [
            {
                'pattern': r'this\s+(?:site|website)\s+uses\s+cookies',
                'replacement': 'This website uses cookies. We require your consent for non-essential cookies',
                'reason': 'PECR - Explicit consent required for non-essential cookies',
                'flags': re.IGNORECASE
            }
        ]

        # Children's data
        self.templates['children'] = [
            {
                'template': 'CHILDREN: Our service is not directed at children under 13. We do not knowingly collect data from children without parental consent.',
                'position': 'end',
                'condition': r'(?:children|child|minor|age)'
            }
        ]

        # Accuracy of data
        self.templates['accuracy'] = [
            {
                'template': 'DATA ACCURACY: We take reasonable steps to ensure personal data is accurate and up to date. You can request corrections to inaccurate data at any time.',
                'position': 'end',
                'condition': r'(?:personal data|accuracy|correct|update)'
            }
        ]

        # Accountability
        self.templates['accountability'] = [
            {
                'template': 'ACCOUNTABILITY: We maintain records of our processing activities and can demonstrate GDPR compliance. Our Data Protection Officer can be contacted at [contact details].',
                'position': 'end',
                'condition': r'(?:gdpr|data protection|compliance)'
            }
        ]

        # Automated Decision Making
        self.templates['automated_decisions'] = [
            {
                'template': 'AUTOMATED DECISIONS: [We do not use automated decision-making including profiling / We use automated decision-making for [specify purpose]. You have the right to request human intervention and contest the decision].',
                'position': 'end',
                'condition': r'(?:automated|profiling|algorithm|decision)'
            }
        ]

        # Breach Notification
        self.templates['breach_notification'] = [
            {
                'template': 'DATA BREACHES: In the event of a personal data breach likely to result in high risk to your rights, we will notify you without undue delay as required by GDPR Article 34.',
                'position': 'end',
                'condition': r'(?:breach|security incident|notification)'
            }
        ]

        # Processors (third party data processors)
        self.templates['processors'] = [
            {
                'template': 'THIRD PARTY PROCESSORS: We engage third party processors to process personal data on our behalf. All processors are subject to GDPR-compliant contracts ensuring appropriate safeguards.',
                'position': 'end',
                'condition': r'(?:processor|third party|subprocessor|service provider)'
            }
        ]

        # Third party sharing
        self.templates['third_party_sharing'] = [
            {
                'template': 'DATA SHARING: We share your personal data with [specify categories of recipients]. We only share data where necessary and ensure recipients have appropriate safeguards in place.',
                'position': 'end',
                'condition': r'(?:share|sharing|third party|recipient)'
            }
        ]

    # ===========================================
    # Tax UK - HMRC Compliance
    # ===========================================

    def _init_tax_uk_patterns(self):
        """Tax UK compliance correction patterns"""

        # VAT threshold corrections
        self.regex_patterns['vat_threshold'] = [
            {
                'pattern': r'£85,?000',
                'replacement': '£90,000',
                'reason': 'Updated VAT threshold (April 2024)',
                'flags': 0
            },
            {
                'pattern': r'£83,?000',
                'replacement': '£90,000',
                'reason': 'Updated VAT threshold (April 2024)',
                'flags': 0
            },
            {
                'pattern': r'VAT\s+registration\s+threshold.*£\d+,?\d+',
                'replacement': 'VAT registration threshold is £90,000',
                'reason': 'Current VAT threshold as of April 2024',
                'flags': re.IGNORECASE
            }
        ]

        # CIS Compliance (Construction Industry Scheme)
        self.templates['cis_compliance'] = [
            {
                'template': 'CIS DEDUCTIONS: Contractors must verify subcontractors with HMRC and make appropriate deductions (20% for registered subcontractors, 30% for unregistered). Monthly returns required.',
                'position': 'end',
                'condition': r'(?:construction|subcontractor|cis|contractor)'
            }
        ]

        # Corporation Tax basics
        self.templates['corporation_tax'] = [
            {
                'template': 'CORPORATION TAX: UK companies must file Corporation Tax returns (CT600) within 12 months of accounting period end and pay tax within 9 months. Rate is [19%/25% depending on profits].',
                'position': 'end',
                'condition': r'(?:corporation tax|company tax|ct600)'
            }
        ]

        # Dividend Tax clarification
        self.templates['dividend_tax'] = [
            {
                'template': 'DIVIDEND TAX: Dividends are subject to Income Tax at 8.75% (basic rate), 33.75% (higher rate), or 39.35% (additional rate) after the £500 dividend allowance.',
                'position': 'end',
                'condition': r'(?:dividend|shareholder distribution)'
            }
        ]

        # Expense Rules
        self.templates['expense_rules'] = [
            {
                'template': 'ALLOWABLE EXPENSES: Business expenses must be wholly and exclusively for business purposes. Dual-purpose expenses require apportionment between business and private use.',
                'position': 'end',
                'condition': r'(?:expense|deduction|allowable|claim)'
            }
        ]

        # Flat Rate VAT Scheme
        self.templates['flat_rate_vat'] = [
            {
                'template': 'FLAT RATE VAT: Available to businesses with turnover under £150,000. You charge normal VAT but pay HMRC a fixed percentage based on your trade sector (ranges from 4% to 14.5%).',
                'position': 'end',
                'condition': r'(?:flat rate|frs|vat scheme)'
            }
        ]

        # Import VAT clarification
        self.templates['import_vat'] = [
            {
                'template': 'IMPORT VAT: VAT is charged on goods imported into the UK. Use postponed VAT accounting to declare and recover import VAT on the same VAT return (no upfront payment).',
                'position': 'end',
                'condition': r'(?:import|customs|duty|border)'
            }
        ]

        # Invoice Requirements
        self.templates['invoice_legal_requirements'] = [
            {
                'template': '''INVOICE REQUIREMENTS: UK invoices must include:
• Unique invoice number
• Business name and address
• Customer name and address
• Date of supply
• Description of goods/services
• Amounts excluding and including VAT
• VAT number (if VAT registered)
• Payment terms''',
                'position': 'end',
                'condition': r'(?:invoice|bill|statement)'
            }
        ]

        # Company Name Display
        self.regex_patterns['legal_entity_name'] = [
            {
                'pattern': r'\bLtd\b(?!\.|imited)',
                'replacement': 'Limited',
                'reason': 'Must display full "Limited" on business documents',
                'flags': 0
            },
            {
                'pattern': r'\bLLC\b',
                'replacement': 'Limited',
                'reason': 'UK uses "Limited" or "Ltd" not "LLC"',
                'flags': 0
            }
        ]

        # PAYE basics
        self.templates['paye_basics'] = [
            {
                'template': 'PAYE: Employers must operate PAYE if paying employees £123+ per week. Register with HMRC, deduct tax and National Insurance, submit RTI returns on or before each payday.',
                'position': 'end',
                'condition': r'(?:paye|payroll|employee|salary|wage)'
            }
        ]

        # Self-Assessment deadlines
        self.templates['self_assessment'] = [
            {
                'template': 'SELF-ASSESSMENT: Paper tax returns due 31 October, online returns due 31 January following the tax year (6 April to 5 April). Payment deadline is 31 January. Second payment on account due 31 July.',
                'position': 'end',
                'condition': r'(?:self assessment|self-assessment|tax return|sa100)'
            }
        ]

        # Making Tax Digital references
        self.templates['mtd'] = [
            {
                'template': 'MAKING TAX DIGITAL: VAT-registered businesses must use MTD-compatible software to keep digital records and submit VAT returns.',
                'position': 'end',
                'condition': r'(?:VAT|value added tax)'
            }
        ]

        # HMRC scam warnings
        self.regex_patterns['hmrc_scam'] = [
            {
                'pattern': r'(?:pay|payment).*(?:via|using|with).*(?:gift\s+card|itunes|amazon\s+voucher)',
                'replacement': '[REMOVED - SCAM INDICATOR: HMRC never requests payment via gift cards]',
                'reason': 'HMRC scam prevention - HMRC never accepts gift card payments',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:immediate|urgent).*(?:arrest|prosecution).*(?:tax|debt)',
                'replacement': '[REMOVED - SCAM INDICATOR: HMRC does not threaten immediate arrest]',
                'reason': 'HMRC scam prevention',
                'flags': re.IGNORECASE
            }
        ]

        self.templates['hmrc_scam_notice'] = [
            {
                'template': '⚠️ HMRC WARNING: HMRC will never request payment via gift cards, Bitcoin, or threaten immediate arrest. Always verify contact through gov.uk.',
                'position': 'start',
                'condition': r'(?:hmrc|tax|payment|refund)'
            }
        ]

        # IR35 corrections
        self.templates['ir35'] = [
            {
                'template': 'IR35 STATUS: [Specify whether IR35 applies to this engagement and reasoning]',
                'position': 'after_header',
                'condition': r'(?:contractor|freelance|self-employed|engagement)'
            }
        ]

    # ===========================================
    # NDA UK - Non-Disclosure Agreements
    # ===========================================

    def _init_nda_uk_patterns(self):
        """NDA UK compliance correction patterns"""

        # Whistleblowing protection
        self.templates['whistleblowing'] = [
            {
                'template': 'PROTECTED DISCLOSURES: Nothing in this Agreement prevents the disclosure of information protected under the Public Interest Disclosure Act 1998 (whistleblowing) or required by law.',
                'position': 'end',
                'condition': r'(?:disclose|confidential|nda|non-disclosure)'
            }
        ]

        # Crime reporting protection
        self.templates['crime_reporting'] = [
            {
                'template': 'RIGHT TO REPORT CRIME: Nothing in this Agreement prevents you from reporting suspected criminal activity to law enforcement or regulatory authorities.',
                'position': 'end',
                'condition': r'(?:nda|confidential|disclose)'
            }
        ]

        # Harassment protection (Equality Act 2010 Section 111)
        self.templates['harassment'] = [
            {
                'template': 'HARASSMENT AND DISCRIMINATION: Nothing in this Agreement prevents you from making a complaint of harassment, discrimination, or victimisation under the Equality Act 2010.',
                'position': 'end',
                'condition': r'(?:nda|confidential|settlement|agreement)'
            }
        ]

        # GDPR compliance in NDAs
        self.templates['nda_gdpr'] = [
            {
                'template': 'DATA PROTECTION: Both parties agree to comply with UK GDPR and Data Protection Act 2018 in relation to any personal data shared under this Agreement.',
                'position': 'end',
                'condition': r'(?:nda|confidential|personal data)'
            }
        ]

        # Duration reasonableness
        self.regex_patterns['duration'] = [
            {
                'pattern': r'(?:in\s+)?perpetuity',
                'replacement': 'for a period of [specify reasonable duration, typically 2-5 years for commercial information]',
                'reason': 'Unreasonable duration - must be proportionate',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'indefinitely',
                'replacement': 'for [specify period] years',
                'reason': 'Indefinite duration may be unenforceable',
                'flags': re.IGNORECASE
            }
        ]

        # Governing law
        self.templates['governing_law'] = [
            {
                'template': 'GOVERNING LAW: This Agreement is governed by the laws of England and Wales / Scotland / Northern Ireland.',
                'position': 'before_signature',
                'condition': r'(?:nda|agreement|contract)'
            }
        ]

        # Consideration clause
        self.templates['consideration'] = [
            {
                'template': 'CONSIDERATION: In consideration of £1 and other valuable consideration (the receipt and sufficiency of which is hereby acknowledged), the parties agree as follows:',
                'position': 'start',
                'condition': r'(?:nda|agreement|contract|confidential)'
            }
        ]

        # Definition Specificity
        self.templates['definition_specificity'] = [
            {
                'template': '''CONFIDENTIAL INFORMATION: "Confidential Information" means information in any form relating to [specify categories: trade secrets, financial data, customer lists, technical specifications, business plans, etc.] disclosed by one party to the other.

EXCLUSIONS: Confidential Information does NOT include information that:
(a) is or becomes publicly available through no breach of this Agreement;
(b) was lawfully known to the recipient prior to disclosure;
(c) is independently developed by the recipient without use of the Confidential Information;
(d) is lawfully obtained from a third party without breach of confidentiality; or
(e) must be disclosed by law or regulatory requirement.''',
                'position': 'after_header',
                'condition': r'(?:confidential|nda|non-disclosure)'
            }
        ]

        # Parties Identification
        self.templates['parties_identified'] = [
            {
                'template': '''PARTIES:

(1) [Full Legal Name] (company number: [XXXXXX]) whose registered office is at [Full Registered Address] ("Disclosing Party"); and

(2) [Full Legal Name] (company number: [XXXXXX]) whose registered office is at [Full Registered Address] ("Receiving Party").''',
                'position': 'start',
                'condition': r'(?:agreement|nda|contract)'
            }
        ]

        # Permitted Disclosures
        self.templates['permitted_disclosures'] = [
            {
                'template': '''PERMITTED DISCLOSURES: The Receiving Party may disclose Confidential Information to:
(a) employees, officers, and professional advisers who have a legitimate need to know;
(b) as required by law, regulation, or court order (with advance notice to Disclosing Party where legally permitted); and
(c) to the extent protected under the Public Interest Disclosure Act 1998 (whistleblowing).''',
                'position': 'end',
                'condition': r'(?:disclosure|disclose|nda)'
            }
        ]

        # Permitted Purpose
        self.templates['permitted_purpose'] = [
            {
                'template': 'PERMITTED PURPOSE: The Receiving Party shall use Confidential Information solely for [specify purpose: evaluating business opportunity / performing services under contract / etc.].',
                'position': 'after_header',
                'condition': r'(?:purpose|use of information|confidential)'
            }
        ]

        # Prior Knowledge Exclusion
        self.templates['prior_knowledge_exclusion'] = [
            {
                'template': 'PRIOR KNOWLEDGE: Information already known to the Receiving Party prior to disclosure (as evidenced by written records) is excluded from confidentiality obligations.',
                'position': 'end',
                'condition': r'(?:exclusion|confidential information|nda)'
            }
        ]

        # Public domain exclusion
        self.templates['public_domain'] = [
            {
                'template': 'PUBLIC DOMAIN EXCLUSION: Confidential Information does not include information that: (a) is or becomes publicly available through no breach of this Agreement; (b) was lawfully known prior to disclosure; (c) is independently developed; or (d) is lawfully obtained from a third party.',
                'position': 'after_header',
                'condition': r'(?:confidential information|nda)'
            }
        ]

        # Return/Destruction of Information
        self.templates['return_destruction'] = [
            {
                'template': 'RETURN OR DESTRUCTION: Upon termination or at the Disclosing Party\'s request, the Receiving Party shall return or destroy all Confidential Information and certify such destruction in writing.',
                'position': 'end',
                'condition': r'(?:termination|return|destroy|confidential)'
            }
        ]

    # ===========================================
    # HR Scottish - Employment Law (Scotland)
    # ===========================================

    def _init_hr_scottish_patterns(self):
        """HR Scottish employment law correction patterns"""

        # Accompaniment rights (Employment Relations Act 1999, Section 10)
        self.templates['accompaniment'] = [
            {
                'template': 'RIGHT TO BE ACCOMPANIED: You have the statutory right to be accompanied at this meeting by a work colleague or trade union representative. Please inform us in advance if you wish to be accompanied and provide the name of your companion.',
                'position': 'after_header',
                'condition': r'(?:disciplinary|grievance|hearing|meeting)'
            }
        ]

        # Remove unlawful restrictions on accompaniment
        self.regex_patterns['accompaniment_restrictions'] = [
            {
                'pattern': r'(?:you\s+)?(?:may\s+not|cannot|must\s+not).*(?:bring|accompanied\s+by).*(?:solicitor|lawyer)',
                'replacement': 'You have the right to be accompanied by a work colleague or trade union representative',
                'reason': 'ERA 1999 s10 - Statutory right to accompaniment',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:no|cannot\s+have).*legal\s+representation',
                'replacement': 'You have the right to be accompanied by a work colleague or trade union representative',
                'reason': 'Cannot restrict statutory accompaniment right',
                'flags': re.IGNORECASE
            }
        ]

        # Notice period
        self.templates['notice'] = [
            {
                'template': 'NOTICE: You are required to attend a [disciplinary/grievance] meeting on [date] at [time] at [location]. You have the right to be accompanied by a colleague or trade union representative.',
                'position': 'start',
                'condition': r'(?:disciplinary|grievance|meeting)'
            }
        ]

        # Right to be heard
        self.templates['right_to_be_heard'] = [
            {
                'template': 'RIGHT TO RESPOND: You will have the opportunity to state your case, present evidence, and call witnesses before any decision is made.',
                'position': 'after_header',
                'condition': r'(?:disciplinary|allegation|misconduct)'
            }
        ]

        # Appeal rights
        self.templates['appeal'] = [
            {
                'template': 'APPEAL RIGHTS: If you are dissatisfied with the outcome, you have the right to appeal. You must submit your appeal in writing within [5-10] working days to [name/position].',
                'position': 'before_signature',
                'condition': r'(?:disciplinary|grievance|outcome|decision)'
            }
        ]

        # Evidence and disclosure
        self.templates['evidence'] = [
            {
                'template': 'EVIDENCE: You will be provided with copies of all evidence to be relied upon at the meeting at least [48 hours / 2 working days] in advance.',
                'position': 'after_header',
                'condition': r'(?:evidence|investigation|disciplinary)'
            }
        ]

        # Impartial decision maker
        self.templates['impartial_chair'] = [
            {
                'template': 'IMPARTIALITY: The meeting will be chaired by an impartial manager who has not been involved in the investigation.',
                'position': 'after_header',
                'condition': r'(?:disciplinary|grievance|meeting|hearing)'
            }
        ]

        # Suspension clarification
        self.regex_patterns['suspension'] = [
            {
                'pattern': r'suspended.*(?:pending|during).*investigation',
                'replacement': 'suspended on full pay (not a disciplinary sanction) pending investigation',
                'reason': 'Clarify suspension is neutral act, not punishment',
                'flags': re.IGNORECASE
            }
        ]

        # Allegations clarity
        self.templates['allegations'] = [
            {
                'template': 'ALLEGATIONS: You are invited to a [disciplinary/grievance] meeting to discuss the following allegations: [specify clear, specific allegations]. You will have the opportunity to respond to these allegations at the meeting.',
                'position': 'start',
                'condition': r'(?:disciplinary|allegation|misconduct|grievance)'
            }
        ]

        # Consistency in decisions
        self.templates['consistency'] = [
            {
                'template': 'CONSISTENCY: We apply our disciplinary procedures consistently across all employees. Similar cases are treated similarly, taking into account individual circumstances and mitigating factors.',
                'position': 'end',
                'condition': r'(?:disciplinary|sanction|decision)'
            }
        ]

        # Disclosure of evidence
        self.templates['disclosure'] = [
            {
                'template': 'EVIDENCE DISCLOSURE: You will receive copies of all evidence to be relied upon at least [48 hours / 2 working days] before the meeting.',
                'position': 'after_header',
                'condition': r'(?:evidence|investigation|disciplinary|meeting)'
            }
        ]

        # Informal resolution
        self.regex_patterns['informal_threats'] = [
            {
                'pattern': r'(?:this is your|informal|final)\s+(?:last\s+)?(?:warning|chance)',
                'replacement': 'we would like to discuss this matter with you',
                'reason': 'Informal warnings must not threaten formal consequences',
                'flags': re.IGNORECASE
            }
        ]

        # Investigation process
        self.templates['investigation'] = [
            {
                'template': 'INVESTIGATION: An investigation will be conducted by [name/position]. You may be asked to attend an investigatory meeting. This is fact-finding and not disciplinary. You do not have the right to be accompanied at investigatory meetings, though we may allow it in complex cases.',
                'position': 'after_header',
                'condition': r'(?:investigation|investigat|allegation)'
            }
        ]

        # Meeting notes
        self.templates['meeting_notes'] = [
            {
                'template': 'MEETING NOTES: We will take notes of the meeting. You will receive a copy and may submit corrections or comments within [5] working days.',
                'position': 'end',
                'condition': r'(?:meeting|hearing|disciplinary|grievance)'
            }
        ]

        # Meeting postponement
        self.templates['postponement'] = [
            {
                'template': 'POSTPONEMENT: If you cannot attend, contact us immediately. We may postpone once if you provide good reason. Your companion must be available within 5 working days of the original date.',
                'position': 'end',
                'condition': r'(?:meeting|hearing|attend)'
            }
        ]

        # Mitigating circumstances
        self.templates['mitigating_circumstances'] = [
            {
                'template': 'MITIGATING CIRCUMSTANCES: You may present any mitigating circumstances that should be taken into account when determining the outcome (e.g., length of service, previous record, personal circumstances).',
                'position': 'end',
                'condition': r'(?:disciplinary|sanction|outcome|decision)'
            }
        ]

        # Outcome reasons
        self.templates['outcome_reasons'] = [
            {
                'template': 'OUTCOME: Our decision is [specify outcome]. The reasons for this decision are: [specify reasons]. This decision was reached after considering all evidence and your response.',
                'position': 'after_header',
                'condition': r'(?:outcome|decision|finding)'
            }
        ]

        # Previous warnings
        self.templates['previous_warnings'] = [
            {
                'template': 'PREVIOUS RECORD: Your previous disciplinary record [has been considered / shows no previous warnings]. [Expired warnings have been disregarded].',
                'position': 'end',
                'condition': r'(?:previous|record|warning|history)'
            }
        ]

        # Representation choice
        self.templates['representation_choice'] = [
            {
                'template': 'YOUR CHOICE OF COMPANION: You may be accompanied by a work colleague or trade union representative of your choice. Your companion may address the hearing, confer with you, and ask questions, but may not answer questions on your behalf.',
                'position': 'after_header',
                'condition': r'(?:companion|accompanied|representative)'
            }
        ]

        # Sanction graduation
        self.templates['sanction_graduation'] = [
            {
                'template': 'DISCIPLINARY SANCTIONS: Sanctions are normally applied progressively: (1) Verbal warning, (2) First written warning, (3) Final written warning, (4) Dismissal. Gross misconduct may result in summary dismissal without prior warnings.',
                'position': 'end',
                'condition': r'(?:sanction|warning|dismissal|progressive)'
            }
        ]

        # Timeframes
        self.templates['timeframes'] = [
            {
                'template': 'TIMEFRAMES: Meetings will be held within [specify reasonable timeframe]. Decisions will be communicated within [specify period]. Appeal outcomes will be provided within [specify period].',
                'position': 'end',
                'condition': r'(?:timeline|timeframe|deadline|period)'
            }
        ]

        # Witness statements
        self.templates['witness_statements'] = [
            {
                'template': 'WITNESSES: You may call relevant witnesses. Provide names in advance. Witnesses will only attend for their evidence. We will also call our witnesses.',
                'position': 'end',
                'condition': r'(?:witness|evidence|testimony)'
            }
        ]

        # Dismissal procedures
        self.templates['dismissal'] = [
            {
                'template': 'DISMISSAL: Dismissal will only occur after a fair procedure including investigation, meeting with right to be accompanied, consideration of your response, and right of appeal. Gross misconduct may result in summary dismissal (without notice).',
                'position': 'end',
                'condition': r'(?:dismiss|termination|gross misconduct|summary)'
            }
        ]

        # Confidentiality
        self.templates['confidentiality'] = [
            {
                'template': 'CONFIDENTIALITY: All parties are expected to maintain confidentiality. However, you may discuss this matter with your representative, trade union, or as required by law.',
                'position': 'end',
                'condition': r'(?:disciplinary|grievance|investigation)'
            }
        ]

    # ===========================================
    # EXPANDED PATTERNS - Additional 100+ patterns
    # ===========================================

    def _expand_fca_uk_patterns(self):
        """Additional FCA UK patterns for comprehensive coverage"""

        # Market abuse prevention
        self.templates['market_abuse'] = [
            {
                'template': 'MARKET ABUSE: We have policies to prevent market abuse including insider dealing and market manipulation. All staff must comply with these policies.',
                'position': 'end',
                'condition': r'(?:market|trading|inside information|price sensitive)'
            }
        ]

        # Treating Customers Fairly (TCF)
        self.templates['tcf'] = [
            {
                'template': 'TREATING CUSTOMERS FAIRLY: We are committed to treating customers fairly at all stages: (1) Product design, (2) Promotion, (3) Advice, (4) Point of sale, (5) After sale, (6) Handling complaints.',
                'position': 'end',
                'condition': r'(?:customer|client|fair treatment)'
            }
        ]

        # Best execution
        self.templates['best_execution'] = [
            {
                'template': 'BEST EXECUTION: We will take all sufficient steps to obtain the best possible result for you when executing orders, taking into account price, costs, speed, likelihood of execution and settlement.',
                'position': 'end',
                'condition': r'(?:execution|order|trading)'
            }
        ]

        # Product disclosure
        self.regex_patterns['product_disclosure'] = [
            {
                'pattern': r'fees\s+may\s+apply',
                'replacement': 'The following fees apply: [specify all fees and charges]',
                'reason': 'FCA requires clear fee disclosure',
                'flags': re.IGNORECASE
            }
        ]

        # Performance data
        self.regex_patterns['performance_data'] = [
            {
                'pattern': r'(?:average|typical)\s+returns?',
                'replacement': 'Past performance data (not indicative of future results)',
                'reason': 'Performance data must include risk warnings',
                'flags': re.IGNORECASE
            }
        ]

        # Cooling off period
        self.templates['cooling_off'] = [
            {
                'template': 'CANCELLATION RIGHTS: You have 14 days to cancel this contract from the date of agreement. To cancel, contact us in writing.',
                'position': 'after_header',
                'condition': r'(?:contract|agreement|purchase)'
            }
        ]

        # Suitability assessment
        self.templates['suitability'] = [
            {
                'template': 'SUITABILITY: Before providing personal recommendations, we assess your knowledge, experience, financial situation, and investment objectives to ensure suitability.',
                'position': 'after_header',
                'condition': r'(?:recommendation|advice|suitable)'
            }
        ]

        # Appropriateness assessment
        self.templates['appropriateness'] = [
            {
                'template': 'APPROPRIATENESS: We assess whether you have the necessary knowledge and experience to understand the risks of this product/service.',
                'position': 'after_header',
                'condition': r'(?:execution only|non-advised)'
            }
        ]

        # Key information documents
        self.templates['kid'] = [
            {
                'template': 'KEY INFORMATION DOCUMENT: You will receive a Key Information Document (KID) which summarises key features, risks, and costs of this product.',
                'position': 'after_header',
                'condition': r'(?:packaged retail|investment product|priips)'
            }
        ]

        # Professional client classification
        self.templates['client_classification'] = [
            {
                'template': 'CLIENT CLASSIFICATION: You are classified as a [Retail/Professional/Eligible Counterparty] client. This affects the level of regulatory protection you receive.',
                'position': 'after_header',
                'condition': r'(?:client|customer|classification)'
            }
        ]

        # Additional regex patterns for FCA compliance
        self.regex_patterns['unclear_risk_warnings'] = [
            {'pattern': r'minimal risk', 'replacement': 'lower risk (capital at risk)', 'reason': 'No investment is minimal risk', 'flags': re.IGNORECASE},
            {'pattern': r'safe bet', 'replacement': 'potential opportunity (capital at risk)', 'reason': 'No investment is a safe bet', 'flags': re.IGNORECASE},
            {'pattern': r'cant lose', 'replacement': 'potential for returns (may incur losses)', 'reason': 'All investments can lose', 'flags': re.IGNORECASE},
            {'pattern': r'zero risk', 'replacement': 'lower risk (capital at risk)', 'reason': 'No investment has zero risk', 'flags': re.IGNORECASE},
            {'pattern': r'no downside', 'replacement': 'potential for loss', 'reason': 'All investments have downside risk', 'flags': re.IGNORECASE},
            {'pattern': r'sure thing', 'replacement': 'investment opportunity (not guaranteed)', 'reason': 'No investment is guaranteed', 'flags': re.IGNORECASE},
            {'pattern': r'easy money', 'replacement': 'investment opportunity (capital at risk)', 'reason': 'Avoid misleading simplification', 'flags': re.IGNORECASE},
            {'pattern': r'passive income guaranteed', 'replacement': 'potential income stream (not guaranteed)', 'reason': 'Income not guaranteed', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['misleading_performance'] = [
            {'pattern': r'always profitable', 'replacement': 'historically profitable (past performance not indicative)', 'reason': 'Cannot guarantee profitability', 'flags': re.IGNORECASE},
            {'pattern': r'never lost money', 'replacement': 'positive historical performance (not guaranteed)', 'reason': 'Past performance disclaimers required', 'flags': re.IGNORECASE},
            {'pattern': r'outperforms? the market', 'replacement': 'historical performance data (not guaranteed to continue)', 'reason': 'Market outperformance not guaranteed', 'flags': re.IGNORECASE},
            {'pattern': r'consistent returns', 'replacement': 'historical returns (past performance not indicative)', 'reason': 'Consistency not guaranteed', 'flags': re.IGNORECASE},
            {'pattern': r'proven track record', 'replacement': 'track record (past performance not indicative of future results)', 'reason': 'Past performance disclaimers required', 'flags': re.IGNORECASE},
            {'pattern': r'beats inflation', 'replacement': 'historical performance vs inflation (not guaranteed)', 'reason': 'Future performance not guaranteed', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['urgency_tactics'] = [
            {'pattern': r'act now or miss out', 'replacement': 'opportunity available', 'reason': 'Avoid pressure tactics', 'flags': re.IGNORECASE},
            {'pattern': r'limited (?:time|availability|spots?)', 'replacement': 'available', 'reason': 'Avoid false scarcity', 'flags': re.IGNORECASE},
            {'pattern': r'offer expires soon', 'replacement': 'offer available', 'reason': 'Avoid undue pressure', 'flags': re.IGNORECASE},
            {'pattern': r'while stocks last', 'replacement': 'available', 'reason': 'Avoid false urgency', 'flags': re.IGNORECASE},
            {'pattern': r'today only', 'replacement': 'available', 'reason': 'Avoid artificial time pressure', 'flags': re.IGNORECASE},
            {'pattern': r'dont delay', 'replacement': 'consider this opportunity', 'reason': 'Avoid pressure language', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['misleading_language'] = [
            {'pattern': r'foolproof investment', 'replacement': 'investment opportunity (capital at risk)', 'reason': 'No investment is foolproof', 'flags': re.IGNORECASE},
            {'pattern': r'get rich quick', 'replacement': 'investment opportunity', 'reason': 'Avoid unrealistic expectations', 'flags': re.IGNORECASE},
            {'pattern': r'no-brainer', 'replacement': 'opportunity to consider', 'reason': 'Avoid dismissive language', 'flags': re.IGNORECASE},
            {'pattern': r'cant go wrong', 'replacement': 'investment opportunity (capital at risk)', 'reason': 'All investments carry risk', 'flags': re.IGNORECASE},
            {'pattern': r'guaranteed success', 'replacement': 'potential opportunity (not guaranteed)', 'reason': 'Success cannot be guaranteed', 'flags': re.IGNORECASE},
        ]

    def _expand_gdpr_uk_patterns(self):
        """Additional GDPR UK patterns"""

        # Data minimization
        self.templates['data_minimization'] = [
            {
                'template': 'DATA MINIMIZATION: We only collect personal data that is necessary for the specified purpose. We do not collect excessive data.',
                'position': 'end',
                'condition': r'(?:collect|personal data|information)'
            }
        ]

        # Storage limitation
        self.templates['storage_limitation'] = [
            {
                'template': 'STORAGE: Personal data is kept only as long as necessary for the purpose collected, or as required by law. Data is then securely deleted or anonymized.',
                'position': 'end',
                'condition': r'(?:storage|retention|delete)'
            }
        ]

        # Security measures
        self.templates['security_measures'] = [
            {
                'template': 'SECURITY: We implement appropriate technical and organizational measures to protect personal data against unauthorized access, loss, or destruction.',
                'position': 'end',
                'condition': r'(?:security|protection|safeguard)'
            }
        ]

        # Data subject access requests
        self.templates['dsar'] = [
            {
                'template': 'DATA ACCESS: You can request a copy of your personal data by submitting a Data Subject Access Request (DSAR). We will respond within one month.',
                'position': 'end',
                'condition': r'(?:access|copy of data|personal information)'
            }
        ]

        # Legitimate interests assessment
        self.templates['legitimate_interests'] = [
            {
                'template': 'LEGITIMATE INTERESTS: Where we process data based on legitimate interests, we have conducted a balancing test and determined our interests do not override your rights.',
                'position': 'end',
                'condition': r'(?:legitimate interest|lawful basis)'
            }
        ]

        # Special category data
        self.templates['special_category'] = [
            {
                'template': 'SENSITIVE DATA: We process special category data (health, ethnicity, religion, etc.) only with your explicit consent or where legally permitted.',
                'position': 'after_header',
                'condition': r'(?:sensitive|special category|health data)'
            }
        ]

        # Additional GDPR regex patterns
        self.regex_patterns['gdpr_consent_issues'] = [
            {'pattern': r'we may share your data', 'replacement': 'We will only share your data with your explicit consent or legal basis', 'reason': 'Consent required for data sharing', 'flags': re.IGNORECASE},
            {'pattern': r'we reserve the right to', 'replacement': 'We may (with your consent or legal basis)', 'reason': 'Cannot reserve unilateral rights over personal data', 'flags': re.IGNORECASE},
            {'pattern': r'by ticking this box', 'replacement': 'You may provide explicit consent by ticking this box', 'reason': 'Clarify consent is optional', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['gdpr_clarity'] = [
            {'pattern': r'we use cookies', 'replacement': 'We use cookies. Essential cookies are necessary; others require consent', 'reason': 'PECR compliance', 'flags': re.IGNORECASE},
            {'pattern': r'see our privacy policy', 'replacement': 'See our privacy policy at [URL] for details on data processing', 'reason': 'Provide accessible link', 'flags': re.IGNORECASE},
            {'pattern': r'third parties', 'replacement': 'named third parties (see list)', 'reason': 'Be specific about third parties', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['data_retention_vague'] = [
            {'pattern': r'as long as necessary', 'replacement': 'for [specify period] or as required by law', 'reason': 'Specific retention periods required', 'flags': re.IGNORECASE},
            {'pattern': r'indefinitely', 'replacement': 'for [specify period]', 'reason': 'Indefinite retention not permitted', 'flags': re.IGNORECASE},
        ]

    def _expand_tax_uk_patterns(self):
        """Additional Tax UK patterns"""

        # Annual accounting scheme
        self.templates['annual_accounting'] = [
            {
                'template': 'ANNUAL ACCOUNTING SCHEME: Available if turnover under £1.35m. Submit one VAT return per year but make payments on account.',
                'position': 'end',
                'condition': r'(?:vat|annual accounting)'
            }
        ]

        # Cash accounting scheme
        self.templates['cash_accounting'] = [
            {
                'template': 'CASH ACCOUNTING: Available if turnover under £1.35m. Account for VAT on cash basis (when paid/received) rather than invoice basis.',
                'position': 'end',
                'condition': r'(?:vat|cash accounting)'
            }
        ]

        # Research & Development tax relief
        self.templates['r_and_d_relief'] = [
            {
                'template': 'R&D TAX RELIEF: Companies undertaking qualifying R&D can claim enhanced deductions or tax credits. SME scheme: 186% deduction. RDEC scheme: 13% credit.',
                'position': 'end',
                'condition': r'(?:r&d|research|development|innovation)'
            }
        ]

        # Capital allowances
        self.templates['capital_allowances'] = [
            {
                'template': 'CAPITAL ALLOWANCES: Claim tax relief on capital expenditure. Annual Investment Allowance: 100% relief on first £1m. Writing down allowances available thereafter.',
                'position': 'end',
                'condition': r'(?:capital|equipment|machinery|allowance)'
            }
        ]

        # Employment status
        self.templates['employment_status'] = [
            {
                'template': 'EMPLOYMENT STATUS: Status determines tax treatment. HMRC considers control, substitution, mutuality of obligation. Use HMRC Check Employment Status for Tax tool (CEST).',
                'position': 'end',
                'condition': r'(?:employment status|contractor|employee)'
            }
        ]

        # Business expenses
        self.templates['business_expenses'] = [
            {
                'template': 'BUSINESS EXPENSES: Expenses must be wholly and exclusively for business purposes. Common allowable: office costs, travel, professional fees, stock, staff costs.',
                'position': 'end',
                'condition': r'(?:expense|deductible|allowable)'
            }
        ]

        # VAT partial exemption
        self.templates['partial_exemption'] = [
            {
                'template': 'PARTIAL EXEMPTION: If you make both taxable and exempt supplies, you can only reclaim VAT on purchases relating to taxable supplies.',
                'position': 'end',
                'condition': r'(?:vat|exempt|partial exemption)'
            }
        ]

        # Transfer pricing
        self.templates['transfer_pricing'] = [
            {
                'template': 'TRANSFER PRICING: Transactions between related parties must be at arm\'s length. Documentation required if transactions exceed £10m.',
                'position': 'end',
                'condition': r'(?:related party|transfer|arm\'s length)'
            }
        ]

        # Additional Tax regex patterns
        self.regex_patterns['tax_terminology'] = [
            {'pattern': r'tax evasion', 'replacement': 'tax avoidance (legal tax planning) [Note: Tax evasion is illegal]', 'reason': 'Clarify legal vs illegal', 'flags': re.IGNORECASE},
            {'pattern': r'VAT exempt', 'replacement': 'VAT zero-rated or VAT exempt (specify which)', 'reason': 'Distinguish zero-rated from exempt', 'flags': re.IGNORECASE},
            {'pattern': r'off the books', 'replacement': '[REMOVED - implies tax evasion]', 'reason': 'Off-the-books transactions are illegal', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['tax_dates'] = [
            {'pattern': r'end of (?:the )?tax year', 'replacement': '5 April (tax year end)', 'reason': 'Specify exact date', 'flags': re.IGNORECASE},
            {'pattern': r'tax deadline', 'replacement': 'tax return deadline: 31 October (paper) or 31 January (online)', 'reason': 'Specify deadlines', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['vat_registration'] = [
            {'pattern': r'register for VAT', 'replacement': 'register for VAT if turnover exceeds £90,000', 'reason': 'Include threshold', 'flags': re.IGNORECASE},
            {'pattern': r'VAT return', 'replacement': 'VAT return (quarterly unless on annual accounting scheme)', 'reason': 'Specify frequency', 'flags': re.IGNORECASE},
        ]

    def _expand_nda_uk_patterns(self):
        """Additional NDA UK patterns"""

        # Standard of care
        self.templates['standard_of_care'] = [
            {
                'template': 'STANDARD OF CARE: The Receiving Party shall use the same degree of care to protect Confidential Information as it uses for its own confidential information, but no less than reasonable care.',
                'position': 'end',
                'condition': r'(?:care|protect|confidential)'
            }
        ]

        # No license granted
        self.templates['no_license'] = [
            {
                'template': 'NO LICENSE: Nothing in this Agreement grants any license, right, or interest in intellectual property, except the limited right to use information for the Permitted Purpose.',
                'position': 'end',
                'condition': r'(?:intellectual property|patent|trademark|copyright)'
            }
        ]

        # Residual information
        self.templates['residual_info'] = [
            {
                'template': 'RESIDUAL INFORMATION: The Receiving Party may retain and use residual information retained in the unaided memories of its personnel, provided this clause does not permit deliberate memorization to avoid obligations.',
                'position': 'end',
                'condition': r'(?:memory|residual|retain)'
            }
        ]

        # No obligation to proceed
        self.templates['no_obligation'] = [
            {
                'template': 'NO OBLIGATION: This Agreement does not create any obligation to enter into further agreements, make disclosures, or proceed with any transaction.',
                'position': 'end',
                'condition': r'(?:obligation|commitment|proceed)'
            }
        ]

        # Injunctive relief
        self.templates['injunctive_relief'] = [
            {
                'template': 'INJUNCTIVE RELIEF: The parties acknowledge that breach may cause irreparable harm for which monetary damages are inadequate. The Disclosing Party may seek injunctive relief in addition to other remedies.',
                'position': 'end',
                'condition': r'(?:breach|remedy|damages)'
            }
        ]

        # Survival
        self.templates['survival'] = [
            {
                'template': 'SURVIVAL: Confidentiality obligations survive termination of this Agreement for [specify period, typically 2-5 years] or until Confidential Information enters the public domain.',
                'position': 'end',
                'condition': r'(?:termination|survival|duration)'
            }
        ]

        # Additional NDA regex patterns
        self.regex_patterns['nda_overbroad'] = [
            {'pattern': r'all information', 'replacement': 'Confidential Information as defined herein', 'reason': 'Be specific about what is confidential', 'flags': re.IGNORECASE},
            {'pattern': r'any and all', 'replacement': 'Confidential', 'reason': 'Avoid overbroad language', 'flags': re.IGNORECASE},
            {'pattern': r'forever', 'replacement': 'for [specify period]', 'reason': 'Perpetual obligations may be unenforceable', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['nda_illegal_restrictions'] = [
            {'pattern': r'prevent.*disclosure.*crime', 'replacement': '[REMOVED - Cannot prevent disclosure of crimes]', 'reason': 'Cannot restrict crime reporting', 'flags': re.IGNORECASE},
            {'pattern': r'prohibit.*whistleblow', 'replacement': '[REMOVED - Whistleblowing protected by law]', 'reason': 'PIDA 1998 protection', 'flags': re.IGNORECASE},
            {'pattern': r'cannot.*report.*authorities', 'replacement': '[REMOVED - Right to report to authorities protected]', 'reason': 'Legal reporting protected', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['nda_unilateral'] = [
            {'pattern': r'sole discretion', 'replacement': 'reasonable discretion', 'reason': 'Sole discretion may be unfair', 'flags': re.IGNORECASE},
            {'pattern': r'at our option', 'replacement': 'by mutual agreement', 'reason': 'Unilateral options may be unenforceable', 'flags': re.IGNORECASE},
        ]

    def _expand_hr_scottish_patterns(self):
        """Additional HR Scottish patterns"""

        # TUPE transfers
        self.templates['tupe'] = [
            {
                'template': 'TUPE: Transfer of Undertakings (Protection of Employment) Regulations apply. Your employment transfers automatically on same terms. Consultation required for any changes.',
                'position': 'after_header',
                'condition': r'(?:transfer|tupe|undertaking)'
            }
        ]

        # Redundancy consultation
        self.templates['redundancy_consultation'] = [
            {
                'template': 'REDUNDANCY CONSULTATION: We will consult on selection criteria, alternatives to redundancy, and mitigation measures. Collective consultation required for 20+ redundancies.',
                'position': 'after_header',
                'condition': r'(?:redundancy|redundancies|reduction)'
            }
        ]

        # Statutory sick pay
        self.templates['ssp'] = [
            {
                'template': 'STATUTORY SICK PAY: Eligible employees receive SSP (£109.40/week) from day 4 of sickness for up to 28 weeks. Qualifying days: normally working days.',
                'position': 'end',
                'condition': r'(?:sick|sickness|absence|ill)'
            }
        ]

        # Maternity/paternity rights
        self.templates['parental_rights'] = [
            {
                'template': 'PARENTAL RIGHTS: Statutory maternity leave: 52 weeks. Statutory maternity pay: 90% salary for 6 weeks then £172.48 for 33 weeks. Protection from detriment and dismissal.',
                'position': 'end',
                'condition': r'(?:maternity|paternity|parental|pregnancy)'
            }
        ]

        # Protected characteristics
        self.templates['protected_characteristics'] = [
            {
                'template': 'EQUALITY: Under the Equality Act 2010, discrimination is prohibited based on: age, disability, gender reassignment, marriage/civil partnership, pregnancy/maternity, race, religion/belief, sex, sexual orientation.',
                'position': 'end',
                'condition': r'(?:discrimination|equality|protected)'
            }
        ]

        # Working time regulations
        self.templates['working_time'] = [
            {
                'template': 'WORKING TIME: Maximum 48-hour average working week (can opt out). Rest breaks: 20 minutes if working 6+ hours. Daily rest: 11 hours. Weekly rest: 24 hours per week.',
                'position': 'end',
                'condition': r'(?:working time|hours|rest break)'
            }
        ]

        # Additional HR regex patterns
        self.regex_patterns['hr_terminology'] = [
            {'pattern': r'fire(?:d)?', 'replacement': 'dismiss', 'reason': 'Use formal terminology', 'flags': re.IGNORECASE},
            {'pattern': r'let go', 'replacement': 'dismiss or make redundant', 'reason': 'Use precise legal terminology', 'flags': re.IGNORECASE},
            {'pattern': r'sack(?:ed)?', 'replacement': 'dismiss', 'reason': 'Use formal terminology', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['hr_unlawful_discrimination'] = [
            {'pattern': r'young and dynamic', 'replacement': 'energetic and motivated', 'reason': 'Age discrimination', 'flags': re.IGNORECASE},
            {'pattern': r'native English speaker', 'replacement': 'fluent English speaker', 'reason': 'Race discrimination', 'flags': re.IGNORECASE},
            {'pattern': r'recent graduate', 'replacement': 'graduate', 'reason': 'Age discrimination', 'flags': re.IGNORECASE},
        ]

        self.regex_patterns['hr_procedural'] = [
            {'pattern': r'immediately dismissed', 'replacement': 'dismissed following fair procedure', 'reason': 'Fair procedure required', 'flags': re.IGNORECASE},
            {'pattern': r'without warning', 'replacement': 'after appropriate warnings (except gross misconduct)', 'reason': 'Progressive discipline required', 'flags': re.IGNORECASE},
            {'pattern': r'no appeal', 'replacement': 'with right of appeal', 'reason': 'Appeal rights required', 'flags': re.IGNORECASE},
        ]

    # ===========================================
    # Getter Methods
    # ===========================================

    def get_regex_patterns(self, gate_pattern: str = None) -> Dict:
        """Get regex patterns, optionally filtered by gate pattern"""
        if gate_pattern:
            return {k: v for k, v in self.regex_patterns.items() if gate_pattern.lower() in k.lower()}
        return self.regex_patterns

    def get_templates(self, gate_pattern: str = None) -> Dict:
        """Get templates, optionally filtered by gate pattern"""
        if gate_pattern:
            return {k: v for k, v in self.templates.items() if gate_pattern.lower() in k.lower()}
        return self.templates

    def get_structural_rules(self, gate_pattern: str = None) -> Dict:
        """Get structural rules, optionally filtered by gate pattern"""
        if gate_pattern:
            return {k: v for k, v in self.structural_rules.items() if gate_pattern.lower() in k.lower()}
        return self.structural_rules

    def get_all_patterns(self) -> Dict:
        """Get all patterns organized by type"""
        return {
            'regex': self.regex_patterns,
            'templates': self.templates,
            'structural': self.structural_rules
        }
