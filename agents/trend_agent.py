"""
Trend Agent - 趋势智能体
职责：实时感知市场趋势变化，输出趋势关键词与热度评分
"""

from dataclasses import dataclass, asdict
from typing import List

try:  # 作为包导入时使用相对导入，作为脚本直接运行时回退到绝对导入
    from .llm import extract_json
except ImportError:  # pragma: no cover
    from agents.llm import extract_json


@dataclass
class TrendSignal:
    keyword: str          # 趋势关键词
    score: float          # 热度评分 0-100
    growth: float         # 环比增速 %
    platform: str         # 来源平台


class TrendAgent:
    """趋势智能体 - 模拟版（生产环境接入淘宝/小红书/抖音 API）"""

    def __init__(self):
        # 模拟文化基因库的趋势种子
        self.cultural_genome_seeds = {
            "生活家居": ["新中式", "植物香氛", "情绪疗愈", "盲盒", "东方植物", "宋代美学"],
            "美妆": ["纯欲妆", "亚比风", "清冷感", "甜妹妆"],
            "饰品": ["新中式首饰", "蝴蝶元素", "串珠", "锁骨链"],
            "文具": ["手帐", "国风", "解压文具", "治愈系"],
        }

    def run(self, category: str, platform: str = "xiaohongshu", top_k: int = 10) -> List[TrendSignal]:
        """执行趋势分析"""
        base_keywords = self.cultural_genome_seeds.get(category, ["新趋势", "情绪价值", "国潮"])

        # 模拟趋势评分：基于关键词在种子库的位置给一个递增分数
        signals = []
        for i, kw in enumerate(base_keywords[:top_k]):
            score = 95 - i * 7  # 衰减评分
            growth = 180 - i * 18  # 模拟增速
            signals.append(TrendSignal(
                keyword=kw,
                score=max(score, 50),
                growth=max(growth, 20),
                platform=platform
            ))
        return signals

    def to_dict(self, signals: List[TrendSignal]) -> List[dict]:
        return [asdict(s) for s in signals]

    def analyze(
        self, llm, category: str, platform: str = "xiaohongshu", top_k: int = 10
    ) -> List[TrendSignal]:
        """LLM 驱动的趋势分析：让 GPT-4o 基于类目真实研判趋势信号。

        若 LLM 返回无法解析或为空，则安全回退到规则引擎 :meth:`run`，保证可用性。
        """
        system = (
            "你是名创优品(MINISO)的趋势分析师，擅长从社媒与电商信号中提炼消费趋势。"
            "你必须只返回 JSON，不要任何解释文字。格式为："
            '{"signals":[{"keyword":"趋势词","score":0到100,"growth":0到300,'
            '"platform":"来源平台"}]}'
        )
        user = (
            f"请分析「{category}」品类在「{platform}」等平台的最新消费趋势，"
            f"输出 top {top_k} 个趋势信号。score 为热度(0-100)，"
            f"growth 为近 90 天环比增速(%)。"
        )
        try:
            raw = llm.complete(system, user)
        except Exception:
            return self.run(category, platform, top_k)

        data = extract_json(raw) or {}
        signals: List[TrendSignal] = []
        for item in data.get("signals", [])[:top_k]:
            try:
                signals.append(
                    TrendSignal(
                        keyword=str(item.get("keyword", "新趋势")),
                        score=float(item.get("score", 70)),
                        growth=float(item.get("growth", 50)),
                        platform=str(item.get("platform", platform)),
                    )
                )
            except (TypeError, ValueError):
                continue
        return signals or self.run(category, platform, top_k)


if __name__ == "__main__":
    agent = TrendAgent()
    result = agent.run("生活家居")
    print("=== Trend Agent 输出 ===")
    for s in result:
        print(f"  {s.keyword:12s}  热度 {s.score:.0f}  增速 +{s.growth:.0f}%")
