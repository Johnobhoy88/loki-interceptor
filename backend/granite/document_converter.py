"""
Granite-Docling Document Converter

Converts complex documents (PDFs, images, scans) into structured text
using IBM's Granite-Docling 258M model.

Features:
- PDF to structured markdown
- Table extraction and preservation
- Figure/image extraction
- Layout preservation
- OCR for scanned documents
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of document conversion"""
    text: str
    markdown: str
    tables: List[Dict[str, Any]]
    figures: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    source_path: str
    success: bool
    error: Optional[str] = None


class DocumentConverter:
    """
    Converts documents to structured text using Granite-Docling.

    Examples:
        >>> converter = DocumentConverter()
        >>> result = converter.convert_document("invoice.pdf")
        >>> print(result.text)
        >>> print(f"Found {len(result.tables)} tables")

        >>> # Batch conversion
        >>> results = converter.convert_batch(["doc1.pdf", "doc2.pdf"])
    """

    def __init__(self, use_gpu: bool = False, cache_dir: Optional[str] = None):
        """
        Initialize document converter.

        Args:
            use_gpu: Use GPU acceleration if available
            cache_dir: Directory for caching converted documents
        """
        self.use_gpu = use_gpu
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), ".docling_cache")
        self._docling_available = self._check_docling()

    def _check_docling(self) -> bool:
        """Check if Docling is installed and available"""
        try:
            import docling  # noqa: F401
            return True
        except ImportError:
            logger.warning(
                "Docling not installed. Install with: pip install docling\n"
                "PDF/image conversion will not be available."
            )
            return False

    def convert_document(
        self,
        file_path: Union[str, Path],
        extract_tables: bool = True,
        extract_figures: bool = True,
        preserve_layout: bool = True
    ) -> ConversionResult:
        """
        Convert a document to structured text.

        Args:
            file_path: Path to document (PDF, image, etc.)
            extract_tables: Extract and structure tables
            extract_figures: Extract figures and images
            preserve_layout: Maintain document layout

        Returns:
            ConversionResult with text, tables, figures, and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If Docling not installed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if not self._docling_available:
            raise RuntimeError(
                "Docling not installed. Install with: pip install docling"
            )

        try:
            from docling.document_converter import DocumentConverter as DoclingConverter

            # Initialize converter
            converter = DoclingConverter()

            # Convert document
            result = converter.convert(str(file_path))

            # Extract text
            text = result.document.export_to_text()
            markdown = result.document.export_to_markdown()

            # Extract tables
            tables = []
            if extract_tables:
                for table in result.document.tables:
                    tables.append({
                        'data': table.data if hasattr(table, 'data') else str(table),
                        'caption': getattr(table, 'caption', None),
                        'position': getattr(table, 'position', None)
                    })

            # Extract figures
            figures = []
            if extract_figures:
                for figure in result.document.figures:
                    figures.append({
                        'caption': getattr(figure, 'caption', None),
                        'position': getattr(figure, 'position', None),
                        'type': getattr(figure, 'type', 'image')
                    })

            # Extract metadata
            metadata = {
                'pages': getattr(result.document, 'page_count', 0),
                'format': file_path.suffix,
                'file_size': file_path.stat().st_size,
                'converter': 'Granite-Docling 258M'
            }

            return ConversionResult(
                text=text,
                markdown=markdown,
                tables=tables,
                figures=figures,
                metadata=metadata,
                source_path=str(file_path),
                success=True
            )

        except Exception as e:
            logger.error(f"Error converting document {file_path}: {e}")
            return ConversionResult(
                text="",
                markdown="",
                tables=[],
                figures=[],
                metadata={},
                source_path=str(file_path),
                success=False,
                error=str(e)
            )

    def convert_batch(
        self,
        file_paths: List[Union[str, Path]],
        **kwargs
    ) -> List[ConversionResult]:
        """
        Convert multiple documents in batch.

        Args:
            file_paths: List of document paths
            **kwargs: Arguments passed to convert_document()

        Returns:
            List of ConversionResults
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.convert_document(file_path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in batch conversion for {file_path}: {e}")
                results.append(ConversionResult(
                    text="",
                    markdown="",
                    tables=[],
                    figures=[],
                    metadata={},
                    source_path=str(file_path),
                    success=False,
                    error=str(e)
                ))
        return results

    def convert_to_validation_format(
        self,
        file_path: Union[str, Path],
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Convert document and format for Loki validation.

        Args:
            file_path: Path to document
            document_type: Type for validation (financial, privacy_policy, etc.)

        Returns:
            Dict formatted for DocumentValidator
        """
        result = self.convert_document(file_path)

        if not result.success:
            raise RuntimeError(f"Conversion failed: {result.error}")

        return {
            'text': result.text,
            'markdown': result.markdown,
            'document_type': document_type,
            'metadata': {
                'source': result.source_path,
                'tables_count': len(result.tables),
                'figures_count': len(result.figures),
                'converter': 'Granite-Docling',
                **result.metadata
            },
            'tables': result.tables,
            'figures': result.figures
        }

    def supports_file_type(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file type is supported.

        Args:
            file_path: Path to check

        Returns:
            True if supported
        """
        supported_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp',
            '.doc', '.docx', '.txt', '.html', '.htm'
        }
        return Path(file_path).suffix.lower() in supported_extensions
