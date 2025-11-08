# LOKI Claude Code Skills

Comprehensive expertise skills for LOKI document compliance system development.

## Available Skills

### 1. compliance-gate-developer
**Expert in creating and maintaining compliance gates**

Files:
- `skill.md` - Gate creation methodology and architecture
- `gate-design-patterns.md` - Comprehensive regex pattern library
- `testing-framework.md` - Testing strategies and frameworks
- `regulatory-research.md` - How to research UK regulations
- `accuracy-optimization.md` - Reducing false positives

**Use when:**
- Creating new compliance gates
- Debugging existing gate patterns
- Optimizing gate accuracy
- Researching regulatory requirements

### 2. uk-employment-law
**Specialist in UK employment law and ACAS Code**

Files:
- `skill.md` - UK employment law overview
- `acas-guidance.md` - ACAS Code interpretation
- `tribunal-procedures.md` - Employment tribunal process
- `2025-updates.md` - Employment Rights Bill changes
- `scottish-differences.md` - Scots law employment specifics

**Use when:**
- Validating HR documents
- Creating disciplinary procedure gates
- Understanding tribunal risks
- Checking ACAS Code compliance

### 3. scottish-legal-system
**Expert in Scots law differences from English law**

Files:
- `skill.md` - Scots law overview
- `contract-law.md` - Scots contract law differences
- `employment.md` - Scottish employment specifics
- `regulatory-bodies.md` - Scottish regulators
- `legal-precedents.md` - Key Scottish cases

**Use when:**
- Validating Scottish legal documents
- Understanding jurisdictional differences
- Creating Scotland-specific gates

### 4. document-correction-expert
**Specialist in auto-correction and template design**

Files:
- `skill.md` - Auto-correction strategies
- `template-design.md` - Building compliance templates
- `context-analysis.md` - Document type detection
- `quality-assurance.md` - Ensuring correction accuracy
- `deterministic-synthesis.md` - Reproducible corrections

**Use when:**
- Implementing auto-correction features
- Creating correction templates
- Ensuring deterministic results
- Quality-checking corrections

### 5. api-integration-master
**Expert in LOKI API integration patterns**

Files:
- `skill.md` - LOKI API integration patterns
- `authentication.md` - OAuth2/JWT implementation
- `error-handling.md` - Graceful error recovery
- `performance.md` - Optimization strategies
- `webhooks.md` - Event-driven integration

**Use when:**
- Integrating LOKI into applications
- Building API clients
- Implementing authentication
- Optimizing API performance

### 6. b2b-saas-development
**Specialist in B2B SaaS architecture**

Files:
- `skill.md` - B2B SaaS architecture
- `multi-tenancy.md` - Tenant isolation patterns
- `billing.md` - Subscription management
- `analytics.md` - Usage tracking and reporting
- `customer-management.md` - Onboarding and support

**Use when:**
- Architecting LOKI for SaaS
- Implementing multi-tenancy
- Building billing systems
- Creating customer dashboards

## Quick Reference

### Module Locations
- FCA UK: `backend/modules/fca_uk/`
- GDPR UK: `backend/modules/gdpr_uk/`
- Tax UK: `backend/modules/tax_uk/`
- NDA UK: `backend/modules/nda_uk/`
- HR Scottish: `backend/modules/hr_scottish/`

### Core Components
- Gate Registry: `backend/core/gate_registry.py`
- Validators: `backend/core/`
- Tests: `backend/tests/semantic/`
- Fixtures: `backend/tests/semantic/gold_fixtures/`

### Key Patterns

**Creating a new gate:**
1. Research regulation (use `compliance-gate-developer/regulatory-research.md`)
2. Design patterns (use `compliance-gate-developer/gate-design-patterns.md`)
3. Implement gate class (use `compliance-gate-developer/skill.md`)
4. Write tests (use `compliance-gate-developer/testing-framework.md`)
5. Optimize accuracy (use `compliance-gate-developer/accuracy-optimization.md`)

**Validating employment documents:**
1. Understand ACAS Code (use `uk-employment-law/acas-guidance.md`)
2. Check tribunal risks (use `uk-employment-law/tribunal-procedures.md`)
3. Consider Scottish law (use `scottish-legal-system/employment.md`)
4. Apply gates from `hr_scottish` module

**Implementing corrections:**
1. Analyze document context (use `document-correction-expert/context-analysis.md`)
2. Design templates (use `document-correction-expert/template-design.md`)
3. Ensure determinism (use `document-correction-expert/deterministic-synthesis.md`)
4. QA corrections (use `document-correction-expert/quality-assurance.md`)

## Skill Activation

Skills are automatically available in Claude Code. Reference them in your work:

```
I need to create a new FCA compliance gate. Using the compliance-gate-developer skill, help me:
1. Research FCA COBS 4.2.1R
2. Design detection patterns
3. Implement the gate class
4. Write comprehensive tests
```

## Contributing

When updating skills:
1. Maintain clear structure
2. Include code examples from LOKI codebase
3. Cite specific regulations
4. Provide real-world scenarios
5. Keep examples up-to-date

## Version

Skills Version: 1.0.0
Last Updated: 2025-01-08
Compatible with: LOKI v1.0+
