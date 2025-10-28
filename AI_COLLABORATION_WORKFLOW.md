# Multi-AI Development Workflow

**Team**: User (PM/Tester) + Claude (Integration Lead) + Codex (Validation Engineer) + Copilot (Documentation Lead)

## Roles & Responsibilities

### User (Project Manager / Manual Tester)
- **Primary**: Set requirements, prioritize work, manual testing, git operations
- **Tools**: Terminal, manual test cases, git commands
- **Output**: Requirements docs, test scenarios, git commits/PRs

### Claude (Integration Lead)
- **Primary**: Architecture, cross-module integration, complex refactoring
- **Strengths**: Read/Edit/Write operations, parallel tool execution, planning
- **Tools**: All file tools, Bash, TodoWrite for task tracking
- **Output**: Code changes, integration fixes, architecture docs

### Codex (Validation Engineer)
- **Primary**: Testing, validation, bug fixes, coverage analysis
- **Strengths**: Test execution, error diagnosis, systematic validation
- **Tools**: pytest, compileall, coverage tools
- **Output**: Test results, bug reports, validation coverage

### Copilot (Documentation Lead)
- **Primary**: Git operations, commit messages, technical documentation
- **Strengths**: GPT-5 reasoning, git MCP server access, production-quality writing
- **Tools**: Git commands via MCP, markdown generation
- **Output**: Commit messages, PRs, architectural documentation

---

## Workflow Patterns

### Pattern 1: Parallel Feature Development

**Scenario**: Multiple independent tasks can run simultaneously

**Steps**:
1. **User** breaks down feature into independent tasks
2. **Claude** creates task division using TodoWrite
3. **Claude + Codex + Copilot** work in parallel:
   - Claude: Core implementation
   - Codex: Test harness setup
   - Copilot: Documentation outline
4. **User** reviews outputs and triggers next phase

**Example** (Universal Synthesis):
```
User: "Complete the universal synthesis refactor"

Claude:
- Reconcile SnippetRegistry (snippets.py)
- Fix engine integration (engine.py)
- Update snippet_mapper (snippet_mapper.py)

Codex:
- Create comprehensive test suite
- Validate all 85 gates
- Generate coverage report

Copilot:
- Review git diff for all files
- Draft production commit message
- Document architecture decisions
```

### Pattern 2: Sequential Dependency Chain

**Scenario**: Tasks must complete in order

**Steps**:
1. **Claude** completes foundational work
2. **Claude** signals completion to **User**
3. **User** triggers **Codex** validation
4. **Codex** reports results to **User**
5. **User** triggers **Copilot** documentation
6. **Copilot** delivers final docs

**Example** (Test Fix):
```
Claude: Fix SnippetRegistry → "Reconciliation complete, ready for testing"
↓
User: Trigger Codex → "Run validation"
↓
Codex: Run tests → "29/29 tests PASS, coverage 85/85"
↓
User: Trigger Copilot → "Create commit message"
↓
Copilot: Generate docs → "COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt created"
```

### Pattern 3: Iterative Debugging

**Scenario**: Complex bug requiring multiple fix attempts

**Steps**:
1. **Codex** identifies failure with pytest
2. **User** shares error with **Claude**
3. **Claude** implements fix
4. **User** triggers **Codex** re-test
5. Repeat 2-4 until tests pass
6. **Copilot** documents the fix

---

## Git Workflow

### Pre-Commit Checklist
- [ ] All tests pass (run by **Codex**)
- [ ] Code compiles without errors
- [ ] TodoWrite list is clean (no stale items)
- [ ] Commit message drafted (by **Copilot**)

### Commit Protocol

**Step 1: Code Complete**
```bash
# User runs compilation check
python3 -m compileall backend/core/synthesis
```

**Step 2: Testing** (Codex executes)
```bash
# Run all relevant test suites
python3 -m pytest tests/test_synthesis.py -v
python3 -m pytest tests/test_universal_synthesis.py -v

# Verify coverage
python3 -c "
from core.synthesis import SnippetRegistry
registry = SnippetRegistry()
print(f'Gates: {len(registry.snippets)}')
print(f'Modules: {list(registry.module_catalog.keys())}')
"
```

**Step 3: Documentation** (Copilot executes)
```bash
# Review all changes
git status
git diff backend/core/synthesis/

# Generate commit message
# Output: COMMIT_MESSAGE_<FEATURE>.txt
```

**Step 4: Commit** (User executes)
```bash
# Review staged changes
git status

# Add all synthesis changes
git add backend/core/synthesis/

# Commit with Copilot's message
git commit -F COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt

# Verify commit
git log -1 --stat
```

**Step 5: Push & PR** (User executes)
```bash
# Push to feature branch
git push -u origin feature/compliance-automation-loop

# Create PR (via GitHub UI or gh CLI)
gh pr create \
  --title "Add universal synthesis system" \
  --body-file COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt \
  --base main
```

---

## Communication Protocol

### Status Updates

**Format**: `[AI_NAME] [STATUS] [SUMMARY]`

**Examples**:
```
Claude: ✓ COMPLETE - SnippetRegistry reconciliation (26→29 tests passing)
Codex: ✓ COMPLETE - All tests validated (33/33 PASS, 85/85 gates)
Copilot: ✓ COMPLETE - Commit message created (COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt)
```

### Error Reporting

**Format**: `[AI_NAME] ✗ ERROR - [ISSUE] - [FILE:LINE]`

**Examples**:
```
Codex: ✗ ERROR - AttributeError '_count_failures' - tests/test_synthesis.py:313
Claude: ✓ FIX - Replaced with _extract_failures() - snippets.py:180
Codex: ✓ RETEST - Test now passing
```

### Handoff Protocol

**Format**: `[AI_NAME] → [NEXT_AI]: [TASK]`

**Examples**:
```
Claude → Codex: Reconciliation complete, please validate all tests
Codex → Copilot: 33/33 tests pass, ready for commit message
Copilot → User: Commit message ready in COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt
```

---

## Testing Standards

### Required Test Levels

1. **Unit Tests** (per module)
   - `tests/test_synthesis.py` (29 tests)
   - `tests/test_universal_synthesis.py` (4 tests)

2. **Integration Tests**
   - End-to-end synthesis flow
   - Multi-module scenarios

3. **Coverage Requirements**
   - 85/85 gates must have snippets
   - All 5 modules represented
   - Special snippets preserved

### Test Execution Order

```bash
# 1. Compilation (fast)
python3 -m compileall backend/core/synthesis

# 2. Unit tests (medium)
python3 -m pytest tests/test_universal_synthesis.py -v

# 3. Integration tests (slow)
python3 -m pytest tests/test_synthesis.py -v

# 4. Coverage check (fast)
python3 -c "from core.synthesis import SnippetRegistry; r=SnippetRegistry(); print(f'Coverage: {len(r.snippets)}/85 gates')"
```

---

## Conflict Resolution

### File Conflicts

**If Claude & Codex modify same file**:
1. **Claude** works on implementation logic
2. **Codex** works on test assertions
3. **User** manually merges if needed

**Prevention**: Assign clear file ownership
- Claude: `backend/core/synthesis/*.py` (implementation)
- Codex: `tests/test_*.py` (tests)
- Copilot: `*.md`, `*.txt` (docs)

### Merge Strategy

```bash
# User resolves conflicts
git status  # See conflicts
git diff    # Review differences

# Accept changes from both
git checkout --ours backend/core/synthesis/snippets.py
git checkout --theirs tests/test_synthesis.py

# Or manual merge
code backend/core/synthesis/snippets.py  # Edit manually

git add .
git commit
```

---

## Current Session Summary

**Date**: 2025-10-17
**Feature**: Universal Synthesis System
**Branch**: `feature/compliance-automation-loop`

**Completed Work**:

| AI | Task | Status | Output |
|---|---|---|---|
| Claude | SnippetRegistry reconciliation | ✓ COMPLETE | snippets.py, engine.py, snippet_mapper.py |
| Codex | Test validation & fixes | ✓ COMPLETE | 33/33 tests PASS, 85/85 gates |
| Copilot | Commit message & docs | ✓ COMPLETE | COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt |

**Files Modified**:
- ✓ `backend/core/synthesis/domain_templates.py` (NEW, 1,518 lines)
- ✓ `backend/core/synthesis/snippets.py` (MODIFIED)
- ✓ `backend/core/synthesis/engine.py` (MODIFIED)
- ✓ `backend/core/synthesis/snippet_mapper.py` (MODIFIED)
- ✓ `tests/test_synthesis.py` (MODIFIED - 3 assertions fixed)

**Test Results**:
- ✅ 29/29 synthesis tests PASS
- ✅ 4/4 universal tests PASS
- ✅ 85/85 gate coverage
- ✅ All 5 modules validated

**Next Steps**:
1. User reviews all changes
2. User commits with: `git commit -F COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt`
3. User pushes: `git push -u origin feature/compliance-automation-loop`
4. User creates PR to main

---

## Quick Reference Commands

### For User
```bash
# Check what changed
git status
git diff --stat

# Run all tests
python3 -m pytest tests/ -v

# Commit with AI-generated message
git add backend/core/synthesis/ tests/
git commit -F COMMIT_MESSAGE_UNIVERSAL_SYNTHESIS.txt

# Push and create PR
git push -u origin feature/compliance-automation-loop
gh pr create --fill
```

### For Claude (via User)
```python
# Check syntax
python3 -m compileall backend/core/synthesis

# Quick integration test
from core.synthesis import SnippetRegistry
r = SnippetRegistry()
print(f"Loaded {len(r.snippets)} snippets")
```

### For Codex (via User)
```bash
# Run specific test
python3 -m pytest tests/test_synthesis.py::TestIntegration -v

# Coverage report
python3 -m pytest --cov=backend/core/synthesis tests/
```

### For Copilot (via User)
```bash
# Review changes for commit message
git log --oneline -5
git diff main..HEAD --stat

# Check PR readiness
gh pr checks
```
