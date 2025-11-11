"""Tests for Tax UK Gates"""
import pytest
from backend.modules.tax_uk.module import TaxUkModule


class TestTaxGates:
    def setup_method(self):
        self.module = TaxUkModule()

    def test_module_initialization(self):
        """Test module initializes with correct number of gates"""
        assert self.module.total_gates == 74
        assert len(self.module.gates) == 74
        assert self.module.version == "2.0.0"

    def test_vat_rate_accuracy(self):
        """Test VAT rate accuracy gate"""
        text = "VAT will be charged at 17.5%"
        result = self.module.execute(text, "invoice")

        assert 'vat_rate_accuracy' in result['gates']
        gate_result = result['gates']['vat_rate_accuracy']
        assert gate_result['status'] == 'FAIL'

    def test_ct_rate_validation(self):
        """Test Corporation Tax rate validation gate"""
        text = "Corporation tax is charged at 30%"
        result = self.module.execute(text, "tax_document")

        assert 'ct_rate_validation' in result['gates']
        gate_result = result['gates']['ct_rate_validation']
        assert gate_result['status'] in ['FAIL', 'WARNING']

    def test_mtd_compliance(self):
        """Test MTD compliance gate"""
        text = "MTD for VAT is optional for all businesses"
        result = self.module.execute(text, "guidance")

        assert 'mtd_compliance' in result['gates']
        gate_result = result['gates']['mtd_compliance']
        assert gate_result['status'] == 'FAIL'

    def test_scottish_tax_gate(self):
        """Test Scottish tax gate"""
        text = "Scottish income tax rates apply in Scotland"
        result = self.module.execute(text, "tax_document")

        assert 'paye_scottish_tax' in result['gates']
        assert 'scottish_tax_specifics' in result['gates']

    def test_cgt_annual_exempt_amount(self):
        """Test CGT annual exempt amount gate"""
        text = "Capital Gains Tax annual allowance is £12,300"
        result = self.module.execute(text, "guidance")

        assert 'cgt_annual_exempt_amount' in result['gates']

    def test_iht_nil_rate_band(self):
        """Test IHT nil rate band gate"""
        text = "Inheritance Tax nil rate band is £300,000"
        result = self.module.execute(text, "will")

        assert 'iht_nil_rate_band' in result['gates']

    def test_ir35_gates_present(self):
        """Test IR35 gates are present"""
        ir35_gates = [
            'ir35_control_test',
            'ir35_substitution',
            'ir35_mutuality_obligation',
            'ir35_sds_requirement',
            'ir35_deemed_payment'
        ]

        for gate in ir35_gates:
            assert gate in self.module.gates

    def test_rd_gates_present(self):
        """Test R&D gates are present"""
        rd_gates = [
            'rd_qualifying_activity',
            'rd_merged_scheme',
            'rd_qualifying_expenditure',
            'rd_pre_notification',
            'rd_additional_information'
        ]

        for gate in rd_gates:
            assert gate in self.module.gates

    def test_comprehensive_check(self):
        """Test comprehensive document check"""
        text = """
        VAT Invoice
        VAT at 20%
        Corporation tax at 25%
        MTD compliant
        Scottish tax rates apply
        """
        result = self.module.execute(text, "invoice")

        assert 'gates' in result
        assert 'summary' in result
        assert result['summary']['total_gates'] == 74
        assert result['summary']['module_version'] == "2.0.0"

    def test_error_handling(self):
        """Test gate error handling"""
        result = self.module.execute(None, "test")

        assert 'gates' in result
        # Most gates should return N/A for None text
        n_a_count = sum(1 for gate_result in result['gates'].values()
                       if gate_result.get('status') == 'N/A')
        assert n_a_count > 0
