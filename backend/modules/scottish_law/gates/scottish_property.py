"""
Scottish Property Law Compliance Gate

Checks for Scotland-specific property law differences:
- Scots property law vs English land law
- Leases and tenancies differences
- Land registration (Registers of Scotland vs Land Registry)
- Residential tenancy legislation
"""

import re


class ScottishPropertyGate:
    def __init__(self):
        self.name = "scottish_property"
        self.severity = "high"
        self.legal_source = "Land Registration etc. (Scotland) Act 2012; Private Housing (Tenancies) (Scotland) Act 2016; Leases Act 1449"

    def _is_relevant(self, text):
        """Check if document relates to Scottish property"""
        text_lower = (text or '').lower()
        is_scottish = any([
            'scotland' in text_lower,
            'scottish' in text_lower,
            'scots law' in text_lower,
            re.search(r'governed\s+by.*scots?\s+law', text_lower)
        ])
        is_property = any([
            'property' in text_lower,
            'lease' in text_lower,
            'tenancy' in text_lower,
            'landlord' in text_lower,
            'tenant' in text_lower,
            'land' in text_lower,
            'heritable' in text_lower,
            'freehold' in text_lower,
            'leasehold' in text_lower,
            'conveyance' in text_lower,
            'title' in text_lower
        ])
        return is_scottish and is_property

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not relate to Scottish property law'
            }

        issues = []
        corrections = []

        # 1. Check for "freehold" terminology (not used in Scotland)
        if re.search(r'\bfreehold\b', text, re.IGNORECASE):
            issues.append("English 'freehold' terminology used in Scottish property context")
            corrections.append({
                'type': 'property_terminology',
                'suggestion': 'Scotland does not use "freehold" - use "heritable property" or "ownership"',
                'correction': 'Replace "freehold" with "heritable property" or "outright ownership"',
                'citation': 'Scots property law - no freehold/leasehold distinction'
            })

        # 2. Check for "leasehold" terminology
        if re.search(r'\bleasehold\b', text, re.IGNORECASE):
            issues.append("English 'leasehold' terminology used in Scottish property context")
            corrections.append({
                'type': 'leasehold_terminology',
                'suggestion': 'Scotland does not use "leasehold" in the same way as England - use "lease" or "leasehold interest"',
                'correction': 'Replace "leasehold" with "lease" or describe the specific property interest',
                'citation': 'Scots property law - different lease concepts'
            })

        # 3. Check for Land Registry references (should be Registers of Scotland)
        if re.search(r'Land\s+Registry|HM\s+Land\s+Registry|HMLR', text, re.IGNORECASE):
            issues.append("English Land Registry referenced instead of Registers of Scotland")
            corrections.append({
                'type': 'land_registry',
                'suggestion': 'Scotland uses Registers of Scotland (RoS), not HM Land Registry',
                'correction': 'Replace "Land Registry" or "HM Land Registry" with "Registers of Scotland" or "RoS"',
                'citation': 'Land Registration etc. (Scotland) Act 2012; Registers of Scotland'
            })

        # 4. Check for Assured Shorthold Tenancy (AST) - English concept
        if re.search(r'Assured\s+Shorthold\s+Tenancy|AST', text, re.IGNORECASE):
            issues.append("English Assured Shorthold Tenancy (AST) referenced in Scottish context")
            corrections.append({
                'type': 'tenancy_type',
                'suggestion': 'Scotland does not have ASTs - use Private Residential Tenancy (PRT) for tenancies started after 1 December 2017',
                'correction': 'Replace "Assured Shorthold Tenancy" with "Private Residential Tenancy" (PRT)',
                'citation': 'Private Housing (Tenancies) (Scotland) Act 2016'
            })

        # 5. Check for Private Residential Tenancy references
        residential_tenancy = re.search(r'residential\s+tenanc(?:y|ies)', text, re.IGNORECASE)
        prt_mentioned = re.search(r'Private\s+Residential\s+Tenancy|PRT', text, re.IGNORECASE)

        if residential_tenancy and not prt_mentioned:
            corrections.append({
                'type': 'prt_reference',
                'suggestion': 'Most Scottish residential tenancies started after 1 Dec 2017 are Private Residential Tenancies (PRTs)',
                'citation': 'Private Housing (Tenancies) (Scotland) Act 2016'
            })

        # 6. Check for Section 21 eviction references (English only)
        if re.search(r'Section\s+21|s\.?\s*21|s21', text, re.IGNORECASE):
            context = re.search(r'(?:Housing\s+Act|evict|notice|possess)', text, re.IGNORECASE)
            if context:
                issues.append("Section 21 eviction (English law) referenced in Scottish context")
                corrections.append({
                    'type': 'eviction_procedure',
                    'suggestion': 'Scotland does not have Section 21 "no-fault" evictions - landlords must use statutory grounds under PRT',
                    'correction': 'Reference the 18 grounds for eviction under the Private Housing (Tenancies) (Scotland) Act 2016',
                    'citation': 'Private Housing (Tenancies) (Scotland) Act 2016 - no Section 21 equivalent'
                })

        # 7. Check for deposit protection schemes
        deposit_mentioned = re.search(r'deposit.*(?:protection|scheme)|tenancy\s+deposit', text, re.IGNORECASE)
        scottish_schemes = re.search(r'(?:SafeDeposits\s+Scotland|Letting\s+Protection\s+Service\s+Scotland|MyDeposits\s+Scotland)', text, re.IGNORECASE)

        if deposit_mentioned and not scottish_schemes:
            corrections.append({
                'type': 'deposit_protection',
                'suggestion': 'Scottish landlords must use approved Scottish tenancy deposit schemes: SafeDeposits Scotland, Letting Protection Service Scotland, or MyDeposits Scotland',
                'citation': 'Tenancy Deposit Schemes (Scotland) Regulations 2011'
            })

        # 8. Check for First-tier Tribunal references
        tribunal_mentioned = re.search(r'tribunal|dispute\s+resolution', text, re.IGNORECASE)
        scottish_tribunal = re.search(r'First-tier\s+Tribunal\s+for\s+Scotland|Housing\s+and\s+Property\s+Chamber', text, re.IGNORECASE)

        if tribunal_mentioned and not scottish_tribunal:
            corrections.append({
                'type': 'tribunal_reference',
                'suggestion': 'Scottish housing disputes are handled by the First-tier Tribunal for Scotland (Housing and Property Chamber)',
                'citation': 'Tribunals (Scotland) Act 2014'
            })

        # 9. Check for "conveyancing" and missives
        if re.search(r'conveyance|conveyancing', text, re.IGNORECASE):
            if not re.search(r'missives', text, re.IGNORECASE):
                corrections.append({
                    'type': 'conveyancing_process',
                    'suggestion': 'Scottish property conveyancing uses "missives" (exchange of letters forming the contract)',
                    'citation': 'Scots property law - missives process'
                })

        # 10. Check for "exchange of contracts"
        if re.search(r'exchange\s+of\s+contracts', text, re.IGNORECASE):
            issues.append("English 'exchange of contracts' terminology used in Scottish context")
            corrections.append({
                'type': 'contract_exchange',
                'suggestion': 'Scotland uses "conclusion of missives" not "exchange of contracts"',
                'correction': 'Replace "exchange of contracts" with "conclusion of missives"',
                'citation': 'Scots conveyancing law - missives conclude the bargain'
            })

        # 11. Check for Right to Buy references
        if re.search(r'Right\s+to\s+Buy', text, re.IGNORECASE):
            corrections.append({
                'type': 'right_to_buy',
                'suggestion': 'Right to Buy was abolished in Scotland from 1 August 2016 (ended earlier than in England)',
                'citation': 'Housing (Scotland) Act 2014 - Right to Buy abolished'
            })

        # 12. Check for leasehold reform references
        if re.search(r'leasehold\s+reform|commonhold', text, re.IGNORECASE):
            corrections.append({
                'type': 'leasehold_reform',
                'suggestion': 'English leasehold reform and commonhold do not apply in Scotland - Scotland has different property ownership structures',
                'citation': 'Scots property law - no English leasehold/commonhold system'
            })

        # 13. Check for "gazumping" references
        if re.search(r'gazump(?:ing)?', text, re.IGNORECASE):
            corrections.append({
                'type': 'gazumping',
                'suggestion': 'Gazumping is much rarer in Scotland due to binding missives concluded earlier in the process',
                'citation': 'Scots conveyancing - missives create binding contract'
            })

        # 14. Check for Home Report requirements
        if re.search(r'(?:selling|sale\s+of).*(?:property|house|flat)', text, re.IGNORECASE):
            if not re.search(r'Home\s+Report', text, re.IGNORECASE):
                corrections.append({
                    'type': 'home_report',
                    'suggestion': 'Scottish residential property sellers must provide a Home Report before marketing (not required in England)',
                    'citation': 'Housing (Scotland) Act 2006, Part 3'
                })

        # 15. Check for commercial lease references
        commercial_lease = re.search(r'commercial\s+(?:lease|property|letting)', text, re.IGNORECASE)
        if commercial_lease:
            corrections.append({
                'type': 'commercial_lease_scots',
                'suggestion': 'Scottish commercial leases follow different rules - check Land Registration etc. (Scotland) Act 2012 for leases over 20 years',
                'citation': 'Land Registration etc. (Scotland) Act 2012; Scots commercial lease law'
            })

        # Compile final result
        if issues:
            return {
                'status': 'FAIL',
                'severity': self.severity,
                'message': f"Scottish property law issues detected: {'; '.join(issues)}",
                'legal_source': self.legal_source,
                'corrections': corrections,
                'issues': issues
            }
        elif corrections:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Scottish property law guidance applicable',
                'legal_source': self.legal_source,
                'corrections': corrections
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Scottish property law compliance checks passed',
            'legal_source': self.legal_source
        }


# Test cases
TEST_CASES = [
    {
        'name': 'Freehold property in Scotland',
        'text': 'This freehold property in Scotland is registered with the Land Registry.',
        'expected_status': 'FAIL',
        'expected_issues': ['freehold terminology', 'Land Registry']
    },
    {
        'name': 'English AST in Scottish context',
        'text': 'This Assured Shorthold Tenancy is for a property in Edinburgh, Scotland.',
        'expected_status': 'FAIL',
        'expected_issues': ['Assured Shorthold Tenancy']
    },
    {
        'name': 'Section 21 eviction in Scotland',
        'text': 'The Scottish landlord issued a Section 21 notice to evict the tenant.',
        'expected_status': 'FAIL',
        'expected_issues': ['Section 21 eviction']
    },
    {
        'name': 'Correct Scottish property terminology',
        'text': 'This heritable property in Scotland is registered with Registers of Scotland. The Private Residential Tenancy is governed by Scots law.',
        'expected_status': 'PASS'
    },
    {
        'name': 'Exchange of contracts in Scotland',
        'text': 'Upon exchange of contracts, the sale of this Scottish property will be complete.',
        'expected_status': 'FAIL',
        'expected_issues': ['exchange of contracts']
    },
    {
        'name': 'Scottish residential sale without Home Report',
        'text': 'Selling residential property in Scotland under Scots law.',
        'expected_status': 'WARNING',
        'expected_corrections': ['home report']
    }
]
