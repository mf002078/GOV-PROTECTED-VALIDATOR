"""Bounded untrusted PR Git diff. No execution, no egress, no credential use."""
import hashlib, json, os, re, subprocess
from .llm_review_contract import assess_report
SHA=re.compile(r"[0-9a-f]{40}\Z")
DIGEST=re.compile(r"[0-9a-f]{64}\Z")
class ReviewBlocked(ValueError): pass
def git(repo,*args):
    env={**os.environ,"GIT_NO_REPLACE_OBJECTS":"1","GIT_OPTIONAL_LOCKS":"0","GIT_TERMINAL_PROMPT":"0"}
    try:
        r=subprocess.run(["git","-C",str(repo),*args],capture_output=True,timeout=20,env=env)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ReviewBlocked("git execution failed") from exc
    if r.returncode: raise ReviewBlocked("git rejected")
    return r.stdout
def safe_path(p):
    return (bool(p) and len(p)<=512 and not p.startswith("/") and "\\" not in p and
            not any(c in p for c in "\r\n\x00") and
            all(x not in ("",".","..") for x in p.split("/")))
def prepare_review(repo,base,head,policy_sha256):
    if not all(isinstance(x,str) and SHA.fullmatch(x) for x in (base,head)) or base==head:
        raise ReviewBlocked("invalid sha")
    if not isinstance(policy_sha256,str) or not DIGEST.fullmatch(policy_sha256):
        raise ReviewBlocked("invalid policy")
    if git(repo,"rev-parse","--is-shallow-repository").strip()!=b"false":
        raise ReviewBlocked("shallow repository")
    for sha in (base,head):
        if git(repo,"rev-parse","--verify",sha+"^{commit}").strip()!=sha.encode():
            raise ReviewBlocked("missing commit")
    git(repo,"merge-base","--is-ancestor",base,head)
    raw=git(repo,"diff","--no-ext-diff","--no-textconv","--no-renames","--name-only","-z",base,head,"--")
    try: paths=[p.decode("utf-8") for p in raw.split(b"\0") if p]
    except UnicodeDecodeError as exc: raise ReviewBlocked("nonutf8 path") from exc
    if not paths or len(paths)>50 or len(set(paths))!=len(paths) or any(not safe_path(p) for p in paths):
        raise ReviewBlocked("invalid paths")
    if any(p.lower().endswith((".pem",".pfx",".p12",".key",".env")) or "/.env" in p.lower() for p in paths):
        raise ReviewBlocked("sensitive path")
    raw=git(repo,"diff","--no-ext-diff","--no-textconv","--no-renames","--binary",base,head,"--")
    if not raw or len(raw)>100000 or b"GIT binary patch" in raw:
        raise ReviewBlocked("binary/oversize diff")
    try: diff=raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise ReviewBlocked("nonutf8 diff") from exc
    return dict(repository_data_trust="UNTRUSTED",base_sha=base,head_sha=head,
                policy_sha256=policy_sha256,diff_sha256=hashlib.sha256(raw).hexdigest(),
                changed_paths=paths,diff_data=diff)
def evaluate_model_output(raw,*,expected_repo,request):
    if not isinstance(raw,(bytes,str)) or len(raw)>64000: return "BLOCKED"
    try:
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d: raise ValueError("duplicate key")
                d[k]=v
            return d
        obj=json.loads(raw,object_pairs_hook=unique)
        return assess_report(obj,expected_repo=expected_repo,expected_base=request["base_sha"],
                             expected_head=request["head_sha"],expected_policy=request["policy_sha256"])
    except (ValueError,TypeError,KeyError,UnicodeDecodeError):
        return "BLOCKED"
