"""
Change Monitor - Monitors regulatory changes and updates
Tracks regulatory updates, amendments, and new requirements across jurisdictions.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ChangeMonitor:
    """
    Regulatory change monitoring system.
    
    Features:
    - Track regulatory updates by jurisdiction
    - Alert on relevant changes
    - Provide impact assessments
    - Generate change summaries
    """
    
    def __init__(self):
        self._initialize_monitoring_sources()
    
    def _initialize_monitoring_sources(self):
        """Initialize regulatory monitoring sources."""
        self.monitoring_sources = {
            'UK': {
                'ICO': 'https://ico.org.uk',
                'FCA': 'https://www.fca.org.uk',
                'HMRC': 'https://www.gov.uk/hmrc',
                'CQC': 'https://www.cqc.org.uk'
            },
            'EU': {
                'EDPB': 'https://edpb.europa.eu',
                'ESMA': 'https://www.esma.europa.eu'
            },
            'US': {
                'HHS': 'https://www.hhs.gov',
                'SEC': 'https://www.sec.gov',
                'PCAOB': 'https://pcaobus.org'
            }
        }
        
        # Simulated recent changes (in production, would fetch from APIs)
        self.recent_changes = self._get_simulated_changes()
    
    def _get_simulated_changes(self) -> List[Dict[str, Any]]:
        """Get simulated regulatory changes for demonstration."""
        return [
            {
                'id': 'ICO-2024-001',
                'jurisdiction': 'UK',
                'authority': 'ICO',
                'date': (datetime.now() - timedelta(days=15)).isoformat(),
                'title': 'Updated guidance on AI and automated decision-making',
                'description': 'New requirements for transparency in AI systems processing personal data',
                'affected_modules': ['gdpr_uk', 'gdpr_advanced'],
                'impact': 'high',
                'action_required': 'Review AI systems for GDPR compliance',
                'deadline': (datetime.now() + timedelta(days=90)).isoformat()
            },
            {
                'id': 'FCA-2024-002',
                'jurisdiction': 'UK',
                'authority': 'FCA',
                'date': (datetime.now() - timedelta(days=30)).isoformat(),
                'title': 'Consumer Duty implementation updates',
                'description': 'Additional guidance on fair value assessments',
                'affected_modules': ['fca_uk', 'fca_advanced'],
                'impact': 'medium',
                'action_required': 'Update fair value assessment processes',
                'deadline': (datetime.now() + timedelta(days=120)).isoformat()
            },
            {
                'id': 'HMRC-2024-001',
                'jurisdiction': 'UK',
                'authority': 'HMRC',
                'date': (datetime.now() - timedelta(days=45)).isoformat(),
                'title': 'Making Tax Digital expansion',
                'description': 'MTD extended to smaller businesses',
                'affected_modules': ['tax_uk'],
                'impact': 'medium',
                'action_required': 'Assess MTD readiness for smaller entities',
                'deadline': (datetime.now() + timedelta(days=180)).isoformat()
            }
        ]
    
    def check_updates(self, jurisdictions: List[str]) -> Dict[str, Any]:
        """
        Check for regulatory updates in specified jurisdictions.
        
        Args:
            jurisdictions: List of jurisdictions to monitor (e.g., ['UK', 'EU', 'US'])
        
        Returns:
            Dictionary of updates and alerts
        """
        logger.info(f"Checking regulatory updates for {jurisdictions}")
        
        relevant_changes = [
            change for change in self.recent_changes
            if change['jurisdiction'] in jurisdictions
        ]
        
        # Categorize by impact
        high_impact = [c for c in relevant_changes if c['impact'] == 'high']
        medium_impact = [c for c in relevant_changes if c['impact'] == 'medium']
        low_impact = [c for c in relevant_changes if c['impact'] == 'low']
        
        # Identify urgent changes (deadline < 30 days)
        urgent_changes = [
            c for c in relevant_changes
            if datetime.fromisoformat(c['deadline']) < datetime.now() + timedelta(days=30)
        ]
        
        return {
            'last_checked': datetime.now().isoformat(),
            'jurisdictions_monitored': jurisdictions,
            'total_changes': len(relevant_changes),
            'changes_by_impact': {
                'high': len(high_impact),
                'medium': len(medium_impact),
                'low': len(low_impact)
            },
            'urgent_changes': urgent_changes,
            'all_changes': relevant_changes,
            'monitoring_sources': {j: self.monitoring_sources.get(j, {}) for j in jurisdictions},
            'recommendations': self._generate_change_recommendations(relevant_changes)
        }
    
    def _generate_change_recommendations(self, changes: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on regulatory changes."""
        recommendations = []
        
        if any(c['impact'] == 'high' for c in changes):
            recommendations.append(
                "HIGH PRIORITY: Review high-impact changes immediately and assess required actions"
            )
        
        urgent = [
            c for c in changes
            if datetime.fromisoformat(c['deadline']) < datetime.now() + timedelta(days=30)
        ]
        if urgent:
            recommendations.append(
                f"URGENT: {len(urgent)} changes have deadlines within 30 days"
            )
        
        if len(changes) > 5:
            recommendations.append(
                "Consider establishing a dedicated regulatory monitoring team"
            )
        
        recommendations.append(
            "Subscribe to regulatory authority newsletters for timely updates"
        )
        
        return recommendations
