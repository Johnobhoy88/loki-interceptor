import re


class GardenLeaveGate:
    def __init__(self):
        self.name = "garden_leave"
        self.severity = "medium"
        self.legal_source = "Contract Law, William Hill v Tucker [1998]"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['garden leave', 'notice', 'terminat', 'resign'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        garden_leave_patterns = [
            r'garden\s+leave',
            r'(?:require|direct|instruct).*(?:not\s+(?:attend|come\s+to)\s+work|stay\s+away)',
            r'(?:during\s+notice|notice\s+period).*(?:not\s+required|may\s+be\s+required).*(?:attend|work)'
        ]

        has_garden_leave = any(re.search(p, text, re.IGNORECASE) for p in garden_leave_patterns)

        if not has_garden_leave:
            return {'status': 'N/A', 'message': 'No garden leave provisions', 'legal_source': self.legal_source}

        # Check for express contractual right
        express_right_patterns = [
            r'(?:may|right\s+to|entitled\s+to).*(?:require|place).*garden\s+leave',
            r'(?:discretion|option).*(?:require|direct).*(?:not\s+attend|stay\s+away)',
            r'(?:employer|company).*may.*(?:require|direct)'
        ]

        has_express_right = any(re.search(p, text, re.IGNORECASE) for p in express_right_patterns)

        if not has_express_right:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Garden leave mentioned without express contractual right',
                'legal_source': 'William Hill v Tucker [1998] IRLR 313',
                'suggestion': 'Add express clause: "The employer may require you to remain away from work during notice period on full pay and benefits"',
                'risk': 'Without express right, requiring garden leave may be breach of contract (duty to provide work)'
            }

        elements = {
            'full_pay': r'full\s+(?:pay|salary|remuneration)',
            'benefits_continue': r'(?:benefit|entitlement).*(?:continue|maintain)',
            'no_other_employment': r'(?:not|shall\s+not).*(?:work\s+for|employed\s+by|engage\s+in).*(?:other|another)',
            'company_property': r'(?:return|surrender).*(?:property|equipment|device|laptop)',
            'contact_restrictions': r'(?:not|shall\s+not).*(?:contact|communicate).*(?:client|customer|employee)',
            'confidentiality': r'confidential',
            'availability': r'(?:available|contactable).*(?:if\s+required|reasonable)',
            'duration': r'(?:whole|entire|all).*notice\s+period|up\s+to'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found_elements.values())

        if not found_elements['full_pay']:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Garden leave without full pay provision',
                'legal_source': self.legal_source,
                'suggestion': 'Must specify full pay and benefits continue during garden leave',
                'risk': 'Employee may argue garden leave invalid without full pay'
            }

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive garden leave clause ({score}/8 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v]
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic garden leave provisions ({score}/8)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: contact restrictions, property return, availability requirements'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Garden leave clause lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: full pay, benefits continue, no other employment, return property, contact restrictions, duration'
        }
