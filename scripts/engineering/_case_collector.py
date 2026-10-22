"""「收集 cases」的单一实现（原在两个 dataclass 里各有一份、且**名字还不一样**）。"""
# ── 来源 ──────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/engineering/_case_collector.py
# 定位:   ★★ 2026-10-22（仓库统一化）：同一件事在两个 dataclass 里
#         **两个名字**（`EvalSet.add` 与 `FinalDod.add_case`），而两个方法体都是
#         一行 `self.cases.append(x)` —— ★这正是业主说的「同一个东西命名不一样」。
#         ⇒ 抽成 mixin，统一叫 `add_case`。
#         ★ 改名风险 = 0：全仓 `.add(` / `.add_case(` 对这两个类**零调用点**
#           （实测：两个文件各 0 次；其余 310 处 `.add(` 全是 `set.add`）。
# 官方依据: 不适用（本模块只做列表追加）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations


class CaseCollectorMixin:
    """★ 「收集案例」形状：实现类必须有 `cases` 字段（列表）。"""

    cases: list

    def add_case(self, case) -> None:
        """★ 往 `cases` 里追加一个案例。

        ★ 唯一名字：原来一处叫 `add`、一处叫 `add_case`。
        """
        self.cases.append(case)
