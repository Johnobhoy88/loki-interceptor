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
                'pattern': r'by\s+using\s+(?:this|our)\s+(?:website|service|app),?\s+you\s+(?:automatically\s+)?(?:agree|consent)\s+to',
                'replacement': 'We request your explicit consent to',
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

        # Public domain exclusion
        self.templates['public_domain'] = [
            {
                'template': 'EXCLUSIONS: Confidential Information does not include information that: (a) is or becomes publicly available through no breach of this Agreement; (b) was lawfully known prior to disclosure; (c) is independently developed; or (d) is lawfully obtained from a third party.',
                'position': 'after_header',
                'condition': r'(?:confidential information|nda)'
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

        # Confidentiality
        self.templates['confidentiality'] = [
            {
                'template': 'CONFIDENTIALITY: All parties are expected to maintain confidentiality. However, you may discuss this matter with your representative, trade union, or as required by law.',
                'position': 'end',
                'condition': r'(?:disciplinary|grievance|investigation)'
            }
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
