"""通过 gh api (Contents API) 更新仓库中的非 .github 文件。
每个文件先 GET 取 sha，再 PUT 更新。gh 走自身 egress，规避 git 直连 443 被挡的问题。
"""
import subprocess, json, base64, tempfile, os, sys

REPO = "ledi13035/MINISO-AI-Product-Genome"
LOCAL = "D:/WorkBuddy/MINISO-AI-Product-Genome"
FILES = [
    "agents/design_agent.py",
    "demo/product_generation_demo.py",
    "tests/test_pipeline.py",
]
MSG = "feat(rule-engine): 按品类+关键词生成设计语言，优化产品命名与营销语"


def gh(method, path, body=None):
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["-X", method]
    cmd += [f"repos/{REPO}/{path}"]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                          dir=tempfile.gettempdir())
        json.dump(body, tmp)
        tmp.close()
        cmd += ["--input", tmp.name]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if tmp:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    if r.returncode != 0:
        raise RuntimeError(f"{method} {path} -> {r.stderr.strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


for rel in FILES:
    local_path = os.path.join(LOCAL, rel)
    with open(local_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    # 1) 取当前 sha
    cur = gh("GET", f"contents/{rel}")
    sha = cur.get("sha")
    # 2) 更新
    body = {
        "message": MSG,
        "content": b64,
        "encoding": "base64",
        "sha": sha,
        "branch": "main",
    }
    res = gh("PUT", f"contents/{rel}", body)
    print(f"OK  {rel}  ->  new sha {res.get('commit', {}).get('sha', '')[:10]}")
print("ALL_PUSHED")
