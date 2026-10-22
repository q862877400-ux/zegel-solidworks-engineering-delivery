"""无头（headless）路线的共用访问器（原先在两个模块里各有一份）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/headless_common.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能单份实现」）：同一个单行访问器原先有
#         **两个名字、两份实现**（逐字相同）——
#           · `headless_cad_writer._feature_params`
#           · `headless_occt_service._params`
#         两者都做「从 feature 字典里安全取 `parameters`，不是 dict 就回空 dict」。
#         本模块给出唯一实现 `feature_params`。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只读 Python 字典，不调 COM、不碰几何内核）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any


def feature_params(feature: dict[str, Any]) -> dict[str, Any]:
    """★ 安全取 `feature["parameters"]`：★ 不是 dict（含缺席、`None`、别的类型）⇒ 回 `{}`。

    ★ 为什么容忍而不抛：无头路线的输入是外部 JSON，**字段缺失是常态**；
      这里回空 dict 让上层按「没给参数」处理，★ 而不是让整条流水线因一个字段崩掉。
    """
    return feature.get("parameters") if isinstance(feature.get("parameters"), dict) else {}
