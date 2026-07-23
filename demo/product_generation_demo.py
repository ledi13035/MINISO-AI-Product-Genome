"""
MINISO AI Product Genome - 端到端 Demo
输入用户需求，跑 4 个 Agent，输出产品决策报告。

运行方式：
    # 无 API key：使用本地规则引擎（默认）
    python demo/product_generation_demo.py

    # 设置 OPENAI_API_KEY 后，自动切换为 GPT-4o 真实分析
    export OPENAI_API_KEY=sk-...
    python demo/product_generation_demo.py

    # 强制走规则引擎 / 指定参数
    python demo/product_generation_demo.py --no-llm --category 饰品 --keywords 新中式 蝴蝶
"""

import sys
import os
import json
import argparse

# 把父目录加进 path，让 agents 包可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trend_agent import TrendAgent
from agents.consumer_agent import ConsumerAgent
from agents.design_agent import DesignAgent
from agents.prediction_agent import PredictionAgent
from agents.llm import LLMClient


def _parse_target_user(target_user: str):
    """从 '18-25岁女性' 这类字符串里拆出年龄与性别。"""
    age = "".join([c for c in target_user if c.isdigit() or c == "-"]) or "18-25"
    gender = "女" if "女" in target_user else ("男" if "男" in target_user else "不限")
    return age, gender


def generate_product_report(
    target_user: str,
    category: str,
    price_range: str,
    keywords: list,
    llm=None,
) -> dict:
    """生成产品决策报告。

    llm 为可选的大模型客户端；可用时各 Agent 走 LLM 真实分析路径，
    否则回退到本地规则引擎。返回结构稳定的报告字典，便于测试与下游消费。
    """
    use_llm = llm is not None and getattr(llm, "available", False)

    print("\n" + "=" * 60)
    print("  MINISO AI Product Genome · 决策报告生成中")
    print("=" * 60)
    print(f"  目标用户: {target_user}")
    print(f"  品类: {category}")
    print(f"  价格: {price_range}")
    print(f"  关键词: {', '.join(keywords)}")
    print(f"  引擎: {'GPT-4o (LLM)' if use_llm else '本地规则引擎'}")
    print("=" * 60)

    trend_agent = TrendAgent()
    consumer_agent = ConsumerAgent()
    design_agent = DesignAgent()
    prediction_agent = PredictionAgent()

    print("\n[1/4] Trend Agent 分析趋势...")
    if use_llm:
        trend_signals = trend_agent.analyze(llm, category)
    else:
        trend_signals = trend_agent.run(category)
    for s in trend_signals[:5]:
        print(f"  -  {s.keyword:12s} 热度 {s.score:.0f}  +{s.growth:.0f}%")

    print("\n[2/4] Consumer Agent 解析用户...")
    age, gender = _parse_target_user(target_user)
    if use_llm:
        consumer_insights = consumer_agent.analyze(llm, age, gender, keywords)
    else:
        consumer_insights = consumer_agent.run(age, gender, keywords)
    for r in consumer_insights[:3]:
        print(f"  -  {r.segment}: {r.emotion}")

    print("\n[3/4] Design Agent 生成设计...")
    if use_llm:
        design_output = design_agent.analyze(llm, keywords, category)
    else:
        design_output = design_agent.run(keywords, category)
    print(f"  -  元素: {design_output.element}")
    print(f"  -  配色: {' / '.join(design_output.color_palette[:3])}")
    print(f"  -  材料: {design_output.material}")

    print("\n[4/4] Prediction Agent 预测爆款概率...")
    if use_llm:
        prediction = prediction_agent.analyze(
            llm,
            trend_agent.to_dict(trend_signals),
            consumer_agent.to_dict(consumer_insights),
            design_output,
        )
    else:
        prediction = prediction_agent.run(
            trend_agent.to_dict(trend_signals),
            consumer_agent.to_dict(consumer_insights),
            design_output,
        )
    print(f"  -  爆款概率: {prediction.hit_probability * 100:.0f}%")
    print(f"  -  预期销量: {prediction.expected_sales}")
    print(f"  -  建议: {prediction.recommendation}")

    # 组装报告（结构稳定，与引擎无关）
    top_trend = trend_signals[0].keyword if trend_signals else "新趋势"
    top_keyword = keywords[0] if keywords else "治愈"

    product_name = (
        f"「{top_trend}{top_keyword}香氛盲盒」"
        if category == "生活家居"
        else f"「{top_trend}{top_keyword}系列」"
    )

    report = {
        "engine": "llm" if use_llm else "rule",
        "product_name": product_name,
        "market_insight": f"年轻消费者关注{keywords[0]}价值，{top_trend}类目搜索量持续增长",
        "design": design_agent.to_dict(design_output),
        "consumer": consumer_agent.to_dict(consumer_insights[:2]),
        "trend": trend_agent.to_dict(trend_signals[:5]),
        "prediction": prediction_agent.to_dict(prediction),
        "marketing_theme": f"「把{top_trend}带回房间」",
        "next_step": prediction.recommendation,
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="MINISO AI Product Genome Demo")
    parser.add_argument("--target-user", default="18-25岁女性", help="目标用户，如 '18-25岁女性'")
    parser.add_argument("--category", default="生活家居", help="品类，如 生活家居/饰品/美妆/文具")
    parser.add_argument("--price", default="30-100元", help="价格区间")
    parser.add_argument("--keywords", nargs="+", default=["治愈", "东方", "年轻化"], help="文化基因关键词")
    parser.add_argument("--no-llm", action="store_true", help="强制使用本地规则引擎（不调用 LLM）")
    args = parser.parse_args()

    llm = None if args.no_llm else LLMClient()

    report = generate_product_report(
        target_user=args.target_user,
        category=args.category,
        price_range=args.price,
        keywords=args.keywords,
        llm=llm,
    )

    print("\n" + "=" * 60)
    print("  [产品决策报告]")
    print("=" * 60)
    print(f"\n  【产品名称】{report['product_name']}")
    print(f"  【市场洞察】{report['market_insight']}")
    print(f"  【设计元素】{report['design']['element']}")
    print(f"  【配色】{' / '.join(report['design']['color_palette'][:4])}")
    print(f"  【建议材料】{report['design']['material']}")
    print(f"  【营销主题】{report['marketing_theme']}")
    print(f"  【爆款预测】{report['prediction']['hit_probability'] * 100:.0f}%")
    print(f"  【预期销量】{report['prediction']['expected_sales']}")
    print(f"  【下一步】{report['next_step']}")
    print("\n" + "=" * 60)

    out_path = os.path.join(os.path.dirname(__file__), "last_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  报告已保存: {out_path}")


if __name__ == "__main__":
    main()
