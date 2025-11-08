"""
Scottish Data Protection Law Compliance Gate

Checks for Scotland-specific data protection differences:
- Scottish Information Commissioner references
- Scottish public sector requirements
- Freedom of Information (Scotland) Act 2002 differences
- Public Records (Scotland) Act 2011
"""

import re


class ScottishDataProtectionGate:
    def __init__(self):
        self.name = "scottish_data_protection"
        self.severity = "high"
        self.legal_source = "UK GDPR; Data Protection Act 2018; Freedom of Information (Scotland) Act 2002; Public Records (Scotland) Act 2011"

    def _is_relevant(self, text):
        """Check if document relates to Scottish data protection"""
        text_lower = (text or '').lower()
        is_scottish = any([
            'scotland' in text_lower,
            'scottish' in text_lower,
            'scots law' in text_lower
        ])
        is_data_protection = any([
            'data protection' in text_lower,
            'gdpr' in text_lower,
            'personal data' in text_lower,
            'information commissioner' in text_lower,
            'freedom of information' in text_lower,
            'foi' in text_lower,
            'data subject' in text_lower,
            'privacy' in text_lower
        ])
        return is_scottish and is_data_protection

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to Scottish data protection'
            }

        issues = []
        corrections = []

        # 1. Check for Scottish Information Commissioner references
        ico_mentioned = re.search(r'\bICO\b|Information\s+Commissioner', text, re.IGNORECASE)
        scottish_ico_mentioned = re.search(r'Scottish\s+Information\s+Commissioner', text, re.IGNORECASE)

        if ico_mentioned and not scottish_ico_mentioned:
            # Check if it's a public authority context
            public_sector = re.search(r'public\s+(?:authority|body|sector)|(?:council|NHS|government)', text, re.IGNORECASE)
            if public_sector:
                corrections.append({
                    'type': 'scottish_information_commissioner',
                    'suggestion': 'Scottish public authorities should reference the Scottish Information Commissioner (SIC) for FOI matters',
                    'correction': 'Add reference to Scottish Information Commissioner for FOI Scotland compliance',
                    'citation': 'Freedom of Information (Scotland) Act 2002 - enforced by Scottish Information Commissioner'
                })

        # 2. Check for Freedom of Information Act references
        foi_uk_act = re.search(r'Freedom\s+of\s+Information\s+Act\s+2000', text, re.IGNORECASE)
        foi_scotland_act = re.search(r'Freedom\s+of\s+Information\s+\(Scotland\)\s+Act\s+2002', text, re.IGNORECASE)

        if foi_uk_act and not foi_scotland_act:
            issues.append("FOI Act 2000 (UK) referenced instead of FOI (Scotland) Act 2002")
            corrections.append({
                'type': 'foi_legislation',
                'suggestion': 'Scottish public authorities are subject to the Freedom of Information (Scotland) Act 2002, not the UK FOIA 2000',
                'correction': 'Replace "Freedom of Information Act 2000" with "Freedom of Information (Scotland) Act 2002"',
                'citation': 'Freedom of Information (Scotland) Act 2002'
            })

        # 3. Check for Environmental Information Regulations
        eir_mentioned = re.search(r'Environmental\s+Information\s+Regulations', text, re.IGNORECASE)
        eir_scotland_mentioned = re.search(r'Environmental\s+Information\s+\(Scotland\)\s+Regulations', text, re.IGNORECASE)

        if eir_mentioned and not eir_scotland_mentioned:
            corrections.append({
                'type': 'eir_scotland',
                'suggestion': 'Scottish public authorities must comply with Environmental Information (Scotland) Regulations 2004',
                'correction': 'Reference "Environmental Information (Scotland) Regulations 2004" for Scottish public authorities',
                'citation': 'Environmental Information (Scotland) Regulations 2004 (SSI 2004/520)'
            })

        # 4. Check for ICO UK references in Scottish public sector context
        if re.search(r'(?:report\s+to|contact).*\bICO\b', text, re.IGNORECASE):
            if re.search(r'scottish.*(?:public|authority|body|council|nhs)', text, re.IGNORECASE):
                corrections.append({
                    'type': 'dual_commissioner_jurisdiction',
                    'suggestion': 'Scottish public authorities: UK ICO for data protection (UK GDPR/DPA 2018); Scottish Information Commissioner for FOI Scotland',
                    'correction': 'Clarify: "UK ICO for data protection matters; Scottish Information Commissioner for FOI (Scotland) Act 2002"',
                    'citation': 'Dual regulatory framework in Scotland'
                })

        # 5. Check for Public Records Act references
        if re.search(r'public\s+records?', text, re.IGNORECASE):
            public_records_scotland = re.search(r'Public\s+Records\s+\(Scotland\)\s+Act\s+2011', text, re.IGNORECASE)
            if not public_records_scotland:
                corrections.append({
                    'type': 'public_records_scotland',
                    'suggestion': 'Scottish public authorities must comply with Public Records (Scotland) Act 2011 for records management',
                    'citation': 'Public Records (Scotland) Act 2011 (PRSA)'
                })

        # 6. Check for Data Protection Officer references
        dpo_mentioned = re.search(r'Data\s+Protection\s+Officer|DPO', text, re.IGNORECASE)
        if dpo_mentioned:
            # Verify UK GDPR is referenced (applies equally in Scotland)
            if not re.search(r'UK\s+GDPR|Data\s+Protection\s+Act\s+2018', text, re.IGNORECASE):
                corrections.append({
                    'type': 'uk_gdpr_reference',
                    'suggestion': 'Ensure UK GDPR and Data Protection Act 2018 are referenced (apply throughout UK including Scotland)',
                    'citation': 'UK GDPR and Data Protection Act 2018'
                })

        # 7. Check for Scottish public authority obligations
        scottish_public_body = re.search(r'scottish.*(?:public\s+authority|public\s+body|council|nhs|government|parliament)', text, re.IGNORECASE)
        if scottish_public_body:
            # Check for records management plan mention
            if not re.search(r'records?\s+management\s+plan|RMP', text, re.IGNORECASE):
                corrections.append({
                    'type': 'records_management_plan',
                    'suggestion': 'Scottish public authorities must have a Records Management Plan approved by Keeper of the Records of Scotland',
                    'citation': 'Public Records (Scotland) Act 2011, s.1'
                })

        # 8. Check for FOI request timescales
        if re.search(r'(?:foi|freedom\s+of\s+information).*request', text, re.IGNORECASE):
            if re.search(r'(?:20|twenty)[\s-]working[\s-]day', text, re.IGNORECASE):
                # Correct - both UK and Scotland use 20 working days
                pass
            else:
                corrections.append({
                    'type': 'foi_timescale',
                    'suggestion': 'FOI (Scotland) Act 2002: requests must be responded to within 20 working days (same as UK FOIA)',
                    'citation': 'Freedom of Information (Scotland) Act 2002, s.10'
                })

        # 9. Check for Scottish Parliament and government references
        if re.search(r'scottish\s+(?:parliament|government|ministers)', text, re.IGNORECASE):
            corrections.append({
                'type': 'devolved_data_protection',
                'suggestion': 'Scottish Parliament and Government are subject to both FOI (Scotland) Act 2002 and UK data protection law',
                'citation': 'Scotland Act 1998; FOI (Scotland) Act 2002; UK GDPR'
            })

        # 10. Check for vexatious or repeated requests language
        if re.search(r'vexatious|repeated.*request', text, re.IGNORECASE):
            corrections.append({
                'type': 'vexatious_requests_scotland',
                'suggestion': 'FOI (Scotland) Act 2002, s.14: Scottish public authorities can refuse vexatious or repeated requests',
                'citation': 'Freedom of Information (Scotland) Act 2002, s.14'
            })

        # 11. Check for National Records of Scotland
        if re.search(r'national\s+archives|public\s+records', text, re.IGNORECASE):
            if not re.search(r'National\s+Records\s+of\s+Scotland|NRS', text, re.IGNORECASE):
                corrections.append({
                    'type': 'nrs_reference',
                    'suggestion': 'In Scotland, reference National Records of Scotland (NRS) and the Keeper of the Records of Scotland',
                    'citation': 'Public Records (Scotland) Act 2011; National Records of Scotland'
                })

        # Compile final result
        if issues:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': f"Scottish data protection law issues detected: {'; '.join(issues)}",
                'legal_source': self.legal_source,
                'corrections': corrections,
                'issues': issues
            }
        elif corrections:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Scottish data protection guidance applicable',
                'legal_source': self.legal_source,
                'corrections': corrections
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Scottish data protection compliance checks passed',
            'legal_source': self.legal_source
        }


# Test cases
TEST_CASES = [
    {
        'name': 'Scottish public authority with UK FOI Act',
        'text': 'This Scottish council complies with the Freedom of Information Act 2000 and reports to the ICO.',
        'expected_status': 'FAIL',
        'expected_issues': ['FOI Act 2000 referenced instead of FOI (Scotland) Act 2002']
    },
    {
        'name': 'Correct Scottish FOI reference',
        'text': 'Scottish public authorities must comply with the Freedom of Information (Scotland) Act 2002 and are overseen by the Scottish Information Commissioner.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Scottish public body without records management plan',
        'text': 'This Scottish Government agency processes personal data under UK GDPR and is a Scottish public authority.',
        'expected_status': 'WARNING',
        'expected_corrections': ['records management plan']
    },
    {
        'name': 'Environmental information in Scotland',
        'text': 'Scottish council must provide environmental information under Environmental Information (Scotland) Regulations 2004.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Mixed jurisdiction - ICO and Scottish context',
        'text': 'Scottish NHS board reports data breaches to ICO but handles FOI requests.',
        'expected_status': 'WARNING',
        'expected_corrections': ['dual commissioner jurisdiction']
    }
]
