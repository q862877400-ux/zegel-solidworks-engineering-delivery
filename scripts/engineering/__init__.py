"""★ EC02 的包初始化（★ 让 `scripts/engineering/` 成为可导入的包）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` §5 EC02（★ 建议落点 `scripts/enginee
# ring/`）
# 定位:   ★ EC02 的确定性规则与计算层入口。
# 官方依据: 不适用
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from . import rules  # noqa: F401

__all__ = ["rules"]
