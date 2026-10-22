r"""@brief 决定性实验：**把载荷 `State` 设成"另一侧"，再跑 `RunAnalysis`，看框还弹不弹**。

## ★★★★★ 为什么这是"从代码层面解决"的关键实验
```
★ 探针已证：载荷新建时 `State = 0`，`SuppressUnSuppress()` 在 **0 ⇄ 1** 之间可逆切换。
⚠ 但 **0 与 1 哪个是"活动"**，我不能猜 —— ★ 而对话框说的是「载荷将**不处于活动状态**」。
⇒ ★★★ 唯一的证明：**把 State 设成 1，然后跑 `RunAnalysis`**：
     · **不弹了** ⇒ ★ **1 就是"活动"，`State` 就是那个前置条件** ⇒ **代码层面正解找到** ✓
     · **还弹** ⇒ 0 才是活动侧（或前置条件另有其因）⇒ ★ 两种结果**都记下来**
```

## 与"看门狗"的根本区别（★ 用户 2026-10-01 的指令）
```
★ 看门狗 = **事后**（弹了再点）、**本机**（别人装了 skill 没有）、**轮询有窗口期**。
⇒ ★★ 本实验要证明的是**事前**的代码修复：
   在 `scripts/sw_simulation.py` 里，跑分析**之前**把 `State` 摆正
   ⇒ ★ **随 skill 发布** ⇒ **任何装了本 skill 的人都受保护**。
```

## ⚠ 安全预案（★ 万一还挂）
```
★ 本脚本**只在新零件上跑**，且 `finally` 里**关件不保存**。
★ 若仍弹框 ⇒ ★ 用**安全**手法解：**只点对话框自己的「确定」按钮**，
  ★★ **绝不 `WM_CLOSE`**（★ 上一次那么做把 SolidWorks 一起关了 —— 事实 175）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实验脚本）
# 文件:   tools/probe_load_state_active.py
# 定位:   给"载荷活动状态"定**哪一侧是活动**；产物 `output/load-state-active.json`。
# 官方依据: `ICWLoadsAndRestraints.get_State()` / `SuppressUnSuppress()`
#          （`D:\AI\SW\_raw\reflect\iface_cosmosworks.txt`）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "load-state-active.json")
STUDY = "DSH-Active"


TOGGLE = [True]  #: ★ `--no-toggle` 时置 False（对照组：不切 State 就跑）


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_simulation import out_i4

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)

        sim.select_face_at(doc, 0.0, 0.0, -0.02)
        sim.apply_fixed_restraint(study, model=doc)
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        sim.select_face_at(doc, 0.0, 0.0, 0.0)
        sim.apply_normal_force(study, 100.0, model=doc)

        mgr = sim._loads_and_restraints_manager(study)
        count = int(sw_connect.safe_get_com_member(mgr, "Count") or 0)

        def states() -> list:
            out = []
            for i in range(count):
                it = sw_connect.safe_get_com_member(
                    mgr, "GetLoadsAndRestraints", i, out_i4()
                )
                #: ⚠⚠ **不能写 `State or -1`** —— `State` 的合法值包含 **0**，`0 or -1`
                #: 会得到 -1
                #:   （★ 本文件的初版就是这么写的，于是把"State=0"读成了"-1" ——
                #: 门禁 `check_env_pitfalls` 的"③ falsy-zero"当场抓到，见 known-facts 17
                #: 8）。
                _st = sw_connect.safe_get_com_member(it, "State")
                out.append(int(_st) if _st is not None else -1)
            return out

        ev["steps"]["state_initial"] = states()
        ev["steps"]["toggle_enabled"] = TOGGLE[0]
        print("  [1] 初始 State = %s" % ev["steps"]["state_initial"])

        #: ★★ 把每个载荷切到"另一侧"（★ 对照组 `--no-toggle` 时**跳过这一步**）
        if TOGGLE[0]:
            for i in range(count):
                it = sw_connect.safe_get_com_member(
                    mgr, "GetLoadsAndRestraints", i, out_i4()
                )
                sw_connect.call_com_member(it, "SuppressUnSuppress")
        ev["steps"]["state_after_toggle"] = states()
        print("  [2] 切一次后 State = %s" % ev["steps"]["state_after_toggle"])

        #: ★ 建网格（既有脚本证明这一步本身不弹框）
        size, tol = sim.default_element_size_and_tolerance(study, -1)
        mc = sim.create_mesh(
            study, units=0, element_size=float(size), tolerance=float(tol)
        )
        mesh = sw_connect.safe_get_com_member(study, "Mesh")
        elements = int(sw_connect.safe_get_com_member(mesh, "ElementCount") or 0)
        ev["steps"]["mesh"] = {
            "CreateMesh": mc,
            "element_count": elements,
            "ok": elements > 0,
        }
        print("  [3] 网格 CreateMesh=%r 单元=%d" % (mc, elements))

        #: ★★★★★ **决定性一步**：跑分析。★ 若 State=1 是活动侧 ⇒ **不应弹框**
        print("  [4] ★ 跑 RunAnalysis（决定性一步 —— 若框不弹，就找到正解了）")
        t0 = time.time()
        rc = sim.run_analysis(study)
        results = sw_connect.safe_get_com_member(study, "Results")
        plots = None
        names = None
        if results is not None:
            try:
                plots = int(
                    sw_connect.safe_get_com_member(results, "GetPlotCount") or 0
                )
            except Exception:  # noqa: BLE001
                plots = None
            try:
                names = [
                    str(x)
                    for x in (
                        sw_connect.safe_get_com_member(results, "GetPlotNames") or ()
                    )
                ]
            except Exception:  # noqa: BLE001
                names = None
        ev["steps"]["run_analysis"] = {
            "ok": results is not None and bool(plots),
            "return_code": rc,
            "return_is_trustworthy": False,
            "results_present": results is not None,
            "plot_count": plots,
            "plot_names": names,
            "seconds": round(time.time() - t0, 1),
            "★": "★★ 若这里**没弹框且 results 非空** ⇒ `State=1` 就是「活动」侧 ⇒ **代码正解成立**",
        }
        print(
            "  [5] ★★ 跑完了！Results=%s 图数=%s 用时=%.1fs"
            % (results is not None, plots, ev["steps"]["run_analysis"]["seconds"])
        )
        print("       图名 = %s" % names)
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        print("  ⚠ error: %s" % ev["error"])
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

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    if "--no-toggle" in sys.argv:
        TOGGLE[0] = False
        print("  ★ 对照组：**不切换** State，直接跑 RunAnalysis")
    raise SystemExit(main())
