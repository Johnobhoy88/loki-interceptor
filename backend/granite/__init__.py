"""
IBM Granite Models Integration for Loki Interceptor

This module provides integration with IBM Granite model family:
- Granite-Docling 258M: Document preprocessing (PDF, images, scans)
- Granite Guardian 3.0: Compliance risk detection and safety validation
- Granite 3.2/4.0 VLM: Vision-language models for semantic analysis (optional)

Architecture:
    Document → Docling Parser → Loki Validator → Guardian Safety Check → Output

Usage:
    from backend.granite import DocumentConverter, GuardianValidator

    # Convert PDF to text
    converter = DocumentConverter()
    result = converter.convert_document("financial_promotion.pdf")

    # Validate safety
    guardian = GuardianValidator()
    safety_check = guardian.validate(result.text, dimensions=["harm", "bias"])
"""

__version__ = "1.0.0"
__author__ = "Highland AI"

# Import key classes for easier access
from .document_converter import DocumentConverter, ConversionResult
from .guardian_validator import GuardianValidator, SafetyResult
from .granite_interceptor import GraniteInterceptor

__all__ = [
    "DocumentConverter",
    "ConversionResult",
    "GuardianValidator",
    "SafetyResult",
    "GraniteInterceptor",
]
