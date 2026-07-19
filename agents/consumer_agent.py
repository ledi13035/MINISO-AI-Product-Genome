"""
Consumer Agent - 用户智能体
职责：解析目标用户画像与情绪需求
"""

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class ConsumerInsight:
    segment: str          # 人群标签
    age: str              # 年龄段
    emotion: str          # 核心情绪价值
    pain_point: str       # 痛点
    unmet_need: str       # 未被满足的需求


class ConsumerAgent:
    """用户智能体 - 模拟版"""

    def __init__(self):
        # 情绪价值映射表
        self.emotion_map = {
            "治愈": "寻求内心平静，渴望从快节奏中抽离",
            "解压": "工作/学习压力大，需要情绪出口",
            "亚比": "追求个性化表达，区别于主流",
            "Citywalk": "热爱城市探索，注重视觉与体验",
            "东方": "文化自信，对传统美学有亲近感",
            "年轻化": "自我认同，拒绝被定义",
        }

    def run(self, target_age: str, gender: str, keywords: List[str]) -> List[ConsumerInsight]:
        """根据输入输出用户洞察"""
        insights = []
        for kw in keywords:
            emotion = self.emotion_map.get(kw, f"关注{kw}的群体")
            insight = ConsumerInsight(
                segment=f"{target_age}{gender} · {kw}派",
                age=target_age,
                emotion=emotion,
                pain_point=f"在{emotion}的需求上，缺乏有美学设计感的产品",
                unmet_need=f"兼具{kw}感 + 性价比 + 社交分享价值的产品"
            )
            insights.append(insight)
        return insights

    def to_dict(self, insights: List[ConsumerInsight]) -> List[dict]:
        return [asdict(i) for i in insights]


if __name__ == "__main__":
    agent = ConsumerAgent()
    result = agent.run("18-25岁", "女性", ["治愈", "东方", "年轻化"])
    print("=== Consumer Agent 输出 ===")
    for r in result:
        print(f"  -  人群：{r.segment}")
        print(f"    情绪：{r.emotion}")
        print(f"    痛点：{r.pain_point}")
