"""
Module Recommender - Intelligent auto-detection of required compliance modules
Analyzes document content and organization profile to recommend relevant compliance frameworks.
"""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModuleRecommendation:
    """Recommendation for a compliance module."""
    module_id: str
    module_name: str
    confidence: float  # 0.0 - 1.0
    reason: str
    triggers: List[str]
    priority: str  # 'critical', 'high', 'medium', 'low'
    estimated_impact: str


class ModuleRecommender:
    """
    Intelligent compliance module recommendation engine.

    Features:
    - Content-based analysis
    - Organization profile matching
    - Jurisdiction detection
    - Industry classification
    - Risk-based prioritization
    """

    def __init__(self, modules: Dict[str, Any]):
        self.modules = modules
        self._initialize_detection_patterns()

    def _initialize_detection_patterns(self):
        """Initialize keyword patterns for module detection."""
        self.detection_patterns = {
            'gdpr_uk': {
                'keywords': [
                    r'\bGDPR\b', r'\bdata protection\b', r'\bpersonal data\b',
                    r'\bconsent\b', r'\bdata subject\s+rights\b', r'\bprivacy\b',
                    r'\bICO\b', r'\bUK GDPR\b', r'\bdata controller\b',
                    r'\bdata processor\b', r'\bright to be forgotten\b',
                    r'\bdata portability\b', r'\bprivacy policy\b'
                ],
                'document_types': ['privacy_policy', 'data_processing', 'consent_form'],
                'industries': ['all'],
                'jurisdictions': ['UK', 'EU'],
                'required_triggers': 2,  # Minimum keyword matches
            },
            'gdpr_advanced': {
                'keywords': [
                    r'\bautomated\s+decision', r'\bprofiling\b', r'\bDPIA\b',
                    r'\bdata\s+protection\s+impact', r'\bhigh\s+risk\s+processing\b',
                    r'\bspecial\s+category\s+data\b', r'\bArticle\s+9\b',
                    r'\bdata\s+protection\s+officer\b', r'\bDPO\b'
                ],
                'document_types': ['dpia', 'high_risk_processing'],
                'industries': ['all'],
                'jurisdictions': ['UK', 'EU'],
                'required_triggers': 1,
            },
            'fca_uk': {
                'keywords': [
                    r'\bFCA\b', r'\bFinancial\s+Conduct\s+Authority\b',
                    r'\bauthorised\s+firm\b', r'\bregulated\s+activity\b',
                    r'\bfinancial\s+services\b', r'\bSMCR\b',
                    r'\bSenior\s+Managers\b', r'\bclient\s+assets\b',
                    r'\bTCF\b', r'\bTreating\s+Customers\s+Fairly\b'
                ],
                'document_types': ['financial_policy', 'compliance_manual', 'client_agreement'],
                'industries': ['financial_services', 'banking', 'investment'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'fca_advanced': {
                'keywords': [
                    r'\bcrypto\s+assets\b', r'\bcryptocurrency\b',
                    r'\binvestment\s+advice\b', r'\bportfolio\s+management\b',
                    r'\bmarket\s+abuse\b', r'\bMAR\b',
                    r'\bMiFID\s+II\b', r'\balgorithmic\s+trading\b'
                ],
                'document_types': ['investment_policy', 'trading_manual'],
                'industries': ['investment', 'crypto', 'asset_management'],
                'jurisdictions': ['UK'],
                'required_triggers': 1,
            },
            'hipaa_us': {
                'keywords': [
                    r'\bHIPAA\b', r'\bPHI\b', r'\bprotected\s+health\s+information\b',
                    r'\belectronic\s+health\s+records\b', r'\bEHR\b',
                    r'\bmedical\s+records\b', r'\bhealth\s+data\b',
                    r'\bpatient\s+privacy\b', r'\bHHS\b'
                ],
                'document_types': ['healthcare_policy', 'patient_consent', 'medical_records'],
                'industries': ['healthcare', 'medical'],
                'jurisdictions': ['US'],
                'required_triggers': 2,
            },
            'sox_us': {
                'keywords': [
                    r'\bSarbanes-Oxley\b', r'\bSOX\b', r'\bSection\s+404\b',
                    r'\binternal\s+controls\b', r'\bfinancial\s+reporting\b',
                    r'\bpublic\s+company\b', r'\bPCAOB\b',
                    r'\baudit\s+committee\b', r'\bmaterial\s+weakness\b'
                ],
                'document_types': ['financial_controls', 'audit_report', 'internal_controls'],
                'industries': ['public_company', 'financial_reporting'],
                'jurisdictions': ['US'],
                'required_triggers': 2,
            },
            'pci_dss': {
                'keywords': [
                    r'\bPCI\s+DSS\b', r'\bPCI\b', r'\bpayment\s+card\b',
                    r'\bcardholder\s+data\b', r'\bcard\s+data\b',
                    r'\bcredit\s+card\b', r'\bdebit\s+card\b',
                    r'\bpayment\s+processing\b', r'\bPAN\b'
                ],
                'document_types': ['payment_policy', 'security_policy', 'payment_processing'],
                'industries': ['retail', 'e-commerce', 'payment_processing'],
                'jurisdictions': ['Global'],
                'required_triggers': 2,
            },
            'nda_uk': {
                'keywords': [
                    r'\bnon-disclosure\b', r'\bNDA\b', r'\bconfidential\s+information\b',
                    r'\btrade\s+secrets\b', r'\bproprietary\s+information\b',
                    r'\bconfidentiality\b', r'\brestricted\s+information\b'
                ],
                'document_types': ['nda', 'confidentiality_agreement', 'employment_contract'],
                'industries': ['all'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'tax_uk': {
                'keywords': [
                    r'\bMaking\s+Tax\s+Digital\b', r'\bMTD\b', r'\bHMRC\b',
                    r'\bVAT\b', r'\bvalue\s+added\s+tax\b',
                    r'\btax\s+returns\b', r'\bcorporation\s+tax\b',
                    r'\bself-assessment\b', r'\btax\s+compliance\b'
                ],
                'document_types': ['tax_policy', 'financial_records', 'vat_returns'],
                'industries': ['all'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'hr_scottish': {
                'keywords': [
                    r'\bScottish\s+employment\b', r'\bScots\s+law\b',
                    r'\bemployment\s+contract\b', r'\bScottish\s+tribunal\b',
                    r'\bemployee\s+rights\b', r'\bworkplace\s+rights\b',
                    r'\bScotland\b.*\bemployment\b'
                ],
                'document_types': ['employment_contract', 'hr_policy', 'employee_handbook'],
                'industries': ['all'],
                'jurisdictions': ['Scotland'],
                'required_triggers': 2,
            },
            'uk_employment': {
                'keywords': [
                    r'\bemployment\s+law\b', r'\bemployment\s+contract\b',
                    r'\bemployee\s+rights\b', r'\bemployment\s+tribunal\b',
                    r'\bunfair\s+dismissal\b', r'\bredundancy\b',
                    r'\bworking\s+time\s+regulations\b', r'\bmaternity\b',
                    r'\bpaternity\b', r'\bholiday\s+entitlement\b'
                ],
                'document_types': ['employment_contract', 'hr_policy', 'employee_handbook'],
                'industries': ['all'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'scottish_law': {
                'keywords': [
                    r'\bScots\s+law\b', r'\bScottish\s+legal\b',
                    r'\bCourt\s+of\s+Session\b', r'\bSheriff\s+Court\b',
                    r'\bScottish\s+contract\b', r'\bScottish\s+legislation\b'
                ],
                'document_types': ['legal_contract', 'scottish_agreement'],
                'industries': ['all'],
                'jurisdictions': ['Scotland'],
                'required_triggers': 2,
            },
            'healthcare_uk': {
                'keywords': [
                    r'\bNHS\b', r'\bNational\s+Health\s+Service\b',
                    r'\bCQC\b', r'\bCare\s+Quality\s+Commission\b',
                    r'\bpatient\s+care\b', r'\bmedical\s+records\b',
                    r'\bhealthcare\s+provider\b', r'\bCaldicott\b',
                    r'\bhealth\s+and\s+social\s+care\b'
                ],
                'document_types': ['healthcare_policy', 'patient_care', 'medical_records'],
                'industries': ['healthcare', 'nhs', 'medical'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'finance_industry': {
                'keywords': [
                    r'\bfinancial\s+services\b', r'\bbanking\b',
                    r'\binvestment\b', r'\basset\s+management\b',
                    r'\bfinancial\s+advice\b', r'\bwealth\s+management\b'
                ],
                'document_types': ['financial_policy', 'investment_policy'],
                'industries': ['financial_services', 'banking', 'investment'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
            'education_uk': {
                'keywords': [
                    r'\beducation\b', r'\bschool\b', r'\buniversity\b',
                    r'\bstudent\s+data\b', r'\bpupil\s+data\b',
                    r'\beducational\s+institution\b', r'\blearning\s+records\b',
                    r'\bOfsted\b'
                ],
                'document_types': ['education_policy', 'student_records'],
                'industries': ['education', 'academic'],
                'jurisdictions': ['UK'],
                'required_triggers': 2,
            },
        }

    def recommend(
        self,
        text: str,
        document_type: str,
        organization_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend relevant compliance modules.

        Args:
            text: Document text to analyze
            document_type: Type of document
            organization_profile: Optional organization profile with industry, jurisdiction, etc.

        Returns:
            List of recommended modules with confidence scores and reasons
        """
        logger.info("Starting module recommendation analysis")

        recommendations = []
        text_lower = text.lower()

        # Extract metadata from organization profile
        org_industry = organization_profile.get('industry') if organization_profile else None
        org_jurisdiction = organization_profile.get('jurisdiction') if organization_profile else None
        org_size = organization_profile.get('size') if organization_profile else None

        # Analyze each module
        for module_id, patterns in self.detection_patterns.items():
            confidence = self._calculate_confidence(
                text_lower,
                document_type,
                patterns,
                org_industry,
                org_jurisdiction
            )

            if confidence >= 0.3:  # Threshold for recommendation
                triggers = self._extract_triggers(text_lower, patterns['keywords'])

                recommendation = {
                    'module_id': module_id,
                    'module_name': self.modules[module_id].name,
                    'confidence': confidence,
                    'reason': self._generate_reason(module_id, triggers, confidence, org_industry),
                    'triggers': triggers,
                    'priority': self._determine_priority(confidence, module_id),
                    'estimated_impact': self._estimate_impact(module_id, org_size),
                    'implementation_time': self.modules[module_id].implementation_time_days,
                    'complexity': self.modules[module_id].complexity_score
                }
                recommendations.append(recommendation)

        # Sort by confidence and priority
        recommendations.sort(key=lambda x: (
            {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            x['confidence']
        ), reverse=True)

        logger.info(f"Recommended {len(recommendations)} modules")
        return recommendations

    def _calculate_confidence(
        self,
        text: str,
        document_type: str,
        patterns: Dict[str, Any],
        org_industry: Optional[str],
        org_jurisdiction: Optional[str]
    ) -> float:
        """Calculate confidence score for module recommendation."""
        confidence = 0.0

        # Keyword matching (0.0 - 0.5)
        keyword_matches = sum(1 for keyword in patterns['keywords'] if re.search(keyword, text, re.IGNORECASE))
        required_triggers = patterns.get('required_triggers', 1)

        if keyword_matches >= required_triggers:
            keyword_confidence = min(0.5, (keyword_matches / len(patterns['keywords'])) * 0.7)
            confidence += keyword_confidence

        # Document type matching (0.0 - 0.2)
        if document_type in patterns['document_types'] or 'all' in patterns['document_types']:
            confidence += 0.2

        # Industry matching (0.0 - 0.2)
        if org_industry:
            if org_industry in patterns['industries'] or 'all' in patterns['industries']:
                confidence += 0.2

        # Jurisdiction matching (0.0 - 0.1)
        if org_jurisdiction:
            if org_jurisdiction in patterns['jurisdictions'] or 'Global' in patterns['jurisdictions']:
                confidence += 0.1

        return min(1.0, confidence)

    def _extract_triggers(self, text: str, keywords: List[str]) -> List[str]:
        """Extract triggering keywords found in text."""
        triggers = []
        for keyword in keywords:
            if re.search(keyword, text, re.IGNORECASE):
                # Clean up regex pattern for display
                clean_keyword = re.sub(r'[\\^$.*+?{}[\]|()\s]+', ' ', keyword).strip()
                triggers.append(clean_keyword)
        return triggers[:5]  # Limit to 5 for readability

    def _generate_reason(
        self,
        module_id: str,
        triggers: List[str],
        confidence: float,
        org_industry: Optional[str]
    ) -> str:
        """Generate human-readable reason for recommendation."""
        reasons = {
            'gdpr_uk': "Document contains personal data processing terminology requiring GDPR compliance",
            'gdpr_advanced': "High-risk data processing detected requiring advanced GDPR measures",
            'fca_uk': "Financial services activity detected requiring FCA authorization",
            'fca_advanced': "Complex financial services requiring advanced FCA compliance",
            'hipaa_us': "Protected health information (PHI) detected requiring HIPAA compliance",
            'sox_us': "Financial reporting controls requiring SOX compliance",
            'pci_dss': "Payment card data handling requiring PCI-DSS compliance",
            'nda_uk': "Confidential information handling requiring NDA protection",
            'tax_uk': "Tax obligations requiring HMRC compliance",
            'hr_scottish': "Scottish employment law applies to this document",
            'uk_employment': "UK employment law requirements detected",
            'scottish_law': "Scottish legal framework applies",
            'healthcare_uk': "UK healthcare regulations (NHS/CQC) apply",
            'finance_industry': "Financial industry standards apply",
            'education_uk': "UK education sector regulations apply",
        }

        base_reason = reasons.get(module_id, "Compliance requirements detected")

        if triggers:
            trigger_text = ', '.join(triggers[:3])
            return f"{base_reason}. Key indicators: {trigger_text}"

        return base_reason

    def _determine_priority(self, confidence: float, module_id: str) -> str:
        """Determine priority level based on confidence and module criticality."""
        critical_modules = ['gdpr_uk', 'gdpr_advanced', 'fca_uk', 'hipaa_us', 'pci_dss']

        if confidence >= 0.8:
            return 'critical'
        elif confidence >= 0.6:
            return 'high' if module_id in critical_modules else 'medium'
        elif confidence >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _estimate_impact(self, module_id: str, org_size: Optional[str]) -> str:
        """Estimate implementation impact based on module and organization size."""
        high_impact_modules = ['gdpr_advanced', 'fca_uk', 'fca_advanced', 'sox_us', 'pci_dss']
        medium_impact_modules = ['gdpr_uk', 'hipaa_us', 'healthcare_uk']

        if org_size == 'enterprise':
            if module_id in high_impact_modules:
                return 'Very High - Requires dedicated team and significant resources'
            elif module_id in medium_impact_modules:
                return 'High - Requires cross-functional coordination'
            else:
                return 'Medium - Manageable with existing resources'
        elif org_size == 'medium':
            if module_id in high_impact_modules:
                return 'High - May require external consultants'
            elif module_id in medium_impact_modules:
                return 'Medium - Requires focused effort'
            else:
                return 'Low - Can be handled internally'
        else:  # small or unknown
            if module_id in high_impact_modules:
                return 'Very High - Consider external compliance support'
            elif module_id in medium_impact_modules:
                return 'High - Significant undertaking for small organization'
            else:
                return 'Medium - Achievable with dedicated effort'

    def get_module_dependencies(self, module_ids: List[str]) -> Dict[str, List[str]]:
        """Get dependencies between recommended modules."""
        dependencies = {}

        for module_id in module_ids:
            if module_id in self.modules:
                module = self.modules[module_id]
                deps = {
                    'required_by': module.required_by,
                    'complements': module.complements,
                    'conflicts_with': module.conflicts_with
                }
                dependencies[module_id] = deps

        return dependencies

    def suggest_module_combinations(
        self,
        recommended_modules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest optimal combinations of modules to implement together."""
        combinations = []

        module_ids = [m['module_id'] for m in recommended_modules]

        # GDPR combinations
        if 'gdpr_uk' in module_ids:
            combo = {
                'name': 'GDPR Foundation Package',
                'modules': ['gdpr_uk'],
                'reason': 'Essential data protection compliance for UK organizations',
                'priority': 'critical'
            }
            if 'gdpr_advanced' in module_ids:
                combo['modules'].append('gdpr_advanced')
                combo['reason'] += ' with advanced processing capabilities'
            combinations.append(combo)

        # Financial services combinations
        if 'fca_uk' in module_ids:
            combo = {
                'name': 'Financial Services Compliance Package',
                'modules': ['fca_uk'],
                'reason': 'Core financial conduct requirements',
                'priority': 'critical'
            }
            if 'fca_advanced' in module_ids:
                combo['modules'].append('fca_advanced')
            if 'gdpr_uk' in module_ids:
                combo['modules'].append('gdpr_uk')
                combo['reason'] += ' with data protection'
            combinations.append(combo)

        # Healthcare combinations
        if 'healthcare_uk' in module_ids or 'hipaa_us' in module_ids:
            combo = {
                'name': 'Healthcare Compliance Package',
                'modules': [],
                'reason': 'Healthcare data protection and patient care standards',
                'priority': 'critical'
            }
            if 'healthcare_uk' in module_ids:
                combo['modules'].append('healthcare_uk')
            if 'hipaa_us' in module_ids:
                combo['modules'].append('hipaa_us')
            if 'gdpr_uk' in module_ids:
                combo['modules'].append('gdpr_uk')
            combinations.append(combo)

        # Employment combinations
        if 'uk_employment' in module_ids or 'hr_scottish' in module_ids:
            combo = {
                'name': 'Employment Law Package',
                'modules': [],
                'reason': 'Comprehensive employment law compliance',
                'priority': 'high'
            }
            if 'uk_employment' in module_ids:
                combo['modules'].append('uk_employment')
            if 'hr_scottish' in module_ids:
                combo['modules'].append('hr_scottish')
            if 'gdpr_uk' in module_ids:
                combo['modules'].append('gdpr_uk')
            combinations.append(combo)

        return combinations


# Testing and validation
def test_module_recommender():
    """Test the module recommender with sample documents."""
    from backend.compliance.orchestrator import ComplianceOrchestrator

    orchestrator = ComplianceOrchestrator()
    recommender = ModuleRecommender(orchestrator.modules)

    # Test 1: GDPR document
    gdpr_text = """
    Privacy Policy - Data Protection Notice

    We process personal data in accordance with UK GDPR and the Data Protection Act 2018.
    This includes collecting consent for data processing, ensuring data subject rights,
    and implementing appropriate security measures. Data subjects have the right to access,
    rectification, erasure, and data portability.
    """
    results = recommender.recommend(gdpr_text, 'privacy_policy')
    assert any(r['module_id'] == 'gdpr_uk' for r in results), "Should recommend GDPR UK module"
    print(" GDPR detection test passed")

    # Test 2: Financial services document
    fca_text = """
    FCA Compliance Manual for Authorised Firms

    This manual covers regulatory requirements for firms authorized by the Financial Conduct Authority.
    It includes client assets protection, SMCR requirements, and Treating Customers Fairly (TCF) principles.
    """
    results = recommender.recommend(fca_text, 'compliance_manual')
    assert any(r['module_id'] == 'fca_uk' for r in results), "Should recommend FCA UK module"
    print(" FCA detection test passed")

    # Test 3: Healthcare document
    healthcare_text = """
    NHS Patient Care Policy

    This policy ensures compliance with CQC fundamental standards and Caldicott principles.
    All patient medical records will be handled in accordance with NHS information governance
    requirements and stored securely for the required retention period.
    """
    results = recommender.recommend(healthcare_text, 'healthcare_policy')
    assert any(r['module_id'] == 'healthcare_uk' for r in results), "Should recommend Healthcare UK module"
    print(" Healthcare detection test passed")

    # Test 4: Multi-module document
    multi_text = """
    Employee Data Protection and Payment Processing Policy

    This policy covers GDPR compliance for employee personal data, PCI-DSS requirements
    for payment card processing, and UK employment law obligations. All data must be
    processed with consent and stored securely.
    """
    results = recommender.recommend(multi_text, 'policy')
    assert len(results) >= 2, "Should recommend multiple modules"
    print(" Multi-module detection test passed")

    print("\nAll module recommender tests passed!")
    return True


if __name__ == "__main__":
    test_module_recommender()
