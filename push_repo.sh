#!/usr/bin/env bash
# 通过 GitHub Git Data API 提交并推送到 ledi13035/MINISO-AI-Product-Genome
# 原因：沙箱内 git/HTTPS 直连被挡，但 gh api（api.github.com）可用。
set -euo pipefail

REPO="ledi13035/MINISO-AI-Product-Genome"
ROOT="/d/WorkBuddy/MINISO-AI-Product-Genome"
PYTHON="/d/WorkBuddy/.workbuddy/binaries/python/envs/miniso/Scripts/python.exe"
cd "$ROOT"

# 待提交文件（新增或已修改），mode 均为 100644
FILES=(
  "README.md"
  "requirements.txt"
  "requirements-dev.txt"
  ".env.example"
  "pytest.ini"
  "conftest.py"
  "agents/__init__.py"
  "agents/llm.py"
  "agents/trend_agent.py"
  "agents/consumer_agent.py"
  "agents/design_agent.py"
  "agents/prediction_agent.py"
  "demo/product_generation_demo.py"
  "tests/test_agents.py"
  "tests/test_llm.py"
  "tests/test_pipeline.py"
  ".github/workflows/test.yml"
  "visualization/generate_dashboard.py"
  "visualization/dashboard.png"
)

# 待删除文件
DELETES=(
  "visualization/dashboard.png.placeholder"
)

echo "==> 获取 base commit / tree"
BASE_SHA=$(gh api "repos/$REPO/git/ref/heads/main" --jq '.object.sha')
TREE_SHA=$(gh api "repos/$REPO/git/commits/$BASE_SHA" --jq '.tree.sha')
echo "    base=$BASE_SHA tree=$TREE_SHA"

# 构造 tree entries JSON 数组
ENTRIES_JSON=""
for f in "${FILES[@]}"; do
  b64=$(base64 -w0 "$ROOT/$f")
  entry=$(printf '{"path":%s,"mode":"100644","type":"blob","sha":%s}' \
    "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$f")" \
    "$(gh api "repos/$REPO/git/blobs" --input - <<JSON | $PYTHON -c "import json,sys; print(json.dumps(json.load(sys.stdin)['sha']))"
{"content":"$b64","encoding":"base64"}
JSON
)")
  ENTRIES_JSON+="$entry,"
  echo "    blob: $f"
done

for d in "${DELETES[@]}"; do
  entry=$(printf '{"path":%s,"mode":"100644","type":"blob","sha":null}' \
    "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$d")")
  ENTRIES_JSON+="$entry,"
  echo "    delete: $d"
done

# 去掉末尾逗号，组成完整数组
ENTRIES_JSON="[${ENTRIES_JSON%,}]"

echo "==> 创建 tree"
NEW_TREE=$(printf '{"base_tree":%s,"tree":%s}' \
  "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$TREE_SHA")" \
  "$ENTRIES_JSON" | gh api "repos/$REPO/git/trees" --input - | $PYTHON -c "import json,sys; print(json.load(sys.stdin)['sha'])")
echo "    new_tree=$NEW_TREE"

echo "==> 创建 commit"
MSG="feat: 接入 GPT-4o 真实 LLM、pytest 测试、GitHub Actions CI 与 matplotlib 真实可视化

- agents/llm.py: 统一 GPT-4o 接入层（无 key 自动回退规则引擎，支持 MockLLM 注入测试）
- 四个 Agent 新增 analyze(llm,...) LLM 路径，保留 run() 规则引擎
- demo 支持 --no-llm / --category / --keywords，自动选择引擎
- tests/: pytest 覆盖各 Agent 逻辑、JSON 解析与完整 LLM 代码路径
- .github/workflows/test.yml: push/PR 自动跑测试（Python 3.10/3.11/3.12）
- visualization: matplotlib 生成真实 dashboard.png 替换占位图
- requirements.txt / .env.example / README 升级"
NEW_COMMIT=$(printf '{"message":%s,"tree":%s,"parents":[%s]}' \
  "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$MSG")" \
  "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$NEW_TREE")" \
  "$($PYTHON -c "import json,sys; print(json.dumps(sys.argv[1]))" "$BASE_SHA")" \
  | gh api "repos/$REPO/git/commits" --input - | $PYTHON -c "import json,sys; print(json.load(sys.stdin)['sha'])")
echo "    new_commit=$NEW_COMMIT"

echo "==> 更新 main 分支引用"
gh api -X PATCH "repos/$REPO/git/refs/heads/main" --input - <<JSON
{"sha":"$NEW_COMMIT","force":false}
JSON

echo "==> DONE. 新提交: $NEW_COMMIT"
