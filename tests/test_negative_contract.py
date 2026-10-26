"""Negative assurance for independently maintained validator (synthetic only)."""
import unittest
from unittest.mock import patch
from validator import check_candidate as check

class NegativeContractTests(unittest.TestCase):
    def test_malformed_record_rejects_missing_fields(self):
        rec={"schema_version":"2.0","entry_id":"TEST"}
        self.assertFalse(check.valid_strict_record(rec,"a"*40))
    def test_malformed_record_rejects_bad_timestamp(self):
        rec=self.valid()
        rec["timestamp_utc"]="yesterday"
        self.assertFalse(check.valid_strict_record(rec,"a"*40))
    def test_malformed_record_rejects_invalid_correction(self):
        rec=self.valid()
        rec["correction_of"]="UNKNOWN"
        self.assertFalse(check.valid_strict_record(rec,"a"*40))
    def test_malformed_record_rejects_untrusted_path(self):
        rec=self.valid()
        rec["code_files"]=["../escape"]
        self.assertFalse(check.valid_strict_record(rec,"a"*40))
    def test_strict_record_passes(self):
        self.assertTrue(check.valid_strict_record(self.valid(),"a"*40))
    @staticmethod
    def valid():
        return dict(schema_version="2.0",entry_id="TEST",timestamp_utc="2026-10-25T01:00:00Z",version="1",
           issue_id="X",summary="ok",completed_items=["done"],code_files=["file.txt"],
           evidence_paths=["file.txt"],status="TESTED",baseline_sha="a"*40,
           author_role="validator-test",correction_of=None)
if __name__=="__main__":unittest.main()
