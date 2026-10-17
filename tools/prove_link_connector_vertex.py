"""★ 真机：`AddLinkConnector` —— ★ 形参名是 `VertexPoint*` ⇒ 试**顶点**那几个形态。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_link_connector_vertex.py
# 定位:   ★ 2026-10-03（轮 457）—— ★ 承 `plan-200r-v3` **§七 W2**（★ 那一条是 `1/2`：★ `rigid` 成、`link`/`pin` 未成）
#   与**事实 341**（★ 我此前对 B 组试过**五种给法**，全 `0→0`）。
#   ★★★ **而本轮的关键信息来自出厂程序集的**形参名****（★ 那是我此前没读的）：
#     ```
#     ★ `AddLinkConnector( **VertexPoint**forFirstLocation: Object,
#                          **VertexPoint**forSecondLocation: Object,
#                          ByRef ErrorCode: Int32 ) ⇒ CWLinkConnector`
#     ★★ 而★ 名字里有 **`VertexPoint`** ⇒ ★ **它要的是"顶点"**，
#        ★ **而不是**我此前传的"面 / 组件" ⚠
#     ★ 对照：★ `AddPinConnector(DispArray**Comp**1, DispArray**Comp**2, …)` ⇒ ★ 要**组件**
#             ★ `AddRigidConnector(PersistID**Face**Array, …)` ⇒ ★ 要**面**（★ 而我**做成了**）
#     ```
#   ★★ **故本轮试**三个**有依据的**形态**（★ 而★ 不瞎试 —— 每个都对应"VertexPoint 可能是什么"）：
#     ```
#     ★ ① 各传**一个 `IVertex` 对象**（★ 最直译）
#     ★ ② 各传**单元素数组** `[vertex]`（★ 因为形参类型是 `Object`，★ 而那常是数组）
#     ★ ③ 各传**点的三元组**（★ `(x, y, z)` —— ★ 因为名字叫 **VertexPoint**，★ 可能直接要"带坐标的点"）✓
#     ```
#   ⚠★ **判据**（★ 与 `rigid` 同一口径）：★ **载荷与约束计数** `GetLoadsAndRestraints` **+1** ✓
#     ★★ 而★ **不拿返回值当判据**（★ 事实 8）✓
# 官方依据: 出厂程序集 `SolidWorks.Interop.cosworks.dll` 的
#   `ICWLoadsAndRestraintsManager.AddLinkConnector`（★ **arity 3** · 形参名如上 · ★ 真机反射读得）·
#   `IBody2.GetVertices`（★ 顶点对象）· `IEntity`/`IVertex` 的 `GetPoint`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（计数 +1）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "link-connector-vertex-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "trials": []}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)

        #: ★ 建算例（★ 连接件要挂在算例上）
        from scripts.sw_simulation import create_static_study, get_study_manager
        try:
            create_static_study(sw, "LinkStudy")
        except Exception as exc:                               # noqa: BLE001
            ev["study_err"] = str(exc)[:100]
        mgr = get_study_manager(sw)
        study = None
        try:
            study = get_com_member(get_com_member(mgr, "GetStudy", 0))
        except Exception:                                      # noqa: BLE001
            try:
                study = get_com_member(mgr, "GetStudy", 0)
            except Exception as exc:                           # noqa: BLE001
                ev["getstudy_err"] = str(exc)[:100]
        ev["study_none"] = study is None
        if study is None:
            ev["verdict"] = "fail"
        else:
            lm = get_com_member(study, "LoadsAndRestraintsManager")
            ev["lm_none"] = lm is None

            def count():
                #: ★★★ 2026-10-03（轮 457）**读数三条并列** ——
                #:   ★ 上一版只用 `GetLoadsAndRestraints`，★ 而它**回 -1**（★ 而不是报错）⚠
                #:   ★★ 而「建成没有」**现在读不出来** ⇒ ★ 故**把三条读数都报出来**：
                #:     ① `Count`（★ 本仓旧包装用的 · ★★ 而事实里记过它**间歇性不稳**）
                #:     ② `GetLoadsAndRestraints` 的长度（★ 而**报错原文**）
                #:     ③ ★**特征树名字增量**（★ 连接件可能**不是特征**，★ 而那也该看）
                out = {}
                try:
                    v = get_com_member(lm, "Count")
                    out["count"] = int(v) if v is not None else None
                except Exception as exc:                       # noqa: BLE001
                    out["count_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                try:
                    arr = get_com_member(lm, "GetLoadsAndRestraints")
                    out["lar_len"] = len(list(arr or []))
                except Exception as exc:                       # noqa: BLE001
                    out["lar_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                try:
                    from scripts.sw_feature_readback import feature_names as _fn
                    out["tree"] = len(list(_fn(doc)))
                except Exception as exc:                       # noqa: BLE001
                    out["tree_err"] = str(exc)[:60]
                return out

            #: ★ 取两个顶点（★ 一个体上的两个不同顶点）
            #: ★★★ 2026-10-03（轮 457）**两个体各取一个顶点** ——
            #:   ★ 上一版两个顶点**同属一个体** ⇒ ★★ 调用**不报错而 Count 0→0**（★ 没建成）
            #:   ★ 而 ★★ **`AddRigidConnector` 在两个体上才成**（★ 而它的形参叫 `PersistIDFace**Array**`）；
            #:     ★★★ 而 `AddPinConnector` 的形参**直接叫 `DispArray**Comp**1/2`**（★ 两个组件）
            #:   ⇒ ★ 故同理：**连接件连的是"两个东西"** ⇒ ★ **两个顶点得分属两个体** ✓
            verts = []
            try:
                bodies = list(get_com_member(doc, "GetBodies2", -1, True) or [])
                ev["bodies"] = len(bodies)
                for b in bodies[:2]:
                    vs = list(get_com_member(b, "GetVertices") or [])
                    if vs:
                        verts.append(vs[0])
            except Exception as exc:                           # noqa: BLE001
                ev["verts_err"] = str(exc)[:100]
            ev["verts"] = len(verts)
            pts = []
            for v in verts:
                try:
                    pts.append(tuple(float(x) for x in get_com_member(v, "GetPoint")))
                except Exception:                              # noqa: BLE001
                    pts.append(None)
            ev["points"] = pts

            forms = []
            if len(verts) >= 2:
                forms = [
                    ("vertex_objects", lambda: (verts[0], verts[1])),
                    ("one_element_arrays", lambda: ([verts[0]], [verts[1]])),
                    ("point_tuples", lambda: (pts[0], pts[1])),
                ]
            for label, mk in forms:
                rec: dict = {"trial": label}
                before = count()
                #: ★★★ 2026-10-03（轮 457）**arity 要对** ——
                #:   ★ 真机抽象：`AddLinkConnector(first:Object, second:Object, ByRef ErrorCode:Int32)`
                #:     ⇒ ★★ **arity 3**。★ 而本仓的 `add_link_connector` 走 `_check(..., 2, …)`
                #:     ⇒ ★ **只传 2 个** ⚠（★ 与事实 315 那条"arity 写错"同一族）
                #:   ★ 故本轮**把 3 个都传上**（★ out 参数给 0）✓
                #: ★★★ 2026-10-03（轮 457）**out 参数要用 VARIANT(VT_BYREF|VT_I4)** ——
                #:   ★ 上一版传了个普通整数 ⇒ 真机报 **"非选择性的参数"\**
                #:     （★ 而同一波里数组/元组报的是 **"类型不匹配"** ⇒
                #:      ★★ **故对象形态是对的，卡在 out 参数**）✓
                #:   ★ 而本仓早有先例：`tools/audit_byref_args.py` 记着
                #:     `v = VARIANT(VT_BYREF | VT_R8, 0.0)` → `get_com_member(..., v)` ✓
                from win32com.client import VARIANT
                from pythoncom import VT_BYREF, VT_I4
                try:
                    a, b = mk()
                    ec = VARIANT(VT_BYREF | VT_I4, 0)
                    lm.AddLinkConnector(a, b, ec)
                    rec["arity"] = 3
                    rec["byref_variant"] = True
                    rec["called"] = True
                except Exception as exc3:                      # noqa: BLE001
                    rec["err_arity3"] = "%s: %s" % (type(exc3).__name__, str(exc3)[:90])
                    try:
                        a, b = mk()
                        ec = 0
                        lm.AddLinkConnector(a, b)
                        rec["arity"] = 2
                        rec["called"] = True
                    except Exception as exc2:                  # noqa: BLE001
                        rec["err"] = "%s: %s" % (type(exc2).__name__, str(exc2)[:110])
                except Exception as exc:                       # noqa: BLE001
                    rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
                after = count()
                rec["before"] = before
                rec["after"] = after
                ev["trials"].append(rec)
            def _n(d, key="count"):
                v = (d or {}).get(key)
                return v if isinstance(v, int) else -1
            ev["any_built"] = any(_n(t.get("after")) > _n(t.get("before")) for t in ev["trials"])
            ev["verdict"] = "pass" if ev["any_built"] else "fail"
        ev["note"] = ("★ 试三个有依据的形态（★ 都对应「VertexPoint 可能是什么」）："
                      "① 一个 IVertex 对象 · ② 单元素数组 · ③ 点的三元组。"
                      "★ 判据：★ 载荷与约束计数 **+1**（★ 不拿返回值当判据）。")
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
