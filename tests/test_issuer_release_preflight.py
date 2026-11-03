"""Synthetic adversarial preflight tests; no GitHub App credentials or network."""
import copy
import unittest
from validator.issuer_release_preflight import (
    evaluate_release_request, DECISION_OK, DECISION_BLOCK)
class ReleasePreflightTests(unittest.TestCase):
    def setUp(self):
        self.now="2026-11-03T05:00:00Z"
        self.data=dict(schema_version="1.0",repository="mf002078/GOV-GITHUB",
            installation_repository="mf002078/GOV-GITHUB",app_id=5475837,
            candidate_sha="a"*40,observed_head_sha="a"*40,base_sha="b"*40,
            validator_sha="c"*40,policy_sha256="d"*64,
            evidence_sha256="e"*64,model_report_sha256="f"*64,
            model_result="REVIEWED_NO_ATTESTATION",
            checks=[dict(context=x,head_sha="a"*40,conclusion="success",app_id=15368)
                for x in ("validate","self-test")],
            workflow_run_id=100,workflow_attempt=1,
            review_executed_at_utc="2026-11-03T04:59:59Z",
            provenance="UNTRUSTED_CANDIDATE_INPUT",
            requested_check="trusted-validator")
    def check(self, data=None, **kwargs):
        return evaluate_release_request(
            data if data is not None else self.data,
            expected_candidate_sha=kwargs.get("candidate", "a"*40),
            expected_validator_sha=kwargs.get("validator", "c"*40),
            expected_policy_sha256=kwargs.get("policy", "d"*64),
            current_head_sha=kwargs.get("head", "a"*40),
            current_time_utc=kwargs.get("now", self.now),
            known_workflow_attempts=kwargs.get("seen", frozenset()))
    def change(self, key, value):
        d=copy.deepcopy(self.data);d[key]=value;return d
    def test_clean_preflight_is_not_attestation(self):
        self.assertEqual(self.check(),DECISION_OK)
        self.assertNotIn("PASS",self.check())
    def test_wrong_repo(self):
        self.assertEqual(self.check(self.change("repository","evil/repo")),DECISION_BLOCK)
    def test_wrong_installation(self):
        self.assertEqual(self.check(self.change("installation_repository","evil/repo")),DECISION_BLOCK)
    def test_wrong_app(self):
        self.assertEqual(self.check(self.change("app_id",123)),DECISION_BLOCK)
    def test_boolean_app_id(self):
        self.assertEqual(self.check(self.change("app_id",True)),DECISION_BLOCK)
    def test_wrong_head(self):
        self.assertEqual(self.check(self.change("observed_head_sha","b"*40)),DECISION_BLOCK)
    def test_stale_candidate(self):
        self.assertEqual(self.check(head="f"*40),DECISION_BLOCK)
    def test_mismatched_validator(self):
        self.assertEqual(self.check(validator="a"*40),DECISION_BLOCK)
    def test_stale_policy(self):
        self.assertEqual(self.check(policy="e"*64),DECISION_BLOCK)
    def test_wrong_model_result(self):
        self.assertEqual(self.check(self.change("model_result","PASS")),DECISION_BLOCK)
    def test_spoofed_provenance(self):
        self.assertEqual(self.check(self.change("provenance","ATTESTED")),DECISION_BLOCK)
    def test_wrong_check_context(self):
        self.assertEqual(self.check(self.change("requested_check","self-test")),DECISION_BLOCK)
    def test_missing_status(self):
        self.assertEqual(self.check(self.change("checks",[])),DECISION_BLOCK)
    def test_failed_status(self):
        x=copy.deepcopy(self.data);x["checks"][0]["conclusion"]="failure"
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_stale_status_sha(self):
        x=copy.deepcopy(self.data);x["checks"][0]["head_sha"]="b"*40
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_fake_status_app(self):
        x=copy.deepcopy(self.data);x["checks"][0]["app_id"]=12
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_duplicate_checks(self):
        x=copy.deepcopy(self.data);x["checks"][1]=x["checks"][0]
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_replay_seen(self):
        self.assertEqual(self.check(seen={(100,1,"a"*40)}),DECISION_BLOCK)
    def test_rerun_has_distinct_attempt(self):
        x=self.change("workflow_attempt",2)
        self.assertEqual(self.check(x,seen={(100,1,"a"*40)}),DECISION_OK)
    def test_future_time(self):
        x=self.change("review_executed_at_utc","2026-11-03T05:00:01Z")
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_too_old(self):
        x=self.change("review_executed_at_utc","2026-11-03T04:00:00Z")
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_bad_timezone(self):
        x=self.change("review_executed_at_utc","2026-11-03T04:59:59+00:00")
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_invalid_calendar(self):
        x=self.change("review_executed_at_utc","2026-13-03T04:59:59Z")
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_bad_run_id(self):
        self.assertEqual(self.check(self.change("workflow_run_id",False)),DECISION_BLOCK)
    def test_base_equals_head(self):
        self.assertEqual(self.check(self.change("base_sha","a"*40)),DECISION_BLOCK)
    def test_extra_claim(self):
        x=self.change("verified",True)
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_missing_field(self):
        x=copy.deepcopy(self.data);del x["model_report_sha256"]
        self.assertEqual(self.check(x),DECISION_BLOCK)
    def test_wrong_hash(self):
        self.assertEqual(self.check(self.change("evidence_sha256","notahash")),DECISION_BLOCK)
if __name__=="__main__":unittest.main()
