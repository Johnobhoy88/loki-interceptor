# Original gates
from .gates.vat_invoice_integrity import VatInvoiceIntegrityGate
from .gates.vat_number_format import VatNumberFormatGate
from .gates.vat_rate_accuracy import VatRateAccuracyGate
from .gates.vat_threshold import VatThresholdGate
from .gates.invoice_legal_requirements import InvoiceLegalRequirementsGate
from .gates.company_limited_suffix import CompanyLimitedSuffixGate
from .gates.tax_deadline_accuracy import TaxDeadlineAccuracyGate
from .gates.mtd_compliance import MtdComplianceGate
from .gates.allowable_expenses import AllowableExpensesGate
from .gates.capital_revenue_distinction import CapitalRevenueDistinctionGate
from .gates.business_structure_consistency import BusinessStructureConsistencyGate
from .gates.hmrc_scam_detection import HmrcScamDetectionGate
from .gates.scottish_tax_specifics import ScottishTaxSpecificsGate
from .gates.invoice_numbering import InvoiceNumberingGate
from .gates.payment_method_validation import PaymentMethodValidationGate

# VAT gates (additional)
from .gates.vat_flat_rate_scheme import VatFlatRateSchemeGate
from .gates.vat_partial_exemption import VatPartialExemptionGate

# Corporation Tax gates
from .gates.ct_rate_validation import CtRateValidationGate
from .gates.ct_marginal_relief import CtMarginalReliefGate
from .gates.ct_associated_companies import CtAssociatedCompaniesGate
from .gates.ct_accounting_period import CtAccountingPeriodGate
from .gates.ct_payment_deadlines import CtPaymentDeadlinesGate
from .gates.ct_quarterly_instalments import CtQuarterlyInstalmentsGate
from .gates.ct_capital_allowances import CtCapitalAllowancesGate
from .gates.ct_intangible_assets import CtIntangibleAssetsGate
from .gates.ct_loan_relationships import CtLoanRelationshipsGate
from .gates.ct_distributions import CtDistributionsGate
from .gates.ct_group_relief import CtGroupReliefGate
from .gates.ct_losses import CtLossesGate

# PAYE/NIC gates
from .gates.paye_tax_code import PayeTaxCodeGate
from .gates.paye_scottish_tax import PayeScottishTaxGate
from .gates.paye_student_loan import PayeStudentLoanGate
from .gates.ni_category_validation import NiCategoryValidationGate
from .gates.paye_benefits_in_kind import PayeBenefitsInKindGate
from .gates.paye_expenses import PayeExpensesGate
from .gates.paye_termination_payments import PayeTerminationPaymentsGate
from .gates.paye_personal_allowance_taper import PayePersonalAllowanceTaperGate
from .gates.paye_pension_contributions import PayePensionContributionsGate
from .gates.ni_employment_allowance import NiEmploymentAllowanceGate

# Self-Assessment gates
from .gates.sa_registration_requirement import SaRegistrationRequirementGate
from .gates.sa_filing_deadlines import SaFilingDeadlinesGate
from .gates.sa_payment_on_account import SaPaymentOnAccountGate
from .gates.sa_penalties import SaPenaltiesGate
from .gates.sa_trading_allowance import SaTradingAllowanceGate
from .gates.sa_property_allowance import SaPropertyAllowanceGate
from .gates.sa_high_earner_check import SaHighEarnerCheckGate
from .gates.sa_class2_nic import SaClass2NicGate

# Capital Gains Tax gates
from .gates.cgt_rate_validation import CgtRateValidationGate
from .gates.cgt_annual_exempt_amount import CgtAnnualExemptAmountGate
from .gates.cgt_property_disposal import CgtPropertyDisposalGate
from .gates.cgt_badr_validation import CgtBadrValidationGate
from .gates.cgt_private_residence_relief import CgtPrivateResidenceReliefGate
from .gates.cgt_share_matching import CgtShareMatchingGate
from .gates.cgt_business_asset_rollover import CgtBusinessAssetRolloverGate
from .gates.cgt_crypto_assets import CgtCryptoAssetsGate

# Inheritance Tax gates
from .gates.iht_nil_rate_band import IhtNilRateBandGate
from .gates.iht_residence_nil_rate_band import IhtResidenceNilRateBandGate
from .gates.iht_rate_validation import IhtRateValidationGate
from .gates.iht_seven_year_rule import IhtSevenYearRuleGate
from .gates.iht_exemptions import IhtExemptionsGate
from .gates.iht_taper_relief import IhtTaperReliefGate
from .gates.iht_lifetime_transfers import IhtLifetimeTransfersGate

# MTD gates
from .gates.mtd_vat_mandatory import MtdVatMandatoryGate
from .gates.mtd_digital_records import MtdDigitalRecordsGate
from .gates.mtd_digital_links import MtdDigitalLinksGate
from .gates.mtd_itsa_thresholds import MtdItsaThresholdsGate
from .gates.mtd_quarterly_updates import MtdQuarterlyUpdatesGate

# IR35 gates
from .gates.ir35_control_test import Ir35ControlTestGate
from .gates.ir35_substitution import Ir35SubstitutionGate
from .gates.ir35_mutuality_obligation import Ir35MutualityObligationGate
from .gates.ir35_sds_requirement import Ir35SdsRequirementGate
from .gates.ir35_deemed_payment import Ir35DeemedPaymentGate

# R&D gates
from .gates.rd_qualifying_activity import RdQualifyingActivityGate
from .gates.rd_merged_scheme import RdMergedSchemeGate
from .gates.rd_qualifying_expenditure import RdQualifyingExpenditureGate
from .gates.rd_pre_notification import RdPreNotificationGate
from .gates.rd_additional_information import RdAdditionalInformationGate


class TaxUkModule:
    def __init__(self):
        self.name = "UK Tax Compliance - Enhanced"
        self.version = "2.0.0"
        self.gates = {
            # Original 15 gates
            'vat_invoice_integrity': VatInvoiceIntegrityGate(),
            'vat_number_format': VatNumberFormatGate(),
            'vat_rate_accuracy': VatRateAccuracyGate(),
            'vat_threshold': VatThresholdGate(),
            'invoice_legal_requirements': InvoiceLegalRequirementsGate(),
            'company_limited_suffix': CompanyLimitedSuffixGate(),
            'tax_deadline_accuracy': TaxDeadlineAccuracyGate(),
            'mtd_compliance': MtdComplianceGate(),
            'allowable_expenses': AllowableExpensesGate(),
            'capital_revenue_distinction': CapitalRevenueDistinctionGate(),
            'business_structure_consistency': BusinessStructureConsistencyGate(),
            'hmrc_scam_detection': HmrcScamDetectionGate(),
            'scottish_tax_specifics': ScottishTaxSpecificsGate(),
            'invoice_numbering': InvoiceNumberingGate(),
            'payment_method_validation': PaymentMethodValidationGate(),

            # VAT gates (2 additional)
            'vat_flat_rate_scheme': VatFlatRateSchemeGate(),
            'vat_partial_exemption': VatPartialExemptionGate(),

            # Corporation Tax gates (12)
            'ct_rate_validation': CtRateValidationGate(),
            'ct_marginal_relief': CtMarginalReliefGate(),
            'ct_associated_companies': CtAssociatedCompaniesGate(),
            'ct_accounting_period': CtAccountingPeriodGate(),
            'ct_payment_deadlines': CtPaymentDeadlinesGate(),
            'ct_quarterly_instalments': CtQuarterlyInstalmentsGate(),
            'ct_capital_allowances': CtCapitalAllowancesGate(),
            'ct_intangible_assets': CtIntangibleAssetsGate(),
            'ct_loan_relationships': CtLoanRelationshipsGate(),
            'ct_distributions': CtDistributionsGate(),
            'ct_group_relief': CtGroupReliefGate(),
            'ct_losses': CtLossesGate(),

            # PAYE/NIC gates (10)
            'paye_tax_code': PayeTaxCodeGate(),
            'paye_scottish_tax': PayeScottishTaxGate(),
            'paye_student_loan': PayeStudentLoanGate(),
            'ni_category_validation': NiCategoryValidationGate(),
            'paye_benefits_in_kind': PayeBenefitsInKindGate(),
            'paye_expenses': PayeExpensesGate(),
            'paye_termination_payments': PayeTerminationPaymentsGate(),
            'paye_personal_allowance_taper': PayePersonalAllowanceTaperGate(),
            'paye_pension_contributions': PayePensionContributionsGate(),
            'ni_employment_allowance': NiEmploymentAllowanceGate(),

            # Self-Assessment gates (8)
            'sa_registration_requirement': SaRegistrationRequirementGate(),
            'sa_filing_deadlines': SaFilingDeadlinesGate(),
            'sa_payment_on_account': SaPaymentOnAccountGate(),
            'sa_penalties': SaPenaltiesGate(),
            'sa_trading_allowance': SaTradingAllowanceGate(),
            'sa_property_allowance': SaPropertyAllowanceGate(),
            'sa_high_earner_check': SaHighEarnerCheckGate(),
            'sa_class2_nic': SaClass2NicGate(),

            # CGT gates (8)
            'cgt_rate_validation': CgtRateValidationGate(),
            'cgt_annual_exempt_amount': CgtAnnualExemptAmountGate(),
            'cgt_property_disposal': CgtPropertyDisposalGate(),
            'cgt_badr_validation': CgtBadrValidationGate(),
            'cgt_private_residence_relief': CgtPrivateResidenceReliefGate(),
            'cgt_share_matching': CgtShareMatchingGate(),
            'cgt_business_asset_rollover': CgtBusinessAssetRolloverGate(),
            'cgt_crypto_assets': CgtCryptoAssetsGate(),

            # IHT gates (7)
            'iht_nil_rate_band': IhtNilRateBandGate(),
            'iht_residence_nil_rate_band': IhtResidenceNilRateBandGate(),
            'iht_rate_validation': IhtRateValidationGate(),
            'iht_seven_year_rule': IhtSevenYearRuleGate(),
            'iht_exemptions': IhtExemptionsGate(),
            'iht_taper_relief': IhtTaperReliefGate(),
            'iht_lifetime_transfers': IhtLifetimeTransfersGate(),

            # MTD gates (5)
            'mtd_vat_mandatory': MtdVatMandatoryGate(),
            'mtd_digital_records': MtdDigitalRecordsGate(),
            'mtd_digital_links': MtdDigitalLinksGate(),
            'mtd_itsa_thresholds': MtdItsaThresholdsGate(),
            'mtd_quarterly_updates': MtdQuarterlyUpdatesGate(),

            # IR35 gates (5)
            'ir35_control_test': Ir35ControlTestGate(),
            'ir35_substitution': Ir35SubstitutionGate(),
            'ir35_mutuality_obligation': Ir35MutualityObligationGate(),
            'ir35_sds_requirement': Ir35SdsRequirementGate(),
            'ir35_deemed_payment': Ir35DeemedPaymentGate(),

            # R&D gates (5)
            'rd_qualifying_activity': RdQualifyingActivityGate(),
            'rd_merged_scheme': RdMergedSchemeGate(),
            'rd_qualifying_expenditure': RdQualifyingExpenditureGate(),
            'rd_pre_notification': RdPreNotificationGate(),
            'rd_additional_information': RdAdditionalInformationGate(),
        }

        # Total: 74 gates (15 original + 59 new)
        self.total_gates = len(self.gates)

    def execute(self, text, document_type):
        results = {
            'gates': {},
            'summary': {
                'total_gates': self.total_gates,
                'module_version': self.version
            }
        }

        for name, gate in self.gates.items():
            try:
                results['gates'][name] = gate.check(text, document_type)
            except Exception as e:
                results['gates'][name] = {
                    'status': 'ERROR',
                    'severity': 'critical',
                    'message': f'Gate error: {str(e)}'
                }

        return results
