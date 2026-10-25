"""Separately owned offline structural validator; no candidate code execution."""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

ANCHOR = "1975ee74a62be815a032254d51603e15b4bbe093"
AUDIT_ANCHOR = "26026250d7ba49f29349a706a27676827af861d7"
PATHS = ("worklog/CHANGELOG.jsonl", "worklog/CHANGELOG.md")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ENTRY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
EXCLUDED = set(PATHS)
KEYS = {"schema_version","entry_id","timestamp_utc","version","issue_id","summary","completed_items","code_files","evidence_paths","status","baseline_sha","author_role","correction_of"}

def call(repo, *args):
    result = subprocess.run(["git","--no-replace-objects","-C",str(repo),*args],
                            env=dict(os.environ, GIT_NO_LAZY_FETCH="1"),capture_output=True)
    if result.returncode:
        raise ValueError("git check failed: "+args[0])
    return result.stdout

def blob(repo, sha, path):
    return call(repo,"show",sha+":"+path)

def render(record):
    return ("\n## "+record["entry_id"]+"\n\n```json\n"+
            json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n```\n").encode()

def paths(repo, parent, sha):
    raw=call(repo,"diff","--no-renames","--no-ext-diff","--no-textconv","--name-only","-z",parent,sha,"--")
    out=set()
    for p in raw.split(b"\x00"):
        if not p:continue
        x=p.decode("utf-8")
        if not x or "\\" in x or "\n" in x or "\r" in x or any(s in ("",".","..") for s in x.split("/")):
            raise ValueError("invalid changed path")
        out.add(x)
    return out

def verify(repo, head, profile="source", *, trusted_utc=None):
    """Read Git objects only. CLI fixes profile boundaries and obtains UTC itself.

    trusted_utc is an executor reference; tests inject synthetic time, never
    candidate journal data. An absent/naive reference fails closed.
    """
    if profile not in ("source", "validator-audit"):
        raise ValueError("unknown fixed-boundary profile")
    boundary = ANCHOR if profile == "source" else AUDIT_ANCHOR
    if (not isinstance(trusted_utc,dt.datetime) or trusted_utc.tzinfo is None
            or trusted_utc.utcoffset()!=dt.timedelta(0)):
        raise ValueError("BLOCKED/NOT_VERIFIED: trusted execution UTC required")
    if not isinstance(head,str) or not HEX40.fullmatch(head):
        raise ValueError("head must be 40 lowercase hex characters")
    if call(repo,"rev-parse","--verify",head+"^{commit}").decode().strip()!=head:
        raise ValueError("head SHA missing")
    if call(repo,"rev-parse","--is-shallow-repository").strip()!=b"false":
        raise ValueError("incomplete shallow ancestry")
    graft=pathlib.Path(call(repo,"rev-parse","--git-path","info/grafts").decode().strip())
    if not graft.is_absolute(): graft=pathlib.Path(repo)/graft
    if graft.exists(): raise ValueError("grafted history not accepted")
    # Traverse all real ancestor/tree/blob objects. No promisor lazy fetch and
    # no replace-ref shortcut may hide a missing object or an earlier bad commit.
    call(repo,"rev-list","--objects","--missing=error",head)
    if call(repo,"merge-base",boundary,head).decode().strip()!=boundary:
        raise ValueError("head not descended from approved anchor")
    original=[blob(repo,boundary,p) for p in PATHS]
    prior=list(original)
    seen=set()
    for line in original[0].splitlines():
        legacy=json.loads(line)
        entry_id=legacy.get("entry_id") if isinstance(legacy,dict) else None
        if not isinstance(entry_id,str) or not ENTRY.fullmatch(entry_id) or entry_id in seen:
            raise ValueError("invalid legacy identity set")
        seen.add(entry_id)
    # The one approved discontinuity: do not seed time from legacy records.
    last_new_time=None
    prior_count=0
    revisions=call(repo,"rev-list","--reverse","--first-parent",boundary+".."+head).decode().splitlines()
    for sha in revisions:
        parents=call(repo,"rev-list","--parents","-n","1",sha).decode().split()
        if len(parents)!=2:raise ValueError("merge commit not accepted")
        parent=parents[1]
        cur=[blob(repo,sha,p) for p in PATHS]
        if any(not cur[i].startswith(prior[i]) for i in (0,1)):
            raise ValueError("history rewritten")
        suffix=cur[0][len(original[0]):]
        if suffix and not suffix.endswith(b"\n"):
            raise ValueError("missing final newline")
        try:
            records=[json.loads(line) for line in suffix.splitlines()]
        except (ValueError,UnicodeDecodeError):
            raise ValueError("malformed JSONL") from None
        if len(records)<=prior_count:
            raise ValueError("revision lacks new worklog entry")
        if cur[1]!=original[1]+b"".join(render(r) for r in records):
            raise ValueError("JSONL / Markdown mismatch")
        new=records[prior_count:]
        changed=paths(repo,parent,sha)-EXCLUDED
        declared=set()
        for record in new:
            if not valid_strict_record(record, parent):
                raise ValueError("invalid new worklog schema")
            if not isinstance(record["entry_id"],str) or not ENTRY.fullmatch(record["entry_id"]) or record["entry_id"] in seen:
                raise ValueError("duplicate or invalid entry ID")
            if record["baseline_sha"]!=parent or record["status"] not in {"IMPLEMENTED","TESTED","BLOCKED","RELEASED","CORRECTION"}:
                raise ValueError("incorrect baseline/status")
            if record["status"]=="CORRECTION" and record["correction_of"] not in seen:
                raise ValueError("correction must reference a prior existing entry ID")
            current_time=dt.datetime.fromisoformat(record["timestamp_utc"].replace("Z","+00:00"))
            if last_new_time is not None and current_time<last_new_time:
                raise ValueError("post-boundary time regression")
            if current_time>trusted_utc:
                raise ValueError("post-boundary timestamp in future")
            last_new_time=current_time
            if not isinstance(record["completed_items"],list) or not record["completed_items"]:
                raise ValueError("missing accomplishments")
            if not isinstance(record["code_files"],list) or not isinstance(record["evidence_paths"],list) or not record["evidence_paths"]:
                raise ValueError("missing paths/evidence")
            for p in record["code_files"]+record["evidence_paths"]:
                if not isinstance(p,str) or not p or p.startswith("/") or "\\" in p or any(v in ("",".","..") for v in p.split("/")):
                    raise ValueError("unsafe path")
            declared.update(record["code_files"])
            for evidence_path in record["evidence_paths"]:
                blob(repo,sha,evidence_path)
            seen.add(record["entry_id"])
        if declared!=changed:
            raise ValueError("changed paths differ from declared paths")
        prior=cur
        prior_count=len(records)
    if not revisions:
        raise ValueError("no revisions examined")
    return {"candidate_sha":head,"revisions":len(revisions),"new_entries":prior_count,
            "legacy_boundary_sha":boundary,
            "legacy_status":"LEGACY_AUDIT_EXCEPTION" if profile=="validator-audit" else "LEGACY_COMPAT",
            "provenance":"NOT_ATTESTED","verified_utc_limit":trusted_utc.isoformat(),
            "level":"STRUCTURE_PASS_NOT_ATTESTED","gate_a":"BLOCKED/UNVERIFIED"}

def valid_strict_record(record, parent):
    """Basic strict schema guard for independent reviewer; no acceptance side effects."""
    if not isinstance(record, dict) or set(record) != KEYS or record.get("schema_version") != "2.0":
        return False
    for k in ("entry_id","version","issue_id","summary","author_role"):
        if not isinstance(record[k],str) or not record[k].strip():
            return False
    if not ENTRY.fullmatch(record["entry_id"]):
        return False
    if not isinstance(record["timestamp_utc"],str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z",record["timestamp_utc"]):
        return False
    try:
        dt.datetime.fromisoformat(record["timestamp_utc"].replace("Z","+00:00"))
    except ValueError:
        return False
    if record["baseline_sha"] != parent or record["status"] not in {"IMPLEMENTED","TESTED","BLOCKED","RELEASED","CORRECTION"}:
        return False
    if record["correction_of"] is not None and record["status"] != "CORRECTION":
        return False
    if record["status"] == "CORRECTION" and not isinstance(record["correction_of"],str):
        return False
    for k in ("completed_items","code_files","evidence_paths"):
        if not isinstance(record[k],list) or (k!="code_files" and not record[k]):
            return False
        for value in record[k]:
            if not isinstance(value,str) or not value.strip():
                return False
            if k!="completed_items" and (value.startswith("/") or "\\" in value or
                    any(c in value for c in "\n\r\x00") or
                    any(s in ("",".","..") for s in value.split("/"))):
                return False
        if k in ("code_files","evidence_paths") and len(record[k])!=len(set(record[k])):
            return False
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",type=pathlib.Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--profile",choices=("source","validator-audit"),default="source")
    a=p.parse_args()
    try:
        if __package__:
            from .utc_reference import acquire_utc
        else:
            from utc_reference import acquire_utc
        reference=acquire_utc()
        result=verify(a.checkout,a.head,profile=a.profile,trusted_utc=reference)
        result["utc_source"]="TLS_GITHUB_DATE_MIN_EXECUTOR_CLOCK"
        print(json.dumps(result,sort_keys=True))
    except (ValueError,OSError,TypeError,KeyError) as e:
        print("PROTECTED_PROTOTYPE_REJECT",e,file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":sys.exit(main())
