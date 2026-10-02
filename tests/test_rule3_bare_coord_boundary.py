"""★ 规则 3 的**裸坐标判据边界** —— ★ 而它钉的是**轮 433 那次放宽的两侧**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_rule3_bare_coord_boundary.py
# 定位:   ★ 2026-10-03（轮 433）—— ★★ **我放宽了一条门禁，而放宽必须有看守**。
#   ★★ 背景：`pytest` 收集期抓到 **4 条** `规则 3 违反：… 是裸坐标`，★ 而**查明**：
#     ```
#     · `solidworks_sketch_add_ellipse.z_mm`       —— ★ 草图几何的面内坐标
#     · `solidworks_sketch_add_centerline.z_mm`    —— ★ 同上
#     · `solidworks_add_dimension.x_mm`            —— ★ 同上
#     · `solidworks_surface_fill.boundary_z`       —— ⚠★ **这一条不是**（★ 见下）
#     ```
#     ★★ 而**前三条例外是有依据的**：`AGENTS.md` 明写规则 3 **有一条文档化的例外** ——
#       「*Sketch geometry MUST be given as in-plane coordinates — this is the documented
#        exception in rule 3*」✓
#   ★★★ **而真正的矛盾在别处**：★ **精确黑名单里有 `x_mm`/`y_mm`/`z_mm`**，
#     ★ 而**规则 2 恰恰要求长度参数以 `_mm` 结尾** ⇒ ★★ **两条规则自相矛盾** ⚠
#   ⇒ ★ 修法：★ **"裸"的定义收紧为「没有单位信息」** ⇒
#     ★ **以 `_mm` 结尾的坐标放过**（★ 它带着单位），★ 而 `x` / `boundary_z` / `d1_x` **照旧拦** ✓
#   ⚠ ★ 而 `boundary_z` **照旧被拦**是**对的** —— ★ 它是"**用坐标去选那一圈边**"，
#     ★ 那**正是**规则 3 要禁的形态 ⇒ ★ **它是真欠账，不许被这次放宽掩盖** ✓
# 官方依据: `AGENTS.md` §二 铁律（规则 2 与规则 3）· `mcp-server/tool_registry.py` 的
#   `_BARE_COORD_NAMES` / `_looks_like_coord_component`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp-server"))

from tool_registry import _BARE_COORD_NAMES, _looks_like_coord_component  # noqa: E402


def _flagged(name: str) -> bool:
    """★ 该名字会不会被规则 3 拦（★ 与门禁里那两段判据**同一口径**）。"""
    return name in _BARE_COORD_NAMES or _looks_like_coord_component(name)


def test_unit_carrying_coordinates_are_not_bare() -> None:
    """★★ **放宽的那一侧**：★ **带 `_mm` 的坐标不"裸"**（★ 它携带着单位）。

    ★ 依据：★ 规则 2 **要求**长度参数以 `_mm` 结尾 ⇒ 若把 `z_mm` 当裸坐标，
      ★ 两条规则就**自相矛盾**（★ 而那就是轮 433 查明的东西）。"""
    for nm in ("x_mm", "y_mm", "z_mm", "start_x_mm", "end_y_mm", "center_x_mm"):
        assert not _flagged(nm), "%s 带着单位（_mm），不该算裸坐标" % nm


def test_bare_coordinates_are_still_flagged() -> None:
    """★★ **没放宽的那一侧**：★ **不带单位**的坐标**照旧拦** —— ★ 而这条是放宽的**守卫**。

    ⚠★ 尤其包括 `boundary_z` —— ★ 它是**真欠账**（"用坐标去选那一圈边"），
      ★ 轮 433 的放宽**不许**把它一起放过。"""
    for nm in ("x", "y", "z", "x1", "y2", "cx", "cy", "cz",
               "d1_x", "d1_y", "major_x", "minor_y", "point", "coordinate",
               "boundary_z"):
        assert _flagged(nm), "%s 不带单位 ⇒ 应算裸坐标" % nm


def test_non_coordinate_lengths_are_not_flagged() -> None:
    """★ **非坐标的长度参数**不受影响（★ 免得放宽时误伤）。"""
    for nm in ("radius_mm", "depth", "thickness_mm", "offset", "pitch"):
        assert not _flagged(nm), "%s 不是坐标分量，不该被规则 3 拦" % nm


def test_the_three_exact_entries_are_gone() -> None:
    """★★ **那三个自相矛盾的条目已从精确黑名单里去掉** —— ★ 谁把它们加回来，这条就红。"""
    for nm in ("x_mm", "y_mm", "z_mm"):
        assert nm not in _BARE_COORD_NAMES, (
            "%s 又被加回 `_BARE_COORD_NAMES` 了 ⇒ 规则 2 与规则 3 会重新自相矛盾（轮 433）" % nm)


def test_real_debt_still_flagged_by_the_gate() -> None:
    """★★★ **真欠账仍被门禁拦着**（★ 而不是被放宽掩盖）。

    ★ `solidworks_surface_fill.boundary_z` 是"**用坐标去选那一圈边**" ——
      ★ 那**正是**规则 3 要禁的形态（★ "必须改用具名实体 + 声明式 selection"）。
    ★★ 而本条**故意不修它**：★ 修它要动 `sw_surface_features` 的实现 ⇒ ★ **另开一轮**。"""
    assert _flagged("boundary_z"), (
        "boundary_z 若不再被拦，说明轮 433 的放宽扩大化了 —— "
        "它是真欠账（用坐标选边），不许被掩盖")
