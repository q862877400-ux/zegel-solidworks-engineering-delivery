r"""@brief 决定性实验：`CreateCylindricalSurface` 的成功取决于**axis**还是**调用顺序/状态**？

## 上一个矩阵的异常结果
```
第 1 个（③ 节首试）: axis=(0,0,1) → **None**
第 2 个:            axis=(1,0,0) → **非 None**   ← 唯一的成功
第 3 个:            axis=(0,1,0) → **None**
第 4 个:            axis=(0,0,0) → **None**
```
**⇒ 两种解释：**
* **A（axis 决定）**：只有 `+X` 能建圆柱面。**但这在物理上没道理** —— 圆柱面不该挑轴。
* **B（状态/顺序决定）**：第 2 次调用成功与 axis 无关，是**前面失败的调用留下了某种状态**，
  或**第 2 次**这个位置本身特殊。

**⇒ 决定性实验：把 `(1,0,0)` 放到**第一个**。
* 若它仍成功 ⇒ 支持 A（axis 决定）
* 若它失败，而**后面某个别的**成功 ⇒ 支持 B（状态/顺序）
* 若**全失败** ⇒ 说明「第一次调用」这个位置有影响

**⚠ 还要单独测一个可能：`IModeler` 每次是否应重新取**
（`ISldWorks.GetModeler` 可能返回同一单例；`.Refresh()` / 重新取 可能重置状态）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_cyl_order_vs_axis.py
# 定位:   已知事实 40「圆柱/圆锥返回 None」的**最后一层定性**。
# 官方签名依据: `IModeler.CreateCylindricalSurface(Object, Object, Double)`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只调 `IModeler`、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_surface as S  # noqa: E402

AXES = ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        modeler = S.get_modeler(sw)
        print("[参照] 零件 %r" % title)

        print()
        print("=== 实验 A：**把 (1,0,0) 放到第一个**（轴序固定，看位置效应）===")
        print("    顺序: (1,0,0) → (0,0,1) → (0,1,0) → (0,0,1)")
        for i, ax in enumerate(AXES, 1):
            try:
                v = get_com_member(modeler, "CreateCylindricalSurface",
                                   (0.0, 0.0, 0.0), ax, 0.01)
                print("  %d. axis=%-16r → %s" % (i, ax, "✓ 非 None" if v is not None else "✗ **None**"))
            except Exception as exc:  # noqa: BLE001
                print("  %d. axis=%-16r → ✗ %s" % (i, ax, str(exc)[:50]))

        print()
        print("=== 实验 B：**每次重新取 modeler**（排除单例状态）===")
        for i, ax in enumerate(AXES, 1):
            m2 = S.get_modeler(sw)
            try:
                v = get_com_member(m2, "CreateCylindricalSurface",
                                   (0.0, 0.0, 0.0), ax, 0.01)
                print("  %d. **新取 modeler** axis=%-16r → %s"
                      % (i, ax, "✓ 非 None" if v is not None else "✗ **None**"))
            except Exception as exc:  # noqa: BLE001
                print("  %d. 新取 modeler axis=%-16r → ✗ %s" % (i, ax, str(exc)[:46]))

        print()
        print("=== 实验 C：**连续调同一个 axis 三次**（看是否「第 N 次」在起作用）===")
        for i in range(1, 4):
            try:
                v = get_com_member(modeler, "CreateCylindricalSurface",
                                   (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.01)
                print("  第 %d 次（axis=(1,0,0)）→ %s" % (i, "✓ 非 None" if v is not None else "✗ **None**"))
            except Exception as exc:  # noqa: BLE001
                print("  第 %d 次 → ✗ %s" % (i, str(exc)[:50]))

        print()
        print("=== 实验 D：球面/圆环面（**已知成功**的）在同一 modeler 上再调，看还成不成 ===")
        for label, fn in (
            ("spherical((0,0,0), 0.01)",
             lambda: get_com_member(modeler, "CreateSphericalSurface", (0.0, 0.0, 0.0), 0.01)),
            ("cyl((0,0,0),(0,0,1),0.01) 再试",
             lambda: get_com_member(modeler, "CreateCylindricalSurface",
                                    (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.01)),
        ):
            try:
                v = fn()
                print("  %-42s → %s" % (label, "✓ 非 None" if v is not None else "✗ **None**"))
            except Exception as exc:  # noqa: BLE001
                print("  %-42s → ✗ %s" % (label, str(exc)[:46]))

        print()
        print("=== 结论 ===")
        print("  若实验 A 里 (1,0,0) **失败** ⇒ **不是 axis 决定** ⇒ 是**顺序/状态**")
        print("  若实验 B 里它**成功** ⇒ **单例 modeler 的状态**是原因（重新取即好）")
        print("  若实验 C 里**都成功** ⇒ 「第一次调用」这个位置有影响")
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
