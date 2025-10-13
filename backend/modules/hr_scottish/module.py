from .gates.accompaniment import AccompanimentGate
from .gates.evidence import EvidenceGate
from .gates.appeal import AppealGate
from .gates.allegations import AllegationsGate
from .gates.dismissal import DismissalGate
from .gates.meeting_notice import MeetingNoticeGate
from .gates.investigation import InvestigationGate
from .gates.witness_statements import WitnessStatementsGate
from .gates.meeting_notes import MeetingNotesGate
from .gates.suspension import SuspensionGate
from .gates.previous_warnings import PreviousWarningsGate
from .gates.outcome_reasons import OutcomeReasonsGate
from .gates.representation_choice import RepresentationChoiceGate
from .gates.timeframes import TimeframesGate
from .gates.consistency import ConsistencyGate
from .gates.informal_threats import InformalThreatsGate


class HrScottishModule:
    def __init__(self):
        self.name = "HR Scottish Compliance"
        self.version = "2.0.0"
        self.gates = {
            'informal_threats': InformalThreatsGate(),
            'accompaniment': AccompanimentGate(),
            'evidence': EvidenceGate(),
            'appeal': AppealGate(),
            'allegations': AllegationsGate(),
            'dismissal': DismissalGate(),
            'meeting_notice': MeetingNoticeGate(),
            'investigation': InvestigationGate(),
            'witness_statements': WitnessStatementsGate(),
            'meeting_notes': MeetingNotesGate(),
            'suspension': SuspensionGate(),
            'previous_warnings': PreviousWarningsGate(),
            'outcome_reasons': OutcomeReasonsGate(),
            'representation_choice': RepresentationChoiceGate(),
            'timeframes': TimeframesGate(),
            'consistency': ConsistencyGate()
        }

    def execute(self, text, document_type):
        """Run all gates and return results"""
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
