"""把本次增强（设计库 + Web 界面）推到 GitHub，使用 gh api Contents API。"""
import subprocess, json, base64, tempfile, os, sys

REPO = "ledi13035/MINISO-AI-Product-Genome"
ROOT = os.path.dirname(os.path.abspath(__file__))
BRANCH = "main"
MSG = "feat: 丰富设计元素库(季节限定/联名款) + 新增 Web 可视化界面"

# (本地相对路径, 远端路径)
FILES = [
    ("agents/design_agent.py", "agents/design_agent.py"),
    ("web/app.py", "web/app.py"),
    ("web/templates/index.html", "web/templates/index.html"),
    ("web/templates/report.html", "web/templates/report.html"),
    ("requirements.txt", "requirements.txt"),
    ("tests/test_agents.py", "tests/test_agents.py"),
]


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
        except Exception:
            pass
    return r


def main():
    for local, remote in FILES:
        with open(os.path.join(ROOT, local), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        # 查询是否已存在，拿 sha
        resp = gh("GET", f"contents/{remote}")
        sha = None
        if resp.returncode == 0:
            try:
                sha = json.loads(resp.stdout).get("sha")
            except Exception:
                sha = None
        body = {
            "message": MSG,
            "content": b64,
            "encoding": "base64",
            "branch": BRANCH,
        }
        if sha:
            body["sha"] = sha
        r = gh("PUT", f"contents/{remote}", body)
        status = "UPDATED" if sha else "CREATED"
        ok = r.returncode == 0
        print(f"[{status if ok else 'FAIL'}] {remote} (rc={r.returncode})")
        if not ok:
            print("   ", r.stderr[:200])
    print("DONE")


if __name__ == "__main__":
    main()
