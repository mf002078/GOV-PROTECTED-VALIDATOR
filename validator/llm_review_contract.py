"""Schema-only gate for untrusted LLM review reports; NOT a trusted approval."""
import re

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
SEVERITIES = {"info", "low", "medium", "high", "critical"}
ROOT_KEYS = {"schema_version", "repository", "base_sha", "head_sha", "policy_sha256",
             "model_id", "provenance", "status", "findings"}
FINDING_KEYS = {"rule_id", "path", "severity", "explanation"}
MAX_FINDINGS = 100

def _canonical_path(v):
    return (isinstance(v, str) and bool(v) and len(v) <= 512
            and not v.startswith("/") and "\\" not in v
            and not any(ch in v for ch in "\r\n\x00")
            and all(p not in ("", ".", "..") for p in v.split("/")))

def assess_report(report, *, expected_repo, expected_base, expected_head, expected_policy):
    """Return REVIEWED_NO_ATTESTATION or BLOCKED. Cannot issue PASS/Gate A.

    External LLM output is untrusted input. Source identity and policy ownership
    must be authenticated separately, in an isolated protected service.
    """
    if not isinstance(report, dict) or set(report) != ROOT_KEYS:
        return "BLOCKED"
    if report["schema_version"] != "1.0" or report["provenance"] != "UNTRUSTED_MODEL_OUTPUT":
        return "BLOCKED"
    if report["status"] != "REVIEW_COMPLETE":
        return "BLOCKED"
    if (not SHA40.fullmatch(str(expected_base))
            or not SHA40.fullmatch(str(expected_head))
            or not SHA64.fullmatch(str(expected_policy))):
        return "BLOCKED"
    if (report["repository"] != expected_repo or report["base_sha"] != expected_base
            or report["head_sha"] != expected_head or report["policy_sha256"] != expected_policy):
        return "BLOCKED"
    if not isinstance(report["model_id"], str) or not 1 <= len(report["model_id"]) <= 128:
        return "BLOCKED"
    findings = report["findings"]
    if not isinstance(findings, list) or len(findings) > MAX_FINDINGS:
        return "BLOCKED"
    for f in findings:
        if not isinstance(f, dict) or set(f) != FINDING_KEYS:
            return "BLOCKED"
        if f["severity"] not in SEVERITIES or not _canonical_path(f["path"]):
            return "BLOCKED"
        if not isinstance(f["rule_id"], str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", f["rule_id"]):
            return "BLOCKED"
        if not isinstance(f["explanation"], str) or not 1 <= len(f["explanation"].strip()) <= 4000:
            return "BLOCKED"
    if any(f["severity"] in {"high", "critical"} for f in findings):
        return "BLOCKED"
    # The returned label is intentionally NOT a GitHub required Check success.
    return "REVIEWED_NO_ATTESTATION"
