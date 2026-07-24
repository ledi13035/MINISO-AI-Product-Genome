#!/usr/bin/env python3
"""Full-sync the local MINISO-AI-Product-Genome project to GitHub via gh Contents API.
Uses --input <tempfile> for PUT bodies to avoid Windows command-line length limits.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

OWNER = "ledi13035"
REPO = "MINISO-AI-Product-Genome"
ROOT = r"D:\WorkBuddy\MINISO-AI-Product-Genome"

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
SKIP_EXT = {".pyc"}


def gh_get(path):
    cmd = ["gh", "api", f"repos/{OWNER}/{REPO}/contents/{path}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def gh_put(path, body):
    # write body to a temp file, use --input to avoid command-line length limits
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="ghput_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(body, f)
        cmd = ["gh", "api", "--method", "PUT",
               f"repos/{OWNER}/{REPO}/contents/{path}", "--input", tmp]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


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
        rem = gh_get(rel)
        if rem and base64.b64decode(rem.get("content", "")) == local:
            print(f"[SKIP] {rel} (unchanged)")
            skip += 1
            continue
        body = {"message": f"sync: {rel}",
                "content": base64.b64encode(local).decode("ascii")}
        sha = rem.get("sha") if rem else None
        if sha:
            body["sha"] = sha
        rc, out, err = gh_put(rel, body)
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
