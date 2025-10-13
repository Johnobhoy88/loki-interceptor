"""
Bulk enhance all remaining modules with N/A messages
GDPR UK (20 gates), HR Scottish (25 gates), NDA UK (14 gates)
"""
import re
import os

# N/A messages for GDPR UK gates
GDPR_MESSAGES = {
    'accountability.py': 'Not applicable - document does not discuss data protection accountability or governance',
    'accuracy.py': 'Not applicable - document does not discuss data accuracy or correction procedures',
    'automated_decisions.py': 'Not applicable - document does not involve automated decision-making or profiling',
    'breach_notification.py': 'Not applicable - document does not discuss data breaches or breach notification procedures',
    'children.py': 'Not applicable - document does not involve children or processing of children\'s data',
    'children_data.py': 'Not applicable - document does not involve processing of children\'s personal data',
    'consent.py': 'Not applicable - document does not involve data collection or consent for processing',
    'cookies_tracking.py': 'Not applicable - document does not discuss cookies or tracking technologies',
    'data_minimisation.py': 'Not applicable - document does not discuss data collection or data minimisation principles',
    'dpo_contact.py': 'Not applicable - document is not a privacy notice requiring DPO contact information',
    'international_transfer.py': 'Not applicable - document does not involve international data transfers',
    'international_transfers.py': 'Not applicable - document does not involve international data transfers outside UK/EEA',
    'lawful_basis.py': 'Not applicable - document does not discuss personal data processing or lawful bases',
    'processors.py': 'Not applicable - document does not involve third-party data processors',
    'purpose.py': 'Not applicable - document does not specify purposes for data processing',
    'retention.py': 'Not applicable - document does not discuss data retention periods or deletion',
    'rights.py': 'Not applicable - document is not a privacy notice requiring data subject rights information',
    'security.py': 'Not applicable - document does not discuss data security measures or safeguards',
    'third_party_sharing.py': 'Not applicable - document does not involve sharing data with third parties',
    'withdrawal_consent.py': 'Not applicable - document does not involve consent or consent withdrawal mechanisms',
}

# N/A messages for HR Scottish gates
HR_MESSAGES = {
    'accompaniment.py': 'Not applicable - document is not a disciplinary or grievance procedure document',
    'allegations.py': 'Not applicable - document does not describe disciplinary allegations or misconduct',
    'appeal.py': 'Not applicable - document is not a disciplinary outcome or dismissal letter',
    'confidentiality.py': 'Not applicable - document does not involve disciplinary or HR processes',
    'consistency.py': 'Not applicable - document does not describe disciplinary sanctions or procedures',
    'disclosure.py': 'Not applicable - document is not a disciplinary investigation or hearing notice',
    'dismissal.py': 'Not applicable - document does not involve dismissal or termination',
    'evidence.py': 'Not applicable - document is not a disciplinary investigation or hearing',
    'impartial_chair.py': 'Not applicable - document does not describe a disciplinary hearing process',
    'informal_threats.py': 'Not applicable - document is not a disciplinary communication',
    'investigation.py': 'Not applicable - document does not involve disciplinary investigation procedures',
    'meeting_details.py': 'Not applicable - document is not a disciplinary meeting notice',
    'meeting_notice.py': 'Not applicable - document is not a disciplinary or grievance meeting invitation',
    'meeting_notes.py': 'Not applicable - document is not disciplinary meeting documentation',
    'mitigating_circumstances.py': 'Not applicable - document is not a disciplinary hearing or outcome',
    'notice.py': 'Not applicable - document is not a disciplinary notice or warning',
    'outcome_reasons.py': 'Not applicable - document is not a disciplinary outcome decision',
    'postponement.py': 'Not applicable - document does not involve disciplinary meeting scheduling',
    'previous_warnings.py': 'Not applicable - document is not a disciplinary sanction decision',
    'representation_choice.py': 'Not applicable - document is not a disciplinary or grievance procedure notice',
    'right_to_be_heard.py': 'Not applicable - document does not involve disciplinary decision-making',
    'sanction_graduation.py': 'Not applicable - document is not a disciplinary sanction for first offense',
    'suspension.py': 'Not applicable - document does not involve suspension during investigation',
    'timeframes.py': 'Not applicable - document does not specify disciplinary process timeframes',
    'witness_statements.py': 'Not applicable - document is not a disciplinary investigation',
}

# N/A messages for NDA UK gates
NDA_MESSAGES = {
    'consideration.py': 'Not applicable - document is not a confidentiality or non-disclosure agreement',
    'definition_specificity.py': 'Not applicable - document is not a non-disclosure agreement',
    'duration_reasonableness.py': 'Not applicable - document is not a confidentiality agreement',
    'gdpr_compliance.py': 'Not applicable - document is not an NDA involving personal data',
    'governing_law.py': 'Not applicable - document is not a non-disclosure or confidentiality agreement',
    'parties_identified.py': 'Not applicable - document is not a formal NDA contract',
    'permitted_disclosures.py': 'Not applicable - document is not a non-disclosure agreement',
    'permitted_purpose.py': 'Not applicable - document is not a confidentiality agreement',
    'prior_knowledge_exclusion.py': 'Not applicable - document is not an NDA or confidentiality agreement',
    'protected_crime_reporting.py': 'Not applicable - document is not a non-disclosure agreement',
    'protected_harassment.py': 'Not applicable - document is not a confidentiality or non-disclosure agreement',
    'protected_whistleblowing.py': 'Not applicable - document is not a non-disclosure agreement',
    'public_domain_exclusion.py': 'Not applicable - document is not an NDA',
    'return_destruction.py': 'Not applicable - document is not a confidentiality agreement',
}

def enhance_gate(filepath, message):
    """Enhanced gate with N/A message"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Pattern: return {'status': 'N/A'}
        old_pattern = r"return \{'status': 'N/A'\}"
        new_return = f"""return {{
                'status': 'N/A',
                'message': '{message}',
                'legal_source': self.legal_source
            }}"""

        count = len(re.findall(old_pattern, content))

        if count > 0:
            content = re.sub(old_pattern, new_return, content)
            with open(filepath, 'w') as f:
                f.write(content)
            return count
        return 0
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")
        return 0

def main():
    print("="*80)
    print("BULK ENHANCING ALL MODULES WITH N/A MESSAGES")
    print("="*80)

    modules = [
        ("GDPR UK", "modules/gdpr_uk/gates", GDPR_MESSAGES),
        ("HR Scottish", "modules/hr_scottish/gates", HR_MESSAGES),
        ("NDA UK", "modules/nda_uk/gates", NDA_MESSAGES),
    ]

    total_enhanced = 0
    total_files = 0

    for module_name, base_path, messages in modules:
        print(f"\n{module_name}:")
        print("-" * 80)

        module_count = 0
        for filename, message in messages.items():
            filepath = os.path.join(base_path, filename)
            if os.path.exists(filepath):
                count = enhance_gate(filepath, message)
                if count > 0:
                    print(f"  ✅ {filename}: Enhanced {count} return(s)")
                    module_count += 1
                    total_enhanced += count
                else:
                    print(f"  ⏭️  {filename}: Already enhanced")
                total_files += 1
            else:
                print(f"  ⚠️  {filename}: File not found")

        print(f"  → {module_count} files enhanced in {module_name}")

    print("\n" + "="*80)
    print(f"COMPLETE: {total_enhanced} enhancements across {total_files} files")
    print("="*80)

if __name__ == "__main__":
    os.chdir('/mnt/c/Users/jpmcm.DESKTOP-CQ0CL93/OneDrive/Desktop/HighlandAI/LOKI_INTERCEPTOR_CLAUDEV1/backend')
    main()
