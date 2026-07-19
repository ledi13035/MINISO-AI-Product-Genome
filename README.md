# MINISO AI Product Genome

> AI 产品开发智能体架构 · 为名创优品类目打造的产品基因引擎

[![GitHub](https://img.shields.io/badge/GitHub-ledi13035%2FMINISO--AI--Product--Genome-blue)](https://github.com/ledi13035/MINISO-AI-Product-Genome)
[![Status](https://img.shields.io/badge/Status-Prototype-orange)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🎯 项目目标

名创优品（MINISO）每年需要快速响应潮流文化、IP 联名、东方美学、年轻消费情绪等多维信号，开发上千 SKU。传统"拍脑袋选品 + 调研"链路慢、成本高、容易错过窗口期。

**MINISO AI Product Genome** 是一套**多智能体协同的产品开发架构**，输入用户需求和品类，输出：
- 产品概念与命名
- 市场洞察与文化基因拆解
- 设计元素与材料建议
- 营销主题
- 爆款概率预测

让产品开发从"经验驱动"变成"**AI + 文化基因 + 数据**"驱动。

---

## 🧬 核心理念：AI Cultural Genome（文化基因库）

名创优品大量产品依赖四大文化基因：

| 基因类别 | 示例 |
| --- | --- |
| **IP / 潮流文化** | 迪士尼、Sanrio、Loopy、Chiikawa |
| **东方元素** | 故宫纹样、敦煌壁画、宋画意境、节气 |
| **情绪消费** | 治愈、解压、陪伴、亚比风、Citywalk |
| **年轻网络文化** | B站梗、抖音爆款、小红书趋势、二次元 |

**AI 拆解文化基因 → 重组生成符合目标用户的新产品语言。**

---

## 🏗️ 系统架构

```
                        用户需求
                (目标用户 / 品类 / 价格 / 关键词)
                            ↓
            ┌───────────────────────────────┐
            │   MINISO AI Product Genome     │
            │      (产品基因引擎)             │
            └───────────────┬───────────────┘
                            ↓
        ┌──────────┬──────────┬──────────┬──────────┐
        │ Trend    │ Consumer │ Design   │Prediction│
        │ Agent    │ Agent    │ Agent    │ Agent    │
        │ 趋势智能体│ 用户智能体│ 设计智能体│ 预测智能体│
        └────┬─────┴────┬─────┴────┬─────┴────┬─────┘
             │          │          │          │
             └──────────┴──────────┴──────────┘
                            ↓
                    产品决策报告
            (名称 / 洞察 / 设计 / 材料 / 营销 / 爆款概率)
                            ↓
        设计团队 · 供应链团队 · 营销团队
```

---

## 🧩 四个核心 Agent

| Agent | 职责 | 关键输入 | 关键输出 |
| --- | --- | --- | --- |
| **Trend Agent** | 抓取电商平台 / 社交媒体趋势信号 | 类目、平台、时间窗 | 趋势关键词、热度评分 |
| **Consumer Agent** | 解析目标用户画像与情绪需求 | 年龄、性别、场景 | 用户洞察、情绪价值点 |
| **Design Agent** | 调用文化基因库重组设计语言 | 关键词、风格标签 | 设计元素、配色、材料 |
| **Prediction Agent** | 综合上述信号预测爆款概率 | 历史 SKU、销售数据 | 爆款概率、风险提示 |

---

## 🚀 Demo 示例

**输入：**
```
目标用户：18-25 岁女性
产品类别：生活家居
价格区间：30-100 元
关键词：治愈、东方、年轻化
```

**AI 输出：**

> **产品名称：** 「东方植物疗愈香氛盲盒」
>
> **市场洞察：** 年轻消费者关注情绪价值，搜索量同比增长 +187%。东方美学在小红书"新中式"话题下持续升温，植物香氛与盲盒机制形成稀缺感。
>
> **设计元素：** 宋代植物纹样（萱草、玉兰）+ 现代极简线条，圆角方形礼盒，6 款随机。
>
> **建议材料：** 环保 PET 礼盒、生物基香氛原料（大豆蜡）、可回收纸卡。
>
> **营销主题：** "把东方自然带回房间" —— 联合小红书 KOC 做开箱种草，主打"拆盲盒"内容。
>
> **爆款预测：** 87%（基于近 90 天类目增速、文化基因匹配度、价格带竞争密度综合评估）

---

## 📁 仓库结构

```
MINISO-AI-Product-Genome
├── README.md                  ← 你正在看的
├── docs/
│   ├── business_analysis.md   ← 商业分析
│   ├── AI_architecture.md     ← AI 架构详细设计
│   └── competition_report.md  ← 竞品调研
├── agents/
│   ├── trend_agent.py         ← 趋势智能体
│   ├── consumer_agent.py      ← 用户智能体
│   ├── design_agent.py        ← 设计智能体
│   └── prediction_agent.py    ← 预测智能体
├── dataset/
│   ├── trend_sample.csv       ← 趋势数据样例
│   ├── product_features.json  ← 产品特征库
│   └── consumer_feedback.json ← 用户反馈数据
├── demo/
│   ├── product_generation_demo.py  ← 一键运行 demo
│   └── screenshots/                ← 截图
└── visualization/
    └── dashboard.png          ← 决策报告可视化
```

---

## ⚡ 快速开始

```bash
git clone https://github.com/ledi13035/MINISO-AI-Product-Genome.git
cd MINISO-AI-Product-Genome

# 跑个 demo（无需 API key，使用本地 mock）
python demo/product_generation_demo.py
```

---

## 🛣️ Roadmap

- [x] 多 Agent 架构原型
- [x] 文化基因库（4 大类目种子数据）
- [x] 端到端 demo 跑通
- [ ] 接入真实电商数据 API（淘宝/天猫/京东）
- [ ] 接入 LLM（GPT-4 / Claude）替代规则引擎
- [ ] 文化基因库扩展到 20+ 类目
- [ ] 爆款预测模型训练（基于名创优品历史 SKU 销售）
- [ ] 设计稿自动生成（Stable Diffusion + ControlNet）

---

## 🤝 适用场景

- 名创优品品类经理的**选品辅助工具**
- 创业团队的**MVP 产品概念验证**
- 设计团队的**风格探索起点**
- 学术研究：多智能体协同决策 / 文化基因计算

---

## 📄 License

MIT
