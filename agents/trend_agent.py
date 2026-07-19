"""
Trend Agent - 趋势智能体
职责：实时感知市场趋势变化，输出趋势关键词与热度评分
"""

from dataclasses import dataclass, asdict
from typing import List


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


if __name__ == "__main__":
    agent = TrendAgent()
    result = agent.run("生活家居")
    print("=== Trend Agent 输出 ===")
    for s in result:
        print(f"  {s.keyword:12s}  热度 {s.score:.0f}  增速 +{s.growth:.0f}%")
