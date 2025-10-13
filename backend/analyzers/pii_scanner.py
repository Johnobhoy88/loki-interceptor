import re


# UK-focused patterns and general patterns
NI_PATTERN = re.compile(r"\b(?!BG|GB|NK|KN|TN|NT|ZZ)[A-CEGHJ-PR-TW-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b", re.IGNORECASE)
NHS_PATTERN = re.compile(r"\b\d{3}\s?\d{3}\s?\d{4}\b")
UK_MOBILE_PATTERN = re.compile(r"(\+44\s?7\d{3}|\(?07\d{3}\)?)\s?\d{3}\s?\d{3}")

PII_PATTERNS = {
    'email': re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}") ,
    'phone': UK_MOBILE_PATTERN,
    'ssn': re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    'credit_card': re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    'ni_number': NI_PATTERN,
    'nhs_number': NHS_PATTERN,
}

RISKY_SHARE = re.compile(r"\b(public|publish|posted|share publicly|broadcast|disclose|release|expose|leak|dump|pastebin|github)\b", re.IGNORECASE)


def scan_pii(text: str, document_type: str | None = None):
    content = text or ''
    entities = []
    for etype, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(content):
            entities.append({'type': etype, 'match': match.group(0)})

    # Critical/high classes always escalate
    has_cc = any(e['type'] == 'credit_card' for e in entities)
    has_ni = any(e['type'] == 'ni_number' for e in entities)
    has_nhs = any(e['type'] == 'nhs_number' for e in entities)
    has_ssn = any(e['type'] == 'ssn' for e in entities)
    if has_cc:
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Credit card number detected',
            'entities': [e for e in entities if e['type'] == 'credit_card']
        }
    if has_ni or has_nhs or has_ssn:
        types = []
        if has_ni: types.append('NI number')
        if has_nhs: types.append('NHS number')
        if has_ssn: types.append('SSN')
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Sensitive identifier detected: ' + ', '.join(types),
            'entities': [e for e in entities if e['type'] in ('ni_number','nhs_number','ssn')]
        }

    # Context-aware handling for email/phone
    email_count = sum(1 for e in entities if e['type'] == 'email')
    phone_count = sum(1 for e in entities if e['type'] == 'phone')
    risky_language = bool(RISKY_SHARE.search(content))

    content_lower = content.lower()
    policy_context = any(k in content_lower for k in ['privacy policy', 'privacy notice', 'contact us', 'contact', 'support@', 'help@'])
    allowed_doc_types = {'privacy_notice', 'privacy_policy', 'consent_form', 'security_policy', 'contact_page'}
    if policy_context or (document_type or '').lower() in allowed_doc_types:
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Contact info present in a policy/contact context',
            'entities': [e for e in entities if e['type'] in ('email', 'phone')]
        }

    if (email_count + phone_count) >= 5 or risky_language:
        return {
            'status': 'WARN',
            'severity': 'medium',
            'message': 'Contact info with potential sharing risk',
            'entities': [e for e in entities if e['type'] in ('email', 'phone')]
        }

    return {
        'status': 'PASS',
        'severity': 'none',
        'message': 'No sensitive PII detected; contact info may be expected',
        'entities': [e for e in entities if e['type'] in ('email', 'phone')]
    }
