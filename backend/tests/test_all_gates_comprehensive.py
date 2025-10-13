"""
Comprehensive Test Suite for All FCA Gates
==========================================
This file contains one targeted test case for each gate in the system,
designed to trigger FAIL or WARNING status to verify gate functionality.

Author: Claude Code
Date: 2025-10-11
Total Gates: 26
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.fca_uk.gates.client_money_segregation import ClientMoneySegregationGate
from modules.fca_uk.gates.complaint_route_clock import ComplaintRouteClockGate
from modules.fca_uk.gates.comprehension_aids import ComprehensionAidsGate
from modules.fca_uk.gates.conflicts_declaration import ConflictsDeclarationGate
from modules.fca_uk.gates.cross_cutting_rules import CrossCuttingRulesGate
from modules.fca_uk.gates.defined_roles import DefinedRolesGate
from modules.fca_uk.gates.distribution_controls import DistributionControlsGate
from modules.fca_uk.gates.fair_clear_not_misleading import FairClearNotMisleadingGate
from modules.fca_uk.gates.fair_value import FairValueGate
from modules.fca_uk.gates.fair_value_assessment_ref import FairValueAssessmentRefGate
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


class TestAllGatesComprehensive:
    """Test suite with one test per gate designed to trigger violations"""

    # ========================================================================
    # GATE 1: Fair, Clear, Not Misleading
    # ========================================================================
    def test_fair_clear_not_misleading_trigger(self):
        """Test case designed to trigger fair/clear/misleading violations"""
        gate = FairClearNotMisleadingGate()

        test_text = """
        BEST INVESTMENT OPPORTUNITY EVER!

        Get guaranteed returns of 15% per year! This is the ultimate investment
        that outperforms the market consistently. Risk-free and always profitable.

        Higher returns than any bank account! Perfect for everyone!

        *Terms and conditions apply - see footnote below
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Fair/Clear/Misleading Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 2: No Implicit Advice
    # ========================================================================
    def test_no_implicit_advice_trigger(self):
        """Test case designed to trigger implicit advice violation"""
        gate = NoImplicitAdviceGate()

        test_text = """
        We recommend you invest in our premium bond fund. This is the right choice
        for you and would be suitable for your needs. You should buy now before
        prices increase. This is a tailored recommendation based on your profile.
        """

        result = gate.check(test_text, "communication")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ No Implicit Advice Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 3: Vulnerability Identification
    # ========================================================================
    def test_vulnerability_identification_trigger(self):
        """Test case designed to trigger vulnerability detection without support"""
        gate = VulnerabilityIdentificationGate()

        test_text = """
        Dear Customer,

        We understand you recently lost your job due to redundancy and are
        experiencing financial difficulty. You mentioned your elderly mother
        has dementia and you're struggling with debt payments.

        Please pay your outstanding balance within 7 days.

        Regards,
        Collections Team
        """

        result = gate.check(test_text, "communication")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Vulnerability Identification Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 4: Risk-Benefit Balance
    # ========================================================================
    def test_risk_benefit_balance_trigger(self):
        """Test case designed to trigger risk-benefit imbalance"""
        gate = RiskBenefitBalanceGate()

        test_text = """
        EXCEPTIONAL RETURNS UP TO 20% ANNUALLY!

        Our premium investment fund has delivered outstanding performance with
        significant gains year after year. Investors enjoy high yields and
        attractive returns consistently. Join thousands of satisfied investors
        experiencing remarkable growth!

        Maximum returns with our proven strategy!
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Risk-Benefit Balance Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 5: Target Audience
    # ========================================================================
    def test_target_audience_trigger(self):
        """Test case designed to trigger missing target audience"""
        gate = TargetAudienceGate()

        test_text = """
        Complex Structured Investment Product

        This sophisticated derivative instrument involves high-risk strategies
        including leverage, short-selling, and options trading. Requires advanced
        knowledge of financial markets and complex instruments.

        Available to all investors - apply now!
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Target Audience Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 6: FOS Signposting
    # ========================================================================
    def test_fos_signposting_trigger(self):
        """Test case designed to trigger missing FOS information"""
        gate = FosSignpostingGate()

        test_text = """
        FINAL RESPONSE TO YOUR COMPLAINT

        We have thoroughly investigated your complaint and have decided to
        reject it. We believe our actions were appropriate and in line with
        our terms and conditions.

        This is our final decision on the matter.

        Regards,
        Complaints Team
        """

        result = gate.check(test_text, "complaints_response")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ FOS Signposting Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 7: Complaint Route/Clock
    # ========================================================================
    def test_complaint_route_clock_trigger(self):
        """Test case designed to trigger missing complaint timeline"""
        gate = ComplaintRouteClockGate()

        test_text = """
        Thank you for your complaint about our service.

        We will investigate this matter and get back to you when we can.

        If you have any questions, please contact us.

        Customer Service Team
        """

        result = gate.check(test_text, "complaints_response")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Complaint Route/Clock Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 8: Comprehension Aids
    # ========================================================================
    def test_comprehension_aids_trigger(self):
        """Test case designed to trigger missing comprehension aids"""
        gate = ComprehensionAidsGate()

        test_text = """
        Our innovative financial product utilizes sophisticated algorithmic
        methodologies incorporating multi-factor quantitative strategies with
        dynamic hedging mechanisms. The underlying infrastructure leverages
        advanced derivatives including synthetic CDOs, credit default swaps,
        and exotic options with embedded stochastic volatility models.

        The systematic implementation of our proprietary risk-parity framework
        optimizes portfolio allocations through continuous rebalancing protocols.
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Comprehension Aids Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 9: Conflicts Declaration
    # ========================================================================
    def test_conflicts_declaration_trigger(self):
        """Test case designed to trigger undisclosed conflicts"""
        gate = ConflictsDeclarationGate()

        test_text = """
        We recommend you invest in the XYZ Premium Fund. This product offers
        excellent returns and we believe it's the best option for you.

        Our advisers receive commission and incentive payments for selling this
        product, and we have a corporate partnership with the fund provider.
        """

        result = gate.check(test_text, "communication")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Conflicts Declaration Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 10: Inducements & Referrals
    # ========================================================================
    def test_inducements_referrals_trigger(self):
        """Test case designed to trigger undisclosed inducement"""
        gate = InducementsReferralsGate()

        test_text = """
        REFER A FRIEND AND EARN £500!

        For every friend who opens an account and deposits £10,000, we'll pay
        you a £500 bonus! Plus get a free iPad when you sign up today!

        Unlimited referrals - the more friends you refer, the more you earn!
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Inducements & Referrals Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 11: Finfluencer Controls
    # ========================================================================
    def test_finfluencer_controls_trigger(self):
        """Test case designed to trigger finfluencer red flags"""
        gate = FinfluencerControlsGate()

        test_text = """
        Hey guys! 🚀💰 Just made 10K this week trading crypto!

        Use my affiliate link to sign up and get a bonus! I get paid for referrals
        but trust me this platform is AMAZING! Not financial advice but you should
        definitely check it out!

        #crypto #investing #getrich #moneymoves
        """

        result = gate.check(test_text, "social_media")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Finfluencer Controls Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 12: Promotions Approval
    # ========================================================================
    def test_promotions_approval_trigger(self):
        """Test case designed to trigger missing approval"""
        gate = PromotionsApprovalGate()

        test_text = """
        INVESTMENT OPPORTUNITY - HIGH RETURNS!

        Invest in our exclusive fund offering exceptional returns. Limited time
        offer for sophisticated investors.

        Contact: john@example.com
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Promotions Approval Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 13: Fair Value
    # ========================================================================
    def test_fair_value_trigger(self):
        """Test case designed to trigger fair value concerns"""
        gate = FairValueGate()

        test_text = """
        Our premium savings account offers:
        - 0.01% interest rate
        - £25 monthly maintenance fee
        - £5 per transaction fee
        - £50 annual account fee
        - Early withdrawal penalty: 10% of balance

        Compared to market average savings rates of 4.5%
        """

        result = gate.check(test_text, "product_description")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Fair Value Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 14: Fair Value Assessment Reference
    # ========================================================================
    def test_fair_value_assessment_ref_trigger(self):
        """Test case designed to trigger missing FVA reference"""
        gate = FairValueAssessmentRefGate()

        test_text = """
        NEW PRODUCT LAUNCH: Premium Investment Account

        We're proud to introduce our new investment product with competitive
        fees and excellent returns. Available to all customers now.

        Terms and conditions apply.
        """

        result = gate.check(test_text, "product_launch")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Fair Value Assessment Ref Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 15: Outcomes Coverage
    # ========================================================================
    def test_outcomes_coverage_trigger(self):
        """Test case designed to trigger missing Consumer Duty outcomes"""
        gate = OutcomesCoverageGate()

        test_text = """
        CONSUMER DUTY COMPLIANCE REPORT

        We have implemented Consumer Duty policies across our organization.
        Staff have been trained and processes updated.

        Our products meet regulatory requirements.
        """

        result = gate.check(test_text, "policy_document")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Outcomes Coverage Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 16: Support Journey
    # ========================================================================
    def test_support_journey_trigger(self):
        """Test case designed to trigger poor support journey"""
        gate = SupportJourneyGate()

        test_text = """
        Customer Service Options:

        - Email us at support@company.com (response within 10 working days)
        - Write to us at PO Box 123, London
        - Visit our office between 9-10am on Tuesdays only

        For urgent issues, please wait for our response.
        """

        result = gate.check(test_text, "customer_service")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Support Journey Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 17: Target Market Definition
    # ========================================================================
    def test_target_market_definition_trigger(self):
        """Test case designed to trigger vague target market"""
        gate = TargetMarketDefinitionGate()

        test_text = """
        HIGH-RISK DERIVATIVE PRODUCT

        This complex structured product involves significant leverage and
        requires advanced understanding of financial markets.

        Suitable for: Anyone interested in investing
        """

        result = gate.check(test_text, "product_description")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Target Market Definition Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 18: Distribution Controls
    # ========================================================================
    def test_distribution_controls_trigger(self):
        """Test case designed to trigger missing distribution controls"""
        gate = DistributionControlsGate()

        test_text = """
        COMPLEX INVESTMENT PRODUCT - FOR SOPHISTICATED INVESTORS

        This high-risk product requires expertise in derivatives and leverage.

        Apply online now - instant approval for all applicants!
        No questions asked - quick and easy sign up!
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Distribution Controls Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 19: Reasonable Adjustments
    # ========================================================================
    def test_reasonable_adjustments_trigger(self):
        """Test case designed to trigger missing reasonable adjustments"""
        gate = ReasonableAdjustmentsGate()

        test_text = """
        IMPORTANT: ACCOUNT CHANGES REQUIRED

        You must complete the attached 50-page form and return it within 48 hours
        or your account will be closed. The form must be completed online only.

        No extensions or alternative formats available. This is a final notice.
        """

        result = gate.check(test_text, "customer_communication")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Reasonable Adjustments Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 20: Cross-Cutting Rules
    # ========================================================================
    def test_cross_cutting_rules_trigger(self):
        """Test case designed to trigger cross-cutting issues"""
        gate = CrossCuttingRulesGate()

        test_text = """
        Special promotion! Act now before time runs out!

        Our sales team is incentivized to sell you this product. We receive
        higher commissions for premium accounts. You should sign up immediately
        as this offer expires soon!

        *Full terms available on request
        """

        result = gate.check(test_text, "financial_promotion")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Cross-Cutting Rules Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 21: Defined Roles (SMCR)
    # ========================================================================
    def test_defined_roles_trigger(self):
        """Test case designed to trigger missing SMCR accountability"""
        gate = DefinedRolesGate()

        test_text = """
        INTERNAL MEMO: New Client Onboarding Process

        All staff should follow the new procedures for onboarding clients.
        Please ensure all steps are completed properly.

        Any issues should be escalated to management.
        """

        result = gate.check(test_text, "internal_policy")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Defined Roles (SMCR) Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 22: Record Keeping
    # ========================================================================
    def test_record_keeping_trigger(self):
        """Test case designed to trigger poor record keeping"""
        gate = RecordKeepingGate()

        test_text = """
        Meeting Notes - Client Advisory Session

        Discussed investment options with client. Client seemed interested.
        Recommended some products. Client will think about it.

        Follow up next week.
        """

        result = gate.check(test_text, "client_notes")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Record Keeping Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 23: Personal Dealing
    # ========================================================================
    def test_personal_dealing_trigger(self):
        """Test case designed to trigger personal dealing violation"""
        gate = PersonalDealingGate()

        test_text = """
        EMAIL FROM: Investment Manager
        TO: Colleague

        Hey, I'm about to place a big trade for our clients in XYZ Corp tomorrow.
        You might want to buy some shares today before the price moves!

        Keep this between us.
        """

        result = gate.check(test_text, "internal_communication")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Personal Dealing Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 24: Client Money Segregation
    # ========================================================================
    def test_client_money_segregation_trigger(self):
        """Test case designed to trigger client money concerns"""
        gate = ClientMoneySegregationGate()

        test_text = """
        INTERNAL MEMO: Cash Management

        Client funds received today have been deposited into our general
        operating account. We'll use these funds for operational expenses
        and will allocate them to client accounts at month-end.

        Current client money balance: £5M in main business account
        """

        result = gate.check(test_text, "internal_document")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Client Money Segregation Gate: {result['status']} - {result.get('message', 'N/A')}")


    # ========================================================================
    # GATE 25: Third Party Banks
    # ========================================================================
    def test_third_party_banks_trigger(self):
        """Test case designed to trigger third party bank concerns"""
        gate = ThirdPartyBanksGate()

        test_text = """
        PAYMENT INSTRUCTIONS

        Please transfer your investment funds to:

        Account Name: Offshore Holdings Ltd
        Bank: International Bank of [Tax Haven]
        Account Number: 123456789

        This is our partner company that will process your investment.
        """

        result = gate.check(test_text, "payment_instructions")

        assert result['status'] in ['FAIL', 'WARNING'], \
            f"Expected FAIL/WARNING, got {result['status']}"
        print(f"✓ Third Party Banks Gate: {result['status']} - {result.get('message', 'N/A')}")


if __name__ == "__main__":
    """Run all tests and display results"""
    print("\n" + "="*70)
    print("COMPREHENSIVE GATE TEST SUITE - TRIGGERING ALL 26 GATES")
    print("="*70 + "\n")

    test_suite = TestAllGatesComprehensive()
    tests = [method for method in dir(test_suite) if method.startswith('test_')]

    passed = 0
    failed = 0

    for test_name in tests:
        try:
            test_method = getattr(test_suite, test_name)
            test_method()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {str(e)}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")

    if failed > 0:
        sys.exit(1)
