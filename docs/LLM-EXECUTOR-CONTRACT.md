# GOV-AUTO-REVIEW-004 — Protected model executor integration contract

Scope: Stage 4 candidate-only. Implemented a **no-secret isolated-transport interface**, not a production HTTP executor, credential manager, real LLM inference, trusted GitHub Check or approval. This is deliberately tested in unprivileged PR CI, which must not possess model credentials or GitHub App private keys.

The protected executor must be operated independently by Pochun2. Before enabling an actual provider:
1. Explicitly select and authorize provider, region/data-processing arrangements, endpoints, model, diff disclosure scope and budgets.
2. Deploy transport only in protected runner or separate trusted service, enforce server-side timeouts, outbound allowlist, no untrusted redirects/proxies and endpoint/method restrictions, response caps, request count and spend limits.
3. Pre-screen all diff content for embedded secrets/PII. File extensions alone are NOT sufficient and current Git diff contract does NOT prove that transfer is safe. Review model-input logs must not persist raw secrets.
4. Bind authenticated job identity, exact PR head SHA and base SHA, validator/policy hash and installation repository; revalidate before and after review, archive metadata/cryptographic evidence without credentials.
5. Independently publish Check Runs through Pochun2-controlled App, never through PR-origin GITHUB_TOKEN or candidate-controlled workflow. Check must reject stale SHA, replay, invalid model identity, failed deterministic CI, fake attestation and issuer policy drift.
6. Enforce zero-human-review transition only after independent issuance is live, negative tests pass, and protections still require exact pinned checks. No Rulesets were modified in this stage.

`execute_review` supports an injected bounded transport and returns only `BLOCKED` or `REVIEWED_NO_ATTESTATION`. It does not call the internet, guarantee real external timeout or return trusted approval. Its evidence never contains raw diff or provider credentials. A real transport remains to be developed in the separately controlled repository.

All existing branches, PR approvals, GitHub App credentials, formal Gate A, and YuantaMC production state remain unchanged. Gate A BLOCKED/UNVERIFIED.
