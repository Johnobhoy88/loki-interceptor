import re


PROTECTED_CLASSES = [
    r"race", r"ethnicity", r"religion", r"gender", r"sex", r"sexual orientation",
    r"disability", r"age", r"pregnancy", r"maternity", r"marital status",
    r"transgender", r"non-binary", r"nationality", r"origin"
]

BIAS_ADJECTIVES = [
    r"lazy", r"unreliable", r"aggressive", r"emotional", r"irrational",
    r"weak", r"inferior", r"superior"
]


def detect_bias(text: str):
    content = text or ""
    findings = []

    # Simple heuristic: adjective within 5 words of a protected class term
    tokens = re.findall(r"\b\w+\b", content.lower())
    for i, tok in enumerate(tokens):
        for adj in BIAS_ADJECTIVES:
            if re.fullmatch(adj, tok):
                window = tokens[max(0, i - 5): i + 6]
                for pc in PROTECTED_CLASSES:
                    if any(re.fullmatch(pc, w) for w in window):
                        findings.append({
                            'adj': tok,
                            'context': ' '.join(window)
                        })
                        break

    has_bias = len(findings) > 0
    severity = 'medium' if has_bias else 'none'
    status = 'FAIL' if has_bias else 'PASS'
    message = 'Potential biased language near protected classes' if has_bias else 'No bias indicators found'

    return {
        'status': status,
        'severity': severity,
        'message': message,
        'details': findings
    }
