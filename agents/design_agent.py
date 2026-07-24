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
        # 类目默认设计语言（关键词未命中基因库时兜底，保证与品类强相关）
        self.category_design = {
            "饰品": {
                "colors": ["#D4AF37", "#F5E6D3", "#C0C0C0", "#B76E79"],
                "materials": ["合金镀金", "天然石", "925银"],
                "form": "日常佩戴",
            },
            "生活家居": {
                "colors": ["#2C5F2D", "#F5E6D3", "#C8102E", "#E8DCC4"],
                "materials": ["陶瓷", "实木", "环保PET"],
                "form": "桌面陈列",
            },
            "美妆": {
                "colors": ["#FFCAD4", "#F4ACB7", "#FFF0F5", "#C81571"],
                "materials": ["玻璃", "亚克力", "环保塑料"],
                "form": "随身补妆",
            },
            "文具": {
                "colors": ["#003366", "#FFD700", "#F5E6D3", "#9D8189"],
                "materials": ["环保纸", "再生纸", "PP"],
                "form": "桌面收纳",
            },
        }
        # 关键词启发式（覆盖基因库之外的常见词，如 新中式 / 蝴蝶）
        self.keyword_heuristics = {
            "新中式": {
                "elements": ["国风纹样", "留白构图", "水墨笔触"],
                "colors": ["#C8102E", "#003366", "#F5E6D3"],
            },
            "蝴蝶": {
                "elements": ["蝴蝶造型", "对称翅脉", "轻盈线条"],
                "colors": ["#FF6B9D", "#00C9A7", "#C3B1E1"],
            },
            "国潮": {
                "elements": ["国潮符号", "复古字体", "撞色块"],
                "colors": ["#C8102E", "#FFD700", "#003366"],
            },
            "植物": {
                "elements": ["植物轮廓", "叶片纹理", "自然曲线"],
                "colors": ["#2C5F2D", "#A3C9A8", "#E8DCC4"],
            },
            "香氛": {
                "elements": ["雾面瓶身", "柔光质感", "扩香纹理"],
                "colors": ["#F5E6D3", "#E8DCC4", "#C81571"],
            },
        }

    def run(self, keywords: List[str], category: str) -> DesignOutput:
        """根据关键词 + 品类生成一套协调的设计语言（规则引擎，离线可用）。"""
        elements, colors, materials = [], [], []
        for kw in keywords:
            if kw in self.genome:
                elements.extend(self.genome[kw]["elements"][:2])
                colors.extend(self.genome[kw]["colors"][:2])
                materials.extend(self.genome[kw]["materials"][:1])
            elif kw in self.keyword_heuristics:
                h = self.keyword_heuristics[kw]
                elements.extend(h.get("elements", [])[:2])
                colors.extend(h.get("colors", [])[:2])
            else:
                # 未知关键词：以其本身构造自然元素名，避免回退到笼统的"极简设计"
                elements.append(f"{kw}元素")

        # 类目兜底：保证配色/材料与品类强相关，且永不为空
        cat = self.category_design.get(category)
        if cat:
            if not colors:
                colors = list(cat["colors"])
            if not materials:
                materials = cat["materials"][:2]
            form_factor = cat["form"]
        else:
            if not colors:
                colors = ["#FFFFFF", "#000000"]
            if not materials:
                materials = ["环保材料"]
            form_factor = "日常便携"

        # 去重保持顺序
        elements = list(dict.fromkeys(elements)) or [f"{category}设计"]
        colors = list(dict.fromkeys(colors))
        materials = list(dict.fromkeys(materials))

        prompt = f"{', '.join(elements[:3])}, {category} design, {', '.join(colors[:3])}, minimalist, oriental aesthetic, healing vibe, product photography"

        return DesignOutput(
            element=" + ".join(elements[:3]),
            color_palette=colors[:4],
            material="、".join(materials[:2]),
            form_factor=form_factor,
            prompt=prompt,
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
