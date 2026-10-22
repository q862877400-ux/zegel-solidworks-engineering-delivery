"""门禁脚本共用的「向上找声明行」实现（原先 4 个门禁各有一份）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/gate_decl.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能多份实现」）：
#         `declaration_above` 原先在 4 个门禁脚本里各有一份，分**两个变体**：
#           · 返回 `mode`     —— `check_arity_tables_vs_reflection` /
#             `check_assembly_doc_call_shape`
#             （这两份**连 `DECL` 正则都逐字相同** ⇒ 真重复）
#           · 返回 `(head, rest)` —— `check_create_definition_site_disposition` /
#             `check_dispatch_forward_arg_guard`
#             （**同形但绑不同正则** ⇒ 参数化即可共用）
#         本模块给出唯一实现；正则由调用方传入，故三种绑定都能用同一份逻辑。
# 官方依据: 不适用（本模块只读源码行文本，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from typing import Any

#: ★ `arity-reflect` 族共用的声明正则（两个门禁原本各写一遍、逐字相同）
DECL_ARITY_REFLECT = re.compile(
    r"^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$")


def declaration_above(lines: list[str], lineno: int, decl: Any):
    """⇒ 表起始行（1-based `lineno`）**上方最近的声明**的 `re.Match`；`None` = 未表态。

    ★ **确定性**：只跳过空行，第一行非空行必须匹配 `decl` —— ★ 不往上多翻一行，
      也不接受「隔了几行也算」⇒ ★ 同一个位置永远得到同一个判定。
    ★ `decl` 由调用方传入：不同门禁声明的是不同指令（`arity-reflect` / `cd-site` /
      `dispatch-fwd`），★ 但「向上找最近声明」这段逻辑是同一件事。
    """
    i = lineno - 2
    while i >= 0 and not lines[i].strip():
        i -= 1
    if i < 0:
        return None
    return decl.match(lines[i].strip())


def arity_mode_above(lines: list[str], lineno: int) -> str | None:
    """⇒ `arity-reflect: byref=included|excluded` 里的 **mode**；`None` = 未表态。

    ★ 供 `check_arity_tables_vs_reflection` 与 `check_assembly_doc_call_shape` 共用
      （★ 这两个门禁原先各有一份**逐字相同**的实现，连 `DECL` 正则都一样）。
    """
    m = declaration_above(lines, lineno, DECL_ARITY_REFLECT)
    return m.group("mode") if m else None


def decl_parts_above(lines: list[str], lineno: int, decl: Any):
    """⇒ `(head, rest)` 或 `None`（未表态）。

    ★ 供 `check_create_definition_site_disposition`（`cd-site:`）与
      `check_dispatch_forward_arg_guard`（`dispatch-fwd:`）共用 —— ★ 两者**同形但绑不同
      正则**，正则由调用方传入即可共用同一份逻辑。
    """
    m = declaration_above(lines, lineno, decl)
    if not m:
        return None
    return m.group("head"), (m.group("rest") or "").strip()
