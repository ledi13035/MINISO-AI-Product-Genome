"""
Prediction Agent - 预测智能体
职责：综合各 Agent 信号预测爆款概率
"""

from dataclasses import dataclass, asdict
from typing import List

try:
    from .llm import extract_json
except ImportError:  # pragma: no cover
    from agents.llm import extract_json


@dataclass
class PredictionResult:
    hit_probability: float      # 爆款概率 0-1
    expected_sales: str         # 预期销量区间
    risk_factors: List[str]     # 风险点
    confidence: str             # 置信度
    recommendation: str         # 建议


class PredictionAgent:
    """预测智能体 - 模拟版（生产环境用 XGBoost 训练）"""

    def __init__(self):
        # 各因素权重（生产环境由模型学习得到）
        self.weights = {
            "trend_score": 0.30,
            "consumer_match": 0.25,
            "design_uniqueness": 0.20,
            "price_competitiveness": 0.15,
            "season_fit": 0.10,
        }

    def run(self, trend_signals: list, consumer_insights: list, design_output) -> PredictionResult:
        """综合评分"""
        # 简化版评分：基于 trend signal 平均分
        if trend_signals:
            trend_score = sum(s.get("score", 70) if isinstance(s, dict) else s.score
                              for s in trend_signals) / len(trend_signals)
        else:
            trend_score = 70

        # 各因素打分（mock）
        scores = {
            "trend_score": trend_score,
            "consumer_match": 88 if consumer_insights else 75,
            "design_uniqueness": 82,
            "price_competitiveness": 90,
            "season_fit": 78,
        }

        # 加权
        hit_prob = sum(scores[k] * self.weights[k] for k in scores) / 100

        # 风险点
        risks = []
        if hit_prob < 0.6:
            risks.append("文化基因匹配度需要加强")
        if trend_score < 70:
            risks.append("趋势热度处于下行通道")
        if not risks:
            risks = ["同质化竞争", "季节性窗口期短"]

        # 预期销量
        if hit_prob >= 0.8:
            expected = "10-30 万件 / 季度"
            confidence = "高"
            rec = "强烈建议立项，优先进入开发流程"
        elif hit_prob >= 0.6:
            expected = "3-10 万件 / 季度"
            confidence = "中"
            rec = "建议立项，可小批量试产"
        else:
            expected = "1-3 万件 / 季度"
            confidence = "低"
            rec = "谨慎立项，建议调整设计后再评估"

        return PredictionResult(
            hit_probability=round(hit_prob, 2),
            expected_sales=expected,
            risk_factors=risks,
            confidence=confidence,
            recommendation=rec
        )

    def to_dict(self, result: PredictionResult) -> dict:
        return asdict(result)

    def analyze(
        self, llm, trend_signals: list, consumer_insights: list, design_output
    ) -> PredictionResult:
        """先由透明加权模型得出数值，再用 GPT-4o 生成更有洞察的定性结论。

        数值（爆款概率、预期销量、置信度）保持确定性、可解释、可测试；
        定性部分（风险提示、立项建议、营销主题）交由 LLM 润色。
        """
        base = self.run(trend_signals, consumer_insights, design_output)

        system = (
            "你是名创优品(MINISO)的选品决策顾问，擅长用商业语言给出立项建议。"
            "你必须只返回 JSON，不要解释。格式："
            '{"risk_factors":["风险1","风险2"],"recommendation":"一句话立项建议"}'
        )
        signals_desc = "; ".join(
            f"{s.get('keyword', '趋势')}(热度{s.get('score', 70)})"
            if isinstance(s, dict)
            else f"{getattr(s, 'keyword', '趋势')}(热度{getattr(s, 'score', 70)})"
            for s in trend_signals[:3]
        )
        user = (
            f"当前爆款概率 {base.hit_probability * 100:.0f}%，置信度 {base.confidence}。"
            f"趋势信号：{signals_desc}。请输出风险提示与立项建议。"
        )
        try:
            raw = llm.complete(system, user)
            data = extract_json(raw) or {}
        except Exception:
            data = {}

        risk = [str(r) for r in data.get("risk_factors", [])] or base.risk_factors
        rec = str(data.get("recommendation", base.recommendation))
        return PredictionResult(
            hit_probability=base.hit_probability,
            expected_sales=base.expected_sales,
            risk_factors=risk,
            confidence=base.confidence,
            recommendation=rec,
        )


if __name__ == "__main__":
    agent = PredictionAgent()
    result = agent.run([{"score": 92}, {"score": 85}], ["insight1"], None)
    print("=== Prediction Agent 输出 ===")
    print(f"  爆款概率：{result.hit_probability*100:.0f}%")
    print(f"  预期销量：{result.expected_sales}")
    print(f"  置信度：{result.confidence}")
    print(f"  建议：{result.recommendation}")
