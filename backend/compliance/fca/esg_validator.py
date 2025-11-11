"""
FCA ESG and Greenwashing Detection Module
Implements FCA guidance on ESG claims and SDR (Sustainability Disclosure Requirements)

Legal References:
- FG21/1: Guiding firms on the fair treatment of vulnerable customers
- PS23/16: Sustainability Disclosure Requirements (SDR) and investment labels
- Discussion Paper DP21/4: Sustainability Disclosure Requirements
- Effective from July 31, 2024
"""

import re
from typing import Dict, List, Tuple


class ESGGreenwashingDetector:
    """
    Detects greenwashing and validates ESG claims
    FCA defines greenwashing as: misleading sustainability claims
    """

    def __init__(self):
        self.name = "esg_greenwashing"
        self.legal_source = "FCA PS23/16 (SDR) & FG21/1"

    def check_esg_claims(self, text: str) -> Dict:
        """Main ESG claims validation"""
        text_lower = text.lower()

        # Determine if document makes ESG claims
        if not self._has_esg_claims(text):
            return {
                'status': 'N/A',
                'message': 'No ESG claims detected',
                'legal_source': self.legal_source
            }

        results = {
            'unsubstantiated_claims': self.check_unsubstantiated_claims(text),
            'vague_language': self.check_vague_language(text),
            'investment_labels': self.check_investment_labels(text),
            'evidence_backing': self.check_evidence_backing(text),
            'metrics_disclosure': self.check_metrics_disclosure(text),
            'exclusion_clarity': self.check_exclusion_clarity(text),
            'carbon_claims': self.check_carbon_claims(text),
            'impact_claims': self.check_impact_claims(text)
        }

        failures = [k for k, v in results.items() if v['status'] == 'FAIL']
        warnings = [k for k, v in results.items() if v['status'] == 'WARNING']

        overall_status = 'PASS'
        overall_severity = 'none'

        if failures:
            overall_status = 'FAIL'
            overall_severity = 'critical'
        elif warnings:
            overall_status = 'WARNING'
            overall_severity = 'medium'

        return {
            'status': overall_status,
            'severity': overall_severity,
            'message': f'ESG/Greenwashing: {len(failures)} failures, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings
        }

    def _has_esg_claims(self, text: str) -> bool:
        """Detect if document makes ESG/sustainability claims"""
        esg_terms = [
            r'\besg\b',
            r'(?:environmental|social|governance)',
            r'sustainab(?:le|ility)',
            r'(?:green|ethical)\s+(?:investment|fund|product)',
            r'(?:carbon|climate)[- ](?:neutral|positive|friendly)',
            r'(?:net[- ]zero|carbon[- ]offset)',
            r'(?:renewable|clean)\s+energy',
            r'social(?:ly)?\s+responsible',
            r'impact\s+(?:investment|investing)',
            r'(?:un\s+)?sdg',  # UN Sustainable Development Goals
            r'paris\s+agreement',
            r'biodiversity',
            r'circular\s+economy'
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in esg_terms)

    def check_unsubstantiated_claims(self, text: str) -> Dict:
        """Check for unsubstantiated ESG claims"""
        unsubstantiated_patterns = [
            r'\b(?:100%|completely|fully|totally)\s+(?:sustainable|green|carbon[- ]neutral|ethical)',
            r'\b(?:most|best|leading)\s+(?:sustainable|green|ethical)',
            r'(?:guaranteed|promise|ensure).*(?:positive\s+impact|sustainable|green)',
            r'(?:always|never).*(?:harm|damage|negative)',
            r'perfect.*(?:esg|sustainability)\s+(?:score|rating)',
            r'zero\s+(?:impact|footprint|harm)(?!\s+(?:target|goal|ambition))'  # Allow "zero target"
        ]

        issues = []
        spans = []

        for pattern in unsubstantiated_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for m in matches:
                issues.append(f'Unsubstantiated claim: "{m.group()}"')
                spans.append({
                    'type': 'unsubstantiated_esg_claim',
                    'text': m.group(),
                    'severity': 'critical'
                })

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Unsubstantiated ESG claims detected',
                'legal_source': 'FCA PS23/16 (Anti-greenwashing rule)',
                'suggestion': 'Remove absolute or superlative claims unless backed by verifiable evidence',
                'issues': issues,
                'spans': spans
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No unsubstantiated claims detected',
            'legal_source': 'FCA PS23/16'
        }

    def check_vague_language(self, text: str) -> Dict:
        """Check for vague ESG language without specificity"""
        vague_terms = [
            r'\b(?:eco[- ]friendly|green)\b(?!\s+(?:bond|finance|energy|building|certification))',
            r'sustainab(?:le|ility)(?!\s+(?:fund|investment|strategy|policy|report|framework))',
            r'responsible\s+(?:investment|investing)(?!\s+(?:policy|framework|strategy))',
            r'ethical(?!\s+(?:policy|framework|screening|criteria))',
            r'positive\s+impact(?!\s+(?:strategy|measurement|metric))',
            r'(?:good|better)\s+for\s+(?:the\s+)?(?:planet|environment|society)'
        ]

        vague_count = 0
        examples = []

        for pattern in vague_terms:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            vague_count += len(matches)
            for m in matches[:2]:  # Limit examples
                examples.append(m.group())

        if vague_count >= 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Vague ESG language detected ({vague_count} instances)',
                'legal_source': 'FCA PS23/16 (Clarity requirement)',
                'suggestion': 'Replace vague terms with specific, measurable ESG criteria and metrics',
                'examples': examples
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'ESG language is specific',
            'legal_source': 'FCA PS23/16'
        }

    def check_investment_labels(self, text: str) -> Dict:
        """
        Check FCA sustainability labels usage
        Labels: Sustainability Focus, Sustainability Improvers, Sustainability Impact, Sustainability Mixed Goals
        """
        # Check for label claims
        label_patterns = [
            r'sustainability\s+(?:focus|improvers?|impact|mixed\s+goals)',
            r'(?:fca|uk)\s+(?:sustainability|esg)\s+label'
        ]

        has_label_claim = any(re.search(p, text, re.IGNORECASE) for p in label_patterns)

        if not has_label_claim:
            return {
                'status': 'N/A',
                'message': 'No FCA sustainability labels claimed',
                'legal_source': 'FCA PS23/16'
            }

        # If label claimed, check for required disclosures
        required_disclosures = {
            'investment_policy': r'(?:investment|sustainability)\s+policy',
            'objectives': r'(?:objective|goal|aim)s?',
            'metrics': r'(?:metric|measure|kpi|indicator)s?',
            'reporting': r'(?:report|reporting|disclosure).*(?:annual|regular|periodic)'
        }

        missing_disclosures = []
        for disclosure, pattern in required_disclosures.items():
            if not re.search(pattern, text, re.IGNORECASE):
                missing_disclosures.append(disclosure)

        if missing_disclosures:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'FCA label used without required disclosures',
                'legal_source': 'FCA PS23/16 (Label disclosure requirements)',
                'suggestion': f'When using FCA sustainability labels, must disclose: {", ".join(missing_disclosures)}',
                'missing': missing_disclosures
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'FCA sustainability label disclosures present',
            'legal_source': 'FCA PS23/16'
        }

    def check_evidence_backing(self, text: str) -> Dict:
        """Check if ESG claims are backed by evidence"""
        # Look for evidence/verification mentions
        evidence_patterns = [
            r'(?:verified|validated|certified)\s+by',
            r'(?:third[- ]party|independent)\s+(?:verification|audit|assessment)',
            r'(?:msci|sustainalytics|cdp|gri|tcfd)\s+(?:rating|score|assessment)',
            r'(?:carbon|sustainability)\s+(?:report|disclosure)',
            r'(?:science[- ]based|sbti)\s+target',
            r'(?:b\s+corp|bcorp)\s+certified',
            r'iso\s+14001',
            r'(?:data|evidence)\s+(?:available|provided|disclosed)'
        ]

        has_evidence = any(re.search(p, text, re.IGNORECASE) for p in evidence_patterns)

        # Count ESG claims
        claim_patterns = [
            r'reduce(?:s|d|ing)?\s+(?:carbon|emissions|waste)',
            r'improv(?:e|es|ed|ing)\s+(?:biodiversity|social|governance)',
            r'support(?:s|ed|ing)?\s+(?:renewable|clean|sustainable)',
            r'contribut(?:e|es|ed|ing)\s+to\s+(?:sdg|net[- ]zero|climate)'
        ]

        claim_count = sum(len(list(re.finditer(p, text, re.IGNORECASE))) for p in claim_patterns)

        if claim_count > 2 and not has_evidence:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Multiple ESG claims ({claim_count}) without evidence/verification',
                'legal_source': 'FCA PS23/16 (Anti-greenwashing)',
                'suggestion': 'Provide evidence: third-party verification, ESG ratings, certifications, or data sources'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'ESG claims appear to be evidence-backed',
            'legal_source': 'FCA PS23/16'
        }

    def check_metrics_disclosure(self, text: str) -> Dict:
        """Check if quantitative ESG metrics are disclosed"""
        # Look for quantitative metrics
        metric_patterns = [
            r'\d+%\s+(?:reduction|decrease|improvement)',
            r'\d+\s+(?:tonnes?|tons?|kg)\s+(?:co2|carbon|ghg)',
            r'scope\s+[123]\s+emissions',
            r'\d+\s+(?:mw|gwh|kwh)',
            r'(?:carbon|esg)\s+(?:score|rating):\s*\d+',
            r'\d+%\s+(?:renewable|clean)\s+energy'
        ]

        has_metrics = any(re.search(p, text, re.IGNORECASE) for p in metric_patterns)

        # If making climate/carbon claims, metrics are important
        climate_claim_patterns = [
            r'(?:carbon|climate)[- ](?:neutral|positive)',
            r'net[- ]zero',
            r'reduce.*emissions'
        ]

        makes_climate_claims = any(re.search(p, text, re.IGNORECASE) for p in climate_claim_patterns)

        if makes_climate_claims and not has_metrics:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Climate claims without quantitative metrics',
                'legal_source': 'FCA PS23/16 & TCFD',
                'suggestion': 'Provide quantitative metrics: emissions data, reduction targets, timelines'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Metrics disclosure adequate',
            'legal_source': 'FCA PS23/16'
        }

    def check_exclusion_clarity(self, text: str) -> Dict:
        """Check clarity of investment exclusions"""
        exclusion_patterns = [
            r'exclud(?:e|es|ing|ed)',
            r'do\s+not\s+invest\s+in',
            r'no\s+(?:investment|exposure)\s+(?:in|to)',
            r'avoid.*(?:sector|industry|company)'
        ]

        has_exclusions = any(re.search(p, text, re.IGNORECASE) for p in exclusion_patterns)

        if not has_exclusions:
            return {
                'status': 'N/A',
                'message': 'No exclusions claimed',
                'legal_source': 'FCA PS23/16'
            }

        # If exclusions mentioned, check for specificity
        specific_patterns = [
            r'(?:fossil\s+fuel|coal|oil|gas)',
            r'(?:tobacco|alcohol|gambling|weapons)',
            r'(?:thermal\s+coal|tar\s+sands)',
            r'controversi(?:al|es)\s+(?:weapons|activities)',
            r'un\s+global\s+compact',
            r'international\s+(?:norm|standard)s?'
        ]

        is_specific = any(re.search(p, text, re.IGNORECASE) for p in specific_patterns)

        if not is_specific:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Exclusions mentioned but not specific',
                'legal_source': 'FCA PS23/16',
                'suggestion': 'Specify exactly what is excluded (e.g., fossil fuels, tobacco, weapons)'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Exclusions clearly specified',
            'legal_source': 'FCA PS23/16'
        }

    def check_carbon_claims(self, text: str) -> Dict:
        """Specific validation for carbon/climate claims"""
        carbon_claims = {
            'carbon_neutral': r'carbon[- ]neutral',
            'net_zero': r'net[- ]zero',
            'carbon_negative': r'(?:carbon|climate)[- ](?:negative|positive)',
            'carbon_offset': r'carbon\s+offset',
            'climate_friendly': r'climate[- ]friendly'
        }

        found_claims = []
        for claim_type, pattern in carbon_claims.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_claims.append(claim_type)

        if not found_claims:
            return {
                'status': 'N/A',
                'message': 'No carbon claims made',
                'legal_source': 'FCA PS23/16'
            }

        # Check for required carbon disclosures
        carbon_disclosures = [
            r'scope\s+[123]\s+emissions',
            r'ghg\s+(?:protocol|inventory|emissions)',
            r'carbon\s+(?:footprint|baseline)',
            r'(?:verified|certified).*(?:carbon|emissions)',
            r'(?:reduction\s+)?(?:target|goal).*\d+%'
        ]

        has_disclosures = any(re.search(p, text, re.IGNORECASE) for p in carbon_disclosures)

        if not has_disclosures:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Carbon claims ({", ".join(found_claims)}) without proper disclosure',
                'legal_source': 'FCA PS23/16 & TCFD',
                'suggestion': 'Carbon claims require: emissions scope, baseline, targets, methodology, verification',
                'claims': found_claims
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Carbon claims properly disclosed',
            'legal_source': 'FCA PS23/16',
            'claims': found_claims
        }

    def check_impact_claims(self, text: str) -> Dict:
        """Validate impact investment claims"""
        impact_patterns = [
            r'(?:positive\s+)?impact\s+(?:investment|investing|fund)',
            r'measurable\s+(?:positive\s+)?impact',
            r'(?:social|environmental)\s+impact',
            r'impact\s+(?:objective|goal|outcome)'
        ]

        makes_impact_claim = any(re.search(p, text, re.IGNORECASE) for p in impact_patterns)

        if not makes_impact_claim:
            return {
                'status': 'N/A',
                'message': 'No impact investment claims',
                'legal_source': 'FCA PS23/16'
            }

        # For impact claims, need impact measurement framework
        impact_frameworks = [
            r'impact\s+(?:measurement|metric|indicator|reporting)',
            r'theory\s+of\s+change',
            r'(?:iris|giirs|giin)\s+(?:metric|framework)',
            r'impact\s+management\s+project',
            r'sdg\s+(?:alignment|contribution|mapping)',
            r'impact\s+report(?:ing)?'
        ]

        has_framework = any(re.search(p, text, re.IGNORECASE) for p in impact_frameworks)

        if not has_framework:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Impact claims without measurement framework',
                'legal_source': 'FCA PS23/16 (Sustainability Impact label requirements)',
                'suggestion': 'Impact claims require: defined theory of change, measurable outcomes, impact metrics, reporting'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Impact investment claims properly supported',
            'legal_source': 'FCA PS23/16'
        }
