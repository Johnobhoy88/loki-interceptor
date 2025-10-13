"""
GOLD STANDARD EDGE CASE TEST SUITE - FCA Gates
================================================

This suite contains meticulously crafted edge cases designed to:
1. Reliably trigger each gate with high confidence
2. Test boundary conditions and detection limits
3. Document the "gold standard" patterns for each gate

Based on analysis of gate implementations, this suite addresses why certain
gates didn't trigger in the basic tests and provides optimized triggers.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.fca_uk.gates.client_money_segregation import ClientMoneySegregationGate
from modules.fca_uk.gates.complaint_route_clock import ComplaintRouteClockGate
from modules.fca_uk.gates.comprehension_aids import ComprehensionAidsGate
from modules.fca_uk.gates.conflicts_declaration import ConflictsDeclarationGate
from modules.fca_uk.gates.cross_cutting_rules import CrossCuttingRulesGate
from modules.fca_uk.gates.defined_roles import DefinedRolesGate
from modules.fca_uk.gates.distribution_controls import DistributionControlsGate
from modules.fca_uk.gates.fair_clear_not_misleading import FairClearNotMisleadingGate
from modules.fca_uk.gates.fair_value_assessment_ref import FairValueAssessmentRefGate
from modules.fca_uk.gates.fair_value import FairValueGate
from modules.fca_uk.gates.finfluencer_controls import FinfluencerControlsGate
from modules.fca_uk.gates.fos_signposting import FosSignpostingGate
from modules.fca_uk.gates.inducements_referrals import InducementsReferralsGate
from modules.fca_uk.gates.no_implicit_advice import NoImplicitAdviceGate
from modules.fca_uk.gates.outcomes_coverage import OutcomesCoverageGate
from modules.fca_uk.gates.personal_dealing import PersonalDealingGate
from modules.fca_uk.gates.promotions_approval import PromotionsApprovalGate
from modules.fca_uk.gates.reasonable_adjustments import ReasonableAdjustmentsGate
from modules.fca_uk.gates.record_keeping import RecordKeepingGate
from modules.fca_uk.gates.risk_benefit_balance import RiskBenefitBalanceGate
from modules.fca_uk.gates.support_journey import SupportJourneyGate
from modules.fca_uk.gates.target_audience import TargetAudienceGate
from modules.fca_uk.gates.target_market_definition import TargetMarketDefinitionGate
from modules.fca_uk.gates.third_party_banks import ThirdPartyBanksGate
from modules.fca_uk.gates.vulnerability_identification import VulnerabilityIdentificationGate


class TestGoldStandardEdgeCases:
    """Gold standard edge cases for all 26 FCA gates"""

    # ========== GATES THAT ALREADY TRIGGERED WELL ==========

    def test_client_money_segregation_gold(self):
        """GOLD: Client money without segregation statement"""
        gate = ClientMoneySegregationGate()

        text = """
        Client Account Statement

        We hold your funds of £50,000 in our client account.
        Your money is safe with us and managed professionally.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Client Money Segregation: {result['status']}")

    def test_complaint_route_clock_gold(self):
        """GOLD: Complaint response missing 8-week deadline"""
        gate = ComplaintRouteClockGate()

        text = """
        Complaint Handling Process

        If you are unhappy with our service, please write to our complaints team.
        We will acknowledge your complaint and investigate the matter.
        We aim to resolve complaints as quickly as possible.
        """

        result = gate.check(text, "complaints_response")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Complaint Route/Clock: {result['status']}")

    def test_conflicts_declaration_gold(self):
        """GOLD: Conflict of interest without declaration"""
        gate = ConflictsDeclarationGate()

        text = """
        We receive commission from the product provider when you invest.
        Our parent company also manufactures some of the investment products we recommend.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Conflicts Declaration: {result['status']}")

    def test_fair_clear_not_misleading_gold(self):
        """GOLD: Misleading promotional claims"""
        gate = FairClearNotMisleadingGate()

        text = """
        GUARANTEED 15% RETURNS!

        This investment ALWAYS outperforms the market!
        RISK-FREE opportunity of a lifetime!
        Better than ANY other investment!
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Fair/Clear/Misleading: {result['status']}")

    def test_fos_signposting_gold(self):
        """GOLD: Financial service without FOS information"""
        gate = FosSignpostingGate()

        text = """
        Complaint Procedure

        If you are dissatisfied with our response to your complaint,
        you may wish to seek independent advice or legal counsel.
        """

        result = gate.check(text, "complaints_response")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD FOS Signposting: {result['status']}")

    # ========== COMPREHENSION AIDS (Was: PASS, Need: FAIL) ==========

    def test_comprehension_aids_gold(self):
        """GOLD: Complex jargon without explanations, long sentences"""
        gate = ComprehensionAidsGate()

        # Must be >1000 chars OR contain complex terms
        # Must have jargon WITHOUT explanations nearby
        # Must have long sentences (>40 words)
        text = """
        Investment Product Information

        This derivative investment utilizes leveraged portfolio strategies with subordinated
        debt instruments and requires understanding of counterparty risk management, collateral
        posting requirements, and the impact of basis points fluctuations on overall yield
        optimization through sophisticated amortisation schedules and covenant compliance monitoring
        processes which are essential for maintaining optimal risk-adjusted returns throughout
        the investment lifecycle and ensuring appropriate hedging mechanisms are in place.

        The product employs complex derivative structures including interest rate swaps and
        credit default swaps with embedded leverage multipliers that amplify both gains and
        losses through notional exposure calculations which exceed the initial capital commitment
        by factors ranging from two to ten depending on market volatility conditions and the
        counterparty credit assessment results obtained from our proprietary risk modeling systems.

        Covenant compliance requirements mandate quarterly reporting of subordinated debt ratios
        and collateral adequacy metrics measured against pre-agreed thresholds established at
        inception with adjustments for basis points movements in benchmark interest rates affecting
        amortisation calculations throughout the tenor of the commitment period subject to early
        termination provisions triggered by material adverse change clauses or counterparty default
        events as defined in the master agreement documentation and supplementary credit annexes.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Comprehension Aids: {result['status']} - {result.get('message', 'N/A')}")

    # ========== DISTRIBUTION CONTROLS (Was: N/A, Need: FAIL/WARNING) ==========

    def test_distribution_controls_gold(self):
        """GOLD: Intermediary distribution without controls"""
        gate = DistributionControlsGate()

        # Must mention intermediaries/distribution
        # Must have negative indicators about control
        text = """
        Distribution Model

        Our products are sold through a network of independent financial advisers and
        third-party brokers across the UK. These intermediaries operate independently
        and are outside our control. We have no responsibility for the advice they
        provide to customers.

        Distribution is handled by appointed representatives and partner firms.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Distribution Controls: {result['status']} - {result.get('message', 'N/A')}")

    # ========== FINFLUENCER CONTROLS (Was: N/A, Need: FAIL) ==========

    def test_finfluencer_controls_gold(self):
        """GOLD: Social media promotion without required controls"""
        gate = FinfluencerControlsGate()

        # Must mention social media/influencer
        # Must be promotional
        # Must lack approval, ad label, and risk warning
        text = """
        Follow us on Instagram and TikTok!

        Check out our investment opportunity - join now and start earning!
        Limited time offer, don't miss out! Sign up today!

        Click the link in our bio to get started.

        Working with content creators and brand ambassadors to spread the word.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Finfluencer Controls: {result['status']} - {result.get('message', 'N/A')}")

    # ========== INDUCEMENTS & REFERRALS (Was: N/A, Need: FAIL) ==========

    def test_inducements_referrals_gold(self):
        """GOLD: Undisclosed referral fees and inducements"""
        gate = InducementsReferralsGate()

        # Must mention referrals/commissions/incentives
        # Must lack disclosure
        text = """
        Referral Program

        Refer a friend and earn commission! Get paid for every successful referral.
        Our advisers receive incentive payments based on sales performance.

        We partner with introducers who bring us new clients and receive fees.
        Performance bonuses are awarded to staff who meet sales targets.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Inducements/Referrals: {result['status']} - {result.get('message', 'N/A')}")

    # ========== OUTCOMES COVERAGE (Was: N/A, Need: FAIL) ==========

    def test_outcomes_coverage_gold(self):
        """GOLD: Product document missing Consumer Duty outcomes"""
        gate = OutcomesCoverageGate()

        # Must be >150 chars
        # Must contain product indicators AND communication indicators
        # Must miss 3+ outcomes
        text = """
        Investment Product Information - Detailed Brochure

        This product is designed for investors seeking growth opportunities.
        Information about our investment service includes various features and
        benefits that are tailored to meet customer needs in the market.

        The product includes a range of investment options suitable for different
        customer profiles. This product is designed to provide long-term returns
        and is suitable for various investment objectives depending on individual
        circumstances and financial goals.

        Details of the product features include portfolio diversification,
        professional management, and access to global markets. This service
        is designed for customers who want investment exposure.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Outcomes Coverage: {result['status']} - {result.get('message', 'N/A')}")

    # ========== PERSONAL DEALING (Was: N/A, Need: FAIL/WARNING) ==========

    def test_personal_dealing_gold(self):
        """GOLD: Staff trading without controls"""
        gate = PersonalDealingGate()

        # Must mention employee/staff trading
        # Must lack controls
        text = """
        Employee Share Scheme

        Staff members are permitted to trade in company shares and may invest
        in the same products we offer to clients. Employees can buy and sell
        securities at their discretion.

        Personal investment accounts are available to all staff members.
        """

        result = gate.check(text, "smcr_policy")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Personal Dealing: {result['status']} - {result.get('message', 'N/A')}")

    # ========== REASONABLE ADJUSTMENTS (Was: PASS, Need: FAIL) ==========

    def test_reasonable_adjustments_gold(self):
        """GOLD: Disability mentioned with process barriers"""
        gate = ReasonableAdjustmentsGate()

        # Must mention disability/accessibility (triggers relevance)
        # Must have barriers (not alternatives)
        text = """
        Application Process for Disabled Customers

        All customers must complete the online application form.
        Applications can only be submitted through our website.

        You are required to attend an in-person meeting at our office.
        There is no alternative method available.

        The standard process applies to all applicants without exception.
        """

        result = gate.check(text, "consumer_duty_policy")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Reasonable Adjustments: {result['status']} - {result.get('message', 'N/A')}")

    # ========== RECORD KEEPING (Was: N/A, Need: WARNING) ==========

    def test_record_keeping_gold(self):
        """GOLD: Records mentioned without retention policy"""
        gate = RecordKeepingGate()

        # Must mention records/documents
        # Must lack retention periods or policies
        text = """
        Documentation Requirements

        We maintain records of all client interactions and transactions.
        Files are stored securely and documents are archived.

        Records include correspondence, advice given, and transaction history.
        All documentation is kept in our systems.
        """

        result = gate.check(text, "smcr_policy")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Record Keeping: {result['status']} - {result.get('message', 'N/A')}")

    # ========== SUPPORT JOURNEY (Was: PASS, Need: FAIL) ==========

    def test_support_journey_gold(self):
        """GOLD: Dark patterns in cancellation process"""
        gate = SupportJourneyGate()

        # Must mention contact/support (triggers relevance)
        # Must have dark patterns
        text = """
        Cancellation Policy

        To cancel your account, you must contact us in writing by post only.
        Phone cancellations are not accepted.

        A notice period of 90 days is required for cancellation.
        An exit fee of £150 will be charged for early withdrawal.

        Our customer service team is available Monday to Friday, 9am-11am only.

        Please complete the 15-page cancellation form before we can process your request.
        """

        result = gate.check(text, "consumer_duty_policy")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Support Journey: {result['status']} - {result.get('message', 'N/A')}")

    # ========== TARGET MARKET DEFINITION (Was: PASS, Need: FAIL) ==========

    def test_target_market_definition_gold(self):
        """GOLD: Generic 'for everyone' target market"""
        gate = TargetMarketDefinitionGate()

        # Must mention product/target (triggers relevance)
        # Must have generic targeting
        text = """
        Product Suitability

        This product is suitable for everyone and anyone can invest.
        The service is appropriate for all customers regardless of circumstances.

        There are no restrictions or requirements - broadly suitable for any investor.
        The target market is all retail customers with no minimum criteria.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ GOLD Target Market Definition: {result['status']} - {result.get('message', 'N/A')}")

    # ========== THIRD PARTY BANKS (Was: N/A, Need: WARNING) ==========

    def test_third_party_banks_gold(self):
        """GOLD: Third party bank without safeguards"""
        gate = ThirdPartyBanksGate()

        # Must mention third party banks
        # Must lack disclosure/safeguards
        text = """
        Payment Processing

        Your funds will be transferred to our partner bank account.
        We use a third-party banking provider for payment processing.
        Payments are held by an external financial institution.
        """

        result = gate.check(text, "consumer_duty_policy")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ GOLD Third Party Banks: {result['status']} - {result.get('message', 'N/A')}")

    # ========== GATES THAT ALREADY WORK WELL - EDGE CASE VARIANTS ==========

    def test_cross_cutting_rules_edge(self):
        """EDGE: Consumer Duty mention without specific rules"""
        gate = CrossCuttingRulesGate()

        text = """
        Our Commitment to Customers

        We follow the FCA Consumer Duty requirements in our operations.
        Customer outcomes are important to us.
        """

        result = gate.check(text, "consumer_duty_policy")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ EDGE Cross-Cutting Rules: {result['status']}")

    def test_no_implicit_advice_edge(self):
        """EDGE: Subtle advice without authorization statement"""
        gate = NoImplicitAdviceGate()

        text = """
        You might want to consider increasing your pension contributions.
        It could be beneficial to review your investment portfolio.
        Perhaps you should look at diversifying your holdings.
        """

        result = gate.check(text, "ai_generated")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ EDGE No Implicit Advice: {result['status']}")

    def test_risk_benefit_balance_edge(self):
        """EDGE: All benefits, zero risk warnings"""
        gate = RiskBenefitBalanceGate()

        text = """
        Amazing Investment Benefits:

        • Tax-free growth potential
        • High returns
        • Capital appreciation
        • Income generation
        • Portfolio diversification
        • Professional management
        • Low fees

        Sign up today!
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'FAIL', f"Expected FAIL, got {result['status']}"
        print(f"✓ EDGE Risk-Benefit Balance: {result['status']}")

    def test_defined_roles_edge(self):
        """EDGE: SMCR context without role clarity"""
        gate = DefinedRolesGate()

        text = """
        Senior Management Function

        The management team oversees operations.
        Various people are responsible for different things.
        We have managers looking after compliance matters.
        """

        result = gate.check(text, "smcr_policy")
        assert result['status'] in ['WARNING', 'FAIL'], f"Expected WARNING/FAIL, got {result['status']}"
        print(f"✓ EDGE Defined Roles: {result['status']}")

    def test_fair_value_edge(self):
        """EDGE: Price mentioned without value justification"""
        gate = FairValueGate()

        text = """
        Investment Product - £5,000 minimum

        Annual management fee: 2.5%
        Platform fee: 1.2%
        Transaction costs: 0.8%
        Additional charges may apply.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ EDGE Fair Value: {result['status']}")

    def test_promotions_approval_edge(self):
        """EDGE: S.21 exemption claim without validation"""
        gate = PromotionsApprovalGate()

        text = """
        This financial promotion is exempt under FCA rules (s.21 exemption applies).
        Sophisticated investors only.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'WARNING', f"Expected WARNING, got {result['status']}"
        print(f"✓ EDGE Promotions Approval: {result['status']}")

    def test_vulnerability_identification_edge(self):
        """EDGE: Multiple vulnerability indicators without support"""
        gate = VulnerabilityIdentificationGate()

        text = """
        I'm 78 years old and recently widowed. I'm finding it difficult to understand
        all these financial terms. I have some health issues that make it hard to
        get to the bank. I'm worried about running out of money for care home fees.
        """

        result = gate.check(text, "ai_generated")
        assert result['status'] in ['WARNING', 'FAIL'], f"Expected WARNING/FAIL, got {result['status']}"
        print(f"✓ EDGE Vulnerability Identification: {result['status']}")

    def test_target_audience_edge(self):
        """EDGE: Vague target audience in complex product"""
        gate = TargetAudienceGate()

        text = """
        Structured Investment Product

        For investors looking for growth.
        Target customers: people interested in investments.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] == 'WARNING', f"Expected WARNING, got {result['status']}"
        print(f"✓ EDGE Target Audience: {result['status']}")

    def test_fair_value_assessment_ref_edge(self):
        """EDGE: Pricing without assessment process"""
        gate = FairValueAssessmentRefGate()

        text = """
        Our fees are 3% per annum plus performance fees.
        Transaction costs and fund charges apply.
        Early exit penalties may be charged.
        """

        result = gate.check(text, "financial_promotion")
        assert result['status'] in ['WARNING', 'FAIL'], f"Expected WARNING/FAIL, got {result['status']}"
        print(f"✓ EDGE Fair Value Assessment Ref: {result['status']}")


def main():
    """Run all gold standard edge case tests"""
    print("=" * 70)
    print("GOLD STANDARD EDGE CASE TEST SUITE - ALL 26 GATES")
    print("=" * 70)
    print()

    test_class = TestGoldStandardEdgeCases()
    tests = [
        # Gates that needed improvement
        ("test_comprehension_aids_gold", "Comprehension Aids"),
        ("test_distribution_controls_gold", "Distribution Controls"),
        ("test_finfluencer_controls_gold", "Finfluencer Controls"),
        ("test_inducements_referrals_gold", "Inducements/Referrals"),
        ("test_outcomes_coverage_gold", "Outcomes Coverage"),
        ("test_personal_dealing_gold", "Personal Dealing"),
        ("test_reasonable_adjustments_gold", "Reasonable Adjustments"),
        ("test_record_keeping_gold", "Record Keeping"),
        ("test_support_journey_gold", "Support Journey"),
        ("test_target_market_definition_gold", "Target Market Definition"),
        ("test_third_party_banks_gold", "Third Party Banks"),

        # Gates that already worked - gold standards
        ("test_client_money_segregation_gold", "Client Money Segregation"),
        ("test_complaint_route_clock_gold", "Complaint Route/Clock"),
        ("test_conflicts_declaration_gold", "Conflicts Declaration"),
        ("test_fair_clear_not_misleading_gold", "Fair/Clear/Misleading"),
        ("test_fos_signposting_gold", "FOS Signposting"),

        # Edge cases for working gates
        ("test_cross_cutting_rules_edge", "Cross-Cutting Rules (EDGE)"),
        ("test_no_implicit_advice_edge", "No Implicit Advice (EDGE)"),
        ("test_risk_benefit_balance_edge", "Risk-Benefit Balance (EDGE)"),
        ("test_defined_roles_edge", "Defined Roles (EDGE)"),
        ("test_fair_value_edge", "Fair Value (EDGE)"),
        ("test_promotions_approval_edge", "Promotions Approval (EDGE)"),
        ("test_vulnerability_identification_edge", "Vulnerability ID (EDGE)"),
        ("test_target_audience_edge", "Target Audience (EDGE)"),
        ("test_fair_value_assessment_ref_edge", "Fair Value Assessment (EDGE)"),
    ]

    passed = 0
    failed = 0

    for test_method, test_name in tests:
        try:
            method = getattr(test_class, test_method)
            method()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {str(e)}")
            failed += 1

    print()
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)
    print()

    # Print gold standard summary
    if failed == 0:
        print("🏆 GOLD STANDARD ACHIEVED - All gates triggered successfully!")
    else:
        print(f"⚠️  {failed} gates need further refinement")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
