"""stdio UTF-8 重配的单一实现（原先在四个模块里各有一份）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_stdio.py
# 定位:   ★ 2026-10-22（仓库统一化）：`_configure_stdio_utf8` 原先在
#         `sw_macro_guard.py` / `sw_preflight.py` / `validate_mcp.py` /
#         `validate_skill.py` **各有一份**（四份逻辑逐字相同，只差一行的返回注解）
#         ⇒ 收敛到这里。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只调 Python 标准库 `sys.stdout.reconfigure`，不碰 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys


def configure_stdio_utf8() -> None:
    """在 Windows 旧代码页下尽量使用 UTF-8 输出中文提示。

    ★ 为什么要有它：中文 Windows 的控制台默认代码页（GBK）会让含中文的 `print` 抛
      `UnicodeEncodeError`；`reconfigure` 是标准库给的正解。
    ★ 为什么用 `hasattr` 判一下：`sys.stdout` 被重定向成非 `TextIOWrapper` 时
      没有该方法。
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
