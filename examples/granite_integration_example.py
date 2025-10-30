"""
IBM Granite Integration Examples

Demonstrates how to use Granite models with Loki Interceptor for:
1. PDF document conversion
2. Safety validation with Guardian
3. Model interception and validation
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def example_1_pdf_conversion():
    """Example 1: Convert PDF to structured text"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: PDF Document Conversion with Granite-Docling")
    print("=" * 60)

    from backend.granite import DocumentConverter

    # Initialize converter
    converter = DocumentConverter()

    # Check if PDF support is available
    if not converter.supports_file_type("test.pdf"):
        print("❌ PDF support not available")
        print("   Install with: pip install docling")
        return

    print("✅ DocumentConverter initialized")

    # Example: Convert a PDF (you'll need to provide an actual PDF)
    pdf_path = "examples/sample_invoice.pdf"  # Replace with actual path

    if Path(pdf_path).exists():
        print(f"\nConverting: {pdf_path}")

        result = converter.convert_document(pdf_path)

        if result.success:
            print(f"✅ Conversion successful!")
            print(f"   Text length: {len(result.text)} characters")
            print(f"   Tables found: {len(result.tables)}")
            print(f"   Figures found: {len(result.figures)}")
            print(f"\nFirst 200 characters:")
            print(result.text[:200])
        else:
            print(f"❌ Conversion failed: {result.error}")
    else:
        print(f"⚠️  Sample PDF not found at {pdf_path}")
        print("   This is expected - add your own PDF to test")


def example_2_guardian_validation():
    """Example 2: Safety validation with Granite Guardian"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Safety Validation with Granite Guardian")
    print("=" * 60)

    from backend.granite import GuardianValidator

    # Initialize Guardian
    guardian = GuardianValidator(model_size="2b")

    print("✅ GuardianValidator initialized")

    # Test texts with different risk levels
    test_cases = [
        {
            'text': 'Our investment fund offers competitive returns based on market performance.',
            'label': 'Low Risk (Compliant)'
        },
        {
            'text': 'Guaranteed 15% annual returns with zero risk! Limited time offer!',
            'label': 'High Risk (Non-compliant)'
        },
        {
            'text': 'This product is not suitable for inexperienced investors.',
            'label': 'Medium Risk (Warning required)'
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {case['label']} ---")
        print(f"Text: \"{case['text']}\"")

        result = guardian.validate(
            text=case['text'],
            dimensions=['harm', 'social_bias']
        )

        print(f"Risk Level: {result.overall_risk.value}")
        print(f"Passed: {'✅' if result.passed else '❌'}")
        print(f"Recommendation: {result.recommendation}")


def example_3_granite_interceptor():
    """Example 3: Intercept Granite model calls"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Granite Model Interception")
    print("=" * 60)

    from backend.granite import GraniteInterceptor, GuardianValidator
    from backend.core.engine import ComplianceEngine

    try:
        # Initialize components
        engine = ComplianceEngine()
        guardian = GuardianValidator()
        interceptor = GraniteInterceptor(engine, guardian)

        print("✅ GraniteInterceptor initialized")

        # Example request
        request = {
            'model': 'granite-3.2-8b-instruct',
            'messages': [{
                'role': 'user',
                'content': 'Write a brief financial promotion for an investment fund.'
            }],
            'max_tokens': 200
        }

        print("\n📤 Request to Granite model:")
        print(f"   Model: {request['model']}")
        print(f"   Prompt: {request['messages'][0]['content']}")

        # NOTE: This requires a running Granite endpoint
        # Uncomment and adjust endpoint when ready
        """
        result = interceptor.intercept(
            request_data=request,
            endpoint='http://localhost:8000',  # Local vLLM/TGI
            active_modules=['fca_uk']
        )

        if result['blocked']:
            print(f"\n🚫 BLOCKED: {result['message']}")
            print(f"   Risk: {result.get('validation', {}).get('overall_risk')}")
        else:
            print(f"\n✅ ALLOWED")
            print(f"   Risk: {result['loki']['risk']}")
            print(f"   Response preview: {result['response']['choices'][0]['message']['content'][:100]}...")
        """

        print("\n⚠️  Granite endpoint not configured")
        print("   To test:")
        print("   1. Start local Granite server: vllm serve ibm-granite/granite-4.0-8b-instruct")
        print("   2. Uncomment the interceptor.intercept() call above")
        print("   3. Run this script again")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_4_hybrid_workflow():
    """Example 4: Complete hybrid workflow"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Complete Hybrid Workflow")
    print("=" * 60)

    print("""
This example demonstrates a complete workflow:

1. PDF Input → Granite-Docling Conversion
2. Text → LOKI Pattern Validation (141 rules)
3. Corrections → Granite Guardian Safety Check
4. Output → Enhanced validated document

Steps:
    """)

    workflow_code = '''
    from backend.granite import DocumentConverter, GuardianValidator
    from backend.core.document_validator import DocumentValidator
    from backend.core.document_corrector import DocumentCorrector

    # 1. Convert PDF
    converter = DocumentConverter()
    doc_data = converter.convert_to_validation_format(
        "financial_promotion.pdf",
        document_type="financial"
    )

    # 2. Validate with LOKI patterns
    validator = DocumentValidator()
    validation = validator.validate_document(
        text=doc_data['text'],
        document_type='financial',
        modules=['fca_uk', 'gdpr_uk']
    )

    # 3. Apply corrections
    corrector = DocumentCorrector(advanced_mode=True)
    corrected = corrector.correct_document(
        text=doc_data['text'],
        validation_results=validation,
        document_type='financial'
    )

    # 4. Guardian safety check
    guardian = GuardianValidator()
    safety = guardian.validate_correction(
        original=doc_data['text'],
        corrected=corrected['corrected'],
        correction_type='pattern_based'
    )

    # 5. Final output
    if safety.passed:
        print("✅ Document validated and corrected")
        print(f"   LOKI corrections: {corrected['correction_count']}")
        print(f"   Guardian risk: {safety.overall_risk.value}")
        return corrected['corrected']
    else:
        print("⚠️ Safety concerns detected")
        print(f"   Recommendation: {safety.recommendation}")
    '''

    print(workflow_code)
    print("\n✅ This workflow combines:")
    print("   • Granite-Docling: PDF preprocessing")
    print("   • LOKI Patterns: 141 detection rules")
    print("   • Granite Guardian: Safety validation")
    print("   • Result: Maximum compliance coverage")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("IBM GRANITE INTEGRATION EXAMPLES FOR LOKI INTERCEPTOR")
    print("=" * 60)

    examples = [
        example_1_pdf_conversion,
        example_2_guardian_validation,
        example_3_granite_interceptor,
        example_4_hybrid_workflow
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Install Granite dependencies: pip install -r requirements-granite.txt")
    print("2. Test PDF conversion with your own documents")
    print("3. Set up local Granite endpoint for model testing")
    print("4. Benchmark against existing Claude integration")


if __name__ == "__main__":
    main()
