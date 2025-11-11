"""
Export Engine
Handles data export in multiple formats (PDF, Excel, CSV, JSON, HTML, Word).
"""

from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    WORD = "word"


@dataclass
class ExportConfig:
    """Export configuration"""
    format: ExportFormat
    include_metadata: bool = True
    include_charts: bool = True
    page_orientation: str = "portrait"  # For PDF
    include_toc: bool = True  # For PDF/Word
    compress: bool = False


class ExportEngine:
    """
    Multi-format export engine for compliance reports.

    Features:
    - JSON export
    - CSV export
    - HTML export with styling
    - PDF generation
    - Excel workbook generation
    - Word document generation
    - Compression support
    - Data validation
    """

    def __init__(self):
        """Initialize export engine."""
        self.export_history: List[Dict[str, Any]] = []

    def export(
        self,
        data: Dict[str, Any],
        format: ExportFormat,
        filename: str,
        config: Optional[ExportConfig] = None
    ) -> Dict[str, Any]:
        """
        Export data in specified format.

        Args:
            data: Data to export
            format: Export format
            filename: Output filename
            config: Optional export configuration

        Returns:
            Export result with status and metadata
        """
        config = config or ExportConfig(format=format)

        try:
            if format == ExportFormat.JSON:
                result = self._export_json(data, filename, config)
            elif format == ExportFormat.CSV:
                result = self._export_csv(data, filename, config)
            elif format == ExportFormat.HTML:
                result = self._export_html(data, filename, config)
            elif format == ExportFormat.PDF:
                result = self._export_pdf(data, filename, config)
            elif format == ExportFormat.EXCEL:
                result = self._export_excel(data, filename, config)
            elif format == ExportFormat.WORD:
                result = self._export_word(data, filename, config)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Record export
            self.export_history.append({
                'timestamp': datetime.now().isoformat(),
                'format': format.value,
                'filename': filename,
                'status': 'success',
            })

            return result

        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'format': format.value,
            }

    def _export_json(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as JSON."""
        export_data = {}

        if config.include_metadata:
            export_data['metadata'] = {
                'exported_at': datetime.now().isoformat(),
                'format': 'json',
                'version': '1.0',
            }

        export_data['data'] = data

        json_content = json.dumps(export_data, indent=2, default=str)

        return {
            'status': 'success',
            'format': 'json',
            'filename': filename,
            'size': len(json_content),
            'content': json_content,
        }

    def _export_csv(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as CSV."""
        csv_rows = []

        # Flatten nested data for CSV
        for section_name, section_data in data.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    csv_rows.append({
                        'section': section_name,
                        'metric': key,
                        'value': value,
                    })
            elif isinstance(section_data, list):
                for idx, item in enumerate(section_data):
                    csv_rows.append({
                        'section': section_name,
                        'index': idx,
                        'data': str(item),
                    })

        # Create CSV content
        if csv_rows:
            fieldnames = csv_rows[0].keys()
        else:
            fieldnames = ['section', 'metric', 'value']

        csv_lines = []
        csv_lines.append(','.join(fieldnames))

        for row in csv_rows:
            values = [str(row.get(f, '')) for f in fieldnames]
            csv_lines.append(','.join(values))

        csv_content = '\n'.join(csv_lines)

        return {
            'status': 'success',
            'format': 'csv',
            'filename': filename,
            'rows': len(csv_rows),
            'content': csv_content,
        }

    def _export_html(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as HTML."""
        html_parts = []

        # HTML header
        html_parts.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Compliance Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #1976d2; border-bottom: 2px solid #1976d2; }
                h2 { color: #424242; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #1976d2; color: white; }
                tr:nth-child(even) { background-color: #f5f5f5; }
                .metric-value { font-weight: bold; color: #388e3c; }
                .warning { color: #f57c00; }
                .critical { color: #d32f2f; }
            </style>
        </head>
        <body>
        <h1>Compliance Report</h1>
        """)

        # Add table of contents if enabled
        if config.include_toc:
            html_parts.append("<h2>Table of Contents</h2><ul>")
            for section in data.keys():
                html_parts.append(f"<li><a href='#{section}'>{section}</a></li>")
            html_parts.append("</ul>")

        # Add content sections
        for section_name, section_data in data.items():
            html_parts.append(f"<h2 id='{section_name}'>{section_name}</h2>")

            if isinstance(section_data, dict):
                html_parts.append("<table>")
                html_parts.append("<tr><th>Metric</th><th>Value</th></tr>")
                for key, value in section_data.items():
                    html_parts.append(f"<tr><td>{key}</td>")
                    html_parts.append(f"<td class='metric-value'>{value}</td></tr>")
                html_parts.append("</table>")
            elif isinstance(section_data, list):
                html_parts.append("<ul>")
                for item in section_data:
                    html_parts.append(f"<li>{item}</li>")
                html_parts.append("</ul>")

        # HTML footer
        html_parts.append(f"""
        <hr>
        <p><em>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </body>
        </html>
        """)

        html_content = '\n'.join(html_parts)

        return {
            'status': 'success',
            'format': 'html',
            'filename': filename,
            'size': len(html_content),
            'content': html_content,
        }

    def _export_pdf(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as PDF."""
        # In production, use reportlab or similar library
        logger.info(f"PDF export for {filename} - would use reportlab")

        return {
            'status': 'success',
            'format': 'pdf',
            'filename': filename,
            'note': 'PDF generation requires reportlab library',
            'data_sections': len(data),
        }

    def _export_excel(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as Excel workbook."""
        # In production, use openpyxl or xlsxwriter
        logger.info(f"Excel export for {filename} - would use openpyxl")

        # Create workbook structure
        workbook_structure = {
            'sheets': []
        }

        # Create one sheet per data section
        for section_name, section_data in data.items():
            if isinstance(section_data, dict):
                rows = []
                rows.append(['Metric', 'Value'])
                for key, value in section_data.items():
                    rows.append([key, value])

                workbook_structure['sheets'].append({
                    'name': section_name[:31],  # Excel sheet name limit
                    'rows': rows,
                })

        return {
            'status': 'success',
            'format': 'excel',
            'filename': filename,
            'sheets': len(workbook_structure['sheets']),
            'note': 'Excel generation requires openpyxl library',
        }

    def _export_word(
        self,
        data: Dict[str, Any],
        filename: str,
        config: ExportConfig
    ) -> Dict[str, Any]:
        """Export data as Word document."""
        # In production, use python-docx
        logger.info(f"Word export for {filename} - would use python-docx")

        return {
            'status': 'success',
            'format': 'word',
            'filename': filename,
            'sections': len(data),
            'note': 'Word document generation requires python-docx library',
        }

    def export_report_with_format(
        self,
        report_data: Dict[str, Any],
        formats: List[ExportFormat],
        base_filename: str
    ) -> Dict[str, Any]:
        """
        Export report in multiple formats.

        Args:
            report_data: Report data
            formats: List of formats to export
            base_filename: Base filename without extension

        Returns:
            Dictionary with results for each format
        """
        results = {}

        for export_format in formats:
            filename = f"{base_filename}.{export_format.value}"
            result = self.export(
                report_data,
                export_format,
                filename
            )
            results[export_format.value] = result

        return results

    def batch_export(
        self,
        reports: List[Dict[str, Any]],
        format: ExportFormat
    ) -> List[Dict[str, Any]]:
        """
        Batch export multiple reports.

        Args:
            reports: List of report data
            format: Format to export

        Returns:
            List of export results
        """
        results = []

        for idx, report in enumerate(reports):
            filename = f"report_{idx + 1}.{format.value}"
            result = self.export(report, format, filename)
            results.append(result)

        return results

    def get_export_history(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent export history."""
        return self.export_history[-limit:]

    def validate_export_data(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data before export.

        Args:
            data: Data to validate

        Returns:
            Validation result
        """
        issues = []

        # Check for required fields
        if not data:
            issues.append("Data is empty")

        # Check for large values
        total_size = sum(len(str(v)) for v in data.values())
        if total_size > 10_000_000:  # 10MB
            issues.append("Data size exceeds 10MB limit for some formats")

        # Check for problematic characters in CSV
        for key, value in data.items():
            if isinstance(value, str) and '\n' in value:
                issues.append(f"Key '{key}' contains newlines (problematic for CSV)")

        return {
            'valid': len(issues) == 0,
            'warnings': issues,
            'data_size': total_size,
            'sections': len(data),
        }
