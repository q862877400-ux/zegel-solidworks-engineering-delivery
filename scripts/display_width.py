"""显示宽度（CJK 全角计 2 列）的单一实现。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/display_width.py
# 定位:   ★ 2026-10-22（仓库统一化）：ruff 的 `E501`、以及本仓的折行工具，量的都是
#         **显示宽度**（不是字符数）—— CJK 全角占 2 列。原先这个函数有**两份**：
#           · `tools/wrap_long_comments.width`
#           · `scripts/check_repo_uniformity._display_width`
#         本模块给出唯一实现。判据 = `scripts/check_repo_uniformity.py` 指标⑤只降不升。
# 官方依据: `unicodedata.east_asian_width` 的 `W`（Wide）与 `F`（Fullwidth）两类 ≠ 1 列。
#         第 7 轮实测过：按**字符数**折行，ruff 的 E501 反而**变多**（因为 CJK 计 2 列）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import unicodedata

#: ★ 占 **2 列**的东亚宽度类别：`W`(Wide) / `F`(Fullwidth)
_WIDE = ("W", "F")


def display_width(s: str) -> int:
    """⇒ 字符串在等宽终端里的**显示宽度**（CJK 全角按 2 列算）。"""
    return sum(2 if unicodedata.east_asian_width(c) in _WIDE else 1 for c in s)
