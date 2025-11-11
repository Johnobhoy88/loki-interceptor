"""
Tests for Risk Categorization Module
"""
import sys
sys.path.insert(0, '/home/user/loki-interceptor')

import pytest
from backend.compliance.fca.risk_categorizer import RiskCategorizer


class TestRiskCategorization:
    def setup_method(self):
        self.categorizer = RiskCategorizer()

    def test_high_risk_crypto(self):
        """Test crypto is categorized as high risk"""
        text = "Investment in cryptocurrency and digital tokens"
        result = self.categorizer.categorize_risk(text)
        assert result['risk_category'] == 'HIGH'
        assert result['risk_level'] == 'high'

    def test_high_risk_p2p(self):
        """Test P2P lending is high risk"""
        text = "Peer-to-peer lending platform offering returns of 8%"
        result = self.categorizer.categorize_risk(text)
        assert result['risk_category'] == 'HIGH'

    def test_medium_risk_equity_fund(self):
        """Test equity fund is medium risk"""
        text = "UK equity fund investing in FTSE 100 companies"
        result = self.categorizer.categorize_risk(text)
        assert result['risk_category'] == 'MEDIUM'

    def test_low_risk_savings(self):
        """Test savings account is low risk"""
        text = "Fixed term deposit account with guaranteed return"
        result = self.categorizer.categorize_risk(text)
        assert result['risk_category'] == 'LOW'

    def test_warnings_adequate_for_high_risk(self):
        """Test warning adequacy for high-risk products"""
        text = """
        High-risk cryptocurrency investment.
        This is speculative and you could lose all your money.
        No protection available.
        Complex and difficult to understand.
        Not suitable for all investors.
        """
        result = self.categorizer.categorize_risk(text)
        assert result['warnings_analysis']['adequate'] is True

    def test_warnings_inadequate_for_high_risk(self):
        """Test inadequate warnings for high-risk"""
        text = "Invest in crypto for high returns"
        result = self.categorizer.categorize_risk(text)
        assert result['warnings_analysis']['adequate'] is False

    def test_audience_appropriateness_high_risk_mass_market_fails(self):
        """Test high-risk to mass market fails"""
        text = """
        Cryptocurrency investment for everyone!
        All retail customers can invest.
        High-risk speculative investment.
        """
        result = self.categorizer.categorize_risk(text)
        audience_check = result['audience_check']
        assert audience_check['status'] == 'FAIL'

    def test_audience_appropriateness_high_risk_restricted_passes(self):
        """Test high-risk restricted to sophisticated passes"""
        text = """
        High-risk cryptocurrency investment.
        Restricted to sophisticated investors only.
        You could lose all your money.
        """
        result = self.categorizer.categorize_risk(text)
        audience_check = result['audience_check']
        assert audience_check['status'] == 'PASS'

    def test_comprehensive_risk_profile(self):
        """Test comprehensive risk profile assessment"""
        text = """
        Complex leveraged cryptocurrency derivative product.
        High volatility expected.
        Illiquid - difficult to sell quickly.
        Not regulated by the FCA.
        You could lose more than you invest due to leverage.
        """
        result = self.categorizer.assess_document_risk_profile(text)
        assert result['risk_score'] >= 70
        assert result['overall_risk_rating'] in ['HIGH RISK', 'VERY HIGH RISK']
        assert len(result['recommendations']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
