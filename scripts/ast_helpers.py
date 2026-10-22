"""AST 小工具：取 `a.b.c` 的根标识符（原先在门禁与探针里各有一份）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/ast_helpers.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能多份实现」）：
#         同一段 4 行 AST 逻辑原先有**两个名字、两份实现**（逐字相同）——
#           · `check_member_names._base_name`
#           · `tools/probe_direct_member_access.py` 里的**嵌套** `ident`
#         本模块给出唯一实现 `base_name`。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只做 `ast` 树的形状判断，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast


def base_name(node) -> str | None:
    """取 `a.b.c` 的**根标识符** `a`（不是 `a` 就返回 `None`）。

    ★ 用途（两处，语义相同）：判「这个属性链的根是谁」——
      · `check_member_names`：判 `obj.Member` 里的 `obj`；
      · `probe_direct_member_access`：判
        `interference.GetInterference(...)` 的 `interference`。
    ★ 只沿 `ast.Attribute.value` 往下走，不做任何求值或名字解析。
    """
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None
