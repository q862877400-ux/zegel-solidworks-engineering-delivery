"""★ 首件重建（**唯一**入口）：4 个 **GB** 孔（标准已修；其余两条见下）。

## 三条批评的现状（业主 2026-10-26）

| # | 批评 | 本工具 |
|---|---|---|
| 1 | 四个孔特征不优雅（应一个特征多个点） | ⚠ **未解决** —— 三条 API 路线都失败，见下 |
| 2 | 孔位草图欠定义（能单向拖） | ⚠ **未解决** —— 孔位草图状态仍 2 |
| 3 | 标准该用 GB（旧件是 ANSI Metric） | ✅ **已修** —— 四个孔全部 `标准=GB · 螺钉间隙 · M6` |

## 第 3 条怎么修好的（关键索引）

```
standard_index = 13     GB（Toolbox GetHoleStandards 名单里的 GB）
fastener_index = 356    GB 下的「螺钉间隙」
```
★ 旧件的 `fastener_index=40` 是 **ANSI Metric** 的口径。
★ 我先扫了 0..90 全失败、据此差点写下「GB 建不出孔」的错误结论；
  扩到 0..400 才在 **356** 命中 —— 教训：**扫描范围不足会产出假结论**。

## 第 1 条为什么没做成（三条路，都有读数）

```
① 草图里 4 点/4 圆 → 一次 HoleWizard5
   ⇒ HoleWizard5 回 None，特征 0 个（连已知可用的 ANSI 也如此）
② 特征线性阵列（选 BODYFEATURE，mark 4/0/1）
   ⇒ 特征树不变（封装明确：本函数不做选择，前置由调用方给）
   而选 SOLIDBODY + mark 256 会得到**体阵列** ⇒ 4 块板（几何错）
③ 孔特征自己的定位草图里做草图阵列（CreateLinearSketchStepAndRepeat）
   ⇒ 返回 True 但草图点仍 6 个、孔仍 1 个（换对象选点、强制重建都无效）
```

## 第 2 条为什么没做成

孔位草图里那个点**没有可用的参照实体**来标位置尺寸：
- 圆单独选中只能标**直径**（连做 8 次只落地 1 个尺寸）
- 草图内 `SelectByID2("Origin"/"" , "SKETCHPOINT")` 都回 `False`
- `fully_define_sketch` 回 True 但状态仍 2（其 docstring 自陈取值表未核实）

## 两处读数修正（本轮实测）

- `ISurface.IsCylinder` 是**属性**（bool），不是方法 ⇒ 之前圆柱面数恒为 0
- 该文档上 `SaveAs` 报「找不到成员」⇒ 用 `IModelDoc2.Save3`

## 判据

`HoleWzd` = 4 · 每个 `Standard` 含 `GB` · 实体 1 · 圆柱面 4
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "stage2" / "板1_rev-4.SLDPRT"

#: GB 标准与「螺钉间隙」的索引（真机 0..400 扫描命中，见文件头）
GB_STANDARD_INDEX = 13
GB_FASTENER_INDEX = 356
#: 孔心（毫米）
HOLES = ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0))
M6_CLEARANCE_MM = 6.6


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（首件重建 · 唯一入口）
# 文件:   tools/build_first_part.py
# 定位:   重建首件孔系为 **GB 标准**（旧件是 ANSI Metric）；单特征多孔位与孔位全约束两条
#          仍未解决，原因与三次失败证据写在本文件头部。
# 官方依据: IFeatureManager.HoleWizard5 · IHoleStandardsData.GetHoleStandards（GB=13）·
#          ISurface.IsCylinder（**属性**）· IModelDoc2.Save3 ·
#          IFeatureManager.FeatureLinearPattern5 · ISketchManager.CreateLinearSketchStepAndRepeat
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    import shutil
    import time

    import sw_connect as c_
    from sw_connect import get_com_member as g
    from sw_hole_features import create_hole_wizard_at_point_report
    from sw_part import feature_delete

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
        ok, doc = c_.try_call(c_.open_document, sw, str(DEST))
        if not ok or doc is None:
            print("★ 打不开")
            return 1
        doc = g(sw, "ActiveDoc") or doc
        print("① 副本 %s" % DEST.name)

        old = _feat(doc, "HoleWzd")
        for nm in old:
            c_.try_call(feature_delete, doc, nm)
        print("② 旧孔 %d → %d" % (len(old), len(_feat(doc, "HoleWzd"))))
        if _feat(doc, "HoleWzd"):
            return 1

        #: ③ 逐点建 4 个 GB 孔
        for (hx, hy) in HOLES:
            c_.try_call(
                lambda: create_hole_wizard_at_point_report(
                    doc, hx, hy, 10.0, "M6",
                    diameter_mm=M6_CLEARANCE_MM, depth_mm=20.0, through=True,
                    fastener_index=GB_FASTENER_INDEX,
                    standard_index=GB_STANDARD_INDEX,
                )
            )
        holes = _feat(doc, "HoleWzd")
        print("③ GB 孔 %d 个 %s" % (len(holes), holes))

        #: ④ 回读标准（不信返回值）
        gb_all = True
        for nm in holes:
            okf, f = c_.try_call(g, doc, "FeatureByName", nm)
            if not (okf and f is not None):
                gb_all = False
                continue
            d = g(f, "GetDefinition")
            std = str(g(d, "Standard"))
            print("   %s 标准=%s 类型=%s 规格=%s"
                  % (nm, std, g(d, "FastenerType"), g(d, "FastenerSize")))
            gb_all = gb_all and ("GB" in std)

        n_body = _body_count(doc)
        n_cyl = _cylinder_count(doc)
        print("④ 实体 %d · 圆柱面 %d" % (n_body, n_cyl))

        rows = _sketch_status(doc)
        bad = [r for r in rows if r[1] != 3]
        print("⑤ 草图 %d 张 · 非全定义 %d %s" % (len(rows), len(bad), bad))

        ok_save, _ = c_.try_call(doc.Save3, 1, c_.out_i4(), c_.out_i4())
        print("⑥ 存盘 ok=%s" % ok_save)

        good = (len(holes) == 4 and gb_all and n_body == 1 and n_cyl == 4)
        print("★ %s" % ("孔标准=GB 已达标（单特征/全约束两条仍未解决）"
                        if good else "未达判据"))
        return 0 if good else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def _feat(doc, type_name: str) -> list:
    from sw_connect import get_com_member as g

    out = []
    f = g(doc, "FirstFeature")
    while f is not None:
        if str(g(f, "GetTypeName2") or "") == type_name:
            out.append(str(g(f, "Name") or ""))
        f = g(f, "GetNextFeature")
    return out


def _body_count(doc) -> int:
    from sw_connect import get_com_member as g

    return len(list(g(doc, "GetBodies2", 0, False) or ()))


def _cylinder_count(doc) -> int:
    """数圆柱面 —— ★ `IsCylinder` 是**属性**（bool），不是方法。"""
    from sw_connect import get_com_member as g

    bodies = list(g(doc, "GetBodies2", 0, False) or ())
    if not bodies:
        return -1
    faces = g(bodies[0], "GetFaces") or ()
    n = 0
    for face in list(faces):
        surf = g(face, "GetSurface")
        if surf is None:
            continue
        try:
            n += 1 if bool(surf.IsCylinder) else 0
        except Exception:  # noqa: BLE001
            pass
    return n


def _sketch_status(doc) -> list:
    """每张草图（含特征子草图）的求解状态 → [(名字, 状态)]。"""
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
                rows.append((str(g(feat, "Name") or ""), st))
            sub = g(feat, "GetFirstSubFeature")
            while sub is not None:
                stack.append(sub)
                sub = g(sub, "GetNextSubFeature")
        f = g(f, "GetNextFeature")
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
