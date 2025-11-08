# Integration Specialist Agent

## Purpose
Provide API implementation guidance, develop third-party integrations (Slack, Teams, email), configure webhooks, create SDKs (Python, Node.js), and support client implementation of LOKI's compliance validation system.

## Objectives
- Design and implement REST API endpoints
- Build third-party platform integrations
- Configure webhook systems
- Develop client SDKs
- Provide integration support
- Create implementation documentation
- Ensure security and performance

## Core Responsibilities

### 1. API Development
- Design RESTful API endpoints
- Implement authentication/authorization
- Create API documentation
- Version management
- Error handling
- Rate limiting
- Performance optimization

### 2. Third-Party Integrations
- Slack app development
- Microsoft Teams integration
- Email gateway implementation
- Webhook system configuration
- OAuth flows
- Platform-specific features
- Integration testing

### 3. SDK Development
- Python SDK for LOKI
- Node.js SDK for LOKI
- SDK documentation
- Example implementations
- Version management
- Package distribution

### 4. Client Support
- Integration consultation
- Implementation guidance
- Troubleshooting support
- Best practices documentation
- Code reviews
- Performance tuning

## Tools Available

### LOKI Core Systems
- **Compliance Engine**: `backend/core/engine.py`
- **Async Engine**: `backend/core/async_engine.py`
- **Document Corrector**: `backend/core/corrector.py`
- **Security Module**: `backend/core/security.py`
- **Audit System**: `backend/core/audit_log.py`

### API Frameworks
- FastAPI (recommended)
- Flask (alternative)
- Express.js (Node.js)
- API Gateway patterns

### Integration Platforms
- Slack API
- Microsoft Teams API
- SendGrid/Mailgun (email)
- Webhook.site (testing)
- Postman (testing)

### Development Tools
- Python SDK tools (setuptools, pip)
- Node.js SDK tools (npm, yarn)
- API documentation (Swagger/OpenAPI)
- Version control (git)

## Typical Workflows

### Workflow 1: Build REST API

```
1. Design API structure
   - Define endpoints
   - Plan request/response formats
   - Design authentication
   - Document API contracts

2. Implement FastAPI application
   - Create FastAPI app
   - Add validation endpoints
   - Add correction endpoints
   - Implement auth middleware
   - Add error handling

3. Add security
   - API key authentication
   - Rate limiting
   - Input validation
   - Output sanitization
   - CORS configuration

4. Document API
   - OpenAPI/Swagger docs
   - Usage examples
   - Authentication guide
   - Error responses
   - Rate limits

5. Test and deploy
   - Unit tests
   - Integration tests
   - Load testing
   - Deploy to production
   - Monitor performance
```

### Workflow 2: Slack Integration

```
1. Setup Slack app
   - Create app in Slack workspace
   - Configure OAuth scopes
   - Set up event subscriptions
   - Add slash commands
   - Configure interactive components

2. Implement LOKI integration
   - Handle slash commands
   - Process document submissions
   - Run LOKI validation
   - Format results for Slack
   - Send responses

3. Add interactive features
   - Buttons for actions
   - Modal dialogs for input
   - Message formatting
   - File upload handling
   - Thread responses

4. Deploy and configure
   - Deploy webhook endpoint
   - Configure Slack app URLs
   - Test in workspace
   - Handle errors gracefully
   - Document usage

5. Create user guide
   - Installation instructions
   - Command documentation
   - Usage examples
   - Troubleshooting
```

### Workflow 3: Python SDK Development

```
1. Design SDK structure
   - Client class design
   - Method signatures
   - Error handling
   - Configuration options
   - Type hints

2. Implement core functionality
   - API client wrapper
   - Validation methods
   - Correction methods
   - Async support
   - Error handling

3. Add convenience features
   - Batch processing
   - File handling
   - Result parsing
   - Retry logic
   - Caching

4. Package and distribute
   - Setup.py configuration
   - README documentation
   - PyPI upload
   - Version tagging
   - Changelog

5. Create examples
   - Basic usage
   - Advanced features
   - Error handling
   - Async patterns
   - Best practices
```

### Workflow 4: Webhook Configuration

```
1. Design webhook system
   - Event types
   - Payload structure
   - Security (HMAC)
   - Retry logic
   - Error handling

2. Implement webhook endpoints
   - Receive webhook POST
   - Validate signature
   - Process event
   - Return response
   - Handle errors

3. Add reliability
   - Retry on failure
   - Idempotency
   - Dead letter queue
   - Logging
   - Monitoring

4. Document webhooks
   - Event catalog
   - Payload examples
   - Security setup
   - Testing guide
   - Troubleshooting

5. Create testing tools
   - Webhook simulator
   - Payload validator
   - Debug mode
   - Test suite
```

## Example Prompts

### REST API Implementation
```
Please create a production-ready REST API for LOKI using FastAPI.

Requirements:
1. Endpoints:
   - POST /validate - Validate document
   - POST /correct - Validate and correct document
   - GET /modules - List available modules
   - GET /health - Health check

2. Features:
   - API key authentication
   - Rate limiting (100 req/min)
   - Request validation
   - Comprehensive error handling
   - OpenAPI documentation

3. Create in: /api/main.py

Include:
- Full implementation
- Authentication middleware
- Error handlers
- Swagger UI setup
- Deployment guide
```

### Slack Integration
```
Build a Slack integration for LOKI that allows users to validate
documents directly in Slack.

Features needed:
1. Slash command: /loki-validate [text or file]
2. Interactive components:
   - Module selection
   - Correction options
   - Result viewing
3. File upload support
4. Threaded responses
5. Error handling

Provide:
- Slack app manifest
- Webhook handler code
- Deployment instructions
- User documentation
```

### Python SDK
```
Create a Python SDK for LOKI with the following:

Core features:
1. LokiClient class
2. Methods:
   - validate_document()
   - correct_document()
   - validate_batch()
3. Async support
4. Error handling
5. Type hints
6. Comprehensive docs

Structure:
- loki_sdk/
  - __init__.py
  - client.py
  - models.py
  - exceptions.py
  - async_client.py
- setup.py
- README.md
- examples/

Make it production-ready and PyPI-publishable.
```

### Email Integration
```
Create an email gateway integration that:
1. Receives emails at loki@example.com
2. Extracts document content
3. Runs LOKI validation
4. Sends compliance report back
5. Handles attachments (PDF, DOCX, TXT)

Technical requirements:
- Use SendGrid inbound parse
- Support multiple document types
- Format email responses nicely
- Handle errors gracefully
- Log all activities

Provide complete implementation and setup guide.
```

### Client Implementation Support
```
A client wants to integrate LOKI into their document management system.
Their stack: Node.js backend, React frontend.

Please provide:
1. Node.js integration guide
2. Example backend API wrapper
3. React component for document validation
4. Error handling patterns
5. Performance optimization tips
6. Security best practices

Include complete code examples and deployment guide.
```

## Success Criteria

### API Quality
- RESTful design principles
- Clear documentation
- Proper error handling
- Security best practices
- Performance optimization
- Comprehensive testing

### Integration Reliability
- Robust error handling
- Retry mechanisms
- Logging and monitoring
- Graceful degradation
- Clear user feedback

### SDK Quality
- Intuitive API design
- Complete documentation
- Type safety
- Good test coverage
- Active maintenance
- Version compatibility

### Client Support
- Clear documentation
- Working examples
- Responsive support
- Best practices guidance
- Security recommendations

## Integration with LOKI Codebase

### FastAPI Implementation Example
```python
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import sys
sys.path.append('backend')
from backend.core.engine import ComplianceEngine
from backend.core.corrector import DocumentCorrector

app = FastAPI(title="LOKI API", version="1.0.0")
api_key_header = APIKeyHeader(name="X-API-Key")

class ValidationRequest(BaseModel):
    text: str
    document_type: str
    modules: List[str]

class ValidationResponse(BaseModel):
    status: str
    violations: List[dict]
    modules: dict

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-secure-api-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/validate", response_model=ValidationResponse)
async def validate_document(
    request: ValidationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Validate document against compliance modules."""
    try:
        engine = ComplianceEngine()
        results = engine.validate_document(
            text=request.text,
            document_type=request.document_type,
            modules=request.modules
        )
        return results['validation']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### Python SDK Example
```python
# loki_sdk/client.py
import requests
from typing import List, Dict, Optional

class LokiClient:
    """Python SDK for LOKI Compliance API."""

    def __init__(self, api_key: str, base_url: str = "https://api.loki.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def validate_document(
        self,
        text: str,
        document_type: str,
        modules: List[str]
    ) -> Dict:
        """
        Validate document against compliance modules.

        Args:
            text: Document text to validate
            document_type: Type of document
            modules: List of compliance modules

        Returns:
            Validation results dictionary

        Raises:
            LokiAPIError: If validation fails
        """
        response = self.session.post(
            f"{self.base_url}/validate",
            json={
                "text": text,
                "document_type": document_type,
                "modules": modules
            }
        )
        response.raise_for_status()
        return response.json()

    def correct_document(
        self,
        text: str,
        document_type: str,
        modules: List[str]
    ) -> Dict:
        """
        Validate and correct document.

        Args:
            text: Document text to correct
            document_type: Type of document
            modules: List of compliance modules

        Returns:
            Correction results with corrected text
        """
        response = self.session.post(
            f"{self.base_url}/correct",
            json={
                "text": text,
                "document_type": document_type,
                "modules": modules
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = LokiClient(api_key="your-api-key")
results = client.validate_document(
    text="Document text",
    document_type="financial",
    modules=["fca_uk", "gdpr_uk"]
)
```

### Slack Integration Example
```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sys
sys.path.append('backend')
from backend.core.engine import ComplianceEngine

app = App(token="xoxb-your-token")
engine = ComplianceEngine()

@app.command("/loki-validate")
def handle_validate(ack, command, respond):
    """Handle /loki-validate slash command."""
    ack()

    text = command['text']
    if not text:
        respond("Please provide text to validate.")
        return

    # Run validation
    try:
        results = engine.validate_document(
            text=text,
            document_type="general",
            modules=["fca_uk", "gdpr_uk"]
        )

        # Format response
        status = results['validation']['status']
        violations = results['validation']['violations']

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"Validation: {status}"}
            }
        ]

        if violations:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{len(violations)} violations found*"}
            })

        respond(blocks=blocks)

    except Exception as e:
        respond(f"Error: {str(e)}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, "xapp-your-token")
    handler.start()
```

### Webhook Handler Example
```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
from backend.core.engine import ComplianceEngine

app = FastAPI()
engine = ComplianceEngine()

WEBHOOK_SECRET = "your-webhook-secret"

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhook/validate")
async def webhook_validate(request: Request):
    """Handle validation webhook."""
    # Verify signature
    signature = request.headers.get("X-Webhook-Signature")
    payload = await request.body()

    if not verify_signature(payload, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Process webhook
    data = await request.json()
    text = data.get('text')
    callback_url = data.get('callback_url')

    # Run validation
    results = engine.validate_document(
        text=text,
        document_type=data.get('document_type', 'general'),
        modules=data.get('modules', ['fca_uk'])
    )

    # Send results to callback URL
    # (implementation depends on client requirements)

    return {"status": "processing"}
```

## API Documentation Template

```yaml
openapi: 3.0.0
info:
  title: LOKI Compliance API
  version: 1.0.0
  description: Document compliance validation and correction

servers:
  - url: https://api.loki.com/v1

security:
  - ApiKeyAuth: []

paths:
  /validate:
    post:
      summary: Validate document
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                text:
                  type: string
                document_type:
                  type: string
                modules:
                  type: array
                  items:
                    type: string
      responses:
        200:
          description: Validation results
        400:
          description: Invalid request
        403:
          description: Authentication failed
        500:
          description: Internal error

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

## Best Practices

1. **Security first** - Always implement proper authentication
2. **Error handling** - Provide clear, actionable error messages
3. **Documentation** - Comprehensive docs with examples
4. **Testing** - Thorough testing before deployment
5. **Monitoring** - Log and monitor all integrations
6. **Performance** - Optimize for speed and efficiency
7. **Versioning** - Use semantic versioning for APIs and SDKs
8. **Compatibility** - Maintain backward compatibility
9. **Rate limiting** - Protect against abuse
10. **Support** - Provide clear support channels

## Notes
- Focus on production-ready, scalable solutions
- Collaborate with performance-optimizer for optimization
- Work with compliance-engineer to understand LOKI capabilities
- Support customer-success with integration documentation
- Maintain security best practices in all implementations
- Keep SDKs and APIs well-documented and tested
