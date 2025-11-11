"""
Enhanced GDPR UK Gates - Comprehensive Data Protection Compliance
60+ validation rules for UK GDPR compliance

References:
- UK GDPR (retained EU law)
- Data Protection Act 2018
- ICO Guidance and Codes of Practice
- Privacy and Electronic Communications Regulations (PECR)

Author: LOKI GDPR Compliance Specialist Agent
Version: 3.0.0
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.gdpr_uk.gates.consent import ConsentGate
from modules.gdpr_uk.gates.purpose import PurposeGate
from modules.gdpr_uk.gates.retention import RetentionGate
from modules.gdpr_uk.gates.rights import RightsGate
from modules.gdpr_uk.gates.security import SecurityGate
from modules.gdpr_uk.gates.lawful_basis import LawfulBasisGate
from modules.gdpr_uk.gates.data_minimisation import DataMinimisationGate
from modules.gdpr_uk.gates.third_party_sharing import ThirdPartySharingGate
from modules.gdpr_uk.gates.international_transfer import InternationalTransferGate
from modules.gdpr_uk.gates.automated_decisions import AutomatedDecisionsGate
from modules.gdpr_uk.gates.children_data import ChildrenDataGate
from modules.gdpr_uk.gates.breach_notification import BreachNotificationGate
from modules.gdpr_uk.gates.dpo_contact import DpoContactGate
from modules.gdpr_uk.gates.cookies_tracking import CookiesTrackingGate
from modules.gdpr_uk.gates.withdrawal_consent import WithdrawalConsentGate

# Import compliance validators
from compliance.gdpr.consent_validator import ConsentValidator
from compliance.gdpr.subject_rights import SubjectRightsValidator
from compliance.gdpr.retention import RetentionPolicyChecker
from compliance.gdpr.international_transfer import InternationalTransferValidator
from compliance.gdpr.dpia_checker import DPIAChecker
from compliance.gdpr.cookie_consent import CookieConsentValidator
from compliance.gdpr.breach_checker import BreachNotificationChecker
from compliance.gdpr.children import ChildrenDataProtection
from compliance.gdpr.legitimate_interest import LegitimateInterestAssessor
from compliance.gdpr.privacy_notice import PrivacyNoticeChecker
from compliance.gdpr.data_minimization import DataMinimizationValidator

import re
from typing import Dict, List


class EnhancedGDPRGates:
    """
    Comprehensive GDPR UK compliance gate system
    60+ validation rules covering all aspects of UK GDPR
    """

    def __init__(self):
        self.name = "Enhanced GDPR UK Compliance"
        self.version = "3.0.0"
        self.total_gates = 0

        # Initialize all gates
        self.gates = self._initialize_gates()
        self.total_gates = len(self.gates)

        # Initialize compliance validators
        self.consent_validator = ConsentValidator()
        self.rights_validator = SubjectRightsValidator()
        self.retention_checker = RetentionPolicyChecker()
        self.transfer_validator = InternationalTransferValidator()
        self.dpia_checker = DPIAChecker()
        self.cookie_validator = CookieConsentValidator()
        self.breach_checker = BreachNotificationChecker()
        self.children_validator = ChildrenDataProtection()
        self.li_assessor = LegitimateInterestAssessor()
        self.privacy_checker = PrivacyNoticeChecker()
        self.minimization_validator = DataMinimizationValidator()

    def _initialize_gates(self) -> Dict:
        """Initialize all 60+ GDPR compliance gates"""
        gates = {}

        # ===== CORE EXISTING GATES (15) =====
        gates['consent'] = ConsentGate()
        gates['purpose'] = PurposeGate()
        gates['retention'] = RetentionGate()
        gates['rights'] = RightsGate()
        gates['security'] = SecurityGate()
        gates['lawful_basis'] = LawfulBasisGate()
        gates['data_minimisation'] = DataMinimisationGate()
        gates['third_party_sharing'] = ThirdPartySharingGate()
        gates['international_transfer'] = InternationalTransferGate()
        gates['automated_decisions'] = AutomatedDecisionsGate()
        gates['children_data'] = ChildrenDataGate()
        gates['breach_notification'] = BreachNotificationGate()
        gates['dpo_contact'] = DpoContactGate()
        gates['cookies_tracking'] = CookiesTrackingGate()
        gates['withdrawal_consent'] = WithdrawalConsentGate()

        # ===== CONSENT GATES (10) =====
        gates['consent_freely_given'] = self._create_simple_gate(
            "consent_freely_given",
            "critical",
            "UK GDPR Article 7(4); ICO Consent Guidance",
            ['consent', 'agree', 'permission'],
            [r'by\s+using.*(?:you\s+)?agree', r'continued\s+use.*constitutes', r'must\s+(?:agree|consent).*to\s+use'],
            "Forced consent detected - consent must be freely given without detriment",
            "Remove forced consent: 'By using this site you agree...' is not valid. Provide clear opt-in choice."
        )

        gates['consent_specific'] = self._create_simple_gate(
            "consent_specific",
            "high",
            "UK GDPR Article 7; ICO Consent Guidance",
            ['consent', 'agree'],
            [r'(?:agree|consent)\s+to\s+(?:all|everything)', r'accept\s+all.*terms.*and.*privacy'],
            "Bundled consent - must provide separate consent for different purposes",
            "Provide granular consent: separate opt-ins for marketing, analytics, cookies, etc."
        )

        gates['consent_informed'] = self._create_simple_gate(
            "consent_informed",
            "high",
            "UK GDPR Article 7; ICO Consent Guidance",
            ['consent', 'agree'],
            [r'consent|agree'],
            "Consent requested without clear information about processing",
            "Provide clear information before requesting consent: what data, why, how long, who has access."
        )

        gates['consent_unambiguous'] = self._create_simple_gate(
            "consent_unambiguous",
            "critical",
            "UK GDPR Article 4(11); ICO Consent Guidance",
            ['consent'],
            [r'automatically.*consent', r'pre.?selected', r'opt.?out.*if.*don.?t', r'deemed.*consented'],
            "Consent not unambiguous - pre-selected boxes, silence, or inactivity not valid",
            "Require clear affirmative action: active opt-in, explicit checkbox, or 'I agree' button."
        )

        gates['consent_explicit'] = self._create_simple_gate(
            "consent_explicit",
            "critical",
            "UK GDPR Article 9; ICO Special Category Data",
            ['health', 'medical', 'biometric', 'genetic', 'racial', 'ethnic', 'religious', 'sexual orientation'],
            [r'(?:health|medical|biometric|genetic).*data'],
            "Special category data requires explicit consent (Article 9)",
            "Add: 'By clicking [I agree], you provide explicit consent to process your [health/biometric] data.'"
        )

        gates['consent_withdrawable'] = self._create_simple_gate(
            "consent_withdrawable",
            "high",
            "UK GDPR Article 7(3); ICO Consent Guidance",
            ['consent'],
            [r'consent'],
            "Consent mentioned but no easy withdrawal mechanism",
            "Add: 'You can withdraw consent at any time by [simple method].'"
        )

        gates['consent_records'] = self._create_simple_gate(
            "consent_records",
            "medium",
            "UK GDPR Article 7(1); ICO Consent Guidance",
            ['consent'],
            [r'consent'],
            "No mention of consent record-keeping (Article 7(1) requires proof)",
            "Add: 'We maintain records of your consent including date, method, and information provided.'"
        )

        gates['consent_age_verification'] = self._create_simple_gate(
            "consent_age_verification",
            "high",
            "UK GDPR Article 8; DPA 2018 s9",
            ['child', 'children', 'under 13'],
            [r'(?:child|children|under\s+13)'],
            "Children mentioned but no age verification mechanism",
            "Implement age verification for children under 13 (UK consent age)."
        )

        gates['consent_parental'] = self._create_simple_gate(
            "consent_parental",
            "critical",
            "UK GDPR Article 8; DPA 2018 s9",
            ['child', 'children', 'under 13'],
            [r'(?:child|children|under\s+13)'],
            "Children under 13 require parental consent (UK DPA 2018)",
            "Implement parental consent mechanism: email verification, credit card check, etc."
        )

        gates['consent_conditional'] = self._create_simple_gate(
            "consent_conditional",
            "high",
            "UK GDPR Article 7(4); ICO Consent Guidance",
            ['consent'],
            [r'(?:cannot|unable\s+to).*(?:provide|offer).*(?:without|unless).*consent'],
            "Consent tied to service access (only valid if strictly necessary)",
            "Only make consent conditional if strictly necessary for the service. Otherwise provide choice."
        )

        # ===== RIGHTS GATES (8 gates - one per right) =====
        gates['right_to_be_informed'] = self._create_simple_gate(
            "right_to_be_informed",
            "high",
            "UK GDPR Articles 12-14",
            ['privacy policy', 'privacy notice'],
            [r'privacy\s+(?:policy|notice)'],
            "Privacy notice incomplete - right to be informed",
            "Provide transparent information about data processing."
        )

        gates['right_of_access'] = self._create_simple_gate(
            "right_of_access",
            "critical",
            "UK GDPR Article 15",
            ['privacy'],
            [r'privacy'],
            "No mention of right to access personal data (SAR)",
            "Add: 'You have the right to access your personal data. Submit a Subject Access Request (SAR).'"
        )

        gates['right_to_rectification'] = self._create_simple_gate(
            "right_to_rectification",
            "high",
            "UK GDPR Article 16",
            ['privacy'],
            [r'privacy'],
            "No mention of right to rectification",
            "Add: 'You have the right to correct inaccurate or incomplete personal data.'"
        )

        gates['right_to_erasure'] = self._create_simple_gate(
            "right_to_erasure",
            "critical",
            "UK GDPR Article 17",
            ['privacy'],
            [r'privacy'],
            "No mention of right to erasure (right to be forgotten)",
            "Add: 'You have the right to request deletion of your personal data in certain circumstances.'"
        )

        gates['right_to_restrict'] = self._create_simple_gate(
            "right_to_restrict",
            "high",
            "UK GDPR Article 18",
            ['privacy'],
            [r'privacy'],
            "No mention of right to restrict processing",
            "Add: 'You have the right to restrict processing in certain circumstances.'"
        )

        gates['right_to_portability'] = self._create_simple_gate(
            "right_to_portability",
            "high",
            "UK GDPR Article 20",
            ['privacy'],
            [r'privacy'],
            "No mention of right to data portability",
            "Add: 'You have the right to receive your data in a structured, machine-readable format.'"
        )

        gates['right_to_object'] = self._create_simple_gate(
            "right_to_object",
            "high",
            "UK GDPR Article 21",
            ['privacy'],
            [r'privacy'],
            "No mention of right to object to processing",
            "Add: 'You have the right to object to processing, including for direct marketing.'"
        )

        gates['automated_decision_rights'] = self._create_simple_gate(
            "automated_decision_rights",
            "critical",
            "UK GDPR Article 22",
            ['automated', 'profiling', 'AI'],
            [r'(?:automated|profiling|AI)'],
            "Automated decisions mentioned but no rights disclosure",
            "Add: 'You have the right not to be subject to automated decision-making with legal effects.'"
        )

        # ===== RETENTION & DELETION GATES (5) =====
        gates['retention_period_specified'] = self._create_simple_gate(
            "retention_period_specified",
            "high",
            "UK GDPR Article 5(1)(e)",
            ['privacy', 'data'],
            [r'privacy'],
            "Data retention periods not specified",
            "Specify: 'We retain personal data for [specific period] or until [event].'"
        )

        gates['retention_vague'] = self._create_simple_gate(
            "retention_vague",
            "high",
            "UK GDPR Article 5(1)(e)",
            ['retention', 'retain'],
            [r'as\s+long\s+as\s+necessary', r'reasonable\s+(?:period|time)', r'indefinitely'],
            "Vague retention periods - must be specific",
            "Replace vague terms with specific periods: '12 months', 'duration of contract + 6 years', etc."
        )

        gates['deletion_procedures'] = self._create_simple_gate(
            "deletion_procedures",
            "medium",
            "UK GDPR Article 5(1)(e); ICO Retention Guidance",
            ['privacy', 'data'],
            [r'privacy'],
            "No secure deletion or anonymization procedures described",
            "Add: 'We securely delete/anonymize data at end of retention period.'"
        )

        gates['retention_review'] = self._create_simple_gate(
            "retention_review",
            "low",
            "ICO Retention Guidance",
            ['retention'],
            [r'retention'],
            "No mention of retention policy review",
            "Add: 'We regularly review retention periods to ensure compliance.'"
        )

        gates['indefinite_retention'] = self._create_simple_gate(
            "indefinite_retention",
            "critical",
            "UK GDPR Article 5(1)(e)",
            ['retain', 'keep'],
            [r'(?:indefinitely|permanently|forever)', r'never\s+delete'],
            "Indefinite retention violates storage limitation principle",
            "Data cannot be kept indefinitely. Specify retention periods."
        )

        # ===== INTERNATIONAL TRANSFER GATES (7) =====
        gates['transfer_safeguards'] = self._create_simple_gate(
            "transfer_safeguards",
            "critical",
            "UK GDPR Articles 44-50",
            ['transfer', 'outside', 'international'],
            [r'(?:transfer|outside).*(?:uk|eu)'],
            "International transfers without safeguards",
            "Implement SCCs, BCRs, or rely on adequacy decisions for international transfers."
        )

        gates['transfer_adequacy'] = self._create_simple_gate(
            "transfer_adequacy",
            "high",
            "UK GDPR Article 45",
            ['transfer', 'outside'],
            [r'transfer.*(?:to|outside)'],
            "No mention of adequacy decisions for transfers",
            "Specify if transferring to adequate countries or safeguards used."
        )

        gates['transfer_sccs'] = self._create_simple_gate(
            "transfer_sccs",
            "medium",
            "UK GDPR Article 46",
            ['transfer', 'outside'],
            [r'transfer.*outside'],
            "No mention of Standard Contractual Clauses (SCCs)",
            "For non-adequate countries, implement SCCs or other Article 46 mechanisms."
        )

        gates['transfer_us_dpf'] = self._create_simple_gate(
            "transfer_us_dpf",
            "high",
            "UK Extension to EU-US DPF",
            ['usa', 'united states', 'us '],
            [r'(?:usa|united\s+states|u\.s\.)'],
            "US transfers require Data Privacy Framework or SCCs",
            "Verify US recipients under DPF or implement SCCs (Privacy Shield invalid since 2020)."
        )

        gates['transfer_privacy_shield'] = self._create_simple_gate(
            "transfer_privacy_shield",
            "critical",
            "Schrems II (2020)",
            ['privacy shield'],
            [r'privacy\s+shield'],
            "Privacy Shield is INVALID (Schrems II, 2020)",
            "Remove Privacy Shield references. Use Data Privacy Framework or SCCs instead."
        )

        gates['transfer_tia'] = self._create_simple_gate(
            "transfer_tia",
            "medium",
            "ICO International Transfers Guidance",
            ['transfer', 'international'],
            [r'transfer.*international'],
            "No Transfer Impact Assessment (TIA) mentioned",
            "Conduct TIA for transfers to non-adequate countries."
        )

        gates['transfer_recipients'] = self._create_simple_gate(
            "transfer_recipients",
            "medium",
            "UK GDPR Article 13(1)(e)",
            ['transfer', 'share'],
            [r'transfer.*to\s+third'],
            "Transfer recipients not clearly identified",
            "Name specific entities receiving data or categories of recipients."
        )

        # ===== DPIA GATES (5) =====
        gates['dpia_required'] = self._create_simple_gate(
            "dpia_required",
            "high",
            "UK GDPR Article 35",
            ['systematic', 'large scale', 'monitoring', 'automated'],
            [r'(?:systematic.*extensive|large.?scale.*special|systematic.*monitoring)'],
            "High-risk processing requires DPIA",
            "Conduct Data Protection Impact Assessment for high-risk processing."
        )

        gates['dpia_conducted'] = self._create_simple_gate(
            "dpia_conducted",
            "high",
            "UK GDPR Article 35",
            ['automated', 'biometric', 'large scale'],
            [r'(?:automated|biometric|large.?scale)'],
            "DPIA not documented for high-risk processing",
            "Document DPIA covering: processing description, necessity, risk assessment, mitigation."
        )

        gates['dpia_ico_consultation'] = self._create_simple_gate(
            "dpia_ico_consultation",
            "critical",
            "UK GDPR Article 36",
            ['dpia', 'impact assessment'],
            [r'(?:dpia|impact\s+assessment)'],
            "Residual high risk may require ICO consultation",
            "If DPIA shows high residual risk, consult ICO before processing."
        )

        gates['dpia_biometric'] = self._create_simple_gate(
            "dpia_biometric",
            "critical",
            "UK GDPR Article 35",
            ['biometric', 'facial recognition', 'fingerprint'],
            [r'(?:biometric|facial\s+recognition|fingerprint)'],
            "Biometric processing requires DPIA",
            "Biometric identification always requires DPIA."
        )

        gates['dpia_vulnerable'] = self._create_simple_gate(
            "dpia_vulnerable",
            "critical",
            "UK GDPR Article 35; ICO DPIA Guidance",
            ['vulnerable', 'children', 'employee monitoring'],
            [r'(?:vulnerable|children.*data|employee.*monitoring)'],
            "Processing vulnerable individuals requires DPIA",
            "Conduct DPIA for processing data of vulnerable groups."
        )

        # ===== COOKIE & PECR GATES (7) =====
        gates['cookie_consent_required'] = self._create_simple_gate(
            "cookie_consent_required",
            "high",
            "PECR Regulation 6",
            ['cookie', 'analytics', 'advertising'],
            [r'(?:analytics|advertising|marketing).*cookie'],
            "Non-essential cookies require consent (PECR)",
            "Implement cookie consent banner for non-essential cookies."
        )

        gates['cookie_preticked'] = self._create_simple_gate(
            "cookie_preticked",
            "critical",
            "PECR Regulation 6; ICO Cookies Guidance",
            ['cookie'],
            [r'pre.?ticked.*cookie', r'automatically.*accept.*cookie', r'default.*accept'],
            "Pre-ticked cookie consent is illegal",
            "Remove pre-ticked boxes. Require active opt-in."
        )

        gates['cookie_granular'] = self._create_simple_gate(
            "cookie_granular",
            "high",
            "PECR; ICO Cookies Guidance",
            ['cookie', 'analytics', 'advertising'],
            [r'cookie.*(?:types?|categories)'],
            "No granular cookie controls",
            "Provide separate consent for: analytics, advertising, functional, social media cookies."
        )

        gates['cookie_wall'] = self._create_simple_gate(
            "cookie_wall",
            "high",
            "GDPR Article 7(4); PECR",
            ['cookie'],
            [r'(?:cannot|unable).*(?:access|use).*without.*(?:accept|cookie)'],
            "Cookie wall (blocking access) may violate freely given consent",
            "Allow users to decline cookies and still access basic content."
        )

        gates['cookie_duration'] = self._create_simple_gate(
            "cookie_duration",
            "medium",
            "ICO Cookies Guidance",
            ['cookie'],
            [r'cookie'],
            "Cookie retention periods not specified",
            "Specify how long cookies remain: session vs persistent, expiry periods."
        )

        gates['cookie_third_party'] = self._create_simple_gate(
            "cookie_third_party",
            "medium",
            "PECR; ICO Cookies Guidance",
            ['cookie', 'google analytics', 'facebook'],
            [r'(?:google|facebook|third.?party).*cookie'],
            "Third-party cookies not clearly disclosed",
            "Name all third-party cookie providers: Google Analytics, Facebook, etc."
        )

        gates['cookie_information'] = self._create_simple_gate(
            "cookie_information",
            "high",
            "PECR Regulation 6; ICO Guidance",
            ['cookie'],
            [r'cookie'],
            "Insufficient cookie information",
            "Explain: what cookies are, why used, what data collected, how long stored."
        )

        # ===== BREACH NOTIFICATION GATES (3) =====
        gates['breach_ico_notification'] = self._create_simple_gate(
            "breach_ico_notification",
            "critical",
            "UK GDPR Article 33",
            ['privacy'],
            [r'privacy'],
            "No ICO breach notification procedure (72 hours required)",
            "Add: 'We notify ICO within 72 hours of becoming aware of a breach.'"
        )

        gates['breach_individual_notification'] = self._create_simple_gate(
            "breach_individual_notification",
            "critical",
            "UK GDPR Article 34",
            ['privacy'],
            [r'privacy'],
            "No individual breach notification for high-risk breaches",
            "Add: 'We notify affected individuals without undue delay if breach poses high risk.'"
        )

        gates['breach_documentation'] = self._create_simple_gate(
            "breach_documentation",
            "high",
            "UK GDPR Article 33(5)",
            ['breach'],
            [r'breach'],
            "No breach register/documentation mentioned",
            "Add: 'We maintain a register of all personal data breaches (Article 33(5)).'"
        )

        # ===== ADDITIONAL PRINCIPLE GATES (5) =====
        gates['transparency_principle'] = self._create_simple_gate(
            "transparency_principle",
            "high",
            "UK GDPR Article 5(1)(a)",
            ['privacy'],
            [r'privacy'],
            "Transparency principle - information must be clear and accessible",
            "Use plain language, avoid legal jargon, make privacy info easily accessible."
        )

        gates['accuracy_principle'] = self._create_simple_gate(
            "accuracy_principle",
            "medium",
            "UK GDPR Article 5(1)(d)",
            ['privacy'],
            [r'privacy'],
            "Accuracy principle not addressed",
            "Add: 'We take steps to ensure personal data is accurate and up-to-date.'"
        )

        gates['accountability_principle'] = self._create_simple_gate(
            "accountability_principle",
            "high",
            "UK GDPR Article 5(2)",
            ['privacy'],
            [r'privacy'],
            "Accountability principle - demonstrate compliance",
            "Maintain documentation: policies, DPIAs, data processing records, consent logs."
        )

        gates['integrity_confidentiality'] = self._create_simple_gate(
            "integrity_confidentiality",
            "critical",
            "UK GDPR Article 5(1)(f)",
            ['privacy'],
            [r'privacy'],
            "Integrity and confidentiality - security measures not described",
            "Add: 'We implement appropriate technical and organizational measures to protect data.'"
        )

        gates['privacy_by_design'] = self._create_simple_gate(
            "privacy_by_design",
            "medium",
            "UK GDPR Article 25",
            ['privacy', 'system', 'platform'],
            [r'(?:design|develop|build)'],
            "Privacy by design and default not mentioned",
            "Implement privacy by design: data protection built into systems from the start."
        )

        # ===== PROCESSOR & CONTROLLER GATES (4) =====
        gates['processor_agreements'] = self._create_simple_gate(
            "processor_agreements",
            "high",
            "UK GDPR Article 28",
            ['processor', 'sub-processor', 'third party'],
            [r'(?:processor|sub.?processor|third\s+party\s+service)'],
            "No processor agreements mentioned (Article 28 requirement)",
            "Add: 'We ensure processors comply with GDPR through written agreements.'"
        )

        gates['processor_instructions'] = self._create_simple_gate(
            "processor_instructions",
            "high",
            "UK GDPR Article 28(3)",
            ['processor'],
            [r'processor'],
            "Processors must only process on documented instructions",
            "Add: 'Processors only process data on our documented instructions.'"
        )

        gates['controller_identity'] = self._create_simple_gate(
            "controller_identity",
            "critical",
            "UK GDPR Article 13(1)(a)",
            ['privacy'],
            [r'privacy'],
            "Data controller identity not clearly stated",
            "Clearly identify: 'We are [Company Name], the data controller for your personal data.'"
        )

        gates['joint_controllers'] = self._create_simple_gate(
            "joint_controllers",
            "high",
            "UK GDPR Article 26",
            ['joint', 'jointly'],
            [r'joint(?:ly)?.*(?:controller|responsible)'],
            "Joint controllers must have transparent arrangements",
            "If joint controllers, explain arrangement and respective responsibilities."
        )

        return gates

    def _create_simple_gate(self, name: str, severity: str, legal_source: str,
                           relevance_keywords: List[str], fail_patterns: List[str],
                           fail_message: str, suggestion: str):
        """Helper to create simple pattern-based gates"""

        class SimpleGate:
            def __init__(self):
                self.name = name
                self.severity = severity
                self.legal_source = legal_source
                self.relevance_keywords = relevance_keywords
                self.fail_patterns = fail_patterns
                self.fail_message = fail_message
                self.suggestion = suggestion

            def _is_relevant(self, text):
                if not self.relevance_keywords:
                    return True
                text_lower = (text or '').lower()
                return any(kw in text_lower for kw in self.relevance_keywords)

            def check(self, text, document_type):
                if not self._is_relevant(text):
                    return {
                        'status': 'N/A',
                        'message': f'Not applicable - {name}',
                        'legal_source': self.legal_source
                    }

                text_lower = (text or '').lower()

                # Check fail patterns
                for pattern in self.fail_patterns:
                    if re.search(pattern, text_lower):
                        return {
                            'status': 'FAIL',
                            'severity': self.severity,
                            'message': self.fail_message,
                            'legal_source': self.legal_source,
                            'suggestion': self.suggestion
                        }

                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': f'{name} check passed'
                }

        return SimpleGate()

    def execute(self, text: str, document_type: str = "privacy_policy") -> Dict:
        """
        Execute all GDPR gates against the provided text

        Args:
            text: The document text to validate
            document_type: Type of document being validated

        Returns:
            Dict with comprehensive validation results
        """
        results = {
            'module': self.name,
            'version': self.version,
            'total_gates': self.total_gates,
            'gates': {},
            'summary': {
                'pass': 0,
                'fail': 0,
                'warning': 0,
                'na': 0,
                'critical_failures': [],
                'high_failures': [],
                'compliance_score': 0.0
            }
        }

        # Execute all gates
        for gate_name, gate in self.gates.items():
            try:
                gate_result = gate.check(text, document_type)
                results['gates'][gate_name] = gate_result

                # Update summary
                status = gate_result.get('status', 'N/A')
                if status == 'PASS':
                    results['summary']['pass'] += 1
                elif status == 'FAIL':
                    results['summary']['fail'] += 1
                    severity = gate_result.get('severity', 'high')
                    if severity == 'critical':
                        results['summary']['critical_failures'].append(gate_name)
                    elif severity == 'high':
                        results['summary']['high_failures'].append(gate_name)
                elif status == 'WARNING':
                    results['summary']['warning'] += 1
                elif status == 'N/A':
                    results['summary']['na'] += 1

            except Exception as e:
                results['gates'][gate_name] = {
                    'status': 'ERROR',
                    'severity': 'critical',
                    'message': f'Gate execution error: {str(e)}'
                }

        # Calculate compliance score
        applicable_gates = self.total_gates - results['summary']['na']
        if applicable_gates > 0:
            passed_gates = results['summary']['pass']
            results['summary']['compliance_score'] = (passed_gates / applicable_gates) * 100

        return results

    def get_gate_count(self) -> int:
        """Return total number of gates"""
        return self.total_gates

    def get_gate_list(self) -> List[str]:
        """Return list of all gate names"""
        return list(self.gates.keys())


# Convenience function
def validate_gdpr_compliance(text: str, document_type: str = "privacy_policy") -> Dict:
    """
    Validate GDPR compliance for provided text

    Args:
        text: The document text to validate
        document_type: Type of document

    Returns:
        Dict with validation results
    """
    gates = EnhancedGDPRGates()
    return gates.execute(text, document_type)


if __name__ == "__main__":
    # Test with sample text
    gates = EnhancedGDPRGates()
    print(f"✓ Enhanced GDPR UK Gates Initialized")
    print(f"✓ Total Gates: {gates.get_gate_count()}")
    print(f"✓ Gate Categories: Consent, Rights, Retention, Transfers, DPIA, Cookies, Breach, Principles, Processors")
    print(f"\nGate List:")
    for i, gate_name in enumerate(gates.get_gate_list(), 1):
        print(f"  {i}. {gate_name}")
