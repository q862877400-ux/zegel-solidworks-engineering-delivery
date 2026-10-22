r"""@brief 真机证据：**载荷族 4 个工具**（24h 段 2.1 / Spec Kit `143` 的验收②）。

## 判据（★ 按 `AGENTS.md` §5.0：**先在自家仓库找** —— 找到就照用，不新搓）
```
★ 来源：`tools/capture_simulation_loads_evidence.py` 的判据表（**本项目自己写的**）：
    「夹具 / 载荷 | **选区计数 = 1** 且 `LoadsAndRestraintsManager.Count == 2`」
⇒ 本脚本对**四类载荷各施一次**，每次断言 ★ **`Count` 恰好 +1**（★ 回读，不看返回对象）。
★ 四家开源项目的测试里**没有**载荷判据（W7 已核实）⇒ ★ **找过了，没有**。
```

## ⚠ 本批**不调** `RunAnalysis` / `CreateMesh` ⇒ ★ **没有模态框挂起风险**
```
★ 会弹框的只有那两步（known-facts 174/177）；本脚本只**建载荷** ⇒ 可在普通进程跑。
```

## 四类载荷各自的选面注意
```
★ `add_pressure(manager, entities, …)` / `add_torque(manager, entities, …)` ⇒ 要 **DispArray**（可多面）
★ `add_gravity(manager, entity)` / `add_centrifugal_force(manager, entity)` ⇒ 要 **单实体**
  ⇒ ★ 能力层的包装取选区里**第一个**（★ 已在 docstring 写明）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_loadfamily_evidence.py
# 定位:   Spec Kit `143` 的**验收②**：产出 `output/loadfamily-evidence.json`。
# 官方依据: `ICWLoadsAndRestraintsManager.AddPressure` / `AddForce` / `AddGravity` /
#          `AddCentriFugalForce`（见 `scripts/sw_simulation_loads.py` 的来源块）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "loadfamily-evidence.json")
STUDY = "DSH-143"


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "simulation_load_family",
        "★": "★ 判据沿用本项目既有脚本：Count 恰好 +1（回读，不看返回对象）",
        "steps": {},
    }
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        import tool_specs_batch29 as b29

        from scripts import sw_part
        from scripts import sw_simulation as sim
        from scripts import sw_simulation_loads as l

        #: ① 核 4 个工具声明解析得到（★ 静态那一半）
        bindings = {}
        for spec in b29.SPECS_BATCH29:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {
                "resolved": callable(getattr(mod, spec.function, None)),
                "inject": spec.inject,
            }
        ev["steps"]["bindings"] = {
            "ok": all(v["resolved"] for v in bindings.values()),
            "count": len(bindings),
            "detail": bindings,
        }
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ② 造零件 + 材料 + 研究
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)

        #: ⚠ 先自报零件尺寸与文档单位（★ 上一批在这两处吃过亏 —— known-facts 180）
        try:
            bb = sw_part.get_bounding_box(doc)
            ev["steps"]["part_size_mm"] = [
                round(float(x), 2) for x in (bb or {}).get("size", [])
            ]
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["part_size_mm"] = "取不到: %s" % str(exc)[:60]

        sim.set_material(doc, "AISI 1020")
        ev["steps"]["material"] = str(
            sw_connect.safe_get_com_member(doc, "MaterialIdName") or ""
        )
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(study)

        #: ③ ★ 四类载荷各施一次（每次**先清选区**，避免上一轮的选择残留）
        results = []

        def _apply(label: str, fn):
            """选一个面 ⇒ 施加载荷 ⇒ 记**回读报告**。"""
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            sim.select_face_at(doc, 0.0, 0.0, 0.0)  #: 顶面
            r = fn()
            r["label"] = label
            results.append(r)
            print(
                "    %-20s ok=%s  Count %s→%s  err=%s"
                % (
                    label,
                    r.get("ok"),
                    r.get("count_before"),
                    r.get("count_after"),
                    (r.get("error") or "")[:60],
                )
            )
            return r

        _apply("pressure", lambda: l.apply_pressure_report(mgr, doc))
        _apply("torque", lambda: l.apply_torque_report(mgr, doc))
        _apply("gravity", lambda: l.apply_gravity_report(mgr, doc))
        _apply("centrifugal_force", lambda: l.apply_centrifugal_force_report(mgr, doc))

        ev["steps"]["loads"] = results
        ev["steps"]["final_count"] = l._loads_count(mgr)
        n_ok = sum(1 for r in results if r.get("ok"))
        ev["steps"]["verdict_judgement"] = {
            "applied_ok": n_ok,
            "of": len(results),
            "final_count": ev["steps"]["final_count"],
            "★": "★ 四类各 +1 ⇒ final_count 应为 4；每条 ok 由 count_after == count_before + 1 判定",
        }
        ok = ok and n_ok == len(results) and ev["steps"]["final_count"] == len(results)
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ok = False
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
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 载荷族（4 类）真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-20s %s" % (k, json.dumps(v, ensure_ascii=False)[:220]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
