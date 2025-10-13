import re


class InvoiceNumberingGate:
    def __init__(self):
        self.name = "invoice_numbering"
        self.severity = "medium"
        self.legal_source = "VAT Regulations 1995; HMRC Internal Manuals (VATREC5010)"

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'invoice' in t

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain invoice numbers',
                'legal_source': self.legal_source
            }

        # Capture common invoice number formats
        patterns = [
            r'\b(?:inv|invoice)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z]{2,5}-?\d{2,6}|\d{5,})\b',
            r'\b([A-Z]{2,5}-\d{2,6})\b'
        ]

        spans = []
        ids = []
        seen_positions = set()
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                rng = (m.start(1), m.end(1))
                if rng in seen_positions:
                    continue
                seen_positions.add(rng)
                full = m.group(1)
                # Normalize: split prefix and numeric tail
                prefix_match = re.match(r'([A-Z]{2,5})-?(\d+)$', full, re.IGNORECASE)
                if prefix_match:
                    prefix = prefix_match.group(1).upper()
                    num = int(prefix_match.group(2))
                else:
                    prefix = ''
                    try:
                        num = int(full)
                    except Exception:
                        continue
                ids.append((prefix, num))
                spans.append({
                    'type': 'invoice_number',
                    'start': m.start(1),
                    'end': m.end(1),
                    'text': full,
                    'severity': 'medium'
                })

        if not ids:
            return {'status': 'PASS', 'severity': 'none', 'message': 'No invoice numbers detected', 'spans': []}

        # Check for gaps in sequences per prefix
        from collections import defaultdict
        groups = defaultdict(list)
        for pfx, num in ids:
            groups[pfx].append(num)

        gaps = []
        for pfx, nums in groups.items():
            if len(nums) < 2:
                continue
            nums_sorted = sorted(set(nums))
            for a, b in zip(nums_sorted, nums_sorted[1:]):
                if b - a > 1:
                    gaps.append(f"{pfx+'-' if pfx else ''}{a}->{pfx+'-' if pfx else ''}{b}")

        if gaps:
            return {
                'status': 'FAIL',
                'severity': 'medium',
                'message': 'Invoice numbering issues - gaps in sequence: ' + ', '.join(gaps),
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Use unique sequential numbering without gaps (e.g., INV-100, 101, 102).'
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'Invoice numbering appears sequential', 'spans': spans}
