# GOV-PROTECTED-001 / architecture contract

Status: PROTOTYPE / NOT DEPLOYED / Gate A BLOCKED.

Source of record: https://github.com/mf002078/GOV-GITHUB/issues/7
Candidate PR: https://github.com/mf002078/GOV-GITHUB/pull/6
Untrusted candidate head: 08bcc423f67a0f89e11874dc8585b8805e3a3edc
Approved legacy anchor: 1975ee74a62be815a032254d51603e15b4bbe093

## Trust separation
- This repository contains its **own** validator code. Never run the candidate's checker/workflow, scripts or tests as the final authority.
- A manual `workflow_dispatch` receives a 40-hex commit SHA; independently fetches ONLY the public synthetic GOV-GITHUB repo via exact SHA. Never fetch PR-supplied arbitrary URLs.
- Validator independently confirms ancestry and commit-by-commit immutable worklogs, exact changed paths, parent SHA, evidence blobs and canonical mirrors, returning `STRUCTURE_PASS_NOT_ATTESTED` or failure.
- Never present a self-generated hash manifest as an attestation of the original Codex test execution.
- This preliminary workflow does NOT create a check run on the source repository, does not have a GitHub App, and is not required by its Ruleset. Its PASS is not Gate A.
- A private repository under the same owner is NOT independent administration; Ruleset/main protection, separate service identity, reviewer control, and bypass denial must be verified before promotion.
- Workflow remains disabled for automatic PR triggers. Manually review parameters and SHA. Protected validation must always fetch code by immutable SHA.

## Remaining gates
1. Independent protected repository rules (required approval, no bypass, stable required status) with effective enforcement.
2. Separately administered GitHub App with read-only source / checks:write only, secure private key, no candidate access.
3. Trusted status `protected-review / validate` bound to immutable PR head and actual service identity; no fake GitHub review.
4. Integration negative tests: candidate checker/workflow tampering, stale SHA, forged evidence, failed authorization and bypass.
5. Independent review of this validator and policy, Gate D/A signed evidence, rollback plan and historical worklogs.

No secrets/quotes/vendor endpoints. The source repository is public generic synthetic code. Real YuantaMC and its policy are not fetched or copied.
