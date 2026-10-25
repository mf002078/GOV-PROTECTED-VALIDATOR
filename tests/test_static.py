import pathlib
import unittest
from validator.check_candidate import render
class StructuralTests(unittest.TestCase):
    def test_deterministic_mirror(self):
        r={"entry_id":"EXAMPLE","summary":"s"}
        self.assertEqual(render(r),render(r))
        self.assertIn(b'EXAMPLE',render(r))
    def test_workflow_manual_only(self):
        w=(pathlib.Path(__file__).resolve().parents[1]/'.github/workflows/structural-validation.yml').read_text()
        self.assertIn('workflow_dispatch:',w)
        self.assertNotIn('pull_request:',w)
        self.assertIn('permissions:\n  contents: read',w)
    def test_no_candidate_code_execute(self):
        s=(pathlib.Path(__file__).resolve().parents[1]/'validator/check_candidate.py').read_text()
        self.assertNotIn('shell=True',s)
if __name__=='__main__':unittest.main()
