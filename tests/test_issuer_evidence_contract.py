"""No-token synthetic negative contract tests. Do not call GitHub APIs."""
import unittest
from validator.issuer_evidence_contract import validate_proposed_evidence
class IssuerEvidenceContractTests(unittest.TestCase):
    def good(self):
        return dict(repository="mf002078/GOV-GITHUB", installation_repository="mf002078/GOV-GITHUB",
                    app_id=5475837, candidate_sha="a"*40, observed_head_sha="a"*40,
                    validator_sha="b"*40, policy_sha256="c"*64, evidence_sha256="d"*64,
                    decision="NOT_ATTESTED", provenance="UNTRUSTED_INPUT")
    def test_baseline_synthetic_only(self):
        self.assertTrue(validate_proposed_evidence(self.good()))
    def test_wrong_repository(self):
        x=self.good(); x["repository"]="mf002078/OTHER"
        self.assertFalse(validate_proposed_evidence(x))
    def test_wrong_installation(self):
        x=self.good(); x["installation_repository"]="mf002078/OTHER"
        self.assertFalse(validate_proposed_evidence(x))
    def test_wrong_app(self):
        x=self.good(); x["app_id"]=12
        self.assertFalse(validate_proposed_evidence(x))
    def test_bool_app_id(self):
        x=self.good(); x["app_id"]=True
        self.assertFalse(validate_proposed_evidence(x))
    def test_sha_drift(self):
        x=self.good(); x["observed_head_sha"]="f"*40
        self.assertFalse(validate_proposed_evidence(x))
    def test_bad_policy_digest(self):
        x=self.good(); x["policy_sha256"]="invalid"
        self.assertFalse(validate_proposed_evidence(x))
    def test_bad_evidence_digest(self):
        x=self.good(); x["evidence_sha256"]="0"*63
        self.assertFalse(validate_proposed_evidence(x))
    def test_attempt_fake_pass(self):
        x=self.good(); x["decision"]="SUCCESS"
        self.assertFalse(validate_proposed_evidence(x))
    def test_attempt_claim_trusted(self):
        x=self.good(); x["provenance"]="ATTESTED"
        self.assertFalse(validate_proposed_evidence(x))
    def test_extra_unapproved_field(self):
        x=self.good(); x["token"]="exfiltration"
        self.assertFalse(validate_proposed_evidence(x))
    def test_missing_field(self):
        x=self.good(); del x["validator_sha"]
        self.assertFalse(validate_proposed_evidence(x))
if __name__=="__main__": unittest.main()
