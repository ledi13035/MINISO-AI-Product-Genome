"""
Design Agent - 设计智能体
职责：调用文化基因库，生成产品设计语言
"""

from dataclasses import dataclass, asdict
from typing import List

try:
    from .llm import extract_json
except ImportError:  # pragma: no cover
    from agents.llm import extract_json


@dataclass
class DesignOutput:
    element: str          # 设计元素
    color_palette: List[str]   # 配色
    material: str         # 推荐材料
    form_factor: str      # 形态/造型
    prompt: str           # Stable Diffusion prompt


class DesignAgent:
    """设计智能体 - 模拟版"""

    def __init__(self):
        # 文化基因库简化版
        self.genome = {
            "东方": {
                "elements": ["宋代植物纹样", "萱草", "玉兰", "山水留白", "祥云"],
                "colors": ["#C8102E", "#FFD700", "#003366", "#F5E6D3", "#2C5F2D"],
                "materials": ["环保PET", "生物基大豆蜡", "可回收纸卡", "实木"],
            },
            "治愈": {
                "elements": ["圆润弧线", "奶油色", "植物", "云朵", "猫爪"],
                "colors": ["#FFE5D9", "#FFCAD4", "#F4ACB7", "#9D8189"],
                "materials": ["磨砂硅胶", "桃皮绒", "记忆棉"],
            },
            "年轻化": {
                "elements": ["极简线条", "几何", "撞色", "数字", "Y2K"],
                "colors": ["#FF6B9D", "#00C9A7", "#C3B1E1", "#FFD93D"],
                "materials": ["亚克力", "镜面金属", "彩色塑料"],
            },
        }

    def run(self, keywords: List[str], category: str) -> DesignOutput:
        """根据关键词生成设计建议"""
        elements, colors, materials = [], [], []
        for kw in keywords:
            if kw in self.genome:
                elements.extend(self.genome[kw]["elements"][:2])
                colors.extend(self.genome[kw]["colors"][:2])
                materials.extend(self.genome[kw]["materials"][:1])

        # 去重保持顺序
        elements = list(dict.fromkeys(elements))
        colors = list(dict.fromkeys(colors))
        materials = list(dict.fromkeys(materials))

        prompt = f"{', '.join(elements[:3])}, {category} design, {', '.join(colors[:3])}, minimalist, oriental aesthetic, healing vibe, product photography"

        return DesignOutput(
            element=" + ".join(elements[:3]) if elements else "极简设计",
            color_palette=colors[:4] if colors else ["#FFFFFF", "#000000"],
            material="、".join(materials[:2]) if materials else "环保材料",
            form_factor="圆润方形礼盒" if "盲盒" in str(elements) else "日常便携",
            prompt=prompt
        )

    def to_dict(self, output: DesignOutput) -> dict:
        return asdict(output)

    def analyze(self, llm, keywords: List[str], category: str) -> DesignOutput:
        """LLM 驱动的设计语言生成：让 GPT-4o 基于文化基因库重组设计元素。"""
        system = (
            "你是名创优品(MINISO)的设计总监，擅长把文化基因重组为可落地的产品设计语言。"
            "你必须只返回 JSON，不要解释。格式："
            '{"element":"设计元素描述","color_palette":["#RRGGBB",...],'
            '"material":"推荐材料","form_factor":"形态造型","prompt":"Stable Diffusion 提示词"}'
        )
        user = (
            f"品类：{category}；文化基因关键词：{', '.join(keywords)}。"
            f"请输出一套符合目标用户的设计方案。"
        )
        try:
            raw = llm.complete(system, user)
        except Exception:
            return self.run(keywords, category)

        data = extract_json(raw) or {}
        if not data:
            return self.run(keywords, category)
        return DesignOutput(
            element=str(data.get("element", "极简设计")),
            color_palette=[str(c) for c in data.get("color_palette", ["#FFFFFF", "#000000"])][:4],
            material=str(data.get("material", "环保材料")),
            form_factor=str(data.get("form_factor", "日常便携")),
            prompt=str(
                data.get(
                    "prompt",
                    f"{', '.join(keywords)}, {category}, minimalist, oriental aesthetic",
                )
            ),
        )


if __name__ == "__main__":
    agent = DesignAgent()
    result = agent.run(["东方", "治愈", "年轻化"], "香氛盲盒")
    print("=== Design Agent 输出 ===")
    print(f"  元素：{result.element}")
    print(f"  配色：{' / '.join(result.color_palette)}")
    print(f"  材料：{result.material}")
    print(f"  形态：{result.form_factor}")
    print(f"  SD Prompt: {result.prompt}")
