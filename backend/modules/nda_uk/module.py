from .gates.protected_whistleblowing import ProtectedWhistleblowingGate
from .gates.protected_crime_reporting import ProtectedCrimeReportingGate
from .gates.protected_harassment import ProtectedHarassmentGate
from .gates.definition_specificity import DefinitionSpecificityGate
from .gates.public_domain_exclusion import PublicDomainExclusionGate
from .gates.prior_knowledge_exclusion import PriorKnowledgeExclusionGate
from .gates.duration_reasonableness import DurationReasonablenessGate
from .gates.permitted_disclosures import PermittedDisclosuresGate
from .gates.governing_law import GoverningLawGate
from .gates.consideration import ConsiderationGate
from .gates.return_destruction import ReturnDestructionGate
from .gates.gdpr_compliance import GdprComplianceGate
from .gates.parties_identified import PartiesIdentifiedGate
from .gates.permitted_purpose import PermittedPurposeGate


class NdaUkModule:
    def __init__(self):
        self.name = "UK/EU NDA Compliance"
        self.version = "1.0.0"
        self.gates = {
            'protected_whistleblowing': ProtectedWhistleblowingGate(),
            'protected_crime_reporting': ProtectedCrimeReportingGate(),
            'protected_harassment': ProtectedHarassmentGate(),
            'definition_specificity': DefinitionSpecificityGate(),
            'public_domain_exclusion': PublicDomainExclusionGate(),
            'prior_knowledge_exclusion': PriorKnowledgeExclusionGate(),
            'duration_reasonableness': DurationReasonablenessGate(),
            'permitted_disclosures': PermittedDisclosuresGate(),
            'governing_law': GoverningLawGate(),
            'consideration': ConsiderationGate(),
            'return_destruction': ReturnDestructionGate(),
            'gdpr_compliance': GdprComplianceGate(),
            'parties_identified': PartiesIdentifiedGate(),
            'permitted_purpose': PermittedPurposeGate()
        }
    
    def execute(self, text, document_type):
        results = {'gates': {}}
        for gate_name, gate in self.gates.items():
            try:
                results['gates'][gate_name] = gate.check(text, document_type)
            except Exception as e:
                results['gates'][gate_name] = {
                    'status': 'ERROR',
                    'severity': 'critical',
                    'message': f'Gate error: {str(e)}'
                }
        return results
