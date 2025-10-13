from core.universal_detectors import UniversalDetectors


def test_detect_bias_flagged_when_hateful_language_present():
    detector = UniversalDetectors()
    text = "Those women are inferior and should not be trusted."
    result = detector.detect_bias(text)
    assert result['status'] == 'FAIL'
    assert result['severity'] == 'high'
    assert result['instances']


def test_detect_bias_passes_when_language_neutral():
    detector = UniversalDetectors()
    text = "Our policy applies to women and men equally without exception."
    result = detector.detect_bias(text)
    assert result['status'] == 'PASS'
    assert result['severity'] == 'none'


def test_detect_harm_marks_critical_language():
    detector = UniversalDetectors()
    text = "Step-by-step instructions on how to kill yourself."
    result = detector.detect_harm(text)
    assert result['status'] == 'FAIL'
    assert result['severity'] == 'critical'


def test_detect_illegal_content_alerts_on_weapon_building():
    detector = UniversalDetectors()
    text = "This guide explains how to make a bomb with household items."
    result = detector.detect_illegal_content(text)
    assert result['status'] == 'FAIL'
    assert result['severity'] in {'high', 'critical'}
    assert 'examples' in result
