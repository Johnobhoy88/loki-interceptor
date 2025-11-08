import re


class AutomatedDecisionsGate:
    """
    UK GDPR Article 22 - Automated Decision-Making and Profiling (2025 updates)
    Covers: Automated decisions, human review requirements, profiling, AI/ML transparency
    """
    def __init__(self):
        self.name = "automated_decisions"
        self.severity = "critical"
        self.legal_source = "UK GDPR Article 22, Data Use and Access Act 2025 (AI provisions)"

    def _is_relevant(self, text):
        """Check if document relates to automated decision-making"""
        text_lower = text.lower()
        keywords = [
            'automated', 'algorithm', 'profiling', 'ai ', 'artificial intelligence',
            'machine learning', 'ml ', 'decision-making', 'decision making',
            'automatic', 'computer', 'system', 'scoring', 'credit',
            'solely automated', 'without human', 'article 22'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to automated decision-making',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. SOLELY AUTOMATED DECISIONS (Article 22 prohibition)
        automated_decision_patterns = [
            r'(?:solely|entirely|fully|completely|purely)\s+automated',
            r'automated\s+(?:decision|processing).*(?:without|no)\s+human',
            r'(?:without|no)\s+human\s+(?:involvement|intervention|review|oversight)',
            r'algorithm(?:ic)?.*(?:decides?|determines?)',
            r'system.*(?:automatically|decides?)\s+(?:whether|to)'
        ]

        has_solely_automated = any(re.search(p, text, re.IGNORECASE) for p in automated_decision_patterns)

        if has_solely_automated:
            # Check for legal effects or significant effects
            effects_patterns = [
                r'legal\s+effects?',
                r'similarly\s+significant(?:ly)?',
                r'significant\s+(?:impact|effect|consequence)',
                r'affects?.*(?:rights|entitlements?|benefits?)',
                r'(?:credit|loan|mortgage|insurance|employment)\s+(?:decision|application)',
                r'accept(?:ance|ed)|reject(?:ion|ed)|refus(?:e|al)'
            ]

            has_significant_effects = any(re.search(p, text, re.IGNORECASE) for p in effects_patterns)

            if has_significant_effects:
                # Check for exceptions (consent, contract, legal authorization)
                exception_patterns = [
                    r'explicit\s+consent',
                    r'consent.*automated\s+decision',
                    r'necessary.*(?:contract|performance)',
                    r'authorised?\s+by.*law',
                    r'statutory\s+(?:provision|authority)'
                ]

                has_exception = any(re.search(p, text, re.IGNORECASE) for p in exception_patterns)

                if not has_exception:
                    issues.append('CRITICAL: Solely automated decisions with legal/significant effects prohibited unless: explicit consent, necessary for contract, or authorized by law (Article 22)')

                # Check for safeguards even if exception applies
                safeguard_patterns = [
                    r'safeguards?',
                    r'(?:right\s+to\s+)?human\s+(?:intervention|review|oversight)',
                    r'express.*(?:views?|point\s+of\s+view)',
                    r'contest.*decision',
                    r'challenge.*decision'
                ]

                has_safeguards = any(re.search(p, text, re.IGNORECASE) for p in safeguard_patterns)

                if has_exception and not has_safeguards:
                    issues.append('CRITICAL: Automated decisions require safeguards - right to human intervention, express views, and contest decision')

        # 2. PROFILING
        profiling_patterns = [
            r'profiling',
            r'profile.*(?:behaviour|behavior|preferences?|characteristics?)',
            r'(?:analyze|analyse|predict).*(?:behaviour|behavior|performance|preferences?)',
            r'(?:personal\s+)?aspects?.*(?:individual|person)',
            r'categoris[ez].*(?:individuals?|people|users?|customers?)'
        ]

        has_profiling = any(re.search(p, text, re.IGNORECASE) for p in profiling_patterns)

        if has_profiling:
            # Check for information about profiling logic
            logic_patterns = [
                r'(?:how|explain).*(?:profiling|algorithm|system)\s+works?',
                r'logic\s+(?:involved|underlying)',
                r'significance.*(?:profiling|automated\s+processing)',
                r'consequences?.*(?:profiling|automated\s+processing)',
                r'criteria.*(?:used|considered)'
            ]

            has_logic_explanation = any(re.search(p, text, re.IGNORECASE) for p in logic_patterns)

            if not has_logic_explanation:
                warnings.append('Must provide meaningful information about profiling logic, significance and consequences (2025 transparency requirements)')

            # Check for special category data in profiling (extra protections)
            special_category_patterns = [
                r'(?:race|ethnic|political|religious|philosophical|belief)',
                r'health\s+data',
                r'(?:sex\s+life|sexual\s+orientation)',
                r'genetic\s+data',
                r'biometric\s+data',
                r'sensitive\s+(?:personal\s+)?data',
                r'special\s+categor(?:y|ies)'
            ]

            uses_special_category = any(re.search(p, text, re.IGNORECASE) for p in special_category_patterns)

            if uses_special_category and has_profiling:
                warnings.append('Profiling using special category data requires explicit consent or substantial public interest (Article 9)')

        # 3. HUMAN REVIEW REQUIREMENT (2025 strengthened)
        human_review_patterns = [
            r'human\s+(?:review|oversight|intervention|involvement)',
            r'(?:reviewed|checked|verified)\s+by.*(?:human|person|staff)',
            r'manual\s+(?:review|check|verification)',
            r'human\s+in\s+the\s+loop',
            r'human[\s-]in[\s-]the[\s-]loop'
        ]

        has_human_review = any(re.search(p, text, re.IGNORECASE) for p in human_review_patterns)

        if has_solely_automated and not has_human_review:
            warnings.append('2025 best practice: implement human review for high-stakes automated decisions')

        if has_human_review:
            # Check quality of human review (2025 emphasis - must be meaningful)
            meaningful_review_patterns = [
                r'meaningful\s+(?:human\s+)?(?:review|oversight)',
                r'(?:authority|power)\s+to\s+(?:change|override|reverse)',
                r'not.*(?:rubber[\s-]stamp|formality)',
                r'genuine\s+(?:assessment|consideration)',
                r'competent.*(?:review|assess)'
            ]

            has_meaningful = any(re.search(p, text, re.IGNORECASE) for p in meaningful_review_patterns)

            if not has_meaningful:
                warnings.append('2025 emphasis: human review must be meaningful - reviewer must have authority to change decision, not rubber-stamp')

        # 4. RIGHT TO EXPLANATION (2025 expanded)
        explanation_patterns = [
            r'right\s+to.*explanation',
            r'explain.*(?:decision|outcome|result)',
            r'how.*(?:decision\s+was\s+made|we\s+reached)',
            r'why.*(?:decision|outcome)',
            r'transparent.*(?:decision[\s-]making|processing)'
        ]

        has_explanation = any(re.search(p, text, re.IGNORECASE) for p in explanation_patterns)

        if (has_solely_automated or has_profiling) and not has_explanation:
            warnings.append('2025 expansion: individuals have right to explanation of automated decision logic and significance')

        if has_explanation:
            # Check for quality of explanation (2025 requirements)
            quality_patterns = [
                r'meaningful\s+(?:information|explanation)',
                r'(?:clear|plain|simple)\s+language',
                r'understandable',
                r'(?:specific|individualized)\s+explanation',
                r'factors.*(?:considered|influenced)'
            ]

            has_quality = any(re.search(p, text, re.IGNORECASE) for p in quality_patterns)

            if not has_quality:
                warnings.append('Explanations must be in clear language, meaningful, and specific to individual case (not generic)')

        # 5. AI AND MACHINE LEARNING (2025 specific provisions)
        ai_patterns = [
            r'\bAI\b',
            r'artificial\s+intelligence',
            r'machine\s+learning',
            r'\bML\b',
            r'neural\s+network',
            r'deep\s+learning',
            r'predictive\s+(?:model|analytics)',
            r'training\s+data'
        ]

        has_ai = any(re.search(p, text, re.IGNORECASE) for p in ai_patterns)

        if has_ai:
            # Check for AI-specific disclosures (2025 Data Use and Access Act)
            ai_disclosures = {
                'ai_use': r'(?:use|using|powered\s+by)\s+(?:AI|artificial\s+intelligence|machine\s+learning)',
                'training_data': r'training\s+data.*(?:source|bias|quality)',
                'accuracy': r'accuracy.*(?:rate|level|metrics?)',
                'limitations': r'limitations?.*(?:system|model|AI)',
                'human_oversight': r'human\s+(?:oversight|supervision|monitoring)'
            }

            disclosures_made = sum(1 for p in ai_disclosures.values() if re.search(p, text, re.IGNORECASE))

            if disclosures_made < 3:
                warnings.append('2025 AI provisions: disclose AI use, training data sources, accuracy rates, limitations, and human oversight')

            # Check for bias mitigation
            bias_patterns = [
                r'bias\s+(?:mitigation|testing|assessment)',
                r'fairness\s+(?:testing|assessment|evaluation)',
                r'discriminat(?:ion|ory)\s+(?:testing|checks?|monitoring)',
                r'equality\s+(?:impact|assessment)'
            ]

            has_bias_mitigation = any(re.search(p, text, re.IGNORECASE) for p in bias_patterns)

            if not has_bias_mitigation:
                warnings.append('2025 requirement: AI systems must be tested for bias and discrimination')

        # 6. CREDIT SCORING AND FINANCIAL DECISIONS
        credit_patterns = [
            r'credit\s+(?:scoring|score|rating|assessment|decision)',
            r'creditworthiness',
            r'(?:loan|mortgage|finance)\s+(?:application|decision|approval)',
            r'affordability\s+(?:check|assessment)',
            r'financial\s+(?:assessment|decision|profiling)'
        ]

        has_credit = any(re.search(p, text, re.IGNORECASE) for p in credit_patterns)

        if has_credit:
            # Credit decisions are high-stakes - extra scrutiny
            credit_requirements = {
                'factors': r'factors?.*(?:considered|affect|influence)',
                'improve': r'(?:how\s+to\s+)?improve.*(?:score|rating)',
                'review': r'(?:request|right\s+to)\s+(?:review|reconsider)',
                'adverse': r'adverse\s+(?:action|decision)\s+notice',
                'human_review': r'human\s+(?:review|intervention)'
            }

            credit_coverage = sum(1 for p in credit_requirements.values() if re.search(p, text, re.IGNORECASE))

            if credit_coverage < 3:
                warnings.append('Credit scoring must disclose: factors considered, how to improve score, right to review, and human oversight')

        # 7. EMPLOYMENT DECISIONS
        employment_patterns = [
            r'(?:recruitment|hiring|employment)\s+(?:decision|process|algorithm)',
            r'CV\s+(?:screening|filtering|review)',
            r'candidate\s+(?:assessment|screening|selection|ranking)',
            r'job\s+(?:matching|recommendation)',
            r'applicant\s+tracking\s+system'
        ]

        has_employment = any(re.search(p, text, re.IGNORECASE) for p in employment_patterns)

        if has_employment:
            # Employment decisions are high-stakes
            employment_requirements = {
                'non_discrimination': r'(?:non[\s-])?discriminat(?:ion|ory)\s+(?:checks?|testing)',
                'human_review': r'human\s+(?:review|involvement|decision)',
                'criteria': r'(?:selection\s+)?criteria',
                'feedback': r'feedback.*(?:decision|rejection)',
                'challenge': r'(?:challenge|appeal|contest)'
            }

            employment_coverage = sum(1 for p in employment_requirements.values() if re.search(p, text, re.IGNORECASE))

            if employment_coverage < 3:
                warnings.append('Employment decisions must: test for discrimination, involve human review, disclose criteria, provide feedback')

        # 8. RIGHT TO CONTEST DECISION (2025 strengthened)
        contest_patterns = [
            r'contest.*decision',
            r'challenge.*decision',
            r'appeal',
            r'request.*reconsideration',
            r'dispute.*outcome'
        ]

        has_contest = any(re.search(p, text, re.IGNORECASE) for p in contest_patterns)

        if has_solely_automated and not has_contest:
            warnings.append('Must provide clear process to contest automated decisions')

        if has_contest:
            # Check for timeframe
            contest_timeframe_patterns = [
                r'within\s+(\d+)\s+(?:days?|weeks?|months?)',
                r'(?:time\s+)?(?:limit|deadline|period).*contest',
                r'as\s+soon\s+as\s+(?:possible|practicable)'
            ]

            has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in contest_timeframe_patterns)
            # Good practice to specify timeframe

        # 9. TRANSPARENCY AND INFORMATION (Article 13-15)
        transparency_info = {
            'existence': r'(?:existence|use)\s+of\s+automated\s+(?:decision[\s-]making|processing)',
            'logic': r'logic\s+(?:involved|underlying)',
            'significance': r'significance.*(?:processing|decision)',
            'consequences': r'(?:envisaged\s+)?consequences?'
        }

        transparency_score = sum(1 for p in transparency_info.values() if re.search(p, text, re.IGNORECASE))

        if (has_solely_automated or has_profiling) and transparency_score < 2:
            warnings.append('Must provide: existence of automated decision-making, logic involved, significance and consequences')

        # 10. AUDIT AND ACCOUNTABILITY (2025 requirement)
        audit_patterns = [
            r'audit',
            r'(?:monitor|review).*(?:algorithm|system|model)',
            r'(?:regular|periodic)\s+(?:testing|assessment|evaluation)',
            r'accountab(?:ility|le)',
            r'documentation.*(?:decision[\s-]making|processing)'
        ]

        has_audit = any(re.search(p, text, re.IGNORECASE) for p in audit_patterns)

        if has_ai and not has_audit:
            warnings.append('2025 requirement: regular auditing and monitoring of automated decision systems')

        # 11. SPECIAL PROTECTIONS FOR CHILDREN (2025 enhanced)
        children_automated_patterns = [
            r'child(?:ren)?.*(?:profiling|automated)',
            r'under\s+(?:13|16|18).*(?:automated|profiling)',
            r'minor.*(?:automated\s+decision|profiling)'
        ]

        has_children_automated = any(re.search(p, text, re.IGNORECASE) for p in children_automated_patterns)

        if has_children_automated:
            warnings.append('2025 enhanced protection: generally prohibited to use automated decisions/profiling on children unless explicit consent and child\'s best interests')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Automated decision-making violates Article 22 requirements',
                'legal_source': self.legal_source,
                'suggestion': 'Urgent compliance required: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 4:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Automated decision-making needs strengthening for 2025 compliance',
                'legal_source': self.legal_source,
                'suggestion': 'Key improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Automated decision-making could be improved',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Automated decision-making provisions appear compliant',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_automated_decisions_gate():
    gate = AutomatedDecisionsGate()

    # Test 1: Solely automated without safeguards
    test1 = """
    CREDIT SCORING SYSTEM

    Our algorithm automatically decides whether to approve your loan application.
    The decision is based on your credit score and is made entirely by the system.
    This decision has legal effects on your ability to obtain credit.
    """
    result1 = gate.check(test1, "credit_policy")
    assert result1['status'] == 'FAIL'
    assert 'Article 22' in str(result1) or 'safeguards' in str(result1).lower()

    # Test 2: Compliant automated decision with safeguards
    test2 = """
    AUTOMATED CREDIT DECISIONS

    We use automated processing to assess credit applications.
    However, you have the right to:
    - Human intervention and review
    - Express your point of view
    - Contest the decision

    The decision is based on explicit consent in your application.

    Our system considers: credit history, income, existing debts.
    You can request a full explanation of how the decision was made.
    """
    result2 = gate.check(test2, "credit_policy")
    assert result2['status'] in ['PASS', 'WARNING']

    # Test 3: AI with transparency (2025)
    test3 = """
    AI-POWERED RECRUITMENT

    We use artificial intelligence to screen CVs.
    All decisions involve human review - our AI assists but doesn't decide alone.

    Our AI system:
    - Is trained on diverse, representative data
    - Has been tested for bias and discrimination
    - Achieves 92% accuracy
    - Has limitations in assessing soft skills

    Human recruiters review all AI recommendations before making decisions.
    You can request feedback and challenge our decision.
    """
    result3 = gate.check(test3, "recruitment_policy")
    assert result3['status'] in ['PASS', 'WARNING']

    # Test 4: Profiling with explanation
    test4 = """
    CUSTOMER PROFILING

    We profile customer behavior to personalize recommendations.

    We provide meaningful information about:
    - How our profiling algorithm works
    - What factors influence recommendations
    - The significance and consequences of profiling
    - Your right to object to profiling

    You can request a clear explanation of how profiling affects you specifically.
    """
    result4 = gate.check(test4, "profiling_notice")
    assert result4['status'] in ['PASS', 'WARNING']

    print("All automated decisions gate tests passed!")


if __name__ == "__main__":
    test_automated_decisions_gate()
