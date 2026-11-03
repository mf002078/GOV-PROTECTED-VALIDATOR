# GOV-AUTO-REVIEW-003 — No-secret LLM provider adapter and review lifecycle contract

**Current state: MOCK-ONLY, NOT_ATTESTED, Gate A BLOCKED/UNVERIFIED.**

This stage adds `validator/review_pipeline.py` and 24 offline synthetic tests. The module has no HTTP client, model credentials, GitHub API publisher, or candidate source editing. `review_once` receives an injected callable which MUST be supplied only by a separately administered executor when a model provider is approved. It validates request digest, repository, SHA and provider policy, bounds response format and rejects malformed/stale/spoofed output, timeout and provider failures. Its only nonblocked result is `REVIEWED_NO_ATTESTATION`, never trusted PASS.

The `repair_next_step` state machine enforces a changed commit SHA, successful deterministic checks and a maximum of two repair attempts; it cannot write commits or reuse reviews. This is not an automatic source repair implementation.

**Pending integrations**: approved provider and privacy/secret scanning, model key isolated to Pochun2-controlled Issuer runtime (no keys in candidate workflows), actual independent LLM call with enforceable transport deadline, failure and budget controls, redacted report archive, external policy snapshot and GitHub App identity validation, stale SHA/replay rejection, protected Check Run publisher, end-to-end self-healing workflow and source Ruleset cutover. No App keys, PATs, production live data, or external candidate diff transfer were used here. Existing `validate` and `self-test` remain required and all three Rulesets unchanged.
