# GOV-AUTO-REVIEW-001 — LLM-first review integration stage 1

Owner decision: https://github.com/mf002078/GOV-PROTECTED-VALIDATOR/issues/4#issuecomment-6595676353

This commit introduces only an **offline review report contract** and synthetic negative tests. The new `llm-contract-offline` GitHub job DOES NOT invoke any model, authenticate any LLM output or issue an independently protected check. Its success must not be construed as LLM review, Gate A approval, or permission to remove existing required checks.

## Intended production pipeline

1. LLM/Codex proposes code, tests and append-only worklogs in a development branch.
2. A separate low-privilege PR CI runs unit/integration/negative tests, policy/commit lineage and coverage checks. Candidate PR content is untrusted data.
3. An independently controlled executor retrieves bounded PR diff and fixed validated policy, calls a selected supported LLM service, parses a strictly bounded report with `assess_report`, and combines it with deterministic tests. LLM input may contain prompt injection and must never be executed or gain trusted credentials.
4. A trusted Pochun2-owned Issuer (separate repo/credentials/runner), only when independently deployed, binds exact repo/PR head/policy/validator SHA and releases an App-owned Check Run. Bad/missing/stale evidence always blocks. Model output alone cannot assert success.
5. Only once the replacement mandatory Check is observed and provider identity verified may Repo admins consider switching required human approval from 1 to 0. Preserve existing `validate` / `self-test` until this is tested. Changes to formal YMC-GOV-001 and Gate A require a separate explicit policy disposition.

## Gates and safeguards

- Initial no-secret workflow runs on pull_request with `contents:read`. No `pull_request_target`, no issuer secret, no access to candidate-controlled artifacts beyond untrusted content.
- `llm-contract-offline` is not a production required check and is not eligible to authorize merges.
- No model API provider, external network egress allowance, costs/quotas or privacy boundary have yet been approved. No live vendor/OMS/order/production access.
- Review report can only return `BLOCKED` or `REVIEWED_NO_ATTESTATION`, never a trusted PASS.
- Report producer and execution provenance are not authenticated; future issuer must verify those independently.
- Applicable repositories: `GOV-GITHUB`, `GOV-PROTECTED-VALIDATOR`, `GOV-TRUSTED-ISSUER`. Eliminate all human PR approval gates only after compensating enforced CI is live in each.
