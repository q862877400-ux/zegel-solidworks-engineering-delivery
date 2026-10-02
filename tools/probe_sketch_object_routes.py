r"""@brief 探针：**从 model 取「草图对象」的三条路**，以及关掉草图后哪条还活着。

## 为什么要有这个探针（2026-10-01 轮 220，砌墙阶段 A 的前置）
`scripts/sw_sketch.py` 有 **25 个公开函数没挂成工具**，而它们的首参**全是 `sketch`**
（一个 COM 对象）—— 不在既有注入点（`model` / `sw_app` / `study`）里。
⇒ 要挂它们，先得有一层「**从 model 取到 sketch 对象**」的包装。
★ 而**这个动作有三条候选路**，本探针在真机上把它们跑一遍，用结果决定选哪条：

| 路 | 取法 | 官方依据 |
|---|---|---|
| A | `model.GetActiveSketch2` | 官方示例 `Autodimension_a_Sketch_Example_VB.htm`：`Set swSketch = swModel.GetActiveSketch2` |
| B | `model.SketchManager.ActiveSketch` | 官方示例 `Constrain_Sketch_Example_CSharp.htm`：`swSketch = swSketchMgr.ActiveSketch` |
| C | `model.FeatureByName(名字)` → 由特征取 ISketch | 本项目既有 `sw_part` 的按名取法 |

⚠ **关键未知**：`ActiveSketch` 顾名思义只在**草图打开时**有效。
  若草图 `end_sketch` 之后 A/B 取不到 ⇒ ★ **包装层只能走 C（按名字取）** ——
   这正是本探针要回答的那一个问题（**先实测，再写工具**）。

## ⚠ 安全（照 `tools/probe_sketch_enumeration_lag.py` 的骨架）
**只在新零件上跑**、不改用户文档；`CommandInProgress` 抑制弹窗；
收尾**关件不保存**；产物落 `D:\AI\SW\output\`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/probe_sketch_object_routes.py
# 定位:   给「砌墙 A 第一批（草图只读工具）」定包装层的取法；产出 `output/sketch-object-routes.json`。
# 官方依据: `IModelDoc2.GetActiveSketch2` · `ISketchManager.ActiveSketch`
#          （见 `C:\swapi\` 与 `D:\AI\SW\AI Solidworks\官方文档\` 的两处官方示例）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
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

OUT = Path(r"D:\AI\SW\output\sketch-object-routes.json")


def _name_of(sw_connect, obj):
    """尽力取对象的 Name；取不到就回 None（不编）。"""
    try:
        return str(sw_connect.safe_get_com_member(obj, "Name")) if obj is not None else None
    except Exception:                                          # noqa: BLE001
        return None


def probe(doc, sw_connect, sketch_name: str) -> dict:
    """三条路各试一次，返回读数。"""
    out: dict = {}
    skm = sw_connect.safe_get_com_member(doc, "SketchManager")
    #: A · GetActiveSketch2
    try:
        a = sw_connect.safe_get_com_member(doc, "GetActiveSketch2")
        out["A_GetActiveSketch2"] = _name_of(sw_connect, a)
    except Exception as exc:                                   # noqa: BLE001
        out["A_GetActiveSketch2"] = "EXC:%s" % str(exc)[:40]
    #: B · SketchManager.ActiveSketch
    try:
        b = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        out["B_ActiveSketch"] = _name_of(sw_connect, b)
    except Exception as exc:                                   # noqa: BLE001
        out["B_ActiveSketch"] = "EXC:%s" % str(exc)[:40]
    #: C · 按特征名取
    try:
        feat = doc.FeatureByName(sketch_name)
        if feat is None:
            out["C_FeatureByName"] = None
        else:
            sk = sw_connect.safe_get_com_member(feat, "GetSpecificFeature2")
            out["C_FeatureByName"] = _name_of(sw_connect, sk) or "(取到对象但 Name 读不到)"
            out["C_got_object"] = sk is not None
    except Exception as exc:                                   # noqa: BLE001
        out["C_FeatureByName"] = "EXC:%s" % str(exc)[:40]
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
        except Exception:                                      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: 建一个已知草图：1 条线 + 1 个圆（=1 段） + 1 个矩形（=4 条线）
        sw_part.start_sketch(doc)
        sw_part.sketch_line(doc, -20.0, 0.0, 20.0, 0.0)
        sw_part.sketch_circle(doc, 0.0, 20.0, 5.0)
        ev["steps"].append({"tag": "草图打开中（画了线+圆）",
                            "sketch_name": sw_part.current_sketch_name(doc),
                            **probe(doc, sw_connect, sw_part.current_sketch_name(doc))})
        name = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        ev["steps"].append({"tag": "草图已关闭（★ 关键读点）",
                            "sketch_name": name, **probe(doc, sw_connect, name)})

        #: 再开一个草图，看"重开"时的读数（多草图场景）
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, -10.0, -10.0, 10.0, 10.0)
        n2 = sw_part.current_sketch_name(doc)
        ev["steps"].append({"tag": "第二个草图打开中", "sketch_name": n2,
                            **probe(doc, sw_connect, n2)})
        sw_part.end_sketch(doc)
        ev["steps"].append({"tag": "第二个草图已关闭", "sketch_name": n2,
                            **probe(doc, sw_connect, n2)})
        ev["sketch_names"] = [name, n2]
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    print("  ── 三条路对照（★ 重点看「草图已关闭」那两行）──")
    for s in ev["steps"]:
        print("     %-24s A(GetActiveSketch2)=%-14s B(ActiveSketch)=%-14s C(按名)=%s"
              % (s["tag"], s.get("A_GetActiveSketch2"), s.get("B_ActiveSketch"),
                 s.get("C_FeatureByName")))
    print()
    closed = [s for s in ev["steps"] if "已关闭" in s["tag"]]
    if closed:
        a_ok = any(s.get("A_GetActiveSketch2") for s in closed)
        b_ok = any(s.get("B_ActiveSketch") for s in closed)
        c_ok = any(s.get("C_got_object") for s in closed)
        print("  ★ 草图**关闭后**还能取到对象吗：")
        print("     A GetActiveSketch2 : %s" % ("能" if a_ok else "**不能**"))
        print("     B ActiveSketch     : %s" % ("能" if b_ok else "**不能**"))
        print("     C 按名取           : %s" % ("能" if c_ok else "**不能**"))
        print("  ⇒ 包装层应选：%s" % ("C（按名取）" if (c_ok and not a_ok and not b_ok)
                                     else "见上面读数"))
        ev["usable_after_close"] = {"A": a_ok, "B": b_ok, "C": c_ok}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
