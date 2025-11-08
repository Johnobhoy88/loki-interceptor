import re


class DataProtectionAdvancedGate:
    """
    Data Use and Access Act 2025 + UK GDPR Advanced Compliance
    Covers: DSAR updates, complaint procedures, enforcement, ICO obligations
    """
    def __init__(self):
        self.name = "data_protection_advanced"
        self.severity = "critical"
        self.legal_source = "Data Use and Access Act 2025, UK GDPR, Data Protection Act 2018"

    def _is_relevant(self, text):
        """Check if document relates to data protection"""
        text_lower = text.lower()
        keywords = [
            'data protection', 'personal data', 'gdpr', 'dpa', 'privacy',
            'data subject', 'subject access', 'dsar', 'sar',
            'data controller', 'data processor', 'ico',
            'information commissioner', 'complaint', 'breach'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to data protection',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. DATA SUBJECT ACCESS REQUESTS (DSAR) - 2025 Updates
        dsar_patterns = [
            r'(?:subject\s+access|data\s+access)\s+request',
            r'\bDSAR\b',
            r'\bSAR\b',
            r'request.*(?:copy|access).*(?:personal\s+)?data',
            r'right\s+(?:to\s+)?access'
        ]

        has_dsar = any(re.search(p, text, re.IGNORECASE) for p in dsar_patterns)

        if has_dsar:
            # Check for 1-month timeframe (2025: extended to 3 months for complex requests)
            timeframe_patterns = [
                r'(?:1|one)\s+month',
                r'(?:30|thirty)\s+days?',
                r'(?:within\s+)?(?:calendar\s+)?month',
                r'(?:3|three)\s+months?.*(?:complex|additional\s+time)'
            ]

            has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)
            if not has_timeframe:
                warnings.append('DSAR response deadline: 1 month (extendable to 3 months for complex requests under 2025 Act)')

            # Check for free of charge provision
            free_patterns = [
                r'free\s+of\s+charge',
                r'no\s+fee',
                r'without\s+charge',
                r'at\s+no\s+cost'
            ]

            has_free = any(re.search(p, text, re.IGNORECASE) for p in free_patterns)
            if not has_free:
                warnings.append('DSARs must be provided free of charge (unless manifestly unfounded or excessive)')

            # Check for manifestly unfounded/excessive provision (2025 clarification)
            unfounded_patterns = [
                r'manifestly\s+unfounded',
                r'excessive\s+(?:request|repetitive)',
                r'reasonable\s+fee',
                r'refuse.*(?:unfounded|excessive)'
            ]

            has_unfounded_provision = any(re.search(p, text, re.IGNORECASE) for p in unfounded_patterns)
            # Good practice to include

            # Check for identity verification (2025 strengthened requirements)
            identity_patterns = [
                r'verif(?:y|ication).*identity',
                r'confirm.*(?:your\s+)?identity',
                r'proof\s+of\s+identity',
                r'ID\s+(?:check|verification)',
                r'reasonable\s+doubt'
            ]

            has_identity = any(re.search(p, text, re.IGNORECASE) for p in identity_patterns)
            if not has_identity:
                warnings.append('2025 Act: strengthen identity verification before responding to DSARs')

            # Check for third-party data exemption
            third_party_patterns = [
                r'third[\s-]party\s+(?:data|information)',
                r'other\s+(?:individuals|people)',
                r'redact',
                r'(?:cannot|must\s+not)\s+disclose.*(?:other|another)'
            ]

            has_third_party = any(re.search(p, text, re.IGNORECASE) for p in third_party_patterns)
            # Good practice to clarify

            # Check for information to be provided (2025 expanded)
            info_requirements = {
                'data_held': r'(?:what|which)\s+(?:personal\s+)?data\s+(?:we\s+)?hold',
                'purposes': r'purposes?\s+of\s+processing',
                'recipients': r'(?:recipients?|who.*shared)',
                'retention': r'(?:retention\s+period|how\s+long)',
                'source': r'source\s+of\s+(?:the\s+)?data',
                'automated_decisions': r'automated\s+(?:decision|processing)',
                'safeguards': r'safeguards?.*(?:transfer|international)'
            }

            info_provided = sum(1 for p in info_requirements.values() if re.search(p, text, re.IGNORECASE))
            if info_provided < 4:
                warnings.append('DSAR response should include: data held, purposes, recipients, retention, source, automated decisions, transfer safeguards')

        # 2. RIGHT TO RECTIFICATION (2025 expedited process)
        rectification_patterns = [
            r'right\s+to\s+rectif(?:ication|y)',
            r'correct.*(?:inaccurate|incorrect)\s+data',
            r'update.*(?:personal\s+)?data',
            r'amend.*(?:data|information)'
        ]

        has_rectification = any(re.search(p, text, re.IGNORECASE) for p in rectification_patterns)

        if has_rectification:
            # Check for timeframe
            rect_timeframe_patterns = [
                r'(?:without\s+)?(?:undue\s+)?delay',
                r'(?:1|one)\s+month',
                r'promptly',
                r'as\s+soon\s+as\s+(?:possible|practicable)'
            ]

            has_rect_timeframe = any(re.search(p, text, re.IGNORECASE) for p in rect_timeframe_patterns)
            if not has_rect_timeframe:
                warnings.append('Right to rectification must be actioned without undue delay (within 1 month)')

            # Check for notification to third parties (2025 requirement)
            notification_patterns = [
                r'notif(?:y|ication).*(?:recipients?|third\s+part)',
                r'inform.*(?:other|those).*(?:data\s+shared|disclosed\s+to)',
                r'tell.*(?:who.*shared|recipients?)'
            ]

            has_notification = any(re.search(p, text, re.IGNORECASE) for p in notification_patterns)
            if not has_notification:
                warnings.append('2025 Act: must notify third parties when data is rectified unless impossible or disproportionate')

        # 3. RIGHT TO ERASURE ('Right to be Forgotten') - 2025 exceptions
        erasure_patterns = [
            r'right\s+to\s+erasure',
            r'right\s+to\s+be\s+forgotten',
            r'delete.*(?:personal\s+)?data',
            r'removal\s+of\s+(?:personal\s+)?data'
        ]

        has_erasure = any(re.search(p, text, re.IGNORECASE) for p in erasure_patterns)

        if has_erasure:
            # Check for valid grounds for erasure
            grounds_patterns = [
                r'no\s+longer\s+necessary',
                r'withdraw.*consent',
                r'object.*processing',
                r'unlawfully\s+processed',
                r'legal\s+obligation.*erasure',
                r'child.*online\s+services'
            ]

            has_grounds = any(re.search(p, text, re.IGNORECASE) for p in grounds_patterns)
            if not has_grounds:
                warnings.append('Right to erasure applies when: no longer necessary, consent withdrawn, objection, unlawful processing, legal obligation, or child data')

            # Check for exceptions (2025 clarified)
            exceptions_patterns = [
                r'(?:legal\s+obligation|compliance\s+with\s+law)',
                r'(?:public\s+interest|official\s+authority)',
                r'(?:legal\s+claims?|defence\s+of\s+claims?)',
                r'(?:archiving|research|statistical)\s+purposes?',
                r'freedom\s+of\s+expression'
            ]

            has_exceptions = any(re.search(p, text, re.IGNORECASE) for p in exceptions_patterns)
            if not has_exceptions:
                warnings.append('Right to erasure exceptions: legal obligations, public interest, legal claims, research, freedom of expression')

        # 4. RIGHT TO DATA PORTABILITY (2025 expanded)
        portability_patterns = [
            r'data\s+portability',
            r'receive.*data.*structured.*commonly\s+used',
            r'transmit.*data.*another\s+controller',
            r'machine[\s-]readable\s+format'
        ]

        has_portability = any(re.search(p, text, re.IGNORECASE) for p in portability_patterns)

        if has_portability:
            # Check for conditions
            portability_conditions = {
                'consent_contract': r'(?:consent|contract).*basis',
                'automated': r'automated\s+(?:means|processing)',
                'provided_by_subject': r'(?:provided|supplied)\s+by.*data\s+subject'
            }

            conditions_met = sum(1 for p in portability_conditions.values() if re.search(p, text, re.IGNORECASE))
            if conditions_met < 2:
                warnings.append('Data portability applies when: based on consent/contract, automated processing, data provided by data subject')

            # Check for format (2025 standardized)
            format_patterns = [
                r'structured',
                r'commonly\s+used',
                r'machine[\s-]readable',
                r'(?:JSON|XML|CSV)',
                r'interoperable\s+format'
            ]

            has_format = any(re.search(p, text, re.IGNORECASE) for p in format_patterns)
            if not has_format:
                warnings.append('Data portability: provide in structured, commonly used, machine-readable format (e.g., JSON, CSV)')

        # 5. RIGHT TO OBJECT (2025 strengthened for direct marketing)
        objection_patterns = [
            r'right\s+to\s+object',
            r'object\s+to\s+processing',
            r'opt[\s-]out',
            r'stop.*(?:processing|using)\s+(?:my\s+)?data'
        ]

        has_objection = any(re.search(p, text, re.IGNORECASE) for p in objection_patterns)

        if has_objection:
            # Check for direct marketing (absolute right - 2025 strengthened)
            marketing_patterns = [
                r'direct\s+marketing',
                r'marketing\s+purposes?',
                r'promotional\s+(?:material|communications?)',
                r'profiling.*marketing'
            ]

            has_marketing = any(re.search(p, text, re.IGNORECASE) for p in marketing_patterns)

            if has_marketing:
                absolute_patterns = [
                    r'absolute\s+right',
                    r'must\s+stop',
                    r'immediately\s+(?:cease|stop)',
                    r'without\s+(?:exception|delay)'
                ]

                has_absolute = any(re.search(p, text, re.IGNORECASE) for p in absolute_patterns)
                if not has_absolute:
                    warnings.append('2025 strengthening: absolute right to object to direct marketing - must stop immediately')

        # 6. COMPLAINT PROCEDURES (2025 enhanced requirements)
        complaint_patterns = [
            r'complaint',
            r'how\s+to\s+complain',
            r'raise\s+(?:a\s+)?(?:concern|issue)',
            r'data\s+protection\s+(?:officer|concern)'
        ]

        has_complaint = any(re.search(p, text, re.IGNORECASE) for p in complaint_patterns)

        if has_complaint:
            # Check for internal complaint process (2025 requirement)
            internal_patterns = [
                r'(?:contact|write\s+to|email).*(?:us|DPO|data\s+protection\s+officer)',
                r'internal\s+(?:complaint|resolution)',
                r'(?:investigate|resolve).*complaint',
                r'(?:within\s+)?(?:\d+)\s+(?:days?|weeks?).*respond'
            ]

            has_internal = any(re.search(p, text, re.IGNORECASE) for p in internal_patterns)
            if not has_internal:
                warnings.append('2025 Act: must provide clear internal complaint procedure with response timeframe')

            # Check for ICO complaint right
            ico_patterns = [
                r'\bICO\b',
                r'Information\s+Commissioner',
                r'supervisory\s+authority',
                r'ico\.org\.uk',
                r'casework@ico\.org\.uk'
            ]

            has_ico = any(re.search(p, text, re.IGNORECASE) for p in ico_patterns)
            if not has_ico:
                issues.append('CRITICAL: Must inform data subjects of right to complain to ICO (Information Commissioner\'s Office)')

        else:
            issues.append('CRITICAL: Must provide information on how to make a data protection complaint')

        # 7. ICO CONTACT DETAILS (2025 mandatory)
        ico_details_patterns = [
            r'Information\s+Commissioner\'?s\s+Office',
            r'Wycliffe\s+House',
            r'Water\s+Lane',
            r'Wilmslow',
            r'SK9\s+5AF',
            r'0303\s+123\s+1113',
            r'ico\.org\.uk'
        ]

        ico_mentions = sum(1 for p in ico_details_patterns if re.search(p, text, re.IGNORECASE))

        if has_complaint and ico_mentions < 2:
            warnings.append('Should provide full ICO contact details: casework@ico.org.uk, 0303 123 1113, ico.org.uk')

        # 8. ENFORCEMENT AND PENALTIES (2025 updated fines)
        enforcement_patterns = [
            r'(?:penalty|fine|enforcement)',
            r'up\s+to.*(?:million|£)',
            r'regulatory\s+action',
            r'non[\s-]compliance',
            r'breach.*(?:may\s+result|penalties?)'
        ]

        has_enforcement = any(re.search(p, text, re.IGNORECASE) for p in enforcement_patterns)

        if has_enforcement:
            # Check for updated 2025 penalty amounts
            penalty_patterns = [
                r'(?:£17\.5|17\.5)\s+million',
                r'(?:£8\.7|8\.7)\s+million',
                r'4%.*(?:global|annual|worldwide)\s+(?:turnover|revenue)',
                r'2%.*(?:global|annual|worldwide)\s+(?:turnover|revenue)'
            ]

            has_penalties = any(re.search(p, text, re.IGNORECASE) for p in penalty_patterns)
            # Good practice to mention severity

        # 9. DATA PROTECTION OFFICER (DPO) - 2025 expanded obligations
        dpo_patterns = [
            r'Data\s+Protection\s+Officer',
            r'\bDPO\b',
            r'privacy\s+officer'
        ]

        has_dpo = any(re.search(p, text, re.IGNORECASE) for p in dpo_patterns)

        if has_dpo:
            # Check for DPO contact details
            dpo_contact_patterns = [
                r'dpo@',
                r'(?:email|contact).*(?:DPO|data\s+protection\s+officer)',
                r'(?:address|phone).*DPO'
            ]

            has_dpo_contact = any(re.search(p, text, re.IGNORECASE) for p in dpo_contact_patterns)
            if not has_dpo_contact:
                warnings.append('Must provide DPO contact details for data protection queries')

            # Check for DPO independence (2025 emphasis)
            independence_patterns = [
                r'independent(?:ly)?',
                r'report.*(?:highest|senior)\s+management',
                r'no\s+(?:conflict\s+of\s+interest|instructions?)',
                r'autonomous'
            ]

            has_independence = any(re.search(p, text, re.IGNORECASE) for p in independence_patterns)
            if not has_independence:
                warnings.append('2025 emphasis: DPO must operate independently without instructions regarding their tasks')

        # 10. INTERNATIONAL TRANSFERS (2025 post-Brexit updates)
        transfer_patterns = [
            r'international\s+transfers?',
            r'transfer.*(?:outside|beyond)\s+(?:UK|EEA)',
            r'third\s+countr(?:y|ies)',
            r'adequacy\s+(?:decision|regulation)'
        ]

        has_transfers = any(re.search(p, text, re.IGNORECASE) for p in transfer_patterns)

        if has_transfers:
            # Check for transfer mechanisms (2025 UK-specific)
            mechanism_patterns = [
                r'adequacy\s+(?:decision|regulation)',
                r'(?:UK\s+)?International\s+Data\s+Transfer\s+(?:Agreement|Addendum)',
                r'\bIDTA\b',
                r'(?:UK\s+)?(?:addendum|standard\s+contractual\s+clauses)',
                r'binding\s+corporate\s+rules',
                r'\bBCRs?\b'
            ]

            has_mechanism = any(re.search(p, text, re.IGNORECASE) for p in mechanism_patterns)
            if not has_mechanism:
                warnings.append('2025: International transfers require: adequacy decision, UK IDTA, UK Addendum to SCCs, or BCRs')

            # Check for safeguards mention
            safeguards_patterns = [
                r'appropriate\s+safeguards?',
                r'protection.*(?:data\s+subjects?|rights)',
                r'enforceable\s+rights',
                r'effective\s+(?:remedies|legal\s+remedies)'
            ]

            has_safeguards = any(re.search(p, text, re.IGNORECASE) for p in safeguards_patterns)
            if not has_safeguards:
                warnings.append('International transfers must have appropriate safeguards and enforceable data subject rights')

        # 11. TRANSPARENCY (2025 enhanced plain language requirement)
        transparency_patterns = [
            r'(?:clear|plain|simple)\s+language',
            r'easy\s+to\s+understand',
            r'transparent',
            r'accessible',
            r'layered\s+(?:approach|notice)'
        ]

        has_transparency = any(re.search(p, text, re.IGNORECASE) for p in transparency_patterns)

        if not has_transparency and has_dsar:
            warnings.append('2025 Act: information must be in clear, plain language, easily accessible and understandable')

        # 12. CHILDREN'S DATA (2025 enhanced protections)
        children_patterns = [
            r'\bchild(?:ren)?\b',
            r'under\s+(?:13|16|18)',
            r'minor',
            r'parental\s+(?:consent|permission)'
        ]

        has_children = any(re.search(p, text, re.IGNORECASE) for p in children_patterns)

        if has_children:
            children_protection_patterns = [
                r'age\s+(?:verification|appropriate)',
                r'parental\s+consent',
                r'best\s+interests?',
                r'enhanced\s+protection',
                r'child[\s-]friendly'
            ]

            has_children_protection = any(re.search(p, text, re.IGNORECASE) for p in children_protection_patterns)
            if not has_children_protection:
                warnings.append('2025 enhanced: special protections for children\'s data - age verification, parental consent, best interests')

        # 13. ACCOUNTABILITY (2025 documentation requirements)
        accountability_patterns = [
            r'accountab(?:ility|le)',
            r'demonstrate\s+compliance',
            r'(?:maintain|keep)\s+records?',
            r'document(?:ation|ed)',
            r'data\s+protection\s+impact\s+assessment',
            r'\bDPIA\b'
        ]

        has_accountability = any(re.search(p, text, re.IGNORECASE) for p in accountability_patterns)

        if not has_accountability:
            warnings.append('Must demonstrate accountability - maintain records of processing, DPIAs, policies')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Data protection provisions have critical compliance gaps',
                'legal_source': self.legal_source,
                'suggestion': 'Urgent fixes required: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Data protection provisions need updating for 2025 Act',
                'legal_source': self.legal_source,
                'suggestion': 'Key improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Minor data protection improvements recommended',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Data protection provisions appear compliant with 2025 Act',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_data_protection_advanced_gate():
    gate = DataProtectionAdvancedGate()

    # Test 1: Missing ICO complaint right
    test1 = """
    DATA SUBJECT RIGHTS

    You have the right to access your personal data.
    We will respond within 1 month free of charge.

    If you are unhappy, please contact our DPO at dpo@company.com
    """
    result1 = gate.check(test1, "privacy_notice")
    assert result1['status'] == 'FAIL'
    assert 'ICO' in str(result1) or 'Information Commissioner' in str(result1)

    # Test 2: Compliant DSAR provisions
    test2 = """
    SUBJECT ACCESS REQUESTS

    You can request a copy of your personal data free of charge.
    We will respond within 1 month (extendable to 3 months for complex requests).

    We will verify your identity before responding.

    Your data will include: what data we hold, purposes, recipients, retention periods,
    sources, automated decisions, and international transfer safeguards.

    To complain, contact our DPO at dpo@company.com
    Or complain to the ICO: casework@ico.org.uk, 0303 123 1113, ico.org.uk
    """
    result2 = gate.check(test2, "privacy_notice")
    assert result2['status'] in ['PASS', 'WARNING']

    # Test 3: Right to erasure with exceptions
    test3 = """
    RIGHT TO ERASURE

    You can request deletion of your data when:
    - No longer necessary for the purposes
    - You withdraw consent
    - You object to processing
    - Data processed unlawfully
    - Required by legal obligation

    Exceptions apply for:
    - Legal obligations and compliance
    - Legal claims or defence
    - Public interest or official authority
    - Archiving, research or statistical purposes
    - Freedom of expression
    """
    result3 = gate.check(test3, "privacy_notice")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: Absolute right to object to marketing (2025)
    test4 = """
    DIRECT MARKETING

    You have an absolute right to object to direct marketing.
    We must stop immediately without exception if you object.

    To opt-out: email unsubscribe@company.com or click unsubscribe in emails.
    """
    result4 = gate.check(test4, "privacy_notice")
    assert result4['status'] in ['PASS', 'WARNING']

    print("All data protection advanced gate tests passed!")


if __name__ == "__main__":
    test_data_protection_advanced_gate()
