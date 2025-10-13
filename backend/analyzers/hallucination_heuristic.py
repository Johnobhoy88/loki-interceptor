import re


ABSOLUTES = [r"always", r"never", r"guarantee", r"certainly", r"undeniably", r"proven"]


def assess_hallucination(text: str):
    content = (text or '').strip()
    if not content:
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Empty content'
        }

    # Heuristic: many digits and absolutes without citations
    digit_count = len(re.findall(r"\d", content))
    absolutes = [w for w in ABSOLUTES if re.search(rf"\b{w}\b", content, re.IGNORECASE)]
    has_citation = bool(re.search(r"\b(source|according to|ref\.|doi:|http[s]?://)\b", content, re.IGNORECASE))

    score = 0
    score += 1 if digit_count >= 10 else 0
    score += 1 if len(absolutes) >= 1 else 0
    score += 0 if has_citation else 1

    if score >= 2:
        return {
            'status': 'WARN',
            'severity': 'medium',
            'message': 'Potentially assertive content without citations; review for hallucinations',
            'signals': {
                'digits': digit_count,
                'absolutes': absolutes,
                'has_citation': has_citation,
            }
        }

    return {
        'status': 'PASS',
        'severity': 'none',
        'message': 'No strong hallucination signals detected'
    }

