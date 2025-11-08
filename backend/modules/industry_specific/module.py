"""
Industry-Specific Module
Industry-specific compliance gates for:
- Healthcare (NHS, CQC, medical records)
- Education (KCSIE, SEND, safeguarding)
- Finance (AML/KYC, PSD2, SMCR)
- Construction (CDM, Building Regs, Building Safety Act)
- Technology (Open source licenses, SaaS, cloud)
"""

from .gates.healthcare_compliance import HealthcareComplianceGate
from .gates.education_compliance import EducationComplianceGate
from .gates.finance_compliance import FinanceComplianceGate
from .gates.construction_compliance import ConstructionComplianceGate
from .gates.technology_compliance import TechnologyComplianceGate


class IndustrySpecificModule:
    """Industry-Specific compliance module"""

    def __init__(self):
        self.name = "Industry-Specific"
        self.version = "1.0.0"
        self.description = "Industry-specific compliance gates (Healthcare, Education, Finance, Construction, Technology)"
        self.gates = {
            'healthcare_compliance': HealthcareComplianceGate(),
            'education_compliance': EducationComplianceGate(),
            'finance_compliance': FinanceComplianceGate(),
            'construction_compliance': ConstructionComplianceGate(),
            'technology_compliance': TechnologyComplianceGate(),
        }

    def execute(self, text, document_type='policy'):
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
