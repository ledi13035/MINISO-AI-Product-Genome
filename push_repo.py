#!/usr/bin/env python3
"""
通过 GitHub API 提交并推送到 ledi13035/MINISO-AI-Product-Genome。
策略：
  - 主文件通过 Git Data API（单次原子提交）
  - .github/ 路径的文件若触发 tree 404，则回退到 Contents API 补充
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

REPO = "ledi13035/MINISO-AI-Product-Genome"
ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "README.md",
    "requirements.txt",
    "requirements-dev.txt",
    ".env.example",
    "pytest.ini",
    "conftest.py",
    "agents/__init__.py",
    "agents/llm.py",
    "agents/trend_agent.py",
    "agents/consumer_agent.py",
    "agents/design_agent.py",
    "agents/prediction_agent.py",
    "demo/product_generation_demo.py",
    "tests/test_agents.py",
    "tests/test_llm.py",
    "tests/test_pipeline.py",
    ".github/workflows/test.yml",       # 可能需要走 Contents API 回退
    "visualization/generate_dashboard.py",
    "visualization/dashboard.png",
]

DELETES = ["visualization/dashboard.png.placeholder"]


def gh_api(method, path, input_data=None):
    cmd = ["gh", "api", f"repos/{REPO}/{path}"]
    if method != "GET":
        cmd.insert(1, "-X")
        cmd.insert(2, method)
    if input_data is not None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", prefix="ghapi_", delete=False
        ) as tf:
            json.dump(input_data, tf)
            tmp = tf.name
        cmd.extend(["--input", tmp])
        r = subprocess.run(cmd, capture_output=True)
        try:
            os.unlink(tmp)
        except OSError:
            pass
        if r.returncode != 0:
            print(f"  ERROR {method} {path}: {r.stderr.decode()[:500]}")
            return None
        return json.loads(r.stdout)
    else:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ERROR GET {path}: {r.stderr[:300]}")
            sys.exit(1)
        return json.loads(r.stdout)


def create_blob(filepath):
    """上传文件内容为 Git blob，返回 SHA。"""
    with open(os.path.join(ROOT, filepath), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    blob = gh_api("POST", "git/blobs", {"content": b64, "encoding": "base64"})
    print(f"    blob: {filepath} ({os.path.getsize(os.path.join(ROOT, filepath))} bytes)")
    return blob["sha"]


def contents_api_put(filepath, message, branch="main"):
    """通过 Contents API 创建/更新文件（自动产生一个 commit）。"""
    fpath = os.path.join(ROOT, filepath)
    with open(fpath, "rb") as fh:
        content_b64 = base64.b64encode(fh.read()).decode()
    r = subprocess.run(
        [
            "gh", "api", "-XPUT", f"repos/{REPO}/contents/{filepath}",
            "-f", f"message={message}",
            "-f", f"content={content_b64}",
            "-f", "encoding=base64",
            "-f", f"branch={branch}",
        ],
        capture_output=True,
    )
    if r.returncode != 0:
        print(f"  WARNING Contents API {filepath}: {r.stderr.decode()[:200]}")
        return None
    d = json.loads(r.stdout)
    print(f"    contents: {filepath} -> {d['commit']['sha'][:12]}")
    return d["commit"]["sha"]


def main():
    msg = (
        "feat: 接入 GPT-4o 真实 LLM、pytest 测试、GitHub Actions CI 与 matplotlib 真实可视化\n\n"
        "- agents/llm.py: 统一 GPT-4o 接入层（无 key 自动回退规则引擎，支持 MockLLM 注入测试）\n"
        "- 四个 Agent 新增 analyze(llm,...) LLM 路径，保留 run() 规则引擎\n"
        "- demo 支持 --no-llm / --category / --keywords，自动选择引擎\n"
        "- tests/: pytest 覆盖各 Agent 逻辑、JSON 解析与完整 LLM 代码路径\n"
        "- .github/workflows/test.yml: push/PR 自动跑测试（Python 3.10/3.11/3.12）\n"
        "- visualization: matplotlib 生成真实 dashboard.png 替换占位图\n"
        "- requirements.txt / .env.example / README 升级"
    )

    # Phase 1: 获取 base
    print("==> 获取 base commit / tree")
    ref = gh_api("GET", "git/ref/heads/main")
    base_sha = ref["object"]["sha"]
    commit = gh_api("GET", f"git/commits/{base_sha}")
    tree_sha = commit["tree"]["sha"]
    print(f"    base={base_sha}")

    # Phase 2: 创建所有 blobs
    print("\n==> 创建 blobs")
    entries = []
    for f in FILES:
        sha = create_blob(f)
        entries.append({"path": f, "mode": "100644", "type": "blob", "sha": sha})
    for d in DELETES:
        entries.append({"path": d, "mode": "100644", "type": "blob", "sha": None})
        print(f"    delete: {d}")

    # Phase 3: 尝试完整树提交；若 404 则拆分
    print("\n==> 创建 tree + commit")

    # 分离 .github/ 条目（已知可能触发 tree 404）
    github_entries = [e for e in entries if e["path"].startswith(".github/")]
    other_entries = [e for e in entries if not e["path"].startswith(".github/")]

    full_tree = gh_api("POST", "git/trees", {"base_tree": tree_sha, "tree": entries})

    if full_tree is not None:
        # 完整树成功 → 单次提交
        new_commit = gh_api("POST", "git/commits", {
            "message": msg,
            "tree": full_tree["sha"],
            "parents": [base_sha],
        })
        gh_api("PATCH", "git/refs/heads/main", {"sha": new_commit["sha"], "force": False})
        final_sha = new_commit["sha"]
    else:
        # 拆分：先提交不含 .github/ 的文件，再 Contents API 补上
        print("    (tree 404 → 拆分为两阶段提交)")
        part_tree = gh_api("POST", "git/trees", {"base_tree": tree_sha, "tree": other_entries})
        c1 = gh_api("POST", "git/commits", {
            "message": msg + "\n\n[Phase 1/2] core files via Git Data API",
            "tree": part_tree["sha"],
            "parents": [base_sha],
        })
        gh_api("PATCH", "git/refs/heads/main", {"sha": c1["sha"], "force": False})
        print(f"    Phase 1: {c1['sha'][:12]}")

        final_sha = c1["sha"]
        for e in github_entries:
            if e.get("sha") is None:
                continue  # deletion handled separately
            sha = contents_api_put(e["path"], msg + f"\n\n[Phase 2/2] {e['path']}")
            if sha:
                final_sha = sha

    print(f"\n==> DONE! 最终提交: {final_sha}")
    print(f"https://github.com/ledi13035/MINISO-AI-Product-Genome/commit/{final_sha}")


if __name__ == "__main__":
    main()
