import base64, json, tempfile, os, subprocess, sys

REPO = "ledi13035/MINISO-AI-Product-Genome"
BASE_COMMIT = "c67ac345022322e55540d25ca620db0722eb74b1"
CI_LOCAL = r"D:\WorkBuddy\MINISO-AI-Product-Genome\.github\workflows\test.yml"

def gh_api(method, url, body=None):
    cmd = ["gh", "api", "-X", method, f"repos/{REPO}/{url}"]
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

# 1) get base tree recursively (the 18 files already in repo)
r, tree = gh_api("GET", f"git/trees/{BASE_COMMIT}?recursive=1")
if r.returncode != 0:
    print("FAIL get base tree:", r.stderr); sys.exit(1)
entries = tree.get("tree", [])
print("base entries:", len(entries))
# sanity: any two-slash path already? (shouldn't be)
two_slash = [e["path"] for e in entries if e["path"].count("/") >= 2]
print("two-slash entries in base:", two_slash)
# drop any existing .github entries (there shouldn't be any)
entries = [e for e in entries if not e["path"].startswith(".github/") and e["path"] != ".github"]
print("entries after filter:", len(entries))

# 2) blob for CI file
with open(CI_LOCAL, "rb") as f:
    content_b64 = base64.b64encode(f.read()).decode("ascii")
r, blob = gh_api("POST", "git/blobs", {"content": content_b64, "encoding": "base64"})
if r.returncode != 0:
    print("FAIL blob:", r.stderr); sys.exit(1)
ci_blob = blob["sha"]
print("ci_blob:", ci_blob)

# 3) build nested tree objects explicitly (avoid two-slash flat paths)
r, wf_tree = gh_api("POST", "git/trees", {
    "tree": [{"path": "test.yml", "mode": "100644", "type": "blob", "sha": ci_blob}]
})
if r.returncode != 0:
    print("FAIL workflows tree:", r.stderr); sys.exit(1)
wf_sha = wf_tree["sha"]

r, gh_tree = gh_api("POST", "git/trees", {
    "tree": [{"path": "workflows", "mode": "040000", "type": "tree", "sha": wf_sha}]
})
if r.returncode != 0:
    print("FAIL .github tree:", r.stderr); sys.exit(1)
gh_sha = gh_tree["sha"]

# 4) top-level tree = 18 base entries (flat one-slash, proven to work) + explicit .github tree
top_entries = [{"path": e["path"], "mode": e["mode"], "type": e["type"], "sha": e["sha"]} for e in entries]
top_entries.append({"path": ".github", "mode": "040000", "type": "tree", "sha": gh_sha})
print("top_entries count:", len(top_entries))
# verify no two-slash entry
bad = [e["path"] for e in top_entries if e["path"].count("/") >= 2]
print("two-slash in top:", bad)

r, top_tree = gh_api("POST", "git/trees", {"tree": top_entries})
if r.returncode != 0:
    print("FAIL top tree:", r.stderr); sys.exit(1)
top_sha = top_tree["sha"]
print("top_tree:", top_sha)

# 5) commit
r, commit = gh_api("POST", "git/commits", {
    "message": "ci: add GitHub Actions test workflow (.github/workflows/test.yml)",
    "tree": top_sha,
    "parents": [BASE_COMMIT],
})
if r.returncode != 0:
    print("FAIL commit:", r.stderr); sys.exit(1)
new_commit = commit["sha"]
print("new_commit:", new_commit)

# 6) update ref
r, _ = gh_api("PATCH", "git/refs/heads/main", {"sha": new_commit})
if r.returncode != 0:
    print("FAIL ref:", r.stderr); sys.exit(1)
print("SUCCESS ->", new_commit)
