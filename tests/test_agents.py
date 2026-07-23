"""各 Agent 规则引擎（离线可跑）逻辑的单元测试。

这些测试不依赖网络或 API key，保证核心逻辑稳定可回归。
"""
import math

from agents.trend_agent import TrendAgent
from agents.consumer_agent import ConsumerAgent
from agents.design_agent import DesignAgent
from agents.prediction_agent import PredictionAgent


def test_trend_agent_run_known_category():
    agent = TrendAgent()
    signals = agent.run("生活家居")
    assert 1 <= len(signals) <= 10
    for s in signals:
        assert 0 <= s.score <= 100
        assert s.growth >= 0
        assert isinstance(s.keyword, str) and s.keyword


def test_trend_agent_run_unknown_category_fallback():
    agent = TrendAgent()
    signals = agent.run("不存在的品类")
    # 未知类目回退到默认种子
    assert len(signals) == 3
    assert all(s.score >= 50 for s in signals)


def test_trend_agent_run_is_deterministic():
    a = TrendAgent().run("生活家居")
    b = TrendAgent().run("生活家居")
    assert [s.keyword for s in a] == [s.keyword for s in b]


def test_trend_agent_to_dict():
    agent = TrendAgent()
    d = agent.to_dict(agent.run("生活家居"))
    assert isinstance(d, list) and isinstance(d[0], dict)
    assert set(["keyword", "score", "growth", "platform"]).issubset(d[0].keys())


def test_consumer_agent_run_maps_emotion():
    agent = ConsumerAgent()
    insights = agent.run("18-25", "女性", ["治愈", "东方", "年轻化"])
    assert len(insights) == 3
    # 已知关键词应命中情绪映射
    assert "治愈" in insights[0].emotion or "内心平静" in insights[0].emotion
    # 未知关键词应安全回退
    unknown = agent.run("18-25", "女性", ["量子纠缠"])
    assert "量子纠缠" in unknown[0].segment


def test_design_agent_run_dedup_and_valid():
    agent = DesignAgent()
    out = agent.run(["东方", "治愈", "年轻化"], "香氛盲盒")
    # 设计元素去重后仍为列表
    assert isinstance(out.element, str) and len(out.element) > 0
    assert 0 < len(out.color_palette) <= 4
    assert all(c.startswith("#") for c in out.color_palette)
    assert out.material
    assert out.prompt


def test_design_agent_run_unknown_keyword():
    agent = DesignAgent()
    out = agent.run(["不存在基因"], "杯子")
    assert out.element  # 回退到默认 "极简设计"
    assert out.color_palette == ["#FFFFFF", "#000000"]


def test_prediction_agent_run_high_score_tier():
    agent = PredictionAgent()
    # 全部满分趋势 + 有用户洞察 → 高概率档
    trend = [{"keyword": "x", "score": 100}, {"keyword": "y", "score": 100}]
    result = agent.run(trend, ["insight"], None)
    assert 0.8 <= result.hit_probability <= 1.0
    assert result.confidence == "高"
    assert "10-30" in result.expected_sales
    assert "强烈建议" in result.recommendation


def test_prediction_agent_run_low_score_tier():
    agent = PredictionAgent()
    # 极低趋势分 + 无用户洞察 → 低概率档
    trend = [{"keyword": "x", "score": 10}]
    result = agent.run(trend, [], None)
    assert result.hit_probability < 0.6
    assert result.confidence == "低"
    assert "谨慎立项" in result.recommendation


def test_prediction_agent_run_risk_logic():
    agent = PredictionAgent()
    # 趋势分高但存在下行（<70）触发风险
    trend = [{"keyword": "x", "score": 50}]
    result = agent.run(trend, ["insight"], None)
    assert any("下行" in r for r in result.risk_factors)


def test_prediction_agent_to_dict_roundtrip():
    agent = PredictionAgent()
    result = agent.run([{"keyword": "x", "score": 90}], ["i"], None)
    d = agent.to_dict(result)
    assert set(
        ["hit_probability", "expected_sales", "risk_factors", "confidence", "recommendation"]
    ).issubset(d.keys())
    assert isinstance(d["risk_factors"], list)
