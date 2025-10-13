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


class TaxUkModule:
    def __init__(self):
        self.name = "UK Tax Compliance"
        self.version = "1.0.0"
        self.gates = {
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
        }

    def execute(self, text, document_type):
        results = {'gates': {}}
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
