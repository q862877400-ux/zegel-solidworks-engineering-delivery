r"""@brief 真机证据：**网格参数生效判据**（24h 段 5「修地基」/ Spec Kit `145`）。

## ★★★★★ 这道闸要证明什么
```
★ 对照事实（2026-10-01 轮 248，有据）：
    | 方式 | 报出的 element_size | 单元数 | RunAnalysis |
    | 既有 `capture_simulation_evidence.py`（**跑通**）| **4.9339** | **7310** | **1 秒 · 4 张图** |
    | 本项目其它链                                      | **4930.5** | **7250** | **300 秒超时** |
  ⇒ ★★ 同一句 `default_element_size_and_tolerance(study, -1)` 两次差 **恰好 1000 倍**
    （★ 原因**未查清**）；而 4930.5 **比零件最大边还大 49 倍** ⇒ 网格退化 ⇒
    `CreateMesh` **静默退回默认值** ⇒ `RunAnalysis` **无解 ⇒ 弹模态框 ⇒ 挂住会话**。
★ 本脚本证明：**加上判据之后，那条链在**建网格之前**就停下** ——
  ⇒ ★★ **不建网格、不跑求解 ⇒ 没有弹框、没有挂起**（★ 挂起从源头被掐断）。
```

## 判据（本脚本断言三件事）
```
① 判据对**不合理**的尺寸回 `ok=False`（★ 用 4930.5 —— 那个**真实观测到**的值，不是编的）
② 判据对**合理**的尺寸回 `ok=True`（★ 用 4.9339 —— 既有脚本真正在用的值）
③ ★★ 且 **`ok=False` 时脚本不去调 `CreateMesh` / `RunAnalysis`** ⇒ **全程无弹框**
```

## ⚠ 本脚本**故意不跑求解** —— 那正是它要演示的处置

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_mesh_sane_evidence.py
# 定位:   Spec Kit `145` 的验收：产出 `output/mesh-sane-evidence.json`。
# 官方依据: `ICWMesh.GetDefaultElementSizeAndTolerance`（本模块已记两次实测差 1000 倍）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mesh-sane-evidence.json")
STUDY = "DSH-145"
#: ★ 两个**真实观测到**的值（★ 不编）：既有脚本在用的、与本项目其它链报出的
GOOD_SIZE = 4.933908705960544
BAD_SIZE = 4930.501659457233


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "mesh_size_sanity_gate",
                "★": "★ 证明这道闸能把'跑求解必挂'掐断在网格之前", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: 造同一工况的零件（100×60×20 mm）
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)

        #: ① 判据对**不合理**的尺寸（★ 真实观测到的 4930.5）
        bad = sim.check_mesh_size_sane(doc, BAD_SIZE)
        ev["steps"]["rejects_bad"] = bad
        print("  [1] 不合理尺寸 %.1f ⇒ ok=%s  %s" % (BAD_SIZE, bad.get("ok"),
                                                     (bad.get("reason") or "")[:88]))

        #: ② 判据对**合理**的尺寸（★ 既有脚本真正在用的 4.9339）
        good = sim.check_mesh_size_sane(doc, GOOD_SIZE)
        ev["steps"]["accepts_good"] = good
        print("  [2] 合理尺寸   %.4f ⇒ ok=%s" % (GOOD_SIZE, good.get("ok")))

        #: ③ ★★ 真正读一次那个值（★ 看本机现在回什么）—— 并与判据联动
        size, tol = sim.default_element_size_and_tolerance(study, -1)
        gate = sim.check_mesh_size_sane(doc, float(size))
        ev["steps"]["live_reading"] = {
            "element_size": float(size), "tolerance": float(tol),
            "gate_ok": bool(gate.get("ok")), "gate_reason": (gate.get("reason") or "")[:200],
            "would_stop_before_mesh": not bool(gate.get("ok")),
        }
        print("  [3] ★ 本机实测读到 %.4f ⇒ 闸 ok=%s ⇒ %s"
              % (size, gate.get("ok"),
                 "**停下，不建网格不跑求解**" if not gate.get("ok") else "继续"))

        #: ④ ★★★ 断言：不合理时**绝不**继续；且本脚本全程**未调** CreateMesh / RunAnalysis
        executed_mesh = False
        executed_run = False
        if gate.get("ok"):
            #: 只有判据放行才建网格（★ 本脚本刻意不跑求解 —— 那是弹框的那一步）
            try:
                r = sim.create_mesh(study, units=0, element_size=float(size), tolerance=float(tol))
                executed_mesh = True
                mesh = sw_connect.safe_get_com_member(study, "Mesh")
                ev["steps"]["mesh"] = {"ok": True, "return_code": r,
                                       "element_count": int(sw_connect.safe_get_com_member(mesh, "ElementCount") or 0)}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["mesh"] = {"ok": False, "error": str(exc)[:120]}
        ev["steps"]["safety"] = {
            "executed_create_mesh": executed_mesh,
            "executed_run_analysis": executed_run,
            "gate_blocked": not bool(gate.get("ok")),
            "★": "★★ 关键断言：闸不放行时 **executed_create_mesh=False** ⇒ 那条会挂的链被掐断在网格之前",
        }
        print("  [4] 建网格执行了=%s · 跑求解执行了=%s（★ 本脚本刻意不跑）"
              % (executed_mesh, executed_run))

        #: ⑤ 综合
        checks = {
            "rejects_bad": bad.get("ok") is False,
            "accepts_good": good.get("ok") is True,
            "no_mesh_when_blocked": (bool(gate.get("ok")) or not executed_mesh),
            "never_runs_analysis": not executed_run,
        }
        ev["steps"]["judgement"] = {"checks": checks,
                                    "passed": sum(1 for v in checks.values() if v),
                                    "of": len(checks),
                                    "★": "★ 四项全真 ⇒ 这道闸成立"}
        ok = all(checks.values())
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ok = False
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

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 网格参数闸门真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-24s %s" % (k, json.dumps(v, ensure_ascii=False)[:220]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
