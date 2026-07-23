"""LLM 接入层与 JSON 解析的单元测试。

验证：无 key 时安全回退、MockLLM 确定性、extract_json 鲁棒性、
以及各 Agent 的 LLM 代码路径可被 MockLLM 驱动。
"""
import json

from agents.llm import MockLLM, LLMClient, extract_json
from agents.trend_agent import TrendAgent
from agents.consumer_agent import ConsumerAgent
from agents.design_agent import DesignAgent
from agents.prediction_agent import PredictionAgent


def test_mock_llm_available_and_canned():
    m = MockLLM(canned='{"hello": "world"}')
    assert m.available is True
    assert json.loads(m.complete("s", "u"))["hello"] == "world"


def test_llmclient_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    client = LLMClient()
    assert client.available is False
    # 不可用时调用应明确报错，而非静默返回错误结果
    try:
        client.complete("s", "u")
        assert False, "应当抛出 RuntimeError"
    except RuntimeError:
        pass


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    text = "好的，结果如下：\n```json\n{\"a\": 1}\n```\n完毕"
    assert extract_json(text) == {"a": 1}


def test_extract_json_with_prefix_suffix():
    text = "以下是数据：{\"score\": 88} 仅供参考"
    assert extract_json(text) == {"score": 88}


def test_extract_json_invalid_returns_none():
    assert extract_json("这根本不是 json") is None
    assert extract_json(None) is None


def test_trend_agent_analyze_with_mockllm():
    canned = json.dumps(
        {"signals": [{"keyword": "国潮新中式", "score": 96, "growth": 200, "platform": "xiaohongshu"}]}
    )
    agent = TrendAgent()
    signals = agent.analyze(MockLLM(canned=canned), "生活家居")
    assert signals[0].keyword == "国潮新中式"
    assert signals[0].score == 96


def test_consumer_agent_analyze_with_mockllm():
    canned = json.dumps(
        {"insights": [{"segment": "Z世代女性", "emotion": "渴望平静", "pain_point": "缺设计", "unmet_need": "治愈+性价比"}]}
    )
    agent = ConsumerAgent()
    insights = agent.analyze(MockLLM(canned=canned), "18-25", "女性", ["治愈"])
    assert insights[0].emotion == "渴望平静"


def test_design_agent_analyze_with_mockllm():
    canned = json.dumps(
        {
            "element": "宋画植物纹样",
            "color_palette": ["#C8102E", "#F5E6D3"],
            "material": "环保PET",
            "form_factor": "圆角礼盒",
            "prompt": "song dynasty botanical",
        }
    )
    agent = DesignAgent()
    out = agent.analyze(MockLLM(canned=canned), ["东方"], "香氛盲盒")
    assert out.element == "宋画植物纹样"
    assert out.color_palette[0] == "#C8102E"


def test_prediction_agent_analyze_with_mockllm():
    canned = json.dumps({"risk_factors": ["同质化", "窗口期短"], "recommendation": "建议小批量试产"})
    agent = PredictionAgent()
    result = agent.analyze(
        MockLLM(canned=canned),
        [{"keyword": "x", "score": 92}],
        ["insight"],
        None,
    )
    assert result.risk_factors == ["同质化", "窗口期短"]
    assert "小批量试产" in result.recommendation
