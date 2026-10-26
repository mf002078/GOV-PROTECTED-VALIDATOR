"""Pure offline issuer evidence schema guard. NOT authorization or a GitHub API publisher."""
import re
SHA = re.compile(r"[0-9a-f]{40}\Z")
EXPECTED_REPO = "mf002078/GOV-GITHUB"
EXPECTED_APP_ID = 5475837
KEYS = {"repository", "candidate_sha", "observed_head_sha", "validator_sha",
        "policy_sha256", "evidence_sha256", "app_id", "installation_repository",
        "decision", "provenance"}
def validate_proposed_evidence(v):
    """Fail closed on malformed schema; valid does NOT mean trusted provenance."""
    if not isinstance(v, dict) or set(v) != KEYS:
        return False
    if v["repository"] != EXPECTED_REPO or v["installation_repository"] != EXPECTED_REPO:
        return False
    if type(v["app_id"]) is not int or v["app_id"] != EXPECTED_APP_ID:
        return False
    for key in ("candidate_sha", "observed_head_sha", "validator_sha"):
        if not isinstance(v[key], str) or not SHA.fullmatch(v[key]):
            return False
    if v["candidate_sha"] != v["observed_head_sha"]:
        return False
    for key in ("policy_sha256", "evidence_sha256"):
        if not isinstance(v[key], str) or not re.fullmatch(r"[a-f0-9]{64}", v[key]):
            return False
    # Candidate controlled data may never claim verified provenance or PASS.
    return v["decision"] == "NOT_ATTESTED" and v["provenance"] == "UNTRUSTED_INPUT"
