r"""@brief 探针：`default_element_size_and_tolerance` 的 **`units` 口径** —— 父进程 vs 子进程。

## ★★★ 要回答的问题（"跑求解必挂"的根因候选）
```
★ 既有脚本（能跑通）用 `default_element_size_and_tolerance(study, **-1**)` ⇒ 文档里记着
  「对本机 100×60×20 mm 的板是 **4.9339 / 0.2467**」（**毫米**级）。
★ 而我的链经**子进程隔离**调 `mesh_size_by_name(STUDY, units=-1)` ⇒ 得到 **4930.5 / 246.5**
  ⇒ ★★ **正好 1000 倍**！
⇒ ★★★ 假设：**`units=-1` 的口径在子进程里与父进程不同**（或 -1 表示"用文档单位"，
   而两个进程看到的文档单位状态不同）。
⇒ ★★ 而**若 `element_size` 大了 1000 倍**，`CreateMesh` 拿到的就是 **4.9 米的单元**
   ⇒ ★★★ **网格退化 ⇒ 求解无解 ⇒ solver 卡住** —— ★ 那可能就是"跑求解必挂"的根因。
```

## 本探针测什么
```
① 在**父进程**里，对同一个 `study`，`units` 取 **-1 / 0 / 1 / 2** 各回什么；
② 在**子进程**里（经 `run_isolated`）同样取四个值 ⇒ ★ 对比两组数字；
③ ★ 顺便记下**零件包围盒**与**文档单位**（★ 用来判断"哪个值才是毫米"）。
```

## ⚠ 安全
**不调 `CreateMesh` / `RunAnalysis`**（★ 那两步才会弹框）· 只在新零件上跑 · 关件不保存。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_mesh_units.py
# 定位:   查清 `units` 口径（父/子进程差异）——"跑求解必挂"的根因候选；
#          产物 `output/mesh-units.json`。
# 官方依据: `ICWMesh.GetDefaultElementSizeAndTolerance`（★ 其 `units` 参数语义由本探针实测）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
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

OUT = Path(r"D:\AI\SW\output\mesh-units.json")
STUDY = "DSH-UNITS"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_isolate import run_isolated

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: 造 100×60×20 的板（★ 与既有脚本同一工况）+ 材料 + 研究
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)

        #: ③ 零件的真实尺寸（★ 用来判"哪个 units 才是毫米"）
        try:
            bb = sw_part.get_bounding_box(doc)
            ev["steps"]["part_size_mm"] = [round(float(x), 2) for x in (bb or {}).get("size", [])]
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["part_size_mm"] = "取不到: %s" % str(exc)[:60]

        #: ① 父进程：四个 units
        parent = {}
        for u in (-1, 0, 1, 2):
            try:
                size, tol = sim.default_element_size_and_tolerance(study, u)
                parent[str(u)] = {"element_size": float(size), "tolerance": float(tol)}
            except Exception as exc:                           # noqa: BLE001
                parent[str(u)] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:60])}
        ev["steps"]["parent"] = parent
        print("  [父进程] %s" % json.dumps(parent, ensure_ascii=False)[:300])

        #: ② 子进程（经隔离）：同样四个 units
        child = {}
        for u in (-1, 0, 1, 2):
            r = run_isolated("scripts.sw_simulation_worker", "mesh_size_by_name",
                             args=[STUDY], kwargs={"units": u}, timeout=60)
            child[str(u)] = ({"element_size": (r.get("result") or {}).get("element_size"),
                              "tolerance": (r.get("result") or {}).get("tolerance")}
                             if r.get("ok") else {"error": (r.get("error") or "")[:80]})
        ev["steps"]["child"] = child
        print("  [子进程] %s" % json.dumps(child, ensure_ascii=False)[:300])

        #: ★★ 判读：父与子是否一致？哪个 units 与零件尺度**同量级**（即"看起来是毫米"）
        def _magnitude(d: dict) -> dict:
            out = {}
            for k, v in d.items():
                es = v.get("element_size")
                out[k] = ("~%.1f" % es) if isinstance(es, (int, float)) else "?"
            return out
        size_mm = ev["steps"].get("part_size_mm")
        maxdim = max(size_mm) if isinstance(size_mm, list) and size_mm else None
        ev["steps"]["verdict"] = {
            "parent": _magnitude(parent), "child": _magnitude(child),
            "parent_child_same": {k: (parent.get(k, {}).get("element_size")
                                      == child.get(k, {}).get("element_size"))
                                  for k in parent},
            "part_max_dim_mm": maxdim,
            "★": ("★★ 若某 units 的值与零件尺度**同量级**（如 4.9 对 100）⇒ 那是「毫米」口径；"
                  "★ 若大 1000 倍（如 4930）⇒ 那是「米」口径被当成毫米用 ⇒ **传给 CreateMesh 会导致网格退化**"),
        }
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
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
                    sw.CloseDoc(t)                             #: ★ 关件不保存
        except Exception:                                      # noqa: BLE001
            pass

    print("  ── units 口径探针 ──")
    for k, v in ev["steps"].items():
        print("  %-16s %s" % (k, json.dumps(v, ensure_ascii=False)[:320]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
