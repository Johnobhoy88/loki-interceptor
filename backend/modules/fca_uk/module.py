from .gates.outcomes_coverage import OutcomesCoverageGate
from .gates.cross_cutting_rules import CrossCuttingRulesGate
from .gates.fair_value import FairValueGate
from .gates.comprehension_aids import ComprehensionAidsGate
from .gates.support_journey import SupportJourneyGate
from .gates.fair_clear_not_misleading import FairClearNotMisleadingGate
from .gates.risk_benefit_balance import RiskBenefitBalanceGate
from .gates.target_audience import TargetAudienceGate
from .gates.finfluencer_controls import FinfluencerControlsGate
from .gates.complaint_route_clock import ComplaintRouteClockGate
from .gates.fos_signposting import FosSignpostingGate
from .gates.vulnerability_identification import VulnerabilityIdentificationGate
from .gates.reasonable_adjustments import ReasonableAdjustmentsGate
from .gates.target_market_definition import TargetMarketDefinitionGate
from .gates.distribution_controls import DistributionControlsGate
from .gates.fair_value_assessment_ref import FairValueAssessmentRefGate
from .gates.conflicts_declaration import ConflictsDeclarationGate
from .gates.inducements_referrals import InducementsReferralsGate
from .gates.personal_dealing import PersonalDealingGate
from .gates.defined_roles import DefinedRolesGate
from .gates.record_keeping import RecordKeepingGate
from .gates.client_money_segregation import ClientMoneySegregationGate
from .gates.third_party_banks import ThirdPartyBanksGate
from .gates.no_implicit_advice import NoImplicitAdviceGate
from .gates.promotions_approval import PromotionsApprovalGate


class FcaUkModule:
    def __init__(self):
        self.name = "FCA UK Compliance"
        self.version = "1.0.0"
        self.gates = {
            # A) Consumer Duty (PRIN 2A) - Critical/High
            'outcomes_coverage': OutcomesCoverageGate(),
            'cross_cutting_rules': CrossCuttingRulesGate(),
            'fair_value': FairValueGate(),
            'comprehension_aids': ComprehensionAidsGate(),
            'support_journey': SupportJourneyGate(),

            # B) Financial Promotions (COBS 4) - Critical/High
            'fair_clear_not_misleading': FairClearNotMisleadingGate(),
            'risk_benefit_balance': RiskBenefitBalanceGate(),
            'target_audience': TargetAudienceGate(),
            'finfluencer_controls': FinfluencerControlsGate(),

            # C) Complaints (DISP) - Critical
            'complaint_route_clock': ComplaintRouteClockGate(),
            'fos_signposting': FosSignpostingGate(),

            # D) Vulnerable Customers (FG21/1) - High/Medium
            'vulnerability_identification': VulnerabilityIdentificationGate(),
            'reasonable_adjustments': ReasonableAdjustmentsGate(),

            # E) Product Governance (PROD) - High/Medium
            'target_market_definition': TargetMarketDefinitionGate(),
            'distribution_controls': DistributionControlsGate(),
            'fair_value_assessment_ref': FairValueAssessmentRefGate(),

            # F) Conflicts & Inducements - High/Medium
            'conflicts_declaration': ConflictsDeclarationGate(),
            'inducements_referrals': InducementsReferralsGate(),
            'personal_dealing': PersonalDealingGate(),

            # G) Systems & Controls - Medium
            'defined_roles': DefinedRolesGate(),
            'record_keeping': RecordKeepingGate(),

            # H) Client Assets (CASS) - Critical/High
            'client_money_segregation': ClientMoneySegregationGate(),
            'third_party_banks': ThirdPartyBanksGate(),

            # I) Suitability - Critical
            'no_implicit_advice': NoImplicitAdviceGate(),
            'promotions_approval': PromotionsApprovalGate(),
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
