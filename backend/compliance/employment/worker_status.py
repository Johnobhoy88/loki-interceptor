"""
Worker Status Determination
Determines employment status: Employee, Worker, or Self-Employed
"""

import re
from typing import Dict, List, Any
from enum import Enum


class WorkerStatus(Enum):
    """Employment status categories"""
    EMPLOYEE = "employee"
    WORKER = "worker"
    SELF_EMPLOYED = "self_employed"
    UNCLEAR = "unclear"


class WorkerStatusDetermination:
    """
    Determines worker status based on contract terms and working arrangements

    Legal framework:
    - Employment Rights Act 1996 s.230
    - Autoclenz v Belcher [2011] UKSC 41
    - Uber v Aslam [2021] UKSC 5
    - Pimlico Plumbers v Smith [2018] UKSC 29
    """

    def __init__(self):
        self.legal_source = "Employment Rights Act 1996 s.230, Case Law"

        # Employee indicators (strongest employment relationship)
        self.employee_indicators = {
            'mutuality_of_obligation': [
                r'(?:required|obliged|must).*(?:accept|perform).*work',
                r'employer.*(?:required|obliged|must).*(?:provide|offer).*work'
            ],
            'personal_service': [
                r'(?:personally|yourself|in\s+person).*(?:perform|provide|carry\s+out)',
                r'(?:not|cannot|may\s+not).*(?:substitute|delegate|send\s+replacement)'
            ],
            'control': [
                r'(?:direct|supervise|control|manage).*(?:how|when|where).*work',
                r'subject\s+to.*(?:direction|control|instruction)',
                r'working\s+hours.*(?:set|determined|specified)\s+by'
            ],
            'integration': [
                r'part\s+of.*(?:organisation|business|team)',
                r'(?:company|employer).*equipment|tools|uniform',
                r'email.*(?:address|account).*provided'
            ],
            'exclusivity': [
                r'(?:not|cannot|shall\s+not).*work\s+for.*(?:other|another|competitor)',
                r'(?:full[- ]time|exclusive).*(?:service|employment)'
            ]
        }

        # Worker indicators (limb (b) worker)
        self.worker_indicators = {
            'contract_for_services': [
                r'contract.*(?:provide|perform).*services',
                r'undertakes?\s+to.*(?:do|perform).*work'
            ],
            'not_client_customer': [
                r'(?:not|does\s+not).*(?:client|customer).*(?:of|to).*business',
                r'work.*for.*business.*not.*profession'
            ],
            'personal_performance': [
                r'personally.*(?:perform|execute|carry\s+out)',
                r'limited\s+substitution'
            ]
        }

        # Self-employed indicators
        self.self_employed_indicators = {
            'business_on_own_account': [
                r'(?:own|independent).*business',
                r'business\s+risk|financial\s+risk',
                r'profit\s+(?:and|or)\s+loss'
            ],
            'multiple_clients': [
                r'(?:other|multiple|various)\s+(?:client|customer|engager)',
                r'free\s+to.*work\s+for.*other'
            ],
            'substitution': [
                r'(?:may|can|entitled\s+to).*(?:substitute|send\s+replacement|delegate)',
                r'substitution.*(?:unfettered|unlimited)'
            ],
            'invoicing': [
                r'invoice|raise.*invoice|bill\s+for.*services',
                r'payment.*(?:invoice|receipt\s+of\s+invoice)'
            ],
            'own_equipment': [
                r'(?:own|provide.*own).*(?:equipment|tools|materials)',
                r'responsible\s+for.*(?:equipment|tools)'
            ]
        }

    def determine_status(self, text: str) -> Dict[str, Any]:
        """
        Determine worker status from contract/document text

        Args:
            text: Contract or document text

        Returns:
            Dict with status determination and analysis
        """
        results = {
            'status': WorkerStatus.UNCLEAR,
            'confidence': 'low',
            'employee_score': 0,
            'worker_score': 0,
            'self_employed_score': 0,
            'indicators_found': {
                'employee': [],
                'worker': [],
                'self_employed': []
            },
            'analysis': '',
            'legal_source': self.legal_source,
            'warnings': []
        }

        # Check employee indicators
        for indicator_name, patterns in self.employee_indicators.items():
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                results['employee_score'] += 1
                results['indicators_found']['employee'].append(indicator_name)

        # Check worker indicators
        for indicator_name, patterns in self.worker_indicators.items():
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                results['worker_score'] += 1
                results['indicators_found']['worker'].append(indicator_name)

        # Check self-employed indicators
        for indicator_name, patterns in self.self_employed_indicators.items():
            if any(re.search(p, text, re.IGNORECASE) for p in patterns):
                results['self_employed_score'] += 1
                results['indicators_found']['self_employed'].append(indicator_name)

        # Determine status based on scores
        total_employee_indicators = len(self.employee_indicators)
        total_self_employed_indicators = len(self.self_employed_indicators)

        employee_percentage = (results['employee_score'] / total_employee_indicators) * 100
        self_employed_percentage = (results['self_employed_score'] / total_self_employed_indicators) * 100

        # Employee status (highest protection)
        if employee_percentage >= 60:
            results['status'] = WorkerStatus.EMPLOYEE
            results['confidence'] = 'high' if employee_percentage >= 80 else 'medium'
            results['analysis'] = f"Strong employee indicators ({employee_percentage:.0f}%): mutuality of obligation, personal service, control, integration. Full employment rights."
            results['rights'] = "Full employment rights including: unfair dismissal, redundancy pay, statutory notice, TUPE, written particulars"

        # Self-employed (lowest protection)
        elif self_employed_percentage >= 60 and employee_percentage < 40:
            results['status'] = WorkerStatus.SELF_EMPLOYED
            results['confidence'] = 'high' if self_employed_percentage >= 80 else 'medium'
            results['analysis'] = f"Strong self-employed indicators ({self_employed_percentage:.0f}%): business on own account, substitution, multiple clients, own equipment. Limited employment rights."
            results['rights'] = "Limited rights: health & safety, discrimination protection (if personally providing services). No unfair dismissal, statutory notice, or most employment rights."
            results['warnings'].append("If substitution is restricted or mutuality exists, may be reclassified as worker/employee")

        # Worker status (intermediate)
        elif results['worker_score'] >= 2 or (employee_percentage >= 30 and employee_percentage < 60):
            results['status'] = WorkerStatus.WORKER
            results['confidence'] = 'medium'
            results['analysis'] = f"Worker status (limb b): contract to personally perform services, not client/customer of business. Intermediate employment rights."
            results['rights'] = "Worker rights: NMW/NLW, holiday pay, rest breaks, whistleblowing, discrimination protection, working time limits. No unfair dismissal (unless 2+ years service and treated as employee)."

        # Unclear
        else:
            results['status'] = WorkerStatus.UNCLEAR
            results['confidence'] = 'low'
            results['analysis'] = "Insufficient indicators to determine status. Actual working arrangements will determine status (Autoclenz v Belcher [2011])."
            results['warnings'].append("Courts look at actual working arrangements, not just contract terms")
            results['warnings'].append("Consider: Can worker refuse work? Can they send substitute? Do they have multiple clients?")

        # Check for sham contract indicators
        sham_patterns = [
            r'(?:independent\s+contractor|self[- ]employed).*(?:in\s+name\s+only|but\s+actually)',
            r'(?:label|status).*does\s+not\s+reflect.*reality'
        ]
        if any(re.search(p, text, re.IGNORECASE) for p in sham_patterns):
            results['warnings'].append("Possible sham self-employment arrangement - courts look at reality not labels")

        return results

    def get_recommendations(self, determination_result: Dict[str, Any]) -> List[str]:
        """Get recommendations based on status determination"""
        recommendations = []

        status = determination_result['status']

        if status == WorkerStatus.UNCLEAR:
            recommendations.append("Clarify: mutuality of obligation, personal service requirement, degree of control")
            recommendations.append("Specify: can worker refuse work? Can they send substitute? Multiple clients permitted?")

        if status == WorkerStatus.EMPLOYEE:
            recommendations.append("Ensure full employment rights provided: written particulars, notice periods, disciplinary procedures")

        if status == WorkerStatus.SELF_EMPLOYED and determination_result['warnings']:
            recommendations.append("Review genuine self-employment: ensure business risk, true substitution rights, multiple clients")

        return recommendations
