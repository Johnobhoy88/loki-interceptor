import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / 'backend'))

import pytest
from core.synthesis import TextSanitizer, SnippetRegistry, UniversalSnippetMapper, SynthesisEngine
from core.async_engine import AsyncLOKIEngine


@pytest.fixture
def engine():
    eng = AsyncLOKIEngine(max_workers=2)
    for module in ['fca_uk', 'gdpr_uk']:
        eng.load_module(module)
    return eng


def build_fake_failure(gate_id, message):
    module, gate = gate_id.split(':')
    return {
        'module': module,
        'gate': gate,
        'gate_id': gate_id,
        'severity': 'CRITICAL',
        'message': message,
        'suggestion': message,
        'legal_source': '',
        'details': [],
        'excerpt': '',
    }


def test_sanitizer_absolute_claims():
    sanitizer = TextSanitizer()
    text = "Guaranteed 15% returns with zero risk for everyone."
    failures = [build_fake_failure('fca_uk:fair_clear_not_misleading', 'Misleading guarantee detected')]
    result = sanitizer.sanitize(text, failures)
    assert 'not guaranteed' in result['sanitized_text'].lower()
    assert result['actions']


def test_sanitizer_generalises_new_gate():
    sanitizer = TextSanitizer()
    text = "We share your medical records with partners."
    fake_gate = build_fake_failure('hipaa_us:phi_disclosure', 'Protected information disclosure detected')
    result = sanitizer.sanitize(text, [fake_gate])
    assert result['sanitized_text'] != text
    assert result['actions']


def test_snippet_mapper_domain_detection():
    registry = SnippetRegistry()
    mapper = UniversalSnippetMapper(registry)
    failure = build_fake_failure('gdpr_uk:purpose', 'Purpose needs to be explicit')
    plan = mapper.map_gate_to_snippet('gdpr_uk:purpose', failure)
    assert plan is not None
    assert plan.domain in {'definition', 'disclosure'}


def test_engine_full_flow(engine):
    synthesis = SynthesisEngine(engine)
    text = "Guaranteed 15% returns with zero risk for everyone."
    validation = engine.check_document(text, 'ai_generated', ['fca_uk'])
    result = synthesis.synthesize(text, validation, context={'firm_name': 'Test Firm'}, modules=['fca_uk'])
    assert result['snippets_applied']
    assert result['sanitization']['actions']
    assert result['final_validation']
