"""COM 返回值转 list 的单一实现（原先有两个名字）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_com_array.py
# 定位:   ★ 2026-10-22（仓库统一化 · 业主指令「同一个东西在不同的地方命名不一样」）：
#         同一段逻辑原来有**两个名字**（★ 逻辑逐字相同）——
#           · `sw_sketch.as_sequence`（★ 公开名，被 tool_specs_batch2 / tests 引用）
#           · `sw_drawing_create_missing._as_list`
#         本模块给出唯一实现 `as_list`；两处改为导入别名以保住既有名字。
#         判据 = `scripts/check_repo_uniformity.py` 指标⑤「跨文件同函数体组」只降不升。
# 官方依据: 不适用（本模块只做 Python 侧的类型归一，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any


def as_list(value) -> list[Any]:
    """★ COM 数组 → `list`；★ 单对象 → 单元素列表；★ `None` → 空列表。

    ⚠ 转换**只保证拿到元素**，不保证顺序 —— 官方未定义 SAFEARRAY 的顺序保证。
    需要按类型过滤请用 `SKETCH_GETTERS` 里的分类型取法，别用这个。
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]
