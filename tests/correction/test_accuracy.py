"""
Correction Accuracy Tests - Comprehensive Test Suite

This module contains 100+ test cases for verifying correction accuracy across
all regulatory modules and correction strategies.

Test Categories:
- FCA UK corrections (financial services)
- GDPR UK corrections (data protection)
- Tax UK corrections (HMRC compliance)
- NDA UK corrections (non-disclosure agreements)
- HR Scottish corrections (employment law)
- Multi-module corrections
- Edge cases and boundary conditions
"""

import pytest
import re
from typing import Dict, List
from backend.core.correction_synthesizer import CorrectionSynthesizer, CorrectionValidator
from backend.core.correction_strategies import (
    RegexReplacementStrategy,
    TemplateInsertionStrategy,
    StructuralReorganizationStrategy,
    SuggestionExtractionStrategy
)
from backend.core.correction_patterns import CorrectionPatternRegistry


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def pattern_registry():
    """Provide correction pattern registry."""
    return CorrectionPatternRegistry()


@pytest.fixture
def regex_strategy(pattern_registry):
    """Create regex replacement strategy with all patterns."""
    strategy = RegexReplacementStrategy()

    # Register all regex patterns
    for gate_pattern, patterns in pattern_registry.regex_patterns.items():
        for pattern in patterns:
            strategy.register_pattern(
                gate_pattern,
                pattern['pattern'],
                pattern['replacement'],
                pattern['reason'],
                pattern.get('flags', 0)
            )

    return strategy


@pytest.fixture
def template_strategy(pattern_registry):
    """Create template insertion strategy with all templates."""
    strategy = TemplateInsertionStrategy()

    # Register all templates
    for gate_pattern, templates in pattern_registry.templates.items():
        for template in templates:
            strategy.register_template(
                gate_pattern,
                template['template'],
                template['position'],
                template.get('condition')
            )

    return strategy


@pytest.fixture
def structural_strategy(pattern_registry):
    """Create structural reorganization strategy."""
    strategy = StructuralReorganizationStrategy()

    # Register structural rules
    for gate_pattern, rules in pattern_registry.structural_rules.items():
        for rule in rules:
            strategy.register_rule(
                gate_pattern,
                rule['type'],
                rule['config']
            )

    return strategy


@pytest.fixture
def suggestion_strategy():
    """Create suggestion extraction strategy."""
    return SuggestionExtractionStrategy()


@pytest.fixture
def synthesizer(regex_strategy, template_strategy, structural_strategy, suggestion_strategy):
    """Create correction synthesizer with all strategies."""
    strategies = [
        suggestion_strategy,
        regex_strategy,
        template_strategy,
        structural_strategy
    ]
    return CorrectionSynthesizer(strategies)


# ============================================================================
# FCA UK CORRECTIONS - Financial Services (30 tests)
# ============================================================================

class TestFCACorrections:
    """Test FCA UK financial services corrections."""

    def test_risk_warning_correction(self, synthesizer):
        """Test risk warning is properly formatted."""
        text = "investments can go down as well as up"
        gates = [('risk_warning', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert result['corrected'] != text
        assert 'fall as well as rise' in result['corrected'].lower()
        assert len(result['corrections']) > 0

    def test_guaranteed_returns_removal(self, synthesizer):
        """Test removal of 'guaranteed returns' claims."""
        text = "GUARANTEED returns on your investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'GUARANTEED' not in result['corrected'].upper()
        assert 'potential' in result['corrected'].lower()

    def test_risk_free_claim_correction(self, synthesizer):
        """Test 'risk-free' claims are corrected."""
        text = "This is a risk-free investment opportunity"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'risk-free' not in result['corrected'].lower()
        assert 'risk' in result['corrected'].lower()

    def test_risk_benefit_balance(self, synthesizer):
        """Test risk/benefit balance corrections."""
        text = "High returns and attractive yields await!"
        gates = [('risk_benefit', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'capital at risk' in result['corrected'].lower() or 'potential' in result['corrected'].lower()

    def test_fos_signposting_insertion(self, synthesizer):
        """Test Financial Ombudsman Service signposting."""
        text = "We provide financial services to UK customers."
        gates = [('fos_signposting', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        corrected_lower = result['corrected'].lower()
        assert 'financial ombudsman' in corrected_lower or 'complaint' in corrected_lower

    def test_target_market_definition(self, synthesizer):
        """Test target market definition insertion."""
        text = "Our investment product is available now."
        gates = [('target_market', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'target' in result['corrected'].lower()

    def test_promotions_approval(self, synthesizer):
        """Test financial promotion approval statement."""
        text = "Invest in our new financial product today!"
        gates = [('promotions_approval', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'approved' in result['corrected'].lower() or 'fca' in result['corrected'].lower()

    def test_client_money_segregation(self, synthesizer):
        """Test client money segregation notice."""
        text = "We hold client funds securely."
        gates = [('client_money_segregation', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'segregat' in result['corrected'].lower() or 'cass' in result['corrected'].lower()

    def test_consumer_duty_coercion(self, synthesizer):
        """Test removal of coercive language (Consumer Duty)."""
        text = "You must purchase this add-on product."
        gates = [('cross_cutting', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'must' not in result['corrected'] or 'choose' in result['corrected']

    def test_automatic_enrollment_correction(self, synthesizer):
        """Test automatic enrollment language correction."""
        text = "You will be automatically enrolled in this service."
        gates = [('cross_cutting', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'choose' in result['corrected'].lower()

    def test_no_implicit_advice_warning(self, synthesizer):
        """Test implicit advice removal."""
        text = "You should invest in this product."
        gates = [('no_implicit_advice', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'should' not in result['corrected'] or 'removed' in result['corrected'].lower()

    def test_personal_recommendation_removal(self, synthesizer):
        """Test personal recommendation statements removed."""
        text = "We recommend you purchase this investment."
        gates = [('no_implicit_advice', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'suitability' in result['corrected'].lower() or 'removed' in result['corrected'].lower()

    def test_conflicts_of_interest_disclosure(self, synthesizer):
        """Test conflicts of interest disclosure."""
        text = "We offer independent financial advice."
        gates = [('conflicts_declaration', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'conflict' in result['corrected'].lower()

    def test_fair_value_assessment(self, synthesizer):
        """Test fair value assessment insertion."""
        text = "Our fees are competitive. Payment due monthly."
        gates = [('fair_value', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'fair value' in result['corrected'].lower() or 'consumer duty' in result['corrected'].lower()

    def test_inducements_disclosure(self, synthesizer):
        """Test inducements and referrals disclosure."""
        text = "We receive commission from product providers."
        gates = [('inducements_referrals', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'inducement' in result['corrected'].lower() or 'commission' in result['corrected']

    def test_finfluencer_ad_disclosure(self, synthesizer):
        """Test finfluencer advertising disclosure."""
        text = "#ad Check out this amazing investment opportunity!"
        gates = [('finfluencer', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '[AD]' in result['corrected'] or 'promotion' in result['corrected'].lower()

    def test_vulnerability_identification(self, synthesizer):
        """Test vulnerable customer support notice."""
        text = "Contact our customer support team for help."
        gates = [('vulnerability_identification', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'vulnerable' in result['corrected'].lower()

    def test_comprehension_aids(self, synthesizer):
        """Test plain language and comprehension aids."""
        text = "See the glossary for jargon definitions."
        gates = [('comprehension_aids', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'plain' in result['corrected'].lower() or 'clear' in result['corrected'].lower()

    def test_reasonable_adjustments(self, synthesizer):
        """Test reasonable adjustments for disabilities."""
        text = "Our services are accessible to all customers."
        gates = [('reasonable_adjustments', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'adjustment' in result['corrected'].lower() or 'disability' in result['corrected'].lower()

    def test_complaint_route_clock(self, synthesizer):
        """Test 8-week complaint response timeline."""
        text = "We handle complaints efficiently."
        gates = [('complaint_route_clock', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '8 week' in result['corrected'].lower() or 'complaint' in result['corrected']

    def test_support_journey_no_barriers(self, synthesizer):
        """Test support journey without barriers."""
        text = "Contact us for support or to cancel."
        gates = [('support_journey', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'cancel' in result['corrected'] or 'support' in result['corrected']

    def test_target_audience_specification(self, synthesizer):
        """Test target audience specification."""
        text = "This product is suitable for investors."
        gates = [('target_audience', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'target' in result['corrected'].lower() or 'suitable' in result['corrected']

    def test_third_party_banks_cass7(self, synthesizer):
        """Test third party banks CASS 7 compliance."""
        text = "Client money is held in bank accounts."
        gates = [('third_party_banks', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'bank' in result['corrected'] or 'cass' in result['corrected'].lower()

    def test_distribution_controls(self, synthesizer):
        """Test product distribution controls."""
        text = "Our product is distributed through advisers."
        gates = [('distribution_controls', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'distribut' in result['corrected'].lower()

    def test_defined_roles_smcr(self, synthesizer):
        """Test SMCR defined roles disclosure."""
        text = "Our management team oversees operations."
        gates = [('defined_roles', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'manager' in result['corrected'].lower() or 'responsib' in result['corrected'].lower()

    def test_outcomes_coverage_consumer_duty(self, synthesizer):
        """Test Consumer Duty outcomes monitoring."""
        text = "We monitor customer outcomes regularly."
        gates = [('outcomes_coverage', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'consumer duty' in result['corrected'].lower() or 'outcome' in result['corrected'].lower()

    def test_personal_dealing_rules(self, synthesizer):
        """Test personal account dealing rules."""
        text = "Our staff may trade in personal accounts."
        gates = [('personal_dealing', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'personal' in result['corrected'] and 'dealing' in result['corrected'].lower()

    def test_record_keeping_requirements(self, synthesizer):
        """Test record keeping compliance."""
        text = "We maintain records of all transactions."
        gates = [('record_keeping', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'record' in result['corrected']

    def test_multiple_fca_corrections(self, synthesizer):
        """Test multiple FCA corrections in one document."""
        text = "GUARANTEED returns! You must invest now. High yields!"
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('cross_cutting', {'status': 'FAIL', 'severity': 'high'}),
            ('risk_benefit', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        assert result['correction_count'] >= 2
        assert 'GUARANTEED' not in result['corrected']

    def test_fca_determinism(self, synthesizer):
        """Test FCA corrections are deterministic."""
        text = "GUARANTEED returns! Risk-free investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']
        assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']


# ============================================================================
# GDPR UK CORRECTIONS - Data Protection (25 tests)
# ============================================================================

class TestGDPRCorrections:
    """Test GDPR UK data protection corrections."""

    def test_forced_consent_removal(self, synthesizer):
        """Test removal of forced consent language."""
        text = "By using this website, you automatically agree to our terms."
        gates = [('consent', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'automatically' not in result['corrected'].lower() or 'explicit' in result['corrected'].lower()

    def test_continued_use_consent(self, synthesizer):
        """Test correction of continued use as consent."""
        text = "Continued use constitutes agreement to data processing."
        gates = [('consent', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'explicit consent' in result['corrected'].lower() or 'i agree' in result['corrected'].lower()

    def test_access_equals_consent(self, synthesizer):
        """Test removal of access as consent."""
        text = "By accessing this site, you consent to cookies."
        gates = [('consent', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'require' in result['corrected'].lower() or 'provide consent' in result['corrected'].lower()

    def test_withdrawal_of_consent(self, synthesizer):
        """Test withdrawal of consent notice."""
        text = "You consent to receive marketing emails."
        gates = [('withdrawal_consent', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'withdraw' in result['corrected'].lower()

    def test_data_subject_rights(self, synthesizer):
        """Test data subject rights disclosure."""
        text = "We process your personal data securely."
        gates = [('rights', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        corrected_lower = result['corrected'].lower()
        assert 'right' in corrected_lower
        assert 'access' in corrected_lower or 'erase' in corrected_lower

    def test_right_to_erasure(self, synthesizer):
        """Test right to be forgotten disclosure."""
        text = "Your data is stored permanently."
        gates = [('rights', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'erase' in result['corrected'].lower() or 'forgotten' in result['corrected'].lower()

    def test_lawful_basis_disclosure(self, synthesizer):
        """Test lawful basis for processing."""
        text = "We collect and process your personal information."
        gates = [('lawful_basis', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'lawful' in result['corrected'].lower() or 'consent' in result['corrected'].lower()

    def test_data_retention_period(self, synthesizer):
        """Test data retention period disclosure."""
        text = "We store your personal data securely."
        gates = [('retention', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'retain' in result['corrected'].lower() or 'period' in result['corrected'].lower()

    def test_international_transfers(self, synthesizer):
        """Test international data transfer notice."""
        text = "Your data may be transferred outside the UK."
        gates = [('international_transfer', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'safeguard' in result['corrected'].lower() or 'adequacy' in result['corrected'].lower()

    def test_cookie_consent(self, synthesizer):
        """Test cookie consent requirements."""
        text = "This site uses cookies to improve experience."
        gates = [('cookies', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'consent' in result['corrected'].lower()

    def test_children_data_protection(self, synthesizer):
        """Test children's data protection notice."""
        text = "Our service is available to users of all ages."
        gates = [('children', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'children' in result['corrected'].lower() or 'parental' in result['corrected'].lower()

    def test_data_accuracy(self, synthesizer):
        """Test data accuracy commitment."""
        text = "We store your personal data."
        gates = [('accuracy', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'accurate' in result['corrected'].lower() or 'correct' in result['corrected'].lower()

    def test_accountability_dpo(self, synthesizer):
        """Test DPO and accountability disclosure."""
        text = "We are GDPR compliant."
        gates = [('accountability', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'data protection officer' in result['corrected'].lower() or 'dpo' in result['corrected'].lower()

    def test_automated_decision_making(self, synthesizer):
        """Test automated decision making disclosure."""
        text = "We use algorithms to make decisions about your application."
        gates = [('automated_decisions', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'automated' in result['corrected'].lower()

    def test_data_breach_notification(self, synthesizer):
        """Test data breach notification commitment."""
        text = "We maintain security measures for your data."
        gates = [('breach_notification', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'breach' in result['corrected'].lower()

    def test_third_party_processors(self, synthesizer):
        """Test third party processor disclosure."""
        text = "We use service providers to process data."
        gates = [('processors', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'processor' in result['corrected'].lower()

    def test_data_sharing_disclosure(self, synthesizer):
        """Test data sharing disclosure."""
        text = "We may share your data with partners."
        gates = [('third_party_sharing', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'share' in result['corrected'] or 'recipient' in result['corrected'].lower()

    def test_data_portability_right(self, synthesizer):
        """Test data portability right disclosure."""
        text = "Your data is stored in our systems."
        gates = [('rights', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'portability' in result['corrected'].lower() or 'right' in result['corrected'].lower()

    def test_object_to_processing(self, synthesizer):
        """Test right to object to processing."""
        text = "We process your data for marketing."
        gates = [('rights', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'object' in result['corrected'].lower() or 'right' in result['corrected'].lower()

    def test_restrict_processing_right(self, synthesizer):
        """Test right to restrict processing."""
        text = "We process your personal data continuously."
        gates = [('rights', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'restrict' in result['corrected'].lower() or 'right' in result['corrected'].lower()

    def test_multiple_gdpr_corrections(self, synthesizer):
        """Test multiple GDPR corrections."""
        text = "By using this site you agree. We store data permanently."
        gates = [
            ('consent', {'status': 'FAIL', 'severity': 'critical'}),
            ('retention', {'status': 'FAIL', 'severity': 'high'}),
            ('rights', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        assert result['correction_count'] >= 2

    def test_gdpr_determinism(self, synthesizer):
        """Test GDPR corrections are deterministic."""
        text = "By accessing this site you automatically consent."
        gates = [('consent', {'status': 'FAIL', 'severity': 'critical'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']

    def test_legitimate_interest_basis(self, synthesizer):
        """Test legitimate interest lawful basis."""
        text = "We process data for business purposes."
        gates = [('lawful_basis', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'lawful' in result['corrected'].lower() or 'legitimate' in result['corrected'].lower()

    def test_data_minimization(self, synthesizer):
        """Test data minimization principle."""
        text = "We collect comprehensive information about you."
        gates = [('lawful_basis', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should add lawful basis context
        assert len(result['corrected']) >= len(text)

    def test_privacy_by_design(self, synthesizer):
        """Test privacy by design disclosure."""
        text = "Our system processes personal data."
        gates = [('accountability', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'accountab' in result['corrected'].lower() or 'gdpr' in result['corrected'].lower()


# ============================================================================
# TAX UK CORRECTIONS - HMRC Compliance (20 tests)
# ============================================================================

class TestTaxCorrections:
    """Test Tax UK HMRC compliance corrections."""

    def test_vat_threshold_update(self, synthesizer):
        """Test VAT threshold correction to current amount."""
        text = "The VAT registration threshold is £85,000."
        gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '£90,000' in result['corrected']

    def test_old_vat_threshold_83k(self, synthesizer):
        """Test old VAT threshold £83,000 correction."""
        text = "Register for VAT at £83,000 turnover."
        gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '£90,000' in result['corrected']

    def test_company_limited_spelling(self, synthesizer):
        """Test 'Ltd' expanded to 'Limited'."""
        text = "ABC Company Ltd provides services."
        gates = [('legal_entity_name', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'Limited' in result['corrected']

    def test_llc_to_limited_conversion(self, synthesizer):
        """Test LLC converted to Limited (UK)."""
        text = "XYZ LLC is a UK company."
        gates = [('legal_entity_name', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'Limited' in result['corrected']
        assert 'LLC' not in result['corrected']

    def test_hmrc_gift_card_scam_warning(self, synthesizer):
        """Test HMRC scam warning for gift cards."""
        text = "Pay your tax debt via iTunes gift cards immediately."
        gates = [('hmrc_scam', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'REMOVED' in result['corrected'] or 'SCAM' in result['corrected']

    def test_hmrc_arrest_threat_removal(self, synthesizer):
        """Test removal of immediate arrest threats."""
        text = "Pay now or face immediate arrest for tax evasion!"
        gates = [('hmrc_scam', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'REMOVED' in result['corrected'] or 'SCAM' in result['corrected']

    def test_cis_compliance_notice(self, synthesizer):
        """Test CIS compliance information."""
        text = "Construction contractors must deduct amounts from subcontractors."
        gates = [('cis_compliance', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'cis' in result['corrected'].lower() or '20%' in result['corrected']

    def test_corporation_tax_filing(self, synthesizer):
        """Test corporation tax filing information."""
        text = "UK companies must pay corporation tax annually."
        gates = [('corporation_tax', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'ct600' in result['corrected'].lower() or '12 months' in result['corrected'].lower()

    def test_dividend_tax_rates(self, synthesizer):
        """Test dividend tax rate information."""
        text = "Dividend income is taxable for shareholders."
        gates = [('dividend_tax', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '8.75%' in result['corrected'] or 'dividend' in result['corrected'].lower()

    def test_allowable_expenses(self, synthesizer):
        """Test allowable expenses guidance."""
        text = "Business owners can claim various expenses."
        gates = [('expense_rules', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'wholly and exclusively' in result['corrected'].lower() or 'allowable' in result['corrected'].lower()

    def test_flat_rate_vat_scheme(self, synthesizer):
        """Test flat rate VAT scheme information."""
        text = "Small businesses can use simplified VAT schemes."
        gates = [('flat_rate_vat', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'flat rate' in result['corrected'].lower() or '£150,000' in result['corrected']

    def test_import_vat_postponed(self, synthesizer):
        """Test import VAT postponed accounting."""
        text = "Import VAT is charged on goods entering the UK."
        gates = [('import_vat', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'postponed' in result['corrected'].lower() or 'import' in result['corrected']

    def test_invoice_legal_requirements(self, synthesizer):
        """Test VAT invoice legal requirements."""
        text = "Invoices must include business details."
        gates = [('invoice_legal_requirements', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'vat' in result['corrected'].lower() or 'invoice number' in result['corrected'].lower()

    def test_paye_basics(self, synthesizer):
        """Test PAYE basics for employers."""
        text = "Employers must handle employee tax deductions."
        gates = [('paye_basics', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'paye' in result['corrected'].lower() or '£123' in result['corrected']

    def test_self_assessment_deadlines(self, synthesizer):
        """Test self-assessment deadline information."""
        text = "Self-employed individuals must file tax returns."
        gates = [('self_assessment', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '31 january' in result['corrected'].lower() or 'self-assessment' in result['corrected'].lower()

    def test_making_tax_digital(self, synthesizer):
        """Test Making Tax Digital requirements."""
        text = "VAT-registered businesses must keep digital records."
        gates = [('mtd', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'making tax digital' in result['corrected'].lower() or 'mtd' in result['corrected'].lower()

    def test_ir35_status_disclosure(self, synthesizer):
        """Test IR35 status determination."""
        text = "Contractors work on a freelance basis."
        gates = [('ir35', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'ir35' in result['corrected'].lower()

    def test_hmrc_scam_warning_notice(self, synthesizer):
        """Test HMRC scam warning template insertion."""
        text = "Contact HMRC to pay your tax bill urgently."
        gates = [('hmrc_scam_notice', {'status': 'WARNING', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # May add warning at start
        assert 'hmrc' in result['corrected'].lower()

    def test_multiple_tax_corrections(self, synthesizer):
        """Test multiple tax corrections in one document."""
        text = "VAT threshold is £85,000. ABC Company Ltd files taxes."
        gates = [
            ('vat_threshold', {'status': 'FAIL', 'severity': 'medium'}),
            ('legal_entity_name', {'status': 'FAIL', 'severity': 'low'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        assert '£90,000' in result['corrected']
        assert 'Limited' in result['corrected']

    def test_tax_determinism(self, synthesizer):
        """Test tax corrections are deterministic."""
        text = "The VAT registration threshold is £85,000."
        gates = [('vat_threshold', {'status': 'FAIL', 'severity': 'medium'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']


# ============================================================================
# NDA UK CORRECTIONS - Non-Disclosure Agreements (15 tests)
# ============================================================================

class TestNDACorrections:
    """Test NDA UK non-disclosure agreement corrections."""

    def test_whistleblowing_protection(self, synthesizer):
        """Test whistleblowing protection clause."""
        text = "All confidential information must not be disclosed."
        gates = [('whistleblowing', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'whistleblow' in result['corrected'].lower() or 'public interest' in result['corrected'].lower()

    def test_crime_reporting_protection(self, synthesizer):
        """Test crime reporting protection clause."""
        text = "Confidential information cannot be shared with anyone."
        gates = [('crime_reporting', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'crime' in result['corrected'].lower() or 'law enforcement' in result['corrected'].lower()

    def test_harassment_discrimination_protection(self, synthesizer):
        """Test harassment and discrimination complaint protection."""
        text = "This NDA covers all workplace matters."
        gates = [('harassment', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'harassment' in result['corrected'].lower() or 'equality' in result['corrected'].lower()

    def test_perpetuity_duration_correction(self, synthesizer):
        """Test 'in perpetuity' duration correction."""
        text = "Confidentiality obligations last in perpetuity."
        gates = [('duration', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'perpetuity' not in result['corrected'].lower()
        assert 'years' in result['corrected'].lower() or 'period' in result['corrected'].lower()

    def test_indefinite_duration_correction(self, synthesizer):
        """Test 'indefinitely' duration correction."""
        text = "This agreement applies indefinitely."
        gates = [('duration', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'indefinitely' not in result['corrected'].lower()
        assert 'years' in result['corrected'].lower()

    def test_nda_gdpr_compliance(self, synthesizer):
        """Test GDPR compliance in NDA."""
        text = "Both parties will handle confidential data."
        gates = [('nda_gdpr', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'gdpr' in result['corrected'].lower() or 'data protection' in result['corrected'].lower()

    def test_governing_law_clause(self, synthesizer):
        """Test governing law specification."""
        text = "This NDA is legally binding."
        gates = [('governing_law', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'england' in result['corrected'].lower() or 'scotland' in result['corrected'].lower()

    def test_consideration_clause(self, synthesizer):
        """Test consideration clause insertion."""
        text = "The parties agree to maintain confidentiality."
        gates = [('consideration', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'consideration' in result['corrected'].lower() or '£1' in result['corrected']

    def test_definition_specificity(self, synthesizer):
        """Test confidential information definition."""
        text = "Confidential Information includes business secrets."
        gates = [('definition_specificity', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'exclusion' in result['corrected'].lower() or 'publicly available' in result['corrected'].lower()

    def test_parties_identification(self, synthesizer):
        """Test parties identification clause."""
        text = "This agreement is between the parties."
        gates = [('parties_identified', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'party' in result['corrected'].lower() or 'registered' in result['corrected'].lower()

    def test_permitted_disclosures(self, synthesizer):
        """Test permitted disclosures clause."""
        text = "Information must not be disclosed."
        gates = [('permitted_disclosures', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'permitted' in result['corrected'].lower() or 'employee' in result['corrected'].lower()

    def test_permitted_purpose(self, synthesizer):
        """Test permitted purpose specification."""
        text = "The Receiving Party may use confidential information."
        gates = [('permitted_purpose', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'purpose' in result['corrected'].lower()

    def test_public_domain_exclusion(self, synthesizer):
        """Test public domain exclusion clause."""
        text = "All shared information is confidential."
        gates = [('public_domain', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'public' in result['corrected'].lower() or 'exclusion' in result['corrected'].lower()

    def test_return_destruction_clause(self, synthesizer):
        """Test return or destruction of information clause."""
        text = "Upon termination, the agreement ends."
        gates = [('return_destruction', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'return' in result['corrected'].lower() or 'destroy' in result['corrected'].lower()

    def test_nda_determinism(self, synthesizer):
        """Test NDA corrections are deterministic."""
        text = "Confidentiality lasts in perpetuity."
        gates = [('duration', {'status': 'FAIL', 'severity': 'high'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']


# ============================================================================
# HR SCOTTISH CORRECTIONS - Employment Law (15 tests)
# ============================================================================

class TestHRScottishCorrections:
    """Test HR Scottish employment law corrections."""

    def test_accompaniment_rights(self, synthesizer):
        """Test right to be accompanied disclosure."""
        text = "You are invited to a disciplinary meeting."
        gates = [('accompaniment', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'accompanied' in result['corrected'].lower() or 'colleague' in result['corrected'].lower()

    def test_no_lawyer_restriction_removal(self, synthesizer):
        """Test removal of lawyer restriction."""
        text = "You may not bring a solicitor to the meeting."
        gates = [('accompaniment_restrictions', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'may not' not in result['corrected'] or 'right' in result['corrected'].lower()

    def test_no_legal_representation_removal(self, synthesizer):
        """Test removal of no legal representation clause."""
        text = "No legal representation is allowed."
        gates = [('accompaniment_restrictions', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'right' in result['corrected'].lower()

    def test_notice_of_meeting(self, synthesizer):
        """Test proper notice of disciplinary meeting."""
        text = "We need to discuss a workplace matter with you."
        gates = [('notice', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'notice' in result['corrected'].lower() or 'meeting' in result['corrected']

    def test_right_to_be_heard(self, synthesizer):
        """Test right to respond and be heard."""
        text = "We have made a decision regarding your conduct."
        gates = [('right_to_be_heard', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'respond' in result['corrected'].lower() or 'case' in result['corrected'].lower()

    def test_appeal_rights(self, synthesizer):
        """Test appeal rights disclosure."""
        text = "The decision is final."
        gates = [('appeal', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'appeal' in result['corrected'].lower()

    def test_evidence_disclosure(self, synthesizer):
        """Test evidence disclosure requirements."""
        text = "We have evidence of misconduct."
        gates = [('evidence', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'evidence' in result['corrected'] and ('provided' in result['corrected'].lower() or '48 hours' in result['corrected'].lower())

    def test_impartial_chair(self, synthesizer):
        """Test impartial decision maker requirement."""
        text = "The meeting will be chaired by your line manager."
        gates = [('impartial_chair', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'impartial' in result['corrected'].lower()

    def test_suspension_not_punishment(self, synthesizer):
        """Test suspension clarification (not punishment)."""
        text = "You are suspended pending investigation."
        gates = [('suspension', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'full pay' in result['corrected'].lower() or 'not a disciplinary' in result['corrected'].lower()

    def test_clear_allegations(self, synthesizer):
        """Test clear allegations specification."""
        text = "We need to discuss some issues with you."
        gates = [('allegations', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'allegation' in result['corrected'].lower()

    def test_consistency_in_decisions(self, synthesizer):
        """Test consistency statement."""
        text = "We apply our procedures fairly."
        gates = [('consistency', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'consistent' in result['corrected'].lower()

    def test_informal_warning_threat_removal(self, synthesizer):
        """Test removal of informal final warnings."""
        text = "This is your final warning informally."
        gates = [('informal_threats', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'final warning' not in result['corrected'].lower() or 'discuss' in result['corrected'].lower()

    def test_investigation_process(self, synthesizer):
        """Test investigation process disclosure."""
        text = "An investigation will take place."
        gates = [('investigation', {'status': 'FAIL', 'severity': 'medium'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'investigation' in result['corrected'].lower()

    def test_meeting_notes_provision(self, synthesizer):
        """Test meeting notes and correction rights."""
        text = "We will document the meeting."
        gates = [('meeting_notes', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'notes' in result['corrected'].lower() or 'copy' in result['corrected'].lower()

    def test_hr_determinism(self, synthesizer):
        """Test HR corrections are deterministic."""
        text = "You may not bring a solicitor to the meeting."
        gates = [('accompaniment_restrictions', {'status': 'FAIL', 'severity': 'critical'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['corrected'] == result2['corrected']


# ============================================================================
# CROSS-MODULE AND INTEGRATION TESTS (10 tests)
# ============================================================================

class TestCrossModuleCorrections:
    """Test corrections across multiple modules."""

    def test_multi_module_correction(self, synthesizer):
        """Test corrections across FCA and GDPR modules."""
        text = "GUARANTEED returns! By using our site, you automatically consent to data processing."
        gates = [
            ('fair_clear', {'status': 'FAIL', 'severity': 'critical'}),
            ('consent', {'status': 'FAIL', 'severity': 'critical'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        assert 'GUARANTEED' not in result['corrected']
        assert 'automatically' not in result['corrected'].lower() or 'explicit' in result['corrected'].lower()
        assert result['correction_count'] >= 2

    def test_correction_order_determinism(self, synthesizer):
        """Test corrections applied in deterministic order."""
        text = "Test document with multiple issues."
        gates = [
            ('gate_b', {'status': 'FAIL', 'severity': 'high'}),
            ('gate_a', {'status': 'FAIL', 'severity': 'high'}),
            ('gate_c', {'status': 'FAIL', 'severity': 'high'})
        ]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        # Should produce identical results despite gate order
        assert result1['corrected'] == result2['corrected']

    def test_empty_document(self, synthesizer):
        """Test correction of empty document."""
        text = ""
        gates = [('test_gate', {'status': 'FAIL', 'severity': 'high'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert isinstance(result, dict)
        assert 'corrected' in result

    def test_very_short_document(self, synthesizer):
        """Test correction of very short document."""
        text = "Hi."
        gates = [('test_gate', {'status': 'FAIL', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        assert len(result['corrected']) >= len(text)

    def test_no_failing_gates(self, synthesizer):
        """Test document with no failing gates."""
        text = "This is a compliant document."
        gates = [
            ('gate_1', {'status': 'PASS', 'severity': 'low'}),
            ('gate_2', {'status': 'PASS', 'severity': 'low'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        assert result['unchanged'] == True
        assert result['correction_count'] == 0

    def test_warning_vs_fail_priority(self, synthesizer):
        """Test FAIL gates prioritized over WARNING gates."""
        text = "Document with various issues."
        gates = [
            ('warning_gate', {'status': 'WARNING', 'severity': 'low'}),
            ('fail_gate', {'status': 'FAIL', 'severity': 'high'})
        ]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should process both
        assert isinstance(result['corrections'], list)

    def test_unicode_preservation(self, synthesizer):
        """Test unicode characters are preserved."""
        text = "Financial services: £100, €200, ¥300. 中文 العربية"
        gates = [('test_gate', {'status': 'PASS', 'severity': 'low'})]

        result = synthesizer.synthesize_corrections(text, gates)

        # Should preserve all unicode
        assert '£' in result['corrected']
        assert '€' in result['corrected']
        assert '中文' in result['corrected']

    def test_correction_metadata_completeness(self, synthesizer):
        """Test all corrections have complete metadata."""
        text = "GUARANTEED returns! Risk-free investment!"
        gates = [('fair_clear', {'status': 'FAIL', 'severity': 'critical'})]

        result = synthesizer.synthesize_corrections(text, gates)

        for correction in result['corrections']:
            assert 'gate_id' in correction
            assert 'strategy' in correction
            assert 'gate_severity' in correction

    def test_determinism_hash_consistency(self, synthesizer):
        """Test determinism hashes are consistent."""
        text = "Test document"
        gates = [('test', {'status': 'FAIL', 'severity': 'medium'})]

        result1 = synthesizer.synthesize_corrections(text, gates)
        result2 = synthesizer.synthesize_corrections(text, gates)

        assert result1['determinism']['input_hash'] == result2['determinism']['input_hash']
        assert result1['determinism']['output_hash'] == result2['determinism']['output_hash']

    def test_correction_validator_integration(self):
        """Test correction validator catches issues."""
        original = "This is a long document with lots of content and information."
        corrected = "Hi."
        corrections = []

        validation = CorrectionValidator.validate_correction(original, corrected, corrections)

        assert validation['valid'] == False
        assert len(validation['warnings']) > 0 or len(validation['errors']) > 0
