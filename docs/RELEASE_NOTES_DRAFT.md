# LOKI Universal Synthesis – Release Notes (Draft)

Branch: feature/refusal-aware-synthesis
Scope: Backend universal synthesis refactor with domain-based snippet mapping

## Overview
- Introduces a universal, domain-driven synthesis system usable across all modules and gates without code changes.
- Key concepts: six compliance domains (risk_warning, disclosure, procedure, definition, consent, limitation) and an explicit module→gate taxonomy.
- Benefits: removes hardcoded snippets, standardises insertion points (start/section/end), supports future modules (HIPAA, SOX, PCI-DSS, MiFID II, etc.).

## Code changes (key files)
- backend/core/synthesis/domain_templates.py (NEW)
  - DOMAIN_TEMPLATES: domain variants with templates and default_context.
  - MODULE_TAXONOMY: ~85 gates across fca_uk, gdpr_uk, hr_scottish, nda_uk, tax_uk using gate_config().
  - PRIORITY_MAP, default insertion_point by domain, explicit legal_citation and severity.
- backend/core/synthesis/snippets.py (MODIFIED)
  - Imports templates/taxonomy; build_snippet() reworked for variant resolution and context merge.
  - SPECIAL_SNIPPETS preserved; legacy compatibility via .snippets cache and format_snippet().
- backend/core/synthesis/snippet_mapper.py (MODIFIED)
  - UniversalSnippetMapper prioritises SPECIAL_SNIPPETS; maps gates via taxonomy (domain/variant/context).
- backend/core/synthesis/engine.py (MODIFIED)
  - Iterative assembler with sanitizer, respects insertion_point; uses original validation in iteration 1, revalidates thereafter.

## Testing performed
- Pytest commands:
  - Run fast tests: pytest -q
  - Run synthesis suite only: pytest -q tests/test_synthesis.py
- Current branch status:
  - Synthesis tests: passing with iterative assembly and insertion checks (see tests/test_synthesis.py).
  - Universal tests: pass for cross-module gates (FCA risk warning, FOS, GDPR lawful basis).
  - Manual sanity: validated on FCA promotions, GDPR privacy notices, NDA agreements.

Notes:
- tests/test_synthesis.py verifies:
  - snippet application order/iteration metadata
  - multi-module synthesis (FCA + GDPR)
  - insertion point handling (start/section/end)

## Deployment checklist

Pre-reqs
- Environment variables/API keys configured (see API_KEY_SETUP.md).
- Vercel project linked to this repo/workspace; ensure Python runtime supported for /api.
- Confirm domain_templates.py is included in deployment package (no .dockerignore/.vercelignore excluding it).

Manual Vercel deploy (from repo root)
1) Ensure branch is pushed and CI green: git push origin feature/refusal-aware-synthesis
2) Login and link (one-time if not linked):
   - vercel login
   - vercel link
3) Deploy preview:
   - vercel --prod=false
   - Capture preview URL and perform smoke tests
4) Promote to production:
   - vercel --prod

Post-launch verification
- API health: GET /api/health (or root route) returns 200 via vercel.json routing.
- Synthesis smoke test (preview/prod):
  - POST /api/index.py with minimal payload exercising FCA + GDPR gates; verify snippets appear and validation improves.
- Log/Audit checks:
  - Confirm audit.db or telemetry sink records synthesis runs without errors.
- Content checks:
  - Ensure special snippets render correctly (FCA risk warning, FOS, promotions approval, GDPR lawful basis).
- Regression spot-check:
  - Existing modules (hr_scottish, nda_uk, tax_uk) generate domain-mapped content; no missing templates.

Rollback plan
- Re-deploy previous stable commit on Vercel (Deployments tab → Promote), or vercel --prod with prior deployment ID.

Ownership
- Backend synthesis: Core team (LOKI).
- Compliance taxonomy: Codex/Legal review.

Changelog tag
- feat(synthesis): universal domain-based snippet mapping; explicit module taxonomy and insertion handling.
