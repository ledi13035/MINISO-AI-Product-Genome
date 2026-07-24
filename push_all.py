#!/usr/bin/env python3
"""Full-sync the local MINISO-AI-Product-Genome project to GitHub via gh Contents API."""
import base64
import json
import os
import subprocess
import sys

OWNER = "ledi13035"
REPO = "MINISO-AI-Product-Genome"
ROOT = r"D:\WorkBuddy\MINISO-AI-Product-Genome"

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
SKIP_EXT = {".pyc"}


def gh(method, path, body=None):
    cmd = ["gh", "api", "--method", method, f"repos/{OWNER}/{REPO}/contents/{path}"]
    if body is not None:
        for k, v in body.items():
            cmd += ["-f", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def get_remote(path):
    rc, out, err = gh("GET", path)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def main():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if any(fn.endswith(e) for e in SKIP_EXT):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            files.append(rel)

    print(f"found {len(files)} files to sync")
    ok = skip = fail = 0
    for rel in files:
        full = os.path.join(ROOT, rel.replace("/", os.sep))
        with open(full, "rb") as f:
            local = f.read()
        b64 = base64.b64encode(local).decode("ascii")
        rem = get_remote(rel)
        if rem and base64.b64decode(rem.get("content", "")) == local:
            print(f"[SKIP] {rel} (unchanged)")
            skip += 1
            continue
        body = {"message": f"sync: {rel}", "content": b64}
        sha = rem.get("sha") if rem else None
        if sha:
            body["sha"] = sha
        rc, out, err = gh("PUT", rel, body)
        if rc == 0:
            print(f"[OK] {rel}" + (f" (updated {sha[:7]})" if sha else " (new)"))
            ok += 1
        else:
            print(f"[FAIL] {rel}: {err[:300]}")
            fail += 1

    print(f"\nSUMMARY  ok={ok}  skip={skip}  fail={fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
