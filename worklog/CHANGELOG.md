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
