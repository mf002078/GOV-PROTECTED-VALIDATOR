"""Synthetic no-network checks for LLM review input and policy binding."""
import unittest
from validator.llm_review_contract import assess_report

class ReviewContractTests(unittest.TestCase):
    def sample(self):
        return dict(schema_version="1.0",repository="mf002078/GOV-GITHUB",
            base_sha="a"*40,head_sha="b"*40,policy_sha256="c"*64,
            model_id="provider/model",provenance="UNTRUSTED_MODEL_OUTPUT",
            status="REVIEW_COMPLETE",findings=[])
    def gate(self,x):
        return assess_report(x,expected_repo="mf002078/GOV-GITHUB",
            expected_base="a"*40,expected_head="b"*40,expected_policy="c"*64)
    def test_valid_output_not_an_attestation(self):
        self.assertEqual(self.gate(self.sample()),"REVIEWED_NO_ATTESTATION")
    def test_critical_blocks(self):
        x=self.sample(); x["findings"]=[dict(rule_id="SEC-001",path="src/a.py",severity="critical",explanation="bad")]
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_high_blocks(self):
        x=self.sample(); x["findings"]=[dict(rule_id="SEC-001",path="src/a.py",severity="high",explanation="bad")]
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_medium_is_not_a_trusted_success(self):
        x=self.sample(); x["findings"]=[dict(rule_id="OBS-001",path="src/a.py",severity="medium",explanation="review")]
        self.assertEqual(self.gate(x),"REVIEWED_NO_ATTESTATION")
    def test_wrong_sha(self):
        x=self.sample(); x["head_sha"]="d"*40
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_wrong_repo(self):
        x=self.sample(); x["repository"]="Pochun2/GOV-TRUSTED-ISSUER"
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_wrong_policy(self):
        x=self.sample(); x["policy_sha256"]="d"*64
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_forged_provenance(self):
        x=self.sample(); x["provenance"]="ATTESTED"
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_fake_success(self):
        x=self.sample(); x["status"]="SUCCESS"
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_missing(self):
        x=self.sample(); del x["model_id"]
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_unapproved_field(self):
        x=self.sample(); x["approval"]=True
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_insecure_path(self):
        x=self.sample(); x["findings"]=[dict(rule_id="SEC-1",path="../oops",severity="low",explanation="x")]
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_invalid_model(self):
        x=self.sample(); x["model_id"]=""
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_unbounded_findings(self):
        x=self.sample(); x["findings"]=[dict(rule_id="I",path="a",severity="info",explanation="x")]*101
        self.assertEqual(self.gate(x),"BLOCKED")
    def test_non_dict(self):
        self.assertEqual(self.gate([]),"BLOCKED")
if __name__=="__main__":unittest.main()
