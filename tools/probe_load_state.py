r"""@brief 探针：**载荷的「活动状态」**（`ICWLoadsAndRestraints.State` 与 `SuppressUnSuppress()`）。

## ★★★★ 为什么这个探针是"代码层面解决"的关键
```
★ 那个挂住会话的模态框原文：「未定义载荷或规定的位移 … **固定-刚性零件上的载荷将不处于活动状态**」
⇒ ★★ 它不是"没有载荷"，而是**载荷不活动**。
★ 而反射（`iface_cosmosworks.txt`）显示 `ICWLoadsAndRestraints` 上有：
     · `Int32 get_State()`                ← 读状态
     · **`Void SuppressUnSuppress()`**     ← ★★ **抑制/取消抑制**（官方方法）
⇒ ★★★ 正解 = **跑分析之前把不活动的载荷激活**，而不是"弹了框再去点掉"。
```

## 本探针只回答三件事（★ **绝不调用 `RunAnalysis`** ⇒ 不会弹框）
```
① 新建研究 + 夹具 + 载荷之后，**每个载荷的 `State` 是多少**？（学取值语义）
② 调一次 `SuppressUnSuppress()` 之后，`State` **变不变**？（验证它确实是那个开关）
③ ★ 再调一次能否**变回去**？（确认它是**切换**而不是单向）
```

## ⚠ 安全
**不调 `CreateMesh` / `RunAnalysis`**（★ 那两步才会弹框）· 只在新零件上跑 · 关件不保存。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_load_state.py
# 定位:   给"载荷活动状态"定取值与开关语义；产物 `output/load-state.json`。
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "load-state.json")
STUDY = "DSH-LoadState"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_part
        from scripts import sw_simulation as sim
        from scripts.sw_simulation import out_i4  #: ★ by-ref 出参包装（既有）

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
        ev["steps"]["material"] = str(
            sw_connect.safe_get_com_member(doc, "MaterialIdName") or ""
        )

        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)

        #: 夹具 + 载荷（★ 与出事的脚本同一套动作）
        sim.select_face_at(doc, 0.0, 0.0, -0.02)
        sim.apply_fixed_restraint(study, model=doc)
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        sim.select_face_at(doc, 0.0, 0.0, 0.0)
        sim.apply_normal_force(study, 100.0, model=doc)

        mgr = sim._loads_and_restraints_manager(study)
        count = int(sw_connect.safe_get_com_member(mgr, "Count") or 0)
        ev["steps"]["count"] = count

        def read_all(tag: str) -> list:
            """逐个读 `GetLoadsAndRestraints(i)` 的 Name / Type / State。"""
            rows = []
            for i in range(count):
                #: ★★ 官方签名是 **双参**（末位 by-ref）⇒ 必须传 `out_i4()`
                #:   （照抄 `collect_study_evidence` 的既有写法；传裸 0 会 `类型不匹配`）
                item = sw_connect.safe_get_com_member(
                    mgr, "GetLoadsAndRestraints", i, out_i4()
                )
                row = {
                    "index": i,
                    "type": type(item).__name__ if item is not None else None,
                }
                for attr in ("Name", "Type", "State", "EntityCount"):
                    try:
                        row[attr] = sw_connect.safe_get_com_member(item, attr)
                    except Exception:  # noqa: BLE001
                        row[attr] = None
                rows.append(row)
            ev["steps"][tag] = rows
            print("  [%s] %s" % (tag, json.dumps(rows, ensure_ascii=False)[:300]))
            return rows

        before = read_all("state_before")

        #: ★★ 试 `SuppressUnSuppress()`（★ 官方方法 —— 它是"切换"）
        toggled = []
        for i in range(count):
            try:
                item = sw_connect.safe_get_com_member(
                    mgr, "GetLoadsAndRestraints", i, out_i4()
                )
                r = sw_connect.call_com_member(item, "SuppressUnSuppress")
                toggled.append({"index": i, "return": str(r)[:40]})
            except Exception as exc:  # noqa: BLE001
                toggled.append(
                    {
                        "index": i,
                        "error": "%s: %s" % (type(exc).__name__, str(exc)[:70]),
                    }
                )
        ev["steps"]["SuppressUnSuppress"] = toggled
        print("  [toggle] %s" % json.dumps(toggled, ensure_ascii=False)[:260])

        after = read_all("state_after_1")

        #: 再切一次（★ 确认是"切换"而非单向）
        for i in range(count):
            try:
                item = sw_connect.safe_get_com_member(
                    mgr, "GetLoadsAndRestraints", i, out_i4()
                )
                sw_connect.call_com_member(item, "SuppressUnSuppress")
            except Exception:  # noqa: BLE001
                pass
        twice = read_all("state_after_2")

        #: ★ 判读：State 有没有变
        def states(rows):
            return [r.get("State") for r in rows]

        ev["steps"]["verdict"] = {
            "state_before": states(before),
            "after_1_toggle": states(after),
            "after_2_toggles": states(twice),
            "state_changes_on_toggle": states(before) != states(after),
            "toggle_is_reversible": states(after) != states(twice),
            "★": "★ 若 state 变化 ⇒ `SuppressUnSuppress` 就是那个开关 ⇒ **可用来把载荷设成活动**",
        }
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
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

    print("  ── 载荷活动状态探针 ──")
    for k, v in ev["steps"].items():
        print("  %-22s %s" % (k, json.dumps(v, ensure_ascii=False)[:300]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
