"""
Scottish Law Module
Scottish-specific compliance gates for Scots law differences:
- Employment law (5-year prescription)
- Contract law (no consideration, consensus in idem)
- Data protection (Scottish Information Commissioner)
- Property law (heritable property, Registers of Scotland)
- Corporate law (OSCR, Scottish charities)
"""

from .gates.scottish_employment import ScottishEmploymentGate
from .gates.scottish_contracts import ScottishContractsGate
from .gates.scottish_data_protection import ScottishDataProtectionGate
from .gates.scottish_property import ScottishPropertyGate
from .gates.scottish_corporate import ScottishCorporateGate


class ScottishLawModule:
    """Scottish Law compliance module"""

    def __init__(self):
        self.name = "Scottish Law"
        self.version = "1.0.0"
        self.description = "Scottish law compliance gates (Scots law differences)"
        self.gates = {
            'scottish_employment': ScottishEmploymentGate(),
            'scottish_contracts': ScottishContractsGate(),
            'scottish_data_protection': ScottishDataProtectionGate(),
            'scottish_property': ScottishPropertyGate(),
            'scottish_corporate': ScottishCorporateGate(),
        }

    def execute(self, text, document_type='contract'):
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
