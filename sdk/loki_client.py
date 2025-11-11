"""
LOKI Interceptor Python Client SDK

Easy-to-use Python client for the LOKI Interceptor API
"""

import requests
import json
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationResult:
    """Validation result"""
    document_hash: str
    timestamp: str
    overall_risk: RiskLevel
    modules: List[Dict[str, Any]]
    universal_analyzers: List[Dict[str, Any]]
    total_gates_checked: int
    total_gates_failed: int
    execution_time_ms: float
    cached: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationResult':
        """Create ValidationResult from dictionary"""
        return cls(
            document_hash=data.get('document_hash', ''),
            timestamp=data.get('timestamp', ''),
            overall_risk=RiskLevel(data.get('overall_risk', 'LOW')),
            modules=data.get('modules', []),
            universal_analyzers=data.get('universal_analyzers', []),
            total_gates_checked=data.get('total_gates_checked', 0),
            total_gates_failed=data.get('total_gates_failed', 0),
            execution_time_ms=data.get('execution_time_ms', 0.0),
            cached=data.get('cached', False)
        )


@dataclass
class CorrectionResult:
    """Correction result"""
    original_text: str
    corrected_text: str
    issues_found: int
    issues_corrected: int
    corrections: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    improvement_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'CorrectionResult':
        """Create CorrectionResult from dictionary"""
        return cls(
            original_text=data.get('original_text', ''),
            corrected_text=data.get('corrected_text', ''),
            issues_found=data.get('issues_found', 0),
            issues_corrected=data.get('issues_corrected', 0),
            corrections=data.get('corrections', []),
            suggestions=data.get('suggestions', []),
            improvement_score=data.get('improvement_score', 0.0),
            metadata=data.get('metadata', {})
        )


@dataclass
class ModuleInfo:
    """Module information"""
    id: str
    name: str
    version: str
    gates_count: int
    active_gates: int
    categories: List[str] = field(default_factory=list)
    jurisdictions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ModuleInfo':
        """Create ModuleInfo from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            version=data.get('version', ''),
            gates_count=data.get('gates_count', 0),
            active_gates=data.get('active_gates', 0),
            categories=data.get('categories', []),
            jurisdictions=data.get('jurisdictions', [])
        )


class LOKIClientError(Exception):
    """Base exception for LOKI client errors"""
    pass


class LOKIAPIError(LOKIClientError):
    """API error exception"""

    def __init__(self, status_code: int, message: str, details: Optional[dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")


class LOKIClient:
    """
    LOKI Interceptor API Client

    Python client for interacting with the LOKI Interceptor API.

    Example:
        ```python
        from loki_client import LOKIClient

        # Create client
        client = LOKIClient(base_url="http://localhost:8000")

        # Validate document
        result = client.validate(
            text="This is a contract...",
            document_type="contract",
            modules=["gdpr_uk", "hr_scottish"]
        )

        print(f"Risk Level: {result.overall_risk}")
        print(f"Gates Failed: {result.total_gates_failed}")

        # Correct document
        correction = client.correct(
            text="This is a contract...",
            validation_results=result.__dict__,
            auto_apply=True
        )

        print(f"Corrected: {correction.corrected_text}")
        ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize LOKI client

        Args:
            base_url: Base URL of the LOKI API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        # Set headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LOKI-Python-Client/1.0.0'
        })

        if api_key:
            self.session.headers['X-API-Key'] = api_key

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """
        Make HTTP request to API

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        url = f"{self.base_url}/api/v1{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Check for errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise LOKIAPIError(
                        status_code=response.status_code,
                        message=error_data.get('message', 'Unknown error'),
                        details=error_data.get('details')
                    )
                except json.JSONDecodeError:
                    raise LOKIAPIError(
                        status_code=response.status_code,
                        message=response.text or 'Unknown error'
                    )

            return response.json()

        except requests.RequestException as e:
            raise LOKIClientError(f"Request failed: {str(e)}")

    def validate(
        self,
        text: str,
        document_type: str = "unknown",
        modules: Optional[List[str]] = None,
        use_cache: bool = True,
        include_suggestions: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a document

        Args:
            text: Document text to validate
            document_type: Type of document
            modules: Specific modules to run (None = all)
            use_cache: Whether to use cached results
            include_suggestions: Whether to include correction suggestions
            metadata: Additional metadata

        Returns:
            ValidationResult

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        data = {
            'text': text,
            'document_type': document_type,
            'modules': modules,
            'use_cache': use_cache,
            'include_suggestions': include_suggestions,
            'metadata': metadata or {}
        }

        response = self._request('POST', '/validate', data=data)
        return ValidationResult.from_dict(response['validation'])

    def validate_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate multiple documents in batch

        Args:
            documents: List of document validation requests

        Returns:
            List of ValidationResult

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        responses = self._request('POST', '/validate/batch', data=documents)

        return [
            ValidationResult.from_dict(response['validation'])
            for response in responses
        ]

    def correct(
        self,
        text: str,
        validation_results: dict,
        auto_apply: bool = False,
        confidence_threshold: float = 0.8,
        issue_ids: Optional[List[str]] = None
    ) -> CorrectionResult:
        """
        Correct a document based on validation results

        Args:
            text: Original document text
            validation_results: Validation results from validate()
            auto_apply: Automatically apply high-confidence corrections
            confidence_threshold: Minimum confidence for auto-apply
            issue_ids: Specific issues to correct (None = all)

        Returns:
            CorrectionResult

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        data = {
            'text': text,
            'validation_results': validation_results,
            'auto_apply': auto_apply,
            'confidence_threshold': confidence_threshold,
            'issue_ids': issue_ids
        }

        response = self._request('POST', '/correct', data=data)
        return CorrectionResult.from_dict(response)

    def get_modules(self) -> List[ModuleInfo]:
        """
        Get list of available compliance modules

        Returns:
            List of ModuleInfo

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        response = self._request('GET', '/modules')
        return [
            ModuleInfo.from_dict(module)
            for module in response['modules']
        ]

    def get_module(self, module_id: str) -> ModuleInfo:
        """
        Get information about a specific module

        Args:
            module_id: Module identifier

        Returns:
            ModuleInfo

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        response = self._request('GET', f'/modules/{module_id}')
        return ModuleInfo.from_dict(response)

    def get_gates(
        self,
        module_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get list of compliance gates

        Args:
            module_id: Filter by module ID
            active_only: Only return active gates

        Returns:
            List of gate information dictionaries

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        params = {
            'module_id': module_id,
            'active_only': active_only
        }
        response = self._request('GET', '/gates', params=params)
        return response['gates']

    def get_stats(self, include_trends: bool = False) -> Dict[str, Any]:
        """
        Get system statistics

        Args:
            include_trends: Include recent risk trends

        Returns:
            System statistics dictionary

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        params = {'include_trends': include_trends}
        return self._request('GET', '/stats', params=params)

    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get analytics overview

        Args:
            days: Number of days to analyze

        Returns:
            Analytics overview dictionary

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        params = {'days': days}
        return self._request('GET', '/stats/analytics', params=params)

    def get_history(
        self,
        page: int = 1,
        page_size: int = 50,
        risk_level: Optional[RiskLevel] = None,
        document_type: Optional[str] = None,
        include_stats: bool = False
    ) -> Dict[str, Any]:
        """
        Get validation history

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            risk_level: Filter by risk level
            document_type: Filter by document type
            include_stats: Include aggregated statistics

        Returns:
            History response dictionary

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        params = {
            'page': page,
            'page_size': page_size,
            'include_stats': include_stats
        }

        if risk_level:
            params['risk_level'] = risk_level.value
        if document_type:
            params['document_type'] = document_type

        return self._request('GET', '/history', params=params)

    def clear_cache(self) -> bool:
        """
        Clear the validation cache

        Returns:
            True if successful

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        response = self._request('POST', '/stats/cache/clear')
        return response.get('success', False)

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health

        Returns:
            Health status dictionary

        Raises:
            LOKIAPIError: If API returns error
            LOKIClientError: If request fails
        """
        url = f"{self.base_url}/api/health"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LOKIClientError(f"Health check failed: {str(e)}")


# Convenience functions
def validate_document(
    text: str,
    document_type: str = "unknown",
    base_url: str = "http://localhost:8000",
    **kwargs
) -> ValidationResult:
    """
    Quick validation function

    Args:
        text: Document text
        document_type: Document type
        base_url: API base URL
        **kwargs: Additional arguments for validate()

    Returns:
        ValidationResult
    """
    client = LOKIClient(base_url=base_url)
    return client.validate(text, document_type, **kwargs)


def correct_document(
    text: str,
    validation_results: dict,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> CorrectionResult:
    """
    Quick correction function

    Args:
        text: Document text
        validation_results: Validation results
        base_url: API base URL
        **kwargs: Additional arguments for correct()

    Returns:
        CorrectionResult
    """
    client = LOKIClient(base_url=base_url)
    return client.correct(text, validation_results, **kwargs)


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python loki_client.py <text>")
        sys.exit(1)

    text = sys.argv[1]

    try:
        # Create client
        client = LOKIClient(base_url="http://localhost:8000")

        # Check health
        print("Checking API health...")
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
        print(f"✓ Modules loaded: {health['modules_loaded']}")
        print()

        # Validate document
        print("Validating document...")
        result = client.validate(text, document_type="contract")
        print(f"✓ Risk Level: {result.overall_risk.value}")
        print(f"✓ Gates Checked: {result.total_gates_checked}")
        print(f"✓ Gates Failed: {result.total_gates_failed}")
        print(f"✓ Execution Time: {result.execution_time_ms:.2f}ms")
        print(f"✓ Cached: {result.cached}")

        if result.total_gates_failed > 0:
            print()
            print("Attempting corrections...")
            correction = client.correct(
                text,
                result.__dict__,
                auto_apply=True,
                confidence_threshold=0.8
            )
            print(f"✓ Issues Found: {correction.issues_found}")
            print(f"✓ Issues Corrected: {correction.issues_corrected}")
            print(f"✓ Improvement Score: {correction.improvement_score:.2%}")

    except LOKIAPIError as e:
        print(f"✗ API Error {e.status_code}: {e.message}")
        sys.exit(1)
    except LOKIClientError as e:
        print(f"✗ Client Error: {e}")
        sys.exit(1)
