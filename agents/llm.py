"""
LLM Client - 统一的大模型接入层
================================

设计目标（高价值 · 低代码）：
- 生产环境：设置 ``OPENAI_API_KEY`` 后，四个 Agent 自动切换为 GPT-4o 真实分析。
- 本地 / 测试环境：未设置 Key 时自动回退到规则引擎，框架永远可运行。
- 单元测试：可注入 ``MockLLM``，在不联网、零成本的前提下验证 LLM 代码路径。

接口约定：任何 LLM 实现都需提供
    - ``available`` 属性（bool）
    - ``complete(system: str, user: str) -> str`` 方法
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional


class MockLLM:
    """用于单元测试的确定性 LLM 替身，实现与 :class:`LLMClient` 一致的接口。"""

    def __init__(self, canned: Optional[str] = None):
        # canned: 预置返回文本；None 时返回最小可用 JSON，具体由测试覆盖
        self.canned = canned

    @property
    def available(self) -> bool:
        return True

    def complete(self, system: str, user: str) -> str:
        if self.canned is not None:
            return self.canned
        return json.dumps({"result": "mock"})


class LLMClient:
    """OpenAI GPT-4o 接入封装（兼容任意 OpenAI 兼容端点）。"""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.temperature = temperature
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI

                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except Exception:
                # 即使装了 openai，实例化失败也安全回退
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(self, system: str, user: str) -> str:
        if not self.available:
            raise RuntimeError(
                "LLM 当前不可用：请设置 OPENAI_API_KEY，或在调用处注入 MockLLM 进行测试。"
            )
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""


def extract_json(text: str):
    """从 LLM 返回文本中稳健地解析 JSON。

    兼容以下情况：
    - 被 ```json ... ``` 代码块包裹
    - 前后带有解释性文字
    - 不完整的花括号（尽力截取首个 { 到末个 }）
    """
    if text is None:
        return None
    text = text.strip()

    # 1) 去掉 markdown 代码块
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    # 2) 标准解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3) 尽力截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None
