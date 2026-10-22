r"""@brief 探针：核「刚建的草图」到底建了几个 —— ★★ **三种数法对照，暴露位置枚举滞后一格**。

## 为什么要有这个探针
Spec Kit `070`（轮 151）我用 **`FeatureByPositionReverse`** 数草图，得到「只留下 1 个」，
并据此把 `InsertCompositeCurve` 的 `False` 定性为「前提未满足、**属应然**」。
Spec Kit `071`（轮 152）用**三种独立数法**核对 ⇒ **那个结论是测量假象**：
```
树总数            : 18 → 19 → 20 → 21        ★ 每轮 +1 ⇒ 都建了
按名查 FeatureByName: 草图1 → 草图2 → 草图3     ★ 都查得到
活动 ActiveSketch  : 草图1 / 草图2 / 草图3
⚠ FeatureByPositionReverse: [] → ['草图1'] → ['草图2','草图1']   ← **滞后一格**
```
⇒ ★ **本探针就是那次对照的固化版**（可复跑）。

## ⚠ 安全
**只在新零件上跑**、不改用户文档；收尾**关件不保存** + **查模态框**（走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/probe_sketch_enumeration_lag.py
# 定位:   给已知事实 92 提供可复跑的证据（三种数法对照）。
# 官方依据: `IModelDoc2.FeatureByPositionReverse` / `IFeatureManager` / `FeatureByName` 
#           /
#          `ISketchManager.ActiveSketch`（见 `C:\swapi\types\` 对应 md）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "sketch-enumeration-lag.json")
def snapshot(doc, sw_connect) -> dict:
    """同一时刻用**三种独立方式**看「草图在不在」。"""
    by_pos = []
    try:
        n = int(doc.GetFeatureCount)
        for k in range(1, n + 1):
            f = doc.FeatureByPositionReverse(k)
            if f is not None and str(f.Name).startswith(("草图", "Sketch")):
                by_pos.append(str(f.Name))
    except Exception as exc:      # noqa: BLE001
        by_pos = ["ERR:%s" % str(exc)[:30]]
    by_name = []
    for nm in ("草图1", "草图2", "草图3", "草图4"):
        try:
            if doc.FeatureByName(nm) is not None:
                by_name.append(nm)
        except Exception:      # noqa: BLE001
            pass
    try:
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        act = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        act = str(sw_connect.safe_get_com_member(act, "Name")) if act is not None else None
    except Exception:      # noqa: BLE001
        act = "EXC"
    return {"by_position": by_pos, "by_name": by_name, "active": act,
            "tree_total": int(doc.GetFeatureCount)}


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
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        ev["steps"].append({"tag": "新建", **snapshot(doc, sw_connect)})
        for i in range(3):
            sw_part.start_sketch(doc)
            ev["steps"].append({"tag": "第%d轮 start_sketch" % (i + 1),
                                **snapshot(doc, sw_connect)})
            y = float(i) * 30.0
            sw_part.sketch_line(doc, -20.0, y, 20.0, y)
            ev["steps"].append({"tag": "第%d轮 画线后" % (i + 1),
                                **snapshot(doc, sw_connect)})
            sw_part.end_sketch(doc)
            ev["steps"].append({"tag": "第%d轮 end_sketch" % (i + 1),
                                **snapshot(doc, sw_connect)})
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    print("  ── 三种数法对照（★ 看 `by_position` 与 `by_name` 的差）──")
    lag_seen = False
    for s in ev["steps"]:
        print("     %-22s 位置枚举=%-18s 按名查=%-26s 活动=%-8s 树总数=%d"
              % (s["tag"], str(s["by_position"]), str(s["by_name"]),
                 str(s["active"]), s["tree_total"]))
        if len(s["by_position"]) < len(s["by_name"]):
            lag_seen = True
    ev["lag_observed"] = lag_seen
    print()
    print("  ★ **滞后一格**观测到: %s" % lag_seen)
    if lag_seen:
        print("  ⇒ 核对「建了几个」请用 **按名查**（`FeatureByName`）或**总数变化**，")
        print("     不要只用 `FeatureByPositionReverse`。")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if (lag_seen and not ev.get("error")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
