"""Offline, candidate-only trust-release preflight; NEVER a GitHub Check publisher.

All evidence passed here is user/candidate controlled. A successful preflight can
only say ELIGIBLE_FOR_INDEPENDENT_VERIFICATION, not PASS or ATTESTED.
"""
import datetime as dt
import re

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9._-]{1,80}\Z")
EXPECTED_SOURCE = "mf002078/GOV-GITHUB"
EXPECTED_INSTALLATION = EXPECTED_SOURCE
EXPECTED_APP_ID = 5475837
EXPECTED_CHECK_CONTEXT = "trusted-validator"
EXPECTED_CI = frozenset({"validate", "self-test"})
REPORT_FIELDS = frozenset({
    "schema_version", "repository", "installation_repository", "app_id",
    "candidate_sha", "observed_head_sha", "base_sha", "validator_sha",
    "policy_sha256", "evidence_sha256", "model_report_sha256",
    "model_result", "checks", "workflow_run_id", "workflow_attempt",
    "review_executed_at_utc", "provenance", "requested_check"
})
CHECK_FIELDS = frozenset({"context", "head_sha", "conclusion", "app_id"})
DECISION_OK = "ELIGIBLE_FOR_INDEPENDENT_VERIFICATION"
DECISION_BLOCK = "BLOCKED"

def _utc(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", value):
        return None
    try:
        x = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return x if x.utcoffset() == dt.timedelta(0) else None

def evaluate_release_request(
        data, *, expected_candidate_sha, expected_validator_sha,
        expected_policy_sha256, current_head_sha, current_time_utc,
        known_workflow_attempts=frozenset()):
    """Validate syntax/consistency only. Cannot authenticate GitHub or App identity.

    known_workflow_attempts is an independently maintained store supplied by a
    trusted runtime. Caller-supplied or PR-sourced stores provide NO anti-replay.
    """
    if not isinstance(data, dict) or set(data) != REPORT_FIELDS:
        return DECISION_BLOCK
    if not all(isinstance(x, str) and SHA40.fullmatch(x) for x in (
            expected_candidate_sha, expected_validator_sha, current_head_sha)):
        return DECISION_BLOCK
    if not isinstance(expected_policy_sha256, str) or not SHA64.fullmatch(expected_policy_sha256):
        return DECISION_BLOCK
    if (data["schema_version"] != "1.0" or data["repository"] != EXPECTED_SOURCE
            or data["installation_repository"] != EXPECTED_INSTALLATION
            or type(data["app_id"]) is not int or data["app_id"] != EXPECTED_APP_ID
            or data["requested_check"] != EXPECTED_CHECK_CONTEXT):
        return DECISION_BLOCK
    if any(not isinstance(data[k], str) or not SHA40.fullmatch(data[k])
           for k in ("candidate_sha", "observed_head_sha", "base_sha", "validator_sha")):
        return DECISION_BLOCK
    if (data["candidate_sha"] != expected_candidate_sha
            or data["candidate_sha"] != current_head_sha
            or data["observed_head_sha"] != current_head_sha
            or data["validator_sha"] != expected_validator_sha
            or data["base_sha"] == data["candidate_sha"]):
        return DECISION_BLOCK
    if any(not isinstance(data[k], str) or not SHA64.fullmatch(data[k])
           for k in ("policy_sha256", "evidence_sha256", "model_report_sha256")):
        return DECISION_BLOCK
    if data["policy_sha256"] != expected_policy_sha256:
        return DECISION_BLOCK
    if (data["model_result"] != "REVIEWED_NO_ATTESTATION"
            or data["provenance"] != "UNTRUSTED_CANDIDATE_INPUT"):
        return DECISION_BLOCK
    if (type(data["workflow_run_id"]) is not int or data["workflow_run_id"] < 1
            or type(data["workflow_attempt"]) is not int
            or not 1 <= data["workflow_attempt"] <= 100):
        return DECISION_BLOCK
    runkey = (data["workflow_run_id"], data["workflow_attempt"],
              data["candidate_sha"])
    if runkey in known_workflow_attempts:
        return DECISION_BLOCK
    now, executed = _utc(current_time_utc), _utc(data["review_executed_at_utc"])
    if now is None or executed is None:
        return DECISION_BLOCK
    age = (now - executed).total_seconds()
    if not 0 <= age <= 1800:
        return DECISION_BLOCK
    checks = data["checks"]
    if not isinstance(checks, list) or len(checks) != len(EXPECTED_CI):
        return DECISION_BLOCK
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != CHECK_FIELDS:
            return DECISION_BLOCK
        name = check["context"]
        if (not isinstance(name, str) or name not in EXPECTED_CI or name in seen
                or check["head_sha"] != current_head_sha
                or check["conclusion"] != "success"
                or type(check["app_id"]) is not int or check["app_id"] != 15368):
            return DECISION_BLOCK
        seen.add(name)
    if seen != EXPECTED_CI:
        return DECISION_BLOCK
    # Labels in the request are NOT evidence of a live check's authentication.
    # Only the separately controlled App may fetch GitHub check IDs, head SHA,
    # signer identity and current protected policy directly and issue a decision.
    return DECISION_OK
