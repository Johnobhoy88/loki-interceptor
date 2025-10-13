"""
Gate version control and registry
Tracks gate versions, deprecation, and compatibility
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class GateVersion:
    """Gate version metadata"""
    gate_id: str
    version: str
    module_id: str
    legal_source: str
    severity: str
    active: bool = True
    deprecated: bool = False
    deprecation_date: Optional[str] = None
    replacement_gate: Optional[str] = None
    changelog: Optional[str] = None


class GateRegistry:
    """
    Central registry for gate versions and lifecycle management
    """

    def __init__(self):
        self.gates: Dict[str, GateVersion] = {}

    def register_gate(
        self,
        module_id: str,
        gate_id: str,
        gate_obj,
        version: str = "1.0.0"
    ):
        """
        Register a gate with version information

        Args:
            module_id: Module identifier
            gate_id: Gate identifier
            gate_obj: Gate class instance
            version: Gate version
        """
        full_gate_id = f"{module_id}.{gate_id}"

        gate_version = GateVersion(
            gate_id=full_gate_id,
            version=version,
            module_id=module_id,
            legal_source=getattr(gate_obj, 'legal_source', 'Unknown'),
            severity=getattr(gate_obj, 'severity', 'medium'),
            active=True,
            deprecated=False
        )

        self.gates[full_gate_id] = gate_version

    def deprecate_gate(
        self,
        full_gate_id: str,
        replacement_gate: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """
        Mark a gate as deprecated

        Args:
            full_gate_id: Full gate ID (module.gate)
            replacement_gate: ID of replacement gate
            reason: Deprecation reason
        """
        if full_gate_id in self.gates:
            self.gates[full_gate_id].deprecated = True
            self.gates[full_gate_id].deprecation_date = datetime.utcnow().isoformat()
            self.gates[full_gate_id].replacement_gate = replacement_gate
            self.gates[full_gate_id].changelog = reason

    def deactivate_gate(self, full_gate_id: str):
        """Deactivate a gate (will not run in validation)"""
        if full_gate_id in self.gates:
            self.gates[full_gate_id].active = False

    def get_active_gates(self, module_id: Optional[str] = None) -> List[GateVersion]:
        """Get all active gates, optionally filtered by module"""
        result = []
        for gate_id, gate_version in self.gates.items():
            if not gate_version.active:
                continue
            if module_id and gate_version.module_id != module_id:
                continue
            result.append(gate_version)
        return result

    def get_deprecated_gates(self) -> List[GateVersion]:
        """Get all deprecated gates"""
        return [
            gate for gate in self.gates.values()
            if gate.deprecated
        ]

    def get_gate_info(self, full_gate_id: str) -> Optional[GateVersion]:
        """Get version information for a specific gate"""
        return self.gates.get(full_gate_id)

    def list_all_gates(self) -> Dict[str, GateVersion]:
        """Get all registered gates"""
        return self.gates.copy()

    def get_module_gates(self, module_id: str) -> Dict[str, GateVersion]:
        """Get all gates for a specific module"""
        return {
            gate_id: gate_version
            for gate_id, gate_version in self.gates.items()
            if gate_version.module_id == module_id
        }


# Global gate registry instance
gate_registry = GateRegistry()
