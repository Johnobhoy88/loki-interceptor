"""
WebSocket API routes
"""

import json
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState

from ..models.websocket import (
    WebSocketMessage,
    WebSocketValidationRequest,
    WebSocketValidationProgress,
    WebSocketValidationResponse,
    WebSocketError
)
from ..models.validation import RiskLevel
from ..dependencies import (
    get_engine,
    get_cache,
    get_audit_logger
)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            try:
                await self.send_message(connection, message)
            except Exception:
                pass


# Global connection manager
manager = ConnectionManager()


async def send_progress_update(
    websocket: WebSocket,
    request_id: str,
    module_id: str,
    completed: int,
    total: int,
    status: str
):
    """Send validation progress update"""
    progress = WebSocketValidationProgress(
        type="validation_progress",
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat(),
        module_id=module_id,
        modules_completed=completed,
        modules_total=total,
        progress_percent=(completed / total * 100) if total > 0 else 0,
        current_status=status
    )

    await manager.send_message(websocket, progress.model_dump())


async def send_error(
    websocket: WebSocket,
    request_id: Optional[str],
    error: str,
    message: str,
    details: Optional[dict] = None
):
    """Send error message"""
    error_msg = WebSocketError(
        type="error",
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat(),
        error=error,
        message=message,
        details=details
    )

    await manager.send_message(websocket, error_msg.model_dump())


@router.websocket("/ws/validate")
async def websocket_validate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time document validation

    **Protocol:**
    1. Client connects to WebSocket
    2. Client sends validation request (type: "validation_request")
    3. Server sends progress updates (type: "validation_progress")
    4. Server sends final results (type: "validation_response")
    5. For errors, server sends error message (type: "error")

    **Request Format:**
    ```json
    {
      "type": "validation_request",
      "request_id": "REQ_12345",
      "timestamp": "2025-11-11T10:30:00Z",
      "text": "Document text...",
      "document_type": "contract",
      "modules": ["gdpr_uk", "hr_scottish"],
      "include_progress": true
    }
    ```

    **Progress Update Format:**
    ```json
    {
      "type": "validation_progress",
      "request_id": "REQ_12345",
      "timestamp": "2025-11-11T10:30:01Z",
      "module_id": "gdpr_uk",
      "modules_completed": 1,
      "modules_total": 2,
      "progress_percent": 50.0,
      "current_status": "Processing GDPR UK module..."
    }
    ```

    **Response Format:**
    ```json
    {
      "type": "validation_response",
      "request_id": "REQ_12345",
      "timestamp": "2025-11-11T10:30:05Z",
      "validation": {...},
      "risk": "MEDIUM",
      "success": true
    }
    ```

    **Error Format:**
    ```json
    {
      "type": "error",
      "request_id": "REQ_12345",
      "timestamp": "2025-11-11T10:30:00Z",
      "error": "VALIDATION_ERROR",
      "message": "Invalid request"
    }
    ```

    **Example Usage (JavaScript):**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/validate');

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'validation_request',
        request_id: 'REQ_001',
        timestamp: new Date().toISOString(),
        text: 'Document text...',
        document_type: 'contract',
        modules: ['gdpr_uk'],
        include_progress: true
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'validation_progress') {
        console.log(`Progress: ${data.progress_percent}%`);
      } else if (data.type === 'validation_response') {
        console.log('Validation complete:', data.validation);
      } else if (data.type === 'error') {
        console.error('Error:', data.message);
      }
    };
    ```
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await send_error(
                    websocket,
                    None,
                    "INVALID_JSON",
                    "Invalid JSON format"
                )
                continue

            message_type = message.get('type')
            request_id = message.get('request_id')

            # Handle ping/pong
            if message_type == 'ping':
                pong = WebSocketMessage(
                    type='pong',
                    request_id=request_id,
                    timestamp=datetime.utcnow().isoformat()
                )
                await manager.send_message(websocket, pong.model_dump())
                continue

            # Handle validation request
            if message_type == 'validation_request':
                try:
                    # Validate request
                    req = WebSocketValidationRequest(**message)
                except Exception as e:
                    await send_error(
                        websocket,
                        request_id,
                        "INVALID_REQUEST",
                        f"Invalid validation request: {str(e)}"
                    )
                    continue

                # Perform validation with progress updates
                try:
                    engine = get_engine()
                    cache = get_cache()
                    audit_logger = get_audit_logger()

                    modules = req.modules or list(engine.modules.keys())

                    # Check cache
                    cached_result = cache.get(req.text, req.document_type, modules)
                    if cached_result:
                        # Send cached result immediately
                        from ..routes.validation import _convert_validation_result
                        from ..dependencies import RequestTimer

                        timer = RequestTimer()
                        validation = _convert_validation_result(
                            cached_result,
                            timer,
                            cached=True
                        )

                        response = WebSocketValidationResponse(
                            type="validation_response",
                            request_id=request_id,
                            timestamp=datetime.utcnow().isoformat(),
                            validation=validation,
                            risk=validation.overall_risk,
                            success=True
                        )

                        await manager.send_message(websocket, response.model_dump())
                        continue

                    # Run validation with progress updates
                    if req.include_progress:
                        await send_progress_update(
                            websocket,
                            request_id,
                            "initialization",
                            0,
                            len(modules),
                            "Initializing validation..."
                        )

                    # Perform validation
                    # Note: For real progress updates, we'd need to modify the engine
                    # to support callbacks. For now, we'll simulate progress.
                    start_time = asyncio.get_event_loop().time()

                    engine_result = engine.check_document(
                        text=req.text,
                        document_type=req.document_type,
                        active_modules=modules
                    )

                    # Cache result
                    cache.set(req.text, req.document_type, modules, engine_result)

                    # Log to audit
                    try:
                        audit_logger.log_validation(
                            req.text,
                            req.document_type,
                            modules,
                            engine_result,
                            req.metadata.get('client_id', 'unknown')
                        )
                    except Exception:
                        pass

                    # Convert result
                    from ..routes.validation import _convert_validation_result
                    from ..dependencies import RequestTimer

                    timer = RequestTimer()
                    timer.start_time = start_time  # Adjust timer

                    validation = _convert_validation_result(
                        engine_result,
                        timer,
                        cached=False
                    )

                    # Send final response
                    response = WebSocketValidationResponse(
                        type="validation_response",
                        request_id=request_id,
                        timestamp=datetime.utcnow().isoformat(),
                        validation=validation,
                        risk=validation.overall_risk,
                        success=True
                    )

                    await manager.send_message(websocket, response.model_dump())

                except Exception as e:
                    await send_error(
                        websocket,
                        request_id,
                        "VALIDATION_ERROR",
                        f"Validation failed: {str(e)}",
                        {"type": type(e).__name__}
                    )

            else:
                await send_error(
                    websocket,
                    request_id,
                    "UNKNOWN_MESSAGE_TYPE",
                    f"Unknown message type: {message_type}"
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")
