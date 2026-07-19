"""
MINISO AI Product Genome - 端到端 Demo
输入用户需求，跑 4 个 Agent，输出产品决策报告
"""

import sys
import os
import json

# 把父目录加进 path，让 agents 包可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trend_agent import TrendAgent
from agents.consumer_agent import ConsumerAgent
from agents.design_agent import DesignAgent
from agents.prediction_agent import PredictionAgent


def generate_product_report(target_user: str, category: str, price_range: str, keywords: list) -> dict:
    """生成产品决策报告"""

    print("\n" + "=" * 60)
    print("  MINISO AI Product Genome · 决策报告生成中")
    print("=" * 60)
    print(f"  目标用户: {target_user}")
    print(f"  品类: {category}")
    print(f"  价格: {price_range}")
    print(f"  关键词: {', '.join(keywords)}")
    print("=" * 60)

    # 1. 跑 4 个 Agent
    trend_agent = TrendAgent()
    consumer_agent = ConsumerAgent()
    design_agent = DesignAgent()
    prediction_agent = PredictionAgent()

    print("\n[1/4] Trend Agent 分析趋势...")
    trend_signals = trend_agent.run(category)
    for s in trend_signals[:5]:
        print(f"  -  {s.keyword:12s} 热度 {s.score:.0f}  +{s.growth:.0f}%")

    print("\n[2/4] Consumer Agent 解析用户...")
    # 把年龄段从 "18-25岁女性" 拆出来
    age = "".join([c for c in target_user if c.isdigit() or c == "-"]) or "18-25"
    gender = "女" if "女" in target_user else "不限"
    consumer_insights = consumer_agent.run(age, gender, keywords)
    for r in consumer_insights[:3]:
        print(f"  -  {r.segment}: {r.emotion}")

    print("\n[3/4] Design Agent 生成设计...")
    design_output = design_agent.run(keywords, category)
    print(f"  -  元素: {design_output.element}")
    print(f"  -  配色: {' / '.join(design_output.color_palette[:3])}")
    print(f"  -  材料: {design_output.material}")

    print("\n[4/4] Prediction Agent 预测爆款概率...")
    prediction = prediction_agent.run(
        trend_agent.to_dict(trend_signals),
        consumer_agent.to_dict(consumer_insights),
        design_output
    )
    print(f"  -  爆款概率: {prediction.hit_probability*100:.0f}%")
    print(f"  -  预期销量: {prediction.expected_sales}")
    print(f"  -  建议: {prediction.recommendation}")

    # 2. 组装报告
    top_trend = trend_signals[0].keyword if trend_signals else "新趋势"
    top_keyword = keywords[0] if keywords else "治愈"

    product_name = f"「{top_trend}{top_keyword}香氛盲盒」" if category == "生活家居" else f"「{top_trend}{top_keyword}系列」"

    report = {
        "product_name": product_name,
        "market_insight": f"年轻消费者关注{keywords[0]}价值，{top_trend}类目搜索量持续增长",
        "design": design_agent.to_dict(design_output),
        "consumer": consumer_agent.to_dict(consumer_insights[:2]),
        "trend": trend_agent.to_dict(trend_signals[:5]),
        "prediction": prediction_agent.to_dict(prediction),
        "marketing_theme": f"「把{top_trend}带回房间」",
        "next_step": prediction.recommendation
    }

    return report


def main():
    # 用户输入
    target_user = "18-25岁女性"
    category = "生活家居"
    price_range = "30-100元"
    keywords = ["治愈", "东方", "年轻化"]

    report = generate_product_report(target_user, category, price_range, keywords)

    # 输出报告
    print("\n" + "=" * 60)
    print("  [产品决策报告]")
    print("=" * 60)
    print(f"\n  【产品名称】{report['product_name']}")
    print(f"\n  【市场洞察】{report['market_insight']}")
    print(f"\n  【设计元素】{report['design']['element']}")
    print(f"  【配色】{' / '.join(report['design']['color_palette'][:4])}")
    print(f"  【建议材料】{report['design']['material']}")
    print(f"\n  【营销主题】{report['marketing_theme']}")
    print(f"\n  【爆款预测】{report['prediction']['hit_probability']*100:.0f}%")
    print(f"  【预期销量】{report['prediction']['expected_sales']}")
    print(f"\n  【下一步】{report['next_step']}")
    print("\n" + "=" * 60)

    # 顺便把报告写到本地
    out_path = os.path.join(os.path.dirname(__file__), "last_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  报告已保存: {out_path}")


if __name__ == "__main__":
    main()
