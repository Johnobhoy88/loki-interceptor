"""Base classes and helpers for modular gate registration with metadata."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


class GateModuleBase:
    """Base helper for compliance modules that register gates with metadata."""

    def __init__(self) -> None:
        self.gate_registry: Dict[str, Dict[str, Any]] = {}

    def register_gate(
        self,
        gate_id: str,
        gate_obj: Any,
        *,
        version: str = "1.0.0",
        tags: Optional[Iterable[str]] = None,
        legal_reference: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.gate_registry[gate_id] = {
            "gate": gate_obj,
            "version": version,
            "tags": list(tags or []),
            "legal_reference": legal_reference,
            "description": description,
        }

    @property
    def gates(self) -> Dict[str, Any]:
        return {gate_id: entry["gate"] for gate_id, entry in self.gate_registry.items()}

    def gate_metadata(self) -> Dict[str, Dict[str, Any]]:
        return {
            gate_id: {
                "version": entry["version"],
                "tags": entry["tags"],
                "legal_reference": entry["legal_reference"],
                "description": entry["description"],
            }
            for gate_id, entry in self.gate_registry.items()
        }

    def execute(self, text: str, document_type: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"gates": {}}

        for gate_id, entry in self.gate_registry.items():
            gate = entry["gate"]
            metadata = {
                "version": entry["version"],
                "tags": entry["tags"],
                "legal_reference": entry["legal_reference"],
                "description": entry["description"],
            }

            try:
                outcome = gate.check(text, document_type)
                if isinstance(outcome, dict):
                    outcome.setdefault("_metadata", metadata)
                else:
                    outcome = {
                        "status": "ERROR",
                        "severity": "critical",
                        "message": "Gate returned non-dict response",
                        "_metadata": metadata,
                    }
            except Exception as exc:  # pragma: no cover - defensive guard
                outcome = {
                    "status": "ERROR",
                    "severity": "critical",
                    "message": f"Gate error: {exc}",
                    "_metadata": metadata,
                }

            results["gates"][gate_id] = outcome

        return results
