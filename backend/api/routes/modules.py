"""
Modules and Gates API routes
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status

from ..models.modules import (
    ModulesResponse,
    ModuleInfo,
    GatesResponse,
    GateInfo
)
from ..dependencies import (
    get_engine,
    check_rate_limit
)

router = APIRouter()


@router.get(
    "/modules",
    response_model=ModulesResponse,
    status_code=status.HTTP_200_OK,
    summary="List compliance modules",
    description="Get list of all available compliance modules",
    response_description="List of compliance modules"
)
async def list_modules(
    _: bool = Depends(check_rate_limit)
):
    """
    List all available compliance modules

    Returns information about all loaded compliance modules including:
    - Module ID and name
    - Version information
    - Gate counts
    - Categories and jurisdictions
    - Industry focus

    **Example:**
    ```
    GET /api/v1/modules
    ```

    **Response:**
    ```json
    {
      "modules": [
        {
          "id": "gdpr_uk",
          "name": "GDPR UK Compliance",
          "version": "3.2.1",
          "gates_count": 45,
          "active_gates": 43,
          "categories": ["data_protection", "privacy"]
        }
      ],
      "total": 10,
      "total_gates": 234
    }
    ```
    """
    engine = get_engine()

    modules = []
    total_gates = 0

    for module_id, module_obj in engine.modules.items():
        # Get module information
        gates_count = len(module_obj.gates) if hasattr(module_obj, 'gates') else 0
        module_name = getattr(module_obj, 'name', module_id.replace('_', ' ').title())
        module_version = getattr(module_obj, 'version', '1.0.0')

        module_info = ModuleInfo(
            id=module_id,
            name=module_name,
            version=module_version,
            description=getattr(module_obj, 'description', None),
            gates_count=gates_count,
            active_gates=gates_count,  # For now, assume all active
            deprecated_gates=0,
            categories=getattr(module_obj, 'categories', []),
            jurisdictions=getattr(module_obj, 'jurisdictions', []),
            industry=getattr(module_obj, 'industry', None),
            last_updated=getattr(module_obj, 'last_updated', None),
            metadata={}
        )

        modules.append(module_info)
        total_gates += gates_count

    return ModulesResponse(
        modules=modules,
        total=len(modules),
        total_gates=total_gates
    )


@router.get(
    "/modules/{module_id}",
    response_model=ModuleInfo,
    status_code=status.HTTP_200_OK,
    summary="Get module details",
    description="Get detailed information about a specific compliance module",
    response_description="Module details"
)
async def get_module(
    module_id: str,
    _: bool = Depends(check_rate_limit)
):
    """
    Get detailed information about a specific compliance module

    **Example:**
    ```
    GET /api/v1/modules/gdpr_uk
    ```
    """
    engine = get_engine()

    if module_id not in engine.modules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )

    module_obj = engine.modules[module_id]
    gates_count = len(module_obj.gates) if hasattr(module_obj, 'gates') else 0
    module_name = getattr(module_obj, 'name', module_id.replace('_', ' ').title())
    module_version = getattr(module_obj, 'version', '1.0.0')

    return ModuleInfo(
        id=module_id,
        name=module_name,
        version=module_version,
        description=getattr(module_obj, 'description', None),
        gates_count=gates_count,
        active_gates=gates_count,
        deprecated_gates=0,
        categories=getattr(module_obj, 'categories', []),
        jurisdictions=getattr(module_obj, 'jurisdictions', []),
        industry=getattr(module_obj, 'industry', None),
        last_updated=getattr(module_obj, 'last_updated', None),
        metadata={}
    )


@router.get(
    "/gates",
    response_model=GatesResponse,
    status_code=status.HTTP_200_OK,
    summary="List compliance gates",
    description="Get list of all compliance gates, optionally filtered by module",
    response_description="List of compliance gates"
)
async def list_gates(
    module_id: Optional[str] = Query(None, description="Filter by module ID"),
    active_only: bool = Query(True, description="Only return active gates"),
    _: bool = Depends(check_rate_limit)
):
    """
    List all compliance gates

    Returns information about compliance gates including:
    - Gate ID and name
    - Version and module
    - Severity level
    - Legal source
    - Active/deprecated status

    **Filters:**
    - **module_id**: Filter gates by specific module
    - **active_only**: Only return active gates (default: true)

    **Example:**
    ```
    GET /api/v1/gates?module_id=gdpr_uk&active_only=true
    ```
    """
    engine = get_engine()

    gates = []

    # Determine which modules to scan
    if module_id:
        if module_id not in engine.modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{module_id}' not found"
            )
        modules_to_scan = {module_id: engine.modules[module_id]}
    else:
        modules_to_scan = engine.modules

    # Collect gates from modules
    for mod_id, module_obj in modules_to_scan.items():
        if hasattr(module_obj, 'gates'):
            for gate in module_obj.gates:
                gate_info = GateInfo(
                    id=getattr(gate, 'gate_id', 'unknown'),
                    name=getattr(gate, 'name', getattr(gate, 'gate_id', 'Unknown')),
                    version=getattr(gate, 'version', '1.0.0'),
                    module_id=mod_id,
                    severity=getattr(gate, 'severity', 'WARNING'),
                    description=getattr(gate, 'description', None),
                    legal_source=getattr(gate, 'legal_source', None),
                    active=getattr(gate, 'active', True),
                    deprecated=getattr(gate, 'deprecated', False),
                    deprecation_date=getattr(gate, 'deprecation_date', None),
                    replacement_gate=getattr(gate, 'replacement_gate', None),
                    metadata={}
                )

                # Apply filters
                if active_only and not gate_info.active:
                    continue

                gates.append(gate_info)

    return GatesResponse(
        gates=gates,
        total=len(gates),
        module_id=module_id
    )


@router.get(
    "/gates/{gate_id}",
    response_model=GateInfo,
    status_code=status.HTTP_200_OK,
    summary="Get gate details",
    description="Get detailed information about a specific compliance gate",
    response_description="Gate details"
)
async def get_gate(
    gate_id: str,
    _: bool = Depends(check_rate_limit)
):
    """
    Get detailed information about a specific compliance gate

    **Example:**
    ```
    GET /api/v1/gates/gdpr_uk_consent
    ```
    """
    engine = get_engine()

    # Search for gate across all modules
    for mod_id, module_obj in engine.modules.items():
        if hasattr(module_obj, 'gates'):
            for gate in module_obj.gates:
                if getattr(gate, 'gate_id', '') == gate_id:
                    return GateInfo(
                        id=gate_id,
                        name=getattr(gate, 'name', gate_id),
                        version=getattr(gate, 'version', '1.0.0'),
                        module_id=mod_id,
                        severity=getattr(gate, 'severity', 'WARNING'),
                        description=getattr(gate, 'description', None),
                        legal_source=getattr(gate, 'legal_source', None),
                        active=getattr(gate, 'active', True),
                        deprecated=getattr(gate, 'deprecated', False),
                        deprecation_date=getattr(gate, 'deprecation_date', None),
                        replacement_gate=getattr(gate, 'replacement_gate', None),
                        metadata={}
                    )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Gate '{gate_id}' not found"
    )
