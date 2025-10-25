"""Domain templates and full gate taxonomy for the universal synthesis system."""
from __future__ import annotations

from typing import Any, Dict, Optional


def gate_config(
    *,
    domain: str,
    variant: Optional[str],
    severity: str,
    legal: str,
    insertion: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        'domain': domain,
        'variant': variant,
        'severity': severity,
        'legal_citation': legal,
        'insertion_point': insertion,
        'context': context,
    }


DOMAIN_TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    'risk_warning': {
        'financial_promotion': {
            'template': """IMPORTANT RISK WARNING:\n\n{risk_detail}\n\nThe value of investments and any income from them can fall as well as rise. You may not get back the amount invested. Past performance is not a reliable indicator of future results.""",
            'default_context': {
                'section_header': 'IMPORTANT RISK WARNING',
                'risk_detail': 'Capital is at risk. Review product suitability before proceeding.',
            },
        },
        'risk_balance': {
            'template': """RISK-BENEFIT BALANCE:\n\n{risk_detail}\n\nEnsure benefits and risks appear with equal prominence across communications.""",
            'default_context': {
                'section_header': 'RISK-BENEFIT BALANCE',
                'risk_detail': 'Pair projected benefits with plain-language risks, fees, and conditions.',
            },
        },
        'client_assets': {
            'template': """CLIENT ASSET SAFEGUARDS:\n\n{risk_detail}\n\nClient money must remain in segregated accounts with daily reconciliation and clear disclosures of protection limits.""",
            'default_context': {
                'section_header': 'CLIENT ASSET SAFEGUARDS',
                'risk_detail': 'Explain CASS protections, residual risks, and FSCS coverage.',
            },
        },
        'tax_exposure': {
            'template': """TAX RISK WARNING:\n\n{risk_detail}\n\nTax treatment depends on personal circumstances and can change.""",
            'default_context': {
                'section_header': 'TAX RISK WARNING',
                'risk_detail': 'Confirm customers remain responsible for their tax liabilities and should consult HMRC guidance.',
            },
        },
        'data_processing': {
            'template': """DATA PROCESSING WARNING:\n\n{risk_detail}\n\nWe handle personal information under strict controls. Individuals retain all rights afforded by data protection law.""",
            'default_context': {
                'section_header': 'DATA PROCESSING WARNING',
                'risk_detail': 'Summarise how personal data is protected and offer contact routes for questions.',
            },
        },
    },
    'disclosure': {
        'fos_contact': {
            'template': """FINANCIAL OMBUDSMAN SERVICE:\n\n{body_text}\n\nYou may contact the Financial Ombudsman Service via {contact_details}.""",
            'default_context': {
                'section_header': 'FINANCIAL OMBUDSMAN SERVICE',
                'body_text': 'If you remain dissatisfied after our final response you can escalate your complaint within six months.',
                'contact_details': '0800 023 4567 or financial-ombudsman.org.uk',
            },
        },
        'promotion_approval': {
            'template': """FINANCIAL PROMOTION APPROVAL:\n\n{body_text}\n\nApproved by [FIRM NAME] (FCA FRN [FRN_NUMBER]). Queries: {contact_details}.""",
            'default_context': {
                'section_header': 'FINANCIAL PROMOTION APPROVAL',
                'body_text': 'This financial promotion has been signed off by an FCA-authorised approver in accordance with FSMA s21.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'conflicts': {
            'template': """CONFLICTS OF INTEREST:\n\n{body_text}\n\nFor more information contact {contact_details}.""",
            'default_context': {
                'section_header': 'CONFLICTS OF INTEREST',
                'body_text': 'We disclose conflicts, ownership links, and mitigation steps so customers can make informed choices.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'inducements': {
            'template': """INDUCEMENTS & REFERRALS:\n\n{body_text}\n\nFurther details are available from {contact_details}.""",
            'default_context': {
                'section_header': 'INDUCEMENTS & REFERRALS',
                'body_text': 'We explain referral fees or commissions, identify payers, and confirm charges do not increase for customers.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'client_money': {
            'template': """CLIENT MONEY DISCLOSURE:\n\n{body_text}\n\nQuestions can be directed to {contact_details}.""",
            'default_context': {
                'section_header': 'CLIENT MONEY',
                'body_text': 'Client money is held in segregated trust accounts with daily reconciliation. We explain protections and residual risks.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'third_party_banks': {
            'template': """THIRD-PARTY BANKING ARRANGEMENTS:\n\n{body_text}\n\nContact {contact_details} for due diligence information.""",
            'default_context': {
                'section_header': 'THIRD-PARTY BANKING',
                'body_text': 'We assess, monitor, and diversify third-party banks holding client assets, documenting reviews and contingency plans.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'third_party_sharing': {
            'template': """THIRD-PARTY DATA SHARING:\n\n{body_text}\n\nFull partner information is available on request via {contact_details}.""",
            'default_context': {
                'section_header': 'THIRD-PARTY DATA SHARING',
                'body_text': 'Personal data is shared only with contracted processors or partners acting on our instructions under UK GDPR-compliant safeguards.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'no_advice': {
            'template': """INFORMATION ONLY – NO PERSONAL ADVICE:\n\n{body_text}\n\nSeek FCA-authorised advice if unsure about suitability.""",
            'default_context': {
                'section_header': 'NO PERSONAL ADVICE',
                'body_text': 'This communication provides general information only and should not be treated as a personal recommendation.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'data_controller': {
            'template': """DATA CONTROLLER:\n\n{body_text}\n\nFurther privacy information is available at {contact_details}.""",
            'default_context': {
                'section_header': 'DATA CONTROLLER',
                'body_text': '[FIRM NAME] is the data controller responsible for personal data described in this notice.',
                'contact_details': '[URL]',
            },
        },
        'dpo_contact': {
            'template': """DATA PROTECTION OFFICER:\n\n{body_text}\n\nContact: {contact_details}.""",
            'default_context': {
                'section_header': 'DATA PROTECTION OFFICER',
                'body_text': 'Reach our DPO for privacy queries or to exercise data rights.',
                'contact_details': 'dpo@[FIRM_DOMAIN]',
            },
        },
        'international_transfer': {
            'template': """INTERNATIONAL DATA TRANSFERS:\n\n{body_text}\n\nContact {contact_details} for safeguard documentation.""",
            'default_context': {
                'section_header': 'INTERNATIONAL DATA TRANSFERS',
                'body_text': 'When data leaves the UK we rely on adequacy regulations, IDTAs, or Standard Contractual Clauses and assess partner controls.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'gdpr_rights_contact': {
            'template': """DATA SUBJECT RIGHTS:\n\n{body_text}\n\nSubmit requests via {contact_details}.""",
            'default_context': {
                'section_header': 'DATA SUBJECT RIGHTS',
                'body_text': 'Explain how to request access, rectification, erasure, restriction, objection, portability, and how to complain to the ICO.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'nda_governing_law': {
            'template': """GOVERNING LAW & JURISDICTION:\n\n{body_text}\n\nDisputes fall under the exclusive jurisdiction stated above.""",
            'default_context': {
                'section_header': 'GOVERNING LAW',
                'body_text': 'This agreement is governed by the laws of [JURISDICTION] and parties submit to those courts.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'nda_parties': {
            'template': """PARTIES TO THIS AGREEMENT:\n\n{body_text}\n\nFor queries contact {contact_details}.""",
            'default_context': {
                'section_header': 'PARTIES TO THIS AGREEMENT',
                'body_text': '(1) [PARTY_ONE_NAME] and (2) [PARTY_TWO_NAME] including permitted affiliates enter into this agreement.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'tax_registration': {
            'template': """BUSINESS & TAX REGISTRATION:\n\n{body_text}\n\nHMRC contact: {contact_details}.""",
            'default_context': {
                'section_header': 'BUSINESS & TAX REGISTRATION',
                'body_text': '[COMPANY_NAME] is registered under company number [COMPANY_NUMBER] and VAT number [VAT_NUMBER]. Include these details on all invoices.',
                'contact_details': 'hmrc.gov.uk or 0300 200 3700',
            },
        },
        'hr_contact': {
            'template': """HR CONTACT DETAILS:\n\n{body_text}\n\nEnquiries: {contact_details}.""",
            'default_context': {
                'section_header': 'HR CONTACT',
                'body_text': 'Contact HR if you require adjustments, clarification, or additional support before the meeting.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
    },
    'procedure': {
        'complaints_clock': {
            'template': """COMPLAINT HANDLING PROCEDURE:\n\n{procedure_text}\n\nIf unresolved you may escalate to the Financial Ombudsman Service within six months.""",
            'default_context': {
                'section_header': 'COMPLAINT HANDLING',
                'procedure_text': 'We acknowledge complaints promptly, investigate fairly, and issue a final response within eight weeks, keeping customers informed throughout.',
            },
        },
        'support_journey': {
            'template': """CUSTOMER SUPPORT JOURNEY:\n\n{procedure_text}\n\nSupport channels remain as accessible as onboarding routes.""",
            'default_context': {
                'section_header': 'CUSTOMER SUPPORT',
                'procedure_text': 'Customers can reach us via phone, email, live chat, and accessible pathways with fast escalation for cancellations or redress.',
            },
        },
        'distribution_controls': {
            'template': """DISTRIBUTION CONTROLS:\n\n{procedure_text}\n\nWe monitor intermediaries and halt out-of-scope distribution.""",
            'default_context': {
                'section_header': 'DISTRIBUTION CONTROLS',
                'procedure_text': 'We brief distributors, share negative target market indicators, and review MI to ensure promotions reach suitable customers only.',
            },
        },
        'vulnerable_customers': {
            'template': """VULNERABLE CUSTOMER SUPPORT:\n\n{procedure_text}\n\nStaff receive training and tools to deliver appropriate adjustments.""",
            'default_context': {
                'section_header': 'VULNERABLE CUSTOMERS',
                'procedure_text': 'We proactively identify vulnerability indicators, capture customer needs, and tailor communication or products accordingly.',
            },
        },
        'reasonable_adjustments': {
            'template': """REASONABLE ADJUSTMENTS:\n\n{procedure_text}\n\nContact {contact_details} to request additional support.""",
            'default_context': {
                'section_header': 'REASONABLE ADJUSTMENTS',
                'procedure_text': 'We offer alternative formats, flexible scheduling, and accessible meeting options so no customer is disadvantaged.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'personal_dealing': {
            'template': """PERSONAL DEALING CONTROLS:\n\n{procedure_text}\n\nEmployees must pre-clear restricted trades and report holdings.""",
            'default_context': {
                'section_header': 'PERSONAL DEALING',
                'procedure_text': 'We operate pre-trade approval, restricted lists, and periodic attestations to prevent conflicts.',
            },
        },
        'record_keeping': {
            'template': """RECORD KEEPING:\n\n{procedure_text}\n\nRecords are retained for statutory periods and audited regularly.""",
            'default_context': {
                'section_header': 'RECORD KEEPING',
                'procedure_text': 'We maintain approvals, communications, MI, and training logs for at least [RETENTION_PERIOD] in secure systems.',
            },
        },
        'return_destruction': {
            'template': """RETURN OR DESTRUCTION OF MATERIALS:\n\n{procedure_text}\n\nConfirm completion to {contact_details}.""",
            'default_context': {
                'section_header': 'RETURN OR DESTRUCTION',
                'procedure_text': 'Upon request we promptly return or securely destroy confidential information, retaining copies only where legally required.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'investigation': {
            'template': """INVESTIGATION PROCEDURE:\n\n{procedure_text}\n\nFindings are shared before any disciplinary decision.""",
            'default_context': {
                'section_header': 'INVESTIGATION',
                'procedure_text': 'An impartial investigator gathers evidence, interviews witnesses, and discloses relevant materials to those involved.',
            },
        },
        'appeal': {
            'template': """APPEAL PROCESS:\n\n{procedure_text}\n\nSubmit appeals to {contact_details} within the stated timeframe.""",
            'default_context': {
                'section_header': 'APPEAL RIGHTS',
                'procedure_text': 'You may appeal in writing, outlining the grounds. A manager not previously involved will review the decision.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'disciplinary': {
            'template': """DISCIPLINARY PROCEDURE:\n\n{procedure_text}\n\nWe adhere to the ACAS Code at every stage.""",
            'default_context': {
                'section_header': 'DISCIPLINARY PROCEDURE',
                'procedure_text': 'We give reasonable notice, allow accompaniment, consider mitigation, and confirm outcomes in writing.',
            },
        },
        'suspension': {
            'template': """SUSPENSION GUIDANCE:\n\n{procedure_text}\n\nSuspension is reviewed regularly and is not a sanction.""",
            'default_context': {
                'section_header': 'SUSPENSION',
                'procedure_text': 'Where suspension is necessary it is on full pay, kept under review, and confirmed in writing with reasons.',
            },
        },
        'timeframes': {
            'template': """TIMEFRAMES & DEADLINES:\n\n{procedure_text}\n\nWe communicate any extensions promptly.""",
            'default_context': {
                'section_header': 'TIMEFRAMES',
                'procedure_text': 'We advise preparation time, hearing dates, and response deadlines clearly, typically allowing at least five working days.',
            },
        },
        'witness_statements': {
            'template': """WITNESS STATEMENTS:\n\n{procedure_text}\n\nWe provide summaries while protecting confidentiality.""",
            'default_context': {
                'section_header': 'WITNESS STATEMENTS',
                'procedure_text': 'Statements are gathered impartially and shared so employees can meaningfully respond.',
            },
        },
        'breach_notification': {
            'template': """DATA BREACH RESPONSE:\n\n{procedure_text}\n\nContact {contact_details} immediately if you suspect a breach.""",
            'default_context': {
                'section_header': 'DATA BREACH RESPONSE',
                'procedure_text': 'We triage incidents, notify the ICO within 72 hours when required, inform affected individuals promptly, and document remediation.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        },
        'cookies_process': {
            'template': """COOKIES & TRACKING:\n\n{procedure_text}\n\nManage preferences via {contact_details}.""",
            'default_context': {
                'section_header': 'COOKIES & TRACKING',
                'procedure_text': 'We record consent preferences, provide granular controls, and refresh logs regularly for audit.',
                'contact_details': '[URL]',
            },
        },
    },
    'definition': {
        'consumer_duty_outcomes': {
            'template': """CONSUMER DUTY OUTCOMES:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONSUMER DUTY OUTCOMES',
                'definition_text': 'We evidence good outcomes for products and services, price and value, customer understanding, and customer support.',
            },
        },
        'consumer_duty_principles': {
            'template': """CONSUMER DUTY – CROSS-CUTTING RULES:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONSUMER DUTY – CROSS-CUTTING RULES',
                'definition_text': 'We act in good faith, avoid foreseeable harm, and support customers to pursue their objectives.',
            },
        },
        'fair_value': {
            'template': """FAIR VALUE STATEMENT:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'FAIR VALUE STATEMENT',
                'definition_text': 'We assess charges, benefits, and distribution arrangements to confirm fair value and document board oversight.',
            },
        },
        'comprehension_support': {
            'template': """COMPREHENSION SUPPORT:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'COMPREHENSION SUPPORT',
                'definition_text': 'Communications use layered explanations, call-outs for key risks, and accessible language.',
            },
        },
        'target_market': {
            'template': """TARGET MARKET DEFINITION:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'TARGET MARKET',
                'definition_text': 'Define who the product is designed for, the negative target market, and indicators of suitability.',
            },
        },
        'product_scope': {
            'template': """PRODUCT & SERVICE SCOPE:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'PRODUCT SCOPE',
                'definition_text': 'Describe what is included, key exclusions, and scenarios where the product may not be appropriate.',
            },
        },
        'data_purpose': {
            'template': """PURPOSE LIMITATION:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'PURPOSE LIMITATION',
                'definition_text': 'We use personal data only for explicit purposes such as onboarding, servicing, compliance, and analytics consistent with privacy notices.',
            },
        },
        'data_retention': {
            'template': """RETENTION PERIODS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'RETENTION PERIODS',
                'definition_text': 'Retention schedules list how long each record type is kept (e.g., six years for regulatory records) before secure deletion or anonymisation.',
            },
        },
        'lawful_basis': {
            'template': """LAWFUL BASIS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'LAWFUL BASIS',
                'definition_text': 'We identify the lawful basis for each processing activity (contract, legal obligation, legitimate interests, consent, or vital interests) and record the rationale.',
            },
        },
        'data_rights': {
            'template': """DATA SUBJECT RIGHTS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'DATA SUBJECT RIGHTS',
                'definition_text': 'Explain how individuals can exercise access, rectification, erasure, restriction, objection, and portability rights, and contact the ICO.',
            },
        },
        'security_measures': {
            'template': """SECURITY MEASURES:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'SECURITY MEASURES',
                'definition_text': 'Summarise encryption, access controls, testing, supplier oversight, and incident response processes.',
            },
        },
        'automated_decisions': {
            'template': """AUTOMATED DECISIONS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'AUTOMATED DECISIONS',
                'definition_text': 'If automated decisions produce legal or significant effects we explain the logic, consequences, and offer human review.',
            },
        },
        'children_data': {
            'template': """CHILDREN'S DATA:\n\n{definition_text}""",
            'default_context': {
                'section_header': "CHILDREN'S DATA",
                'definition_text': 'We verify age, collect parental consent where required, and tailor content for under-18 users.',
            },
        },
        'data_minimisation': {
            'template': """DATA MINIMISATION:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'DATA MINIMISATION',
                'definition_text': 'Collect only data that is necessary for declared purposes and periodically review forms to remove excess fields.',
            },
        },
        'consent_definition': {
            'template': """CONSENT STANDARD:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONSENT STANDARD',
                'definition_text': 'Consent must be freely given, specific, informed, unambiguous, and recorded via affirmative action.',
            },
        },
        'nda_confidential_information': {
            'template': """CONFIDENTIAL INFORMATION:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONFIDENTIAL INFORMATION',
                'definition_text': 'Define confidential information to include non-public technical, commercial, and strategic data shared or created under the agreement.',
            },
        },
        'nda_purpose': {
            'template': """PERMITTED PURPOSE:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'PERMITTED PURPOSE',
                'definition_text': 'Information may only be used to evaluate or deliver the defined project and requires written consent for any other use.',
            },
        },
        'nda_duration': {
            'template': """DURATION OF OBLIGATIONS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'DURATION OF OBLIGATIONS',
                'definition_text': 'Confidentiality obligations last for an agreed period (for example, two to five years) and survive termination as needed to protect legitimate interests.',
            },
        },
        'nda_consideration': {
            'template': """CONSIDERATION:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONSIDERATION',
                'definition_text': 'Each party acknowledges receipt of sufficient consideration such as mutual disclosures or another item of value supporting the agreement.',
            },
        },
        'nda_exclusions': {
            'template': """STANDARD EXCLUSIONS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'STANDARD EXCLUSIONS',
                'definition_text': 'Obligations do not apply to information already public, lawfully known, independently developed, or required to be disclosed by law.',
            },
        },
        'tax_invoice': {
            'template': """VAT INVOICE CONTENT:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'VAT INVOICE CONTENT',
                'definition_text': 'Invoices must include a unique number, issue date, supplier and customer details, VAT number, description, net amount, VAT amount, and total.',
            },
        },
        'vat_threshold': {
            'template': """VAT REGISTRATION THRESHOLD:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'VAT THRESHOLD',
                'definition_text': 'Monitor rolling taxable turnover against the current registration threshold and notify HMRC immediately when exceeded.',
            },
        },
        'hr_allegations': {
            'template': """ALLEGATIONS SUMMARY:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'ALLEGATIONS',
                'definition_text': 'Provide specific allegations with dates, locations, and examples so the employee can prepare a response.',
            },
        },
        'hr_evidence': {
            'template': """EVIDENCE PROVIDED:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'EVIDENCE',
                'definition_text': 'Supply investigation notes, witness statements, and documents relied upon ahead of the meeting.',
            },
        },
        'hr_outcome_reasons': {
            'template': """OUTCOME REASONS:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'OUTCOME REASONS',
                'definition_text': 'Explain the findings, policy references, mitigation considered, and rationale supporting the decision.',
            },
        },
        'hr_consistency': {
            'template': """CONSISTENT TREATMENT:\n\n{definition_text}""",
            'default_context': {
                'section_header': 'CONSISTENCY',
                'definition_text': 'Comparable cases are treated consistently and outcomes benchmarked to avoid unfair or discriminatory impacts.',
            },
        },
    },
    'consent': {
        'gdpr_consent': {
            'template': """CONSENT & PREFERENCES:\n\n{consent_language}""",
            'default_context': {
                'section_header': 'CONSENT & PREFERENCES',
                'consent_language': 'Obtain granular opt-in consent for optional processing (marketing, analytics, special category data) and log the decision.',
            },
        },
        'withdrawal': {
            'template': """WITHDRAWING CONSENT:\n\n{consent_language}""",
            'default_context': {
                'section_header': 'WITHDRAWING CONSENT',
                'consent_language': 'Individuals can withdraw consent at any time without detriment by contacting us or using the preference centre. We action requests promptly.',
            },
        },
        'cookies': {
            'template': """COOKIES CONSENT:\n\n{consent_language}""",
            'default_context': {
                'section_header': 'COOKIES',
                'consent_language': 'Provide opt-in categories for analytics and advertising cookies, log preferences, and allow changes at any time.',
            },
        },
        'children': {
            'template': """CHILD CONSENT:\n\n{consent_language}""",
            'default_context': {
                'section_header': 'CHILD CONSENT',
                'consent_language': 'For users under 13 obtain verifiable parental consent and present age-appropriate explanations of data use.',
            },
        },
    },
    'limitation': {
        'eligibility': {
            'template': """ELIGIBILITY & EXCLUSIONS:\n\n{limitation_text}""",
            'default_context': {
                'section_header': 'ELIGIBILITY',
                'limitation_text': 'State who the product is designed for and exclude segments that should not be targeted (for example, vulnerable or inexperienced investors).',
            },
        },
        'usage_scope': {
            'template': """USAGE LIMITATIONS:\n\n{limitation_text}""",
            'default_context': {
                'section_header': 'USAGE LIMITATIONS',
                'limitation_text': 'Describe acceptable uses, geographic restrictions, and licensing limits to avoid misuse.',
            },
        },
        'nda_exceptions': {
            'template': """DISCLOSURE EXCEPTIONS:\n\n{limitation_text}""",
            'default_context': {
                'section_header': 'DISCLOSURE EXCEPTIONS',
                'limitation_text': 'Permitted disclosures include protected whistleblowing, crime reporting, legal obligations, and communications with professional advisers.',
            },
        },
    },
}

MODULE_TAXONOMY: Dict[str, Dict[str, Dict[str, Any]]] = {
    'fca_uk': {
        'outcomes_coverage': gate_config(
            domain='definition',
            variant='consumer_duty_outcomes',
            severity='critical',
            legal='FCA PRIN 2A (Consumer Duty)',
            insertion='section',
            context={
                'section_header': 'CONSUMER DUTY OUTCOMES',
                'definition_text': 'We evidence good outcomes for products and services, price and value, customer understanding, and customer support with MI reviewed by senior management.',
            },
        ),
        'cross_cutting_rules': gate_config(
            domain='definition',
            variant='consumer_duty_principles',
            severity='critical',
            legal='FCA PRIN 2A.2 (Consumer Duty Cross-Cutting Rules)',
            insertion='section',
            context={
                'section_header': 'CONSUMER DUTY – CROSS-CUTTING',
                'definition_text': 'We act in good faith, avoid foreseeable harm, and empower customers to pursue their financial objectives throughout the lifecycle.',
            },
        ),
        'fair_value': gate_config(
            domain='definition',
            variant='fair_value',
            severity='high',
            legal='FCA PRIN 2A.4 (Price and Value Outcome)',
            insertion='section',
            context={
                'section_header': 'FAIR VALUE STATEMENT',
                'definition_text': 'We benchmark fees, benefits, and distribution arrangements, documenting governance approval of the fair value assessment.',
            },
        ),
        'comprehension_aids': gate_config(
            domain='definition',
            variant='comprehension_support',
            severity='medium',
            legal='FCA PRIN 2A.5 (Consumer Understanding Outcome)',
            insertion='section',
            context={
                'section_header': 'COMPREHENSION SUPPORT',
                'definition_text': 'We use layered disclosures, glossaries, and clear risk warnings to help customers understand complex information before committing.',
            },
        ),
        'support_journey': gate_config(
            domain='procedure',
            variant='support_journey',
            severity='high',
            legal='FCA PRIN 2A.6 (Consumer Support Outcome)',
            insertion='section',
            context={
                'section_header': 'CUSTOMER SUPPORT',
                'procedure_text': 'Support channels (phone, email, chat) are as easy to access as sales journeys, with monitored response times and escalation routes.',
            },
        ),
        'fair_clear_not_misleading': gate_config(
            domain='risk_warning',
            variant='financial_promotion',
            severity='critical',
            legal='FCA COBS 4.2 (Fair, Clear and Not Misleading)',
            insertion='start',
            context={
                'section_header': 'IMPORTANT RISK WARNING',
                'risk_detail': 'Remove guaranteed or risk-free claims. Highlight that capital is at risk, returns may vary, and tax outcomes depend on individual circumstances.',
            },
        ),
        'risk_benefit_balance': gate_config(
            domain='risk_warning',
            variant='risk_balance',
            severity='high',
            legal='FCA COBS 4.2.3 (Risk Warnings Equally Prominent)',
            insertion='section',
            context={
                'section_header': 'RISK-BENEFIT BALANCE',
                'risk_detail': 'Ensure benefit statements share equal prominence with risks, fees, conditions, and downside scenarios.',
            },
        ),
        'target_audience': gate_config(
            domain='limitation',
            variant='eligibility',
            severity='high',
            legal='FCA COBS 4.7 (Direct Offer Financial Promotions)',
            insertion='section',
            context={
                'section_header': 'TARGET AUDIENCE',
                'limitation_text': 'Define the positive target market (knowledge, objectives, risk tolerance) and who should not invest, including vulnerable or ineligible customers.',
            },
        ),
        'finfluencer_controls': gate_config(
            domain='procedure',
            variant='distribution_controls',
            severity='critical',
            legal='FCA Financial Promotions via Social Media & Influencers',
            insertion='section',
            context={
                'section_header': 'FINANCIAL PROMOTER CONTROLS',
                'procedure_text': 'Influencer content is pre-approved, scripted with mandatory disclosures, monitored for compliance, and recorded for audit.',
            },
        ),
        'complaint_route_clock': gate_config(
            domain='procedure',
            variant='complaints_clock',
            severity='critical',
            legal='FCA DISP 1.6 (Complaints Time Limits)',
            insertion='section',
            context={
                'section_header': 'COMPLAINT HANDLING',
                'procedure_text': 'We acknowledge complaints promptly, provide updates, and issue a final response within eight weeks including escalation instructions.',
            },
        ),
        'fos_signposting': gate_config(
            domain='disclosure',
            variant='fos_contact',
            severity='critical',
            legal='FCA DISP 1.6.2 (Financial Ombudsman Service Signposting)',
            insertion='end',
            context={
                'section_header': 'FINANCIAL OMBUDSMAN SERVICE',
                'body_text': 'If you remain dissatisfied after our final response you can refer the complaint to the Financial Ombudsman Service within six months of our letter.',
                'contact_details': '0800 023 4567 or financial-ombudsman.org.uk',
            },
        ),
        'vulnerability_identification': gate_config(
            domain='procedure',
            variant='vulnerable_customers',
            severity='high',
            legal='FCA FG21/1 (Fair Treatment of Vulnerable Customers)',
            insertion='section',
            context={
                'section_header': 'VULNERABLE CUSTOMERS',
                'procedure_text': 'Staff proactively identify vulnerability indicators, record customer needs, and adapt communications or routes accordingly.',
            },
        ),
        'reasonable_adjustments': gate_config(
            domain='procedure',
            variant='reasonable_adjustments',
            severity='medium',
            legal='FCA FG21/1 & Equality Act 2010',
            insertion='section',
            context={
                'section_header': 'REASONABLE ADJUSTMENTS',
                'procedure_text': 'Provide accessible formats, alternative channels, and flexible timeframes on request so customers are not disadvantaged.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'target_market_definition': gate_config(
            domain='definition',
            variant='target_market',
            severity='high',
            legal='FCA PROD 1.4 & PROD 3 (Product Governance - Target Market)',
            insertion='section',
            context={
                'section_header': 'TARGET MARKET',
                'definition_text': 'Detail the positive and negative target market, distribution strategy, and key customer characteristics, refreshing assessments periodically.',
            },
        ),
        'distribution_controls': gate_config(
            domain='procedure',
            variant='distribution_controls',
            severity='medium',
            legal='FCA PROD 4 (Product Governance - Distribution)',
            insertion='section',
            context={
                'section_header': 'DISTRIBUTION CONTROLS',
                'procedure_text': 'Distributors receive product information, negative target market guidance, and monitoring takes place to halt out-of-scope activity.',
            },
        ),
        'fair_value_assessment_ref': gate_config(
            domain='definition',
            variant='fair_value',
            severity='medium',
            legal='FCA PROD 4.2.17 (Fair Value Assessment Reviews)',
            insertion='section',
            context={
                'section_header': 'FAIR VALUE ASSESSMENT',
                'definition_text': 'Summarise the latest fair value review, metrics considered, corresponding actions, and when the next assessment will occur.',
            },
        ),
        'conflicts_declaration': gate_config(
            domain='disclosure',
            variant='conflicts',
            severity='high',
            legal='FCA SYSC 10 (Conflicts of Interest)',
            insertion='section',
            context={
                'section_header': 'CONFLICTS OF INTEREST',
                'body_text': 'We disclose ownership links, remuneration structures, and mitigation steps (segregation, oversight committees, disclosure to customers).',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'inducements_referrals': gate_config(
            domain='disclosure',
            variant='inducements',
            severity='high',
            legal='FCA COBS 2.3 (Inducements)',
            insertion='section',
            context={
                'section_header': 'INDUCEMENTS & REFERRALS',
                'body_text': 'We identify referral payments, payers, and confirm that incentives do not increase customer costs or impair fair treatment.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'personal_dealing': gate_config(
            domain='procedure',
            variant='personal_dealing',
            severity='medium',
            legal='FCA SYSC 10.1.11 (Personal Account Dealing)',
            insertion='section',
            context={
                'section_header': 'PERSONAL DEALING',
                'procedure_text': 'Employees pre-clear trades in restricted instruments, observe blackout periods, and submit periodic attestations with compliance monitoring.',
            },
        ),
        'defined_roles': gate_config(
            domain='definition',
            variant='product_scope',
            severity='medium',
            legal='FCA SYSC 4 & 5 (Senior Management Arrangements)',
            insertion='section',
            context={
                'section_header': 'GOVERNANCE RESPONSIBILITIES',
                'definition_text': 'Senior Managers (including the Consumer Duty Champion) have documented responsibilities with deputies and escalation lines.',
            },
        ),
        'record_keeping': gate_config(
            domain='procedure',
            variant='record_keeping',
            severity='medium',
            legal='FCA SYSC 9 (Record Keeping)',
            insertion='section',
            context={
                'section_header': 'RECORD KEEPING',
                'procedure_text': 'We retain approvals, communications, complaints MI, and training logs for the statutory minimum period in secure, retrievable systems.',
            },
        ),
        'client_money_segregation': gate_config(
            domain='disclosure',
            variant='client_money',
            severity='critical',
            legal='FCA CASS 7 (Client Money Rules)',
            insertion='section',
            context={
                'section_header': 'CLIENT MONEY',
                'body_text': 'Client funds are held in segregated trust accounts with daily reconciliation. We explain protections, FSCS coverage, and residual risks.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'third_party_banks': gate_config(
            domain='disclosure',
            variant='third_party_banks',
            severity='high',
            legal='FCA CASS 7.13 (Selection and Monitoring of Third Party Banks)',
            insertion='section',
            context={
                'section_header': 'THIRD-PARTY BANKING',
                'body_text': 'We select, diversify, and monitor third-party banks holding client money, documenting due diligence and contingency arrangements.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'no_implicit_advice': gate_config(
            domain='disclosure',
            variant='no_advice',
            severity='critical',
            legal='FCA COBS 2.1 & 9 (Suitability and Acting Honestly, Fairly and Professionally)',
            insertion='section',
            context={
                'section_header': 'NO PERSONAL ADVICE',
                'body_text': 'This material is for information only and does not account for personal circumstances. Customers must assess suitability or seek regulated advice.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'promotions_approval': gate_config(
            domain='disclosure',
            variant='promotion_approval',
            severity='critical',
            legal='FCA FSMA s.21 & s.24 (Financial Promotion Approval)',
            insertion='end',
            context={
                'section_header': 'FINANCIAL PROMOTION APPROVAL',
                'body_text': 'This promotion has been approved by [FIRM NAME] (FCA FRN [FRN_NUMBER]) or another FCA-authorised approver. Approval artefacts are retained for audit.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
    },
    'gdpr_uk': {
        'consent': gate_config(
            domain='consent',
            variant='gdpr_consent',
            severity='critical',
            legal='GDPR Article 6 & 7',
            insertion='section',
            context={
                'section_header': 'CONSENT & PREFERENCES',
                'consent_language': 'We obtain separate opt-in consent for optional marketing, analytics, and special category data, recording the decision and offering clear information before you consent.',
            },
        ),
        'purpose': gate_config(
            domain='definition',
            variant='data_purpose',
            severity='critical',
            legal='GDPR Article 5(1)(b)',
            insertion='section',
            context={
                'section_header': 'PURPOSE LIMITATION',
                'definition_text': 'We use your personal data only for specified purposes such as onboarding, servicing, compliance, and customer support. Any incompatible reuse requires a new lawful basis.',
            },
        ),
        'retention': gate_config(
            domain='definition',
            variant='data_retention',
            severity='high',
            legal='GDPR Article 5(1)(e)',
            insertion='section',
            context={
                'section_header': 'RETENTION PERIODS',
                'definition_text': 'Retention schedules list how long each record type is held (e.g., six years for regulatory records, two years for marketing consents) before secure deletion or anonymisation.',
            },
        ),
        'rights': gate_config(
            domain='definition',
            variant='data_rights',
            severity='critical',
            legal='GDPR Articles 12-22',
            insertion='section',
            context={
                'section_header': 'DATA SUBJECT RIGHTS',
                'definition_text': 'Explain how individuals can exercise access, rectification, erasure, restriction, objection, and portability rights and how to raise concerns with the ICO.',
            },
        ),
        'security': gate_config(
            domain='definition',
            variant='security_measures',
            severity='high',
            legal='GDPR Article 32',
            insertion='section',
            context={
                'section_header': 'SECURITY MEASURES',
                'definition_text': 'Describe encryption, access controls, supplier oversight, and incident response processes appropriate to the risk of the processing.',
            },
        ),
        'lawful_basis': gate_config(
            domain='definition',
            variant='lawful_basis',
            severity='critical',
            legal='GDPR Article 6',
            insertion='section',
            context={
                'section_header': 'LAWFUL BASIS',
                'definition_text': 'We document the lawful basis for each processing activity (contract, legal obligation, legitimate interests, consent, or vital interests) and explain our reasoning to individuals.',
            },
        ),
        'data_minimisation': gate_config(
            domain='definition',
            variant='data_minimisation',
            severity='medium',
            legal='GDPR Article 5(1)(c)',
            insertion='section',
            context={
                'section_header': 'DATA MINIMISATION',
                'definition_text': 'Collect only data that is necessary for defined purposes and periodically review forms and logs to remove unnecessary data points.',
            },
        ),
        'third_party_sharing': gate_config(
            domain='disclosure',
            variant='third_party_sharing',
            severity='high',
            legal='GDPR Article 13(1)(e)',
            insertion='section',
            context={
                'section_header': 'THIRD-PARTY DATA SHARING',
                'body_text': 'List the categories of processors or partners (hosting, payments, analytics) that receive data under contract and confirm they act only on our instructions.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'international_transfer': gate_config(
            domain='disclosure',
            variant='international_transfer',
            severity='high',
            legal='GDPR Article 44-49',
            insertion='section',
            context={
                'section_header': 'INTERNATIONAL TRANSFERS',
                'body_text': 'When exporting personal data we rely on UK adequacy regulations, the International Data Transfer Agreement, or Standard Contractual Clauses with documented risk assessments.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'automated_decisions': gate_config(
            domain='definition',
            variant='automated_decisions',
            severity='critical',
            legal='GDPR Article 22',
            insertion='section',
            context={
                'section_header': 'AUTOMATED DECISIONS',
                'definition_text': 'If automated decisions have legal or similarly significant effects we explain the logic, potential consequences, and how to request human review.',
            },
        ),
        'children_data': gate_config(
            domain='definition',
            variant='children_data',
            severity='critical',
            legal='GDPR Article 8',
            insertion='section',
            context={
                'section_header': "CHILDREN'S DATA",
                'definition_text': 'We verify age, obtain parental consent where required, and deliver age-appropriate explanations for young users.',
            },
        ),
        'breach_notification': gate_config(
            domain='procedure',
            variant='breach_notification',
            severity='medium',
            legal='GDPR Articles 33-34',
            insertion='section',
            context={
                'section_header': 'DATA BREACH RESPONSE',
                'procedure_text': 'We triage incidents immediately, notify the ICO within 72 hours where required, and inform affected individuals without undue delay.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'dpo_contact': gate_config(
            domain='disclosure',
            variant='dpo_contact',
            severity='high',
            legal='GDPR Article 13(1)(b)',
            insertion='end',
            context={
                'section_header': 'DATA PROTECTION OFFICER',
                'body_text': 'Contact our Data Protection Officer for privacy queries or to exercise your rights.',
                'contact_details': 'dpo@[FIRM_DOMAIN]',
            },
        ),
        'cookies_tracking': gate_config(
            domain='consent',
            variant='cookies',
            severity='medium',
            legal='PECR & GDPR',
            insertion='section',
            context={
                'section_header': 'COOKIES',
                'consent_language': 'We use a consent banner with separate toggles for analytics and advertising cookies, store preferences, and allow changes at any time via [URL].',
            },
        ),
        'withdrawal_consent': gate_config(
            domain='consent',
            variant='withdrawal',
            severity='high',
            legal='GDPR Article 7(3)',
            insertion='section',
            context={
                'section_header': 'WITHDRAWING CONSENT',
                'consent_language': 'You may withdraw consent at any time through the preference centre or by contacting us. We action withdrawals promptly without affecting core services.',
            },
        ),
    },
    'hr_scottish': {
        'informal_threats': gate_config(
            domain='procedure',
            variant='disciplinary',
            severity='critical',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'FORMAL PROCESS',
                'procedure_text': 'Conduct issues are addressed through the formal disciplinary process—managers must not threaten sanctions informally or pre-judge outcomes.',
            },
        ),
        'accompaniment': gate_config(
            domain='procedure',
            variant='disciplinary',
            severity='critical',
            legal='Employment Relations Act 1999, Section 10',
            insertion='section',
            context={
                'section_header': 'RIGHT TO BE ACCOMPANIED',
                'procedure_text': 'You may be accompanied by a trade union representative or work colleague of your choice. Please advise us in advance so arrangements can be made.',
            },
        ),
        'evidence': gate_config(
            domain='definition',
            variant='hr_evidence',
            severity='high',
            legal='ACAS Code of Practice, Paragraph 9',
            insertion='section',
            context={
                'section_header': 'EVIDENCE PROVIDED',
                'definition_text': 'We enclose investigation summaries, witness statements, and relevant documents so you can review the evidence ahead of the meeting.',
            },
        ),
        'appeal': gate_config(
            domain='procedure',
            variant='appeal',
            severity='critical',
            legal='ACAS Code of Practice, Paragraph 21',
            insertion='section',
            context={
                'section_header': 'APPEAL RIGHTS',
                'procedure_text': 'You may appeal in writing within the stated timeframe, outlining your grounds. An impartial manager not previously involved will review the decision.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'allegations': gate_config(
            domain='definition',
            variant='hr_allegations',
            severity='high',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'ALLEGATIONS',
                'definition_text': 'We set out the specific allegations with dates, locations, and examples so you can prepare a full response.',
            },
        ),
        'dismissal': gate_config(
            domain='procedure',
            variant='disciplinary',
            severity='critical',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'DISMISSAL PROCESS',
                'procedure_text': 'Dismissal is considered only after investigation, a fair hearing, and review of mitigation. Outcomes confirm notice or pay in lieu and appeal rights.',
            },
        ),
        'meeting_notice': gate_config(
            domain='procedure',
            variant='timeframes',
            severity='high',
            legal='ACAS Code - Reasonable notice required',
            insertion='section',
            context={
                'section_header': 'MEETING NOTICE',
                'procedure_text': 'We provide reasonable notice (normally at least 48 hours) and supply documents relied upon so you have time to prepare.',
            },
        ),
        'investigation': gate_config(
            domain='procedure',
            variant='investigation',
            severity='high',
            legal='ACAS Code, Paragraph 5',
            insertion='section',
            context={
                'section_header': 'INVESTIGATION',
                'procedure_text': 'An impartial manager gathers evidence, interviews relevant parties, and documents findings before any disciplinary meeting.',
            },
        ),
        'witness_statements': gate_config(
            domain='procedure',
            variant='witness_statements',
            severity='medium',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'WITNESS STATEMENTS',
                'procedure_text': 'Statements are collected impartially and summaries are provided in advance, redacted where necessary for confidentiality.',
            },
        ),
        'meeting_notes': gate_config(
            domain='procedure',
            variant='record_keeping',
            severity='low',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'MEETING NOTES',
                'procedure_text': 'We keep an accurate note of the meeting, share it for comment, and store it securely in accordance with our retention schedule.',
            },
        ),
        'suspension': gate_config(
            domain='procedure',
            variant='suspension',
            severity='high',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'SUSPENSION',
                'procedure_text': 'If suspension is necessary it is on full pay, kept under regular review, and confirmed in writing with reasons.',
            },
        ),
        'previous_warnings': gate_config(
            domain='definition',
            variant='hr_consistency',
            severity='medium',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'PREVIOUS WARNINGS',
                'definition_text': 'We consider only relevant live warnings when deciding the outcome and disregard expired warnings.',
            },
        ),
        'outcome_reasons': gate_config(
            domain='definition',
            variant='hr_outcome_reasons',
            severity='high',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'OUTCOME REASONS',
                'definition_text': 'The decision explains findings, policies breached, mitigation considered, and why the sanction is appropriate.',
            },
        ),
        'representation_choice': gate_config(
            domain='procedure',
            variant='disciplinary',
            severity='medium',
            legal='Employment Relations Act 1999, Section 10',
            insertion='section',
            context={
                'section_header': 'REPRESENTATION',
                'procedure_text': 'You may choose your companion (trade union representative or colleague). We will reschedule where reasonable if they are unavailable.',
            },
        ),
        'timeframes': gate_config(
            domain='procedure',
            variant='timeframes',
            severity='medium',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'TIMEFRAMES',
                'procedure_text': 'We set out preparation time, hearing dates, and response deadlines clearly, advising of any extensions promptly.',
            },
        ),
        'consistency': gate_config(
            domain='definition',
            variant='hr_consistency',
            severity='low',
            legal='ACAS Code of Practice (Disciplinary & Grievance)',
            insertion='section',
            context={
                'section_header': 'CONSISTENT TREATMENT',
                'definition_text': 'Comparable cases are treated consistently. We benchmark outcomes across teams to ensure fairness and avoid discriminatory impact.',
            },
        ),
    },
    'nda_uk': {
        'protected_whistleblowing': gate_config(
            domain='limitation',
            variant='nda_exceptions',
            severity='critical',
            legal='Public Interest Disclosure Act 1998, Section 43J',
            insertion='section',
            context={
                'section_header': 'PROTECTED DISCLOSURES',
                'limitation_text': 'Nothing prevents disclosures protected under the Public Interest Disclosure Act 1998. Individuals may raise concerns with prescribed persons without breaching confidentiality.',
            },
        ),
        'protected_crime_reporting': gate_config(
            domain='limitation',
            variant='nda_exceptions',
            severity='critical',
            legal='Victims and Prisoners Act 2024',
            insertion='section',
            context={
                'section_header': 'CRIME REPORTING',
                'limitation_text': 'The agreement does not restrict reporting suspected criminal conduct to law enforcement or complying with statutory duties.',
            },
        ),
        'protected_harassment': gate_config(
            domain='limitation',
            variant='nda_exceptions',
            severity='critical',
            legal='Equality Act 2010; Employment Rights Bill Clause 22A',
            insertion='section',
            context={
                'section_header': 'HARASSMENT & DISCRIMINATION',
                'limitation_text': 'Individuals may still disclose harassment or discrimination concerns to appropriate authorities or support organisations.',
            },
        ),
        'definition_specificity': gate_config(
            domain='definition',
            variant='nda_confidential_information',
            severity='critical',
            legal='Common Law - Restraint of Trade',
            insertion='section',
            context={
                'section_header': 'CONFIDENTIAL INFORMATION',
                'definition_text': 'Define confidential information to include non-public technical, commercial, financial, and strategic materials shared or generated under this agreement.',
            },
        ),
        'public_domain_exclusion': gate_config(
            domain='definition',
            variant='nda_exclusions',
            severity='high',
            legal='Common Law - Information must have quality of confidence',
            insertion='section',
            context={
                'section_header': 'PUBLIC DOMAIN',
                'definition_text': 'Information already in the public domain without breach, or later made public by a third party lawfully, is excluded from confidentiality obligations.',
            },
        ),
        'prior_knowledge_exclusion': gate_config(
            domain='definition',
            variant='nda_exclusions',
            severity='high',
            legal='Common Law principle of reasonableness',
            insertion='section',
            context={
                'section_header': 'PRIOR KNOWLEDGE',
                'definition_text': 'Information lawfully known to the receiving party prior to disclosure, evidenced in writing, is excluded from confidentiality obligations.',
            },
        ),
        'duration_reasonableness': gate_config(
            domain='definition',
            variant='nda_duration',
            severity='high',
            legal='Common Law - Restraint of Trade',
            insertion='section',
            context={
                'section_header': 'DURATION',
                'definition_text': 'Confidentiality obligations last for a reasonable period (for example, two to five years) proportionate to protecting legitimate commercial interests.',
            },
        ),
        'permitted_disclosures': gate_config(
            domain='limitation',
            variant='nda_exceptions',
            severity='high',
            legal='Common Law; SRA Guidance',
            insertion='section',
            context={
                'section_header': 'PERMITTED DISCLOSURES',
                'limitation_text': 'Disclosures to professional advisers, regulators, or as required by law are permitted when recipients are bound by confidentiality obligations.',
            },
        ),
        'governing_law': gate_config(
            domain='disclosure',
            variant='nda_governing_law',
            severity='critical',
            legal='UK Contract Law',
            insertion='section',
            context={
                'section_header': 'GOVERNING LAW',
                'body_text': 'This agreement is governed by the laws of [JURISDICTION] and the parties submit to the exclusive jurisdiction of those courts.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'consideration': gate_config(
            domain='definition',
            variant='nda_consideration',
            severity='critical',
            legal='English Contract Law',
            insertion='section',
            context={
                'section_header': 'CONSIDERATION',
                'definition_text': 'Each party acknowledges consideration supporting this agreement, such as mutual exchange of information or other value.',
            },
        ),
        'return_destruction': gate_config(
            domain='procedure',
            variant='return_destruction',
            severity='medium',
            legal='Best practice (confidentiality)',
            insertion='section',
            context={
                'section_header': 'RETURN OR DESTRUCTION',
                'procedure_text': 'Upon request we promptly return or securely destroy confidential materials and confirm completion, retaining only what law requires.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'gdpr_compliance': gate_config(
            domain='definition',
            variant='security_measures',
            severity='high',
            legal='UK GDPR; Data Protection Act 2018',
            insertion='section',
            context={
                'section_header': 'DATA PROTECTION',
                'definition_text': 'Personal data shared under this agreement is processed in accordance with UK GDPR, using it only for the permitted purpose and honouring data subject rights.',
            },
        ),
        'parties_identified': gate_config(
            domain='disclosure',
            variant='nda_parties',
            severity='critical',
            legal='Fundamental Contract Law',
            insertion='start',
            context={
                'section_header': 'PARTIES',
                'body_text': '(1) [PARTY_ONE_NAME] and (2) [PARTY_TWO_NAME], including permitted subsidiaries and advisers, enter into this agreement.',
                'contact_details': '[CONTACT_DETAILS]',
            },
        ),
        'permitted_purpose': gate_config(
            domain='definition',
            variant='nda_purpose',
            severity='high',
            legal='Reasonableness of restrictions',
            insertion='section',
            context={
                'section_header': 'PERMITTED PURPOSE',
                'definition_text': 'Confidential information may be used solely to evaluate or progress the defined project. Any wider use requires prior written consent.',
            },
        ),
    },
    'tax_uk': {
        'vat_invoice_integrity': gate_config(
            domain='definition',
            variant='tax_invoice',
            severity='critical',
            legal='VAT Regulations 1995 (Regulation 14); HMRC VAT Notice 700/21',
            insertion='section',
            context={
                'section_header': 'VAT INVOICE REQUIREMENTS',
                'definition_text': 'Invoices include a unique number, issue date, supplier and customer details, VAT number, description, net amount, VAT amount, and total payable.',
            },
        ),
        'vat_number_format': gate_config(
            domain='disclosure',
            variant='tax_registration',
            severity='critical',
            legal='HMRC VAT Registration Manual (VATREG03700)',
            insertion='section',
            context={
                'section_header': 'VAT REGISTRATION',
                'body_text': 'We display the VAT number (GB or XI prefix followed by nine digits) on invoices, correspondence, and digital receipts.',
                'contact_details': 'hmrc.gov.uk or 0300 200 3700',
            },
        ),
        'vat_rate_accuracy': gate_config(
            domain='definition',
            variant='tax_invoice',
            severity='high',
            legal='VAT Act 1994; HMRC Guidance on VAT rates',
            insertion='section',
            context={
                'section_header': 'APPLIED VAT RATES',
                'definition_text': 'We apply the correct VAT rate (standard, reduced, zero, or exempt) to each supply and document the rationale with supporting records.',
            },
        ),
        'vat_threshold': gate_config(
            domain='definition',
            variant='vat_threshold',
            severity='critical',
            legal='VAT Act 1994 §3; HMRC Guidance',
            insertion='section',
            context={
                'section_header': 'VAT THRESHOLD',
                'definition_text': 'Monitor rolling taxable turnover against the £90,000 registration threshold and notify HMRC immediately when the limit is exceeded or forecast.',
            },
        ),
        'invoice_legal_requirements': gate_config(
            domain='definition',
            variant='tax_invoice',
            severity='high',
            legal='Companies Act 2006; GOV.UK Guidance on Invoicing',
            insertion='section',
            context={
                'section_header': 'INVOICE LEGAL ELEMENTS',
                'definition_text': 'Invoices show the legal entity name, registered office, company number, description of supplies, pricing, and payment terms that meet UK company law.',
            },
        ),
        'company_limited_suffix': gate_config(
            domain='disclosure',
            variant='tax_registration',
            severity='high',
            legal='Companies Act 2006; Companies (Trading Disclosures) Regulations 2008',
            insertion='section',
            context={
                'section_header': 'COMPANY NAME DISCLOSURE',
                'body_text': 'We display the full registered name including "Limited" or "Ltd" on invoices, letters, and emails in accordance with trading disclosure rules.',
                'contact_details': 'companieshouse.gov.uk',
            },
        ),
        'tax_deadline_accuracy': gate_config(
            domain='procedure',
            variant='timeframes',
            severity='critical',
            legal='HMRC Self-Assessment and Corporation Tax deadlines',
            insertion='section',
            context={
                'section_header': 'TAX DEADLINES',
                'procedure_text': 'We diarise VAT returns, Corporation Tax, PAYE, and other statutory filings to ensure submissions and payments reach HMRC on time.',
            },
        ),
        'mtd_compliance': gate_config(
            domain='procedure',
            variant='record_keeping',
            severity='high',
            legal='Finance (No.2) Act 2017; HMRC MTD Regulations',
            insertion='section',
            context={
                'section_header': 'MAKING TAX DIGITAL',
                'procedure_text': 'We maintain digital records and submit VAT returns via compatible software with end-to-end digital links.',
            },
        ),
        'allowable_expenses': gate_config(
            domain='definition',
            variant='product_scope',
            severity='high',
            legal='Income Tax Act 2005 §34 / Corporation Tax Act 2009 §54',
            insertion='section',
            context={
                'section_header': 'ALLOWABLE EXPENSES',
                'definition_text': 'We claim only expenses incurred wholly and exclusively for business purposes and retain receipts or digital copies to evidence each claim.',
            },
        ),
        'capital_revenue_distinction': gate_config(
            domain='definition',
            variant='product_scope',
            severity='high',
            legal='Capital Allowances Act 2001; HMRC guidance',
            insertion='section',
            context={
                'section_header': 'CAPITAL VS REVENUE',
                'definition_text': 'We classify expenditure correctly between capital and revenue and apply the appropriate relief (for example, capital allowances).',
            },
        ),
        'business_structure_consistency': gate_config(
            domain='definition',
            variant='product_scope',
            severity='medium',
            legal='Companies Act 2006; HMRC terminology',
            insertion='section',
            context={
                'section_header': 'BUSINESS STRUCTURE',
                'definition_text': 'Documents use consistent terminology for our legal entity (limited company, LLP, sole trader) and align with Companies House records.',
            },
        ),
        'hmrc_scam_detection': gate_config(
            domain='risk_warning',
            variant='tax_exposure',
            severity='critical',
            legal='Fraud Act 2006; HMRC guidance on scams',
            insertion='section',
            context={
                'section_header': 'HMRC SCAM WARNING',
                'risk_detail': 'Warn customers that HMRC will never demand instant payment via gift cards or threaten arrest. Provide official contact routes to verify messages.',
            },
        ),
        'scottish_tax_specifics': gate_config(
            domain='definition',
            variant='product_scope',
            severity='medium',
            legal='Scotland Act 2016; Scottish tax bands',
            insertion='section',
            context={
                'section_header': 'SCOTTISH TAX SPECIFICS',
                'definition_text': 'We account for Scottish Income Tax rates and devolved taxes (LBTT, SLfT) when transactions concern Scotland.',
            },
        ),
        'invoice_numbering': gate_config(
            domain='definition',
            variant='tax_invoice',
            severity='medium',
            legal='VAT Regulations 1995; HMRC VATREC5010',
            insertion='section',
            context={
                'section_header': 'INVOICE NUMBERING',
                'definition_text': 'Invoices follow a unique, sequential numbering pattern with controls preventing duplication or gaps.',
            },
        ),
        'payment_method_validation': gate_config(
            domain='procedure',
            variant='support_journey',
            severity='critical',
            legal='GOV.UK guidance on paying HMRC',
            insertion='section',
            context={
                'section_header': 'PAYMENT METHODS',
                'procedure_text': 'We accept HMRC-recognised payment routes (BACS, CHAPS, Direct Debit, corporate card via GOV.UK) and warn customers against transferring funds to personal accounts.',
            },
        ),
    },
}

PRIORITY_MAP = {
    'critical': 100,
    'high': 90,
    'medium': 80,
    'low': 70,
}


def _default_insertion_point(domain: str) -> str:
    if domain == 'risk_warning':
        return 'start'
    return 'section'


for module_id, module_map in MODULE_TAXONOMY.items():
    for gate_id, meta in module_map.items():
        meta.setdefault('variant', None)
        meta.setdefault('context', {})
        severity = (meta.get('severity') or 'medium').lower()
        meta['severity'] = severity
        meta.setdefault('priority', PRIORITY_MAP.get(severity, 75))
        if 'insertion_point' not in meta:
            meta['insertion_point'] = _default_insertion_point(meta['domain'])
        meta.setdefault('module_id', module_id)
        meta.setdefault('gate_id', gate_id)
