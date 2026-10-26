# GOV-PROTECTED-002: immutable audit boundary and segmented UTC

Status: implementation of the owner's narrowly approved contract; not Gate A.
Risk: verifier changes need fresh independent review before acceptance.

Owner decisions (not cryptographic signatures):
- https://github.com/mf002078/GOV-PROTECTED-VALIDATOR/issues/2#issuecomment-6392127997
- https://github.com/mf002078/GOV-PROTECTED-VALIDATOR/issues/2#issuecomment-6392173011

## Immutable history

The sole validator-repository historical boundary is
`26026250d7ba49f29349a706a27676827af861d7`. Its earlier commits remain reachable
and both journal byte prefixes are unchanged. Nineteen prototype commits lacked
contemporaneous per-commit logs; four retrospective schema-1 entries do not cure
those gaps. Report **LEGACY_AUDIT_EXCEPTION / NOT_ATTESTED**. Historical times
02:00 and 02:18 UTC may exceed actual UTC at the transition; no continuous
historical chronology is asserted.

Every later commit must append schema-2 entries and corresponding canonical
Markdown in that SAME commit. No later entry cures a missed earlier commit.
The union of each commit's new code_files must exactly equal its first-parent
Git diff, excluding only the two journal files. Workflow, tests, docs, binaries,
deleted and renamed paths are not exempt. Rename detection is disabled, so both
old and new paths count. Merge commits remain rejected, not silently bypassed.

`--profile validator-audit` fixes this repository's boundary; `--profile source`
fixes the existing GOV-GITHUB source boundary
`1975ee74a62be815a032254d51603e15b4bbe093`. The profiles are distinct histories,
not arbitrary boundary arguments. There is no --base/--boundary/--skip option.
The source profile reports LEGACY_COMPAT, never expands this repository's audit
exception to another project, and still verifies all source post-anchor commits.

IDs from the immutable journal seed the identity set (not the timestamp set).
Every new ID must be unique; CORRECTION must name an already-existing earlier
ID, never itself, a later ID or an unknown string. Paths cannot be duplicated
within code_files or evidence_paths. Evidence blobs must exist at that exact
revision; this does not authenticate digests, provenance or test execution.

## Segmented time and execution reference

The first new entry is not compared with legacy timestamps, exactly once at the
fixed boundary. All new entries, including entries within one commit, are UTC
Z timestamps, nondecreasing against all preceding new entries and no later than
the execution-time reference. **Future acceptance tolerance: zero.**

The CLI obtains time itself; it accepts no caller-controlled --now argument,
environment reference, journal timestamp or local-only fallback. Source:
`validator/utc_reference.py`, a fixed public `https://github.com/` endpoint's
HTTP Date over normally verified TLS, cross-checked against executor UTC.
Requests use a fresh query and no-cache header; redirects are rejected.

Fail-closed clock-quality bounds:
- Request must complete within 10 monotonic seconds.
- Exactly one parseable UTC Date is required.
- Executor clock must not move backward during acquisition.
- Absolute Date/executor disagreement must be at most 60 seconds; otherwise
  source freshness/consistency is unverified and validation stops.
- Use the EARLIER of server Date and executor pre-request UTC. The 60-second
  quality bound never adds grace to a future timestamp. Cached old dates can
  cause a conservative rejection, not acceptance of a future timestamp.
- TLS/network/Date failure returns BLOCKED/NOT_VERIFIED, with no fallback and
  no disabled TLS checks. A new attempt after the source is fresh is required.

This is a documented operational clock source for this candidate prototype,
not an independently signed time attestation, immutable trust root or proof
of a protected runner. The platform clock was separately observed during
development; it is not used to fabricate journal times. Unit tests inject a
synthetic UTC reference and mock HTTP metadata; they never contact a time
endpoint and never stand in for protected production refusal tests.

## Git completeness and execution boundary

The validator reads Git objects, not candidate Python or workflows. It rejects
shallow histories, missing reachable commits/trees/blobs and graft shortcuts.
Replacement refs are disabled, and promisor lazy fetching is disabled during
inspection. All real ancestors remain required even in the legacy exception.
The manual fetch no longer truncates ancestry at depth 100 and does not check
out or execute source code. Source host/repository remain fixed in workflow.

Self-test CI checks out its exact event head with full history, runs owned
synthetic unittest, audits its own post-boundary commits, then structurally
checks fixed source PR #6 SHA `08bcc423f67a0f89e11874dc8585b8805e3a3edc`.
The job remains candidate-controlled, `contents: read`, not a protected service.
The existing self-test is also triggered on pushes to this exact repair branch,
so a new candidate SHA gets CI evidence before PR creation. This adds no token
permissions and publishes no acceptance status on the source repository.

## Reproduction and recovery

```sh
python -B -m unittest discover -s tests -v
python -B validator/check_candidate.py --profile validator-audit \
  --checkout . --head "$(git rev-parse HEAD)"
python -B validator/check_candidate.py --checkout /workspace/GOV-GITHUB \
  --head 08bcc423f67a0f89e11874dc8585b8805e3a3edc
```

Commit only after exact changed-path/log correspondence, both legacy prefixes,
actual UTC and tests are checked. Post-commit rerun the complete suite and audit
the full fixed-boundary range. If recovery is needed, preserve all journal bytes
and append a new correction/recovery record in the same recovery commit; never
force-push, rebase, squash or reset away published history.

## Remaining acceptance gaps

Gate A **BLOCKED/UNVERIFIED**; provenance **NOT_ATTESTED**. No GitHub App,
issuer-bound source Check Run, separate administration, protected policy trust
root, authenticated test provenance or deny-bypass integration evidence is
deployed by this repair. Fresh independent Pochun2 review must cover the new SHA.
No main/Ruleset change, source PR update, broker, credentials, COM, MC, quote,
OMS, order or production operation is authorized or performed.
