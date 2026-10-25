"""Owned synthetic Git fixtures; no network, source code execution or secrets."""
import datetime as dt
import json
import pathlib
import subprocess
import unittest
from unittest.mock import patch

import test_independent_contract as fixtures
from validator import check_candidate as v

NOW = dt.datetime(2026, 10, 25, 3, tzinfo=dt.timezone.utc)


class AuditHardeningTests(unittest.TestCase):
    setUp = fixtures.IndependentContractTests.setUp
    tearDown = fixtures.IndependentContractTests.tearDown
    commit = fixtures.IndependentContractTests.commit

    def git(self, *args):
        return fixtures.git(self.repo, *args)

    def verify(self, sha, now=NOW):
        with patch.object(v, 'AUDIT_ANCHOR', self.anchor):
            return v.verify(self.repo, sha, profile='validator-audit', trusted_utc=now)

    def amendment(self, record_changes=None):
        records=self.j.read_bytes().splitlines()
        r=json.loads(records[-1]); r.update(record_changes or {})
        self.j.write_bytes(b'\n'.join(records[:-1])+b'\n'+(json.dumps(r)+'\n').encode())
        prefix=v.blob(self.repo,self.anchor,v.PATHS[1])
        new=[json.loads(line) for line in self.j.read_bytes()[len(v.blob(self.repo,self.anchor,v.PATHS[0])):].splitlines()]
        self.m.write_bytes(prefix+b''.join(v.render(x) for x in new))
        self.git('add','-A'); self.git('commit','--amend','--no-edit','-q')
        return self.git('rev-parse','HEAD')

    def test_segmented_time_ignores_legacy_future_once(self):
        self.j.write_text(json.dumps(dict(entry_id='LEGACY',timestamp_utc='2099-01-01T00:00:00Z'))+'\n')
        self.git('add','.'); self.git('commit','--amend','--no-edit','-q')
        self.anchor=self.git('rev-parse','HEAD')
        sha=self.commit()
        result=self.verify(sha)
        self.assertEqual('LEGACY_AUDIT_EXCEPTION',result['legacy_status'])
        self.assertEqual(self.anchor,result['legacy_boundary_sha'])

    def test_normal_multiple_commits(self):
        self.commit(code='a')
        sha=self.commit(code='b')
        self.assertEqual(2,self.verify(sha)['revisions'])

    def test_second_new_timestamp_regresses(self):
        self.commit(code='a',record_override={'timestamp_utc':'2026-10-25T01:00:00Z'})
        sha=self.commit(code='b')
        with self.assertRaisesRegex(ValueError,'time regression'): self.verify(sha)

    def test_future_time_rejected(self):
        sha=self.commit(record_override={'timestamp_utc':'2026-10-25T03:00:00.000001Z'})
        with self.assertRaisesRegex(ValueError,'future'): self.verify(sha)

    def test_exact_time_is_allowed(self):
        sha=self.commit(record_override={'timestamp_utc':'2026-10-25T03:00:00Z'})
        self.assertEqual(1,self.verify(sha)['revisions'])

    def test_unverified_utc_rejected(self):
        sha=self.commit()
        for now in [None,dt.datetime(2026,10,25), '2026-10-25']:
            with self.subTest(now=now), self.assertRaises(ValueError): self.verify(sha,now=now)

    def test_missing_log_rejected(self):
        sha=self.commit(write_log=False)
        with self.assertRaises(ValueError): self.verify(sha)

    def test_jsonl_only_append_rejected(self):
        sha=self.commit(); self.m.write_bytes(v.blob(self.repo,self.anchor,v.PATHS[1]))
        self.git('add','.'); self.git('commit','--amend','--no-edit','-q')
        with self.assertRaises(ValueError): self.verify(self.git('rev-parse','HEAD'))

    def test_duplicate_legacy_entry_id(self):
        sha=self.commit(record_override={'entry_id':'LEGACY'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_duplicate_new_id_across_commits(self):
        self.commit(code='a',record_override={'entry_id':'SAME'})
        sha=self.commit(code='b',record_override={'entry_id':'SAME'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_duplicate_paths(self):
        for key in ['code_files','evidence_paths']:
            self.git('reset','--hard',self.anchor)
            sha=self.commit(record_override={key:['sample.txt','sample.txt']})
            with self.subTest(key=key),self.assertRaises(ValueError): self.verify(sha)

    def test_correction_unknown_id(self):
        sha=self.commit(record_override={'status':'CORRECTION','correction_of':'UNKNOWN'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_valid_legacy_correction(self):
        sha=self.commit(record_override={'status':'CORRECTION','correction_of':'LEGACY'})
        self.assertEqual(1,self.verify(sha)['revisions'])

    def test_valid_new_correction(self):
        self.commit(code='a',record_override={'entry_id':'FIRST'})
        sha=self.commit(code='b',record_override={'status':'CORRECTION','correction_of':'FIRST'})
        self.assertEqual(2,self.verify(sha)['revisions'])

    def test_self_correction_rejected(self):
        sha=self.commit(record_override={'entry_id':'SELF','status':'CORRECTION','correction_of':'SELF'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_legacy_history_mutation_truncation_and_reorder(self):
        for data in [b'changed\n',b'',b'\n{"entry_id":"LEGACY"}\n']:
            self.git('reset','--hard',self.anchor)
            self.commit()
            self.j.write_bytes(data)
            self.git('add','.'); self.git('commit','-qm','synthetic tamper')
            with self.subTest(data=data), self.assertRaises(ValueError): self.verify(self.git('rev-parse','HEAD'))

    def test_new_history_reordered(self):
        self.commit(code='a'); self.commit(code='b')
        legacy=v.blob(self.repo,self.anchor,v.PATHS[0])
        lines=self.j.read_bytes()[len(legacy):].splitlines(keepends=True)
        self.j.write_bytes(legacy+b''.join(reversed(lines)))
        self.git('add','.');self.git('commit','-qm','synthetic reorder')
        with self.assertRaises(ValueError): self.verify(self.git('rev-parse','HEAD'))

    def test_bad_middle_commit_cannot_be_cured(self):
        self.commit(code='a',write_log=False)
        sha=self.commit(code='b')
        with self.assertRaises(ValueError): self.verify(sha)

    def test_no_caller_selected_boundary(self):
        sha=self.commit()
        with patch.object(v,'AUDIT_ANCHOR',self.anchor):
            with self.assertRaises(TypeError):
                v.verify(self.repo,sha,profile='validator-audit',trusted_utc=NOW,boundary=sha)

    def test_profile_cannot_expand_exception(self):
        sha=self.commit()
        with self.assertRaises(ValueError):
            v.verify(self.repo,sha,profile='arbitrary',trusted_utc=NOW)
        # Source profile never silently falls back to this repo's audit boundary.
        with self.assertRaises(ValueError): v.verify(self.repo,sha,trusted_utc=NOW)

    def test_missing_ancestor_commit_object(self):
        sha=self.commit()
        # This synthetic repository uses loose objects; remove only its anchor commit.
        obj=self.repo/'.git/objects'/self.anchor[:2]/self.anchor[2:]
        self.assertTrue(obj.is_file()); obj.unlink()
        with self.assertRaises(ValueError): self.verify(sha)

    def test_shallow_history_rejected(self):
        sha=self.commit()
        (self.repo/'.git/shallow').write_text(sha+'\n')
        with self.assertRaises(ValueError): self.verify(sha)

    def test_replacement_cannot_hide_bad_middle(self):
        self.commit(write_log=False)
        sha=self.commit(code='b')
        self.git('replace',sha,self.anchor)
        with self.assertRaises(ValueError): self.verify(sha)

    def test_wrong_paths_rejected(self):
        sha=self.commit(record_override={'code_files':['wrong.txt']})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_missing_evidence_blob_rejected(self):
        sha=self.commit(record_override={'evidence_paths':['does-not-exist']})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_cli_cannot_move_boundary(self):
        sha=self.commit()
        script=pathlib.Path(v.__file__)
        p=subprocess.run(['python','-B',str(script),'--checkout',str(self.repo),
                          '--head',sha,'--profile','validator-audit','--boundary',sha],
                         capture_output=True,text=True)
        self.assertEqual(2,p.returncode)
        self.assertIn('unrecognized arguments',p.stderr)

    def test_schema1_cannot_extend_legacy_exception(self):
        sha=self.commit(record_override={'schema_version':'1.0'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_legacy_exception_field_not_accepted_in_new_records(self):
        sha=self.commit(record_override={'legacy_status':'LEGACY_AUDIT_EXCEPTION'})
        with self.assertRaises(ValueError): self.verify(sha)

    def test_graft_shortcut_rejected(self):
        sha=self.commit()
        graft=self.repo/'.git/info/grafts';graft.parent.mkdir(exist_ok=True)
        graft.write_text(sha+'\n')
        with self.assertRaises(ValueError): self.verify(sha)

    def test_binary_and_rename_paths(self):
        self.commit()
        self.git('mv','sample.txt','renamed.bin')
        (self.repo/'renamed.bin').write_bytes(b'\x00\xff')
        sha=self.commit(record_override={'code_files':['sample.txt','renamed.bin'],
                                         'evidence_paths':['renamed.bin']})
        # commit() recreated sample.txt with identical content, so only the binary
        # addition changed. Explicitly remove it to exercise both rename endpoints.
        (self.repo/'sample.txt').unlink()
        self.git('add','-A');self.git('commit','--amend','--no-edit','-q')
        self.assertEqual(2,self.verify(self.git('rev-parse','HEAD'))['revisions'])

    def test_new_entry_cannot_reference_later_entry(self):
        self.commit(record_override={'status':'CORRECTION','correction_of':'LATER'})
        sha=self.commit(code='b',record_override={'entry_id':'LATER'})
        with self.assertRaises(ValueError): self.verify(sha)
