# GOV-PROTECTED-003 — Offline issuer evidence contract, Phase P3-DESIGN

Issue #4; exact parent SHA `8607456fe4429671e6c27bc72440461ce60b2c59`.

This commit provides a **pure offline format/negative-test contract only**. The module cannot authenticate a GitHub App, access an App private key, mint an installation token, create a GitHub Check Run, or enforce repository rules. Input fields are candidate supplied and untrusted; even a schema-valid object is NEVER a trusted attestation.

Defined negative tests: unknown repository, installation scope mismatch, App ID mismatch, SHA drift, malformed policy/evidence hashes, falsely claimed successful verdict or attested origin, and unexpected fields. More tests needed in a genuinely protected issuer: tampered protected validator release, token theft/expiry, check-run issuer identity, webhook replay, concurrent HEAD updates, ruleset provider spoofing, privileged-workflow attacks, and authenticated evidence signature.

**Trust cutover is NOT authorized.** Next milestone requires independent secret administrator and controlled release/runner. Do not place a PEM, token or other secret in this repository, any PR workflow, an issue or ChatGPT. Do not convert `NOT_ATTESTED` into Check Run success; Gate A stays BLOCKED/UNVERIFIED.
