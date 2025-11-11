"""
Email Integration

Send LOKI events and notifications via email.
Supports HTML formatting, attachments, and templating.
"""

import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseIntegration, IntegrationStatus


logger = logging.getLogger(__name__)


class EmailIntegration(BaseIntegration):
    """
    Email integration for LOKI

    Features:
    - Send emails to recipients
    - HTML email formatting
    - Attachments support
    - SMTP configuration
    - Email templating
    - Distribution lists
    """

    def __init__(
        self,
        name: str,
        smtp_host: str,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_address: str = 'noreply@loki.local',
        use_tls: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Email integration

        Args:
            name: Integration name
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (default: 587)
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            from_address: From address for emails
            use_tls: Use TLS for SMTP (default: True)
            config: Configuration options
        """
        credentials = {
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'from_address': from_address,
        }

        if smtp_username:
            credentials['smtp_username'] = smtp_username
        if smtp_password:
            credentials['smtp_password'] = smtp_password

        config = config or {}
        config.setdefault('use_tls', use_tls)
        config.setdefault('default_recipients', [])
        config.setdefault('include_attachments', False)
        config.setdefault('html_format', True)

        super().__init__(
            name=name,
            integration_type='email',
            credentials=credentials,
            config=config,
        )

    async def connect(self) -> bool:
        """Connect to SMTP server and validate credentials"""
        try:
            is_valid = await self.validate_credentials()
            if is_valid:
                self.status = IntegrationStatus.CONNECTED
                logger.info(f"Email integration connected: {self.name}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to connect Email integration: {str(e)}")
            self.status = IntegrationStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from SMTP server"""
        self.status = IntegrationStatus.DISCONNECTED
        logger.info(f"Email integration disconnected: {self.name}")
        return True

    async def validate_credentials(self) -> bool:
        """Validate SMTP connection and credentials"""
        try:
            smtp_host = self.credentials.get('smtp_host')
            smtp_port = self.credentials.get('smtp_port', 587)
            smtp_username = self.credentials.get('smtp_username')
            smtp_password = self.credentials.get('smtp_password')
            use_tls = self.config.get('use_tls', True)

            async with aiosmtplib.SMTP(
                hostname=smtp_host,
                port=smtp_port,
                use_tls=use_tls,
                timeout=10,
            ) as smtp:
                if smtp_username and smtp_password:
                    await smtp.login(smtp_username, smtp_password)

                return True

        except Exception as e:
            logger.error(f"Email credential validation failed: {str(e)}")
            return False

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message via email

        Args:
            message: Message payload with to_addresses and subject

        Returns:
            True if message sent successfully
        """
        try:
            to_addresses = message.get('to_addresses', self.config.get('default_recipients', []))
            if not to_addresses:
                logger.error("No recipient addresses provided")
                return False

            subject = message.get('subject', 'LOKI Notification')
            body = message.get('body', '')

            return await self.send_email(to_addresses, subject, body)

        except Exception as e:
            logger.error(f"Failed to send email message: {str(e)}")
            return False

    async def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        html: bool = True,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send an email

        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body
            html: Whether body is HTML format (default: True)
            attachments: Optional list of attachments

        Returns:
            True if email sent successfully
        """
        try:
            # Prepare message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.credentials.get('from_address', 'noreply@loki.local')
            msg['To'] = ', '.join(to_addresses)

            # Add body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))

            # Add attachments if enabled
            if self.config.get('include_attachments') and attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Send email
            smtp_host = self.credentials.get('smtp_host')
            smtp_port = self.credentials.get('smtp_port', 587)
            smtp_username = self.credentials.get('smtp_username')
            smtp_password = self.credentials.get('smtp_password')
            use_tls = self.config.get('use_tls', True)

            async with aiosmtplib.SMTP(
                hostname=smtp_host,
                port=smtp_port,
                use_tls=use_tls,
                timeout=30,
            ) as smtp:
                if smtp_username and smtp_password:
                    await smtp.login(smtp_username, smtp_password)

                await smtp.send_message(msg)

            self.last_event_at = datetime.utcnow()
            logger.info(f"Email sent to {', '.join(to_addresses)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    async def on_validation_completed(self, validation_data: Dict[str, Any]) -> bool:
        """Handle validation completion event"""
        subject = "Document Validation Completed"
        body = self._generate_html_body(
            title=subject,
            data=validation_data,
        )
        message = {
            'subject': subject,
            'body': body,
            'to_addresses': self.config.get('default_recipients', []),
        }
        return await self.send_message(message)

    async def on_compliance_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Handle compliance alert event"""
        subject = f"Compliance Alert: {alert_data.get('alert_type', 'Unknown')}"
        body = self._generate_html_body(
            title=subject,
            data=alert_data,
            alert_level=alert_data.get('alert_level'),
        )
        message = {
            'subject': subject,
            'body': body,
            'to_addresses': self.config.get('default_recipients', []),
        }
        return await self.send_message(message)

    async def on_batch_completed(self, batch_data: Dict[str, Any]) -> bool:
        """Handle batch completion event"""
        subject = f"Batch Completed: {batch_data.get('total_documents', 0)} documents"
        body = self._generate_html_body(
            title=subject,
            data=batch_data,
        )
        message = {
            'subject': subject,
            'body': body,
            'to_addresses': self.config.get('default_recipients', []),
        }
        return await self.send_message(message)

    def _generate_html_body(
        self,
        title: str,
        data: Dict[str, Any],
        alert_level: Optional[str] = None,
    ) -> str:
        """
        Generate HTML email body

        Args:
            title: Email title
            data: Data to display
            alert_level: Optional alert level for color coding

        Returns:
            HTML body string
        """
        color = self._get_alert_color(alert_level) if alert_level else '#0078D4'

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ border: 1px solid #ddd; padding: 20px; border-radius: 0 0 5px 5px; }}
                .field {{ margin: 10px 0; }}
                .field-name {{ font-weight: bold; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #999; border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">{title}</h1>
                    <p style="margin: 5px 0 0 0;">LOKI Interceptor</p>
                </div>
                <div class="content">
        """

        # Add data fields
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    html += f"""
                    <div class="field">
                        <span class="field-name">{key}:</span> {self._format_value(value)}
                    </div>
                    """

        html += f"""
                </div>
                <div class="footer">
                    Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | LOKI Interceptor
                </div>
            </div>
        </body>
        </html>
        """

        return html

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for email display"""
        if isinstance(value, bool):
            return '✓ Yes' if value else '✗ No'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value[:200]
        return str(value)[:200]

    @staticmethod
    def _get_alert_color(level: str) -> str:
        """Get alert color based on severity level"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745',
        }
        return colors.get(level, '#0078D4')

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """
        Add an attachment to email message

        Args:
            msg: Email message
            attachment: Attachment data with 'filename' and 'content'
        """
        from email.mime.base import MIMEBase
        from email import encoders

        filename = attachment.get('filename', 'attachment')
        content = attachment.get('content', b'')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
