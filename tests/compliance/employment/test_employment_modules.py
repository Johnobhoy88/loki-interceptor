"""
Comprehensive Test Suite for Employment Compliance Modules
Tests all employment law validators and checkers
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from compliance.employment.era_2023 import EmploymentRightsAct2023Checker
from compliance.employment.worker_status import WorkerStatusDetermination, WorkerStatus


class TestERA2023Checker:
    """Test Employment Rights Act 2023 compliance checker"""

    def setup_method(self):
        self.checker = EmploymentRightsAct2023Checker()

    def test_day_one_flexible_working(self):
        text = "All employees have the right to request flexible working from day one of employment."
        result = self.checker.check(text)
        assert 'flexible_working_day_one' in [p['provision'] for p in result['provisions_found']]

    def test_carers_leave(self):
        text = "Employees are entitled to one week of unpaid carer's leave per year from day one."
        result = self.checker.check(text)
        assert 'carers_leave' in [p['provision'] for p in result['provisions_found']]

    def test_neonatal_care(self):
        text = "Each parent is entitled to 12 weeks neonatal care leave if baby is in NICU for 7+ days."
        result = self.checker.check(text)
        assert 'neonatal_care' in [p['provision'] for p in result['provisions_found']]

    def test_compliance_scoring(self):
        comprehensive_text = """
        Day one flexible working rights. Carer's leave available.
        Neonatal care leave provided. Tips distributed fairly.
        No fire and rehire. Pregnancy redundancy protection.
        """
        result = self.checker.check(comprehensive_text)
        assert result['compliance_percentage'] > 80
        assert result['status'] == 'PASS'


class TestWorkerStatusDetermination:
    """Test worker status determination logic"""

    def setup_method(self):
        self.determiner = WorkerStatusDetermination()

    def test_employee_status(self):
        contract = """
        You are required to work 40 hours per week as directed by your manager.
        You must personally perform all duties and cannot send a substitute.
        The company will provide all equipment and you will work from our office.
        You may not work for any other employer during your employment.
        """
        result = self.determiner.determine_status(contract)
        assert result['status'] == WorkerStatus.EMPLOYEE
        assert result['confidence'] in ['medium', 'high']

    def test_self_employed_status(self):
        contract = """
        You operate your own business and may send a substitute at any time.
        You are free to work for multiple clients and take on other engagements.
        You provide your own equipment and tools and invoice for services.
        You bear all business risk including profit and loss.
        """
        result = self.determiner.determine_status(contract)
        assert result['status'] == WorkerStatus.SELF_EMPLOYED

    def test_worker_status(self):
        contract = """
        You will personally provide services under this contract.
        The contract is for services not as a client or customer.
        You may accept or refuse individual assignments.
        """
        result = self.determiner.determine_status(contract)
        assert result['status'] in [WorkerStatus.WORKER, WorkerStatus.EMPLOYEE]

    def test_unclear_status(self):
        contract = """
        This is a contract between the parties.
        Work shall be performed as agreed.
        """
        result = self.determiner.determine_status(contract)
        assert result['status'] == WorkerStatus.UNCLEAR
        assert result['confidence'] == 'low'


class TestIntegration:
    """Integration tests for compliance modules"""

    def test_settlement_agreement_validity(self):
        from compliance.employment.settlements import SettlementAgreementCompliance

        checker = SettlementAgreementCompliance()

        valid_agreement = """
        This settlement agreement is made in writing.
        The employee has received independent legal advice from a qualified solicitor.
        The adviser has professional indemnity insurance in force.
        This agreement relates to the particular complaint of unfair dismissal.
        The adviser certifies that advice has been provided.
        """

        result = checker.validate(valid_agreement)
        assert result['status'] == 'PASS'

    def test_tupe_compliance(self):
        from compliance.employment.tupe import TUPETransferValidator

        validator = TUPETransferValidator()

        tupe_doc = """
        This is a relevant transfer under TUPE Regulations 2006.
        Employees transfer automatically with protected terms and conditions.
        Full consultation will be conducted with employee representatives.
        Employee Liability Information (ELI) will be provided 28 days before transfer.
        """

        result = validator.validate(tupe_doc)
        assert result['status'] == 'PASS'


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
