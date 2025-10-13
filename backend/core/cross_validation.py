from typing import Dict, Any, List


class CrossValidator:
    def run(self, text: str, modules: Dict[str, Any], universal: Dict[str, Any], analyzers: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        text_l = (text or '').lower()

        tax = (modules or {}).get('tax_uk', {}).get('gates', {}) if modules else {}
        gdpr = (modules or {}).get('gdpr_uk', {}).get('gates', {}) if modules else {}
        hr = (modules or {}).get('hr_scottish', {}).get('gates', {}) if modules else {}
        nda = (modules or {}).get('nda_uk', {}).get('gates', {}) if modules else {}

        def gate_status(gates: Dict[str, Any], key: str) -> str:
            g = gates.get(key) or {}
            return (g.get('status') or 'N/A').upper()

        # Rule 1: Tax invoice consistency (if both core invoice gates fail)
        if tax:
            inv_fail = gate_status(tax, 'vat_invoice_integrity') == 'FAIL'
            req_fail = gate_status(tax, 'invoice_legal_requirements') == 'FAIL'
            if inv_fail and req_fail:
                issues.append({
                    'id': 'invoice_consistency_failure',
                    'severity': 'critical',
                    'message': 'VAT invoice fails both integrity and legal requirements checks'
                })

        # Rule 2: GDPR automated decisions without rights
        if gdpr:
            auto_fail = gate_status(gdpr, 'automated_decisions') == 'FAIL'
            rights_fail = gate_status(gdpr, 'rights') == 'FAIL'
            if auto_fail and rights_fail:
                issues.append({
                    'id': 'gdpr_automation_rights_gap',
                    'severity': 'critical',
                    'message': 'Automated decision-making disclosed without data subject rights'
                })

        # Rule 3: NDA whistleblowing carveout missing while HR confidentiality present
        if nda and hr:
            wb_fail = gate_status(nda, 'protected_whistleblowing') == 'FAIL'
            conf_pass = gate_status(hr, 'confidentiality') == 'PASS'
            if wb_fail and conf_pass:
                issues.append({
                    'id': 'nda_hr_conflict',
                    'severity': 'high',
                    'message': 'NDA blanket prohibition conflicts with HR confidentiality policy (no whistleblowing carve-out)'
                })

        # Rule 4: PII in invoice context — only flag sensitive identifiers (reduce false positives)
        if 'invoice' in text_l:
            u_pii = (universal or {}).get('pii') or {}
            spans = u_pii.get('spans') or []
            severe_types = {'credit_card', 'ni_number', 'nhs_number', 'ssn'}
            severe_spans = [s for s in spans if (s or {}).get('type') in severe_types]

            a_pii = (analyzers or {}).get('pii') or {}
            entities = a_pii.get('entities') or []
            severe_entities = [e for e in entities if (e or {}).get('type') in severe_types]

            if severe_spans or severe_entities:
                sev = 'critical' if any((s or {}).get('severity') == 'critical' for s in severe_spans) or any((e or {}).get('type') == 'credit_card' for e in severe_entities) else 'high'
                issues.append({
                    'id': 'sensitive_pii_in_invoice',
                    'severity': sev,
                    'message': 'Sensitive identifiers detected in invoice context (e.g., card/NI/NHS)'
                })

        # Rule 5: Security breach mentions without notification guidance
        if gdpr:
            breach_fail = gate_status(gdpr, 'breach_notification') == 'FAIL'
            security_fail = gate_status(gdpr, 'security') == 'FAIL'
            if breach_fail and security_fail:
                issues.append({
                    'id': 'gdpr_breach_without_notification',
                    'severity': 'critical',
                    'message': 'Security weakness acknowledged without breach notification protocol'
                })

        # Rule 6: NDA whistleblowing missing alongside illegal content signals
        illegal = (universal or {}).get('illegal_content') or {}
        if nda and illegal and illegal.get('status') == 'FAIL':
            wb_fail = gate_status(nda, 'protected_whistleblowing') == 'FAIL'
            crime_gate = gate_status(nda, 'protected_crime_reporting') == 'FAIL'
            if wb_fail or crime_gate:
                issues.append({
                    'id': 'nda_illegal_content_gap',
                    'severity': 'high',
                    'message': 'Illegal activity detected but NDA lacks crime reporting carve-outs'
                })

        # Rule 7: Bias signals combined with HR dismissal risks
        bias = (universal or {}).get('bias') or {}
        if hr and bias and bias.get('status') == 'FAIL':
            dismissal_fail = gate_status(hr, 'dismissal') == 'FAIL'
            allegations_fail = gate_status(hr, 'allegations') == 'FAIL'
            if dismissal_fail or allegations_fail:
                issues.append({
                    'id': 'hr_bias_risk',
                    'severity': 'critical',
                    'message': 'Biased language present alongside defective disciplinary process'
                })

        # Rule 8: Self-harm or violent instructions flagged with no safeguarding
        harm = (universal or {}).get('harm') or {}
        if harm and harm.get('status') == 'FAIL':
            safeguarding_present = False
            if gdpr:
                safeguarding_present = gate_status(gdpr, 'rights') == 'PASS'
            if not safeguarding_present:
                sev = harm.get('severity', 'high')
                issues.append({
                    'id': 'harm_without_safeguard',
                    'severity': sev,
                    'message': 'Harmful content detected without safeguarding or rights guidance'
                })

        return {'issues': issues}
