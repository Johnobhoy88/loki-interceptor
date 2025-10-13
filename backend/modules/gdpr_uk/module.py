from .gates.consent import ConsentGate
from .gates.purpose import PurposeGate
from .gates.retention import RetentionGate
from .gates.rights import RightsGate
from .gates.security import SecurityGate
from .gates.lawful_basis import LawfulBasisGate
from .gates.data_minimisation import DataMinimisationGate
from .gates.third_party_sharing import ThirdPartySharingGate
from .gates.international_transfer import InternationalTransferGate
from .gates.automated_decisions import AutomatedDecisionsGate
from .gates.children_data import ChildrenDataGate
from .gates.breach_notification import BreachNotificationGate
from .gates.dpo_contact import DpoContactGate
from .gates.cookies_tracking import CookiesTrackingGate
from .gates.withdrawal_consent import WithdrawalConsentGate


class GdprUkModule:
    def __init__(self):
        self.name = "GDPR UK Compliance"
        self.version = "2.0.0"
        self.gates = {
            'consent': ConsentGate(),
            'purpose': PurposeGate(),
            'retention': RetentionGate(),
            'rights': RightsGate(),
            'security': SecurityGate(),
            'lawful_basis': LawfulBasisGate(),
            'data_minimisation': DataMinimisationGate(),
            'third_party_sharing': ThirdPartySharingGate(),
            'international_transfer': InternationalTransferGate(),
            'automated_decisions': AutomatedDecisionsGate(),
            'children_data': ChildrenDataGate(),
            'breach_notification': BreachNotificationGate(),
            'dpo_contact': DpoContactGate(),
            'cookies_tracking': CookiesTrackingGate(),
            'withdrawal_consent': WithdrawalConsentGate(),
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
