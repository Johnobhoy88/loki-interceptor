from core.audit_log import AuditLogger


def build_validation_result():
    return {
        'overall_risk': 'HIGH',
        'modules': {
            'gdpr_uk': {
                'name': 'GDPR UK Compliance',
                'version': '2.0.0',
                'gates': {
                    'security': {
                        'status': 'FAIL',
                        'severity': 'critical',
                        'message': 'Encryption missing',
                        'legal_source': 'GDPR Art. 32',
                        'version': '1.2.0'
                    },
                    'rights': {
                        'status': 'PASS',
                        'severity': 'none',
                        'message': 'Rights covered',
                        'legal_source': 'GDPR Art. 15',
                        'version': '1.0.0'
                    }
                },
                'summary': {'fail': 1, 'pass': 1, 'warning': 0, 'error': 0, 'na': 0}
            }
        },
        'universal': {
            'harm': {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Violence detected'
            }
        },
        'analyzers': {
            'pii': {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Sensitive identifier present'
            }
        },
        'cross': {
            'issues': [
                {
                    'id': 'gdpr_breach_without_notification',
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Security issue with no notification path'
                }
            ]
        }
    }


def test_audit_logger_records_gate_details(tmp_path):
    db_path = tmp_path / 'audit.db'
    logger = AuditLogger(db_path=str(db_path))

    validation = build_validation_result()
    entry_id = logger.log_validation(
        text='Sample document',
        document_type='policy',
        modules_used=['gdpr_uk'],
        validation_result=validation,
        client_id='test-client'
    )
    assert entry_id > 0

    overview = logger.get_overview(window_days=7)
    assert overview['stats']['total_validations'] == 1
    assert overview['stats']['risk_breakdown']['high'] == 1
    assert overview['module_performance'][0]['module'] == 'gdpr_uk'

    modules = logger.get_module_performance(since=None)
    assert modules[0]['failures'] == 1

    universal = logger.get_universal_alerts(since=None)
    assert universal[0]['detector'] == 'harm'

    trends = logger.get_risk_trends(days=7)
    assert trends['timeline']
