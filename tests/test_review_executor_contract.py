"""Isolated executor policy tests, synthetic only, no network or credentials."""
import hashlib
import json
import unittest
from validator.review_executor_contract import execute_review,make_execution_record,ExecutionRejected
class ExecutorTests(unittest.TestCase):
    def setUp(self):
        diff="diff --git a/a.txt b/a.txt\n+hello\n"
        self.req=dict(repository_data_trust="UNTRUSTED",base_sha="a"*40,head_sha="b"*40,
                      policy_sha256="c"*64,diff_sha256=hashlib.sha256(diff.encode()).hexdigest(),
                      changed_paths=["a.txt"],diff_data=diff)
        self.policy=dict(schema_version="1.0",provider="synthetic",endpoint_id="mock",
                         model_id="mock",policy_sha256="c"*64,max_input_bytes=1024,
                         max_output_bytes=2048,max_output_tokens=512,timeout_seconds=5,
                         max_requests=1,allow_external_diff=True)
        self.repo="mf002078/GOV-GITHUB"
    def response(self,**kw):
        obj=dict(schema_version="1.0",repository=self.repo,base_sha="a"*40,head_sha="b"*40,
                 policy_sha256="c"*64,model_id="mock",provenance="UNTRUSTED_MODEL_OUTPUT",
                 status="REVIEW_COMPLETE",findings=[])
        obj.update(kw)
        return json.dumps(obj)
    def run(self,fn=None,request=None,policy=None,repo=None):
        return execute_review(request=request if request is not None else self.req,
                policy=policy if policy is not None else self.policy,
                repository=repo or self.repo,transport=fn)
    def test_valid_mock_is_not_attested(self):
        r=self.run(lambda e,**kw:self.response())
        self.assertEqual(r["status"],"REVIEWED_NO_ATTESTATION")
        self.assertEqual(r["evidence"]["provenance"],"NOT_ATTESTED")
    def test_evidence_does_not_contain_diff(self):
        r=self.run(lambda e,**kw:self.response())
        self.assertNotIn("diff_data",json.dumps(r))
    def test_no_transport_blocks(self):
        self.assertEqual(self.run()["status"],"BLOCKED")
    def test_permission_denied_blocks_without_call(self):
        p=dict(self.policy,allow_external_diff=False)
        def fail(e,**kw):raise AssertionError("must not call")
        self.assertEqual(self.run(fail,policy=p)["status"],"BLOCKED")
    def test_stale_policy_blocks(self):
        x=dict(self.req,policy_sha256="d"*64)
        self.assertEqual(self.run(lambda e,**kw:self.response(),request=x)["status"],"BLOCKED")
    def test_provider_timeout_blocks(self):
        def fail(e,**kw):raise TimeoutError("synthetic")
        self.assertEqual(self.run(fail)["status"],"BLOCKED")
    def test_unexpected_provider_exception_blocks(self):
        def fail(e,**kw):raise RuntimeError("simulated secret must not leak")
        r=self.run(fail);self.assertEqual(r["status"],"BLOCKED")
        self.assertNotIn("secret",json.dumps(r))
    def test_high_finding_blocks(self):
        r=self.run(lambda e,**kw:self.response(findings=[
              dict(rule_id="SEC",path="a.txt",severity="high",explanation="bad")]))
        self.assertEqual(r["status"],"BLOCKED")
    def test_replay_head_blocks(self):
        self.assertEqual(self.run(lambda e,**kw:self.response(head_sha="d"*40))["status"],"BLOCKED")
    def test_wrong_model_blocks(self):
        self.assertEqual(self.run(lambda e,**kw:self.response(model_id="other"))["status"],"BLOCKED")
    def test_forged_pass_blocks(self):
        self.assertEqual(self.run(lambda e,**kw:self.response(status="PASS"))["status"],"BLOCKED")
    def test_overlarge_model_output_blocks(self):
        self.assertEqual(self.run(lambda e,**kw:"x"*3000)["status"],"BLOCKED")
    def test_input_budget_blocks(self):
        p=dict(self.policy,max_input_bytes=2)
        self.assertEqual(self.run(lambda e,**kw:self.response(),policy=p)["status"],"BLOCKED")
    def test_invalid_limits_block(self):
        p=dict(self.policy,timeout_seconds=61)
        self.assertEqual(self.run(lambda e,**kw:self.response(),policy=p)["status"],"BLOCKED")
    def test_boolean_budget_blocks(self):
        p=dict(self.policy,max_requests=True)
        self.assertEqual(self.run(lambda e,**kw:self.response(),policy=p)["status"],"BLOCKED")
    def test_provider_is_called_once(self):
        calls=[]
        def f(e,**kw):calls.append(kw);return self.response()
        self.run(f);self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]["timeout_seconds"],5)
    def test_unknown_repo_blocks(self):
        self.assertEqual(self.run(lambda e,**kw:self.response(),repo="evil/repo")["status"],"BLOCKED")
    def test_bad_provider_type_blocks(self):
        p=dict(self.policy,provider="contains spaces")
        self.assertEqual(self.run(lambda e,**kw:self.response(),policy=p)["status"],"BLOCKED")
    def test_extra_policy_key_blocks(self):
        p=dict(self.policy,private_token="not a key")
        self.assertEqual(self.run(lambda e,**kw:self.response(),policy=p)["status"],"BLOCKED")
    def test_bad_diff_digest_blocks(self):
        r=dict(self.req,diff_sha256="f"*64)
        self.assertEqual(self.run(lambda e,**kw:self.response(),request=r)["status"],"BLOCKED")
    def test_credential_not_in_evidence(self):
        r=self.run(lambda e,**kw:self.response())
        self.assertFalse(any(k in r.get("evidence",{}) for k in ("api_key","private_key","token","diff_data")))
if __name__=="__main__":unittest.main()
