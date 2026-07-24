import base64, json, tempfile, os, subprocess, sys

REPO = "ledi13035/MINISO-AI-Product-Genome"
BASE_COMMIT = "c67ac345022322e55540d25ca620db0722eb74b1"
CI_LOCAL = r"D:\WorkBuddy\MINISO-AI-Product-Genome\.github\workflows\test.yml"

def gh_api(method, url, body=None):
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["-X", method]
    cmd += [f"repos/{REPO}/{url}"]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=tempfile.gettempdir())
        json.dump(body, tmp); tmp.close()
        cmd += ["--input", tmp.name]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if tmp:
        try: os.unlink(tmp.name)
        except Exception: pass
    return r, (json.loads(r.stdout) if r.stdout.strip() else None)

# 1) base commit -> tree (direct children only)
r, commit = gh_api("GET", f"git/commits/{BASE_COMMIT}")
base_tree = commit["tree"]["sha"]
print("base_tree:", base_tree)

# 2) CI blob
with open(CI_LOCAL, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
r, blob = gh_api("POST", "git/blobs", {"content": b64, "encoding": "base64"})
ci_sha = blob["sha"]; print("ci_blob:", ci_sha)

# 3) explicit nested trees (single-segment entries only)
r, wf = gh_api("POST", "git/trees", {"tree": [{"path": "test.yml", "mode": "100644", "type": "blob", "sha": ci_sha}]})
wf_sha = wf["sha"]
r, gh = gh_api("POST", "git/trees", {"tree": [{"path": "workflows", "mode": "040000", "type": "tree", "sha": wf_sha}]})
gh_sha = gh["sha"]

# 4) merge .github into base tree via base_tree (single-segment entry -> no two-slash flat path)
r, top = gh_api("POST", "git/trees", {
    "base_tree": base_tree,
    "tree": [{"path": ".github", "mode": "040000", "type": "tree", "sha": gh_sha}],
})
if r.returncode != 0:
    print("FAIL top tree:", r.stderr); sys.exit(1)
top_sha = top["sha"]; print("top_tree:", top_sha)

# 5) commit
r, c = gh_api("POST", "git/commits", {
    "message": "ci: add GitHub Actions test workflow (.github/workflows/test.yml)",
    "tree": top_sha,
    "parents": [BASE_COMMIT],
})
if r.returncode != 0:
    print("FAIL commit:", r.stderr); sys.exit(1)
new_commit = c["sha"]; print("new_commit:", new_commit)

# 6) update ref
r, _ = gh_api("PATCH", "git/refs/heads/main", {"sha": new_commit, "force": False})
if r.returncode != 0:
    print("FAIL ref:", r.stderr); sys.exit(1)
print("SUCCESS ->", new_commit)
