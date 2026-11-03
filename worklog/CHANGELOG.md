# Append-only engineering log

## GOV-PROTECTED-BOOTSTRAP-001 — v0.1.0-prototype
- UTC: 2026-10-25T00:40:00Z
- Issue: GOV-PROTECTED-001
- Completed: independent validator prototype, manual SHA-driven workflow, static tests and threat model
- Files: AGENTS.md; docs/THREAT_MODEL.md; validator/check_candidate.py; .github/workflows/structural-validation.yml; tests/test_static.py
- Evidence: docs/THREAT_MODEL.md (design only; not actual trusted execution)
- Status: IMPLEMENTED; Gate A BLOCKED
- Baseline: initial protected-repo README on main (precise SHA to be recorded in next entry)

## GOV-PROTECTED-TEST-002 — v0.1.1-prototype
- UTC: 2026-10-25T01:06:37.644Z
- Issue: GOV-PROTECTED-001
- Completed: Owned positive/negative tests and PR-only CI workflow
- Files: tests/test_independent_contract.py; .github/workflows/self-test.yml
- Evidence: PR #1, pending cloud CI
- Status: IMPLEMENTED; Gate A BLOCKED
- Baseline: 889cbfa531801d44f987a76208454db0981f00b0
- Limitation: tests/workflow committed before this log entry; per-commit append-only policy not yet enforced for bootstrap.

## GOV-PROTECTED-SOURCE-003 — v0.1.2-prototype
- UTC: 2026-10-25T02:00:00Z
- Issue: GOV-PROTECTED-001
- Completed: added fixed SHA source PR #6 validation step on PR CI, fetching Git objects only
- Files: .github/workflows/self-test.yml
- Evidence: PR #1 workflow, online execution pending
- Status: IMPLEMENTED; Gate A BLOCKED; origin NOT_ATTESTED
- Baseline: f84f7da81b0f11958519e80b71983c81831f9777
- Limitation: this was appended after workflow file commit; per-commit governance remains NOT VERIFIED.

## GOV-PROTECTED-HARDEN-004 — v0.1.3-prototype
- UTC: 2026-10-25T02:18:00Z
- Issue: GOV-PROTECTED-001
- Completed: enforce schema/timestamp/path checks; five strict-record positive/negative tests
- Files: validator/check_candidate.py; tests/test_negative_contract.py
- Evidence: PR #1, CI pending
- Status: IMPLEMENTED; Gate A BLOCKED/UNVERIFIED
- Baseline: a052d57ba822a6841cd3b1a080749524f2f92882
- Limitation: file edits were sequential GitHub commits; per-commit worklog coverage not yet satisfied, no historical log rewritten.

## GOV-PROTECTED-002-REV-001

```json
{
  "author_role": "Codex",
  "baseline_sha": "26026250d7ba49f29349a706a27676827af861d7",
  "code_files": [
    "validator/check_candidate.py",
    "validator/utc_reference.py",
    "tests/test_independent_contract.py",
    "tests/test_audit_hardening.py",
    "tests/test_utc_reference.py",
    ".github/workflows/self-test.yml",
    ".github/workflows/structural-validation.yml",
    "docs/ADR-002-AUDIT-BOUNDARY.md",
    "docs/evidence/GOV-PROTECTED-002-tests.json"
  ],
  "completed_items": [
    "Preserve legacy Git history and both journal prefixes; LEGACY_AUDIT_EXCEPTION / NOT_ATTESTED only through fixed 26026250 boundary",
    "Enforce nondecreasing post-boundary UTC and zero future tolerance; fixed TLS Date source cross-checked with executor UTC; source failure rejects",
    "Reject unknown/self/future correction references, duplicate IDs and duplicate code/evidence paths",
    "Require exact per-commit diff and same-commit JSONL/Markdown append; no skipped intermediate commit or schema-1 extension",
    "Reject shallow/missing objects/grafts; disable replacements and lazy fetch; fetch full ancestry without source checkout",
    "60 Python 3.12 unittest cases passed, exit 0; cross-repository source 08bcc423 structure passes, NOT_ATTESTED",
    "Keep CI unprivileged and candidate-controlled; no GitHub App/Ruleset/main/source PR modification; Gate A BLOCKED/UNVERIFIED"
  ],
  "correction_of": null,
  "entry_id": "GOV-PROTECTED-002-REV-001",
  "evidence_paths": [
    "docs/evidence/GOV-PROTECTED-002-tests.json",
    "docs/ADR-002-AUDIT-BOUNDARY.md",
    "tests/test_audit_hardening.py",
    "tests/test_utc_reference.py"
  ],
  "issue_id": "GOV-PROTECTED-002",
  "schema_version": "2.0",
  "status": "TESTED",
  "summary": "Implement owner-approved fixed audit boundary, segmented real UTC, correction/identity/path integrity and complete ancestry checks; 60 synthetic tests pass.",
  "timestamp_utc": "2026-10-25T02:02:37.819625Z",
  "version": "0.2.0-audit-candidate"
}
```

## GOV-PROTECTED-003-PREFLIGHT-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "6912bd8840df328df184a5a5ec443642a4a3b808",
  "code_files": [
    ".github/workflows/issuer-preflight.yml",
    "docs/ISSUER-READINESS.md"
  ],
  "completed_items": [
    "Document independently administered issuer requirements and non-attestation boundary",
    "Add only unprivileged PR workflow with offline unit tests and no protected check issuance",
    "Preserve historical audit and gate A restrictions"
  ],
  "correction_of": null,
  "entry_id": "GOV-PROTECTED-003-PREFLIGHT-001",
  "evidence_paths": [
    "docs/ISSUER-READINESS.md"
  ],
  "issue_id": "GOV-PROTECTED-003",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Add credential-free candidate-owned issuer readiness preflight and protected-executor runbook; no App key, token or trusted check deployed.",
  "timestamp_utc": "2026-10-26T08:06:04.107Z",
  "version": "0.3.0-preflight-candidate"
}
```

## GOV-PROTECTED-003-CONTRACT-002

```json
{
  "author_role": "LLM",
  "baseline_sha": "8607456fe4429671e6c27bc72440461ce60b2c59",
  "code_files": [
    "validator/issuer_evidence_contract.py",
    "tests/test_issuer_evidence_contract.py",
    "docs/ISSUER-EVIDENCE-CONTRACT.md"
  ],
  "completed_items": [
    "Add strict candidate-evidence input-format guard; no identity authentication or check issuance",
    "Add 12 synthetic positive/negative unit tests for mismatched app, repo, hashes and spoofed verdicts",
    "Preserve all legacy and post-boundary worklog bytes, and block Gate A"
  ],
  "correction_of": null,
  "entry_id": "GOV-PROTECTED-003-CONTRACT-002",
  "evidence_paths": [
    "docs/ISSUER-EVIDENCE-CONTRACT.md",
    "tests/test_issuer_evidence_contract.py"
  ],
  "issue_id": "GOV-PROTECTED-003",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Add no-credential proposed issuer evidence schema and offline negative tests; NOT_ATTESTED only.",
  "timestamp_utc": "2026-10-26T08:37:07.913Z",
  "version": "0.3.1-issuer-contract-candidate"
}
```

## GOV-AUTO-REVIEW-001-REV-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "05ecfeb6c9320943a4562e650e45c42cb6682eaa",
  "code_files": [
    "validator/llm_review_contract.py",
    "tests/test_llm_review_contract.py",
    ".github/workflows/llm-review-contract.yml",
    "docs/LLM-AUTO-REVIEW.md"
  ],
  "completed_items": [
    "Add fail-closed LLM review response contract with exact SHA/policy/repo binding and high/critical issue rejection",
    "Add fifteen synthetic schema, severity, spoofing and path tests",
    "Add nonprivileged CI for contract tests; explicitly no model invocation or trusted check issuance",
    "Record three-repository human-review retirement plan without changing any Ruleset"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-001-REV-001",
  "evidence_paths": [
    "docs/LLM-AUTO-REVIEW.md",
    "tests/test_llm_review_contract.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Stage 1 of LLM-first no-human-review migration: untrusted review report schema guard, offline negative tests, and no-secret CI only.",
  "timestamp_utc": "2026-11-03T04:49:39.199Z",
  "version": "0.4.0-auto-review-contract-candidate"
}
```

## GOV-AUTO-REVIEW-002-REV-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "274280d0439d1a306af5fd93794a1def42803885",
  "code_files": [
    "validator/llm_diff_boundary.py",
    "tests/test_llm_diff_boundary.py",
    ".github/workflows/llm-diff-boundary.yml",
    "docs/LLM-DIFF-BOUNDARY.md"
  ],
  "completed_items": [
    "Add exact-SHA bounded untrusted diff extractor without executing candidate code",
    "Add synthetic tests for ancestry, sensitive paths, stale/duplicate model output",
    "Add no-secret offline CI for model review data-boundary contract",
    "Preserve Rulesets and Gate A BLOCKED/UNVERIFIED"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-002-REV-001",
  "evidence_paths": [
    "docs/LLM-DIFF-BOUNDARY.md",
    "tests/test_llm_diff_boundary.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Bounded Git diff collection and fail-closed model response parsing in credential-free CI.",
  "timestamp_utc": "2026-11-03T04:54:22.379Z",
  "version": "0.4.1-diff-contract-candidate"
}
```

## GOV-AUTO-REVIEW-002-FIX-002

```json
{
  "author_role": "LLM",
  "baseline_sha": "9c973dc8f5a92ce1d667fd1eb46b95b148d805ee",
  "code_files": [
    "tests/test_llm_diff_boundary.py"
  ],
  "completed_items": [
    "Diagnosed one failing test: class-assigned lambda received BoundayTests instance as first git argument",
    "Convert git fixture helper to staticmethod; keep existing test expectations unchanged",
    "Re-run required CI and retain FAILED evidence for pre-fix SHA"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-002-FIX-002",
  "evidence_paths": [
    "tests/test_llm_diff_boundary.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Fix synthetic Git test helper method binding found by real CI run 41580842463; prior negative sensitive-file test errored before assertion.",
  "timestamp_utc": "2026-11-03T04:55:48.000Z",
  "version": "0.4.1-diff-contract-fix"
}
```

## GOV-AUTO-REVIEW-003-REV-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "13b49e6eeb7575e2b2514384a80f5b25c65b9350",
  "code_files": [
    "validator/review_pipeline.py",
    "tests/test_review_pipeline.py",
    ".github/workflows/model-adapter-offline.yml",
    "docs/LLM-MODEL-ADAPTER.md"
  ],
  "completed_items": [
    "Implement injected mock provider interface with request digest and SHA binding and fail-closed model output",
    "Add synthetic negative tests for provider failures, stale policy/model IDs, malformed JSON and retry limits",
    "Run no-key GitHub Actions CI; no real model invoked",
    "Preserve LLM review data provenance and Gate A blocked"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-003-REV-001",
  "evidence_paths": [
    "docs/LLM-MODEL-ADAPTER.md",
    "tests/test_review_pipeline.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "No-secret mockable provider adapter with fail-closed response and repair re-review state machine.",
  "timestamp_utc": "2026-11-03T04:59:29.500Z",
  "version": "0.4.2-model-adapter-mock"
}
```

## GOV-AUTO-REVIEW-004-REV-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "743ac125e9fa86736b8df79047f36e1235cdab41",
  "code_files": [
    "validator/review_executor_contract.py",
    "tests/test_review_executor_contract.py",
    ".github/workflows/model-executor-offline.yml",
    "docs/LLM-EXECUTOR-CONTRACT.md"
  ],
  "completed_items": [
    "Add explicit authorized model execution policy with request, response, time, model and endpoint limits",
    "Implement injected transport review orchestration with no keys or network and fail-closed error outcomes",
    "Add twenty-one synthetic positive/negative tests and unprivileged CI",
    "Preserve source, issuer, Ruleset, worklog and formal Gate A boundaries"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-004-REV-001",
  "evidence_paths": [
    "docs/LLM-EXECUTOR-CONTRACT.md",
    "tests/test_review_executor_contract.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "No-secret isolated LLM execution policy, injected transport and refusal/metadata audit contract.",
  "timestamp_utc": "2026-11-03T05:02:56.206Z",
  "version": "0.4.3-executor-contract-candidate"
}
```

## GOV-AUTO-REVIEW-004-FIX-002

```json
{
  "author_role": "LLM",
  "baseline_sha": "fc13f196fbcca9ceda04f70a5b5dd367df0cc0dd",
  "code_files": [
    "tests/test_review_executor_contract.py"
  ],
  "completed_items": [
    "Preserve CI failure evidence from candidate fc13f196fbcca9ceda04f70a5b5dd367df0cc0dd",
    "Rename test helper run to run_review, avoiding unittest.TestCase.run override",
    "Re-execute exact-commit CI with unchanged security scope"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-004-FIX-002",
  "evidence_paths": [
    "tests/test_review_executor_contract.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Fix unittest.TestCase.run override in synthetic executor test harness discovered by CI run 41581636809.",
  "timestamp_utc": "2026-11-03T05:04:24.939Z",
  "version": "0.4.3-executor-fix"
}
```

## GOV-AUTO-REVIEW-005-REV-001

```json
{
  "author_role": "LLM",
  "baseline_sha": "1b14c42b8b518a86716e0dd54b524b1d217fc8f1",
  "code_files": [
    "validator/openai_responses_transport.py",
    "tests/test_openai_responses_transport.py",
    ".github/workflows/responses-transport-offline.yml",
    "docs/LLM-REAL-PROVIDER-REFERENCE.md"
  ],
  "completed_items": [
    "Add optional fixed-endpoint HTTPS Responses reference adapter with bounded response parsing and fail-closed errors",
    "Add twenty synthetic fake-HTTP tests for status/model/redirect/oversize/auth redaction and malformed data",
    "Add unprivileged CI and security deployment gaps documentation",
    "Maintain zero credential presence, no external model invocation and unchanged protected Rulesets"
  ],
  "correction_of": null,
  "entry_id": "GOV-AUTO-REVIEW-005-REV-001",
  "evidence_paths": [
    "docs/LLM-REAL-PROVIDER-REFERENCE.md",
    "tests/test_openai_responses_transport.py"
  ],
  "issue_id": "GOV-AUTO-REVIEW-001",
  "schema_version": "2.0",
  "status": "IMPLEMENTED",
  "summary": "Fixed-host HTTPS reference transport for Responses API, fake-network negative tests and no-credential CI; no real model call.",
  "timestamp_utc": "2026-11-03T05:08:01.499Z",
  "version": "0.4.4-responses-transport-reference"
}
```
