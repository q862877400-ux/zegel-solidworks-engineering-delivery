"""★ 首件重建（**唯一**入口）：一个孔特征 + 四点全约束 + GB 标准。

## 这个工具修的三个缺陷（业主 2026-10-26）

| 缺陷 | 旧件 | 本工具 |
|---|---|---|
| 孔特征数 | 4 个 `HoleWzd` | **1 个**，含 4 个孔点 |
| 孔点约束 | 4 张草图状态 2（可拖） | `fully_define_sketch` ⇒ 状态 3 |
| 孔标准 | `ANSI Metric` | **GB**（Toolbox 索引 13） |

## 全程用**本仓封装**（`tools/find_com_wrapper.py` 逐个查过）

| 要做的事 | 用的封装 |
|---|---|
| 删旧孔特征 | `sw_part.feature_delete`（封 `IModelDoc2.EditDelete`） |
| 进草图 | `sw_part.start_sketch`（封 `InsertSketch` 那条链） |
| 放孔点 | `sw_part.sketch_point`（**本轮新补**，封 `ISketchManager.CreatePoint`） |
| 完全定义 | `sw_sketch_dimensions.fully_define_sketch`（封 `FullyDefineSketch`） |
| 一个特征多个孔点 | `sw_hole_features.create_hole_wizard_multi_point`（**本轮新补**） |
| 量包围盒 | `sw_feature_readback.solid_body_extent_mm` |

★ 只有「选中草图点」没有封装（`ISketchPoint.Select4`），因为它是**一个标量 + 空 Dispatch**，
  调用点仅此一处 ⇒ 就地写，并在报告里记为**已知缺口**。

## 输出

`output/stage2/板1_rev-3.SLDPRT`，并在控制台逐项打印**独立读数**：
孔特征数、标准、草图状态、孔径。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "stage2" / "板1_rev-3.SLDPRT"

#: 孔心（毫米，相对板件左下角）
HOLES = ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0))
#: 本机实测：`IHoleStandardsData.GetHoleStandards` 序列里 GB = 13
GB_STANDARD_INDEX = 13
#: GB/T 5277-1985 M6 中等装配通孔（等同采用 ISO 273:1979）
M6_CLEARANCE_MM = 6.6


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（首件重建 · 唯一入口）
# 文件:   tools/build_first_part.py
# 定位:   重建首件板件的孔：一个孔特征 + 四个全约束孔点 + GB 标准。
#          起因：业主 2026-10-26 指出四个孔特征不优雅、孔点未两向约束、标准用了 ANSI Metric。
#          全过程调用本仓封装（见文件头表格）。
# 官方依据: IModelDoc2.EditDelete / AddHorizontalDimension2 / AddVerticalDimension2 ·
#          ISketchManager.CreatePoint / FullyDefineSketch / HoleWizard5 ·
#          IHoleStandardsData.GetHoleStandards（GB=13）· IModelDocExtension.SaveAs（6 参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    import shutil
    import time

    import sw_connect as c_
    from sw_connect import get_com_member as g
    from sw_feature_readback import solid_body_extent_mm
    from sw_hole_features import create_hole_wizard_multi_point
    from sw_part import feature_delete, sketch_point, start_sketch
    from sw_sketch_dimensions import fully_define_sketch

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        for d in list(g(sw, "GetDocuments") or ()):
            c_.try_call(sw.CloseDoc, str(g(d, "GetTitle") or ""))
        for _ in range(6):
            try:
                shutil.copy2(SRC, DEST)
                break
            except PermissionError:
                time.sleep(2)
        else:
            print("★ 源文件被占用")
            return 1
        ok, doc = c_.try_call(c_.open_document, sw, str(DEST))
        if not ok or doc is None:
            return 1
        print("① 副本 %s" % DEST.name)

        #: ② 删旧孔（用封装，不再手写 EditDelete）
        holes = _holes(doc)
        print("② 旧孔 %d 个" % len(holes))
        for name in holes:
            try:
                feature_delete(doc, name)
            except Exception as exc:  # noqa: BLE001
                print("   删 %s 失败：%s" % (name, type(exc).__name__))
        left = _holes(doc)
        print("   删后剩余 %d" % len(left))
        if left:
            print("★ 没删干净，中止")
            return 1

        #: ③ 量包围盒（零件自身坐标系）
        box = solid_body_extent_mm(doc)
        raw = [v * 1000.0 for v in (box.get("raw") or ())]
        if len(raw) < 6:
            print("★ 包围盒读不到")
            return 1
        lo_x, lo_y = raw[0], raw[1]
        print("③ 包围盒 x %.1f…%.1f  y %.1f…%.1f"
              % (lo_x, raw[3], lo_y, raw[4]))

        #: ④ 在**上视基准面**建草图（板件顶面就在 z=0，与该面重合）
        #:   ★ 用 上视基准面 而不是「选顶面」：前者有封装，后者要手写 InsertSketch。
        start_sketch(doc, "上视基准面")
        pts = []
        for (x_mm, y_mm) in HOLES:
            ok_p, pt = c_.try_call(sketch_point, doc, x_mm - lo_x, y_mm - lo_y)
            pts.append(pt if ok_p else None)
        print("④ 孔点 %d/4" % len([p for p in pts if p is not None]))

        #: ⑤ 完全定义（封装 FullyDefineSketch）
        ok_fd, _ = c_.try_call(fully_define_sketch, doc)
        print("⑤ fully_define_sketch：%s" % ok_fd)

        #: ⑥ 选中四点（★ 唯一没有封装的调用：ISketchPoint.Select4 + 空 Dispatch）
        doc.ClearSelection2(True)
        sel = 0
        for pt in pts:
            if pt is None:
                continue
            ok_s, _ = c_.try_call(
                pt.Select4, False, c_.create_empty_dispatch_variant()
            )
            sel += 1 if ok_s else 0
        print("⑥ 选中孔点 %d/4" % sel)

        #: ⑦ 一个孔特征吃四个点（本轮新补的封装）
        #: ★ try_call 只接位置实参 ⇒ 关键字调用要包 lambda（第 70 轮同款坑）
        ok_h, feat = c_.try_call(
            lambda: create_hole_wizard_multi_point(
                doc,
                "M6",
                diameter_mm=M6_CLEARANCE_MM,
                depth_mm=20.0,
                through=True,
                standard_index=GB_STANDARD_INDEX,
            )
        )
        print("⑦ HoleWizard5(GB) ok=%s" % ok_h)

        #: ⑧ 回读
        got = _holes(doc)
        print("⑧ 孔特征 %d 个：" % len(got))
        for f in got:
            d = g(f, "GetDefinition")
            try:
                print("     %-16s 标准=%s 规格=%s"
                      % (g(f, "Name"), g(d, "Standard"), g(d, "FastenerSize")))
            except Exception as exc:  # noqa: BLE001
                print("     %-16s 读不到（%s）" % (g(f, "Name"), type(exc).__name__))

        rows = _sketch_rows(doc)
        bad = [r for r in rows if r["status"] != 3]
        print("   草图共 %d，非全定义 %d %s"
              % (len(rows), len(bad), [(r["name"], r["status"]) for r in bad]))

        ok_save, _ = c_.try_call(
            g(doc, "Extension"), "SaveAs", str(DEST), 0, 5,
            c_.create_empty_dispatch_variant(), c_.out_i4(), c_.out_i4(),
        )
        print("⑨ 存盘 %s" % ok_save)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def _holes(doc) -> list:
    from sw_connect import get_com_member as g

    out = []
    f = g(doc, "FirstFeature")
    while f is not None:
        if str(g(f, "GetTypeName2") or "") == "HoleWzd":
            out.append(str(g(f, "Name") or ""))
        f = g(f, "GetNextFeature")
    return out


def _sketch_rows(doc) -> list:
    import sw_connect as c_
    from sw_connect import get_com_member as g

    rows = []
    f = g(doc, "FirstFeature")
    while f is not None:
        stack = [f]
        while stack:
            feat = stack.pop()
            if str(g(feat, "GetTypeName2") or "") == "ProfileFeature":
                ok, sk = c_.try_call(g, feat, "GetSpecificFeature2")
                st = None
                if ok and sk is not None:
                    ok2, v = c_.try_call(lambda: int(sk.GetConstrainedStatus))
                    st = v if ok2 else None
                rows.append({"name": str(g(feat, "Name") or ""), "status": st})
            sub = g(feat, "GetFirstSubFeature")
            while sub is not None:
                stack.append(sub)
                sub = g(sub, "GetNextSubFeature")
        f = g(f, "GetNextFeature")
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
