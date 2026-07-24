"""把 report.html 模板用一份真实报告渲染成独立静态 HTML，便于预览实际界面。"""
import sys, os

ROOT = r"D:/WorkBuddy/MINISO-AI-Product-Genome"
sys.path.insert(0, ROOT)

from flask import Flask
from demo.product_generation_demo import generate_product_report

app = Flask(__name__, template_folder=os.path.join(ROOT, "web", "templates"))
categories = ["生活家居", "饰品", "美妆", "文具"]

# 用「新春 + 故宫」限定款做样例，能展示季节/联名徽章
rep = generate_product_report(
    target_user="18-25岁女性",
    category="生活家居",
    price_range="30-100元",
    keywords=["新春", "故宫", "香氛"],
    llm=None,
)

html = app.jinja_env.get_template("report.html").render(report=rep, categories=categories)

out = os.path.join(ROOT, "web", "_preview_report.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("written:", out, "len:", len(html))
print("product_name:", rep["product_name"])
