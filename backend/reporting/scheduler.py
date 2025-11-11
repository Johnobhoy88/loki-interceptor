"""
Report Scheduler
Schedules and automates report generation and distribution.
"""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Frequency(str, Enum):
    """Report frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class DayOfWeek(str, Enum):
    """Days of week"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class ScheduleConfig:
    """Schedule configuration"""
    frequency: Frequency
    time_of_day: str = "09:00"  # HH:MM format
    day_of_week: Optional[DayOfWeek] = None  # For weekly
    day_of_month: Optional[int] = None  # For monthly (1-31)
    enabled: bool = True


@dataclass
class RecipientConfig:
    """Report recipient configuration"""
    recipient_type: str  # 'email', 'api_webhook', 'storage'
    recipient_address: str
    format_preference: str = 'pdf'
    include_attachments: bool = True


@dataclass
class ScheduledReport:
    """Scheduled report configuration"""
    schedule_id: str
    name: str
    description: str
    template_id: str
    schedule: ScheduleConfig
    recipients: List[RecipientConfig]
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    is_active: bool = True


class ReportScheduler:
    """
    Automated report scheduling and distribution.

    Features:
    - Flexible scheduling (daily, weekly, monthly, etc.)
    - Multiple recipients
    - Email distribution
    - API webhooks
    - Storage integration
    - Schedule history
    - Error handling and retry logic
    """

    def __init__(self):
        """Initialize report scheduler."""
        self.schedules: Dict[str, ScheduledReport] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.report_generator: Optional[Callable] = None

    def create_schedule(
        self,
        schedule_id: str,
        name: str,
        description: str,
        template_id: str,
        frequency: Frequency,
        time_of_day: str = "09:00",
        day_of_week: Optional[DayOfWeek] = None,
        day_of_month: Optional[int] = None,
        recipients: Optional[List[RecipientConfig]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ScheduledReport:
        """
        Create a scheduled report.

        Args:
            schedule_id: Unique schedule identifier
            name: Schedule name
            description: Schedule description
            template_id: Report template to use
            frequency: Report frequency
            time_of_day: Time to generate report (HH:MM)
            day_of_week: Day for weekly reports
            day_of_month: Day for monthly reports
            recipients: Report recipients
            parameters: Report parameters

        Returns:
            ScheduledReport
        """
        schedule = ScheduleConfig(
            frequency=frequency,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            day_of_month=day_of_month
        )

        scheduled_report = ScheduledReport(
            schedule_id=schedule_id,
            name=name,
            description=description,
            template_id=template_id,
            schedule=schedule,
            recipients=recipients or [],
            parameters=parameters or {},
            next_run=self._calculate_next_run(schedule)
        )

        self.schedules[schedule_id] = scheduled_report
        logger.info(f"Created schedule: {schedule_id}")

        return scheduled_report

    def add_recipient(
        self,
        schedule_id: str,
        recipient: RecipientConfig
    ) -> bool:
        """Add recipient to scheduled report."""
        if schedule_id not in self.schedules:
            return False

        self.schedules[schedule_id].recipients.append(recipient)
        return True

    def remove_recipient(
        self,
        schedule_id: str,
        recipient_address: str
    ) -> bool:
        """Remove recipient from scheduled report."""
        if schedule_id not in self.schedules:
            return False

        schedule = self.schedules[schedule_id]
        original_count = len(schedule.recipients)
        schedule.recipients = [
            r for r in schedule.recipients if r.recipient_address != recipient_address
        ]

        return len(schedule.recipients) < original_count

    def execute_schedule(
        self,
        schedule_id: str,
        report_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a scheduled report generation and distribution.

        Args:
            schedule_id: Schedule to execute
            report_data: Optional pre-generated report data

        Returns:
            Execution result
        """
        if schedule_id not in self.schedules:
            return {'status': 'failed', 'error': 'Schedule not found'}

        schedule = self.schedules[schedule_id]

        if not schedule.is_active:
            return {'status': 'skipped', 'reason': 'Schedule is disabled'}

        try:
            # Generate report if not provided
            if not report_data:
                report_data = self._generate_report(schedule)

            # Distribute to recipients
            distribution_results = self._distribute_report(
                schedule, report_data
            )

            # Update execution history
            execution = {
                'schedule_id': schedule_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'recipients_processed': len(distribution_results),
            }
            self.execution_history.append(execution)

            # Update last run and next run
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(schedule.schedule)

            logger.info(f"Schedule {schedule_id} executed successfully")

            return {
                'status': 'success',
                'schedule_id': schedule_id,
                'execution_id': len(self.execution_history),
                'distribution_results': distribution_results,
            }

        except Exception as e:
            logger.error(f"Schedule execution failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'schedule_id': schedule_id,
            }

    def _generate_report(self, schedule: ScheduledReport) -> Dict[str, Any]:
        """Generate report for schedule."""
        # In production, this would call the actual report generator
        return {
            'template_id': schedule.template_id,
            'generated_at': datetime.now().isoformat(),
            'parameters': schedule.parameters,
        }

    def _distribute_report(
        self,
        schedule: ScheduledReport,
        report_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Distribute report to recipients."""
        results = []

        for recipient in schedule.recipients:
            result = self._send_to_recipient(recipient, report_data)
            results.append({
                'recipient': recipient.recipient_address,
                'status': result['status'],
            })

        return results

    def _send_to_recipient(
        self,
        recipient: RecipientConfig,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send report to single recipient."""
        try:
            if recipient.recipient_type == 'email':
                return self._send_email(recipient, report_data)
            elif recipient.recipient_type == 'api_webhook':
                return self._send_webhook(recipient, report_data)
            elif recipient.recipient_type == 'storage':
                return self._save_to_storage(recipient, report_data)
            else:
                return {'status': 'failed', 'error': 'Unknown recipient type'}

        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def _send_email(
        self,
        recipient: RecipientConfig,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send report via email."""
        logger.info(f"Sending email to {recipient.recipient_address}")
        # In production, use email library (smtplib, etc.)
        return {
            'status': 'success',
            'method': 'email',
            'recipient': recipient.recipient_address,
        }

    def _send_webhook(
        self,
        recipient: RecipientConfig,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send report via webhook."""
        logger.info(f"Sending webhook to {recipient.recipient_address}")
        # In production, use requests library
        return {
            'status': 'success',
            'method': 'webhook',
            'recipient': recipient.recipient_address,
        }

    def _save_to_storage(
        self,
        recipient: RecipientConfig,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save report to storage."""
        logger.info(f"Saving to storage: {recipient.recipient_address}")
        # In production, use cloud storage SDK
        return {
            'status': 'success',
            'method': 'storage',
            'location': recipient.recipient_address,
        }

    def _calculate_next_run(self, schedule: ScheduleConfig) -> datetime:
        """Calculate next scheduled run time."""
        now = datetime.now()
        hour, minute = map(int, schedule.time_of_day.split(':'))
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if next_run <= now:
            # Schedule is in the past, move to next occurrence
            if schedule.frequency == Frequency.DAILY:
                next_run += timedelta(days=1)
            elif schedule.frequency == Frequency.WEEKLY:
                next_run += timedelta(weeks=1)
            elif schedule.frequency == Frequency.MONTHLY:
                # Move to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
            elif schedule.frequency == Frequency.QUARTERLY:
                next_run += timedelta(days=91)
            elif schedule.frequency == Frequency.ANNUALLY:
                next_run += timedelta(days=365)

        return next_run

    def get_schedule(self, schedule_id: str) -> Optional[ScheduledReport]:
        """Retrieve schedule configuration."""
        return self.schedules.get(schedule_id)

    def list_schedules(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """List all schedules."""
        schedules = list(self.schedules.values())

        if active_only:
            schedules = [s for s in schedules if s.is_active]

        return [
            {
                'id': s.schedule_id,
                'name': s.name,
                'frequency': s.schedule.frequency.value,
                'active': s.is_active,
                'next_run': s.next_run.isoformat() if s.next_run else None,
                'last_run': s.last_run.isoformat() if s.last_run else None,
            }
            for s in schedules
        ]

    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        if schedule_id not in self.schedules:
            return False

        self.schedules[schedule_id].is_active = True
        self.schedules[schedule_id].next_run = self._calculate_next_run(
            self.schedules[schedule_id].schedule
        )
        return True

    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        if schedule_id not in self.schedules:
            return False

        self.schedules[schedule_id].is_active = False
        return True

    def get_execution_history(
        self,
        schedule_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get schedule execution history."""
        history = self.execution_history

        if schedule_id:
            history = [e for e in history if e['schedule_id'] == schedule_id]

        return history[-limit:]

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return True

        return False
