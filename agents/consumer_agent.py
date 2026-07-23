"""
Consumer Agent - 用户智能体
职责：解析目标用户画像与情绪需求
"""

from dataclasses import dataclass, asdict
from typing import List

try:
    from .llm import extract_json
except ImportError:  # pragma: no cover
    from agents.llm import extract_json


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

    def analyze(
        self, llm, target_age: str, gender: str, keywords: List[str]
    ) -> List[ConsumerInsight]:
        """LLM 驱动的用户洞察：让 GPT-4o 生成更有温度的情绪价值与痛点描述。"""
        system = (
            "你是名创优品(MINISO)的用户研究员，擅长把抽象关键词转译为真实用户洞察。"
            "你必须只返回 JSON，不要解释。格式："
            '{"insights":[{"segment":"人群标签","emotion":"核心情绪价值",'
            '"pain_point":"痛点","unmet_need":"未被满足的需求"}]}'
        )
        user = (
            f"目标人群：{target_age}{gender}；关键词：{', '.join(keywords)}。"
            f"请为这些关键词各生成一条用户洞察。"
        )
        try:
            raw = llm.complete(system, user)
        except Exception:
            return self.run(target_age, gender, keywords)

        data = extract_json(raw) or {}
        insights: List[ConsumerInsight] = []
        for item in data.get("insights", [])[: len(keywords)]:
            try:
                insights.append(
                    ConsumerInsight(
                        segment=str(item.get("segment", f"{target_age}{gender} · {keywords[0]}派")),
                        age=target_age,
                        emotion=str(item.get("emotion", f"关注{keywords[0]}的群体")),
                        pain_point=str(item.get("pain_point", "缺乏有美学设计感的产品")),
                        unmet_need=str(
                            item.get("unmet_need", f"兼具{keywords[0]}感+性价比+社交分享价值的产品")
                        ),
                    )
                )
            except (TypeError, ValueError):
                continue
        return insights or self.run(target_age, gender, keywords)


if __name__ == "__main__":
    agent = ConsumerAgent()
    result = agent.run("18-25岁", "女性", ["治愈", "东方", "年轻化"])
    print("=== Consumer Agent 输出 ===")
    for r in result:
        print(f"  -  人群：{r.segment}")
        print(f"    情绪：{r.emotion}")
        print(f"    痛点：{r.pain_point}")
