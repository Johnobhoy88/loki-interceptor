"""
UK Employment Law Module
Compliance gates for UK employment regulations including:
- Employment contracts (zero-hours, fixed-term, probation)
- Redundancy procedures (TUPE, consultation)
- Discrimination law (9 protected characteristics)
- Working time regulations
- Health & Safety (RIDDOR)
"""

from .gates.employment_contracts import EmploymentContractsGate
from .gates.redundancy_procedures import RedundancyProceduresGate
from .gates.discrimination_law import DiscriminationLawGate
from .gates.working_time_regulations import WorkingTimeRegulationsGate
from .gates.health_safety import HealthSafetyGate


class UkEmploymentModule:
    """UK Employment Law compliance module"""

    def __init__(self):
        self.name = "UK Employment Law"
        self.version = "1.0.0"
        self.description = "UK employment law compliance gates (2025 regulations)"
        self.gates = {
            'employment_contracts': EmploymentContractsGate(),
            'redundancy_procedures': RedundancyProceduresGate(),
            'discrimination_law': DiscriminationLawGate(),
            'working_time_regulations': WorkingTimeRegulationsGate(),
            'health_safety': HealthSafetyGate(),
        }

    def execute(self, text, document_type='employment'):
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
