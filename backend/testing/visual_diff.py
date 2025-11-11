"""
Visual Diff Tool for Corrections

Provides visual comparison of documents before and after corrections,
with highlighting of changes, additions, and deletions.

Features:
- Side-by-side comparison
- Inline diff with color coding
- HTML output for browser viewing
- Text-based console output
- Change statistics
"""

import difflib
from typing import List, Tuple, Dict, Optional
from enum import Enum


class DiffFormat(Enum):
    """Output format for diffs."""
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"


class VisualDiffer:
    """
    Creates visual diffs of document corrections.

    Usage:
        differ = VisualDiffer()
        html_diff = differ.create_diff(original, corrected, format=DiffFormat.HTML)
        print(html_diff)
    """

    def __init__(self):
        self.differ = difflib.Differ()
        self.html_differ = difflib.HtmlDiff()

    def create_diff(
        self,
        original: str,
        corrected: str,
        format: DiffFormat = DiffFormat.TEXT,
        context_lines: int = 3
    ) -> str:
        """
        Create visual diff in specified format.

        Args:
            original: Original text
            corrected: Corrected text
            format: Output format (TEXT, HTML, MARKDOWN, JSON)
            context_lines: Number of context lines to show

        Returns:
            Formatted diff string
        """
        if format == DiffFormat.TEXT:
            return self._create_text_diff(original, corrected, context_lines)
        elif format == DiffFormat.HTML:
            return self._create_html_diff(original, corrected)
        elif format == DiffFormat.MARKDOWN:
            return self._create_markdown_diff(original, corrected, context_lines)
        elif format == DiffFormat.JSON:
            return self._create_json_diff(original, corrected)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _create_text_diff(self, original: str, corrected: str, context_lines: int) -> str:
        """Create text-based diff with ANSI color codes (for terminal)."""
        original_lines = original.splitlines(keepends=True)
        corrected_lines = corrected.splitlines(keepends=True)

        # Use unified diff for cleaner output
        diff = difflib.unified_diff(
            original_lines,
            corrected_lines,
            fromfile='Original',
            tofile='Corrected',
            lineterm='',
            n=context_lines
        )

        # Add color codes for terminal output
        colored_diff = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                colored_diff.append(f"\033[32m{line}\033[0m")  # Green for additions
            elif line.startswith('-') and not line.startswith('---'):
                colored_diff.append(f"\033[31m{line}\033[0m")  # Red for deletions
            elif line.startswith('@@'):
                colored_diff.append(f"\033[36m{line}\033[0m")  # Cyan for location
            else:
                colored_diff.append(line)

        return '\n'.join(colored_diff)

    def _create_html_diff(self, original: str, corrected: str) -> str:
        """Create HTML side-by-side diff."""
        original_lines = original.splitlines()
        corrected_lines = corrected.splitlines()

        html_diff = self.html_differ.make_file(
            original_lines,
            corrected_lines,
            fromdesc='Original Document',
            todesc='Corrected Document',
            context=True,
            numlines=3
        )

        return html_diff

    def _create_markdown_diff(self, original: str, corrected: str, context_lines: int) -> str:
        """Create Markdown-formatted diff."""
        original_lines = original.splitlines(keepends=True)
        corrected_lines = corrected.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            corrected_lines,
            fromfile='Original',
            tofile='Corrected',
            lineterm='',
            n=context_lines
        )

        markdown_diff = ["# Document Correction Diff\n"]
        markdown_diff.append("```diff")
        markdown_diff.extend(diff)
        markdown_diff.append("```")

        return '\n'.join(markdown_diff)

    def _create_json_diff(self, original: str, corrected: str) -> str:
        """Create JSON representation of changes."""
        import json

        original_lines = original.splitlines()
        corrected_lines = corrected.splitlines()

        # Get sequence matcher for detailed comparison
        matcher = difflib.SequenceMatcher(None, original, corrected)

        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            change = {
                "type": tag,
                "original_start": i1,
                "original_end": i2,
                "corrected_start": j1,
                "corrected_end": j2,
                "original_text": original[i1:i2],
                "corrected_text": corrected[j1:j2]
            }
            changes.append(change)

        result = {
            "original_length": len(original),
            "corrected_length": len(corrected),
            "changes": changes
        }

        return json.dumps(result, indent=2)

    def get_change_statistics(self, original: str, corrected: str) -> Dict:
        """
        Get statistics about changes between original and corrected.

        Returns:
            Dictionary with change statistics
        """
        matcher = difflib.SequenceMatcher(None, original, corrected)

        stats = {
            "similarity_ratio": matcher.ratio(),
            "additions": 0,
            "deletions": 0,
            "replacements": 0,
            "unchanged_chars": 0,
            "total_changes": 0
        }

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                stats['replacements'] += 1
                stats['total_changes'] += 1
            elif tag == 'delete':
                stats['deletions'] += 1
                stats['total_changes'] += 1
            elif tag == 'insert':
                stats['additions'] += 1
                stats['total_changes'] += 1
            elif tag == 'equal':
                stats['unchanged_chars'] += (i2 - i1)

        return stats

    def create_inline_diff(self, original: str, corrected: str) -> str:
        """
        Create inline diff showing changes within text.

        Returns:
            String with inline annotations like:
            "This is [-original-] {+corrected+} text"
        """
        matcher = difflib.SequenceMatcher(None, original, corrected)

        result = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                result.append(f"[-{original[i1:i2]}-]")
                result.append(f"{{+{corrected[j1:j2]}+}}")
            elif tag == 'delete':
                result.append(f"[-{original[i1:i2]}-]")
            elif tag == 'insert':
                result.append(f"{{+{corrected[j1:j2]}+}}")
            elif tag == 'equal':
                result.append(original[i1:i2])

        return ''.join(result)

    def highlight_corrections(
        self,
        original: str,
        corrected: str,
        correction_metadata: List[Dict]
    ) -> str:
        """
        Create HTML with corrections highlighted and annotated.

        Args:
            original: Original text
            corrected: Corrected text
            correction_metadata: List of correction metadata with locations

        Returns:
            HTML string with highlighted corrections
        """
        html = ['<html><head>']
        html.append('<style>')
        html.append('''
            body { font-family: Arial, sans-serif; margin: 20px; }
            .correction { background-color: #ffffcc; border-bottom: 2px solid #ffcc00; }
            .correction:hover { background-color: #ffff99; cursor: help; }
            .metadata { display: none; position: absolute; background: #333; color: #fff;
                       padding: 5px; border-radius: 3px; font-size: 12px; }
            .correction:hover .metadata { display: block; }
            h2 { color: #333; }
            .container { display: flex; gap: 20px; }
            .column { flex: 1; }
            .original { background: #ffe6e6; padding: 10px; }
            .corrected { background: #e6ffe6; padding: 10px; }
        ''')
        html.append('</style></head><body>')

        html.append('<h1>Document Correction Visualization</h1>')

        html.append('<div class="container">')

        # Original column
        html.append('<div class="column"><h2>Original</h2>')
        html.append(f'<div class="original"><pre>{self._escape_html(original)}</pre></div>')
        html.append('</div>')

        # Corrected column with highlights
        html.append('<div class="column"><h2>Corrected</h2>')
        html.append('<div class="corrected">')
        html.append(f'<pre>{self._escape_html(corrected)}</pre>')
        html.append('</div></div>')

        html.append('</div>')

        # Corrections summary
        html.append('<h2>Corrections Applied</h2>')
        html.append('<ul>')
        for correction in correction_metadata:
            gate_id = correction.get('gate_id', 'unknown')
            strategy = correction.get('strategy', 'unknown')
            html.append(f'<li><strong>{gate_id}</strong> - Strategy: {strategy}</li>')
        html.append('</ul>')

        html.append('</body></html>')

        return ''.join(html)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


class DiffSummarizer:
    """
    Summarizes differences between documents.
    """

    @staticmethod
    def summarize_changes(original: str, corrected: str) -> Dict:
        """
        Create human-readable summary of changes.

        Returns:
            Dictionary with summary information
        """
        matcher = difflib.SequenceMatcher(None, original, corrected)

        original_lines = original.splitlines()
        corrected_lines = corrected.splitlines()

        summary = {
            "similarity_percent": matcher.ratio() * 100,
            "original_length": len(original),
            "corrected_length": len(corrected),
            "length_change": len(corrected) - len(original),
            "original_lines": len(original_lines),
            "corrected_lines": len(corrected_lines),
            "lines_changed": 0,
            "characters_added": 0,
            "characters_removed": 0,
            "major_change": False
        }

        # Count line changes
        line_matcher = difflib.SequenceMatcher(None, original_lines, corrected_lines)
        for tag, _, _, _, _ in line_matcher.get_opcodes():
            if tag in ['replace', 'delete', 'insert']:
                summary['lines_changed'] += 1

        # Count character changes
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                summary['characters_added'] += (j2 - j1)
            elif tag == 'delete':
                summary['characters_removed'] += (i2 - i1)
            elif tag == 'replace':
                summary['characters_removed'] += (i2 - i1)
                summary['characters_added'] += (j2 - j1)

        # Determine if major change (>30% different)
        if matcher.ratio() < 0.7:
            summary['major_change'] = True

        return summary

    @staticmethod
    def get_change_description(original: str, corrected: str) -> str:
        """
        Get human-readable description of changes.

        Returns:
            String description like "Minor changes: 3 additions, 2 deletions"
        """
        summary = DiffSummarizer.summarize_changes(original, corrected)

        if summary['similarity_percent'] == 100:
            return "No changes"

        change_type = "Major changes" if summary['major_change'] else "Minor changes"

        parts = [change_type]

        if summary['characters_added'] > 0:
            parts.append(f"{summary['characters_added']} characters added")

        if summary['characters_removed'] > 0:
            parts.append(f"{summary['characters_removed']} characters removed")

        parts.append(f"({summary['similarity_percent']:.1f}% similar)")

        return ": ".join(parts[:1]) + " - " + ", ".join(parts[1:])


# Convenience functions for quick usage

def quick_text_diff(original: str, corrected: str) -> str:
    """Quick text diff for terminal output."""
    differ = VisualDiffer()
    return differ.create_diff(original, corrected, DiffFormat.TEXT)


def quick_html_diff(original: str, corrected: str, output_file: Optional[str] = None) -> str:
    """
    Quick HTML diff, optionally save to file.

    Args:
        original: Original text
        corrected: Corrected text
        output_file: Optional path to save HTML to

    Returns:
        HTML string
    """
    differ = VisualDiffer()
    html = differ.create_diff(original, corrected, DiffFormat.HTML)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

    return html


def get_change_summary(original: str, corrected: str) -> str:
    """Get quick change summary."""
    return DiffSummarizer.get_change_description(original, corrected)
