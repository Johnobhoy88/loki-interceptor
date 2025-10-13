import re


class FinfluencerControlsGate:
    def __init__(self):
        self.name = "finfluencer_controls"
        self.severity = "critical"
        self.legal_source = "FCA Financial Promotions via Social Media & Influencers"

    def _is_relevant(self, text):
        """Check if document references social media or influencers"""
        text_lower = text.lower()
        keywords = [
            'social media', 'influencer', 'instagram', 'tiktok', 'youtube',
            'facebook', 'twitter', 'linkedin', 'post', 'tweet', 'share',
            'online', 'digital', 'content creator', 'ambassador'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not reference social media or influencer marketing',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Detect social media platform mentions
        platform_patterns = [
            r'\b(?:instagram|tiktok|youtube|facebook|twitter|x\.com|linkedin|snapchat|whatsapp)\b',
            r'social\s+media\s+(?:platform|channel|post)',
            r'(?:tweet|post|share|story|reel|video)\b'
        ]

        platforms_mentioned = []
        for pattern in platform_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches:
                    platforms_mentioned.append(m.group())
                    spans.append({
                        'type': 'social_platform',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Detect influencer references
        influencer_patterns = [
            r'\b(?:influencer|ambassador|content\s+creator|partner|affiliate)\b',
            r'working\s+with',
            r'collaboration',
            r'sponsored\s+by',
            r'in\s+partnership\s+with'
        ]

        has_influencer_ref = False
        for pattern in influencer_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_influencer_ref = True
                for m in matches:
                    spans.append({
                        'type': 'influencer_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for required controls
        control_indicators = {
            'approval': [
                r'approved\s+by',
                r'compliance\s+(?:approved|review)',
                r's\.?24\s+approval',
                r'authorised\s+(?:person|firm)'
            ],
            'ad_label': [
                r'#ad\b',
                r'#sponsored\b',
                r'\[ad\]',
                r'this\s+is\s+an?\s+(?:advertisement|ad)',
                r'paid\s+promotion',
                r'promotional\s+content'
            ],
            'risk_warning': [
                r'capital\s+at\s+risk',
                r'not\s+(?:financial\s+)?advice',
                r'seek\s+(?:professional\s+)?advice',
                r'do\s+your\s+own\s+research'
            ]
        }

        controls_present = {}
        for control_name, patterns in control_indicators.items():
            controls_present[control_name] = False
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    controls_present[control_name] = True
                    for m in matches:
                        spans.append({
                            'type': f'control_{control_name}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Detect promotional content without controls
        promotional_patterns = [
            r'(?:invest|buy|get|join|sign\s+up|download|apply)\s+(?:now|today)',
            r'limited\s+(?:time|offer|spaces)',
            r'don\'t\s+miss\s+out',
            r'exclusive\s+(?:offer|access|deal)'
        ]

        is_promotional = False
        for pattern in promotional_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                is_promotional = True
                break

        # Determine status
        issues = []
        missing_controls = []

        # If influencer/social media mentioned with promotional content
        if (platforms_mentioned or has_influencer_ref) and is_promotional:

            # Check for approval
            if not controls_present['approval']:
                missing_controls.append('FCA s.24 approval by authorised person')
                issues.append('No evidence of FCA approval (s.24 requirement)')

            # Check for ad label
            if not controls_present['ad_label']:
                missing_controls.append('#ad or "advertisement" label')
                issues.append('Missing advertisement disclosure label')

            # Check for risk warning
            if not controls_present['risk_warning']:
                missing_controls.append('Risk warning or "not advice" disclaimer')
                issues.append('Missing risk warning or advice disclaimer')

        # Critical failure: promotional social media content without controls
        if len(missing_controls) >= 2:
            details = []
            for issue in issues:
                details.append(issue)
            details.append(f'Missing controls: {", ".join(missing_controls)}')
            if platforms_mentioned:
                details.append(f'Platforms mentioned: {", ".join(list(set(platforms_mentioned)))}')
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Social media financial promotion missing required controls ({len(missing_controls)} missing)',
                'legal_source': self.legal_source,
                'suggestion': f'All social media financial promotions must: (1) be approved by FCA authorised person (s.24), (2) be clearly labelled as ads (#ad), (3) include risk warnings. Missing: {", ".join(missing_controls)}',
                'spans': spans,
                'details': details
            }

        # Warning: some controls missing
        if len(missing_controls) > 0:
            details = []
            details.append(f'Missing controls: {", ".join(missing_controls)}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Social media promotion may lack required controls',
                'legal_source': self.legal_source,
                'suggestion': f'Ensure: {", ".join(missing_controls)}',
                'spans': spans,
                'details': details
            }

        # If social/influencer mentioned but all controls present
        if (platforms_mentioned or has_influencer_ref):
            details = []
            present_controls = [k for k, v in controls_present.items() if v]
            details.append(f'Controls present: {", ".join(present_controls)}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Social media/influencer controls appear adequate',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        return {'status': 'N/A'}
