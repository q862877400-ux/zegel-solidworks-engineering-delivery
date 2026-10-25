"""★ 修正版 · 人工验收第 2 步「准备」：让上面那块**真的在 Y 方向抬高**。

## 上一版错在哪（业主当场纠正）

我把 `add_component(z_m=0.050)` 说成「抬高 50mm」。
但 SolidWorks 默认前视图的**竖直方向是 Y，Z 是深度（朝观察者）**
⇒ 那块板被我推到了**后面**，前视图里两块**一样高**。

业主原话：

> 你所谓的左下的那一块，它的**几何中心和原点**是重合的；你所谓的右上的那一块，
> 它**只是往右错开**了一点，**并没有高出一截**。

三条都核对过（`GetBox` 硬读数）：
- 组件1 中心 **(0,0,0)** ⇒ 几何中心与原点重合 ✓ 业主对
- 组件2 与组件1 的 **Y 完全相同**（都是 −30…30）⇒ 没有高 ✓ 业主对
- 组件2 只 X +30mm、Z +50mm ✓ 业主对

## 本版场景（可目视）

```
组件1（蓝）  中心 (0,  0, 0)     X −50…50  Y −30…30  Z −10…10
组件2（粉）  中心 (0, 90, 0)     X −50…50  Y  60…90  Z −10…10
                                   ↑ 真·抬高：底面 60 = 下方顶面 30 + 间距 30mm
```

★ 两者 X/Z 完全对齐 ⇒ 前视图里就是「一块悬在另一块正上方 30mm」，
  配合做成后应当**垂直落下 30mm 贴住** —— 这在**前视图**里一眼可见。

## 射线（`SelectByRay` 收米）

| 目标面 | 起点 | 方向 |
|---|---|---|
| 组件1 **顶面**（Y=+30mm） | (0, +0.100, 0) | **−Y** |
| 组件2 **底面**（Y=+60mm） | (0, +0.040, 0) | **+Y** |
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（人工验收 · 第 2 步「准备」修正版）
# 文件:   tools/coop_prepare_mate_v2.py
# 定位:   让上面那块板在 **Y 方向**真抬高（上一版用 Z，前视图里看不出高矮），
#          上色 + 三视图 + 包围盒读数一并产出。起因见
#          docs/human-acceptance-protocol.md 与事实 579。
# 官方依据: IAssemblyDoc::AddComponent5 · IComponent2::GetBox ·
#          IComponent2::SetMaterialPropertyValues2 · IModelDoc2::ShowNamedView2 ·
#          IModelDocExtension::SaveAs（6 参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
ASM = R / "output" / "coop" / "配合演示_v2_初始.SLDASM"
SHOTS = R / "output" / "shots"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def _color(comp, rgb) -> bool:
    import pythoncom
    from win32com.client import VARIANT

    vals = [
        float(rgb[0]), float(rgb[1]), float(rgb[2]),
        1.0, 1.0, 0.5, 0.5, 0.0, 0.0,
    ]
    ok, _ = c_.try_call(
        c_.get_com_member,
        comp,
        "SetMaterialPropertyValues2",
        VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vals),
        1,
        VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_BSTR, []),
    )
    return bool(ok)


def _box(comp) -> tuple:
    ok, arr = c_.try_call(c_.get_com_member, comp, "GetBox", False, False)
    if not ok or arr is None:
        return ()
    v = [round(float(x) * 1000.0, 1) for x in list(arr)[:6]]
    return (tuple(v[0:3]), tuple(v[3:6])) if len(v) >= 6 else ()


def main() -> int:
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        for d in list(get_com_member(sw, "GetDocuments") or ()):
            sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))

        c_.open_document(sw, str(PART))
        ok, asm = c_.try_call(c_.new_document, sw, "assembly")
        try:
            sw.ActivateDoc3(str(get_com_member(asm, "GetTitle") or ""), 0, False)
        except Exception:  # noqa: BLE001
            pass
        cand = get_com_member(sw, "ActiveDoc")
        if cand is not None and int(get_com_member(cand, "GetType") or 0) == 2:
            asm = cand

        #: ★ 第二块用 **y_m**（真·抬高），不是 z_m
        asm_.add_component(asm, str(PART), x_m=0.0, y_m=0.0, z_m=0.0, sw=sw)
        asm_.add_component(asm, str(PART), x_m=0.0, y_m=0.090, z_m=0.0, sw=sw)

        comps = list(get_com_member(asm, "GetComponents", False) or ())
        print("组件数：%d" % len(comps))
        if len(comps) >= 1:
            print("组件1 蓝色：%s" % _color(comps[0], (0.15, 0.35, 0.90)))
        if len(comps) >= 2:
            print("组件2 粉色：%s" % _color(comps[1], (0.95, 0.45, 0.75)))

        print("\n── 世界包围盒（毫米）──")
        for i, cp in enumerate(comps, 1):
            nm = str(get_com_member(cp, "Name2") or "")
            bx = _box(cp)
            if bx:
                lo, hi = bx
                print(
                    "  组件%d %-16s X %7.1f…%7.1f  Y %7.1f…%7.1f  Z %7.1f…%7.1f"
                    % (i, nm, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
                )
        if len(comps) >= 2:
            boxes = [_box(c) for c in comps]
            boxes = [b for b in boxes if b]
            if len(boxes) == 2:
                #: ★ 不能按 GetComponents 的顺序假定谁在下 —— 实测顺序**不等于**插入顺序
                #:   （先加的 -1 反而排在后面）。按 Y 区间**排序**再算间隙。
                boxes.sort(key=lambda b: b[0][1])
                low, high = boxes
                gap = high[0][1] - low[1][1]
                print(
                    "  ⇒ 下方顶面 Y=%.1f · 上方底面 Y=%.1f ⇒ **间距 %.1f mm**（Y 方向）"
                    % (low[1][1], high[0][1], gap)
                )

        #: 存盘
        ASM.parent.mkdir(parents=True, exist_ok=True)
        c_.try_call(
            c_.get_com_member,
            c_.get_com_member(asm, "Extension"),
            "SaveAs",
            str(ASM),
            0,
            5,
            c_.create_empty_dispatch_variant(),
            c_.out_i4(),
            c_.out_i4(),
        )

        #: ★ 业主建议：标准视图上打开**网格**，视觉判距离更容易（tools/sw_grid.py）
        try:
            sys.path.insert(0, str(R / "tools"))
            from sw_grid import enable_grid

            print("网格：%s" % enable_grid(asm, major_mm=10.0))
            try:
                asm.GraphicsRedraw2()
            except Exception:  # noqa: BLE001
                pass
        except Exception as exc:  # noqa: BLE001
            print("网格打开失败：%s" % type(exc).__name__)

        #: 三视图（★ 前视图是判断「高不高」的地方）
        SHOTS.mkdir(parents=True, exist_ok=True)
        import time

        from sw_screenshot import capture, find_sw_window

        for label, view in (("前视", "*前视"), ("上视", "*上视"), ("右视", "*右视")):
            try:
                asm.ShowNamedView2(view, 7)
                asm.ViewZoomtofit2()
            except Exception as exc:  # noqa: BLE001
                print("  切视图失败 %s: %s" % (view, type(exc).__name__))
                continue
            time.sleep(0.8)
            ok_c, w, h, err = capture(find_sw_window(), SHOTS / ("v2-%s.png" % label))
            size = ("%sx%s" % (w, h)) if ok_c else err
            print("  %s → v2-%s.png（%s）" % (label, label, size))

        print("★ 文档保持打开：%s" % ASM.name)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    raise SystemExit(main())
