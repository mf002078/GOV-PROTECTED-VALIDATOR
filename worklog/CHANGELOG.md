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
