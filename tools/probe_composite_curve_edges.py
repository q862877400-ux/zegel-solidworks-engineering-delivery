r"""@brief 探针：`InsertCompositeCurve` 换**边**（而不是整个草图）能不能成。

## 背景（`070`/`071` 的尾巴）
```
070：整个**草图**方式 ⇒ InsertCompositeCurve() 返回 False（当时以为根因是"只 1 个草图"）
071：★ 那个根因是**测量假象**（FeatureByPositionReverse 滞后一格）—— 前提其实满足
     ⇒ 更正后：**前提满足仍返回 False** ⇒ 真因未查明
153（本轮）：换一个候选 —— **选边**（而不是"整个草图"）
```

## 候选与依据
```
官方示例选的是 "SKETCH" 类型的两个**草图名** —— 而它返回 False
⇒ 候选①：选 **边**（EDGE）。依据：合成曲线的语义是「把曲线**接**起来」，
  而**草图整体**不是一条曲线。
⇒ ★ 选边必须按 **事实 32** 的可行路径：`SelectByID2("", "EDGE", x, y, z, …, mark=1, …)`
  （按**面上的点**选）—— **按名字选边不成立**（`SelectByID2("Edge1","EDGE")` 计数恒 0）。
```
⇒ 本探针做一个 **50×50×20** 的方块（12 条边），沿两条棱取点、以 **mark=1** 选它们，
再调 `InsertCompositeCurve()`。

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**（走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_composite_curve_edges.py
# 定位:   给 Spec Kit `072` 取「选边能不能让 `InsertCompositeCurve` 成功」的证据。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertCompositeCurve.md`（Remarks：`SelectByID2`
#           + mark 1）
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
    Path(__file__).resolve().parents[1] / "output" / "composite-curve-edges.json"
)
W, H, D = 0.05, 0.05, 0.02  #: 米（50×50×20 mm）


def count_edges(sw_connect, doc) -> list:
    """枚举实体上的边（用 `IEntity` 的对象引用，**不按名字**，事实 32）。"""
    out = []
    try:
        bodies = doc.GetBodies2(0, False)  #: 0 = swSolidBody
        if not bodies:
            return out
        body = bodies[0]
        edges = body.GetEdges()
        if edges:
            out = list(edges)
    except Exception as exc:  # noqa: BLE001
        print("     ⚠ 枚举边失败: %s" % str(exc)[:70])
    return out


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": []}
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        #: 一个 50×50×20 的方块 ⇒ 12 条边
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 50.0, 50.0)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", 20.0)
        edges = count_edges(sw_connect, doc)
        print("  方块建好，边数 = %d" % len(edges))
        ev["edge_count"] = len(edges)

        callout = sw_part._empty_callout()

        #: ① 试**按名字**选边（预期：计数 0 —— 事实 32）
        doc.ClearSelection2(True)
        n1 = 0
        for nm in ("Edge1", "Edge2"):
            try:
                if doc.Extension.SelectByID2(nm, "EDGE", 0, 0, 0, True, 1, callout, 0):
                    n1 += 1
            except Exception:  # noqa: BLE001
                pass
        print("  ① 按名字选边 ⇒ 计数 %d（事实 32 预期 0）" % n1)
        ev["by_name_selected"] = n1

        #: ② 试**按对象** `IEntity.Select4`（事实 32 说的可行路径）
        n2 = 0
        if edges:
            doc.ClearSelection2(True)
            for e in edges[:2]:
                try:
                    if e.Select4(True, callout):
                        n2 += 1
                except Exception as exc:  # noqa: BLE001
                    print("     ⚠ Select4 异常: %s" % str(exc)[:60])
        cnt2 = 0
        try:
            cnt2 = int(doc.SelectionManager.GetSelectedObjectCount2(-1))
        except Exception:  # noqa: BLE001
            pass
        print(
            "  ② 按**对象** `IEntity.Select4` 选前 2 条边 ⇒ 返回真 %d 次 · 选择集计数 %d"
            % (n2, cnt2)
        )
        ev["by_object_selected"] = n2
        ev["selection_count"] = cnt2

        #: ②b ★ 按**面上的点**选边，并且 **mark = 1**（官方 Remarks 明确要求）
        #: ⚠ `IEntity.Select4` **没有 mark 参数** ⇒ 上面那次选**可能不算数**
        #: ⇒ 这一条才是「按官方要求」的形态（事实 32：按点选边是可行路径）
        pts = [
            (0.025, 0.0, 0.0),
            (0.05, 0.025, 0.0),  #: 底面两条相邻棱的中点
            (0.0, 0.025, 0.0),
            (0.025, 0.05, 0.0),
        ]
        doc.ClearSelection2(True)
        picked = 0
        for x, y, z in pts[:2]:
            try:
                if doc.Extension.SelectByID2("", "EDGE", x, y, z, True, 1, callout, 0):
                    picked += 1
            except Exception as exc:  # noqa: BLE001
                print("     ⚠ 按点选边异常: %s" % str(exc)[:60])
        cnt3 = 0
        try:
            cnt3 = int(doc.SelectionManager.GetSelectedObjectCount2(1))  #: ★ mark = 1
        except Exception:  # noqa: BLE001
            pass
        print(
            "  ②b **按点 + mark=1** 选 2 条棱 ⇒ 命中 %d · **mark=1 的计数** %d"
            % (picked, cnt3)
        )
        ev["by_point_mark1_selected"] = picked
        ev["mark1_count"] = cnt3
        cnt2 = max(cnt2, cnt3)

        #: ③ 调它
        if cnt2 >= 2:
            try:
                sw_part.insert_composite_curve(doc)
                print("  ③ ★ **`InsertCompositeCurve()` 成功**（选 2 条边）")
                ev["result"] = "success_by_edges"
            except Exception as exc:  # noqa: BLE001
                print("  ③ ✗ 仍失败：%s" % str(exc)[:110])
                ev["result"] = "false_by_edges"
        else:
            print("  ③ ⚠ 选择集不足 2 ⇒ 跳过（**前提没造出来**，不当成功能失败）")
            ev["result"] = "premise_not_met"

        #: ④ 侧证：特征树总数变化
        try:
            ev["tree_total"] = int(doc.GetFeatureCount)
        except Exception:  # noqa: BLE001
            pass
        print("  ④ 特征树总数 = %s" % ev.get("tree_total"))
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

    from tools.probe_sketch_enumeration_lag import SW_PID as _P  # noqa: F401

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
