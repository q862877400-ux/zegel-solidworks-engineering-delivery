"""★ 真机：`AddLinkConnector` —— ★ **两个体各取一个顶点**（★ 承事实 372 那个下一个维度）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_link_connector_twobody.py
# 定位:   ★ 2026-10-03（轮 458）—— ★ 执行**事实 372** 定下的那个单动作。
#   ★★★ **为什么是"两个体"**（★ 依据与 `rigid` 那条**已验**的路同形）：
#     ```
#     ★ **`AddRigidConnector` 在**两个体**上才成**（★ 单体上它"成功返回却不建" —— **事实 338**）
#     ★ **`AddPinConnector` 的形参**直接叫 `DispArray**Comp**1/2`**（★ 两个组件）
#     ⇒ ★★★ **故"连接件连的是**两个东西**"** ⇒ ★ `AddLinkConnector` 的两个顶点**很可能也要分属两个体** ✓
#     ```
#   ★★ 而**事实 372 已定下**那条调用的**正确形态**：
#     ```
#     ★★ `lm.AddLinkConnector(vertexA, vertexB, VARIANT(VT_BYREF | VT_I4, 0))`
#        ★ 其中 vertexA/B 是 **`IVertex` 对象**（★ 不是数组、★ 不是坐标）✓
#     ```
#   ★ 而★ 上一轮**体数 = 1** ⇒ ★★ **那个维度根本没试到** ⚠ ⇒ 故本轮**先建两个不相连的凸台** ✓
# ★ 判据（★ 与 `rigid` 同口径）：★ **`Count` 0 → 1** · ★ 特征树增量 · ★ 体数仍是 2。
#   ★★ 而★ **带一个对照**：★ **同一体**上的两个顶点（★ 若那个也成 ⇒ 说明"两个体"不是必要条件）
# 官方依据: `ICWLoadsAndRestraintsManager.AddLinkConnector`（★ arity 3 · 形参名 `VertexPointfor*Location`）·
#   `IBody2.GetVertices` · `IBody2.GetBodyBox` · `VARIANT(VT_BYREF | VT_I4)`（★ 本仓 `audit_byref_args.py` 先例）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（Count +1 · 树增量 · 带对照）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\link-connector-twobody-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_feature_readback import feature_names
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_simulation import create_static_study, get_study_manager

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "trials": []}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: ★ **两个不相连的凸台** ⇒ 一个零件两个体
        for x1, x2 in ((-40.0, -10.0), (10.0, 40.0)):
            start_sketch(doc, plane_name="Front Plane")
            sketch_corner_rectangle(doc, x1, -10.0, x2, 10.0)
            sk = current_sketch_name(doc, "")
            end_sketch(doc)
            extrude_boss(doc, sk, 10.0)
        names = list(feature_names(doc))
        ev["tree"] = len(names)

        def bodies():
            return list(get_com_member(doc, "GetBodies2", -1, True) or [])

        bs = bodies()
        ev["bodies"] = len(bs)
        bs = bodies()
        ev["bodies"] = len(bs)

        #: ★ 建算例
        try:
            create_static_study(sw, "LinkTwoBody")
        except Exception as exc:                               # noqa: BLE001
            ev["study_err"] = str(exc)[:110]
        mgr = get_study_manager(sw)
        study = None
        try:
            study = get_com_member(mgr, "GetStudy", 0)
        except Exception as exc:                               # noqa: BLE001
            ev["getstudy_err"] = str(exc)[:110]
        ev["study_none"] = study is None
        if study is None:
            ev["verdict"] = "fail"
            OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
            print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:900])
            return 0
        lm = get_com_member(study, "LoadsAndRestraintsManager")

        def cnt() -> int:
            try:
                return int(get_com_member(lm, "Count") or 0)
            except Exception:                                  # noqa: BLE001
                return -1

        #: ★ 收集两体的顶点
        per_body = []
        for b in bs:
            try:
                per_body.append(list(get_com_member(b, "GetVertices") or []))
            except Exception:                                  # noqa: BLE001
                per_body.append([])
        ev["verts_per_body"] = [len(v) for v in per_body]

        from win32com.client import VARIANT
        from pythoncom import VT_BYREF, VT_I4

        def call(a, b):
            ec = VARIANT(VT_BYREF | VT_I4, 0)
            lm.AddLinkConnector(a, b, ec)
            return True

        trials = []
        if len(per_body) >= 2 and per_body[0] and per_body[1]:
            trials.append(("two_bodies_each_one",
                           lambda: call(per_body[0][0], per_body[1][0])))
        if len(per_body) >= 1 and len(per_body[0]) >= 2:
            trials.append(("same_body_two_verts_control",
                           lambda: call(per_body[0][0], per_body[0][1])))
        for label, fn in trials:
            rec: dict = {"trial": label, "count_before": cnt(), "tree_before": len(list(feature_names(doc)))}
            try:
                fn()
                rec["called"] = True
            except Exception as exc:                           # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            rec["count_after"] = cnt()
            rec["tree_after"] = len(list(feature_names(doc)))
            ev["trials"].append(rec)
        ev["any_built"] = any((t.get("count_after", 0) > t.get("count_before", 0)) for t in ev["trials"])
        ev["verdict"] = "pass" if ev["any_built"] else "fail"
        ev["note"] = ("★ 两个体各取一个顶点（★ 而★ 带一个对照：同一体上的两个顶点）。"
                      "★ 形态照事实 372：★ `IVertex` 对象 + `VARIANT(VT_BYREF|VT_I4)` 的 out。"
                      "★ 判据：★ `Count` **+1** · ★ 特征树增量。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
