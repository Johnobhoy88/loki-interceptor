"""
Scottish Employment Law Compliance Gate

Checks for Scotland-specific employment law differences:
- Employment Tribunal Scotland procedures
- ACAS Scotland guidance
- 5-year prescription period (vs 6-year in England)
- Scots law employment contract differences
"""

import re


class ScottishEmploymentGate:
    def __init__(self):
        self.name = "scottish_employment"
        self.severity = "high"
        self.legal_source = "Prescription and Limitation (Scotland) Act 1973; Employment Tribunals (Scotland) Regulations 2013"

    def _is_relevant(self, text):
        """Check if document is Scottish employment-related"""
        text_lower = (text or '').lower()
        is_scottish = any([
            'scotland' in text_lower,
            'scots law' in text_lower,
            'scottish' in text_lower,
            re.search(r'\bscot(?:land|tish)\b', text_lower)
        ])
        is_employment = any([
            'employment' in text_lower,
            'employee' in text_lower,
            'employer' in text_lower,
            'contract of service' in text_lower,
            'dismissal' in text_lower,
            'redundancy' in text_lower,
            'tribunal' in text_lower
        ])
        return is_scottish and is_employment

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to Scottish employment law'
            }

        issues = []
        corrections = []

        # 1. Check for incorrect tribunal references
        english_tribunal_refs = [
            r'employment\s+tribunal(?!\s+(?:scotland|for\s+scotland))',
            r'ET\s+(?:england|wales)',
            r'employment\s+appeal\s+tribunal(?!\s+scotland)'
        ]

        for pattern in english_tribunal_refs:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append("Document references Employment Tribunal without Scotland specification")
                corrections.append({
                    'type': 'tribunal_reference',
                    'suggestion': 'Use "Employment Tribunal Scotland" or "Employment Tribunal (Scotland)" for Scottish claims',
                    'citation': 'Employment Tribunals (Scotland) Regulations 2013'
                })
                break

        # 2. Check for ACAS references without Scotland specification
        if re.search(r'\bACAS\b(?!\s+scotland)', text, re.IGNORECASE):
            acas_scotland_mentioned = re.search(r'acas\s+scotland', text, re.IGNORECASE)
            if not acas_scotland_mentioned:
                issues.append("ACAS referenced without Scotland specification")
                corrections.append({
                    'type': 'acas_reference',
                    'suggestion': 'Reference "ACAS Scotland" for Scottish employment matters - ACAS Scotland provides Scotland-specific guidance',
                    'citation': 'ACAS Scotland (separate organization from ACAS England & Wales)'
                })

        # 3. Check for 6-year limitation period (incorrect in Scotland)
        six_year_pattern = r'(?:within\s+)?(?:six|6)[\s-]year(?:s)?(?:\s+(?:period|limitation|time\s+limit))'
        if re.search(six_year_pattern, text, re.IGNORECASE):
            context = re.search(r'.{0,50}' + six_year_pattern + r'.{0,50}', text, re.IGNORECASE)
            if context and 'contract' in context.group().lower():
                issues.append("Six-year limitation period stated (incorrect for Scotland)")
                corrections.append({
                    'type': 'prescription_period',
                    'suggestion': 'Scotland uses a 5-year prescription period for contractual claims, not 6 years',
                    'correction': 'Replace "six years" or "6 years" with "five years" or "5 years"',
                    'citation': 'Prescription and Limitation (Scotland) Act 1973, s.6'
                })

        # 4. Check for incorrect prescription terminology
        if re.search(r'\blimitation\s+(?:period|act)\b', text, re.IGNORECASE):
            issues.append("English 'limitation' terminology used instead of Scots 'prescription'")
            corrections.append({
                'type': 'terminology',
                'suggestion': 'Scots law uses "prescription" not "limitation" for time limits on claims',
                'correction': 'Replace "limitation period" with "prescription period"',
                'citation': 'Prescription and Limitation (Scotland) Act 1973'
            })

        # 5. Check for constructive dismissal references
        if re.search(r'constructive\s+dismissal', text, re.IGNORECASE):
            # Check if Scottish case law is referenced
            scottish_case_law = re.search(r'(?:west\s+midlands|scottish\s+coal)', text, re.IGNORECASE)
            if not scottish_case_law:
                corrections.append({
                    'type': 'case_law_suggestion',
                    'suggestion': 'For Scottish constructive dismissal claims, consider citing relevant Scottish precedents',
                    'citation': 'West Midlands Co-operative Society Ltd v Tipton [1986]; Scottish case law applies'
                })

        # 6. Check for employment contract formation terms
        if re.search(r'offer\s+and\s+acceptance', text, re.IGNORECASE):
            issues.append("English contract formation terminology may not apply in Scotland")
            corrections.append({
                'type': 'contract_formation',
                'suggestion': 'Scots law uses "consensus in idem" (meeting of minds) rather than strict offer and acceptance',
                'citation': 'Scots contract law - consensus in idem principle'
            })

        # 7. Check for Early Conciliation requirements
        if re.search(r'early\s+conciliation', text, re.IGNORECASE):
            if not re.search(r'acas\s+scotland', text, re.IGNORECASE):
                corrections.append({
                    'type': 'early_conciliation',
                    'suggestion': 'Early Conciliation in Scotland is handled by ACAS Scotland, not ACAS England & Wales',
                    'citation': 'ACAS Scotland Early Conciliation Service'
                })

        # 8. Check for unfair dismissal time limits
        unfair_dismissal_mentioned = re.search(r'unfair\s+dismissal', text, re.IGNORECASE)
        three_months_mentioned = re.search(r'(?:three|3)\s+months?(?:\s+less\s+one\s+day)?', text, re.IGNORECASE)

        if unfair_dismissal_mentioned and not three_months_mentioned:
            corrections.append({
                'type': 'time_limit_reminder',
                'suggestion': 'Ensure unfair dismissal claim time limit is stated: 3 months less one day from effective date of termination (same as England)',
                'citation': 'Employment Rights Act 1996, s.111(2) (applies to Scotland)'
            })

        # 9. Scottish-specific employment protections
        if re.search(r'zero[\s-]hours?\s+contract', text, re.IGNORECASE):
            if not re.search(r'exclusivity|exclusive\s+services', text, re.IGNORECASE):
                corrections.append({
                    'type': 'zero_hours_protection',
                    'suggestion': 'Zero-hours contracts in Scotland: exclusivity clauses are unenforceable',
                    'citation': 'Employment Rights Act 1996, s.27A (applies throughout UK including Scotland)'
                })

        # Compile final result
        if issues:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': f"Scottish employment law issues detected: {'; '.join(issues)}",
                'legal_source': self.legal_source,
                'corrections': corrections,
                'issues': issues
            }
        elif corrections:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Scottish employment law guidance applicable',
                'legal_source': self.legal_source,
                'corrections': corrections
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Scottish employment law compliance checks passed',
            'legal_source': self.legal_source
        }


# Test cases
TEST_CASES = [
    {
        'name': 'Scottish employment with 6-year limitation',
        'text': 'This employment contract is governed by Scots law. Claims must be brought within six years.',
        'expected_status': 'FAIL',
        'expected_issues': ['Six-year limitation period']
    },
    {
        'name': 'Correct Scottish employment reference',
        'text': 'Employment Tribunal Scotland handles claims. ACAS Scotland provides early conciliation. Claims have a 5-year prescription period under Scots law.',
        'expected_status': 'PASS'
    },
    {
        'name': 'English tribunal reference in Scottish context',
        'text': 'This Scottish employment contract may be subject to Employment Tribunal proceedings.',
        'expected_status': 'FAIL',
        'expected_issues': ['Employment Tribunal without Scotland specification']
    },
    {
        'name': 'ACAS without Scotland specification',
        'text': 'Scottish employees should contact ACAS for early conciliation before tribunal claims.',
        'expected_status': 'FAIL',
        'expected_issues': ['ACAS referenced without Scotland specification']
    },
    {
        'name': 'Unfair dismissal in Scotland',
        'text': 'Unfair dismissal claims in Scotland must be lodged with Employment Tribunal Scotland within 3 months less one day.',
        'expected_status': 'PASS'
    }
]
