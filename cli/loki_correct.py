#!/usr/bin/env python3
"""
LOKI Correct - Command-line correction tool

Features:
- Correct documents from command line
- Batch processing support
- Multiple export formats
- Progress tracking
- Interactive and non-interactive modes

Usage:
    loki_correct document.txt
    loki_correct --batch documents/
    loki_correct document.txt --format docx --output corrected.docx
    loki_correct --server http://localhost:8000 document.txt
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Optional, List
from datetime import datetime

try:
    import click
    import httpx
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    click = None
    httpx = None
    Console = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.correction_pipeline import CorrectionPipeline
from backend.core.batch_corrector import BatchCorrector
from backend.core.correction_exporter import CorrectionExporter


class LOKICorrectCLI:
    """LOKI Correct command-line interface"""

    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize CLI

        Args:
            server_url: API server URL (if using remote server)
        """
        self.server_url = server_url
        self.console = Console() if Console else None

    async def correct_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        export_format: str = "json",
        verbose: bool = False
    ):
        """
        Correct a single file

        Args:
            input_file: Input file path
            output_file: Output file path (optional)
            export_format: Export format
            verbose: Verbose output
        """
        # Read input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            self._error(f"Error reading file: {e}")
            return 1

        # Correct document
        if self.server_url:
            result = await self._correct_remote(text, export_format, verbose)
        else:
            result = await self._correct_local(text, export_format, verbose)

        if not result:
            return 1

        # Determine output file
        if not output_file:
            input_path = Path(input_file)
            output_file = f"{input_path.stem}_corrected{input_path.suffix}"

        # Export result
        try:
            await self._export_result(result, output_file, export_format)
            self._success(f"Corrected document saved to: {output_file}")

            # Print summary
            if verbose:
                self._print_summary(result)

            return 0

        except Exception as e:
            self._error(f"Error saving output: {e}")
            return 1

    async def correct_batch(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        export_format: str = "json",
        parallel: bool = True,
        verbose: bool = False
    ):
        """
        Correct multiple files in batch

        Args:
            input_dir: Input directory
            output_dir: Output directory
            export_format: Export format
            parallel: Process in parallel
            verbose: Verbose output
        """
        # Find all text files
        input_path = Path(input_dir)
        if not input_path.is_dir():
            self._error(f"Not a directory: {input_dir}")
            return 1

        text_files = list(input_path.glob("*.txt")) + list(input_path.glob("*.md"))

        if not text_files:
            self._error(f"No text files found in: {input_dir}")
            return 1

        self._info(f"Found {len(text_files)} files to process")

        # Create output directory
        if not output_dir:
            output_dir = f"{input_dir}_corrected"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # Prepare documents
        documents = []
        for file_path in text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.append({
                        'id': file_path.name,
                        'text': text,
                        'path': str(file_path)
                    })
            except Exception as e:
                self._warning(f"Error reading {file_path}: {e}")

        if not documents:
            self._error("No documents to process")
            return 1

        # Process batch
        if self.server_url:
            results = await self._correct_batch_remote(documents, export_format, verbose)
        else:
            results = await self._correct_batch_local(documents, parallel, export_format, verbose)

        if not results:
            return 1

        # Save results
        successful = 0
        failed = 0

        for doc_result in results.get('results', []):
            if doc_result.get('status') == 'success':
                try:
                    doc_id = doc_result['document_id']
                    output_file = output_path / f"{Path(doc_id).stem}_corrected{Path(doc_id).suffix}"

                    result = doc_result.get('result')
                    if result:
                        await self._export_result(result, str(output_file), export_format)
                        successful += 1
                except Exception as e:
                    self._warning(f"Error saving {doc_id}: {e}")
                    failed += 1
            else:
                failed += 1

        # Print summary
        self._success(f"Batch processing complete: {successful} successful, {failed} failed")

        if verbose and results.get('statistics'):
            self._print_batch_stats(results['statistics'])

        return 0 if failed == 0 else 1

    async def _correct_local(self, text: str, export_format: str, verbose: bool) -> Optional[dict]:
        """Correct document locally"""
        if verbose:
            self._info("Correcting document locally...")

        try:
            # Create pipeline
            pipeline = CorrectionPipeline(
                algorithm_version="2.0.0",
                enable_caching=True
            )

            # Execute correction
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Correcting document...", total=None)
                    result = await pipeline.execute(text=text)
                    progress.update(task, completed=True)
            else:
                result = await pipeline.execute(text=text)

            return result

        except Exception as e:
            self._error(f"Correction error: {e}")
            return None

    async def _correct_remote(self, text: str, export_format: str, verbose: bool) -> Optional[dict]:
        """Correct document using remote API"""
        if verbose:
            self._info(f"Correcting document via {self.server_url}...")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/v1/correct/advanced",
                    json={
                        "text": text,
                        "export_format": export_format
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    self._error(f"API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            self._error(f"Remote correction error: {e}")
            return None

    async def _correct_batch_local(
        self,
        documents: List[dict],
        parallel: bool,
        export_format: str,
        verbose: bool
    ) -> Optional[dict]:
        """Correct batch locally"""
        if verbose:
            self._info(f"Processing {len(documents)} documents locally...")

        try:
            batch_corrector = BatchCorrector(
                batch_id=f"cli_{datetime.now().timestamp()}",
                max_concurrency=10 if parallel else 1
            )

            # Process batch with progress
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        "Processing batch...",
                        total=len(documents)
                    )

                    result = await batch_corrector.process_batch(
                        documents=documents,
                        parallel=parallel,
                        export_format=export_format
                    )

                    progress.update(task, completed=len(documents))
            else:
                result = await batch_corrector.process_batch(
                    documents=documents,
                    parallel=parallel,
                    export_format=export_format
                )

            return result

        except Exception as e:
            self._error(f"Batch correction error: {e}")
            return None

    async def _correct_batch_remote(
        self,
        documents: List[dict],
        export_format: str,
        verbose: bool
    ) -> Optional[dict]:
        """Correct batch using remote API"""
        if verbose:
            self._info(f"Processing {len(documents)} documents via {self.server_url}...")

        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                # Submit batch
                response = await client.post(
                    f"{self.server_url}/api/v1/correct/batch",
                    json={
                        "documents": documents,
                        "export_format": export_format
                    }
                )

                if response.status_code != 202:
                    self._error(f"API error: {response.status_code}")
                    return None

                batch_info = response.json()
                batch_id = batch_info['batch_id']

                # Poll for completion
                if self.console:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=self.console
                    ) as progress:
                        task = progress.add_task("Waiting for batch completion...", total=None)

                        while True:
                            status_response = await client.get(
                                f"{self.server_url}/api/v1/correct/batch/{batch_id}"
                            )

                            if status_response.status_code == 200:
                                status = status_response.json()

                                if status['status'] in ['completed', 'partial', 'failed']:
                                    progress.update(task, completed=True)
                                    return status

                            await asyncio.sleep(2)
                else:
                    # Non-interactive polling
                    while True:
                        status_response = await client.get(
                            f"{self.server_url}/api/v1/correct/batch/{batch_id}"
                        )

                        if status_response.status_code == 200:
                            status = status_response.json()

                            if status['status'] in ['completed', 'partial', 'failed']:
                                return status

                        await asyncio.sleep(2)

        except Exception as e:
            self._error(f"Remote batch correction error: {e}")
            return None

    async def _export_result(self, result: dict, output_file: str, export_format: str):
        """Export correction result to file"""
        exporter = CorrectionExporter()

        # Export to format
        exported = await exporter.export(result, export_format)

        # Write to file
        if export_format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(exported, f, indent=2)
        elif export_format in ['docx', 'xml']:
            with open(output_file, 'wb') as f:
                f.write(exported)
        else:  # html, markdown
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(exported)

    def _print_summary(self, result: dict):
        """Print correction summary"""
        if not self.console:
            print(f"\nSummary:")
            print(f"  Issues Found: {result.get('issues_found', 0)}")
            print(f"  Issues Corrected: {result.get('issues_corrected', 0)}")
            print(f"  Improvement Score: {result.get('improvement_score', 0.0):.2%}")
            return

        table = Table(title="Correction Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Issues Found", str(result.get('issues_found', 0)))
        table.add_row("Issues Corrected", str(result.get('issues_corrected', 0)))
        table.add_row("Improvement Score", f"{result.get('improvement_score', 0.0):.2%}")
        table.add_row("Corrections Applied", str(len(result.get('corrections', []))))

        self.console.print(table)

    def _print_batch_stats(self, stats: dict):
        """Print batch statistics"""
        if not self.console:
            print(f"\nBatch Statistics:")
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            return

        table = Table(title="Batch Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        for key, value in stats.items():
            table.add_row(key.replace('_', ' ').title(), str(value))

        self.console.print(table)

    def _info(self, message: str):
        """Print info message"""
        if self.console:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"INFO: {message}")

    def _success(self, message: str):
        """Print success message"""
        if self.console:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"SUCCESS: {message}")

    def _warning(self, message: str):
        """Print warning message"""
        if self.console:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"WARNING: {message}")

    def _error(self, message: str):
        """Print error message"""
        if self.console:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"ERROR: {message}", file=sys.stderr)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LOKI Correct - Document correction tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'input',
        help="Input file or directory"
    )
    parser.add_argument(
        '-o', '--output',
        help="Output file or directory"
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'xml', 'docx', 'html', 'markdown'],
        default='json',
        help="Export format (default: json)"
    )
    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help="Batch mode (process directory)"
    )
    parser.add_argument(
        '--server',
        help="API server URL (for remote processing)"
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        default=True,
        help="Process batch in parallel (default: True)"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Verbose output"
    )

    args = parser.parse_args()

    # Create CLI instance
    cli = LOKICorrectCLI(server_url=args.server)

    # Run correction
    if args.batch:
        exit_code = asyncio.run(cli.correct_batch(
            input_dir=args.input,
            output_dir=args.output,
            export_format=args.format,
            parallel=args.parallel,
            verbose=args.verbose
        ))
    else:
        exit_code = asyncio.run(cli.correct_file(
            input_file=args.input,
            output_file=args.output,
            export_format=args.format,
            verbose=args.verbose
        ))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
