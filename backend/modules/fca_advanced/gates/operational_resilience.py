import re


class OperationalResilienceGate:
    """
    FCA Operational Resilience Rules - PS21/3 (March 2025 full implementation)
    Covers: Important business services, impact tolerances, testing, governance, incident management
    """
    def __init__(self):
        self.name = "operational_resilience"
        self.severity = "critical"
        self.legal_source = "FCA PS21/3 Operational Resilience (full implementation 31 March 2025), SYSC 15A"

    def _is_relevant(self, text):
        """Check if document relates to operational resilience"""
        text_lower = text.lower()
        keywords = [
            'operational resilience', 'business continuity', 'disaster recovery',
            'important business service', 'impact tolerance', 'severe but plausible',
            'disruption', 'incident', 'recovery', 'critical function',
            'third party', 'outsourcing', 'cyber', 'it resilience',
            'business continuity plan', 'bcp'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to operational resilience',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. IMPORTANT BUSINESS SERVICES (IBS) - Core requirement
        ibs_patterns = [
            r'(?:important|critical)\s+business\s+services?',
            r'\bIBS\b',
            r'critical\s+(?:functions?|operations?|processes?)',
            r'essential\s+services?',
            r'key\s+business\s+services?'
        ]

        has_ibs = any(re.search(p, text, re.IGNORECASE) for p in ibs_patterns)

        if has_ibs:
            # Check for identification/mapping
            identification_patterns = [
                r'identif(?:y|ied|ication).*(?:important|critical)\s+(?:business\s+)?services?',
                r'(?:mapped|mapping|map).*(?:business\s+)?services?',
                r'(?:catalogue|inventory|register).*services?',
                r'assessment.*(?:important|critical)'
            ]

            has_identification = any(re.search(p, text, re.IGNORECASE) for p in identification_patterns)

            if not has_identification:
                warnings.append('Must identify and map Important Business Services (IBS) that customers rely on')

            # Check for examples of IBS
            ibs_examples = [
                r'payment(?:s)?\s+(?:processing|services?)',
                r'deposit\s+taking',
                r'lending',
                r'(?:customer\s+)?(?:accounts?|banking)',
                r'trading',
                r'settlement',
                r'custody',
                r'portfolio\s+management'
            ]

            has_examples = any(re.search(p, text, re.IGNORECASE) for p in ibs_examples)
            # Good to specify which services are important

        else:
            warnings.append('DEADLINE: March 2025 - Must identify Important Business Services (IBS)')

        # 2. IMPACT TOLERANCES - Critical requirement
        impact_tolerance_patterns = [
            r'impact\s+tolerances?',
            r'maximum\s+(?:tolerable|acceptable)\s+(?:impact|disruption)',
            r'tolerance\s+(?:levels?|thresholds?)',
            r'(?:maximum\s+)?(?:outage|downtime)\s+(?:tolerance|duration)'
        ]

        has_impact_tolerance = any(re.search(p, text, re.IGNORECASE) for p in impact_tolerance_patterns)

        if has_impact_tolerance:
            # Check for time-based tolerances
            time_tolerance_patterns = [
                r'(?:within\s+)?(\d+)\s+(?:hours?|days?|minutes?)',
                r'(?:maximum|no\s+more\s+than)\s+(\d+)\s+(?:hours?|days?)',
                r'(?:RTO|recovery\s+time\s+objective)[:\s]*(\d+)',
                r'resume.*within\s+(\d+)'
            ]

            has_time_tolerance = any(re.search(p, text, re.IGNORECASE) for p in time_tolerance_patterns)

            if not has_time_tolerance:
                warnings.append('Impact tolerances should specify maximum tolerable disruption time for each IBS')

            # Check for customer impact consideration
            customer_impact_patterns = [
                r'(?:impact|effect)\s+(?:on|to)\s+customers?',
                r'customer\s+(?:harm|detriment)',
                r'intolerable\s+(?:harm|impact)',
                r'customer\s+outcomes?'
            ]

            has_customer_impact = any(re.search(p, text, re.IGNORECASE) for p in customer_impact_patterns)

            if not has_customer_impact:
                warnings.append('Impact tolerances must be set with reference to impact on customers')

        else:
            issues.append('CRITICAL: Must set impact tolerances for each Important Business Service (March 2025 deadline)')

        # 3. SEVERE BUT PLAUSIBLE SCENARIOS
        scenario_patterns = [
            r'(?:severe\s+but\s+plausible|SBP)\s+scenarios?',
            r'stress\s+(?:testing|scenarios?)',
            r'scenario\s+(?:testing|analysis)',
            r'worst[\s-]case\s+scenarios?',
            r'extreme\s+(?:but\s+plausible|events?)'
        ]

        has_scenarios = any(re.search(p, text, re.IGNORECASE) for p in scenario_patterns)

        if has_scenarios:
            # Check for types of scenarios
            scenario_types = {
                'cyber': r'cyber\s+(?:attack|incident|breach)',
                'technology': r'(?:IT|technology|system)\s+(?:failure|outage)',
                'third_party': r'third[\s-]party\s+(?:failure|disruption)',
                'people': r'(?:loss\s+of\s+)?(?:key\s+)?(?:staff|people|personnel)',
                'site': r'(?:loss\s+of\s+)?(?:site|premises|building)',
                'pandemic': r'pandemic',
                'data_loss': r'data\s+(?:loss|breach|corruption)'
            }

            scenario_coverage = sum(1 for p in scenario_types.values() if re.search(p, text, re.IGNORECASE))

            if scenario_coverage < 3:
                warnings.append('Severe but plausible scenarios should cover: cyber, technology, third parties, people, sites, data loss')

        else:
            warnings.append('Must test against severe but plausible disruption scenarios')

        # 4. TESTING - Mandatory requirement
        testing_patterns = [
            r'(?:test|testing)',
            r'scenario\s+(?:test|analysis)',
            r'(?:simulation|drill|exercise)',
            r'resilience\s+test',
            r'disaster\s+recovery\s+test'
        ]

        has_testing = any(re.search(p, text, re.IGNORECASE) for p in testing_patterns)

        if has_testing:
            # Check for regular/periodic testing
            regular_testing_patterns = [
                r'(?:regular|periodic|annual|regularly)\s+(?:test|testing)',
                r'test.*(?:at\s+least|minimum)\s+(?:annually|yearly|once\s+a\s+year)',
                r'(?:annual|yearly)\s+(?:test|resilience\s+test)',
                r'test\s+(?:schedule|plan|programme)'
            ]

            has_regular_testing = any(re.search(p, text, re.IGNORECASE) for p in regular_testing_patterns)

            if not has_regular_testing:
                warnings.append('Must test operational resilience at least annually')

            # Check for lessons learned/continuous improvement
            improvement_patterns = [
                r'lessons\s+learned',
                r'continuous\s+improvement',
                r'(?:review|analyse|analyze)\s+(?:test\s+)?results?',
                r'post[\s-]incident\s+review',
                r'root\s+cause\s+analysis'
            ]

            has_improvement = any(re.search(p, text, re.IGNORECASE) for p in improvement_patterns)

            if not has_improvement:
                warnings.append('Testing should include lessons learned and continuous improvement process')

        else:
            warnings.append('Must conduct regular testing of operational resilience')

        # 5. GOVERNANCE AND OVERSIGHT - Board/Senior management
        governance_patterns = [
            r'governance',
            r'(?:board|senior\s+management)\s+(?:oversight|responsibility|accountability)',
            r'(?:board|directors?)\s+(?:review|approval|oversight)',
            r'management\s+information',
            r'MI\b.*resilience'
        ]

        has_governance = any(re.search(p, text, re.IGNORECASE) for p in governance_patterns)

        if has_governance:
            # Check for board-level responsibility
            board_patterns = [
                r'board.*(?:responsible|accountable|oversee)',
                r'(?:CEO|Chief\s+Executive|Managing\s+Director).*resilience',
                r'senior\s+management.*(?:responsible|accountable)',
                r'executive\s+(?:sponsor|owner|responsibility)'
            ]

            has_board_responsibility = any(re.search(p, text, re.IGNORECASE) for p in board_patterns)

            if not has_board_responsibility:
                warnings.append('Board and senior management must take accountability for operational resilience')

        else:
            warnings.append('Must establish clear governance and board oversight for operational resilience')

        # 6. INCIDENT MANAGEMENT
        incident_patterns = [
            r'incident\s+(?:management|response)',
            r'(?:major\s+)?incident\s+(?:procedure|plan|process)',
            r'incident\s+(?:handling|resolution)',
            r'(?:crisis|emergency)\s+(?:management|response)'
        ]

        has_incident = any(re.search(p, text, re.IGNORECASE) for p in incident_patterns)

        if has_incident:
            # Check for key components
            incident_components = {
                'detection': r'detect(?:ion)?',
                'escalation': r'escalat(?:e|ion)',
                'communication': r'communicat(?:e|ion).*(?:customers?|stakeholders?)',
                'response': r'response\s+(?:plan|procedure|team)',
                'recovery': r'recover(?:y)?',
                'notification': r'notif(?:y|ication).*(?:FCA|regulator)'
            }

            incident_coverage = sum(1 for p in incident_components.values() if re.search(p, text, re.IGNORECASE))

            if incident_coverage < 3:
                warnings.append('Incident management should cover: detection, escalation, communication, response, recovery, regulatory notification')

        else:
            warnings.append('Must have incident management procedures for operational disruptions')

        # 7. THIRD-PARTY DEPENDENCIES - Critical area
        third_party_patterns = [
            r'third[\s-]part(?:y|ies)',
            r'outsourc(?:e|ed|ing)',
            r'(?:service\s+)?providers?',
            r'(?:critical\s+)?(?:suppliers?|vendors?)',
            r'external\s+(?:dependencies|services?)',
            r'supply\s+chain'
        ]

        has_third_party = any(re.search(p, text, re.IGNORECASE) for p in third_party_patterns)

        if has_third_party:
            # Check for risk assessment
            third_party_risk_patterns = [
                r'(?:assess|assessment|evaluate|evaluation).*(?:third[\s-]party|supplier|vendor)\s+risk',
                r'due\s+diligence',
                r'(?:critical|important)\s+(?:third[\s-]part|suppliers?|vendors?)',
                r'concentration\s+risk'
            ]

            has_risk_assessment = any(re.search(p, text, re.IGNORECASE) for p in third_party_risk_patterns)

            if not has_risk_assessment:
                warnings.append('Must assess and manage third-party and outsourcing risks')

            # Check for contractual provisions
            contract_patterns = [
                r'contract(?:ual)?\s+(?:terms|provisions|requirements)',
                r'service\s+level\s+agreements?',
                r'\bSLA\b',
                r'exit\s+(?:strategy|plan)',
                r'right\s+to\s+audit'
            ]

            has_contracts = any(re.search(p, text, re.IGNORECASE) for p in contract_patterns)

            if not has_contracts:
                warnings.append('Third-party contracts should include SLAs, audit rights, and exit strategies')

            # Check for substitution/alternatives
            substitution_patterns = [
                r'(?:alternative|backup)\s+(?:provider|supplier)',
                r'substitut(?:e|ion|able)',
                r'(?:single\s+point\s+of\s+failure|SPOF)',
                r'redundanc(?:y|ies)',
                r'failover'
            ]

            has_substitution = any(re.search(p, text, re.IGNORECASE) for p in substitution_patterns)

            if not has_substitution:
                warnings.append('Should consider alternative providers/substitutability for critical third parties')

        else:
            warnings.append('Must identify and manage third-party dependencies and outsourcing')

        # 8. COMMUNICATION PLANS - Customer and stakeholder communication
        communication_patterns = [
            r'communicat(?:e|ion)\s+(?:plan|strategy)',
            r'(?:inform|notify).*customers?',
            r'(?:customer|stakeholder)\s+communicat(?:ion|ions)',
            r'(?:internal|external)\s+communicat(?:ion|ions)',
            r'(?:website|social\s+media|email).*(?:update|notification)'
        ]

        has_communication = any(re.search(p, text, re.IGNORECASE) for p in communication_patterns)

        if has_communication:
            # Check for timely communication
            timely_patterns = [
                r'(?:promptly|immediately|quickly|timely)\s+(?:inform|notify|communicate)',
                r'as\s+soon\s+as\s+(?:possible|practicable)',
                r'without\s+(?:undue\s+)?delay',
                r'regular\s+updates?'
            ]

            has_timely = any(re.search(p, text, re.IGNORECASE) for p in timely_patterns)

            if not has_timely:
                warnings.append('Communication plans should emphasize timely customer notification during disruptions')

        else:
            warnings.append('Must have communication plans for informing customers during disruptions')

        # 9. CYBER RESILIENCE - Specific focus area
        cyber_patterns = [
            r'cyber\s+(?:resilience|security|incident)',
            r'cyber\s+attack',
            r'(?:malware|ransomware|phishing)',
            r'information\s+security',
            r'IT\s+security'
        ]

        has_cyber = any(re.search(p, text, re.IGNORECASE) for p in cyber_patterns)

        if has_cyber:
            # Check for cyber-specific measures
            cyber_measures = {
                'prevention': r'prevent(?:ion|ive)',
                'detection': r'detect(?:ion)?.*(?:threat|breach|attack)',
                'response': r'(?:cyber\s+)?(?:incident\s+)?response',
                'recovery': r'recover(?:y)?.*(?:cyber|attack|breach)',
                'backup': r'backup.*(?:data|systems?)',
                'patching': r'(?:patch|update).*(?:systems?|software)'
            }

            cyber_coverage = sum(1 for p in cyber_measures.values() if re.search(p, text, re.IGNORECASE))

            if cyber_coverage < 3:
                warnings.append('Cyber resilience should cover: prevention, detection, response, recovery, backups, patching')

        else:
            warnings.append('Must address cyber resilience as key operational risk')

        # 10. DATA AND TECHNOLOGY - Infrastructure resilience
        data_tech_patterns = [
            r'(?:data|IT|technology)\s+(?:resilience|infrastructure)',
            r'(?:data\s+)?(?:backup|recovery)',
            r'(?:RTO|RPO)',  # Recovery Time/Point Objective
            r'(?:disaster\s+recovery|DR)',
            r'(?:high\s+)?(?:availability|redundancy)',
            r'(?:failover|fail[\s-]over)'
        ]

        has_data_tech = any(re.search(p, text, re.IGNORECASE) for p in data_tech_patterns)

        if has_data_tech:
            # Check for RTO/RPO
            rto_rpo_patterns = [
                r'RTO[:\s]*(\d+)',
                r'Recovery\s+Time\s+Objective[:\s]*(\d+)',
                r'RPO[:\s]*(\d+)',
                r'Recovery\s+Point\s+Objective[:\s]*(\d+)'
            ]

            has_rto_rpo = any(re.search(p, text, re.IGNORECASE) for p in rto_rpo_patterns)
            # Good practice to define RTO/RPO

        # 11. MAPPING AND DOCUMENTATION
        mapping_patterns = [
            r'(?:map|mapping|document(?:ation)?).*(?:processes?|dependencies|resources?)',
            r'(?:process|service)\s+(?:map|flow)',
            r'dependency\s+(?:map|analysis)',
            r'(?:resource|asset)\s+(?:inventory|register)'
        ]

        has_mapping = any(re.search(p, text, re.IGNORECASE) for p in mapping_patterns)

        if not has_mapping:
            warnings.append('Should map and document processes, dependencies, and resources for each IBS')

        # 12. SELF-ASSESSMENT AND REPORTING TO FCA (March 2025)
        reporting_patterns = [
            r'(?:self[\s-])?assessment',
            r'report(?:ing)?\s+(?:to\s+)?(?:FCA|regulator)',
            r'regulatory\s+(?:reporting|return)',
            r'compliance\s+(?:assessment|report)',
            r'(?:annual|regular)\s+(?:review|report)'
        ]

        has_reporting = any(re.search(p, text, re.IGNORECASE) for p in reporting_patterns)

        if not has_reporting:
            warnings.append('Must conduct self-assessment and report to FCA on operational resilience (March 2025)')

        # 13. BUSINESS CONTINUITY PLAN (BCP)
        bcp_patterns = [
            r'business\s+continuity\s+plan',
            r'\bBCP\b',
            r'continuity\s+(?:planning|arrangements?)',
            r'business\s+recovery'
        ]

        has_bcp = any(re.search(p, text, re.IGNORECASE) for p in bcp_patterns)

        if has_bcp:
            # Check for key components
            bcp_components = {
                'risk_assessment': r'risk\s+assessment',
                'recovery_strategy': r'recovery\s+(?:strategy|plan)',
                'alternative_sites': r'(?:alternative|backup)\s+(?:site|location|premises)',
                'key_personnel': r'key\s+(?:personnel|staff|employees)',
                'testing': r'(?:test|testing|exercise|drill)',
                'maintenance': r'(?:maintain|maintenance|review|update)'
            }

            bcp_coverage = sum(1 for p in bcp_components.values() if re.search(p, text, re.IGNORECASE))

            if bcp_coverage < 3:
                warnings.append('BCP should cover: risk assessment, recovery strategy, alternative sites, key personnel, testing, maintenance')

        else:
            warnings.append('Should have comprehensive Business Continuity Plan')

        # 14. MARCH 2025 DEADLINE REFERENCE
        deadline_patterns = [
            r'31\s+March\s+2025',
            r'March\s+2025\s+(?:deadline|implementation)',
            r'(?:by|before)\s+(?:31st\s+)?March\s+2025',
            r'2025\s+(?:deadline|implementation|compliance)'
        ]

        has_deadline_ref = any(re.search(p, text, re.IGNORECASE) for p in deadline_patterns)

        if not has_deadline_ref:
            warnings.append('REMINDER: Full operational resilience implementation deadline is 31 March 2025')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Operational resilience framework has critical gaps (March 2025 deadline)',
                'legal_source': self.legal_source,
                'suggestion': 'Urgent action required: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Operational resilience needs strengthening for March 2025 compliance',
                'legal_source': self.legal_source,
                'suggestion': 'Priority actions: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Operational resilience could be improved',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Operational resilience framework appears compliant with March 2025 requirements',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_operational_resilience_gate():
    gate = OperationalResilienceGate()

    # Test 1: No impact tolerances
    test1 = """
    OPERATIONAL RESILIENCE

    We have identified important business services including:
    - Payment processing
    - Customer accounts
    - Lending services

    We conduct regular testing of our business continuity plans.
    """
    result1 = gate.check(test1, "resilience_framework")
    assert result1['status'] == 'FAIL'
    assert 'impact tolerance' in str(result1).lower()

    # Test 2: No third-party risk management
    test2 = """
    BUSINESS CONTINUITY

    We have business continuity plans in place.
    We test our systems annually.
    We have identified critical functions.
    """
    result2 = gate.check(test2, "bcp")
    assert result2['status'] == 'WARNING'
    assert 'third party' in str(result2).lower() or 'third-party' in str(result2).lower()

    # Test 3: Compliant operational resilience (March 2025)
    test3 = """
    OPERATIONAL RESILIENCE FRAMEWORK (March 2025 Compliance)

    Important Business Services (IBS): We have identified and mapped our IBS:
    - Payment processing
    - Deposit taking and withdrawals
    - Customer account access
    - Lending operations

    Impact Tolerances: We have set impact tolerances for each IBS:
    - Payment processing: Maximum 2 hours disruption
    - Customer accounts: Maximum 4 hours disruption
    These are based on potential impact on customer outcomes.

    Severe But Plausible Scenarios: We test against:
    - Cyber attacks
    - IT system failures
    - Third-party provider failures
    - Loss of key personnel
    - Site unavailability
    - Data loss incidents

    Testing: We conduct annual testing and scenario analysis.
    Lessons learned are captured and drive continuous improvement.

    Governance: The Board has ultimate responsibility for operational resilience.
    The CEO is the executive sponsor. Regular MI is provided to senior management.

    Incident Management: We have procedures covering detection, escalation,
    communication to customers, response, recovery, and FCA notification.

    Third Parties: We assess critical third-party dependencies, conduct due diligence,
    have contractual SLAs and audit rights, and consider alternatives.

    Communication Plans: We will promptly notify customers of any disruptions
    via website, email, and social media with regular updates.

    Cyber Resilience: We have prevention, detection, response, and recovery
    capabilities including backups, patching, and security monitoring.

    Self-Assessment: We conduct annual self-assessment and report to the FCA
    on our operational resilience as required by 31 March 2025 deadline.
    """
    result3 = gate.check(test3, "resilience_framework")
    assert result3['status'] in ['PASS', 'WARNING']

    print("All operational resilience gate tests passed!")


if __name__ == "__main__":
    test_operational_resilience_gate()
