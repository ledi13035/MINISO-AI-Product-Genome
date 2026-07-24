#!/usr/bin/env python3
"""Flush the three pending template changes to GitHub via gh Contents API."""
import base64
import json
import subprocess
import sys

OWNER = "ledi13035"
REPO = "MINISO-AI-Product-Genome"

FILES = [
    "web/app.py",
    "web/templates/index.html",
    "web/templates/report.html",
]


def gh_api(method, path, body=None):
    cmd = ["gh", "api", f"--method", method, f"repos/{OWNER}/{REPO}/contents/{path}"]
    if body is not None:
        for k, v in body.items():
            cmd += ["-f", f"{k}={v}"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def main():
    ok = True
    for rel in FILES:
        with open(rel, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("ascii")
        # fetch existing sha (404 = new file)
        rc, out, err = gh_api("GET", rel)
        sha = None
        if rc == 0:
            try:
                sha = json.loads(out)["sha"]
            except Exception:
                sha = None
        body = {
            "message": f"feat: flush pending web changes ({rel})",
            "content": content_b64,
        }
        if sha:
            body["sha"] = sha
        rc, out, err = gh_api("PUT", rel, body)
        if rc == 0:
            print(f"[OK] pushed {rel}" + (f" (updated {sha[:7]})" if sha else " (new)"))
        else:
            ok = False
            print(f"[FAIL] {rel}: rc={rc}")
            print(err[:500])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
