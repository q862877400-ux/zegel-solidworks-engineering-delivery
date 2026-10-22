"""★ 真机：装配体上的**销钉连接件** —— ★ 同族里"只要两个零件"的那条。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_pin_connector_asm.py
# 定位:   ★ 2026-10-03（轮 426）`plan-200r-v3` 段 1（B 组）—— ★ 承**事实 339** 给同族
#           开的门。
#   ★★ 事实 339 的结论：★ 连接件一族有**两条硬前提** ——
#     ⓐ **它要两个东西**（★ 同族形参名写着 `Comp1`/`Comp2`）·
#     ⓑ **不要从选区读多实体**（★ `ISelectionMgr` 那族只回得到第 1 个，★ 五入口都试过）。
#   ★★★ 而**销钉连接件的形参恰好只要两个零件**：
#     ```
#     AddPinConnector(**DispArrayComp1:Object**, **DispArrayComp2:Object**, ErrorCode&)
#     ```
# ⇒ ★★ 它**比刚性连接件更简单** —— ★ **组件对象本仓直接拿得到**（`sw_assembly.get_compon
# ents`）
#       ⇒ ★ 连"按序号取实体"都不需要 ✓
#   ★ 而**装配体那条路在硬约束⑦（禁保存）下仍走得通**：★ 用**已在盘上的**自带零件
#     （★ 本机 `…\samples\tutorial\api\` 下有几十个 `.sldprt`）⇒ ★ **不保存任何东西** ✓
# ★ 算例名用**唯一名**（事实 329/414）；★ 而**先验入口**（★ 本轮纪律）：★ 先看顶层组件是
# 不是 2 个。
# 官方依据: 出厂类型库反射（`AddPinConnector(DispArrayComp1, DispArrayComp2, ErrorCode&)
#           `）·
#   `IAssemblyDoc.AddComponent5` · `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 顶层组件数 = **2** ★ 且施加后回读计数**恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "pin-connector-asm-evidence.json"
)
STUDY = "DSH-PIN_%s" % time.strftime("%H%M%S")
SAMPLES = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples\tutorial\api"
)


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_assembly import add_component, get_components
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study": STUDY}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        p1, p2 = SAMPLES / "block.sldprt", SAMPLES / "block20.sldprt"
        ev["parts"] = {
            "p1": str(p1),
            "p1_exists": p1.is_file(),
            "p2": str(p2),
            "p2_exists": p2.is_file(),
        }
        doc = sw_connect.new_document(sw, "assembly")
        add_component(doc, str(p1), 0.0, 0.0, 0.0, "", sw)
        add_component(doc, str(p2), 0.1, 0.0, 0.0, "", sw)
        #: ★ **先验入口**：★ 顶层组件是不是 2 个
        comps = list(get_components(doc, top_level_only=True))
        ev["steps"]["entry_check"] = {
            "ok": len(comps) == 2,
            "component_count": len(comps),
            "note": "★ 先验入口：★ 顶层组件 2 个 ⇒ 才继续施加（★ 销钉连接件要两个零件）",
        }
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        ev["steps"]["static_study"] = {"ok": mgr is not None}
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                rep = SL.apply_pin_connector_report(mgr, doc)
                ev["steps"]["pin_connector"] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict)
                    else None,
                    "error": (rep.get("error") or "")[:130]
                    if isinstance(rep, dict)
                    else None,
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["pin_connector"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                }
        else:
            ev["steps"]["pin_connector"] = {
                "ok": False,
                "skipped": "★ 入口没验过 ⇒ 不施加",
            }
        ev["verdict"] = (
            "pass" if (ev["steps"].get("pin_connector") or {}).get("ok") else "partial"
        )
        ev["note"] = (
            "★ 装配体上的销钉连接件 —— ★ 同族里**只要两个零件**的那条。"
            "★ 判据：① 顶层组件 2 个 ★ ② 施加后计数恰好 +1。"
            "★ 零件用**已在盘上的**自带件 ⇒ ★ 不保存任何东西（硬约束⑦）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
