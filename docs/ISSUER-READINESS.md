# GOV-PROTECTED-003 — issuer runner preflight (UNTRUSTED / NO SECRETS)

Issue: https://github.com/mf002078/GOV-PROTECTED-VALIDATOR/issues/4

## Scope and trust statement
This branch adds **only a credential-free PR CI preflight**. It is candidate-owned and not an independent production issuer. Passing does not authorize Gate A, issue a GitHub App check, or permit a merge to main.

Dedicated app: `GOV-Protected-Validator`, owner-reported App ID `5475837`; owner-reported install selected only `mf002078/GOV-GITHUB`. Permissions: Checks write, Contents read, Pull requests read, Metadata read; remaining permissions no access. Installation persistence and independent administrator remain unverified.

## Secret custody / executor requirements (NOT IMPLEMENTED)
- Administrator independent from candidate author must designate a separately secured runner and control credential storage and production workflow release. Existing owner/reviewer roles alone do not prove administrator separation.
- Do **not** create a PEM file, repository secret, token, PAT or credential in this PR. Never permit fork PR workflows, candidate scripts/artifacts or `pull_request_target` to access issuer credentials.
- Release issuer exclusively from independently reviewed, protected default-branch immutable SHA. Before protected main admits new policy/code, separately audit the historical boundary and first deployment.
- App installation token must be minted inside isolated issuer only, scoped to authorized repository and minimum permissions, with expiry and logs redacted. No candidate-facing output may expose token or installation metadata that enables impersonation.
- API publisher must verify repo identity, current PR HEAD SHA, expected installation/App identity, exact validation policy release SHA and external evidence digest. Fail closed on mismatch, missing ancestors, time-source failure, policy mismatch or replay.
- Use check name `protected-validator / gate-a` only after independent authorization. Synthetic smoke checks must use a *different* name and must never report Gate A success.
- Keep source Ruleset `validate` until separately approved hardening adds app-owned required check; test spoofed/absent/outdated checks first.

## Runbook (planned)
P0: isolated CI preflight passes without any secrets.
P1: independent owner documents admin separation, approved runner, secret-retention/rotation, and immutable release controls.
P2: test-only installation-token issuer operates in protected runtime and publishes **synthetic** check on an explicitly approved test SHA, with negative tests for token, app identity, replay and SHA drift.
P3: bind exact GitHub App provider required status on GOV-GITHUB Ruleset without weakening existing checks; demonstrate deny-bypass.
P4: separate Gate A acceptance and signoff. Until then Gate A = BLOCKED/UNVERIFIED.
