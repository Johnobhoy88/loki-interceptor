import re


class IndependentAdviceGate:
    def __init__(self):
        self.name = "independent_advice"
        self.severity = "high"
        self.legal_source = "Settlement Agreement Regulations 2013, Section 203 ERA 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['settlement', 'compromise', 'termination', 'exit'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not appear to be a settlement agreement',
                'legal_source': self.legal_source
            }

        # Check if this is a settlement/compromise agreement
        settlement_patterns = [
            r'settlement\s+agreement',
            r'compromise\s+agreement',
            r'(?:employment|statutory)\s+rights',
            r'waiver\s+of.*(?:claims|rights)'
        ]

        is_settlement = any(re.search(p, text, re.IGNORECASE) for p in settlement_patterns)

        if not is_settlement:
            return {
                'status': 'N/A',
                'message': 'Not a settlement agreement',
                'legal_source': self.legal_source
            }

        # Check for independent legal advice requirement
        advice_patterns = [
            r'independent\s+(?:legal\s+)?advi(?:ce|sor)',
            r'relevant\s+independent\s+adviser',
            r'solicitor.*advise[dr]',
            r'legal\s+advice.*independent',
            r'adviser.*insurance.*force'
        ]

        has_advice_clause = any(re.search(p, text, re.IGNORECASE) for p in advice_patterns)

        # Check for adviser certificate/confirmation
        certificate_patterns = [
            r'certificate.*independent\s+adviser',
            r'adviser.*confirms?.*advice',
            r'solicitor.*certif(?:y|ies|icate)',
            r'I.*confirm.*advice.*given'
        ]

        has_certificate = any(re.search(p, text, re.IGNORECASE) for p in certificate_patterns)

        # Check for insurance requirement
        insurance_pattern = r'professional\s+indemnity\s+insurance'
        has_insurance = re.search(insurance_pattern, text, re.IGNORECASE)

        if has_advice_clause and has_certificate and has_insurance:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Independent legal advice requirements properly documented',
                'legal_source': self.legal_source
            }

        if not has_advice_clause:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Settlement agreement lacks independent legal advice requirement',
                'legal_source': self.legal_source,
                'suggestion': 'Add clause requiring independent legal advice from qualified adviser with professional indemnity insurance per Section 203 ERA 1996',
                'penalty': 'Agreement is void and unenforceable; employee retains all statutory rights'
            }

        if not has_certificate:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No adviser certificate or confirmation clause',
                'legal_source': self.legal_source,
                'suggestion': 'Include section for adviser to certify that advice has been provided'
            }

        if not has_insurance:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'No reference to adviser professional indemnity insurance',
                'legal_source': self.legal_source,
                'suggestion': 'Confirm adviser has professional indemnity insurance in force'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Independent advice provisions incomplete',
            'legal_source': self.legal_source
        }
