"""
Scottish Corporate Law Compliance Gate

Checks for Scotland-specific corporate law differences:
- Companies House Scotland procedures
- Scottish charities (OSCR - Office of the Scottish Charity Regulator)
- Community Interest Companies (CICs) in Scotland
- Scottish Limited Partnerships
"""

import re


class ScottishCorporateGate:
    def __init__(self):
        self.name = "scottish_corporate"
        self.severity = "medium"
        self.legal_source = "Companies Act 2006; Charities and Trustee Investment (Scotland) Act 2005; Limited Partnerships Act 1907"

    def _is_relevant(self, text):
        """Check if document relates to Scottish corporate matters"""
        text_lower = (text or '').lower()
        is_scottish = any([
            'scotland' in text_lower,
            'scottish' in text_lower,
            'scots law' in text_lower
        ])
        is_corporate = any([
            'company' in text_lower,
            'limited' in text_lower,
            'ltd' in text_lower,
            'plc' in text_lower,
            'charity' in text_lower,
            'charitable' in text_lower,
            'community interest company' in text_lower,
            'cic' in text_lower,
            'partnership' in text_lower,
            'incorporation' in text_lower,
            'director' in text_lower,
            'registered office' in text_lower
        ])
        return is_scottish and is_corporate

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to Scottish corporate law'
            }

        issues = []
        corrections = []

        # 1. Check for Companies House references
        companies_house = re.search(r'Companies\s+House', text, re.IGNORECASE)
        if companies_house:
            # Check if Scottish context is specified
            scottish_office = re.search(r'Companies\s+House.*Scotland|Edinburgh.*Companies\s+House', text, re.IGNORECASE)
            if not scottish_office:
                corrections.append({
                    'type': 'companies_house_scotland',
                    'suggestion': 'Scottish companies can file with Companies House Edinburgh office (though it\'s part of UK-wide Companies House)',
                    'citation': 'Companies Act 2006 - applies throughout UK'
                })

        # 2. Check for charity references
        charity_mentioned = re.search(r'\bcharit(?:y|ies|able)\b', text, re.IGNORECASE)
        charity_commission = re.search(r'Charity\s+Commission', text, re.IGNORECASE)

        if charity_mentioned and charity_commission:
            issues.append("English Charity Commission referenced in Scottish charity context")
            corrections.append({
                'type': 'charity_regulator',
                'suggestion': 'Scottish charities are regulated by OSCR (Office of the Scottish Charity Regulator), not the Charity Commission',
                'correction': 'Replace "Charity Commission" with "OSCR (Office of the Scottish Charity Regulator)"',
                'citation': 'Charities and Trustee Investment (Scotland) Act 2005'
            })

        # 3. Check for OSCR references in Scottish charity context
        if charity_mentioned and not re.search(r'\bOSCR\b|Office\s+of\s+the\s+Scottish\s+Charity\s+Regulator', text, re.IGNORECASE):
            corrections.append({
                'type': 'oscr_reference',
                'suggestion': 'Scottish charities must be registered with OSCR and display their Scottish Charity Number (SC number)',
                'citation': 'Charities and Trustee Investment (Scotland) Act 2005'
            })

        # 4. Check for charity number format
        charity_number = re.search(r'Charity\s+(?:Number|No\.?|Registration)\s*:?\s*(\d+)', text, re.IGNORECASE)
        scottish_charity_number = re.search(r'Scottish\s+Charity\s+(?:Number|No\.?)\s*:?\s*(SC\d{6})', text, re.IGNORECASE)

        if charity_number and not scottish_charity_number:
            corrections.append({
                'type': 'charity_number_format',
                'suggestion': 'Scottish charities have SC numbers (e.g., SC012345), not English charity numbers',
                'citation': 'OSCR - Scottish Charity Numbers begin with "SC"'
            })

        # 5. Check for Community Interest Company (CIC) references
        cic_mentioned = re.search(r'Community\s+Interest\s+Compan(?:y|ies)|CIC', text, re.IGNORECASE)
        if cic_mentioned:
            cic_regulator = re.search(r'CIC\s+Regulator', text, re.IGNORECASE)
            if not cic_regulator:
                corrections.append({
                    'type': 'cic_regulator',
                    'suggestion': 'Community Interest Companies (CICs) in Scotland are regulated by the UK-wide CIC Regulator',
                    'citation': 'Companies (Audit, Investigations and Community Enterprise) Act 2004'
                })

        # 6. Check for Scottish Limited Partnership (SLP) references
        limited_partnership = re.search(r'Limited\s+Partnership|L\.?P\.?(?!\s+Act)', text, re.IGNORECASE)
        if limited_partnership:
            corrections.append({
                'type': 'scottish_limited_partnership',
                'suggestion': 'Scottish Limited Partnerships (SLPs) have distinct rules under Scots law and have been subject to transparency reforms',
                'citation': 'Limited Partnerships Act 1907; Scottish Partnerships (Register of People with Significant Control) Regulations 2017'
            })

        # 7. Check for registered office location
        registered_office = re.search(r'registered\s+office', text, re.IGNORECASE)
        if registered_office:
            scotland_office = re.search(r'(?:registered\s+office|located|situated).*(?:Scotland|Scottish\s+address)', text, re.IGNORECASE)
            if scotland_office:
                corrections.append({
                    'type': 'scottish_registered_office',
                    'suggestion': 'Companies with registered offices in Scotland are subject to Scots law for certain matters',
                    'citation': 'Companies Act 2006 - registered office location determines some legal jurisdictions'
                })

        # 8. Check for directors' duties references
        directors_duties = re.search(r'director(?:s\'?)?.*(?:dut(?:y|ies)|obligation|responsibility)', text, re.IGNORECASE)
        if directors_duties:
            corrections.append({
                'type': 'directors_duties_uk_wide',
                'suggestion': 'Directors\' duties under Companies Act 2006 apply equally throughout the UK (including Scotland)',
                'citation': 'Companies Act 2006, Part 10 (applies throughout UK)'
            })

        # 9. Check for insolvency references
        insolvency_mentioned = re.search(r'insolvenc(?:y|ies)|liquidation|administration|receivership', text, re.IGNORECASE)
        if insolvency_mentioned:
            scots_insolvency = re.search(r'Scots\s+(?:insolvency|bankruptcy)|Insolvency\s+\(Scotland\)', text, re.IGNORECASE)
            if not scots_insolvency:
                corrections.append({
                    'type': 'scottish_insolvency',
                    'suggestion': 'Scottish companies are subject to specific Scottish insolvency procedures and terminology (e.g., sequestration)',
                    'citation': 'Insolvency Act 1986 (as applied to Scotland); Bankruptcy (Scotland) Act 2016'
                })

        # 10. Check for articles of association references
        articles = re.search(r'[Aa]rticles\s+of\s+[Aa]ssociation|[Mm]emorandum\s+and\s+[Aa]rticles', text, re.IGNORECASE)
        if articles:
            corrections.append({
                'type': 'articles_uk_wide',
                'suggestion': 'Articles of association requirements are the same for Scottish companies under Companies Act 2006',
                'citation': 'Companies Act 2006 (applies throughout UK)'
            })

        # 11. Check for SCIO (Scottish Charitable Incorporated Organisation)
        scio_mentioned = re.search(r'\bSCIO\b|Scottish\s+Charitable\s+Incorporated\s+Organisation', text, re.IGNORECASE)
        if scio_mentioned:
            corrections.append({
                'type': 'scio_reference',
                'suggestion': 'SCIOs are a Scottish-only charitable structure, registered only with OSCR (not Companies House)',
                'citation': 'Charities and Trustee Investment (Scotland) Act 2005, Part 7'
            })
        elif charity_mentioned:
            corrections.append({
                'type': 'scio_option',
                'suggestion': 'Consider mentioning SCIO (Scottish Charitable Incorporated Organisation) as a charitable structure option in Scotland',
                'citation': 'Charities and Trustee Investment (Scotland) Act 2005, Part 7'
            })

        # 12. Check for charitable purposes references
        charitable_purposes = re.search(r'charitable\s+purpose', text, re.IGNORECASE)
        if charitable_purposes:
            corrections.append({
                'type': 'charitable_purposes_scotland',
                'suggestion': 'Scottish charity law defines charitable purposes under the Charities and Trustee Investment (Scotland) Act 2005',
                'citation': 'Charities and Trustee Investment (Scotland) Act 2005, s.7'
            })

        # 13. Check for company secretary references
        company_secretary = re.search(r'company\s+secretary', text, re.IGNORECASE)
        if company_secretary:
            private_company = re.search(r'private\s+(?:limited\s+)?compan(?:y|ies)', text, re.IGNORECASE)
            if private_company:
                corrections.append({
                    'type': 'company_secretary_optional',
                    'suggestion': 'Private companies (including Scottish companies) are not required to have a company secretary under Companies Act 2006',
                    'citation': 'Companies Act 2006, s.270 (private companies)'
                })

        # 14. Check for Scottish partnership references
        partnership = re.search(r'partnership(?!.*limited)', text, re.IGNORECASE)
        if partnership:
            corrections.append({
                'type': 'scottish_partnership',
                'suggestion': 'Scottish partnerships have separate legal personality (unlike English partnerships) under Scots law',
                'citation': 'Partnership Act 1890, s.4(2) - Scottish partnerships have legal personality'
            })

        # 15. Check for cross-border trading references
        cross_border = re.search(r'(?:England|Wales|Northern\s+Ireland).*(?:trad(?:e|ing)|business|operation)', text, re.IGNORECASE)
        if cross_border and registered_office:
            corrections.append({
                'type': 'cross_border_operations',
                'suggestion': 'Scottish companies trading in England/Wales may need to consider different legal requirements in those jurisdictions',
                'citation': 'Companies Act 2006 - UK-wide registration but different jurisdictional rules'
            })

        # Compile final result
        if issues:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': f"Scottish corporate law issues detected: {'; '.join(issues)}",
                'legal_source': self.legal_source,
                'corrections': corrections,
                'issues': issues
            }
        elif corrections:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'Scottish corporate law guidance applicable',
                'legal_source': self.legal_source,
                'corrections': corrections
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Scottish corporate law compliance checks passed',
            'legal_source': self.legal_source
        }


# Test cases
TEST_CASES = [
    {
        'name': 'Scottish charity with Charity Commission reference',
        'text': 'This Scottish charity is registered with the Charity Commission. Charity Number: 123456.',
        'expected_status': 'FAIL',
        'expected_issues': ['Charity Commission referenced']
    },
    {
        'name': 'Correct Scottish charity reference',
        'text': 'This Scottish charity is registered with OSCR. Scottish Charity Number: SC012345.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Scottish company with SCIO reference',
        'text': 'This SCIO is registered with OSCR in Scotland and operates under Scots law.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Scottish Limited Partnership',
        'text': 'This Scottish Limited Partnership operates in Scotland under Scots law.',
        'expected_status': 'WARNING',
        'expected_corrections': ['scottish_limited_partnership']
    },
    {
        'name': 'Scottish company insolvency',
        'text': 'This Scottish company may face liquidation or administration proceedings.',
        'expected_status': 'WARNING',
        'expected_corrections': ['scottish_insolvency']
    },
    {
        'name': 'Scottish partnership legal personality',
        'text': 'The partnership is registered in Scotland and trades under Scots law.',
        'expected_status': 'WARNING',
        'expected_corrections': ['scottish_partnership']
    }
]
