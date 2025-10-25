# Adding New Compliance Modules to LOKI

The universal synthesiser (sanitiser + snippet mapper) is designed to work with new modules
with almost no code changes.  Follow the steps below to register a new module such as HIPAA,
SOX or PCI DSS.

## 1. Create Your Module & Gates

1. Add a folder under `backend/modules/<module_name>`.
2. Define gate classes that implement a `check(text, document_type)` method.
3. Each gate should expose metadata:
   - `severity`: CRITICAL / HIGH / MEDIUM / LOW
   - `legal_source`: citation or guidance reference
4. Register gates in the module’s `module.py` similar to the existing modules.

## 2. Provide Domain Metadata (optional but recommended)

Gates can include a `domain` attribute or use naming conventions that the universal snippet
mapper can infer.  Domains currently used:

- `disclosure`
- `risk_warning`
- `consent`
- `procedure`
- `definition`
- `limitation`

If a gate does not specify a domain the mapper infers one from the gate ID/message.

## 3. Sanitiser Integration

The sanitiser inspects gate failures at runtime to determine which pattern categories to apply.
To help it adapt to new modules ensure gate failure dictionaries include:

- `gate_id` (e.g., `hipaa_us:phi_disclosure`)
- `message` / `suggestion`
- `excerpt` (optional)

The sanitiser extracts keywords (e.g., “guaranteed”, “everyone”, “no approval”) and applies
category-specific replacements.

## 4. Snippet Mapping Flow

1. **Direct match** – if an explicit snippet exists for the gate it is used.
2. **Domain match** – otherwise the mapper selects a domain template and variant.
3. **Metadata fallback** – if no domain is available the mapper generates a snippet using the
   gate’s own metadata (legal source + suggestion).

To supply module-specific context (e.g., contact details), add entries to
`SnippetRegistry.module_catalog` or pass details via the synthesis context.

## 5. Testing

Add unit or regression tests that instantiate your module, trigger gate failures, and ensure the
sanitiser + mapper produce sensible outputs.  The helper `tests/test_universal_synthesis.py`
contains examples with fake gates.

## 6. When to Add Custom Snippets

Only add explicit snippets when:

- The domain template cannot capture mandatory wording (e.g., legally mandated paragraphs).
- Multiple gates in the same domain require distinct wording.

Otherwise rely on the domain templates to maximise reuse.

## 7. Summary

1. Define gates with metadata.
2. Let the sanitiser learn from failure outputs.
3. Rely on domain templates for snippets.
4. Provide additional context via synthesis `context` or module catalogue entries.

With these steps, new compliance modules can be plugged into LOKI without modifying the
sanitiser, snippet mapper, or synthesis engine.
