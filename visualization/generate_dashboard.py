"""
生成决策报告可视化图表（真实 matplotlib 图表，替换原 placeholder）。

运行：
    python visualization/generate_dashboard.py
输出：
    visualization/dashboard.png

该脚本完全离线可跑，读取 dataset/ 下的样例数据，绘制：
  1) 各趋势关键词热度 Top（柱状）
  2) 各品类平均环比增速（柱状）
  3) 文化基因库四大类目趋势分（柱状）
  4) 基于样例数据的爆款概率仪表盘（环形）
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")  # 无头环境必须使用非交互后端
import matplotlib.pyplot as plt

# 让中文标签正常显示（按可用字体依次回退）
for _cand in ["Microsoft YaHei", "SimHei", "Noto Sans SC", "WenQuanYi Zen Hei", "PingFang SC"]:
    try:
        import matplotlib.font_manager as _fm

        _fm.findfont(_cand, fallback_to_default=False)
        plt.rcParams["font.sans-serif"] = [_cand]
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

# 让脚本可直接运行也能导入 agents 包
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

from agents.prediction_agent import PredictionAgent
from agents.trend_agent import TrendAgent

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "dataset")

# MINISO 品牌色
MINISO_RED = "#E60012"
ACCENT = "#FFB800"
INK = "#2B2B2B"


def load_trend_df():
    csv_path = os.path.join(DATA, "trend_sample.csv")
    if pd is None:
        # 极简 CSV 解析兜底（避免强依赖 pandas）
        import csv

        with open(csv_path, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    return pd.read_csv(csv_path)


def fig_trend_heat(df):
    """趋势关键词热度 Top 10（柱状图）。"""
    if pd is not None:
        top = df.sort_values("score", ascending=False).head(10)
        keywords = top["keyword"].tolist()[::-1]
        scores = top["score"].tolist()[::-1]
    else:
        rows = sorted(df, key=lambda r: float(r["score"]), reverse=True)[:10]
        rows = rows[::-1]
        keywords = [r["keyword"] for r in rows]
        scores = [float(r["score"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(keywords, scores, color=MINISO_RED)
    ax.set_title("趋势关键词热度 Top 10", fontsize=12, color=INK)
    ax.set_xlabel("热度评分")
    ax.set_xlim(0, 100)
    for i, v in enumerate(scores):
        ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=8, color=INK)
    fig.tight_layout()
    return fig


def fig_growth_by_category(df):
    """各品类平均环比增速（柱状图）。"""
    if pd is not None:
        g = df.groupby("category")["growth_pct"].mean().sort_values(ascending=False)
        cats = g.index.tolist()
        vals = g.values.tolist()
    else:
        from collections import defaultdict

        tmp = defaultdict(list)
        for r in df:
            tmp[r["category"]].append(float(r["growth_pct"]))
        cats = sorted(tmp, key=lambda c: -sum(tmp[c]) / len(tmp[c]))
        vals = [sum(tmp[c]) / len(tmp[c]) for c in cats]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(cats, vals, color=ACCENT)
    ax.set_title("各品类平均环比增速", fontsize=12, color=INK)
    ax.set_ylabel("环比增速 %")
    ax.tick_params(axis="x", rotation=20)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", fontsize=8, color=INK)
    fig.tight_layout()
    return fig


def fig_genome_scores():
    """文化基因库四大类目趋势分（柱状图）。"""
    import json

    with open(os.path.join(DATA, "product_features.json"), encoding="utf-8") as f:
        feat = json.load(f)

    cats, scores = [], []
    for cat, items in feat["cultural_genome"].items():
        avg = sum(i.get("trend_score", 0) for i in items) / max(len(items), 1)
        cats.append(cat)
        scores.append(avg)

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(cats, scores, color=MINISO_RED)
    ax.set_title("文化基因库 · 类目趋势分", fontsize=12, color=INK)
    ax.set_ylabel("平均趋势分")
    ax.set_ylim(0, 100)
    ax.tick_params(axis="x", rotation=15)
    for b, v in zip(bars, scores):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.0f}", ha="center", fontsize=8, color=INK)
    fig.tight_layout()
    return fig


def fig_prediction_gauge():
    """基于样例数据生成爆款概率仪表盘（环形图）。"""
    trends = TrendAgent().run("生活家居")
    signals = TrendAgent().to_dict(trends)
    pred = PredictionAgent().run(signals, ["治愈系洞察"], None)
    prob = pred.hit_probability  # 0-1

    fig, ax = plt.subplots(figsize=(6, 4))
    remain = max(1.0 - prob, 0.0)
    ax.pie(
        [prob, remain],
        colors=[MINISO_RED, "#EDEDED"],
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.32),
    )
    ax.text(0, 0, f"{prob * 100:.0f}%", ha="center", va="center", fontsize=26, color=INK, weight="bold")
    ax.text(0, -0.28, "预测爆款概率", ha="center", va="center", fontsize=10, color=INK)
    ax.set_title(f"爆款概率预测 · 置信度 {pred.confidence}", fontsize=12, color=INK)
    fig.tight_layout()
    return fig


def main():
    df = load_trend_df()

    figs = [
        fig_trend_heat(df),
        fig_growth_by_category(df),
        fig_genome_scores(),
        fig_prediction_gauge(),
    ]

    out_path = os.path.join(HERE, "dashboard.png")
    # 2x2 拼图
    import matplotlib.image as mpimg

    # 直接逐张保存再拼接较繁琐，这里改为分别保存后合成大图
    tmp_paths = []
    for i, f in enumerate(figs):
        p = os.path.join(HERE, f"_tmp_{i}.png")
        f.savefig(p, dpi=110)
        plt.close(f)
        tmp_paths.append(p)

    images = [mpimg.imread(p) for p in tmp_paths]
    # 统一高度，2 列布局
    import numpy as np

    row1 = np.hstack([images[0], images[1]])
    row2 = np.hstack([images[2], images[3]])
    grid = np.vstack([row1, row2])

    # 用 imshow 写出拼图
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(grid)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)

    for p in tmp_paths:
        try:
            os.remove(p)
        except OSError:
            pass

    print(f"dashboard saved -> {out_path}")


if __name__ == "__main__":
    main()
