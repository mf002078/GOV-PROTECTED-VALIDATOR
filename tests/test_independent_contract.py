"""Owned offline synthetic integration tests. No candidate code execution."""
import json
import datetime as dt
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from validator import check_candidate as v

def git(path,*args,input=None):
    p=subprocess.run(["git","-C",str(path),*args],input=input,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode())
    return p.stdout.decode().strip()

class IndependentContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.repo=pathlib.Path(self.tmp.name)
        git(self.repo,"init","-q")
        git(self.repo,"config","user.name","Fixture")
        git(self.repo,"config","user.email","fixture@example.invalid")
        (self.repo/"worklog").mkdir()
        self.j=self.repo/"worklog/CHANGELOG.jsonl"
        self.m=self.repo/"worklog/CHANGELOG.md"
        self.j.write_text('{"entry_id":"LEGACY"}\n')
        self.m.write_text("# Legacy\nLEGACY\n")
        git(self.repo,"add",".")
        git(self.repo,"commit","-qm","anchor")
        self.anchor=git(self.repo,"rev-parse","HEAD")
    def tearDown(self):self.tmp.cleanup()
    def commit(self,*,code="x",record_override=None,mirror=True,write_log=True):
        parent=git(self.repo,"rev-parse","HEAD")
        (self.repo/"sample.txt").write_text(code)
        rec=dict(schema_version="2.0",entry_id="E-"+parent[:8],timestamp_utc="2026-10-25T00:00:00Z",
                 version="0.1",issue_id="TEST",summary="synthetic",completed_items=["tested"],
                 code_files=["sample.txt"],evidence_paths=["sample.txt"],status="TESTED",
                 baseline_sha=parent,author_role="fixture",correction_of=None)
        if record_override:rec.update(record_override)
        if write_log:
            with self.j.open("a") as f:f.write(json.dumps(rec)+"\n")
            with self.m.open("ab") as f:f.write(v.render(rec) if mirror else b"\nBAD MIRROR\n")
        git(self.repo,"add","-A")
        git(self.repo,"commit","-qm","synthetic")
        return git(self.repo,"rev-parse","HEAD")
    def verify(self,sha):
        with patch.object(v,"ANCHOR",self.anchor):
            return v.verify(self.repo,sha,trusted_utc=dt.datetime(2026,10,25,3,tzinfo=dt.timezone.utc))
    def test_valid_synthetic_commit(self):
        sha=self.commit()
        r=self.verify(sha)
        self.assertEqual(r["candidate_sha"],sha)
        self.assertEqual(r["level"],"STRUCTURE_PASS_NOT_ATTESTED")
    def test_missing_log_append_rejected(self):
        sha=self.commit(write_log=False)
        with self.assertRaises(ValueError):self.verify(sha)
    def test_mirror_tamper_rejected(self):
        sha=self.commit(mirror=False)
        with self.assertRaises(ValueError):self.verify(sha)
    def test_undeclared_code_path_rejected(self):
        sha=self.commit(record_override={"code_files":["wrong.txt"]})
        with self.assertRaises(ValueError):self.verify(sha)
    def test_incorrect_parent_rejected(self):
        sha=self.commit(record_override={"baseline_sha":"f"*40})
        with self.assertRaises(ValueError):self.verify(sha)
    def test_invalid_head_rejected(self):
        with self.assertRaises(ValueError):self.verify("main")
    def test_unrelated_commit_rejected(self):
        sha=self.commit()
        with patch.object(v,"ANCHOR","f"*40):
            with self.assertRaises(ValueError):v.verify(self.repo,sha,trusted_utc=dt.datetime(2026,10,25,3,tzinfo=dt.timezone.utc))
    def test_history_rewrite_rejected(self):
        a=self.commit()
        self.j.write_text('{"entry_id":"LEGACY-TAMPER"}\n')
        git(self.repo,"add","-A");git(self.repo,"commit","-qm","tamper")
        with self.assertRaises(ValueError):self.verify(git(self.repo,"rev-parse","HEAD"))
    def test_two_revisions(self):
        self.commit(code="a")
        # existing contract first new record has monotonic entry ID tied to parent
        sha=self.commit(code="b")
        self.assertEqual(self.verify(sha)["revisions"],2)
if __name__=="__main__":unittest.main()
