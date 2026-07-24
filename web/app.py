"""
MINISO AI Product Genome - Web 可视化界面

运行方式：
    cd <repo 根目录>
    pip install flask
    python web/app.py
然后浏览器打开 http://127.0.0.1:5000

界面会调用 demo.product_generation_demo.generate_product_report 跑完整 pipeline，
默认走本地规则引擎（无需 API key）；若要接 GPT-4o 可在表单里取消勾选"仅用规则引擎"
并提前配置好 OPENAI_API_KEY 环境变量。
"""

import os
import sys
import json

# 把仓库根目录加入 path，确保能 import demo / agents
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, request, render_template

from demo.product_generation_demo import generate_product_report
from agents.llm import LLMClient

app = Flask(__name__, template_folder="templates")

CATEGORIES = ["生活家居", "饰品", "美妆", "文具"]


def _parse_keywords(raw):
    """把表单里的关键词统一成列表：支持多值 / 逗号 / 空格分隔。"""
    if isinstance(raw, (list, tuple)):
        items = []
        for r in raw:
            items.extend(x.strip() for x in str(r).replace(",", " ").split() if x.strip())
        return items
    if isinstance(raw, str):
        return [x.strip() for x in raw.replace(",", " ").split() if x.strip()]
    return []


@app.route("/", methods=["GET"])
def index():
    last = None
    last_path = os.path.join(ROOT, "demo", "last_report.json")
    if os.path.exists(last_path):
        try:
            with open(last_path, encoding="utf-8") as f:
                last = json.load(f)
        except Exception:
            last = None
    return render_template("index.html", categories=CATEGORIES, last=last)


@app.route("/report", methods=["POST"])
def report():
    category = request.form.get("category", "生活家居")
    keywords = _parse_keywords(request.form.getlist("keywords") or request.form.get("keywords", ""))
    target_user = request.form.get("target_user", "18-25岁女性")
    price = request.form.get("price", "30-100元")
    no_llm = request.form.get("no_llm") == "on"
    if not keywords:
        keywords = ["治愈", "东方", "年轻化"]

    llm = None if no_llm else LLMClient()
    rep = generate_product_report(
        target_user=target_user,
        category=category,
        price_range=price,
        keywords=keywords,
        llm=llm,
    )
    return render_template("report.html", report=rep, categories=CATEGORIES)


@app.route("/sample")
def sample():
    """无需填表，直接渲染一份固定样例报告（新春 + 故宫联名款）。"""
    rep = generate_product_report(
        target_user="18-25岁女性",
        category="生活家居",
        price_range="30-100元",
        keywords=["新春", "故宫", "香氛"],
        llm=None,
    )
    return render_template("report.html", report=rep, categories=CATEGORIES)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
