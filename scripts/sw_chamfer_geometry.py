r"""@brief 倒角的**解析体积**（45° 等距）—— ★ 用来把"倒角断言"从"体积变了"升级为"**体积该变多少**"。

## ★★★ 本文件是**抄判据**，不是抄实现（★ AGENTS.md §5.0 的正解形态）
```
★★ 判据原文（**抄自** `andrewbartels1/SolidworksMCP-python` 的
   `tests/live/test_live_sw_add_chamfer_tool.py`，**MIT**，版权归其作者，见下「来源」）：
     def _expected_circular_chamfer_volume(radius_mm, width_mm):
         r, w = radius_mm, width_mm
         return math.pi * (((r + w) ** 3 - r ** 3) / 3.0 - r * r * w)
     def _expected_straight_chamfer_volume(length_mm, width_mm):
         return 0.5 * width_mm * width_mm * length_mm
⇒ ★ **本文件只搬这两个公式**（★ 几何推出的，★ 不是拟合的）；★ **实现一行没搬**。
```

## ★★★★ 而**为什么值得搬**（★ 那份判据的方法论，比公式更值钱）
```
★ 它原文写着（★ 我照抄要点，不逐字搬）：
   · ★ 测**错误的边**时，量到的体积**不是**圆孔边缘期望的 ~2.29 mm³
     ⇒ ★★ **比早先那个"零体积空操作"更糟** —— ★ 因为**非零体积差**会让人以为对了；
   · ★ 特征树里有它、而移除**零体积** ⇒ **静默空操作**；
   · ★★★ **结论：工具报的状态、特征名、"体积变了一点" —— 没有一个是充分的证明。**
     ★ 要**三件一起**：**特征在** + **体积下降** + **下降量 ≈ 解析公式**。
⇒ ★ **这正是本仓库"回读优先"的加固**：★ 从"变了吗"到"**变了多少、与几何算的对不对**"。
```

## ★ 两个公式的**独立核验**（★ 我不盲信抄来的公式）
```
★ 圆孔缘那条：`π·[ ((r+w)³ − r³)/3 − r²·w ]`
  ⇒ ★ 拆开看 = 「**半径 r → r+w 的圆台体积**」−「**高 w、半径 r 的圆柱体积**」
    · 圆台：`π/3 · h · (R² + Rr + r²)`，取 R = r+w、h = w
      ⇒ `π/3 · w · ((r+w)² + (r+w)r + r²)` = `π/3 · [(r+w)³ − r³]` ✓（★ 立方差）
    · 圆柱：`π r² w` ✓
  ⇒ ★★ **自洽** ✓
★ 数值核验：★ 它的工件是 30×30×15 mm 块 + **Ø5.5 孔**（r = 2.75），
  ★ 判据说圆孔缘倒角期望 **~2.29 mm³** ⇒ 取 w = 0.5 代进去：
    `π·[((3.25)³ − (2.75)³)/3 − (2.75)²·0.5]` = `π·[(34.328 − 20.797)/3 − 3.78125]`
    = `π·[4.510 − 3.781]` = `π·0.729` = **2.29** ✓✓✓
  ⇒ ★★★ **对上了** —— ★ 说明那份判据里的期望值是**算出来的**，★ 不是量出来再写死的。
```

## ⚠ 边界（★ 如实标注，不假装通用）
```
★ **只对 45° 等距倒角成立**（★ 公式的前提）；★ 非 45° 或非等距要另推。
★ **直边**那条假设倒角**贯穿整条边**（★ 长度 L 全程），★ 且**两端没有别的干涉**。
★ **圆孔缘**那条假设孔是**通孔/缘在同一平面上**，★ 且倒角**沿整个圆周**。
⇒ ★ 用之前先确认这三条前提；★ 不符就**不要拿它当判据**。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   andrewbartels1/SolidworksMCP-python（**MIT**）—— ★ **只搬判据（两个解析公式）**
# 文件:   tests/live/test_live_sw_add_chamfer_tool.py（L78-86）
#         ⇒ ★ 本地克隆：`C:\swprojects\andrewbartels1\tests\live\test_live_sw_add_chamfer_tool.py`
# 定位:   24h 计划 段 5「修地基 **D4**」—— 倒角断言升级。
#         ★ 依据：AGENTS.md §5.0（"判据先去开源项目里找"）+ known-facts 171 的待办。
# 许可:   **MIT** ⇒ 可读、可抄、可改；★ **保留版权声明**（见下）。
#         ⚠ 本文件**没有**搬它的任何实现代码、测试骨架或夹具（★ 只搬两个数学公式）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
# Copyright (c) andrewbartels1/SolidworksMCP-python contributors — MIT License.
# ★ 本文件的两个公式派生自上述项目 `tests/live/test_live_sw_add_chamfer_tool.py` 的
#   `_expected_circular_chamfer_volume` / `_expected_straight_chamfer_volume`；
#   ★ 注释、边界说明、独立核验与接口为本项目所加。
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math

__all__ = [
    "straight_chamfer_volume_mm3",
    "circular_rim_chamfer_volume_mm3",
    "chamfer_volume_report",
]


def straight_chamfer_volume_mm3(length_mm: float, width_mm: float) -> float:
    """★ **直边** 45° 等距倒角**切掉的体积**（mm³）。

    ★ 公式：`0.5 · w² · L` —— ★ 截面是**等腰直角三角形**（直角边 = w），沿边扫长度 L。

    ⚠ 前提：★ 倒角**贯穿整条边**、**两端无干涉**、**45° 等距**。
    """
    return 0.5 * float(width_mm) * float(width_mm) * float(length_mm)


def circular_rim_chamfer_volume_mm3(radius_mm: float, width_mm: float) -> float:
    """★ **圆孔缘** 45° 等距倒角**切掉的体积**（mm³）。

    ★ 公式：`π · [ ((r+w)³ − r³)/3 − r²·w ]`
      = 「**半径 r → r+w 的圆台**」−「**高 w、半径 r 的圆柱**」（★ 本文件独立核验过，见模块 docstring）。

    ⚠ 前提：★ 孔在同一平面上、倒角**沿整个圆周**、**45° 等距**。
    """
    r, w = float(radius_mm), float(width_mm)
    return math.pi * (((r + w) ** 3 - r**3) / 3.0 - r * r * w)


def chamfer_volume_report(kind: str, volume_before_mm3: float, volume_after_mm3: float,
                          *, expected_removed_mm3: float, rel_tol: float = 0.05) -> dict:
    """★ 把「**倒角断言**」做成一条可判的判据。

    ★★ 判据**三件一起**（★ 抄自那份判据的方法论；★ 单看任一件都不够）：
        ① ★ **体积下降了吗**（`removed > 0`）—— ★ 否则是"静默空操作"；
        ② ★ **下降量 ≈ 解析公式**（相对误差 ≤ `rel_tol`）—— ★ 否则"做在错的几何上"
           （★ 那份判据原文警告：★ **非零体积差比零体积更糟**，因为它**看起来对了**）；
        ③ ★ **特征是否在**由调用方另查（★ 本函数管不到特征树）。
    """
    before = float(volume_before_mm3)
    after = float(volume_after_mm3)
    removed = before - after
    exp = float(expected_removed_mm3)
    rel = abs(removed - exp) / exp if exp else float("inf")
    return {
        "ok": removed > 0 and rel <= float(rel_tol),
        "kind": kind,
        "volume_before_mm3": before,
        "volume_after_mm3": after,
        "removed_mm3": removed,
        "expected_removed_mm3": exp,
        "rel_error": rel,
        "rel_tol": float(rel_tol),
        "decreased": removed > 0,
        "matches_formula": rel <= float(rel_tol),
        "★": ("ok = **体积下降** 且 **下降量 ≈ 解析公式**（★ 单看任一件都不够："
              "★ 只下降 ⇒ 可能做在错的几何上；★ 只对上公式 ⇒ 不可能）。"
              "★ 特征是否在**由调用方另查**"),
    }
