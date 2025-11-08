"""
GDPR Advanced Module
Advanced GDPR compliance gates for:
- Data Use and Access Act 2025
- Automated decision-making (Article 22)
- Children's data protection
"""

from .gates.data_protection_advanced import DataProtectionAdvancedGate
from .gates.automated_decisions import AutomatedDecisionsGate
from .gates.children_data import ChildrenDataGate


class GdprAdvancedModule:
    """GDPR Advanced compliance module"""

    def __init__(self):
        self.name = "GDPR Advanced"
        self.version = "1.0.0"
        self.description = "Advanced GDPR compliance gates (Data Use and Access Act 2025)"
        self.gates = {
            'data_protection_advanced': DataProtectionAdvancedGate(),
            'automated_decisions': AutomatedDecisionsGate(),
            'children_data': ChildrenDataGate(),
        }

    def execute(self, text, document_type='privacy_policy'):
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
