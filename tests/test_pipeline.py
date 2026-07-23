"""端到端流水线测试：generate_product_report 在规则引擎与 LLM 两条路径下都稳定。"""

import json

from demo.product_generation_demo import generate_product_report


class SmartMockLLM:
    """按 system 提示词返回对应 schema 的确定性 JSON，驱动完整 LLM 路径。"""

    available = True

    def complete(self, system: str, user: str) -> str:
        if "趋势分析师" in system:
            return json.dumps(
                {"signals": [{"keyword": "国潮新中式", "score": 96, "growth": 200, "platform": "xiaohongshu"}]}
            )
        if "用户研究员" in system:
            return json.dumps(
                {"insights": [{"segment": "Z世代女性·治愈派", "emotion": "渴望内心平静", "pain_point": "缺设计感", "unmet_need": "治愈+性价比"}]}
            )
        if "设计总监" in system:
            return json.dumps(
                {
                    "element": "宋画植物纹样",
                    "color_palette": ["#C8102E", "#F5E6D3"],
                    "material": "环保PET",
                    "form_factor": "圆角礼盒",
                    "prompt": "song dynasty botanical, minimalist",
                }
            )
        if "选品决策顾问" in system:
            return json.dumps({"risk_factors": ["同质化竞争", "窗口期短"], "recommendation": "建议小批量试产"})
        return json.dumps({"result": "mock"})


REQUIRED_KEYS = {
    "engine",
    "product_name",
    "market_insight",
    "design",
    "consumer",
    "trend",
    "prediction",
    "marketing_theme",
    "next_step",
}


def test_report_rule_engine():
    report = generate_product_report(
        target_user="18-25岁女性",
        category="生活家居",
        price_range="30-100元",
        keywords=["治愈", "东方", "年轻化"],
        llm=None,
    )
    assert REQUIRED_KEYS.issubset(report.keys())
    assert report["engine"] == "rule"
    assert 0 <= report["prediction"]["hit_probability"] <= 1
    assert report["product_name"]


def test_report_with_mock_llm():
    report = generate_product_report(
        target_user="18-25岁女性",
        category="生活家居",
        price_range="30-100元",
        keywords=["治愈", "东方", "年轻化"],
        llm=SmartMockLLM(),
    )
    assert report["engine"] == "llm"
    assert REQUIRED_KEYS.issubset(report.keys())
    # LLM 路径确实影响了各 Agent 输出
    assert report["trend"][0]["keyword"] == "国潮新中式"
    assert report["design"]["element"] == "宋画植物纹样"
    assert report["prediction"]["risk_factors"] == ["同质化竞争", "窗口期短"]
    assert "小批量试产" in report["next_step"]


def test_report_different_category():
    report = generate_product_report(
        target_user="18-25岁学生", category="饰品", price_range="20-80元",
        keywords=["新中式", "蝴蝶"], llm=None,
    )
    # 产品名由实际 top 趋势 + 首个关键词拼接，结构稳定即可
    assert report["product_name"].startswith("「") and "系列" in report["product_name"]
    assert "新中式" in report["product_name"]
    assert 0 <= report["prediction"]["hit_probability"] <= 1
