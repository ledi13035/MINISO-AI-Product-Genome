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
    season: str = ""      # 季节限定标识（如 圣诞/春日）
    cobrand: str = ""     # 联名款 IP 标识（如 迪士尼/故宫）
    note: str = ""        # 限定/联名说明


class DesignAgent:
    """设计智能体 - 模拟版（规则引擎离线可用，也可接 LLM）"""

    # 季节限定库：命中后叠加限定配色/元素，并把限定配色前置以保留辨识度
    SEASONS = {
        "圣诞": {
            "colors": ["#C8102E", "#0B6623", "#FFD700"],
            "elements": ["雪花纹样", "礼盒丝带", "麋鹿剪影"],
            "materials": ["绒布", "金属配件"],
            "note": "圣诞限定：红绿金配色 + 节日礼物语汇",
        },
        "新年": {
            "colors": ["#C8102E", "#FFD700", "#0B6623"],
            "elements": ["烟花", "灯笼", "金币"],
            "materials": ["红金工艺", "烫金纸"],
            "note": "新年限定：喜庆红金 + 纳福元素",
        },
        "新春": {
            "colors": ["#C8102E", "#FFD700", "#003366"],
            "elements": ["祥云", "灯笼", "牡丹"],
            "materials": ["红金工艺", "绒布"],
            "note": "新春限定：东方新春美学 + 国潮纹样",
        },
        "夏日": {
            "colors": ["#00C9A7", "#FFD93D", "#FF6B9D"],
            "elements": ["海浪", "水果切片", "冰系光泽"],
            "materials": ["透明亚克力", "磨砂硅胶"],
            "note": "夏日限定：清凉配色 + 海洋/水果元素",
        },
        "秋冬": {
            "colors": ["#8B4513", "#C0392B", "#E8DCC4"],
            "elements": ["落叶", "毛绒", "暖光"],
            "materials": ["针织", "绒面"],
            "note": "秋冬限定：暖色调 + 毛绒/针织质感",
        },
        "春日": {
            "colors": ["#FFCAD4", "#A3C9A8", "#F5E6D3"],
            "elements": ["樱花", "新芽", "蝴蝶"],
            "materials": ["陶瓷", "再生纸"],
            "note": "春日限定：柔粉嫩绿 + 花卉元素",
        },
    }
    # 关键词 → 季节 触发词（大小写不敏感）
    SEASON_TRIGGERS = {
        "圣诞": ["圣诞", "圣诞节", "christmas"],
        "新年": ["新年", "元旦"],
        "新春": ["春节", "新春", "过年", "福", "本命年"],
        "夏日": ["夏日", "夏季", "夏天", "清凉", "海洋", "西瓜"],
        "秋冬": ["秋冬", "秋季", "秋天", "冬天", "暖冬", "毛绒"],
        "春日": ["春日", "春季", "春天", "樱花", "踏青"],
    }

    # 联名款库：命中知名 IP 后叠加联名设计语言
    COBRANDS = {
        "迪士尼": {
            "colors": ["#113CCF", "#E4002B", "#FFFFFF"],
            "elements": ["米奇轮廓", "童话符号", "经典红黑"],
            "materials": ["搪胶", "毛绒"],
            "note": "迪士尼联名：经典卡通 IP，强辨识度与童趣感",
        },
        "三丽鸥": {
            "colors": ["#FFB6C1", "#FFF0F5", "#C81571"],
            "elements": ["Hello Kitty", "玉桂狗", "星之卡比"],
            "materials": ["毛绒", "亚克力"],
            "note": "三丽鸥联名：甜美可爱风，少女心定位",
        },
        "故宫": {
            "colors": ["#C8102E", "#003366", "#FFD700"],
            "elements": ["故宫纹样", "千里江山", "缠枝纹"],
            "materials": ["丝绸", "金属"],
            "note": "故宫联名：东方美学，文化厚度与收藏感",
        },
        "泡泡玛特": {
            "colors": ["#FF6B9D", "#00C9A7", "#C3B1E1"],
            "elements": ["盲盒公仔", "Molly", "Dimoo"],
            "materials": ["PVC", "搪胶"],
            "note": "泡泡玛特联名：潮玩盲盒基因，收藏驱动",
        },
        "line friends": {
            "colors": ["#FFFFFF", "#8B5A2B", "#FF6B9D"],
            "elements": ["布朗熊", "可妮兔", "莎莉鸡"],
            "materials": ["毛绒", "陶瓷"],
            "note": "LINE FRIENDS 联名：日常萌系，社交属性强",
        },
    }

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

    # ------------------------------------------------------------------ #
    # 限定身份识别（季节 / 联名），规则引擎与 LLM 路径共用，保证结构一致
    # ------------------------------------------------------------------ #
    def _detect_season(self, keywords: List[str]) -> str:
        text = " ".join(keywords).lower()
        for season, triggers in self.SEASON_TRIGGERS.items():
            for t in triggers:
                if t.lower() in text:
                    return season
        return ""

    def _detect_cobrand(self, keywords: List[str]) -> str:
        text = " ".join(keywords).lower()
        for brand in self.COBRANDS:
            if brand.lower() in text:
                return brand
        return ""

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

        # 季节限定 + 联名款：叠加限定设计语言，并把限定配色前置以保留辨识度
        season = self._detect_season(keywords)
        cobrand = self._detect_cobrand(keywords)
        notes = []
        if season:
            s = self.SEASONS[season]
            elements.extend(s["elements"][:2])
            materials.extend(s["materials"][:1])
            colors = s["colors"] + colors
            notes.append(s["note"])
        if cobrand:
            c = self.COBRANDS[cobrand]
            elements.extend(c["elements"][:2])
            materials.extend(c["materials"][:1])
            colors = c["colors"] + colors
            notes.append(c["note"])

        # 去重保持顺序
        elements = list(dict.fromkeys(elements)) or [f"{category}设计"]
        colors = list(dict.fromkeys(colors))
        materials = list(dict.fromkeys(materials))

        prompt = (
            f"{', '.join(elements[:3])}, {category} design, {', '.join(colors[:3])}, "
            f"limited edition, oriental aesthetic, healing vibe, product photography"
        )

        return DesignOutput(
            element=" + ".join(elements[:3]),
            color_palette=colors[:5],
            material="、".join(materials[:3]),
            form_factor=form_factor,
            prompt=prompt,
            season=season,
            cobrand=cobrand,
            note="；".join(notes),
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

        # 限定身份（季节/联名）由规则引擎统一判定，保证报告结构一致
        season = self._detect_season(keywords)
        cobrand = self._detect_cobrand(keywords)
        notes = []
        if season:
            notes.append(self.SEASONS[season]["note"])
        if cobrand:
            notes.append(self.COBRANDS[cobrand]["note"])

        return DesignOutput(
            element=str(data.get("element", "极简设计")),
            color_palette=[str(c) for c in data.get("color_palette", ["#FFFFFF", "#000000"])][:5],
            material=str(data.get("material", "环保材料")),
            form_factor=str(data.get("form_factor", "日常便携")),
            prompt=str(
                data.get(
                    "prompt",
                    f"{', '.join(keywords)}, {category}, minimalist, oriental aesthetic",
                )
            ),
            season=season,
            cobrand=cobrand,
            note="；".join(notes),
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
