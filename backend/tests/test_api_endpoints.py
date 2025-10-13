import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import app


def test_modules_endpoint_returns_fca_modules():
    client = app.test_client()
    resp = client.get('/modules')
    assert resp.status_code == 200
    data = resp.get_json()
    module_ids = {mod['id'] for mod in data['modules']}
    assert module_ids == {
        'fca_consumer_duty',
        'fca_financial_promotions',
        'fca_conduct_rules',
        'fca_product_governance',
        'fca_complaints_disp',
        'fca_disclosure_cobs',
    }


def test_validate_document_basic_flow():
    client = app.test_client()
    payload = {
        'text': 'Guaranteed returns of 12% with no risk of loss.',
        'document_type': 'financial_promotion',
        'modules': ['fca_financial_promotions']
    }
    resp = client.post('/validate-document', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    gates = data['validation']['modules']['fca_financial_promotions']['gates']
    assert gates['risk_warnings']['status'] == 'FAIL'
