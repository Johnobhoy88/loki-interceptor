"""
R&D Tax Relief Validator
Validation for Research & Development tax relief claims

Legal References:
- Corporation Tax Act 2009, Part 13
- Finance Act 2024
- HMRC Research and Development Manual (CIRD)
- BIS Guidelines on the Meaning of R&D for Tax Purposes

2024/25 Schemes:
- SME R&D Relief: Enhanced credit at 86% or 10% tax credit (loss-making)
- RDEC (R&D Expenditure Credit): 20% above-the-line credit
- Merged scheme from April 2024: Single scheme at 20%
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional


class RDReliefValidator:
    """R&D tax relief compliance validator"""

    # 2024/25 rates (merged scheme from April 2024)
    MERGED_SCHEME_RATE = Decimal('20.00')  # Single scheme
    RDEC_RATE = Decimal('20.00')  # For pre-merger periods
    SME_ADDITIONAL_DEDUCTION = Decimal('86.00')  # 86% additional (pre-merger)
    SME_TAX_CREDIT_RATE = Decimal('10.00')  # For loss-making SMEs (pre-merger)

    # SME thresholds (Companies Act definition)
    SME_EMPLOYEES = 500
    SME_TURNOVER = Decimal('100000000.00')  # €100m
    SME_BALANCE_SHEET = Decimal('86000000.00')  # €86m

    # Qualifying expenditure categories
    QUALIFYING_CATEGORIES = [
        'staffing_costs',
        'software',
        'consumables',
        'subcontractor_costs',
        'externally_provided_workers',
        'data_licenses',
        'cloud_computing'
    ]

    def __init__(self):
        self.legal_source = "CTA 2009, Part 13; Finance Act 2024"

    def assess_qualifying_activity(self, text: str) -> Dict:
        """
        Assess if described activity qualifies as R&D

        Reference: CIRD81000 (Definition of R&D)
        """
        qualifying_indicators = []
        non_qualifying_indicators = []

        text_lower = text.lower()

        # Qualifying R&D indicators
        qualifying_patterns = [
            (r'scientific.*(?:advance|uncertainty|knowledge)', 'Scientific advance'),
            (r'technical.*(?:uncertainty|challenge|problem)', 'Technical uncertainty'),
            (r'new.*(?:process|product|service|material)', 'Novel development'),
            (r'existing.*(?:capabilit(?:y|ies)|technolog(?:y|ies)).*(?:not|extend)', 'Extends existing capabilities'),
            (r'systematic.*(?:investigation|inquiry|research)', 'Systematic investigation'),
            (r'resolv(?:e|ing).*(?:uncertainty|challenge)', 'Resolving uncertainty'),
        ]

        # Non-qualifying indicators
        non_qualifying_patterns = [
            (r'(?:routine|standard|conventional).*(?:work|development)', 'Routine work'),
            (r'off.*shelf|readily.*available', 'Using readily available solutions'),
            (r'market.*research|consumer.*research', 'Market research'),
            (r'social.*science|arts|humanities', 'Social sciences/humanities'),
            (r'legal.*compliance|regulatory.*requirement', 'Regulatory compliance'),
            (r'(?:cosmetic|aesthetic).*change', 'Cosmetic changes'),
        ]

        for pattern, indicator in qualifying_patterns:
            if re.search(pattern, text_lower):
                qualifying_indicators.append(indicator)

        for pattern, indicator in non_qualifying_patterns:
            if re.search(pattern, text_lower):
                non_qualifying_indicators.append(indicator)

        # Assessment
        if len(qualifying_indicators) >= 2 and len(non_qualifying_indicators) == 0:
            assessment = 'likely_qualifying'
            risk = 'low'
        elif len(non_qualifying_indicators) >= 2:
            assessment = 'likely_non_qualifying'
            risk = 'high'
        elif len(qualifying_indicators) > 0:
            assessment = 'potentially_qualifying'
            risk = 'medium'
        else:
            assessment = 'insufficient_information'
            risk = 'high'

        return {
            'rd_assessment': assessment,
            'risk_level': risk,
            'qualifying_indicators': qualifying_indicators,
            'non_qualifying_indicators': non_qualifying_indicators,
            'legal_reference': 'CIRD81000; BIS Guidelines 2023'
        }

    def validate_merged_scheme(self, text: str) -> Dict:
        """
        Validate merged R&D scheme information (from April 2024)

        Reference: FA 2024; CIRD80000
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'r&d' not in text_lower and 'research' not in text_lower:
            return {'applicable': False}

        # Check for outdated scheme mentions (pre-April 2024)
        if re.search(r'sme\s+(?:scheme|relief|rate)|sme\s+r&d', text_lower):
            # Check if referencing pre-2024
            if not re.search(r'(?:before|prior\s+to|until).*april\s+2024|historical', text_lower):
                warnings.append({
                    'type': 'scheme_may_be_outdated',
                    'severity': 'high',
                    'message': 'Reference to SME scheme may be outdated',
                    'note': 'SME and RDEC schemes merged into single scheme from April 2024',
                    'legal_reference': 'FA 2024, s13'
                })

        # Check for merged scheme rate
        if re.search(r'merged.*scheme|single.*scheme|april\s+2024', text_lower):
            if not re.search(r'20\s*%|twenty\s+percent', text_lower):
                issues.append({
                    'type': 'merged_scheme_rate_missing',
                    'severity': 'high',
                    'message': 'Merged scheme rate not specified',
                    'correct_rate': '20%',
                    'legal_reference': 'FA 2024, s13'
                })

        # Check for R&D intensive SME rules
        if 'intensive' in text_lower or '40%' in text:
            if not re.search(r'research.*intensive|r&d.*intensive', text_lower):
                warnings.append({
                    'type': 'intensive_sme_unclear',
                    'severity': 'medium',
                    'message': 'R&D intensive SME rules should be clarified',
                    'note': 'Enhanced relief available for R&D intensive SMEs (40%+ costs are R&D)',
                    'legal_reference': 'FA 2024, s13'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_qualifying_expenditure(self, text: str) -> Dict:
        """
        Validate qualifying R&D expenditure categories

        Reference: CTA 2009, s1041-1053
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for common non-qualifying costs being claimed
        non_qualifying_claims = {
            'patent_costs': (r'patent.*(?:cost|fee|application)', 'CTA 2009, s1052'),
            'capital_expenditure': (r'capital.*(?:expenditure|cost)|land|building', 'CTA 2009, s1051'),
            'non_rd_indirect': (r'marketing|sales|distribution|general\s+admin', 'CTA 2009, s1053'),
            'production_costs': (r'production.*cost|manufacturing.*routine', 'CTA 2009, s1044'),
        }

        for cost_type, (pattern, reference) in non_qualifying_claims.items():
            if re.search(pattern, text_lower):
                if re.search(r'(?:claim|qualify|eligible|allowable)', text_lower):
                    issues.append({
                        'type': f'non_qualifying_{cost_type}',
                        'severity': 'high',
                        'message': f'{cost_type.replace("_", " ").title()} not eligible for R&D relief',
                        'legal_reference': reference
                    })

        # Check for staffing costs documentation
        if re.search(r'staff|employee|payroll', text_lower):
            if not re.search(r'directly.*engaged|time.*record|allocation', text_lower):
                warnings.append({
                    'type': 'staffing_costs_documentation',
                    'severity': 'medium',
                    'message': 'Staffing costs should be for directly engaged employees',
                    'note': 'Must maintain time records showing R&D allocation',
                    'legal_reference': 'CTA 2009, s1123'
                })

        # Check for subcontractor rules
        if 'subcontract' in text_lower:
            if not re.search(r'connected|unconnected|at\s+cost', text_lower):
                warnings.append({
                    'type': 'subcontractor_rules_unclear',
                    'severity': 'high',
                    'message': 'Subcontractor relationship should be clarified',
                    'note': 'Different rules for connected/unconnected subcontractors',
                    'legal_reference': 'CTA 2009, s1128-1132'
                })

        # Check for EPW (Externally Provided Workers)
        if re.search(r'external.*worker|agency.*worker|contractor', text_lower):
            if not re.search(r'65\s*%|externally\s+provided\s+worker|epw', text_lower):
                warnings.append({
                    'type': 'epw_rate_not_mentioned',
                    'severity': 'medium',
                    'message': 'EPW cost attribution rate not mentioned',
                    'note': '65% of cost qualifies for externally provided workers',
                    'legal_reference': 'CTA 2009, s1127'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_advance_assurance(self, text: str) -> Dict:
        """
        Validate advance assurance information

        Reference: HMRC Advance Assurance process
        """
        warnings = []

        text_lower = text.lower()

        if 'advance assurance' not in text_lower and 'hmrc' not in text_lower:
            return {'applicable': False}

        # Check for eligibility mention
        if 'advance assurance' in text_lower:
            if not re.search(r'(?:first|initial|new).*claim|3.*year', text_lower):
                warnings.append({
                    'type': 'advance_assurance_eligibility',
                    'severity': 'medium',
                    'message': 'Advance assurance eligibility should be clarified',
                    'note': 'Available for companies making first 3 R&D claims',
                    'legal_reference': 'HMRC Advance Assurance guidance'
                })

        return {
            'applicable': True,
            'valid': True,
            'warnings': warnings
        }

    def validate_compliance_checks(self, text: str) -> Dict:
        """
        Validate compliance and HMRC check information

        Reference: CIRD89000 (Compliance checks)
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for additional information requirement
        if 'r&d' in text_lower and ('claim' in text_lower or 'relief' in text_lower):
            if not re.search(r'additional.*information|project\s+report|technical\s+narrative', text_lower):
                warnings.append({
                    'type': 'additional_information_not_mentioned',
                    'severity': 'high',
                    'message': 'Additional information requirement not mentioned',
                    'note': 'HMRC requires additional information form with all R&D claims',
                    'legal_reference': 'Finance Act 2023, Schedule 9'
                })

        # Check for pre-notification requirement
        if re.search(r'first.*(?:time|claim)|new.*claim', text_lower):
            if not re.search(r'pre-?notif(?:y|ication)|notify.*hmrc.*(?:advance|before)', text_lower):
                warnings.append({
                    'type': 'pre_notification_missing',
                    'severity': 'critical',
                    'message': 'Pre-notification requirement not mentioned',
                    'note': 'First-time claimants must notify HMRC 6 months before claim',
                    'legal_reference': 'Finance Act 2023, Schedule 9, Para 6'
                })

        # Check for qualifying cost threshold (new)
        if 'claim' in text_lower and 'r&d' in text_lower:
            if not re.search(r'£50,?000|fifty\s+thousand', text_lower):
                warnings.append({
                    'type': 'cost_threshold_not_mentioned',
                    'severity': 'medium',
                    'message': 'Minimum qualifying expenditure threshold not mentioned',
                    'note': 'Minimum £50,000 qualifying expenditure required',
                    'legal_reference': 'Finance Act 2024'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_project_documentation(self, text: str) -> Dict:
        """
        Validate R&D project documentation requirements

        Reference: CIRD81750 (Record keeping)
        """
        warnings = []

        text_lower = text.lower()

        if 'r&d' not in text_lower and 'research' not in text_lower:
            return {'applicable': False}

        required_documentation = {
            'project_description': r'project.*(?:description|detail|specification)',
            'scientific_uncertainty': r'(?:scientific|technical).*uncertainty',
            'advance_sought': r'advance|innovation|novel',
            'systematic_approach': r'systematic|methodical|planned',
            'competent_professional': r'competent\s+professional|qualified.*(?:scientist|engineer)',
        }

        missing_elements = []
        for element, pattern in required_documentation.items():
            if not re.search(pattern, text_lower):
                missing_elements.append(element.replace('_', ' ').title())

        if missing_elements and len(missing_elements) >= 3:
            warnings.append({
                'type': 'incomplete_documentation',
                'severity': 'high',
                'message': 'R&D documentation may be incomplete',
                'missing_elements': missing_elements,
                'note': 'HMRC requires comprehensive project documentation',
                'legal_reference': 'CIRD81750'
            })

        return {
            'applicable': True,
            'valid': True,
            'warnings': warnings
        }

    def comprehensive_rd_check(self, text: str) -> Dict:
        """
        Run comprehensive R&D tax relief compliance check
        """
        results = {
            'qualifying_activity': self.assess_qualifying_activity(text),
            'merged_scheme': self.validate_merged_scheme(text),
            'qualifying_expenditure': self.validate_qualifying_expenditure(text),
            'advance_assurance': self.validate_advance_assurance(text),
            'compliance_checks': self.validate_compliance_checks(text),
            'documentation': self.validate_project_documentation(text)
        }

        all_issues = []
        all_warnings = []

        for check_name, check_result in results.items():
            if 'issues' in check_result:
                all_issues.extend(check_result['issues'])
            if 'warnings' in check_result:
                all_warnings.extend(check_result['warnings'])

        # Overall R&D qualification assessment
        rd_assessment = results['qualifying_activity'].get('rd_assessment', 'insufficient_information')

        return {
            'overall_assessment': rd_assessment,
            'overall_valid': len(all_issues) == 0,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings),
            'detailed_results': results,
            'all_issues': all_issues,
            'all_warnings': all_warnings,
            'recommendation': 'Seek specialist R&D tax advisor for complex claims',
            'legal_source': self.legal_source
        }
