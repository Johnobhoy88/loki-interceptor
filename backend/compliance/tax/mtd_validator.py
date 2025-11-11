"""
Making Tax Digital (MTD) Validator
Comprehensive validation for HMRC Making Tax Digital requirements

Legal References:
- Finance (No.2) Act 2017 - MTD Framework
- The Value Added Tax (Digital Requirements) (Amendment) Regulations 2021
- Income Tax (Making Tax Digital for Income Tax Self Assessment) Regulations 2021
- HMRC Notice 700/22: Making Tax Digital for VAT
- HMRC Notice: Making Tax Digital for Income Tax Self Assessment

2024/25 Requirements:
- MTD for VAT: Mandatory for ALL VAT-registered businesses
- MTD for ITSA: Phased rollout (£50k+ from April 2026, £30k+ from April 2027)
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class MTDValidator:
    """Making Tax Digital compliance validator"""

    # MTD for VAT mandatory dates
    MTD_VAT_MANDATORY_DATE = datetime(2019, 4, 1)

    # MTD for ITSA rollout schedule
    MTD_ITSA_PHASE1_DATE = datetime(2026, 4, 6)  # £50k+ threshold
    MTD_ITSA_PHASE2_DATE = datetime(2027, 4, 6)  # £30k+ threshold

    # Functional compatible software requirements
    REQUIRED_SOFTWARE_FUNCTIONS = [
        'digital_records',
        'digital_links',
        'api_submission',
        'hmrc_compatible'
    ]

    def __init__(self):
        self.legal_source = "Finance (No.2) Act 2017; MTD Regulations 2021"

    def validate_vat_mtd_compliance(
        self,
        text: str,
        vat_registered: bool = True,
        registration_date: Optional[datetime] = None
    ) -> Dict:
        """
        Validate MTD for VAT compliance

        Reference: HMRC Notice 700/22
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for mandatory status acknowledgment
        if vat_registered:
            if any(term in text_lower for term in ['mtd optional', 'mtd voluntary', 'choose mtd']):
                issues.append({
                    'type': 'mtd_vat_mandatory_error',
                    'severity': 'critical',
                    'message': 'MTD for VAT is MANDATORY for ALL VAT-registered businesses since April 2019',
                    'legal_reference': 'MTD Regulations 2021, Reg 3'
                })

        # Check for paper return mentions (no longer allowed)
        paper_patterns = [
            r'paper\s+vat\s+return',
            r'manual\s+vat\s+filing',
            r'post.*vat.*return',
            r'vat.*return.*by\s+post'
        ]

        for pattern in paper_patterns:
            if re.search(pattern, text_lower):
                issues.append({
                    'type': 'paper_return_error',
                    'severity': 'critical',
                    'message': 'Paper VAT returns are no longer accepted. Must use MTD-compatible software',
                    'legal_reference': 'HMRC Notice 700/22, Section 3'
                })
                break

        # Check for digital records requirement
        if not re.search(r'digital\s+record', text_lower):
            warnings.append({
                'type': 'digital_records_missing',
                'severity': 'medium',
                'message': 'Should specify requirement to keep digital records',
                'suggestion': 'MTD requires businesses to keep records digitally and preserve them in digital form'
            })

        # Check for digital links requirement
        if not re.search(r'digital\s+link', text_lower):
            warnings.append({
                'type': 'digital_links_missing',
                'severity': 'medium',
                'message': 'Should mention digital links requirement',
                'suggestion': 'Digital links must transfer data between software without manual intervention'
            })

        # Check for compatible software mention
        software_patterns = [
            r'mtd[-\s]compatible\s+software',
            r'hmrc[-\s]recognized\s+software',
            r'bridging\s+software',
            r'api\s+connection'
        ]

        has_software_mention = any(re.search(p, text_lower) for p in software_patterns)
        if not has_software_mention:
            warnings.append({
                'type': 'software_requirement_missing',
                'severity': 'medium',
                'message': 'Should specify need for MTD-compatible software',
                'suggestion': 'Businesses must use HMRC-recognized MTD-compatible software or bridging software'
            })

        # Check for exemption clarity
        if 'exempt' in text_lower and 'mtd' in text_lower:
            # Very limited exemptions exist (e.g., insolvency practitioners)
            if not re.search(r'(?:insolvency|practitioner|religious society)', text_lower):
                warnings.append({
                    'type': 'exemption_unclear',
                    'severity': 'high',
                    'message': 'MTD exemptions are very limited - clarify if exemption applies',
                    'suggestion': 'Only specific groups exempt: insolvency practitioners acting as such, religious societies'
                })

        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'requirements': {
                'digital_records': True,
                'digital_links': True,
                'compatible_software': True,
                'api_submission': True
            }
        }

    def validate_itsa_mtd_compliance(
        self,
        text: str,
        business_income: Optional[float] = None,
        tax_year: str = "2024/25"
    ) -> Dict:
        """
        Validate MTD for Income Tax Self Assessment compliance

        Reference: Income Tax (MTD for ITSA) Regulations 2021

        Rollout schedule:
        - April 2026: Sole traders/landlords with income £50k+
        - April 2027: Sole traders/landlords with income £30k+
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for outdated implementation dates
        outdated_dates = [
            (r'mtd.*itsa.*2023', '2023'),
            (r'mtd.*itsa.*2024', '2024'),
            (r'itsa.*from\s+april\s+2024', '2024'),
        ]

        for pattern, year in outdated_dates:
            if re.search(pattern, text_lower):
                issues.append({
                    'type': 'outdated_mtd_itsa_date',
                    'severity': 'high',
                    'message': f'MTD for ITSA dates are outdated ({year})',
                    'correction': 'MTD for ITSA: April 2026 (£50k+), April 2027 (£30k+)',
                    'legal_reference': 'MTD for ITSA Regulations 2021 (as amended 2024)'
                })

        # Check for threshold clarity
        if 'itsa' in text_lower or 'income tax' in text_lower and 'digital' in text_lower:
            threshold_mentioned = re.search(r'£(\d{1,3}(?:,\d{3})*(?:k)?)', text_lower)

            if not threshold_mentioned:
                warnings.append({
                    'type': 'threshold_missing',
                    'severity': 'medium',
                    'message': 'Should specify MTD for ITSA income thresholds',
                    'suggestion': '£50,000+ from April 2026; £30,000+ from April 2027'
                })

        # Check for quarterly update requirement
        if 'itsa' in text_lower and 'quarterly' not in text_lower:
            warnings.append({
                'type': 'quarterly_updates_missing',
                'severity': 'medium',
                'message': 'Should mention quarterly update requirement',
                'suggestion': 'MTD for ITSA requires quarterly updates and End of Period Statement'
            })

        # Check for End of Period Statement (EOPS) mention
        if 'itsa' in text_lower and not re.search(r'end\s+of\s+period\s+statement|eops', text_lower):
            warnings.append({
                'type': 'eops_missing',
                'severity': 'medium',
                'message': 'Should mention End of Period Statement requirement',
                'suggestion': 'EOPS required to finalize income and expenses for the tax year'
            })

        # Validate income threshold applicability
        if business_income is not None:
            current_year = datetime.now().year

            if business_income >= 50000:
                if current_year >= 2026:
                    warnings.append({
                        'type': 'mtd_applicable',
                        'severity': 'high',
                        'message': 'MTD for ITSA applies to this income level',
                        'threshold': '£50,000+',
                        'mandatory_from': 'April 2026'
                    })
            elif business_income >= 30000:
                if current_year >= 2027:
                    warnings.append({
                        'type': 'mtd_applicable',
                        'severity': 'high',
                        'message': 'MTD for ITSA applies to this income level',
                        'threshold': '£30,000+',
                        'mandatory_from': 'April 2027'
                    })

        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'thresholds': {
                'phase1': {'amount': 50000, 'date': '2026-04-06'},
                'phase2': {'amount': 30000, 'date': '2027-04-06'}
            }
        }

    def validate_digital_records_requirement(self, text: str) -> Dict:
        """
        Validate digital records keeping requirements

        Reference: HMRC Notice 700/22, Section 4
        """
        issues = []

        text_lower = text.lower()

        # Check for manual/paper record keeping mentions
        manual_patterns = [
            r'manual\s+record',
            r'paper\s+record',
            r'handwritten\s+record',
            r'physical\s+record.*only'
        ]

        for pattern in manual_patterns:
            if re.search(pattern, text_lower):
                issues.append({
                    'type': 'manual_records_not_compliant',
                    'severity': 'high',
                    'message': 'Manual/paper-only records do not meet MTD requirements',
                    'correction': 'Records must be kept in digital form (spreadsheet, accounting software, etc.)',
                    'legal_reference': 'MTD Regulations 2021, Schedule 1'
                })

        # Required digital record elements
        required_elements = [
            ('business name', r'business\s+name'),
            ('vat registration', r'vat\s+(?:registration\s+)?number'),
            ('transaction details', r'transaction|sale|purchase'),
            ('date and time', r'date|time.*supply'),
            ('vat amount', r'vat\s+(?:amount|charge)')
        ]

        missing_elements = []
        for element, pattern in required_elements:
            if 'digital' in text_lower and 'record' in text_lower:
                if not re.search(pattern, text_lower):
                    missing_elements.append(element)

        if missing_elements and len(missing_elements) >= 3:
            issues.append({
                'type': 'incomplete_digital_records',
                'severity': 'medium',
                'message': f'Digital records specification incomplete. Missing: {", ".join(missing_elements)}',
                'legal_reference': 'HMRC Notice 700/22, Section 4.3'
            })

        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }

    def validate_digital_links(self, text: str) -> Dict:
        """
        Validate digital links requirements

        Digital link: Transfer of data without manual intervention
        Reference: HMRC Notice 700/22, Section 5
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for manual intervention in data transfer
        manual_intervention_patterns = [
            r'manual(?:ly)?\s+(?:enter|input|type)',
            r'copy\s+and\s+paste',
            r'rekey',
            r're-enter.*data'
        ]

        for pattern in manual_intervention_patterns:
            if re.search(pattern, text_lower) and 'digital' in text_lower:
                issues.append({
                    'type': 'manual_intervention_not_compliant',
                    'severity': 'high',
                    'message': 'Digital links must not require manual intervention',
                    'correction': 'Data must transfer electronically between software products',
                    'legal_reference': 'HMRC Notice 700/22, Section 5.2'
                })
                break

        # Acceptable digital link methods
        acceptable_methods = [
            'api',
            'xml import',
            'csv import',
            'automated transfer',
            'direct integration'
        ]

        has_acceptable_method = any(method in text_lower for method in acceptable_methods)

        if 'digital link' in text_lower and not has_acceptable_method:
            warnings.append({
                'type': 'digital_link_method_unclear',
                'severity': 'medium',
                'message': 'Should specify digital link method',
                'suggestion': 'Acceptable: API, XML/CSV import, automated transfer, direct integration'
            })

        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_software_compatibility(self, text: str) -> Dict:
        """
        Validate MTD-compatible software requirements

        Reference: HMRC Notice 700/22, Section 3
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for HMRC recognition mention
        if 'software' in text_lower and 'mtd' in text_lower:
            if not re.search(r'hmrc[-\s](?:recognised|recognized|compatible|approved)', text_lower):
                warnings.append({
                    'type': 'software_recognition_unclear',
                    'severity': 'medium',
                    'message': 'Should specify software must be HMRC-recognized',
                    'suggestion': 'Only use software listed on HMRC\'s compatible software list'
                })

        # Check for bridging software option
        if 'spreadsheet' in text_lower and 'mtd' in text_lower:
            if 'bridging' not in text_lower:
                warnings.append({
                    'type': 'bridging_software_not_mentioned',
                    'severity': 'low',
                    'message': 'Consider mentioning bridging software option',
                    'suggestion': 'Bridging software can connect spreadsheets to HMRC\'s MTD API'
                })

        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_mtd_check(
        self,
        text: str,
        vat_registered: bool = True,
        business_income: Optional[float] = None
    ) -> Dict:
        """
        Run comprehensive MTD compliance check
        """
        results = {
            'vat_mtd': self.validate_vat_mtd_compliance(text, vat_registered),
            'itsa_mtd': self.validate_itsa_mtd_compliance(text, business_income),
            'digital_records': self.validate_digital_records_requirement(text),
            'digital_links': self.validate_digital_links(text),
            'software': self.validate_software_compatibility(text)
        }

        all_issues = []
        all_warnings = []

        for check_name, check_result in results.items():
            if 'issues' in check_result:
                all_issues.extend(check_result['issues'])
            if 'warnings' in check_result:
                all_warnings.extend(check_result['warnings'])

        return {
            'overall_compliant': len(all_issues) == 0,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings),
            'detailed_results': results,
            'all_issues': all_issues,
            'all_warnings': all_warnings,
            'legal_source': self.legal_source
        }
