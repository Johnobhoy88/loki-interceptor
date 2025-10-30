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
        """FCA UK compliance correction patterns - GOLD STANDARD"""

        # Risk/Benefit Balance corrections - ENHANCED
        self.regex_patterns['risk_benefit'] = [
            {
                'pattern': r'(?:high|significant|attractive|strong|superior|excellent|award-winning)\s+(?:return|yield|performance|results?|growth)',
                'replacement': r'potential returns (capital at risk - value may fall)',
                'reason': 'FCA COBS 4.2.3 - Balance benefits with risk warnings',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:average|typical|consistent)\s+(?:return|yield)s?\s+of\s+(\d+)%',
                'replacement': r'past returns of \1% (not guaranteed - capital at risk)',
                'reason': 'FCA COBS 4.2.1 - Past performance not indicator of future results',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:targets?|aims? for|seeks?)\s+(?:high|significant)\s+(?:growth|returns?)',
                'replacement': r'targets growth (no guarantee - higher risk investments)',
                'reason': 'FCA COBS 4.2.3 - Balance growth targets with risk',
                'flags': re.IGNORECASE
            }
        ]

        self.templates['risk_benefit'] = [
            {
                'template': '''⚠️ RISK WARNING: The value of investments can fall as well as rise and you may get back less than you invest. Past performance is not a reliable indicator of future results.

KEY RISKS:
• Capital at risk - you may lose some or all of your investment
• Returns are not guaranteed
• Investment values can be volatile
• Past performance does not predict future results
• The value of your investment may be affected by exchange rate movements if investing overseas

This is a high-risk investment. You should not invest unless you can afford to lose all the money you invest.''',
                'position': 'after_header',
                'condition': r'(?:investment|return|profit|yield|fund|portfolio)'
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

        # Fair, Clear, Not Misleading corrections - ENHANCED GOLD STANDARD
        self.regex_patterns['fair_clear'] = [
            {
                'pattern': r'guaranteed\s+(?:returns?|profit|gains?|income|\d+%)',
                'replacement': '[REMOVED - misleading guarantee claim]',
                'reason': 'FCA COBS 4.2.1 - Guaranteed returns are misleading',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:fully|completely)?\s*protected\s+capital',
                'replacement': 'capital at risk',
                'reason': 'FCA COBS 4.2.1 - Capital protection claims are misleading',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:zero|no)\s+risk',
                'replacement': 'investment risk applies',
                'reason': 'FCA COBS 4.2.1 - No investment is risk-free',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'risk-free\s+(?:investment|return|opportunity)',
                'replacement': '[REMOVED - risk-free claim is misleading]',
                'reason': 'FCA COBS 4.2.1 - No investment is risk-free',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'every\s+investor\s+has\s+(?:made|earned)\s+(?:profit|money|returns?)',
                'replacement': '[REMOVED - unsubstantiated claim about investor outcomes]',
                'reason': 'FCA COBS 4.2.1 - Unsubstantiated performance claims',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:secure|lock in|guarantee)\s+(?:your|the)\s+financial\s+future',
                'replacement': '[REMOVED - misleading guarantee about financial outcomes]',
                'reason': 'FCA COBS 4.2.1 - Cannot guarantee financial future',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:exclusive|limited|secret|insider)\s+(?:opportunity|investment|fund|strategy)',
                'replacement': 'investment opportunity',
                'reason': 'FCA COBS 4.2.1 - Remove promotional hyperbole',
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

        # No Implicit Advice - ENHANCED GOLD STANDARD
        self.templates['no_implicit_advice'] = [
            {
                'template': '''IMPORTANT NOTICE: This is not financial advice or a personal recommendation. This information is provided for general purposes only. The suitability of any investment depends on your individual circumstances. You should seek independent financial advice before making any investment decisions. We are not assessing your personal circumstances or making recommendations tailored to you.''',
                'position': 'start',
                'condition': r'(?:invest|purchase|buy|recommend|suitable|should|best|top|choose|select)'
            }
        ]

        self.regex_patterns['no_implicit_advice'] = [
            {
                'pattern': r'(?:you should|we recommend you|this is suitable for you|best for you)',
                'replacement': '[REMOVED - requires suitability assessment for personal recommendations]',
                'reason': 'FCA COBS 9 - Personal recommendations require suitability assessment',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:most customers choose|popular choice|top\s+\d+\s+performing)',
                'replacement': '[REMOVED - implicit guidance may constitute advice]',
                'reason': 'FCA COBS 4.2.1 - Implicit guidance may be considered a recommendation',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:best|top|leading|superior)\s+(?:option|choice|fund|product)',
                'replacement': 'an available option',
                'reason': 'FCA COBS 4.2.1 - Avoid implied recommendations',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'suitable for everyone',
                'replacement': '[REMOVED - suitability depends on individual circumstances]',
                'reason': 'FCA COBS 9 - Suitability is individual-specific',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'no\s+advice\s+(?:needed|required|necessary)',
                'replacement': '[REMOVED - customers should consider seeking advice]',
                'reason': 'FCA COBS 4.2.1 - Do not discourage seeking advice',
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

        # NEW: Pressure Tactics / Urgency (Consumer Duty - Avoid Foreseeable Harm)
        self.regex_patterns['pressure_tactics'] = [
            {
                'pattern': r'(?:limited|last|final)\s+(?:time|chance|opportunity|offer)',
                'replacement': '[REMOVED - pressure tactic]',
                'reason': 'Consumer Duty - Avoid creating undue pressure to invest',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:act|invest|apply|join)\s+(?:now|today|immediately)',
                'replacement': 'consider this investment carefully',
                'reason': 'Consumer Duty - Customers need time to make informed decisions',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:hurry|don\'t miss out|limited spaces?|only\s+\d+\s+places?)',
                'replacement': '[REMOVED - undue pressure tactic]',
                'reason': 'Consumer Duty - Avoid creating false urgency',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Minimum Investment Affordability Context
        self.regex_patterns['minimum_investment'] = [
            {
                'pattern': r'(?:just|only|as little as)\s+£([\d,]+)',
                'replacement': r'minimum investment £\1 (invest only what you can afford to lose)',
                'reason': 'Consumer Duty - Affordability warning required',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Sophistication Requirements for High-Risk Investments
        self.templates['sophistication_requirements'] = [
            {
                'template': '''INVESTOR CLASSIFICATION: This investment is only suitable for sophisticated investors, high net worth individuals, or those who can afford to lose their entire investment. You may need to self-certify as a sophisticated investor or meet high net worth criteria.

This is a high-risk, illiquid investment that may not be suitable for you.''',
                'position': 'after_header',
                'condition': r'(?:high[\s-]risk|illiquid|unregulated|startup|venture|private equity)'
            }
        ]

        # NEW: Performance Fee Disclosure Enhancement
        self.regex_patterns['performance_fees'] = [
            {
                'pattern': r'performance\s+fee(?:s)?\s+only\s+(?:charged|applied)\s+on\s+profit',
                'replacement': 'performance fees apply (see fee schedule - may include high water mark provisions)',
                'reason': 'FCA - Full fee disclosure required, not just "on profits"',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Unsubstantiated Awards/Rankings
        self.regex_patterns['awards_rankings'] = [
            {
                'pattern': r'award-winning\s+(?:team|fund|strategy|manager)',
                'replacement': '[specify award name, date, and awarding body or REMOVE]',
                'reason': 'FCA COBS 4.2.1 - Awards must be substantiated and relevant',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Comparator Requirements
        self.templates['performance_comparator'] = [
            {
                'template': '''PERFORMANCE DISCLOSURE: Past performance figures are shown net of fees. Comparator: [specify benchmark index]. Performance period: [specify]. Source: [specify].

Past performance is not a reliable indicator of future results.''',
                'position': 'after_header',
                'condition': r'(?:performance|returns?\s+of\s+\d+%|annual\s+returns?)'
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
        """GDPR UK compliance correction patterns - GOLD STANDARD"""

        # Consent corrections - ENHANCED
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
            },
            {
                'pattern': r'(?:thanks|welcome).*(?:signing up|subscribed).*(?:you\'ll|you will)\s+(?:now\s+)?receive',
                'replacement': '[MISSING CONSENT - Add explicit opt-in checkbox before data processing]',
                'reason': 'GDPR Article 7 - Consent must be obtained BEFORE processing',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'pre-?(?:ticked|checked|selected)\s+(?:box|checkbox)',
                'replacement': '[INVALID - pre-ticked boxes do not constitute valid consent]',
                'reason': 'GDPR Article 7(2) - Consent requests must be unbundled and not pre-ticked',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Excessive Data Collection
        self.regex_patterns['excessive_collection'] = [
            {
                'pattern': r'(?:mother\'s maiden name|children\'s names|medical conditions|credit score|bank statements|passport number|driving licen[sc]e).*(?:required|mandatory|must provide)',
                'replacement': '[EXCESSIVE - justify necessity or remove under GDPR Article 5(1)(c)]',
                'reason': 'GDPR Article 5(1)(c) - Data minimization principle',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:complete|full|all)\s+(?:information|details|data).*(?:required|needed|necessary)',
                'replacement': '[SPECIFY only necessary data fields]',
                'reason': 'GDPR Article 5(1)(c) - Only collect data adequate, relevant, and limited',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Vague Third Party Sharing (2 rules)
        self.regex_patterns['third_party_vague'] = [
            {
                'pattern': r'(?:carefully selected|trusted|partner)\s+third parties',
                'replacement': '[SPECIFY categories of third parties or list specific recipients]',
                'reason': 'GDPR Article 13(1)(e) - Recipients must be specifically identified',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'we\s+may\s+share.*with.*parties',
                'replacement': '[SPECIFY which categories of recipients and purposes]',
                'reason': 'GDPR - Third party sharing must be transparent and specific',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Vague Purpose Detection (3 rules)
        self.regex_patterns['vague_purpose'] = [
            {
                'pattern': r'(?:various|multiple|other|similar|related)\s+purposes',
                'replacement': '[SPECIFY exact purposes under GDPR Article 13(1)(c)]',
                'reason': 'GDPR Article 13(1)(c) - Purposes must be specific and explicit',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'legitimate\s+business\s+interests?(?!\s+\()',
                'replacement': 'legitimate interests [SPECIFY which interests and balancing test]',
                'reason': 'GDPR Article 6(1)(f) - Legitimate interests must be specified',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:and|or)\s+other\s+(?:uses|purposes|activities)',
                'replacement': '[REMOVE - specify each purpose explicitly]',
                'reason': 'GDPR Article 5(1)(b) - Purpose limitation principle',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Vague Retention Period (3 rules)
        self.regex_patterns['vague_retention'] = [
            {
                'pattern': r'(?:as|for)\s+(?:long\s+as\s+)?(?:required|necessary|needed)(?!\s+\()',
                'replacement': '[SPECIFY retention period - e.g., "for 7 years as required by law"]',
                'reason': 'GDPR Article 13(2)(a) - Retention period must be specified',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'may\s+be\s+retained\s+indefinitely',
                'replacement': '[SPECIFY maximum retention period under GDPR Article 5(1)(e)]',
                'reason': 'GDPR Article 5(1)(e) - Storage limitation principle',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'for\s+regulatory\s+(?:and|or)\s+business\s+purposes',
                'replacement': '[SPECIFY exact retention periods and legal basis]',
                'reason': 'GDPR Article 13(2)(a) - Must specify retention criteria',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Weak Security Practices (3 rules)
        self.regex_patterns['weak_security'] = [
            {
                'pattern': r'(?:password|credential|PIN)\s+(?:is|has been reset to|will be):\s*[A-Za-z0-9]+',
                'replacement': '[SECURITY RISK - Never send passwords in plain text. Use secure reset link]',
                'reason': 'GDPR Article 32 - Technical and organisational measures required',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'you\s+may\s+change\s+it\s+later\s+if\s+desired',
                'replacement': 'You MUST change this temporary password immediately',
                'reason': 'GDPR Article 32 - Security of processing',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:sent|emailed)\s+(?:via|by)\s+(?:email|unencrypted)',
                'replacement': '[SECURITY RISK - Use secure transmission methods]',
                'reason': 'GDPR Article 32(1) - Appropriate security measures',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: International Transfer Without Safeguards (2 rules)
        self.regex_patterns['transfer_safeguards'] = [
            {
                'pattern': r'(?:data|servers?|processing).*(?:located|based|stored)\s+(?:in|across)\s+(?:USA|India|Singapore|China|[A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*)(?!\s*\.?\s*(?:We|All|Appropriate|Standard|Adequate))',
                'replacement': r'\g<0>. We ensure appropriate safeguards are in place through [adequacy decisions / standard contractual clauses / binding corporate rules]',
                'reason': 'GDPR Article 46 - Transfers require appropriate safeguards',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'processed\s+(?:wherever|anywhere)\s+our\s+staff\s+are\s+located',
                'replacement': 'processed in [specify countries]. Appropriate safeguards under GDPR Chapter V are in place',
                'reason': 'GDPR Article 44 - International transfer rules',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Opaque Automated Decisions (2 rules)
        self.regex_patterns['automated_decision_opaque'] = [
            {
                'pattern': r'(?:after\s+)?automated\s+(?:assessment|evaluation|decision).*(?:declined|rejected|approved)(?!.*(?:right to|human|contest|object))',
                'replacement': r'\g<0>. You have the right to human review, to contest this decision, and to express your point of view under GDPR Article 22(3)',
                'reason': 'GDPR Article 22 - Right not to be subject to automated decisions',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:this|the)\s+decision\s+is\s+final(?!\s*\.?\s*(?:You have|Right to))',
                'replacement': 'this decision may be reviewed. You have the right to human intervention under GDPR Article 22',
                'reason': 'GDPR Article 22(3) - Right to obtain human intervention',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Children Data Unprotected (2 rules)
        self.regex_patterns['children_protection'] = [
            {
                'pattern': r'(?:child|minor|ages?\s+\d+(?:-\d+)?).*(?:send|email|provide|marketing|updates)',
                'replacement': '[REQUIRES PARENTAL CONSENT - Children under 13 cannot consent to data processing]',
                'reason': 'GDPR Article 8 - Child consent requires parental authorization',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:account|credentials|password)\s+(?:provided|sent)\s+(?:directly\s+)?to\s+(?:the\s+)?(?:child|minor)',
                'replacement': '[INVALID - Provide account access to parent/guardian only]',
                'reason': 'GDPR Article 8 - Parental responsibility for child data',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Cookies Forced Consent (2 rules)
        self.regex_patterns['cookies_forced'] = [
            {
                'pattern': r'by\s+continuing.*you\s+(?:accept|consent\s+to)\s+(?:all\s+)?cookies',
                'replacement': '[INVALID - Explicit consent required for non-essential cookies before use]',
                'reason': 'PECR Regulation 6 - Prior consent required for cookies',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'third-party\s+cookies.*(?:enabled|help us)(?!.*(?:consent|your choice|opt-out))',
                'replacement': r'\g<0>. [REQUIRES YOUR EXPLICIT CONSENT - Please accept or reject]',
                'reason': 'PECR - Explicit consent for tracking cookies',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Difficult Consent Withdrawal (2 rules)
        self.regex_patterns['withdrawal_difficulty'] = [
            {
                'pattern': r'(?:to\s+(?:update|change|withdraw)).*(?:you\s+must|required\s+to)\s+(?:call|phone|contact)\s+(?:our\s+)?(?:customer\s+service|support)',
                'replacement': '[MUST BE AS EASY AS GIVING CONSENT - Provide simple online withdrawal mechanism]',
                'reason': 'GDPR Article 7(3) - Withdrawal must be as easy as giving consent',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:consent|preferences).*recorded.*(?:call|contact|phone).*to\s+(?:change|update|withdraw)',
                'replacement': '[PROVIDE EASY WITHDRAWAL - Add online unsubscribe or preference center]',
                'reason': 'GDPR Article 7(3) - Easy withdrawal required',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Missing Lawful Basis (1 rule)
        self.regex_patterns['lawful_basis_missing'] = [
            {
                'pattern': r'we\s+(?:collect|process|use).*(?:name|address|email|phone|data|information)(?!.*(?:based on|lawful basis|consent|contract|legal obligation|legitimate interest))',
                'replacement': r'\g<0> based on [specify: your consent / performance of contract / legal obligation / our legitimate interests with balancing test]',
                'reason': 'GDPR Article 6 - Processing requires lawful basis',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Purpose Specification
        self.templates['purpose_limitation'] = [
            {
                'template': '''PURPOSE: We process your personal data for the following specific purposes:
[Specify each purpose clearly]

We will not process your data for purposes incompatible with the original purpose without obtaining your consent.''',
                'position': 'after_header',
                'condition': r'(?:purpose|use|process).*(?:data|information)'
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
        """Tax UK compliance correction patterns - GOLD STANDARD"""

        # VAT threshold corrections (3 rules)
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

        # NEW: Invalid VAT Number Format (2 rules)
        self.regex_patterns['vat_number_invalid'] = [
            {
                'pattern': r'VAT\s+(?:Reg|No|Number):?\s*(?!GB)\d{9}',
                'replacement': r'VAT Registration Number: GB[9 digits]',
                'reason': 'UK VAT numbers must start with GB prefix',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'VAT\s+(?:Reg|No|Number):?\s*GB\d{1,8}(?!\d)',
                'replacement': '[INVALID VAT NUMBER - UK VAT numbers are GB followed by 9 or 12 digits]',
                'reason': 'UK VAT registration numbers require 9 or 12 digits after GB',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Wrong VAT Rates on Specific Goods (4 rules)
        self.regex_patterns['vat_rate_errors'] = [
            {
                'pattern': r'(?:children\'?s?\s+)?(?:educational\s+)?books?.*VAT\s+@\s+20%',
                'replacement': r'\g<0> [ERROR - Most books are zero-rated for VAT]',
                'reason': 'Books are generally zero-rated under UK VAT law',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:food|groceries).*VAT\s+@\s+20%',
                'replacement': r'\g<0> [CHECK RATE - Most food is zero-rated, exceptions apply]',
                'reason': 'Most food is zero-rated unless prepared/luxury items',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:children\'?s?\s+)?clothing.*VAT\s+@\s+20%',
                'replacement': r'\g<0> [CHECK RATE - Children\'s clothing is zero-rated]',
                'reason': 'Children\'s clothing and footwear is zero-rated',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'newspapers?.*VAT\s+@\s+20%',
                'replacement': r'\g<0> [ERROR - Newspapers are zero-rated]',
                'reason': 'Newspapers and most printed matter are zero-rated',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Incomplete Invoice Detection (3 rules)
        self.regex_patterns['incomplete_invoice'] = [
            {
                'pattern': r'INVOICE(?:.*\n){0,10}.*£[\d,]+(?!.*(?:VAT|Tax)\s+(?:No|Number|Registration))',
                'replacement': r'\g<0>\n[MISSING VAT NUMBER - VAT-registered businesses must show VAT number on invoices]',
                'reason': 'VAT Act 1994 - VAT invoices require VAT registration number',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'INVOICE(?!.*(?:date|invoice number|customer name|description))',
                'replacement': '[INCOMPLETE INVOICE - Must include: unique number, date, supplier/customer details, description, amounts, VAT details]',
                'reason': 'VAT regulations require specific invoice elements',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'Payment\s+due.*(?!.*(?:date of supply|tax point|invoice date))',
                'replacement': r'\g<0> [MISSING TAX POINT - Invoice must show date of supply]',
                'reason': 'VAT invoice requirements - tax point must be stated',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Non-Allowable Expense Advice (5 rules)
        self.regex_patterns['non_allowable_expenses'] = [
            {
                'pattern': r'(?:claim|deduct).*(?:client\s+entertainment|entertaining\s+clients)(?!\s+(?:is not|not allowable))',
                'replacement': '[NOT ALLOWABLE - Client entertainment is not a deductible business expense]',
                'reason': 'ITTOIA 2005 s45 - Entertainment expenses disallowed',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:gym|health club)\s+membership.*(?:business\s+expense|claim|deduct)',
                'replacement': '[NOT ALLOWABLE - Personal health expenses are not deductible]',
                'reason': 'Personal expenditure not allowable under ITTOIA 2005',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:home\s+extension|house\s+renovation).*(?:office|business|claim)',
                'replacement': '[CAPITAL EXPENDITURE - Not allowable as revenue expense. May qualify for capital allowances if wholly business use]',
                'reason': 'Capital vs revenue distinction - HMRC guidance',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'family\s+holiday.*(?:networking|conference|business)',
                'replacement': '[DISALLOWABLE - Personal holiday costs are not deductible even if some business activity]',
                'reason': 'Wholly and exclusively test - personal element disallows claim',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'HMRC\s+rarely\s+checks\s+small\s+businesses',
                'replacement': '[REMOVED - MISLEADING. HMRC conducts compliance checks on businesses of all sizes]',
                'reason': 'Misleading tax advice - HMRC actively checks small businesses',
                'flags': re.IGNORECASE
            }
        ]

        # ENHANCED: HMRC Scam Detection (4 rules - was 2)
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
            },
            {
                'pattern': r'refund\s+expires\s+in\s+\d+\s+(?:hours|days)',
                'replacement': '[SCAM WARNING - HMRC refunds do not expire within days]',
                'reason': 'HMRC scam indicator - urgency tactics',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:click here|click\s+link).*(?:claim|refund).*(?:immediately|now)',
                'replacement': '[PHISHING RISK - HMRC communications direct you to official gov.uk services, not external links]',
                'reason': 'HMRC phishing prevention',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Scottish Income Tax (2 rules)
        self.regex_patterns['scottish_tax'] = [
            {
                'pattern': r'(?:Scottish|Scotland).*(?:taxpayer|resident).*(?:20%|40%|45%)\s+(?:tax|rate)(?!\s*\(Scottish rates)',
                'replacement': r'\g<0> [CHECK SCOTTISH RATES - Scotland has different income tax bands: 19%, 20%, 21%, 42%, 47%]',
                'reason': 'Scottish Income Tax rates differ from rest of UK',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'income\s+tax.*UK(?!.*(?:except Scotland|Scottish rates differ))',
                'replacement': r'\g<0> (Scottish taxpayers are subject to different rates)',
                'reason': 'Scottish Income Tax devolution - must clarify',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Cash Business Warnings (2 rules)
        self.regex_patterns['cash_only_warnings'] = [
            {
                'pattern': r'(?:cash\s+only|no\s+cards?|cash\s+preferred).*(?:business|payment|accepted)',
                'replacement': r'\g<0> [TAX COMPLIANCE - Ensure all cash sales are properly recorded and declared to HMRC]',
                'reason': 'Cash business compliance - HMRC scrutiny',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:off\s+the\s+books|under\s+the\s+table|cash\s+in\s+hand)',
                'replacement': '[TAX EVASION - All income must be declared to HMRC. Penalties apply for non-declaration]',
                'reason': 'Tax evasion prevention',
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
        """NDA UK compliance correction patterns - GOLD STANDARD"""

        # NEW: Blocks Whistleblowing Detection (3 rules)
        self.regex_patterns['blocks_whistleblowing'] = [
            {
                'pattern': r'(?:any|all)\s+(?:disclosure|information).*(?:for any reason|under any circumstances)\s+(?:is\s+)?(?:strictly\s+)?prohibited',
                'replacement': '[UNLAWFUL - Must allow protected disclosures under Public Interest Disclosure Act 1998]',
                'reason': 'PIDA 1998 - Cannot prevent whistleblowing',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:must not|cannot|shall not)\s+disclose.*(?:regulators?|authorities|law enforcement)',
                'replacement': '[UNLAWFUL - Cannot prevent reporting to regulators or law enforcement]',
                'reason': 'PIDA 1998 / common law - Protected disclosures',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:accounting|regulatory|internal)\s+(?:practices|matters|investigations).*(?:must remain|strictly)\s+confidential',
                'replacement': r'\g<0> [EXCEPT as protected under PIDA 1998 or required by law]',
                'reason': 'Cannot override statutory whistleblowing protections',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Blocks Crime Reporting (2 rules)
        self.regex_patterns['blocks_crime_reporting'] = [
            {
                'pattern': r'(?:violation|gross misconduct).*(?:disclose|report).*(?:criminal|suspected)',
                'replacement': '[UNLAWFUL RESTRICTION - Employees have right to report suspected crimes]',
                'reason': 'Cannot prevent reporting criminal activity',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'including.*(?:to|with).*(?:regulators|law enforcement|legal authorities)',
                'replacement': 'except where required by law or protected by the Public Interest Disclosure Act 1998',
                'reason': 'Must preserve legal reporting rights',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Overly Broad Definition (3 rules)
        self.regex_patterns['definition_too_broad'] = [
            {
                'pattern': r'"Confidential Information"\s+means\s+any\s+and\s+all\s+information',
                'replacement': '"Confidential Information" means [SPECIFY categories of information - "any and all" is too broad]',
                'reason': 'NDA definitions must be specific and reasonable in scope',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:observations|opinions|ideas).*(?:presumed|deemed)\s+confidential',
                'replacement': '[TOO BROAD - Specify categories of genuinely confidential information only]',
                'reason': 'Overly broad NDA definitions may be unenforceable',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'all\s+information\s+exchanged.*confidential\s+unless.*explicitly\s+stated\s+otherwise',
                'replacement': '[REVERSED PRESUMPTION - Confidentiality should apply only to specifically identified information]',
                'reason': 'Presumption of confidentiality too broad',
                'flags': re.IGNORECASE
            }
        ]

        # ENHANCED: Duration Reasonableness (3 rules - was 2)
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
            },
            {
                'pattern': r'(?:continues?|survives?|remains?).*(?:without\s+time\s+limit|eternal)',
                'replacement': 'continues for [specify reasonable period, e.g., 3 years post-termination]',
                'reason': 'Unlimited duration disproportionate and potentially unenforceable',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Missing Permitted Disclosures Detection (1 rule)
        self.regex_patterns['no_permitted_disclosures'] = [
            {
                'pattern': r'(?:nda|non-disclosure|confidentiality).*(?:agreement|undertaking)(?!.*(?:permitted disclosures|may disclose|except))',
                'replacement': r'\g<0>\n[ADD PERMITTED DISCLOSURES - Specify when disclosure is allowed: to employees, advisers, as required by law, protected disclosures]',
                'reason': 'NDAs should specify circumstances where disclosure is permitted',
                'flags': re.IGNORECASE
            }
        ]

        # Whistleblowing protection template
        self.templates['whistleblowing'] = [
            {
                'template': 'PROTECTED DISCLOSURES: Nothing in this Agreement prevents the disclosure of information protected under the Public Interest Disclosure Act 1998 (whistleblowing) or required by law.',
                'position': 'end',
                'condition': r'(?:disclose|confidential|nda|non-disclosure)'
            }
        ]

        # Crime reporting protection template
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
        """HR Scottish employment law correction patterns - GOLD STANDARD"""

        # NEW: Missing Accompaniment Notice (2 rules)
        self.regex_patterns['missing_accompaniment_notice'] = [
            {
                'pattern': r'(?:disciplinary|grievance)\s+(?:meeting|hearing)(?!.*(?:right to be accompanied|accompanied by|companion))',
                'replacement': r'\g<0> [MISSING - You have the right to be accompanied by a colleague or trade union representative under ERA 1999 s10]',
                'reason': 'ERA 1999 Section 10 - Must inform of accompaniment right',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:required|invited)\s+to\s+attend.*(?:disciplinary|grievance)(?!.*(?:accompanied|companion|representative))',
                'replacement': r'\g<0>. You have the statutory right to be accompanied by a work colleague or trade union representative',
                'reason': 'ERA 1999 - Accompaniment rights must be stated',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Vague Allegations (3 rules)
        self.regex_patterns['vague_allegations'] = [
            {
                'pattern': r'(?:concerns|issues|matters|allegations).*(?:have been raised|been made).*(?:about your|regarding your)\s+(?:behavior|conduct|performance)(?!.*(?:specifically|detail|particular|namely))',
                'replacement': '[TOO VAGUE - Specify exact allegations with dates, times, witnesses, and details]',
                'reason': 'ACAS Code - Employees must know case against them',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'some concerns.*(?:discuss|address|meeting)',
                'replacement': '[INSUFFICIENT - State specific allegations clearly]',
                'reason': 'Natural justice - Right to know allegations in detail',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:performance|conduct).*concerns',
                'replacement': '[SPECIFY - Provide specific examples with dates and details]',
                'reason': 'ACAS Code para 5 - Nature of allegation must be clear',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: No Evidence Disclosed (2 rules)
        self.regex_patterns['no_evidence_disclosed'] = [
            {
                'pattern': r'(?:disciplinary|hearing)(?!.*(?:evidence|copies|documents|statements|provided|attached|enclosed))',
                'replacement': r'\g<0> [EVIDENCE REQUIRED - Provide copies of all evidence at least 48 hours before meeting]',
                'reason': 'ACAS Code para 9 - Advance disclosure of evidence',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:serious|gross)\s+misconduct(?!.*(?:evidence|statement|witness|document))',
                'replacement': r'\g<0> [PROVIDE EVIDENCE - Employee entitled to see evidence before disciplinary hearing]',
                'reason': 'Natural justice - Right to see evidence',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Insufficient Notice Period (2 rules)
        self.regex_patterns['insufficient_notice'] = [
            {
                'pattern': r'(?:disciplinary|hearing).*tomorrow(?!\s+(?:note|please note|we recognize))',
                'replacement': r'\g<0> [INSUFFICIENT NOTICE - Provide reasonable notice, typically 48 hours minimum for disciplinary hearings]',
                'reason': 'ACAS Code - Reasonable notice required',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:meeting|hearing).*(?:this afternoon|in\s+\d+\s+hours?|by\s+\d+(?:pm|am))',
                'replacement': '[UNREASONABLE NOTICE - Employee needs adequate time to prepare, typically 48 hours minimum]',
                'reason': 'ACAS Code - Adequate preparation time',
                'flags': re.IGNORECASE
            }
        ]

        # ENHANCED: Suspension Issues (3 rules - was 1)
        self.regex_patterns['suspension'] = [
            {
                'pattern': r'suspended.*(?:pending|during).*investigation',
                'replacement': 'suspended on full pay (not a disciplinary sanction) pending investigation',
                'reason': 'Clarify suspension is neutral act, not punishment',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'suspended\s+without\s+pay',
                'replacement': 'suspended on full pay',
                'reason': 'Suspension pending investigation must be on full pay',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:immediate|effective immediately)\s+suspension(?!.*(?:full pay|on pay|with pay|justified|gross misconduct proven))',
                'replacement': r'\g<0> on full pay. [Suspension is a neutral act, not a punishment. Only use when necessary]',
                'reason': 'Suspension must be on full pay and justified',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Investigation Skipped (2 rules)
        self.regex_patterns['investigation_skipped'] = [
            {
                'pattern': r'(?:allegation|concern).*(?:disciplinary hearing|dismissal)(?!.*(?:investigation|investigated|inquiry))',
                'replacement': r'\g<0> [INVESTIGATION REQUIRED - Must conduct fair investigation before disciplinary hearing per ACAS Code]',
                'reason': 'ACAS Code para 4 - Investigate before disciplinary action',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:immediate|straight to).*(?:disciplinary|hearing)',
                'replacement': '[UNFAIR PROCESS - Conduct investigation before moving to disciplinary stage]',
                'reason': 'ACAS Code - Investigation must precede disciplinary hearing',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Representation Denied (2 rules)
        self.regex_patterns['representation_denied'] = [
            {
                'pattern': r'(?:you|cannot|may not).*(?:bring|have).*(?:representative|companion|union)',
                'replacement': '[UNLAWFUL - Statutory right to be accompanied by colleague or union rep under ERA 1999 s10]',
                'reason': 'ERA 1999 Section 10 - Cannot deny accompaniment',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:must attend|required)\s+alone',
                'replacement': 'are entitled to be accompanied by a work colleague or trade union representative',
                'reason': 'ERA 1999 - Accompaniment is statutory right',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Missing Outcome Reasoning (2 rules)
        self.regex_patterns['no_outcome_reasoning'] = [
            {
                'pattern': r'(?:decision|outcome)\s+is\s+(?:dismissal|warning|sanction)(?!.*(?:because|reason|based on|considering|after reviewing))',
                'replacement': r'\g<0> [INSUFFICIENT - Explain reasons for decision based on evidence and mitigating factors]',
                'reason': 'ACAS Code para 17 - Decision and reasons must be communicated',
                'flags': re.IGNORECASE
            },
            {
                'pattern': r'(?:been dismissed|final written warning|first written warning)(?!\s*\.?\s*(?:The reason|This is because|Reasons))',
                'replacement': r'\g<0>. [PROVIDE REASONING - Explain why this sanction was chosen]',
                'reason': 'Natural justice - Reasoned decisions required',
                'flags': re.IGNORECASE
            }
        ]

        # NEW: Unreasonable Timeframes (1 rule)
        self.regex_patterns['unreasonable_timeframe'] = [
            {
                'pattern': r'(?:appeal|respond).*(?:within|by)\s+(?:24\s+hours?|1\s+day|tomorrow)',
                'replacement': r'\g<0> [UNREASONABLE - Provide adequate time, typically 5-10 working days for appeals]',
                'reason': 'ACAS Code - Reasonable timeframes for responses',
                'flags': re.IGNORECASE
            }
        ]

        # Accompaniment rights template (Employment Relations Act 1999, Section 10)
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
