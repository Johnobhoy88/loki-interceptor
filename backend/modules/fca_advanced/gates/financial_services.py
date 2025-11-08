import re


class FinancialServicesGate:
    """
    FCA Conduct Rules, Client Money Rules, Consumer Duty (2025 updates)
    Covers: Conduct rules, client money protection, complaints, vulnerable customers
    """
    def __init__(self):
        self.name = "financial_services"
        self.severity = "critical"
        self.legal_source = "FCA Handbook: PRIN (Principles), COBS (Conduct), CASS (Client Assets), Consumer Duty 2023"

    def _is_relevant(self, text):
        """Check if document relates to financial services"""
        text_lower = text.lower()
        keywords = [
            'fca', 'financial conduct authority', 'authorised', 'authorized',
            'financial service', 'client money', 'client asset',
            'conduct', 'consumer duty', 'treating customers fairly',
            'complaint', 'vulnerable', 'financial promotion',
            'regulated activity', 'firm', 'fscs'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to FCA-regulated financial services',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []
        issues = []
        warnings = []

        # 1. FCA AUTHORISATION STATUS
        authorisation_patterns = [
            r'(?:authorised|authorized)\s+(?:and\s+regulated\s+)?by\s+(?:the\s+)?(?:FCA|Financial\s+Conduct\s+Authority)',
            r'FCA\s+(?:firm\s+)?(?:reference|number|FRN)',
            r'(?:FRN|firm\s+reference\s+number)[:\s]*(\d{6})',
            r'register\.fca\.org\.uk'
        ]

        has_authorisation = any(re.search(p, text, re.IGNORECASE) for p in authorisation_patterns)

        # Check for FRN (should be 6 digits)
        frn_match = re.search(r'(?:FRN|firm\s+reference\s+number)[:\s]*(\d+)', text, re.IGNORECASE)
        if frn_match:
            frn = frn_match.group(1)
            if len(frn) != 6:
                warnings.append(f'FRN should be 6 digits (found: {frn})')

        if not has_authorisation:
            warnings.append('Should state FCA authorisation status and FRN')

        # 2. FCA PRINCIPLES FOR BUSINESSES (PRIN)
        principles = {
            'integrity': r'integrit(?:y|ous)',
            'skill_care_diligence': r'(?:skill|care|diligence)',
            'management_control': r'(?:management|control|governance)',
            'financial_prudence': r'financial\s+(?:prudence|resources)',
            'market_conduct': r'market\s+conduct',
            'customers_interests': r'customers?\'?\s+(?:interests?|best\s+interests?)',
            'communications': r'(?:clear|fair|not\s+misleading)\s+(?:communications?|information)',
            'conflicts': r'conflicts?\s+of\s+interest',
            'customers_relationships': r'(?:relationship|dealing)\s+(?:with|of\s+trust)',
            'clients_assets': r'client(?:s\'?)?\s+(?:assets?|money)',
            'relations_regulators': r'relations?\s+(?:with|between).*(?:FCA|regulator)'
        }

        principles_found = sum(1 for p in principles.values() if re.search(p, text, re.IGNORECASE))

        # Good practice to reference principles

        # 3. CONSUMER DUTY (Came into force July 2023, full implementation 2024-2025)
        consumer_duty_patterns = [
            r'Consumer\s+Duty',
            r'act\s+(?:to\s+)?deliver\s+good\s+outcomes',
            r'(?:foreseeable\s+)?harm',
            r'(?:retail\s+)?customers?.*(?:good\s+outcomes|best\s+interests)',
            r'vulnerable\s+customers?'
        ]

        has_consumer_duty = any(re.search(p, text, re.IGNORECASE) for p in consumer_duty_patterns)

        if has_consumer_duty:
            # Check for four outcomes
            four_outcomes = {
                'products_services': r'products?\s+(?:and\s+)?services?\s+(?:outcome|meet\s+needs)',
                'price_value': r'(?:price|value|fair\s+value)\s+outcome',
                'consumer_understanding': r'(?:consumer\s+)?understanding\s+outcome',
                'consumer_support': r'(?:consumer\s+)?support\s+outcome'
            }

            outcomes_mentioned = sum(1 for p in four_outcomes.values() if re.search(p, text, re.IGNORECASE))

            if outcomes_mentioned < 2:
                warnings.append('Consumer Duty: should address four outcomes - products/services, price/value, understanding, support')

        else:
            warnings.append('2025: Consumer Duty requires firms to deliver good outcomes for retail customers')

        # 4. CLIENT MONEY RULES (CASS 7)
        client_money_patterns = [
            r'client\s+money',
            r'client\s+bank\s+account',
            r'segregat(?:e|ed|ion)',
            r'\bCASS\b',
            r'client\s+assets?',
            r'(?:hold|holding)\s+(?:your\s+)?(?:money|funds)'
        ]

        has_client_money = any(re.search(p, text, re.IGNORECASE) for p in client_money_patterns)

        if has_client_money:
            # Check for segregation
            segregation_patterns = [
                r'segregat(?:e|ed|ion)',
                r'separate\s+(?:account|bank\s+account)',
                r'(?:kept|held)\s+(?:separate|separately)',
                r'client\s+(?:money|bank)\s+account'
            ]

            has_segregation = any(re.search(p, text, re.IGNORECASE) for p in segregation_patterns)

            if not has_segregation:
                issues.append('CRITICAL: Client money must be segregated in separate client bank accounts (CASS 7)')

            # Check for daily reconciliation mention
            reconciliation_patterns = [
                r'reconcil(?:e|iation)',
                r'daily\s+(?:checks?|reconcil)',
                r'(?:internal|external)\s+reconciliation'
            ]

            has_reconciliation = any(re.search(p, text, re.IGNORECASE) for p in reconciliation_patterns)

            if not has_reconciliation:
                warnings.append('CASS 7: daily reconciliation of client money required')

            # Check for FSCS protection mention
            fscs_patterns = [
                r'\bFSCS\b',
                r'Financial\s+Services\s+Compensation\s+Scheme',
                r'protected.*(?:up\s+to\s+)?£85,?000',
                r'deposit\s+protection'
            ]

            has_fscs = any(re.search(p, text, re.IGNORECASE) for p in fscs_patterns)

            if not has_fscs:
                warnings.append('Should inform clients about FSCS protection (up to £85,000 per person per firm)')

            # Check for title transfer
            title_transfer_patterns = [
                r'title\s+transfer',
                r'ownership\s+(?:of|transfers?)',
                r'(?:no\s+longer|not)\s+client\s+money'
            ]

            has_title_transfer = any(re.search(p, text, re.IGNORECASE) for p in title_transfer_patterns)
            # If title transfer, different rules apply

        # 5. COMPLAINTS HANDLING (DISP)
        complaints_patterns = [
            r'complaint',
            r'how\s+to\s+complain',
            r'if\s+you\'?re?\s+(?:not\s+)?(?:satisfied|happy|unhappy)',
            r'dissatisfied'
        ]

        has_complaints = any(re.search(p, text, re.IGNORECASE) for p in complaints_patterns)

        if has_complaints:
            # Check for 8-week timeframe
            timeframe_patterns = [
                r'(?:8|eight)\s+weeks?',
                r'within\s+8\s+weeks',
                r'(?:promptly|as\s+soon\s+as\s+(?:possible|practicable))',
                r'final\s+response'
            ]

            has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)

            if not has_timeframe:
                warnings.append('Complaints: must provide final response within 8 weeks (or explain why not)')

            # Check for Financial Ombudsman Service reference
            fos_patterns = [
                r'Financial\s+Ombudsman\s+Service',
                r'\bFOS\b',
                r'ombudsman',
                r'financial[\s-]ombudsman\.org\.uk',
                r'0800\s+023\s+4567'
            ]

            has_fos = any(re.search(p, text, re.IGNORECASE) for p in fos_patterns)

            if not has_fos:
                issues.append('CRITICAL: Must inform customers of right to refer complaint to Financial Ombudsman Service')

            # Check for FOS timeframe (6 months from final response)
            fos_timeframe_patterns = [
                r'(?:6|six)\s+months?.*(?:FOS|Financial\s+Ombudsman)',
                r'(?:FOS|Financial\s+Ombudsman).*(?:6|six)\s+months?',
                r'within\s+6\s+months\s+(?:of|from).*final\s+response'
            ]

            has_fos_timeframe = any(re.search(p, text, re.IGNORECASE) for p in fos_timeframe_patterns)

            if has_fos and not has_fos_timeframe:
                warnings.append('Should inform customers: 6 months to refer to FOS from date of final response')

        else:
            warnings.append('Should provide clear complaints procedure')

        # 6. VULNERABLE CUSTOMERS (Consumer Duty & FG21/1)
        vulnerable_patterns = [
            r'vulnerable\s+(?:customers?|consumers?|clients?)',
            r'(?:customers?|consumers?)\s+(?:in\s+)?vulnerable\s+(?:circumstances?|situations?)',
            r'vulnerability',
            r'health\s+(?:conditions?|issues?)',
            r'financial\s+(?:difficulty|hardship)',
            r'life\s+events?',
            r'resilience',
            r'capability'
        ]

        has_vulnerable = any(re.search(p, text, re.IGNORECASE) for p in vulnerable_patterns)

        if has_vulnerable:
            # Check for four drivers of vulnerability (FG21/1)
            vulnerability_drivers = {
                'health': r'health\s+(?:conditions?|issues?|problems?)',
                'life_events': r'life\s+events?\s+(?:such\s+as\s+)?(?:bereavement|divorce|redundancy)',
                'resilience': r'(?:low\s+)?(?:financial\s+)?resilience',
                'capability': r'(?:low\s+)?(?:financial\s+)?capability'
            }

            drivers_mentioned = sum(1 for p in vulnerability_drivers.values() if re.search(p, text, re.IGNORECASE))

            if drivers_mentioned < 2:
                warnings.append('Vulnerability guidance FG21/1: consider four drivers - health, life events, resilience, capability')

            # Check for reasonable adjustments
            adjustments_patterns = [
                r'reasonable\s+adjustments?',
                r'additional\s+support',
                r'extra\s+(?:help|support|care)',
                r'tailored\s+(?:support|service)',
                r'flexible\s+(?:approach|arrangements?)'
            ]

            has_adjustments = any(re.search(p, text, re.IGNORECASE) for p in adjustments_patterns)

            if not has_adjustments:
                warnings.append('Should provide reasonable adjustments and additional support for vulnerable customers')

        else:
            warnings.append('Consumer Duty 2025: must identify and support vulnerable customers')

        # 7. CONFLICTS OF INTEREST (SYSC 10)
        conflicts_patterns = [
            r'conflicts?\s+of\s+interest',
            r'(?:identify|manage|prevent).*conflicts?',
            r'independent\s+(?:advice|recommendation)',
            r'commission',
            r'inducements?'
        ]

        has_conflicts = any(re.search(p, text, re.IGNORECASE) for p in conflicts_patterns)

        if has_conflicts:
            # Check for management/disclosure
            management_patterns = [
                r'(?:manage|mitigate|prevent|address)\s+conflicts?',
                r'conflicts?\s+(?:policy|register)',
                r'disclose.*conflicts?',
                r'declare.*conflicts?'
            ]

            has_management = any(re.search(p, text, re.IGNORECASE) for p in management_patterns)

            if not has_management:
                warnings.append('Conflicts of interest must be managed and disclosed to clients')

        # 8. FINANCIAL PROMOTIONS (FINANCIAL PROMOTIONS ORDER, COBS 4)
        promotion_patterns = [
            r'financial\s+promotion',
            r'(?:advertis(?:e|ing|ement)|marketing|promot(?:e|ing|ion))',
            r'(?:investment|product)\s+(?:advertis|promotion)'
        ]

        has_promotion = any(re.search(p, text, re.IGNORECASE) for p in promotion_patterns)

        if has_promotion:
            # Check for fair, clear, not misleading
            fcnm_patterns = [
                r'fair,?\s+clear\s+(?:and\s+)?(?:not|&)\s+misleading',
                r'COBS\s+4',
                r'clear,?\s+fair',
                r'not\s+misleading'
            ]

            has_fcnm = any(re.search(p, text, re.IGNORECASE) for p in fcnm_patterns)

            if not has_fcnm:
                warnings.append('Financial promotions must be fair, clear and not misleading (COBS 4.2)')

            # Check for risk warnings
            risk_warnings = [
                r'capital\s+at\s+risk',
                r'value.*(?:can\s+)?(?:go\s+down|fall)',
                r'may\s+(?:not\s+)?get\s+back',
                r'past\s+performance.*not.*(?:guide|indication)',
                r'not\s+guaranteed'
            ]

            has_risk_warning = any(re.search(p, text, re.IGNORECASE) for p in risk_warnings)

            if not has_risk_warning:
                warnings.append('Financial promotions should include appropriate risk warnings')

        # 9. TREATING CUSTOMERS FAIRLY (TCF) - predecessor to Consumer Duty
        tcf_patterns = [
            r'Treating\s+Customers\s+Fairly',
            r'\bTCF\b',
            r'fair\s+treatment',
            r'customers?.*(?:fairly|fair\s+outcomes?)'
        ]

        has_tcf = any(re.search(p, text, re.IGNORECASE) for p in tcf_patterns)

        # TCF is now largely superseded by Consumer Duty

        # 10. KNOW YOUR CUSTOMER (KYC) / AML
        kyc_patterns = [
            r'\bKYC\b',
            r'Know\s+Your\s+Customer',
            r'customer\s+due\s+diligence',
            r'\bCDD\b',
            r'(?:anti[\s-])?money\s+laundering',
            r'\bAML\b',
            r'(?:identify|verification).*(?:customer|identity)',
            r'proof\s+of\s+(?:identity|address)'
        ]

        has_kyc = any(re.search(p, text, re.IGNORECASE) for p in kyc_patterns)

        if has_kyc:
            # Check for documentation requirements
            docs_patterns = [
                r'(?:passport|driving\s+licence|ID\s+card)',
                r'proof\s+of\s+(?:identity|address)',
                r'(?:utility\s+bill|bank\s+statement)',
                r'verification\s+(?:documents?|checks?)'
            ]

            has_docs = any(re.search(p, text, re.IGNORECASE) for p in docs_patterns)
            # Good to specify required documents

        # 11. SUITABILITY AND APPROPRIATENESS (COBS 9 & 10)
        suitability_patterns = [
            r'suitability',
            r'suitable\s+(?:for\s+)?(?:you|your\s+(?:needs|circumstances))',
            r'appropriateness',
            r'appropriate\s+(?:for\s+)?(?:you|your\s+(?:needs|circumstances))',
            r'assess.*(?:needs|circumstances|objectives?|risk\s+tolerance)'
        ]

        has_suitability = any(re.search(p, text, re.IGNORECASE) for p in suitability_patterns)

        if has_suitability:
            # Check for suitability assessment
            assessment_patterns = [
                r'(?:assess|assessment|determine|establish).*(?:your\s+)?(?:needs|circumstances|objectives?)',
                r'(?:knowledge|experience)\s+(?:of|in)\s+(?:investments?|products?)',
                r'financial\s+(?:situation|circumstances)',
                r'risk\s+(?:appetite|tolerance|profile)',
                r'investment\s+(?:objectives?|goals?|time\s+horizon)'
            ]

            assessment_coverage = sum(1 for p in assessment_patterns if re.search(p, text, re.IGNORECASE))

            if assessment_coverage < 2:
                warnings.append('Suitability assessment should cover: needs, knowledge/experience, financial situation, risk tolerance, objectives')

        # 12. PRODUCT GOVERNANCE (PROD)
        product_governance_patterns = [
            r'product\s+governance',
            r'target\s+market',
            r'distribution\s+strategy',
            r'(?:value|fair\s+value)\s+assessment',
            r'product\s+(?:design|approval|review)'
        ]

        has_product_governance = any(re.search(p, text, re.IGNORECASE) for p in product_governance_patterns)

        if has_product_governance:
            # Check for target market definition
            target_market_patterns = [
                r'target\s+market',
                r'intended\s+(?:customers?|for)',
                r'suitable\s+for.*(?:customers?|investors?)\s+who',
                r'not\s+suitable\s+for'
            ]

            has_target_market = any(re.search(p, text, re.IGNORECASE) for p in target_market_patterns)

            if not has_target_market:
                warnings.append('Product governance: should define target market and who product is/isn\'t suitable for')

        # 13. RECORD KEEPING (SYSC 9)
        records_patterns = [
            r'(?:keep|maintain|retain)\s+records?',
            r'record(?:[\s-])?keeping',
            r'retain.*(?:documents?|information|data)',
            r'(?:5|five)\s+years?.*(?:records?|documents?)'
        ]

        has_records = any(re.search(p, text, re.IGNORECASE) for p in records_patterns)

        if not has_records:
            warnings.append('FCA requires adequate record-keeping (typically 5+ years)')

        # Determine overall status
        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Financial services provisions have critical FCA compliance gaps',
                'legal_source': self.legal_source,
                'suggestion': 'Urgent fixes required: ' + '; '.join(issues[:2]),
                'spans': spans,
                'details': issues + warnings
            }

        if len(warnings) >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Financial services provisions need strengthening for FCA compliance',
                'legal_source': self.legal_source,
                'suggestion': 'Key improvements: ' + '; '.join(warnings[:3]),
                'spans': spans,
                'details': warnings
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Financial services provisions could be improved',
                'legal_source': self.legal_source,
                'suggestion': '; '.join(warnings[:2]),
                'spans': spans,
                'details': warnings
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Financial services provisions appear FCA compliant',
            'legal_source': self.legal_source,
            'spans': spans
        }


# Test cases
def test_financial_services_gate():
    gate = FinancialServicesGate()

    # Test 1: No FOS reference in complaints
    test1 = """
    COMPLAINTS PROCEDURE

    If you have a complaint, please contact us at complaints@firm.com

    We will respond within 8 weeks with our final response.
    """
    result1 = gate.check(test1, "complaints_procedure")
    assert result1['status'] == 'FAIL'
    assert 'Financial Ombudsman' in str(result1) or 'FOS' in str(result1)

    # Test 2: Client money not segregated
    test2 = """
    CLIENT MONEY

    We hold client money in our bank account.
    Your funds are protected up to £85,000 by the FSCS.
    """
    result2 = gate.check(test2, "client_money_policy")
    assert result2['status'] == 'FAIL'
    assert 'segregat' in str(result2).lower() or 'separate' in str(result2).lower()

    # Test 3: Compliant financial services document
    test3 = """
    FINANCIAL SERVICES INFORMATION

    We are authorised and regulated by the Financial Conduct Authority (FRN: 123456).
    You can check our registration at register.fca.org.uk

    Consumer Duty: We act to deliver good outcomes for our retail customers across:
    - Products and services
    - Price and value
    - Consumer understanding
    - Consumer support

    Client Money: Your money is held in segregated client bank accounts.
    Daily reconciliation is performed. FSCS protection applies (up to £85,000).

    Vulnerable Customers: We provide reasonable adjustments and additional support
    considering health, life events, resilience, and capability.

    Complaints: If unhappy, contact complaints@firm.com
    We'll respond within 8 weeks. If dissatisfied, you can refer to the
    Financial Ombudsman Service (www.financial-ombudsman.org.uk, 0800 023 4567)
    within 6 months of our final response.
    """
    result3 = gate.check(test3, "terms_business")
    assert result3['status'] in ['PASS', 'WARNING']

    print("All financial services gate tests passed!")


if __name__ == "__main__":
    test_financial_services_gate()
