"""
Tests for Consumer Duty Compliance Checker
"""
import sys
sys.path.insert(0, '/home/user/loki-interceptor')

import pytest
from backend.compliance.fca.consumer_duty import ConsumerDutyChecker


class TestConsumerDuty:
    def setup_method(self):
        self.checker = ConsumerDutyChecker()

    def test_products_services_outcome_pass(self):
        """Test Products & Services outcome passes with good content"""
        text = """
        This product is designed to meet the needs of customers seeking long-term growth.
        It is suitable for customers with medium risk tolerance.
        The product has been designed for our target market of retail investors aged 30-60.
        """
        result = self.checker.check_products_services_outcome(text)
        assert result['status'] == 'PASS'

    def test_products_services_outcome_fail(self):
        """Test Products & Services outcome fails with generic targeting"""
        text = """
        This product is suitable for everyone.
        All customers can buy this product regardless of need.
        """
        result = self.checker.check_products_services_outcome(text)
        assert result['status'] == 'FAIL'

    def test_price_value_outcome_pass(self):
        """Test Price & Value outcome passes"""
        text = """
        We have assessed fair value and confirmed that the price is reasonable.
        Total fees are 1.5% which represents value for money given the service provided.
        """
        result = self.checker.check_price_value_outcome(text)
        assert result['status'] == 'PASS'

    def test_price_value_outcome_fail(self):
        """Test Price & Value outcome fails with unfair pricing"""
        text = """
        Our fees are designed to maximize profit.
        Hidden charges apply.
        Price is not justified by the service.
        """
        result = self.checker.check_price_value_outcome(text)
        assert result['status'] == 'FAIL'

    def test_consumer_understanding_pass(self):
        """Test Consumer Understanding outcome passes"""
        text = """
        We use clear and simple language to explain our products.
        Key information is presented prominently.
        We avoid jargon and provide plain English explanations.
        """
        result = self.checker.check_consumer_understanding_outcome(text)
        assert result['status'] == 'PASS'

    def test_consumer_support_pass(self):
        """Test Consumer Support outcome passes"""
        text = """
        Our customer support team is available Monday-Friday 9am-5pm.
        You can contact us by phone at 0800 123 4567 or email support@example.com.
        We have a clear complaints process and can escalate to Financial Ombudsman.
        """
        result = self.checker.check_consumer_support_outcome(text)
        assert result['status'] == 'PASS'

    def test_all_outcomes_comprehensive(self):
        """Test comprehensive check across all outcomes"""
        text = """
        This investment product is designed to meet the needs of customers seeking capital growth
        over a minimum 5-year period. It is suitable for customers with medium to high risk tolerance
        who have experience of equity markets.

        We assess fair value annually and our prices represent good value for money.
        Total annual charges are 1.2% which is competitive for this type of fund.

        This document is written in clear, plain language. Key risks are highlighted prominently.

        Customer support available 9am-5pm weekdays on 0800 123 4567.
        Complaints process: contact our team, then escalate to Financial Ombudsman if needed.
        """
        result = self.checker.check_all_outcomes(text)
        assert result['status'] in ['PASS', 'WARNING']
        assert result['summary']['fails'] == 0


class TestForeseeableHarm:
    def setup_method(self):
        self.checker = ConsumerDutyChecker()

    def test_harm_prevention_mentioned(self):
        """Test foreseeable harm prevention is detected"""
        text = """
        We take steps to prevent foreseeable harm to customers.
        We avoid poor outcomes and mitigate risk of harm.
        """
        result = self.checker.assess_foreseeable_harm(text)
        assert result['status'] == 'PASS'

    def test_harm_scenarios_detected(self):
        """Test harmful scenarios are flagged"""
        text = """
        Customers are locked in for 10 years with penalties for early exit.
        Automatic renewal without notice.
        """
        result = self.checker.assess_foreseeable_harm(text)
        assert result['status'] == 'FAIL'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
