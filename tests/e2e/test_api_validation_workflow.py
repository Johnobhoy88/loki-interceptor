"""
E2E Tests for Document Validation Workflow

Tests the complete workflow of uploading, validating, and processing
compliance documents through the LOKI platform.
"""

import pytest
import requests
import json
from typing import Dict, Any
import time


@pytest.mark.e2e
@pytest.mark.integration
class TestDocumentValidationWorkflow:
    """Test complete document validation workflow."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client for testing."""
        return requests.Session()

    @pytest.fixture
    def sample_document(self):
        """Sample compliance document for testing."""
        return {
            "title": "Employment Contract",
            "content": """
            EMPLOYMENT AGREEMENT
            This agreement is entered into between Employer and Employee.

            1. Position: Senior Compliance Officer
            2. Start Date: 2024-01-15
            3. Salary: £60,000 per annum
            4. Working Hours: 40 hours per week
            5. Notice Period: 3 months

            Signed: [Signature]
            Date: 2024-01-10
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "employment",
                "industry": "Financial Services",
            },
        }

    def test_document_upload_and_validation(self, api_client, test_config, sample_document):
        """Test document upload and validation."""
        endpoint = f"{test_config['backend_url']}/api/validate"

        response = api_client.post(
            endpoint,
            json=sample_document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()

        assert "validation_id" in data
        assert "status" in data
        assert data["status"] in ["pending", "completed", "failed"]
        assert "timestamp" in data

    def test_validation_retrieval(self, api_client, test_config, sample_document):
        """Test validation result retrieval."""
        # First, upload a document
        upload_response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=sample_document,
            timeout=test_config['api_timeout']
        )

        assert upload_response.status_code == 200
        validation_id = upload_response.json()["validation_id"]

        # Retrieve validation results
        time.sleep(1)  # Wait for processing
        get_response = api_client.get(
            f"{test_config['backend_url']}/api/validation/{validation_id}",
            timeout=test_config['api_timeout']
        )

        assert get_response.status_code in [200, 202]  # 200 if complete, 202 if pending
        data = get_response.json()
        assert "validation_id" in data

    def test_multiple_documents_batch_validation(self, api_client, test_config):
        """Test batch validation of multiple documents."""
        documents = [
            {
                "title": f"Document {i}",
                "content": f"Sample content for document {i}",
                "metadata": {"document_type": "employment", "jurisdiction": "UK"},
            }
            for i in range(3)
        ]

        endpoint = f"{test_config['backend_url']}/api/validate/batch"
        response = api_client.post(
            endpoint,
            json={"documents": documents},
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert "count" in data
        assert data["count"] == 3

    def test_validation_with_gates(self, api_client, test_config, sample_document):
        """Test document validation with specific compliance gates."""
        sample_document["gates"] = ["hr_scottish", "gdpr_uk", "employment"]

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=sample_document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()
        assert "gates_executed" in data or "gates" in data

    def test_validation_results_contain_required_fields(self, api_client, test_config, sample_document):
        """Test that validation results contain all required fields."""
        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=sample_document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()

        required_fields = ["validation_id", "status", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_validation_error_handling(self, api_client, test_config):
        """Test error handling for invalid document."""
        invalid_document = {
            "title": "",  # Invalid: empty title
            "content": None,  # Invalid: None content
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/validate",
            json=invalid_document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [400, 422]  # Bad request or validation error
        data = response.json()
        assert "error" in data or "message" in data


@pytest.mark.e2e
class TestCorrectionWorkflow:
    """Test document correction and enhancement workflow."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client for testing."""
        return requests.Session()

    @pytest.fixture
    def document_needing_correction(self):
        """Document with potential compliance issues."""
        return {
            "title": "Employment Agreement - DRAFT",
            "content": """
            EMPLOYMENT AGREEMENT
            Employee name: John Doe
            Position: Manager
            Start date: 2024-01-15
            Salary: 50000

            Terms and conditions are not fully specified.
            No mention of working hours or notice period.
            """,
            "metadata": {
                "jurisdiction": "UK",
                "document_type": "employment",
                "status": "draft",
            },
        }

    def test_document_correction(self, api_client, test_config, document_needing_correction):
        """Test document correction workflow."""
        endpoint = f"{test_config['backend_url']}/api/correct"

        response = api_client.post(
            endpoint,
            json=document_needing_correction,
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]
        data = response.json()
        assert "correction_id" in data or "id" in data

    def test_correction_with_suggestions(self, api_client, test_config, document_needing_correction):
        """Test correction with improvement suggestions."""
        response = api_client.post(
            f"{test_config['backend_url']}/api/correct",
            json={
                **document_needing_correction,
                "include_suggestions": True,
            },
            timeout=test_config['api_timeout']
        )

        assert response.status_code in [200, 202]
        data = response.json()
        if "suggestions" in data:
            assert isinstance(data["suggestions"], list)

    def test_correction_retrieval(self, api_client, test_config, document_needing_correction):
        """Test retrieving correction results."""
        # Submit for correction
        correction_response = api_client.post(
            f"{test_config['backend_url']}/api/correct",
            json=document_needing_correction,
            timeout=test_config['api_timeout']
        )

        assert correction_response.status_code in [200, 202]
        correction_id = correction_response.json().get("correction_id") or correction_response.json().get("id")

        # Retrieve results
        time.sleep(1)
        get_response = api_client.get(
            f"{test_config['backend_url']}/api/correction/{correction_id}",
            timeout=test_config['api_timeout']
        )

        assert get_response.status_code in [200, 202]


@pytest.mark.e2e
class TestGateworkflow:
    """Test individual compliance gate workflows."""

    @pytest.fixture
    def api_client(self, test_config):
        """Create API client for testing."""
        return requests.Session()

    def test_hr_scottish_gate(self, api_client, test_config):
        """Test HR Scottish compliance gate."""
        document = {
            "title": "Scottish Employment Contract",
            "content": "Employment terms for Scottish location...",
            "metadata": {"jurisdiction": "Scotland"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/gates/hr_scottish",
            json=document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "passed" in data

    def test_gdpr_gate(self, api_client, test_config):
        """Test GDPR compliance gate."""
        document = {
            "title": "Privacy Policy",
            "content": """
            Privacy Policy
            We collect and process personal data as follows:
            - Name and email address
            - Usage analytics
            Data retention: 12 months
            User rights: Users can request access or deletion
            """,
            "metadata": {"document_type": "privacy_policy"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/gates/gdpr_uk",
            json=document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "compliance_status" in data

    def test_tax_gate(self, api_client, test_config):
        """Test Tax compliance gate."""
        document = {
            "title": "Tax Filing Document",
            "content": """
            Financial Summary
            Gross Income: £250,000
            Expenses: £50,000
            Net Income: £200,000
            Tax Period: 2023-2024
            """,
            "metadata": {"document_type": "tax_return"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/gates/tax_uk",
            json=document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200

    def test_fca_gate(self, api_client, test_config):
        """Test FCA compliance gate."""
        document = {
            "title": "Financial Service Agreement",
            "content": """
            Financial Services Agreement
            Service Type: Investment Advisory
            Client Type: Retail
            Fees: 0.5% annually
            Risk Warnings: Investments can go down as well as up
            """,
            "metadata": {"document_type": "financial_service"},
        }

        response = api_client.post(
            f"{test_config['backend_url']}/api/gates/fca_uk",
            json=document,
            timeout=test_config['api_timeout']
        )

        assert response.status_code == 200
