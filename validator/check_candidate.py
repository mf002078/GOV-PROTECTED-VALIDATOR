"""Separately owned offline structural validator; no candidate code execution."""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ANCHOR = "1975ee74a62be815a032254d51603e15b4bbe093"
PATHS = ("worklog/CHANGELOG.jsonl", "worklog/CHANGELOG.md")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ENTRY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
EXCLUDED = set(PATHS)
KEYS = {"schema_version","entry_id","timestamp_utc","version","issue_id","summary","completed_items","code_files","evidence_paths","status","baseline_sha","author_role","correction_of"}

def call(repo, *args):
    result = subprocess.run(["git","-C",str(repo),*args],capture_output=True)
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

def verify(repo, head):
    if not HEX40.fullmatch(head):
        raise ValueError("head must be 40 lowercase hex characters")
    if call(repo,"rev-parse","--verify",head+"^{commit}").decode().strip()!=head:
        raise ValueError("head SHA missing")
    if call(repo,"merge-base",ANCHOR,head).decode().strip()!=ANCHOR:
        raise ValueError("head not descended from approved anchor")
    original=[blob(repo,ANCHOR,p) for p in PATHS]
    prior=list(original)
    seen=set()
    prior_count=0
    revisions=call(repo,"rev-list","--reverse","--first-parent",ANCHOR+".."+head).decode().splitlines()
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
            if not isinstance(record,dict) or set(record)!=KEYS or record["schema_version"]!="2.0":
                raise ValueError("invalid new worklog schema")
            if not isinstance(record["entry_id"],str) or not ENTRY.fullmatch(record["entry_id"]) or record["entry_id"] in seen:
                raise ValueError("duplicate or invalid entry ID")
            if record["baseline_sha"]!=parent or record["status"] not in {"IMPLEMENTED","TESTED","BLOCKED","RELEASED","CORRECTION"}:
                raise ValueError("incorrect baseline/status")
            if not isinstance(record["completed_items"],list) or not record["completed_items"]:
                raise ValueError("missing accomplishments")
            if not isinstance(record["code_files"],list) or not isinstance(record["evidence_paths"],list) or not record["evidence_paths"]:
                raise ValueError("missing paths/evidence")
            for p in record["code_files"]+record["evidence_paths"]:
                if not isinstance(p,str) or not p or p.startswith("/") or "\\" in p or any(v in ("",".","..") for v in p.split("/")):
                    raise ValueError("unsafe path")
            declared.update(record["code_files"])
            seen.add(record["entry_id"])
        if declared!=changed:
            raise ValueError("changed paths differ from declared paths")
        prior=cur
        prior_count=len(records)
    if not revisions:
        raise ValueError("no revisions examined")
    return {"candidate_sha":head,"revisions":len(revisions),"new_entries":prior_count,"level":"STRUCTURE_PASS_NOT_ATTESTED","gate_a":"BLOCKED/UNVERIFIED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checkout",type=pathlib.Path,required=True)
    p.add_argument("--head",required=True)
    a=p.parse_args()
    try:
        print(json.dumps(verify(a.checkout,a.head),sort_keys=True))
    except (ValueError,OSError,TypeError,KeyError) as e:
        print("PROTECTED_PROTOTYPE_REJECT",e,file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":sys.exit(main())
