"""Isolated model transport policy. Import-safe: no network or credentials in this module.

The adapter is injectable; a trusted Pochun2-owned runner must supply a transport
and secrets. These objects must not be used in untrusted PR workflow contexts.
"""
import hashlib
import json
import re
from .review_pipeline import validate_request, review_once

SHA64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_PROMPT_BYTES = 120_000
MAX_RESPONSE_BYTES = 64_000
MAX_TOKENS = 2048
MAX_REQUESTS = 1

class ExecutionRejected(ValueError):
    pass

def pinned_execution_policy(policy):
    keys={"schema_version","provider","endpoint_id","model_id","policy_sha256",
          "max_input_bytes","max_output_bytes","max_output_tokens","timeout_seconds",
          "max_requests","allow_external_diff"}
    if not isinstance(policy,dict) or set(policy)!=keys:
        raise ExecutionRejected("policy schema")
    if policy["schema_version"]!="1.0":
        raise ExecutionRejected("version")
    for name in ("provider","endpoint_id","model_id"):
        if not isinstance(policy[name],str) or not re.fullmatch(r"[A-Za-z0-9_.:/-]{1,128}",policy[name]):
            raise ExecutionRejected("provider identity")
    if (not isinstance(policy["policy_sha256"],str)
            or not SHA64.fullmatch(policy["policy_sha256"])):
        raise ExecutionRejected("policy hash")
    for k, ceiling in (("max_input_bytes",MAX_PROMPT_BYTES),
                       ("max_output_bytes",MAX_RESPONSE_BYTES),
                       ("max_output_tokens",MAX_TOKENS),
                       ("timeout_seconds",60),("max_requests",MAX_REQUESTS)):
        v=policy[k]
        if type(v) is not int or v<1 or v>ceiling:
            raise ExecutionRejected("invalid limit")
    if policy["allow_external_diff"] is not True:
        raise ExecutionRejected("external transfer not authorized")
    return dict(policy)

def make_execution_record(*,request,policy,repository):
    """Build deterministic safe metadata; MUST NOT include raw diff or token."""
    if not validate_request(request):
        raise ExecutionRejected("untrusted input rejected")
    policy=pinned_execution_policy(policy)
    if request["policy_sha256"]!=policy["policy_sha256"]:
        raise ExecutionRejected("policy mismatch")
    if repository not in {"mf002078/GOV-GITHUB","mf002078/GOV-PROTECTED-VALIDATOR",
                          "Pochun2/GOV-TRUSTED-ISSUER"}:
        raise ExecutionRejected("repository not allowed")
    if len(request["diff_data"].encode("utf-8"))>policy["max_input_bytes"]:
        raise ExecutionRejected("input budget")
    return {"schema_version":"1.0","repository":repository,
            "head_sha":request["head_sha"],"base_sha":request["base_sha"],
            "diff_sha256":request["diff_sha256"],"policy_sha256":policy["policy_sha256"],
            "provider":policy["provider"],"endpoint_id":policy["endpoint_id"],
            "model_id":policy["model_id"],"provenance":"NOT_ATTESTED",
            "result":"PENDING"}

def execute_review(*, request, policy, repository, transport):
    """Call an externally injected transport once; fail closed on all errors.

    Adapter contract: transport(envelope, timeout_seconds, max_output_bytes,
    max_output_tokens). The protected executor must enforce a real network timeout,
    an outbound host allowlist, no redirects to untrusted addresses, response bytes,
    secret isolation and rate/cost limits. This module cannot enforce remote egress.
    """
    try:
        record=make_execution_record(request=request,policy=policy,repository=repository)
    except (ExecutionRejected,TypeError,ValueError,KeyError):
        return {"status":"BLOCKED","reason":"POLICY_REJECTED","provenance":"NOT_ATTESTED"}
    if not callable(transport):
        return {"status":"BLOCKED","reason":"NO_ISOLATED_TRANSPORT","provenance":"NOT_ATTESTED"}
    calls=[0]
    def bounded(envelope,*,timeout_seconds):
        calls[0]+=1
        if calls[0]>policy["max_requests"]:
            raise TimeoutError("call budget exceeded")
        raw=transport(envelope,timeout_seconds=timeout_seconds,
                      max_output_bytes=policy["max_output_bytes"],
                      max_output_tokens=policy["max_output_tokens"])
        if not isinstance(raw,(bytes,str)) or len(raw)>policy["max_output_bytes"]:
            raise ValueError("response exceeded budget")
        return raw
    try:
        result=review_once(request,repository=repository,provider=bounded,
                           provider_identity=policy["provider"]+":"+policy["endpoint_id"],
                           policy_model_id=policy["model_id"],
                           timeout_seconds=policy["timeout_seconds"])
    except Exception:
        # No provider exception text, tokens or diff may leak into reported evidence.
        return {"status":"BLOCKED","reason":"TRANSPORT_REJECTED","provenance":"NOT_ATTESTED"}
    # Explicitly never return any model text, credentials or raw candidate diff.
    if result.get("status")!="REVIEWED_NO_ATTESTATION":
        return {"status":"BLOCKED","reason":"MODEL_OR_TRANSPORT_REJECTED",
                "provenance":"NOT_ATTESTED"}
    record["result"]="REVIEWED_NO_ATTESTATION"
    return {"status":"REVIEWED_NO_ATTESTATION","reason":"UNTRUSTED_MODEL_RESULT",
            "provenance":"NOT_ATTESTED","evidence":record}
