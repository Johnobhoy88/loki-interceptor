"""
Scottish Contracts Law Compliance Gate

Checks for Scotland-specific contract law differences:
- Consensus in idem (meeting of minds) vs offer and acceptance
- No consideration requirement in Scots law
- "Subject to contract" warnings (not applicable in Scotland)
- Jus quaesitum tertio (third-party rights)
"""

import re


class ScottishContractsGate:
    def __init__(self):
        self.name = "scottish_contracts"
        self.severity = "critical"
        self.legal_source = "Scots Contract Law; Contract (Scotland) Act 1997; Contract (Third Party Rights) (Scotland) Act 2017"

    def _is_relevant(self, text):
        """Check if document is a Scottish contract"""
        text_lower = (text or '').lower()
        is_scottish = any([
            'scots law' in text_lower,
            'law of scotland' in text_lower,
            re.search(r'governed\s+by.*\bscot(?:s|tish|land)\b', text_lower),
            'scottish law' in text_lower
        ])
        is_contract = any([
            'agreement' in text_lower,
            'contract' in text_lower,
            'parties agree' in text_lower,
            'terms and conditions' in text_lower
        ])
        return is_scottish and is_contract

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a Scottish contract'
            }

        issues = []
        corrections = []

        # 1. Check for "consideration" language (not required in Scots law)
        consideration_patterns = [
            r'in\s+consideration\s+of',
            r'good\s+and\s+valuable\s+consideration',
            r'for\s+and\s+in\s+consideration',
            r'receipt.*consideration.*acknowledged'
        ]

        for pattern in consideration_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append("English law 'consideration' language used in Scottish contract")
                corrections.append({
                    'type': 'consideration_not_required',
                    'suggestion': 'Scots law does not require consideration for contract formation. Remove consideration clauses or note they are not legally necessary in Scotland.',
                    'correction': 'Consideration clauses are superfluous in Scots law contracts',
                    'citation': 'Scots contract law - no consideration requirement (unlike English law)'
                })
                break

        # 2. Check for "subject to contract" warnings
        subject_to_contract = re.search(r'subject\s+to\s+(?:contract|formal\s+contract)', text, re.IGNORECASE)
        if subject_to_contract:
            issues.append("'Subject to contract' used in Scottish context")
            corrections.append({
                'type': 'subject_to_contract_warning',
                'suggestion': '"Subject to contract" may NOT prevent binding contract formation in Scotland if consensus in idem exists',
                'correction': 'In Scotland, if parties reach agreement (consensus in idem), a binding contract may exist even with "subject to contract" language',
                'citation': 'Scots contract law - Stobo Ltd v Morrisons (Gowns) Ltd [1949]; Grant v Stoneham [2011]'
            })

        # 3. Check for strict "offer and acceptance" terminology
        if re.search(r'offer\s+and\s+acceptance', text, re.IGNORECASE):
            # Check if consensus in idem is mentioned
            if not re.search(r'consensus\s+in\s+idem|meeting\s+of\s+(?:the\s+)?minds', text, re.IGNORECASE):
                corrections.append({
                    'type': 'contract_formation_principle',
                    'suggestion': 'Scots law focuses on "consensus in idem" (meeting of minds) rather than strict offer and acceptance',
                    'correction': 'Consider referencing "consensus in idem" alongside or instead of "offer and acceptance"',
                    'citation': 'Scots contract law - consensus in idem principle'
                })

        # 4. Check for third-party rights (Jus quaesitum tertio)
        third_party_mentioned = re.search(r'third[\s-]part(?:y|ies)', text, re.IGNORECASE)
        contracts_act_mentioned = re.search(r'contracts.*rights.*third\s+parties.*act\s+1999', text, re.IGNORECASE)

        if third_party_mentioned and contracts_act_mentioned:
            issues.append("English Contracts (Rights of Third Parties) Act 1999 referenced in Scottish contract")
            corrections.append({
                'type': 'third_party_rights',
                'suggestion': 'The Contracts (Rights of Third Parties) Act 1999 does NOT apply in Scotland',
                'correction': 'Reference the Contract (Third Party Rights) (Scotland) Act 2017 or the common law doctrine of jus quaesitum tertio',
                'citation': 'Contract (Third Party Rights) (Scotland) Act 2017; jus quaesitum tertio (common law)'
            })

        # 5. Check for jus quaesitum tertio concepts
        if third_party_mentioned and re.search(r'enforce|right|benefit', text, re.IGNORECASE):
            if not re.search(r'jus\s+quaesitum\s+tertio|Contract.*Third\s+Party.*Scotland.*2017', text, re.IGNORECASE):
                corrections.append({
                    'type': 'jus_quaesitum_tertio_suggestion',
                    'suggestion': 'For third-party rights in Scotland, reference jus quaesitum tertio or the Contract (Third Party Rights) (Scotland) Act 2017',
                    'citation': 'Contract (Third Party Rights) (Scotland) Act 2017; jus quaesitum tertio doctrine'
                })

        # 6. Check for "executed as a deed" language
        if re.search(r'executed\s+as\s+a\s+deed|signed.*sealed.*delivered', text, re.IGNORECASE):
            corrections.append({
                'type': 'deed_execution',
                'suggestion': 'Scots law does not have the same concept of "deeds" as English law. Contracts are valid without deed formalities.',
                'correction': 'Deed execution is an English law concept; Scots law contracts are binding based on consensus in idem',
                'citation': 'Scots contract law - no deed requirement'
            })

        # 7. Check for "entire agreement" clauses
        entire_agreement = re.search(r'entire\s+agreement', text, re.IGNORECASE)
        if entire_agreement:
            # Check if it acknowledges Scots law limitations
            if not re.search(r'(?:subject\s+to|except\s+for|save\s+for).*fraud|misrepresentation', text, re.IGNORECASE):
                corrections.append({
                    'type': 'entire_agreement_clause',
                    'suggestion': 'Entire agreement clauses in Scots law cannot exclude liability for fraud or fraudulent misrepresentation',
                    'citation': 'Scots contract law - entire agreement clauses subject to fraud exception'
                })

        # 8. Check for contract formation timing issues
        if re.search(r'binding.*(?:upon|when|once).*sign(?:ed|ature)', text, re.IGNORECASE):
            corrections.append({
                'type': 'contract_formation_timing',
                'suggestion': 'In Scots law, contracts may be binding earlier than signature if consensus in idem is reached',
                'correction': 'Consider: "This contract is binding when the parties reach consensus in idem, which may occur before signature"',
                'citation': 'Scots contract law - consensus in idem may precede signature'
            })

        # 9. Check for "without prejudice" usage
        if re.search(r'without\s+prejudice', text, re.IGNORECASE):
            corrections.append({
                'type': 'without_prejudice_scots_law',
                'suggestion': '"Without prejudice" communications in Scots law follow similar principles to English law but are applied under Scots privilege rules',
                'citation': 'Scots law of evidence and privilege'
            })

        # 10. Check for rectification references
        if re.search(r'rectif(?:y|ication)', text, re.IGNORECASE):
            corrections.append({
                'type': 'rectification',
                'suggestion': 'Contract rectification in Scots law requires proof of common error or unilateral error with knowledge',
                'citation': 'Law Reform (Miscellaneous Provisions) (Scotland) Act 1985, s.8; Contract (Scotland) Act 1997'
            })

        # Compile final result
        if issues:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': f"Scottish contract law issues detected: {'; '.join(issues)}",
                'legal_source': self.legal_source,
                'corrections': corrections,
                'issues': issues
            }
        elif corrections:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Scottish contract law guidance applicable',
                'legal_source': self.legal_source,
                'corrections': corrections
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Scottish contract law compliance checks passed',
            'legal_source': self.legal_source
        }


# Test cases
TEST_CASES = [
    {
        'name': 'Scottish contract with consideration clause',
        'text': 'This Agreement is governed by Scots law. In consideration of £1 and other valuable consideration, the parties agree...',
        'expected_status': 'FAIL',
        'expected_issues': ['consideration language used']
    },
    {
        'name': 'Subject to contract in Scotland',
        'text': 'This agreement is subject to contract and governed by the law of Scotland.',
        'expected_status': 'FAIL',
        'expected_issues': ['Subject to contract']
    },
    {
        'name': 'English Third Party Rights Act in Scottish contract',
        'text': 'This contract governed by Scots law. Third parties may enforce rights under the Contracts (Rights of Third Parties) Act 1999.',
        'expected_status': 'FAIL',
        'expected_issues': ['English Contracts (Rights of Third Parties) Act 1999']
    },
    {
        'name': 'Proper Scottish contract with consensus in idem',
        'text': 'This Agreement is governed by Scots law. The parties have reached consensus in idem. Third party rights are governed by jus quaesitum tertio.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Deed execution in Scottish contract',
        'text': 'This contract is governed by Scots law and executed as a deed.',
        'expected_status': 'WARNING',
        'expected_corrections': ['deed execution']
    }
]
