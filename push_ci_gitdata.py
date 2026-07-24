import base64, json, tempfile, os, subprocess, sys

REPO = "ledi13035/MINISO-AI-Product-Genome"
BASE_COMMIT = "c67ac345022322e55540d25ca620db0722eb74b1"
CI_PATH = ".github/workflows/test.yml"
CI_LOCAL = r"D:\WorkBuddy\MINISO-AI-Product-Genome\.github\workflows\test.yml"

def gh_api(method, url, body=None):
    cmd = ["gh", "api", "-X", method, f"repos/{REPO}/{url}"]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=tempfile.gettempdir())
        json.dump(body, tmp)
        tmp.close()
        cmd += ["--input", tmp.name]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if tmp:
        try: os.unlink(tmp.name)
        except Exception: pass
    return r, (json.loads(r.stdout) if r.stdout.strip() else None)

# 1) get base commit -> tree sha
r, data = gh_api("GET", f"git/commits/{BASE_COMMIT}")
if r.returncode != 0:
    print("FAIL get base commit:", r.stderr); sys.exit(1)
base_tree = data["tree"]["sha"]
print("base_tree:", base_tree)

# 2) create blob for CI content
with open(CI_LOCAL, "rb") as f:
    content_b64 = base64.b64encode(f.read()).decode("ascii")
r, blob = gh_api("POST", "git/blobs", {"content": content_b64, "encoding": "base64"})
if r.returncode != 0:
    print("FAIL create blob:", r.stderr); sys.exit(1)
blob_sha = blob["sha"]
print("blob_sha:", blob_sha)

# 3) create tree with ONLY the CI entry, based on base_tree
tree_body = {
    "base_tree": base_tree,
    "tree": [{"path": CI_PATH, "mode": "100644", "type": "blob", "sha": blob_sha}],
}
r, tree = gh_api("POST", "git/trees", tree_body)
if r.returncode != 0:
    print("FAIL create tree:", r.stderr); sys.exit(1)
new_tree = tree["sha"]
print("new_tree:", new_tree)

# 4) create commit
commit_body = {
    "message": "ci: add GitHub Actions test workflow (.github/workflows/test.yml)",
    "tree": new_tree,
    "parents": [BASE_COMMIT],
}
r, commit = gh_api("POST", "git/commits", commit_body)
if r.returncode != 0:
    print("FAIL create commit:", r.stderr); sys.exit(1)
new_commit = commit["sha"]
print("new_commit:", new_commit)

# 5) update main ref
r, _ = gh_api("PATCH", "git/refs/heads/main", {"sha": new_commit})
if r.returncode != 0:
    print("FAIL update ref:", r.stderr); sys.exit(1)
print("SUCCESS -> commit", new_commit)
