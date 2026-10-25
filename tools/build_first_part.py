"""★ 首件重建（唯一入口）：**4 个圆 + 两向尺寸 + 半径 + 一次 HoleWizard(GB)**。

## 要修的三个缺陷（业主 2026-10-26）

| 缺陷 | 旧件 | 本工具 |
|---|---|---|
| 孔特征数 | 4 个 `HoleWzd` | **1 个**，含 4 个孔位 |
| 孔位约束 | 4 张草图状态 2（可拖） | 每圆 X/Y/半径都定 ⇒ 状态 3 |
| 孔标准 | `ANSI Metric` | **GB**（Toolbox 索引 13） |

## 为什么用**圆**而不是点（第 74 轮实测）

```
圆   AddDimension → CDispatch（建得出尺寸）
裸点 AddDimension → None（SW 无法把孤立点标成尺寸）
```
⇒ 孔位用圆；Hole Wizard 同样接受圆作为孔位。

## 全程用本仓封装

| 步骤 | 封装 |
|---|---|
| 删旧孔 | `sw_part.feature_delete` |
| 进草图 | `sw_part.start_sketch` |
| 画圆 | `sw_part.sketch_circle` |
| 加尺寸 | `sw_sketch_dimensions.add_dimension`（**第 4 参 Direction 已封进封装**） |
| 一个特征多孔位 | `sw_hole_features.create_hole_wizard_multi_point` |
| 量包围盒 | `sw_feature_readback.solid_body_extent_mm` |

## 读法

每步打印**独立读数**：圆数、尺寸数、草图状态、孔特征数、标准。
状态不是 3 就**不往下走**（避免又造出一个「看起来成了」的半成品）。
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
HOLE_R = 3.0
#: 本机实测：Toolbox `GetHoleStandards` 里 GB = 13
GB_STANDARD_INDEX = 13
M6_CLEARANCE_MM = 6.6


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（首件重建 · 唯一入口）
# 文件:   tools/build_first_part.py
# 定位:   重建首件孔：4 个**全约束**的圆 + **一个** HoleWizard(GB) 特征。
#          起因：业主 2026-10-26 指出四个孔特征不优雅、孔位未两向约束、标准用了 ANSI Metric。
# 官方依据: IModelDocExtension.AddDimension（**4 参**，第 4 参 Direction）·
#          ISketchManager.CreateCircleByRadius / HoleWizard5 ·
#          IModelDoc2.EditDelete · IHoleStandardsData.GetHoleStandards（GB=13）·
#          IModelDocExtension.SaveAs（6 参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    import shutil
    import threading
    import time

    import sw_connect as c_
    from sw_connect import get_com_member as g
    from sw_feature_readback import solid_body_extent_mm
    from sw_hole_features import create_hole_wizard_multi_point
    from sw_part import feature_delete, sketch_circle, start_sketch
    from sw_sketch_dimensions import (
        SW_SMART_DIM_RIGHT,
        SW_SMART_DIM_UP,
        add_dimension,
    )

    #: ★ 尺寸命令会弹「修改」框；后台 ESC 线程负责点掉（本仓既有做法）
    try:
        import probe_e2_hole_dimension_link as _esc

        threading.Thread(target=_esc._esc_loop, daemon=True).start()
        print("① ESC 线程已起")
    except Exception:  # noqa: BLE001
        print("① ESC 线程没起（继续）")

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        #: ★ 不设 CommandInProgress：它会抑制「修改」框
        sw.CommandInProgress = False
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
        doc = g(sw, "ActiveDoc") or doc
        print("② 副本 %s" % DEST.name)

        #: ③ 删旧孔
        old = _holes(doc)
        for nm in old:
            c_.try_call(feature_delete, doc, nm)
        left = _holes(doc)
        print("③ 旧孔 %d → %d" % (len(old), len(left)))
        if left:
            return 1

        box = solid_body_extent_mm(doc)
        raw = [v * 1000.0 for v in (box.get("raw") or ())]
        if len(raw) < 6:
            print("★ 包围盒读不到")
            return 1
        lo_x, lo_y = raw[0], raw[1]

        #: ④ 建草图 + 4 个圆
        start_sketch(doc, "上视基准面")
        circles = []
        for (x_mm, y_mm) in HOLES:
            okc, circ = c_.try_call(
                sketch_circle, doc, x_mm - lo_x, y_mm - lo_y, HOLE_R
            )
            circles.append(circ if okc else None)
        print("④ 圆 %d/4 · 尺寸数=%s · 状态=%s"
              % (len([x for x in circles if x is not None]),
                 _dims(doc), _status(doc)))

        #: ⑤ 每圆两向位置尺寸
        for i, (circ, (x_mm, y_mm)) in enumerate(zip(circles, HOLES), 1):
            if circ is None:
                continue
            for (dx, dy, dirn, label) in (
                (6.0, 0.0, SW_SMART_DIM_RIGHT, "Right"),
                (0.0, 6.0, SW_SMART_DIM_UP, "Up"),
            ):
                doc.ClearSelection2(True)
                c_.try_call(circ.Select4, False, c_.create_empty_dispatch_variant())
                okd, dim = c_.try_call(
                    lambda: add_dimension(
                        doc, x_mm - lo_x + dx, y_mm - lo_y + dy, dirn
                    )
                )
                time.sleep(0.25)
                if not okd or dim is None:
                    print("   圆%d %s 尺寸**没建出来**" % (i, label))
        print("⑤ 加完位置尺寸：尺寸数=%s · 状态=%s" % (_dims(doc), _status(doc)))

        #: ⑥ 半径（第 1 个圆）
        doc.ClearSelection2(True)
        if circles[0] is not None:
            c_.try_call(circles[0].Select4, False, c_.create_empty_dispatch_variant())
            okr, dimr = c_.try_call(
                lambda: add_dimension(
                    doc, HOLES[0][0] - lo_x, HOLES[0][1] - lo_y - 8.0, SW_SMART_DIM_UP
                )
            )
            time.sleep(0.25)
            print("⑥ 半径尺寸：ok=%s 回=%s" % (okr, type(dimr).__name__))
        print("   加完半径：尺寸数=%s · 状态=%s" % (_dims(doc), _status(doc)))

        #: ⑦ 选 4 圆 → 一次 HoleWizard（GB）
        doc.ClearSelection2(True)
        sel = 0
        for circ in circles:
            if circ is None:
                continue
            oks, _ = c_.try_call(
                circ.Select4, False, c_.create_empty_dispatch_variant()
            )
            sel += 1 if oks else 0
        print("⑦ 选中圆 %d/4" % sel)

        ok_h, _ = c_.try_call(
            lambda: create_hole_wizard_multi_point(
                doc,
                "M6",
                diameter_mm=M6_CLEARANCE_MM,
                depth_mm=20.0,
                through=True,
                standard_index=GB_STANDARD_INDEX,
            )
        )
        print("⑧ HoleWizard5(GB) ok=%s" % ok_h)

        got = _holes(doc)
        print("⑨ 孔特征 %d 个" % len(got))
        for name in got:
            okf, f = c_.try_call(g, doc, "FeatureByName", name)
            if okf and f is not None:
                d = g(f, "GetDefinition")
                try:
                    print("   %s 标准=%s 规格=%s"
                          % (name, g(d, "Standard"), g(d, "FastenerSize")))
                except Exception:  # noqa: BLE001
                    print("   %s（属性读不到）" % name)

        rows = _sketch_rows(doc)
        bad = [r for r in rows if r["status"] != 3]
        print("⑩ 草图 %d 张 · 非全定义 %d 张 %s"
              % (len(rows), len(bad), [(r["name"], r["status"]) for r in bad]))
        return 0 if (len(got) == 1 and not bad) else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def _dims(doc):
    from sw_sketch_dimensions import count_sketch_dimensions

    r = _tc(count_sketch_dimensions, doc)
    return r[1] if isinstance(r, tuple) and len(r) > 1 else None


def _status(doc):
    last = None
    f = _g(doc, "FirstFeature")
    while f is not None:
        if str(_g(f, "GetTypeName2") or "") == "ProfileFeature":
            last = f
        f = _g(f, "GetNextFeature")
    if last is None:
        return None
    ok, sk = _tc(_g, last, "GetSpecificFeature2")
    if not ok or sk is None:
        return None
    ok2, v = _tc(lambda: int(sk.GetConstrainedStatus))
    return v if ok2 else None


def _holes(doc) -> list:
    out = []
    f = _g(doc, "FirstFeature")
    while f is not None:
        if str(_g(f, "GetTypeName2") or "") == "HoleWzd":
            out.append(str(_g(f, "Name") or ""))
        f = _g(f, "GetNextFeature")
    return out


def _sketch_rows(doc) -> list:
    rows = []
    f = _g(doc, "FirstFeature")
    while f is not None:
        stack = [f]
        while stack:
            feat = stack.pop()
            if str(_g(feat, "GetTypeName2") or "") == "ProfileFeature":
                ok, sk = _tc(_g, feat, "GetSpecificFeature2")
                st = None
                if ok and sk is not None:
                    ok2, v = _tc(lambda: int(sk.GetConstrainedStatus))
                    st = v if ok2 else None
                rows.append({"name": str(_g(feat, "Name") or ""), "status": st})
            sub = _g(feat, "GetFirstSubFeature")
            while sub is not None:
                stack.append(sub)
                sub = _g(sub, "GetNextSubFeature")
        f = _g(f, "GetNextFeature")
    return rows


def _g(obj, name):
    from sw_connect import get_com_member as _gcm

    return _gcm(obj, name)


def _tc(*args, **kwargs):
    from sw_connect import try_call

    return try_call(*args, **kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
