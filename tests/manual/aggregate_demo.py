"""
Manual smoke test for the multi-model aggregation flow.

Run with:
    python tests/manual/aggregate_demo.py

This uses simulated responses so no provider credits are required.
"""
import json

from backend.server import aggregator, engine  # noqa: F401  (engine imported for module initialization)


def main() -> None:
    prompt = "Draft a compliance-friendly summary of a high yield investment opportunity."
    providers = [
        {
            "name": "anthropic",
            "simulated_response": (
                "This bond guarantees a 15% return with zero risk. Capital is fully protected and withdrawals are instant."
            ),
        },
        {
            "name": "openai",
            "simulated_response": (
                "The product targets sophisticated investors comfortable accepting capital risk. Returns are not guaranteed; "
                "customers should review the risk factors and suitability checks before investing."
            ),
        },
    ]

    result = aggregator.aggregate(
        prompt=prompt,
        provider_specs=providers,
        modules=['fca_uk']
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
