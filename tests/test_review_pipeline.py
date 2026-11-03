"""Synthetic provider tests; no external inference or privileged tokens."""
import hashlib
import json
import unittest
from validator.review_pipeline import review_once, repair_next_step, ProviderFailure, validate_request

class PipelineTests(unittest.TestCase):
    def setUp(self):
        diff = "diff --git a/a.py b/a.py\n+hello\n"
        self.req = dict(repository_data_trust="UNTRUSTED", base_sha="a"*40,
                        head_sha="b"*40, policy_sha256="c"*64,
                        diff_sha256=hashlib.sha256(diff.encode()).hexdigest(),
                        changed_paths=["a.py"], diff_data=diff)
        self.repo = "mf002078/GOV-GITHUB"
    def model_output(self, **changes):
        v=dict(schema_version="1.0",repository=self.repo,base_sha="a"*40,
               head_sha="b"*40,policy_sha256="c"*64,model_id="mock-model",
               provenance="UNTRUSTED_MODEL_OUTPUT",status="REVIEW_COMPLETE",findings=[])
        v.update(changes)
        return json.dumps(v)
    def run_review(self, provider, req=None, **extra):
        return review_once(req or self.req,repository=self.repo,provider=provider,
                           provider_identity="isolated-mock",policy_model_id="mock-model",**extra)
    def test_clean_mock_not_trusted(self):
        x=self.run_review(lambda e,timeout_seconds:self.model_output())
        self.assertEqual(x["status"],"REVIEWED_NO_ATTESTATION")
    def test_high_finding_blocks(self):
        x=self.run_review(lambda e,timeout_seconds:self.model_output(findings=[
            dict(rule_id="SEC",path="a.py",severity="high",explanation="issue")]))
        self.assertEqual(x["status"],"BLOCKED")
    def test_critical_blocks(self):
        x=self.run_review(lambda e,timeout_seconds:self.model_output(findings=[
            dict(rule_id="SEC",path="a.py",severity="critical",explanation="issue")]))
        self.assertEqual(x["status"],"BLOCKED")
    def test_timeout_blocks(self):
        def f(e,timeout_seconds): raise TimeoutError("synthetic")
        self.assertEqual(self.run_review(f)["reason"],"PROVIDER_FAILURE")
    def test_provider_failure_blocks(self):
        def f(e,timeout_seconds): raise ProviderFailure("synthetic")
        self.assertEqual(self.run_review(f)["status"],"BLOCKED")
    def test_wrong_model_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:self.model_output(model_id="other"))["reason"],"MODEL_ID_MISMATCH")
    def test_sha_stale_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:self.model_output(head_sha="d"*40))["status"],"BLOCKED")
    def test_policy_stale_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:self.model_output(policy_sha256="d"*64))["status"],"BLOCKED")
    def test_forged_attested_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:self.model_output(provenance="ATTESTED"))["status"],"BLOCKED")
    def test_fake_success_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:self.model_output(status="SUCCESS"))["status"],"BLOCKED")
    def test_duplicate_json_blocks(self):
        def f(e,timeout_seconds):return self.model_output().replace('"status":','"status": "SUCCESS", "status":',1)
        self.assertEqual(self.run_review(f)["status"],"BLOCKED")
    def test_malformed_json_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:"{bad")["status"],"BLOCKED")
    def test_large_output_blocks(self):
        self.assertEqual(self.run_review(lambda e,timeout_seconds:"x"*64001)["status"],"BLOCKED")
    def test_bad_digest_blocks_without_provider_call(self):
        x=dict(self.req,diff_sha256="f"*64)
        def fail(e,timeout_seconds):raise AssertionError("must not call")
        self.assertEqual(self.run_review(fail,req=x)["status"],"BLOCKED")
    def test_changed_paths_duplicates_block(self):
        x=dict(self.req,changed_paths=["a.py","a.py"])
        self.assertFalse(validate_request(x))
    def test_unknown_repo_blocks(self):
        x=review_once(self.req,repository="owner/other",provider=lambda e,timeout_seconds:self.model_output(),
                      provider_identity="mock",policy_model_id="mock-model")
        self.assertEqual(x["reason"],"REPO_NOT_ALLOWLISTED")
    def test_timeout_policy_blocks(self):
        def fail(e,timeout_seconds):raise AssertionError("must not call")
        self.assertEqual(self.run_review(fail,timeout_seconds=100)["status"],"BLOCKED")
    def test_no_provider_blocks(self):
        self.assertEqual(self.run_review(None)["status"],"BLOCKED")
    def test_model_request_labels_data_untrusted(self):
        got=[]
        def f(e,timeout_seconds):
            got.append(e)
            return self.model_output()
        self.run_review(f)
        self.assertEqual(got[0]["task"],"REVIEW_SOURCE_DIFF_AS_UNTRUSTED_DATA")
        self.assertEqual(got[0]["head_sha"],self.req["head_sha"])
    def test_repair_new_sha_requires_recheck(self):
        self.assertEqual(repair_next_step(old_sha="a"*40,new_sha="b"*40,attempt=0,
                        review_status="BLOCKED",checks_passed=True),"REVIEW_NEW_SHA_REQUIRED")
    def test_repair_same_sha_blocks(self):
        self.assertEqual(repair_next_step(old_sha="a"*40,new_sha="a"*40,attempt=0,
                        review_status="BLOCKED",checks_passed=True),"BLOCKED")
    def test_repair_attempt_limit(self):
        self.assertEqual(repair_next_step(old_sha="a"*40,new_sha="b"*40,attempt=2,
                        review_status="BLOCKED",checks_passed=True),"STOP_FOR_TRIAGE")
    def test_repair_ci_failure_blocks(self):
        self.assertEqual(repair_next_step(old_sha="a"*40,new_sha="b"*40,attempt=0,
                        review_status="BLOCKED",checks_passed=False),"BLOCKED")
    def test_repair_invalid_result_blocks(self):
        self.assertEqual(repair_next_step(old_sha="a"*40,new_sha="b"*40,attempt=0,
                        review_status="SUCCESS",checks_passed=True),"BLOCKED")

if __name__=="__main__":unittest.main()
