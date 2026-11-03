"""Offline synthetic tests of exact-SHA untrusted data extraction."""
import json, subprocess, tempfile, unittest
from pathlib import Path
from validator.llm_diff_boundary import prepare_review, evaluate_model_output, ReviewBlocked
class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.repo=Path(cls.tmp.name)
        cls.git=staticmethod(lambda *a:subprocess.run(["git","-C",str(cls.repo),*a],capture_output=True,check=True).stdout)
        cls.git("init","-q");cls.git("config","user.name","Synthetic");cls.git("config","user.email","test@example.invalid")
        (cls.repo/"a.txt").write_text("before\n");cls.git("add","a.txt");cls.git("commit","-qm","base")
        cls.base=cls.git("rev-parse","HEAD").decode().strip()
        (cls.repo/"a.txt").write_text("before\nafter\n");cls.git("add","a.txt");cls.git("commit","-qm","head")
        cls.head=cls.git("rev-parse","HEAD").decode().strip()
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def request(self,base=None,head=None,policy=None):
        return prepare_review(self.repo,base or self.base,head or self.head,policy or "c"*64)
    def report(self):
        return dict(schema_version="1.0",repository="mf002078/GOV-GITHUB",base_sha=self.base,head_sha=self.head,
                    policy_sha256="c"*64,model_id="mock",provenance="UNTRUSTED_MODEL_OUTPUT",
                    status="REVIEW_COMPLETE",findings=[])
    def assess(self,raw):
        return evaluate_model_output(raw,expected_repo="mf002078/GOV-GITHUB",request=self.request())
    def test_valid_diff_still_untrusted(self):
        v=self.request();self.assertEqual(v["repository_data_trust"],"UNTRUSTED");self.assertIn("after",v["diff_data"])
    def test_reversed_ancestry_rejected(self):
        with self.assertRaises(ReviewBlocked):self.request(base=self.head,head=self.base)
    def test_missing_sha_rejected(self):
        with self.assertRaises(ReviewBlocked):self.request(head="f"*40)
    def test_same_sha_rejected(self):
        with self.assertRaises(ReviewBlocked):self.request(head=self.base)
    def test_bad_sha_rejected(self):
        with self.assertRaises(ReviewBlocked):self.request(base="-malicious")
    def test_bad_policy_rejected(self):
        with self.assertRaises(ReviewBlocked):self.request(policy="notsha")
    def test_sensitive_file_rejected(self):
        (self.repo/"secret.pem").write_text("synthetic");self.git("add","secret.pem");self.git("commit","-qm","sensitive")
        h=self.git("rev-parse","HEAD").decode().strip()
        try:
            with self.assertRaises(ReviewBlocked):self.request(base=self.head,head=h)
        finally:self.git("reset","--hard","-q",self.head)
    def test_valid_report_not_attested(self):
        self.assertEqual(self.assess(json.dumps(self.report())),"REVIEWED_NO_ATTESTATION")
    def test_high_severity_blocks(self):
        x=self.report();x["findings"]=[dict(rule_id="SEC",path="a.txt",severity="high",explanation="synthetic")]
        self.assertEqual(self.assess(json.dumps(x)),"BLOCKED")
    def test_stale_report_blocks(self):
        x=self.report();x["head_sha"]="d"*40;self.assertEqual(self.assess(json.dumps(x)),"BLOCKED")
    def test_duplicate_key_blocks(self):
        x=json.dumps(self.report()).replace('"status":','"status": "SUCCESS", "status":',1)
        self.assertEqual(self.assess(x),"BLOCKED")
    def test_malformed_json_blocks(self):
        self.assertEqual(self.assess("{broken"),"BLOCKED")
    def test_large_model_output_blocks(self):
        self.assertEqual(self.assess("x"*65000),"BLOCKED")
    def test_array_output_blocks(self):
        self.assertEqual(self.assess("[]"),"BLOCKED")
if __name__=="__main__":unittest.main()
