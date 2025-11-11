"""
Obligation Calendar - Tracks compliance deadlines and obligations
Generates calendars of regulatory deadlines, reporting requirements, and reviews.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceObligation:
    """Represents a compliance obligation."""
    id: str
    module_id: str
    title: str
    description: str
    due_date: datetime
    frequency: str  # 'one-time', 'daily', 'weekly', 'monthly', 'quarterly', 'annually'
    priority: str  # 'critical', 'high', 'medium', 'low'
    responsible_party: str
    estimated_hours: int
    status: str = 'pending'  # 'pending', 'in_progress', 'completed', 'overdue'


class ObligationCalendar:
    """
    Compliance obligation calendar and tracking system.
    
    Features:
    - Track compliance deadlines
    - Recurring obligation management
    - Priority-based scheduling
    - Reminder generation
    - Workload balancing
    """
    
    def __init__(self):
        self._initialize_obligations()
    
    def _initialize_obligations(self):
        """Initialize standard compliance obligations."""
        self.standard_obligations = {
            'gdpr_uk': [
                {
                    'title': 'GDPR Annual Review',
                    'description': 'Annual review of data processing activities and privacy policies',
                    'frequency': 'annually',
                    'priority': 'high',
                    'responsible_party': 'Data Protection Officer',
                    'estimated_hours': 40,
                    'month': 1  # January
                },
                {
                    'title': 'Data Protection Impact Assessment Review',
                    'description': 'Review and update DPIAs for high-risk processing',
                    'frequency': 'quarterly',
                    'priority': 'high',
                    'responsible_party': 'Compliance Team',
                    'estimated_hours': 16
                },
                {
                    'title': 'Staff Privacy Training',
                    'description': 'Annual data protection training for all staff',
                    'frequency': 'annually',
                    'priority': 'medium',
                    'responsible_party': 'HR/Training',
                    'estimated_hours': 20,
                    'month': 3  # March
                }
            ],
            'fca_uk': [
                {
                    'title': 'Regulatory Return Submission',
                    'description': 'Submit required regulatory returns to FCA',
                    'frequency': 'quarterly',
                    'priority': 'critical',
                    'responsible_party': 'Finance/Compliance',
                    'estimated_hours': 24
                },
                {
                    'title': 'SMCR Certification',
                    'description': 'Annual certification of Senior Managers',
                    'frequency': 'annually',
                    'priority': 'critical',
                    'responsible_party': 'HR/Compliance',
                    'estimated_hours': 32,
                    'month': 12  # December
                },
                {
                    'title': 'Consumer Duty Review',
                    'description': 'Review fair value assessments and customer outcomes',
                    'frequency': 'annually',
                    'priority': 'high',
                    'responsible_party': 'Compliance Team',
                    'estimated_hours': 40,
                    'month': 6  # June
                }
            ],
            'tax_uk': [
                {
                    'title': 'VAT Return Submission',
                    'description': 'Submit quarterly VAT return to HMRC',
                    'frequency': 'quarterly',
                    'priority': 'critical',
                    'responsible_party': 'Finance Team',
                    'estimated_hours': 8
                },
                {
                    'title': 'Corporation Tax Return',
                    'description': 'File annual corporation tax return',
                    'frequency': 'annually',
                    'priority': 'critical',
                    'responsible_party': 'Finance Team',
                    'estimated_hours': 40,
                    'month': 12  # December (after year-end)
                }
            ],
            'pci_dss': [
                {
                    'title': 'PCI DSS Quarterly Scan',
                    'description': 'Quarterly vulnerability scan by ASV',
                    'frequency': 'quarterly',
                    'priority': 'critical',
                    'responsible_party': 'IT Security',
                    'estimated_hours': 12
                },
                {
                    'title': 'PCI DSS Annual Assessment',
                    'description': 'Annual PCI DSS compliance assessment and AOC',
                    'frequency': 'annually',
                    'priority': 'critical',
                    'responsible_party': 'IT Security/QSA',
                    'estimated_hours': 80,
                    'month': 11  # November
                }
            ],
            'uk_employment': [
                {
                    'title': 'Employment Law Update Review',
                    'description': 'Review changes in employment legislation',
                    'frequency': 'quarterly',
                    'priority': 'medium',
                    'responsible_party': 'HR Team',
                    'estimated_hours': 8
                },
                {
                    'title': 'Employee Handbook Update',
                    'description': 'Annual review and update of employee handbook',
                    'frequency': 'annually',
                    'priority': 'medium',
                    'responsible_party': 'HR Team',
                    'estimated_hours': 24,
                    'month': 9  # September
                }
            ]
        }
    
    def generate(self, module_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate compliance obligation calendar.
        
        Args:
            module_results: Compliance results for all modules
        
        Returns:
            Calendar with all obligations and deadlines
        """
        logger.info("Generating compliance obligation calendar")
        
        obligations = []
        current_date = datetime.now()
        
        # Generate obligations for each active module
        for module_id in module_results.keys():
            if module_id in self.standard_obligations:
                module_obligations = self._generate_module_obligations(
                    module_id,
                    self.standard_obligations[module_id],
                    current_date
                )
                obligations.extend(module_obligations)
        
        # Sort by due date
        obligations.sort(key=lambda x: x['due_date'])
        
        # Generate calendar views
        upcoming_30_days = [o for o in obligations if self._parse_date(o['due_date']) <= current_date + timedelta(days=30)]
        upcoming_90_days = [o for o in obligations if self._parse_date(o['due_date']) <= current_date + timedelta(days=90)]
        
        # Generate monthly breakdown
        monthly_breakdown = self._generate_monthly_breakdown(obligations, current_date)
        
        # Identify overdue obligations
        overdue = [o for o in obligations if self._parse_date(o['due_date']) < current_date and o['status'] == 'pending']
        
        # Calculate workload
        workload = self._calculate_workload(obligations)
        
        return {
            'generated_at': current_date.isoformat(),
            'total_obligations': len(obligations),
            'all_obligations': obligations,
            'upcoming_30_days': upcoming_30_days,
            'upcoming_90_days': upcoming_90_days,
            'overdue': overdue,
            'monthly_breakdown': monthly_breakdown,
            'workload_analysis': workload,
            'critical_deadlines': [o for o in obligations if o['priority'] == 'critical'],
            'reminders': self._generate_reminders(upcoming_30_days)
        }
    
    def _generate_module_obligations(
        self,
        module_id: str,
        obligations_template: List[Dict[str, Any]],
        start_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate obligations for a specific module."""
        obligations = []
        
        for template in obligations_template:
            # Generate next due date based on frequency
            due_date = self._calculate_next_due_date(
                template['frequency'],
                start_date,
                template.get('month')
            )
            
            obligation = {
                'id': f"{module_id}_{template['title'].replace(' ', '_').lower()}",
                'module_id': module_id,
                'title': template['title'],
                'description': template['description'],
                'due_date': due_date.isoformat(),
                'frequency': template['frequency'],
                'priority': template['priority'],
                'responsible_party': template['responsible_party'],
                'estimated_hours': template['estimated_hours'],
                'status': 'pending'
            }
            obligations.append(obligation)
            
            # For recurring obligations, add future instances
            if template['frequency'] in ['quarterly', 'annually']:
                future_date = self._calculate_next_due_date(
                    template['frequency'],
                    due_date,
                    template.get('month')
                )
                future_obligation = obligation.copy()
                future_obligation['id'] = f"{obligation['id']}_next"
                future_obligation['due_date'] = future_date.isoformat()
                obligations.append(future_obligation)
        
        return obligations
    
    def _calculate_next_due_date(
        self,
        frequency: str,
        start_date: datetime,
        preferred_month: int = None
    ) -> datetime:
        """Calculate next due date based on frequency."""
        if frequency == 'daily':
            return start_date + timedelta(days=1)
        elif frequency == 'weekly':
            return start_date + timedelta(weeks=1)
        elif frequency == 'monthly':
            # Next month, same day
            if start_date.month == 12:
                return start_date.replace(year=start_date.year + 1, month=1)
            else:
                return start_date.replace(month=start_date.month + 1)
        elif frequency == 'quarterly':
            # Next quarter
            current_quarter = (start_date.month - 1) // 3
            next_quarter = (current_quarter + 1) % 4
            next_quarter_month = next_quarter * 3 + 1
            
            if next_quarter_month <= start_date.month:
                # Next year
                return start_date.replace(year=start_date.year + 1, month=next_quarter_month, day=1)
            else:
                return start_date.replace(month=next_quarter_month, day=1)
        elif frequency == 'annually':
            # Next year, preferred month if specified
            if preferred_month:
                if preferred_month <= start_date.month:
                    # Next year
                    return start_date.replace(year=start_date.year + 1, month=preferred_month, day=1)
                else:
                    return start_date.replace(month=preferred_month, day=1)
            else:
                return start_date.replace(year=start_date.year + 1)
        else:  # one-time
            return start_date + timedelta(days=30)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO format date string."""
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    def _generate_monthly_breakdown(
        self,
        obligations: List[Dict[str, Any]],
        start_date: datetime
    ) -> Dict[str, Any]:
        """Generate monthly breakdown of obligations."""
        breakdown = {}
        
        for i in range(12):
            month_date = start_date + timedelta(days=30 * i)
            month_key = month_date.strftime('%Y-%m')
            
            month_obligations = [
                o for o in obligations
                if self._parse_date(o['due_date']).strftime('%Y-%m') == month_key
            ]
            
            breakdown[month_key] = {
                'month': month_date.strftime('%B %Y'),
                'total_obligations': len(month_obligations),
                'critical': len([o for o in month_obligations if o['priority'] == 'critical']),
                'high': len([o for o in month_obligations if o['priority'] == 'high']),
                'total_hours': sum(o['estimated_hours'] for o in month_obligations),
                'obligations': month_obligations
            }
        
        return breakdown
    
    def _calculate_workload(self, obligations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate workload distribution."""
        total_hours = sum(o['estimated_hours'] for o in obligations)
        
        by_priority = {
            'critical': sum(o['estimated_hours'] for o in obligations if o['priority'] == 'critical'),
            'high': sum(o['estimated_hours'] for o in obligations if o['priority'] == 'high'),
            'medium': sum(o['estimated_hours'] for o in obligations if o['priority'] == 'medium'),
            'low': sum(o['estimated_hours'] for o in obligations if o['priority'] == 'low')
        }
        
        by_responsible_party = {}
        for obligation in obligations:
            party = obligation['responsible_party']
            if party not in by_responsible_party:
                by_responsible_party[party] = 0
            by_responsible_party[party] += obligation['estimated_hours']
        
        return {
            'total_hours': total_hours,
            'average_hours_per_month': round(total_hours / 12, 1),
            'by_priority': by_priority,
            'by_responsible_party': by_responsible_party,
            'peak_month': max(by_responsible_party.items(), key=lambda x: x[1])[0] if by_responsible_party else 'N/A'
        }
    
    def _generate_reminders(self, upcoming_obligations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate reminders for upcoming obligations."""
        reminders = []
        current_date = datetime.now()
        
        for obligation in upcoming_obligations:
            due_date = self._parse_date(obligation['due_date'])
            days_until_due = (due_date - current_date).days
            
            if days_until_due <= 7:
                urgency = 'urgent'
            elif days_until_due <= 14:
                urgency = 'high'
            else:
                urgency = 'normal'
            
            reminders.append({
                'obligation_id': obligation['id'],
                'title': obligation['title'],
                'due_in_days': days_until_due,
                'urgency': urgency,
                'message': f"{obligation['title']} due in {days_until_due} days - {obligation['responsible_party']}"
            })
        
        return reminders
