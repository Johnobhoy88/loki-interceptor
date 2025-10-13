import re
import hashlib


class UniversalDetectors:
    def __init__(self):
        # Precompile patterns that are reused frequently
        self._ni_pattern = re.compile(r"\b[A-Z]{2}\d{6}[A-Z]\b")
        self._cc_pattern = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
        self._nhs_pattern = re.compile(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b")
        self._email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

        self._hate_targets = {
            'race': ['black', 'white', 'asian', 'latino', 'jew', 'muslim', 'christian', 'hindu'],
            'gender': ['women', 'men', 'trans', 'transgender', 'non-binary'],
            'orientation': ['gay', 'lesbian', 'bisexual', 'queer'],
            'disability': ['disabled', 'autistic', 'handicapped'],
            'origin': ['immigrant', 'refugee', 'foreigner']
        }
        self._hate_adjectives = ['inferior', 'lazy', 'criminal', 'dirty', 'untrustworthy', 'subhuman', 'vermin']

        harm_keywords = [
            'kill yourself', 'suicide', 'self harm', 'self-harm', 'harm yourself', 'cut myself',
            'bomb', 'explosive', 'shoot up', 'murder', 'poison', 'kill them', 'how to kill',
            'make a bomb', 'build a bomb', 'arson', 'terrorist'
        ]
        self._harm_patterns = [re.compile(rf"{kw}", re.IGNORECASE) for kw in harm_keywords]

        illegal_keywords = [
            'credit card dump', 'counterfeit', 'forged passport', 'money laundering', 'child abuse',
            'buy cocaine', 'drug lab', 'insider trading', 'zero day exploit', 'hack into',
            'lock picking', 'steal credentials', 'make a bomb', 'build a bomb', 'manufacture explosives'
        ]
        self._illegal_patterns = [re.compile(rf"{kw}", re.IGNORECASE) for kw in illegal_keywords]

    def detect_pii(self, text, document_type='unknown'):
        """Context-aware PII with span locations for highlighting"""
        content = text or ''
        findings = []
        spans = []
        severity = 'none'

        # National Insurance numbers (ALWAYS CRITICAL)
        for match in self._ni_pattern.finditer(content):
            findings.append('National Insurance number detected')
            spans.append({
                'type': 'ni_number',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'severity': 'critical'
            })
            severity = 'critical'

        # Credit card patterns (ALWAYS CRITICAL)
        for match in self._cc_pattern.finditer(content):
            findings.append('Credit card-like pattern detected')
            spans.append({
                'type': 'credit_card',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'severity': 'critical'
            })
            severity = 'critical'

        # NHS numbers (HIGH)
        for match in self._nhs_pattern.finditer(content):
            findings.append('NHS number-like pattern')
            spans.append({
                'type': 'nhs_number',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'severity': 'high'
            })
            if severity == 'none':
                severity = 'high'

        # Context-aware emails (only flag if unexpected)
        expected_contexts = ['privacy_notice', 'contact', 'dpo', 'data protection officer', 'disciplinary', 'hr']
        is_expected = any(ctx in (document_type or '').lower() or ctx in content.lower()[:200] for ctx in expected_contexts)

        if not is_expected:
            for match in self._email_pattern.finditer(content):
                findings.append('Email address detected')
                spans.append({
                    'type': 'email',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'medium'
                })
                if severity == 'none':
                    severity = 'medium'

        if not findings:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No concerning PII patterns detected',
                'spans': []
            }

        return {
            'status': 'FAIL' if severity in ['critical', 'high'] else 'WARNING',
            'severity': severity,
            'message': '; '.join(findings),
            'spans': spans,
            'suggestion': 'Remove or redact sensitive personal information.'
        }

    def detect_contradictions(self, text):
        """Basic contradiction detection via negation patterns"""
        content = text or ""
        sentences = content.split('.')
        contradictions = []

        # Look for explicit contradictions
        contradiction_patterns = [
            (r"is\s+(?:not|n't)", r"is\s+(?:a|an|the)"),
            (r"must\s+not", r"must\s+"),
            (r"never", r"always"),
            (r"impossible", r"possible"),
            (r"cannot", r"can\s+")
        ]

        for i, sent1 in enumerate(sentences):
            for sent2 in sentences[i + 1:]:
                for neg_pattern, pos_pattern in contradiction_patterns:
                    if re.search(neg_pattern, sent1, re.IGNORECASE) and re.search(pos_pattern, sent2, re.IGNORECASE):
                        contradictions.append({
                            'sentence_1': sent1.strip(),
                            'sentence_2': sent2.strip()
                        })

        return {
            'status': 'FAIL' if contradictions else 'PASS',
            'severity': 'high' if contradictions else 'none',
            'contradictions': contradictions,
            'message': f"Found {len(contradictions)} potential contradictions" if contradictions else 'No contradictions detected'
        }

    def detect_hallucination_markers(self, text):
        """Flag common hallucination patterns"""
        content = text or ""
        markers = []

        # Overly specific fake data
        if re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", content):
            markers.append('Suspiciously specific timestamps')

        # Fake citations
        if re.search(r"\(Smith et al\.,? \d{4}\)", content):
            markers.append('Academic citation format detected - verify source')

        # Absolute claims
        absolute_words = ['always', 'never', 'impossible', 'guaranteed', 'proven fact']
        found_absolutes = [word for word in absolute_words if word in content.lower()]
        if found_absolutes:
            markers.append(f"Absolute language: {', '.join(found_absolutes)}")

        return {
            'status': 'WARNING' if markers else 'PASS',
            'severity': 'medium' if markers else 'none',
            'markers': markers,
            'message': f"Found {len(markers)} hallucination markers" if markers else 'No obvious hallucination markers'
        }

    def detect_financial_promotion_risk(self, text):
        content = (text or '').lower()
        if not content.strip():
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No promotional content detected'
            }

        prohibited = ['guaranteed returns', 'guaranteed income', 'no risk', 'risk free', 'capital guaranteed']
        required_warning = ['capital at risk', 'you could lose', 'loss of all capital', 'no guarantee']

        breaches = [phrase for phrase in prohibited if phrase in content]
        has_warning = any(fragment in content for fragment in required_warning)

        if breaches and not has_warning:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'High-risk financial promotion language detected without mandatory risk warning.',
                'phrases': breaches,
                'suggestion': 'Insert FCA-compliant risk warnings and remove absolute guarantees.'
            }

        if breaches:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Promotional language includes absolute guarantees. Review against COBS 4 requirements.',
                'phrases': breaches
            }

        if not has_warning:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No explicit risk warning detected. Ensure required wording is present for retail promotions.'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Mandatory risk warnings present and no prohibited promises found.'
        }

    def detect_consumer_duty_gaps(self, text):
        content = (text or '').lower()
        duty_terms = ['foreseeable harm', 'act in good faith', 'consumer duty', 'fair value', 'consumer support']
        missing = [term for term in duty_terms if term not in content]

        if len(missing) == len(duty_terms):
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No explicit references to Consumer Duty principles detected. Validate coverage of PRIN 2A obligations.'
            }

        if missing:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'Consumer Duty coverage is partial. Missing concepts: ' + ', '.join(missing)
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Consumer Duty concepts referenced in document.'
        }

    def detect_bias(self, text):
        content = (text or '').lower()
        findings = []
        for category, targets in self._hate_targets.items():
            for target in targets:
                if target not in content:
                    continue
                for adjective in self._hate_adjectives:
                    patterns = [
                        rf"{adjective}\s+{target}",
                        rf"{target}\s+(?:are|is|were|was|be|being|been|seem|seems|seemed)\s+{adjective}",
                        rf"{target}\s+(?:should|must|ought\s+to|have\s+to)\s+be\s+{adjective}"
                    ]
                    if any(re.search(pat, content) for pat in patterns):
                        findings.append({'category': category, 'target': target, 'descriptor': adjective})
                        break

        if not findings:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No explicit hateful or biased language detected'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Potential hateful or biased language detected',
            'instances': findings,
            'suggestion': 'Remove discriminatory language and ensure inclusive policy guidance.'
        }

    def detect_harm(self, text):
        content = text or ''
        matches = []
        for pattern in self._harm_patterns:
            match = pattern.search(content)
            if match:
                matches.append({'pattern': pattern.pattern, 'text': match.group(0)})

        if not matches:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No self-harm or violence instructions detected'
            }

        severity = 'critical' if any('kill' in m['pattern'] or 'bomb' in m['pattern'] for m in matches) else 'high'
        return {
            'status': 'FAIL',
            'severity': severity,
            'message': 'Detected potential self-harm, violence, or weaponization content',
            'matches': matches,
            'suggestion': 'Block or redact harmful instructions and escalate for human review.'
        }

    def detect_illegal_content(self, text):
        content = text or ''
        matches = []
        for pattern in self._illegal_patterns:
            match = pattern.search(content)
            if match:
                matches.append(match.group(0))

        if not matches:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No clear solicitation of illegal activity detected'
            }

        severity = 'critical' if any('child' in m.lower() or 'exploit' in m.lower() for m in matches) else 'high'
        return {
            'status': 'FAIL',
            'severity': severity,
            'message': 'Detected potential solicitation of illegal activity',
            'examples': matches[:5],
            'suggestion': 'Reject request and follow escalation protocol for illegal content.'
        }

    def _max_severity(self, findings):
        severities = [f.get('severity', 'none') for f in findings]
        if 'critical' in severities:
            return 'critical'
        if 'high' in severities:
            return 'high'
        if 'medium' in severities:
            return 'medium'
        return 'none'
