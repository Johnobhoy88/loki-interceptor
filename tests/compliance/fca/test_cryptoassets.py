"""
Tests for Cryptoasset Promotion Validator
"""
import sys
sys.path.insert(0, '/home/user/loki-interceptor')

import pytest
from backend.compliance.fca.cryptoassets import CryptoPromotionValidator


class TestCryptoPromotions:
    def setup_method(self):
        self.validator = CryptoPromotionValidator()

    def test_crypto_detection(self):
        """Test crypto promotion detection"""
        text = "Invest in Bitcoin and Ethereum for high returns"
        assert self.validator._is_crypto_promotion(text) is True

    def test_non_crypto_ignored(self):
        """Test non-crypto content is ignored"""
        text = "Our savings account offers competitive interest rates"
        result = self.validator.check_crypto_promotion(text)
        assert result['status'] == 'N/A'

    def test_risk_warning_present(self):
        """Test risk warning passes when present"""
        text = """
        Invest in cryptocurrency.
        Don't invest unless you're prepared to lose all the money you invest.
        This is a high-risk investment and you are unlikely to be protected if something goes wrong.
        """
        result = self.validator.check_risk_warning(text)
        assert result['status'] == 'PASS'

    def test_risk_warning_missing_fails(self):
        """Test missing risk warning fails"""
        text = "Invest in Bitcoin for great returns!"
        result = self.validator.check_risk_warning(text)
        assert result['status'] == 'FAIL'

    def test_no_protection_warning(self):
        """Test no protection warning check"""
        text = """
        Cryptocurrency investment.
        You are unlikely to be protected if something goes wrong.
        No FSCS protection applies.
        """
        result = self.validator.check_no_protection_warning(text)
        assert result['status'] == 'PASS'

    def test_cooling_off_required(self):
        """Test 24-hour cooling-off requirement"""
        text = """
        Buy Bitcoin now!
        Invest immediately.
        """
        result = self.validator.check_cooling_off_requirement(text)
        assert result['status'] == 'FAIL'

    def test_cooling_off_present(self):
        """Test cooling-off present passes"""
        text = """
        Cryptocurrency investment.
        24-hour cooling-off period applies.
        You must wait 24 hours after seeing the risk warning before investing.
        """
        result = self.validator.check_cooling_off_requirement(text)
        assert result['status'] == 'PASS'

    def test_incentives_ban(self):
        """Test banned incentives detection"""
        text = """
        Crypto trading platform.
        Refer-a-friend bonus: £50 for each friend who joins!
        Volume bonus: trade more to earn rewards.
        """
        result = self.validator.check_incentives_ban(text)
        assert result['status'] == 'FAIL'
        assert 'refer' in str(result.get('violations', []))

    def test_target_restriction_mass_market_fails(self):
        """Test mass market targeting fails"""
        text = """
        Cryptocurrency for everyone!
        Anyone can invest. No restrictions.
        """
        result = self.validator.check_target_restriction(text)
        assert result['status'] == 'FAIL'

    def test_comprehensive_crypto_promotion(self):
        """Test comprehensive crypto promotion check"""
        compliant_text = """
        Cryptocurrency Investment

        IMPORTANT: Don't invest unless you're prepared to lose all the money you invest.
        This is a high-risk investment and you are unlikely to be protected if something goes wrong.

        Cryptoassets are complex and high-risk investments.
        These assets are not regulated by the FCA.

        This offer is restricted to sophisticated investors only.

        You must wait 24 hours after reading this warning before proceeding.
        """
        result = self.validator.check_crypto_promotion(compliant_text)
        assert result['status'] in ['PASS', 'WARNING']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
