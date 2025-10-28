#!/usr/bin/env python3
"""
Generate gold fixture suite for compliance testing.
Creates 15-20 realistic failing documents per module covering worst-case scenarios.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / 'tests' / 'semantic' / 'gold_fixtures'

# FCA UK fixtures - Financial promotions with multiple violations
FCA_FIXTURES = {
    '05_no_risk_warnings.txt': """Premium Investment Portfolio

Our sophisticated investment strategy targets high-growth companies. Average returns of 12% annually.

Managed by our award-winning team. Portfolio rebalanced quarterly. Performance fees only charged on profits.

Get started with just £10,000. Visit our website to apply.""",

    '06_finfluencer_uncontrolled.txt': """Follow @CryptoKing on TikTok for hot investment tips!

Our community has made millions trading NFTs and DeFi tokens. Join our exclusive Discord for signals.

No boring financial advice - just pure profit strategies. Link in bio to start trading.

#GetRich #FinancialFreedom #CryptoMillionaire""",

    '07_no_target_market.txt': """Multi-Asset Growth Fund

Invest in our diversified portfolio spanning equities, bonds, commodities, and alternatives.

Leverage up to 3x available for qualified investors. Minimum investment £50,000.

Contact our team to discuss your investment needs.""",

    '08_missing_fair_value.txt': """Executive Pension Transfer Service

Transfer your defined benefit pension into our SIPP for greater flexibility and control.

Unlock your pension cash now. Access up to 25% tax-free immediately. Fees from £2,500.

We've helped thousands of executives maximize their retirement funds.""",

    '09_conflicts_undisclosed.txt': """Recommended Investment Opportunities

Our preferred funds for 2024:
- Global Growth Fund (managed by our parent company)
- UK Property Fund (we receive 3% commission)
- Emerging Markets Fund

Speak to our advisers about which is right for you.""",

    '10_client_money_unclear.txt': """Investment Account Opening

Deposit your funds to: Business Account, Sort Code 12-34-56, Account 12345678.

Your money will be held securely while we process your application. Setup fees of £500 will be deducted.

Processing takes 5-10 business days.""",

    '11_implicit_advice.txt': """Investment Comparison Tool

Our tool shows the top 5 performing funds in your risk category. Most customers choose Fund A due to superior returns.

Simply complete the questionnaire and we'll show you the best options. No advice given - you decide.

Open your account in minutes.""",

    '12_poor_comprehension.txt': """Structured Product: FTSE 100 Participation Note

Capital at risk. Participation rate 150%. Barrier 50%. Autocall quarterly at 105%. Counterparty exposure to Global Bank.

Memory feature included. Underlying index FTSE 100 (UKX). Payoff formula: max(0, 100% + 1.5 × return) if barrier not breached.

Minimum £20,000. ISIN: GB00XYZ12345.""",

    '13_no_complaint_info.txt': """Wealth Management Service

We manage portfolios for high net worth individuals. Bespoke investment strategies tailored to your goals.

Annual management fee 1.25%. Performance fee 20% above 8% return. Minimum portfolio £250,000.

To get started, complete our client onboarding form.""",

    '14_third_party_bank_unclear.txt': """Deposit Instructions

Send your investment funds to:
Metro Business Banking
Account Name: Client Funds Pool
Sort Code: 98-76-54
Account: 87654321

Quote your client reference number. Funds must be received before we can proceed.""",

    '15_no_record_keeping_notice.txt': """Telephone Investment Service

Call our dealing desk: 0800 123 4567
Lines open 8am-8pm Monday-Friday

Provide your account number and the fund you wish to purchase. Deals executed immediately.

Confirmation sent by email within 24 hours.""",
}

# GDPR UK fixtures - Data protection violations
GDPR_FIXTURES = {
    '01_no_lawful_basis.txt': """Customer Data Collection

We collect your name, address, email, phone number, date of birth, financial information, and browsing history.

This information helps us provide better service. By using our site you agree to data collection.

See our website for more details.""",

    '02_missing_consent.txt': """Newsletter Signup

Thanks for signing up! You'll now receive weekly investment tips, partner offers, and market updates.

We may share your email with carefully selected third parties. You can unsubscribe anytime.

Welcome to our community!""",

    '03_unclear_purpose.txt': """Privacy Notice

We process your personal data for various purposes including service delivery, marketing, analytics, fraud prevention, and other legitimate business interests.

Your data may be used to improve our services and for research purposes.

For questions, contact privacy@example.com.""",

    '04_no_retention_period.txt': """Account Closure Confirmation

Your account has been closed as requested. We will retain your personal data as required for regulatory and business purposes.

Historical transaction data will be kept on our systems. Account records may be retained indefinitely.

Thank you for being a customer.""",

    '05_rights_not_explained.txt': """Data Protection Information

We take your privacy seriously and comply with UK GDPR. Your data is stored securely.

If you have concerns, email dataprotection@example.com.

Last updated: January 2024.""",

    '06_weak_security.txt': """Account Access

Your password has been reset to: Password123

Please log in using this temporary password. You may change it later if desired.

If you didn't request this, please contact support.""",

    '07_excessive_collection.txt': """Investment Profile Questionnaire

Please provide: Full name, date of birth, national insurance number, passport number, driving license number, mother's maiden name, employment history, salary details, bank statements (last 3 years), credit score, medical conditions, marital status, children's names and ages.

We need complete information to process your application.""",

    '08_third_party_sharing_vague.txt': """Partner Network Disclosure

To provide our services, we may share your information with service providers, affiliates, business partners, and other third parties.

These partners help us deliver enhanced services. They may contact you directly with relevant offers.

Your data may be shared internationally.""",

    '09_no_transfer_safeguards.txt': """Global Service Notice

Our servers are located in USA, India, and Singapore. Your data will be processed across these locations for efficiency.

Customer support is handled by our team in Mumbai. Data processing occurs wherever our staff are located.

This enables 24/7 service availability.""",

    '10_automated_decisions_opaque.txt': """Credit Decision

Thank you for your application. After automated assessment, your application has been declined.

Our system evaluated multiple factors. This decision is final.

You may reapply in 6 months.""",

    '11_children_data_unprotected.txt': """Junior Investment Account

Open an investment account for your child (ages 0-17). We'll send them regular updates about their portfolio.

Marketing materials will be sent to the child's email. Account credentials provided directly to the minor.

Start investing in their future today!""",

    '12_no_breach_notification.txt': """System Maintenance Notice

We recently upgraded our database systems. Some customer records were temporarily unavailable during the migration.

All systems are now operational. No action required from customers.

Thank you for your patience.""",

    '13_no_dpo_contact.txt': """Company Information

Example Investment Services Ltd
123 Finance Street
London EC1A 1BB

Email: info@example.com
Phone: 0800 123 4567

Registered in England No. 1234567""",

    '14_cookies_no_consent.txt': """Cookie Policy

This website uses cookies for functionality, analytics, marketing, and tracking. Essential cookies are always enabled.

Third-party cookies from our partners help us understand user behavior. Advertising cookies enable personalized ads.

By continuing to use this site, you accept all cookies.""",

    '15_cant_withdraw_consent.txt': """Marketing Preferences

You have opted in to receive marketing communications. These emails help us keep you informed of opportunities.

Your consent is recorded in our system. To update preferences, you must call our customer service team.

Marketing emails are an important part of our service.""",
}

# HR Scottish fixtures - Employment law violations
HR_FIXTURES = {
    '01_no_accompaniment_notice.txt': """Disciplinary Meeting Invitation

You are required to attend a disciplinary hearing on 15th March 2024 at 2pm in Conference Room B.

The matter concerns your performance and conduct. Please attend punctually.

Failure to attend may result in the hearing proceeding in your absence.""",

    '02_allegations_vague.txt': """Investigation Meeting

We need to discuss some concerns that have been raised about your behavior at work.

Please attend a meeting on Monday to discuss these issues. The meeting will be with your line manager.

Bring any relevant information you think is important.""",

    '03_no_evidence_disclosed.txt': """Disciplinary Hearing - Final Notice

Further to our investigation, a disciplinary hearing will be held on 20th March 2024.

You are accused of serious misconduct. The panel will consist of HR Director and Department Head.

You may face dismissal. Attend to present your case.""",

    '04_no_appeal_rights.txt': """Disciplinary Outcome

Following the hearing on 20th March, you are hereby issued with a final written warning valid for 12 months.

Any further misconduct will result in dismissal. This decision has been carefully considered.

The warning will be placed on your personnel file.""",

    '05_investigation_skipped.txt': """Suspension Notice

You are suspended with immediate effect on full pay pending a disciplinary hearing.

Allegations of misconduct have been received. A hearing will be scheduled within 2 weeks.

Do not contact colleagues or attend the workplace. Hand in your access card and laptop today.""",

    '06_insufficient_notice.txt': """Urgent Meeting Required

You must attend a disciplinary meeting tomorrow at 9am. This concerns serious allegations.

Your manager and HR will be present. Be prepared to answer questions.

Confirm attendance by 5pm today.""",

    '07_inconsistent_treatment.txt': """Performance Warning

Your sales figures are below target. This is unacceptable given the current market conditions.

You will be placed on a performance improvement plan for 30 days. Failure to improve will lead to dismissal.

Other team members are meeting targets so we know it's achievable.""",

    '08_witness_statements_withheld.txt': """Disciplinary Evidence Summary

Multiple colleagues have raised concerns about your conduct. These complaints are serious and consistent.

The disciplinary panel has reviewed all statements. You will have an opportunity to respond at the hearing.

Hearing scheduled for 25th March 2024.""",

    '09_no_meeting_notes.txt': """Meeting Confirmation

Thank you for attending the investigatory meeting today. We discussed the allegations in detail.

The investigation will now proceed. You will be informed of the outcome in due course.

Continue to report for work as normal unless instructed otherwise.""",

    '10_unjustified_suspension.txt': """Immediate Suspension

You are suspended without pay effective immediately. Allegations of gross misconduct have been made.

An investigation will commence shortly. You must not enter company premises.

Your access has been revoked. Collect personal belongings under supervision.""",

    '11_previous_warnings_ignored.txt': """Final Written Warning

Your continued poor performance requires formal action. This final warning will remain on file for 12 months.

Any repetition will result in dismissal. You must improve immediately.

Your manager will monitor your performance weekly.""",

    '12_no_outcome_reasons.txt': """Disciplinary Decision

Following the hearing, we have decided to issue a written warning. This will remain valid for 6 months.

You should reflect on your conduct and ensure improvement. Further action may be necessary.

This concludes the disciplinary process.""",

    '13_representation_denied.txt': """Meeting Protocol

Tomorrow's disciplinary hearing is for you alone. Due to the serious nature, we require your personal attendance without accompaniment.

Legal representatives and union officials are not permitted. This is an internal matter.

The hearing will last approximately 1 hour.""",

    '14_unreasonable_timeframe.txt': """Investigation Outcome

Following a 6-month investigation, we have concluded there is a case to answer. A disciplinary hearing will be held next week.

You will receive the evidence pack 24 hours before the hearing. The hearing is scheduled for 3 hours.

Prepare your response to the allegations.""",

    '15_informal_threats.txt': """Informal Conversation Notes

Following our chat in the corridor, just to confirm - if your timekeeping doesn't improve by next week, we'll have to let you go.

This is just a friendly warning. We don't want to go down the formal route if we can avoid it.

Let's see how next week goes and take it from there.""",
}

# NDA UK fixtures - Contract law violations
NDA_FIXTURES = {
    '01_blocks_whistleblowing.txt': """Non-Disclosure Agreement

The Receiving Party agrees not to disclose any information relating to the Disclosing Party's business, including but not limited to:
- Financial information
- Business practices
- Customer data
- Internal processes
- Any matters observed during the course of engagement

This obligation continues indefinitely. Breach will result in legal action and damages of £100,000.

Any disclosure for any reason is strictly prohibited.""",

    '02_blocks_crime_reporting.txt': """Confidentiality Clause

You must not disclose any information about Company operations to any third party including regulators, law enforcement, or legal authorities.

All internal matters must remain strictly confidential. Violation will be treated as gross misconduct.

This includes information about accounting practices, regulatory matters, or internal investigations.""",

    '03_blocks_harassment_reporting.txt': """Settlement Agreement

In consideration of the payment of £15,000, you agree to maintain absolute confidentiality regarding:
- Your employment
- Reasons for termination
- Any events during employment
- Workplace relationships

You must not discuss these matters with anyone. This includes complaints, grievances, or disputes.

Breach voids the settlement payment.""",

    '04_definition_too_broad.txt': """Mutual Non-Disclosure Agreement

"Confidential Information" means any and all information of any kind disclosed by either party, in any form, whether marked confidential or not.

This includes but is not limited to: business information, personal information, observations, opinions, ideas, and any other information.

All information exchanged is presumed confidential unless explicitly stated otherwise in writing.""",

    '05_no_public_domain_exclusion.txt': """Confidentiality Agreement

The Recipient agrees to keep all Confidential Information secret and not to disclose to any third party.

Confidential Information includes trade secrets, business plans, customer lists, and technical data.

This obligation is absolute and admits no exceptions.""",

    '06_no_prior_knowledge_exclusion.txt': """NDA - Technology Partnership

Neither party shall disclose the other's Confidential Information without written consent.

All information shared during the partnership term is covered by this agreement.

Confidentiality obligations commence from the date of this agreement.""",

    '07_unreasonable_duration.txt': """Confidentiality Undertaking

The Recipient agrees to keep all Confidential Information secret in perpetuity.

This obligation survives termination of any relationship and continues indefinitely without time limit.

The duty of confidence is absolute and eternal.""",

    '08_no_permitted_disclosures.txt': """Non-Disclosure Obligations

You must not disclose Confidential Information to anyone under any circumstances.

This prohibition is absolute. No disclosure is permitted for any reason.

Legal, professional, or regulatory requirements do not override this obligation.""",

    '09_no_governing_law.txt': """Confidentiality Agreement

The parties agree to keep certain information confidential as detailed below.

Confidential Information includes business plans, customer data, and proprietary processes.

Term: 3 years from the date of disclosure.

Signed: ________________""",

    '10_no_consideration.txt': """One-Way NDA

Receiving Party agrees to maintain confidentiality of all information disclosed by Disclosing Party.

Obligations commence immediately upon signature and continue for 5 years.

Receiving Party acknowledges the value and sensitivity of the information.""",

    '11_no_return_destruction.txt': """NDA Termination Notice

This agreement terminates effective 31st December 2024.

Both parties' confidentiality obligations continue for the full 5-year term from original disclosure dates.

Thank you for your cooperation during this partnership.""",

    '12_no_gdpr_compliance.txt': """Standard NDA Template

Neither party shall disclose Confidential Information without written consent.

Personal data of customers, employees, and contractors is included in Confidential Information.

Standard industry terms apply throughout.""",

    '13_parties_not_identified.txt': """Confidentiality Agreement

This agreement is entered into on 1st January 2024 between the parties identified below.

The Receiving Party shall not disclose Confidential Information belonging to the Disclosing Party.

Signed: ________________
Date: ________________""",

    '14_no_permitted_purpose.txt': """Mutual NDA

Both parties may share confidential information during discussions.

Recipients must keep all shared information confidential and not disclose to third parties.

This agreement governs all information exchanges between the parties for the next 2 years.""",
}

# Tax UK fixtures - Tax compliance violations
TAX_FIXTURES = {
    '01_vat_invoice_incomplete.txt': """INVOICE

To: Customer Name
Item: Consulting Services
Amount: £5,000

Payment due within 30 days.

Thank you for your business.""",

    '02_invalid_vat_number.txt': """TAX INVOICE

From: ABC Services Ltd
VAT Reg: 123456789

Services rendered: £10,000
VAT @ 20%: £2,000
Total: £12,000

Payment details: Bank transfer to Sort Code 12-34-56, Account 12345678""",

    '03_wrong_vat_rate.txt': """INVOICE #2024-001

Children's Educational Books: £500.00
VAT @ 20%: £100.00
Total: £600.00

VAT No: GB123456789

Payment terms: Net 30 days""",

    '04_below_vat_threshold_claiming.txt': """Professional Services Invoice

Annual revenue: £60,000
Service charge: £1,200
VAT @ 20%: £240
Total: £1,440

VAT Registration: GB987654321

We are VAT registered and charge VAT on all services.""",

    '05_missing_company_details.txt': """INVOICE

Consulting Services: £3,000
VAT @ 20%: £600
Total: £3,600

Contact: info@example.com
VAT No: GB123456789""",

    '06_no_limited_suffix.txt': """Invoice from XYZ Company

XYZ Company
123 Business Road
London E1 6AN

To: Client Name
Service: Business Advisory
Amount: £2,500 + VAT

Company Reg: 12345678""",

    '07_wrong_tax_deadline.txt': """Tax Planning Advisory

Important: Your Self Assessment tax return must be filed by 31st January 2025 and payment made by the same date.

HMRC penalties apply for late filing. Get your return in early to avoid issues.

We recommend filing by December to allow processing time.""",

    '08_no_mtd_notice.txt': """VAT Return Reminder

Your VAT return for Q4 2024 is due by 31st January 2025.

Calculate your VAT owed and submit payment to HMRC. Keep records of all transactions.

We can assist with VAT calculations for a fee of £150 + VAT.""",

    '09_non_allowable_expense_advice.txt': """Tax Deductions Guide

You can claim the following as business expenses:
- Client entertainment meals
- Personal gym membership (for health)
- Home extension (creates office space)
- Personal car (used occasionally for business)
- Family holiday (attended networking event)

Maximize your deductions to minimize tax. HMRC rarely checks small businesses.""",

    '10_capital_revenue_confused.txt': """Business Purchase Advice

The £50,000 cost of purchasing new computers can be deducted from your profits this year as a business expense.

This will significantly reduce your tax bill. Claim the full amount on your tax return.

Equipment purchases are standard business expenses.""",

    '11_inconsistent_structure.txt': """Tax Status Change

We recommend switching between sole trader and limited company status each tax year to optimize tax position.

Operate as sole trader when profits are low, incorporate when profits are high. This is standard tax planning.

You can change structure annually to minimize tax.""",

    '12_hmrc_scam_enablement.txt': """URGENT: HMRC TAX REFUND

You are entitled to a tax refund of £2,847.65. Click here to claim immediately.

Refund expires in 48 hours. Provide your national insurance number, bank details, and date of birth to process.

HMRC Refund Processing Team
Email: refunds@hmrc-gov.co.uk""",

    '13_scottish_tax_ignored.txt': """Income Tax Calculation - Scottish Client

Income: £60,000
Personal Allowance: £12,570
Taxable: £47,430

Tax calculation:
£12,570 @ 0% = £0
£37,700 @ 20% = £7,540
£9,730 @ 40% = £3,892

Total tax: £11,432

Standard UK income tax rates applied.""",

    '14_no_invoice_sequence.txt': """INVOICE

Date: 15/03/2024
Client: ABC Ltd
Service: Consulting
Amount: £5,000 + VAT

Payment within 30 days please.

Next invoice: 22/03/2024 - Invoice
Previous invoice: 01/03/2024 - Invoice""",

    '15_cash_only_payment.txt': """Payment Terms

We only accept cash payments for tax efficiency. Card and bank transfer not available.

Cash payment avoids processing fees and admin. Receipt provided on request.

Please bring exact amount in cash to appointments.

No payment records kept for amounts under £1,000.""",
}

def write_fixtures():
    """Write all gold fixtures to disk."""
    fixtures = {
        'fca_uk': FCA_FIXTURES,
        'gdpr_uk': GDPR_FIXTURES,
        'hr_scottish': HR_FIXTURES,
        'nda_uk': NDA_FIXTURES,
        'tax_uk': TAX_FIXTURES,
    }

    for module, docs in fixtures.items():
        module_dir = BASE_DIR / module
        module_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in docs.items():
            filepath = module_dir / filename
            filepath.write_text(content.strip() + '\n')
            print(f"Created: {filepath}")

    print(f"\n✓ Created {sum(len(docs) for docs in fixtures.values())} gold fixtures across 5 modules")

if __name__ == '__main__':
    write_fixtures()
