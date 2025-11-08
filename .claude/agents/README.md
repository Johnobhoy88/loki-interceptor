# LOKI Claude Code Agent Workflows

This directory contains 7 specialized Claude Code agent workflows designed to support LOKI development, operations, and customer success.

## Agent Overview

### 1. Compliance Engineer (`compliance-engineer.md`)
**Purpose**: Develops, tests, and maintains compliance gates

**Key Capabilities**:
- Creates new compliance gates following LOKI architecture
- Tests regulatory accuracy against real-world scenarios
- Updates gates for legislative changes
- Optimizes detection patterns and reduces false positives
- Conducts comprehensive gate validation
- Maintains >95% accuracy on gold standard tests

**Typical Tasks**:
- Implementing new FCA/GDPR/Tax/NDA/HR gates
- Updating gates for regulatory changes
- Optimizing gate performance
- Analyzing false positive/negative rates
- Creating test fixtures and validation suites

**Tools**: Gate Registry, Gate Module Base, Semantic Analyzer, All Compliance Modules

---

### 2. Document Auditor (`document-auditor.md`)
**Purpose**: Reviews documents and generates comprehensive compliance reports

**Key Capabilities**:
- Performs multi-module document validation
- Generates detailed compliance reports with executive summaries
- Identifies and classifies compliance risks
- Suggests specific, actionable corrections
- Produces complete audit trails for regulatory reporting
- Supports batch document processing

**Typical Tasks**:
- Comprehensive document compliance audits
- Batch document review and reporting
- Risk assessment and prioritization
- Audit trail generation for regulatory compliance
- Correction quality analysis

**Tools**: Compliance Engine, Correction Synthesizer, Audit Logger, All Modules

---

### 3. Legal Researcher (`legal-researcher.md`)
**Purpose**: Monitors regulatory changes and maintains legal accuracy

**Key Capabilities**:
- Tracks UK regulatory body updates (FCA, ICO, HMRC, ACAS)
- Researches and interprets new legislation
- Validates gates against case law and current regulations
- Documents regulatory changes and LOKI impacts
- Researches sector-specific compliance requirements
- Provides implementation guidance for regulatory updates

**Typical Tasks**:
- Monitoring FCA Policy Statements and guidance
- Researching new UK legislation impact
- Validating gate legal accuracy
- Case law analysis and application
- Sector-specific regulatory research

**Tools**: Regulatory websites, WebSearch, WebFetch, Gate systems, Documentation

---

### 4. Integration Specialist (`integration-specialist.md`)
**Purpose**: Builds integrations, APIs, and SDKs for LOKI

**Key Capabilities**:
- Designs and implements REST APIs (FastAPI)
- Develops third-party integrations (Slack, Teams, email)
- Creates client SDKs (Python, Node.js)
- Configures webhook systems
- Provides integration implementation support
- Ensures security and performance best practices

**Typical Tasks**:
- Building production-ready REST APIs
- Creating Slack/Teams integrations
- Developing Python/Node.js SDKs
- Implementing webhook systems
- Supporting client integrations
- Creating API documentation

**Tools**: LOKI Core Systems, FastAPI, Slack/Teams APIs, SDK tools, API documentation

---

### 5. Performance Optimizer (`performance-optimizer.md`)
**Purpose**: Optimizes system performance and scalability

**Key Capabilities**:
- Profiles and optimizes gate execution times
- Reduces latency across validation pipeline
- Optimizes resource usage (API calls, memory, CPU)
- Implements caching strategies
- Optimizes database queries
- Enhances scalability for high-volume processing

**Typical Tasks**:
- Gate performance profiling and optimization
- System-wide latency reduction
- API call and token usage optimization
- Cache strategy implementation
- Database query optimization
- Load testing and benchmarking

**Tools**: cProfile, line_profiler, memory_profiler, Cache system, Database tools

---

### 6. Customer Success (`customer-success.md`)
**Purpose**: Ensures successful customer adoption and satisfaction

**Key Capabilities**:
- Designs effective onboarding workflows
- Creates comprehensive training materials
- Develops clear support documentation
- Writes practical use case guides
- Provides troubleshooting assistance
- Tracks customer success metrics

**Typical Tasks**:
- Creating onboarding guides and quick starts
- Developing training videos and courses
- Writing how-to guides and FAQs
- Building troubleshooting documentation
- Supporting customer issues
- Creating use case examples

**Tools**: Full LOKI access, Documentation tools, Training materials, Support systems

---

### 7. Sales Engineer (`sales-engineer.md`)
**Purpose**: Drives sales through technical demonstrations and POCs

**Key Capabilities**:
- Creates compelling industry-specific demos
- Develops proof of concept implementations
- Builds custom gates for prospect requirements
- Prepares executive and technical presentations
- Calculates and presents ROI analyses
- Addresses technical objections

**Typical Tasks**:
- Creating industry demos (financial, insurance, fintech, legal, HR)
- Developing POCs with prospect data
- Building custom gates for specific needs
- Preparing executive presentations
- Calculating ROI for prospects
- Technical sales support

**Tools**: Full LOKI stack, Demo materials, ROI calculator, Presentation templates

---

## How to Use These Agents

### In Claude Code CLI

To invoke an agent workflow, reference the agent file:

```bash
# Example: Get help from the Compliance Engineer
"I need to create a new FCA UK gate for Consumer Duty support requirements.
Please review the compliance-engineer agent workflow and help me implement this."

# Example: Request a document audit
"Please act as the Document Auditor and perform a comprehensive compliance
review of this financial document: [text]"

# Example: Build an integration
"Acting as the Integration Specialist, please create a REST API for LOKI
using FastAPI with the requirements in integration-specialist.md"
```

### Agent Collaboration

Agents are designed to work together:

- **Compliance Engineer** + **Legal Researcher**: New gate development with regulatory research
- **Document Auditor** + **Compliance Engineer**: Validation with gate improvement feedback
- **Performance Optimizer** + **Compliance Engineer**: Gate performance tuning
- **Integration Specialist** + **Customer Success**: API documentation and client support
- **Sales Engineer** + **Customer Success**: Demo creation and post-sale handoff
- **Legal Researcher** + **Sales Engineer**: Sector research for custom demos

## Agent Architecture

Each agent includes:

### 1. Clear Purpose and Objectives
- Well-defined role and responsibilities
- Specific goals and success criteria
- Areas of expertise

### 2. Core Responsibilities
- Detailed breakdown of duties
- Primary focus areas
- Key deliverables

### 3. Tools Available
- LOKI systems access
- External tools and resources
- Development environments
- Documentation and references

### 4. Typical Workflows
- Step-by-step process guides
- Common scenarios
- Best practices
- Decision frameworks

### 5. Example Prompts
- Ready-to-use prompt templates
- Real-world scenarios
- Expected outcomes
- Variations for different needs

### 6. Success Criteria
- Quality metrics
- Performance targets
- Accuracy requirements
- Delivery standards

### 7. Integration with LOKI
- Code examples
- File structure guidance
- Implementation patterns
- Testing requirements

### 8. Best Practices
- Guidelines and standards
- Common pitfalls to avoid
- Optimization tips
- Collaboration patterns

## LOKI System Overview

### Core Systems
- **Compliance Engine**: `backend/core/engine.py` - Main validation orchestrator
- **Async Engine**: `backend/core/async_engine.py` - Asynchronous processing
- **Document Corrector**: `backend/core/corrector.py` - Correction application
- **Correction Synthesizer**: `backend/core/correction_synthesizer.py` - Deterministic corrections
- **Gate Registry**: `backend/core/gate_registry.py` - Gate management
- **Audit System**: `backend/core/audit_log.py` - Compliance audit trails
- **Cache System**: `backend/core/cache.py` - Performance caching

### Compliance Modules
- **FCA UK**: `backend/modules/fca_uk/` - 51 rules across financial regulation
- **GDPR UK**: `backend/modules/gdpr_uk/` - 29 rules for data protection
- **Tax UK**: `backend/modules/tax_uk/` - 25 rules for HMRC compliance
- **NDA UK**: `backend/modules/nda_uk/` - 12 rules for contract law
- **HR Scottish**: `backend/modules/hr_scottish/` - 24 rules for employment law

### Total Coverage
- **141 Detection Rules**
- **83 Template Categories**
- **5 Compliance Modules**
- **>95% Accuracy Rate**
- **<5% False Positive Rate**

## Quick Reference

### For New Gate Development
→ Use **Compliance Engineer** agent

### For Regulatory Updates
→ Use **Legal Researcher** → **Compliance Engineer**

### For Document Review
→ Use **Document Auditor** agent

### For API/Integration Work
→ Use **Integration Specialist** agent

### For Performance Issues
→ Use **Performance Optimizer** agent

### For Customer Support
→ Use **Customer Success** agent

### For Sales/Demos
→ Use **Sales Engineer** agent

## Agent Files

| Agent | File | Size | Purpose |
|-------|------|------|---------|
| Compliance Engineer | `compliance-engineer.md` | 10.4 KB | Gate development & testing |
| Document Auditor | `document-auditor.md` | 13.2 KB | Document review & reporting |
| Legal Researcher | `legal-researcher.md` | 12.1 KB | Regulatory monitoring & research |
| Integration Specialist | `integration-specialist.md` | 17.0 KB | APIs, SDKs, integrations |
| Performance Optimizer | `performance-optimizer.md` | 19.1 KB | Performance & scalability |
| Customer Success | `customer-success.md` | 14.3 KB | Training & support |
| Sales Engineer | `sales-engineer.md` | 16.5 KB | Demos & POCs |

## Contributing

When extending or modifying agents:

1. **Maintain Structure**: Keep the standard agent template sections
2. **Add Examples**: Include clear, working examples
3. **Document Tools**: List all tools and systems the agent uses
4. **Define Success**: Clear success criteria and metrics
5. **Show Integration**: Demonstrate how agent works with LOKI codebase
6. **Test Workflows**: Validate all example prompts work
7. **Update README**: Keep this overview current

## Support

For questions about agents:
- Review the specific agent file for detailed guidance
- Check LOKI README for system documentation
- Consult code examples in agent files
- Reference test fixtures for validation examples

## Version

**Agent Framework Version**: 1.0
**LOKI Version**: Production Ready (141 rules, 5 modules)
**Last Updated**: 2025-11-08

---

**Built for Highland AI's LOKI Interceptor**
*Intelligent Compliance, Powered by Claude*
