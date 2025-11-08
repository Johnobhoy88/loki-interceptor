"""
FCA Advanced Module
Advanced FCA compliance gates for:
- Financial services conduct rules
- Operational resilience (March 2025 deadline)
"""

from .gates.financial_services import FinancialServicesGate
from .gates.operational_resilience import OperationalResilienceGate


class FcaAdvancedModule:
    """FCA Advanced compliance module"""

    def __init__(self):
        self.name = "FCA Advanced"
        self.version = "1.0.0"
        self.description = "Advanced FCA compliance gates (Operational Resilience 2025)"
        self.gates = {
            'financial_services': FinancialServicesGate(),
            'operational_resilience': OperationalResilienceGate(),
        }

    def execute(self, text, document_type='financial'):
        """Execute all gates in the module"""
        results = {
            'module': self.name,
            'version': self.version,
            'gates': {}
        }

        for gate_name, gate in self.gates.items():
            try:
                gate_result = gate.check(text, document_type)
                results['gates'][gate_name] = gate_result
            except Exception as e:
                results['gates'][gate_name] = {
                    'status': 'ERROR',
                    'severity': 'critical',
                    'message': f'Gate execution error: {str(e)}'
                }

        return results
