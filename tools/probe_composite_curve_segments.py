r"""@brief 探针：**回读着 mark 计数**去选 2 个草图实体，再试 `InsertCompositeCurve`。

## 为什么要这样做（轮 152/153/154 的纪律）
```
轮 153：拿 `SelectByID2` 的 `True` 当"选中了" ⇒ 实际计数 0 ⇒ **否定了功能却没验前提**
轮 154：判别实验证明 **mark 能落上、读法也对**；真因是 **`SelectByID2` 的 bool 不可信**（事实 94）
⇒ 本轮：**每一次选完都回读** `GetSelectedObjectCount2(mark)`，**只有计数对了才去调功能**
```

## 候选（逐个试，**用计数当门**）
```
① 草图**整体** × 2（官方示例原样）：已试过 ⇒ False
② 实体**边** × 2（`Select4`，计数 2）：已试过 ⇒ False
③ ★ **草图实体**（`SKETCHSEGMENT`）× 2 —— **本轮的新候选**
   在草图编辑态里用 `ISketch.GetSketchSegments()` 取对象引用（退出后仍可用）
   ⇒ 用 `Select4` 选，并回读计数
④ ★ **`SelectByID2` + mark=1**（按段名，若名字可用）⇒ 回读 `GetSelectedObjectCount2(1)`
```

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**（走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_composite_curve_segments.py
# 定位:   给 Spec Kit `074` 取「**前提真的满足了**之后，`InsertCompositeCurve` 成不成
#           」的证据。
# 官方依据: `IModelDoc2.InsertCompositeCurve`（Remarks：`SelectByID2` + mark 1）·
#          `ICompositeCurveFeatureData.GetEntitiesToJoinCount` · `ISketch.GetSketchSegments`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "composite-curve-segments.json"
)


def count(doc, sw_connect, mark=-1):
    try:
        sel = sw_connect.safe_get_com_member(doc, "SelectionManager")
        return int(sw_connect.safe_get_com_member(sel, "GetSelectedObjectCount2", mark))
    except Exception as exc:  # noqa: BLE001
        return "EXC:%s" % str(exc)[:30]


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "trials": []}
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_part, sw_sketch

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: ── 造一个含 **2 条分离直线** 的草图，并在**编辑态**里取段的对象引用 ──
        sw_part.start_sketch(doc)
        sw_part.sketch_line(doc, -20.0, 0.0, 20.0, 0.0)
        sw_part.sketch_line(doc, -20.0, 20.0, 20.0, 20.0)
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        segs = sw_sketch.get_sketch_segments(sk)
        segs = list(segs) if isinstance(segs, list) else []
        print("  草图编辑态里取到段数 = %d" % len(segs))
        ev["segment_count"] = len(segs)

        #: 试 `SelectByID2` 的名字（编辑态里先看段有没有名字 —— **不猜，问回来**）
        names = []
        for i, s in enumerate(segs[:2]):
            try:
                nm = sw_connect.safe_get_com_member(s, "GetID")
            except Exception:  # noqa: BLE001
                nm = None
            names.append(nm)
        ev["segment_ids"] = [str(n) for n in names]
        print("  段上的 `GetID` = %s（用于判断有没有可用的名字）" % ev["segment_ids"])

        sw_part.end_sketch(doc)
        callout = sw_part._empty_callout()

        #: ── 候选③：按**对象** `Select4` 选 2 段 ──
        doc.ClearSelection2(True)
        n_ok = 0
        for s in segs[:2]:
            try:
                if s.Select4(True, callout):
                    n_ok += 1
            except Exception as exc:  # noqa: BLE001
                print("     ⚠ Select4 异常: %s" % str(exc)[:60])
        c_all = count(doc, sw_connect, -1)
        print(
            "  ③ 按对象选 2 段 ⇒ 返回真 %d 次 · **回读计数(-1)** = %s" % (n_ok, c_all)
        )
        ev["trials"].append(
            {"way": "Select4 x2 segments", "returned": n_ok, "count": c_all}
        )

        #: ── 只有计数对了才去调功能（**这一步是本轮的纪律**）──
        if c_all == 2:
            try:
                sw_part.insert_composite_curve(doc)
                ev["result"] = "success_segments"
                print("  ★★ **成功**（选 2 个草图实体）")
            except Exception as exc:  # noqa: BLE001
                ev["result"] = "false_segments"
                print("  ✗ 仍失败：%s" % str(exc)[:110])
        else:
            ev["result"] = "premise_not_met"
            print(
                "  ⚠ 计数 %s ≠ 2 ⇒ **前提没满足，不去调功能**（不当成功能失败）" % c_all
            )

        #: ── 候选④：`SelectByID2` + **mark=1**（按段名，若名字可用）──
        doc.ClearSelection2(True)
        picked = 0
        for nm in ev["segment_ids"]:
            if not nm or nm in ("None", "0"):
                continue
            for typ in ("SKETCHSEGMENT", "EXTSKETCHSEGMENT", "SKETCH"):
                try:
                    if doc.Extension.SelectByID2(nm, typ, 0, 0, 0, True, 1, callout, 0):
                        picked += 1
                        break
                except Exception:  # noqa: BLE001
                    pass
        c1 = count(doc, sw_connect, 1)
        c_all2 = count(doc, sw_connect, -1)
        print(
            "  ④ 按段名 + mark=1 ⇒ 命中 %d · **回读计数(1)** = %s · (-1) = %s"
            % (picked, c1, c_all2)
        )
        ev["trials"].append(
            {
                "way": "SelectByID2 name mark=1",
                "returned": picked,
                "count_mark1": c1,
                "count_all": c_all2,
            }
        )
        if c_all2 == 2 and ev.get("result") in (None, "premise_not_met"):
            try:
                sw_part.insert_composite_curve(doc)
                ev["result"] = "success_by_name"
                print("  ★★ **成功**（按段名 + mark=1）")
            except Exception as exc:  # noqa: BLE001
                ev["result"] = "false_by_name"
                print("  ✗ 仍失败：%s" % str(exc)[:110])
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print(
        "  收尾：扫了 %d 个窗口 · %s"
        % (scanned, "无模态框" if not dialogs else dialogs)
    )
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
