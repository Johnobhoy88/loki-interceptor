"""
Simple test script to verify all industry-specific compliance gates work correctly.
"""

from modules.industry_specific.gates.healthcare_compliance import HealthcareComplianceGate
from modules.industry_specific.gates.education_compliance import EducationComplianceGate
from modules.industry_specific.gates.finance_compliance import FinanceComplianceGate
from modules.industry_specific.gates.construction_compliance import ConstructionComplianceGate
from modules.industry_specific.gates.technology_compliance import TechnologyComplianceGate


def test_all_gates():
    """Test that all gates can be instantiated and run basic checks."""

    gates = [
        ("Healthcare", HealthcareComplianceGate(), "NHS patient data policy with medical records"),
        ("Education", EducationComplianceGate(), "School safeguarding policy for pupils and students"),
        ("Finance", FinanceComplianceGate(), "Banking AML KYC policy for financial services"),
        ("Construction", ConstructionComplianceGate(), "CDM construction site safety plan with Principal Contractor"),
        ("Technology", TechnologyComplianceGate(), "Software license agreement for SaaS cloud service")
    ]

    print("Testing Industry-Specific Compliance Gates")
    print("=" * 60)

    for name, gate, test_text in gates:
        try:
            result = gate.check(test_text, "policy")
            assert 'status' in result, f"{name}: Missing status in result"
            assert result['status'] in ['PASS', 'FAIL', 'WARNING', 'N/A'], \
                f"{name}: Invalid status {result['status']}"
            assert 'message' in result, f"{name}: Missing message in result"
            assert 'legal_source' in result, f"{name}: Missing legal_source in result"
            print(f"[PASS] {name} Gate: {result['status']} - {result['message'][:60]}")
        except Exception as e:
            print(f"[FAIL] {name} Gate FAILED: {e}")
            raise

    print("=" * 60)
    print("All gates passed basic functionality tests!")
    return True


if __name__ == "__main__":
    test_all_gates()
