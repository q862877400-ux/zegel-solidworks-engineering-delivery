"""★ 真机验：`insert_shut_off_surface`（先打一个**通孔** —— 关断面就是盖住通孔）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_shut_off_surface.py
# 定位:   ★ 2026-10-03（轮 391）**线索① 的真机验证**：轮 390 发现 `insert_shut_off_surface` 回
#   `Feature` 非 None 而**特征树不变**，★ 当时的推测是「模型上**没有通孔**可关」
#   （★ 关断面的作用是**盖住通孔**）。⇒ 本探针先打一个**通孔**，再调它。
#   ⚠ 官方那一页 **Remarks 为空**（★ 查过 CHM）⇒ 只能真机试。
# 官方依据: `C:\swapi\types\IFeatureManager\InsertMoldShutOffSurface.md`（★ 签名 `Feature
#   InsertMoldShutOffSurface()` —— **零参**）· CHM 解包里该页**无 Remarks**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量）：
# ```
# ① 前置：★ 件上**真的有通孔**（★ 用 `create_through_hole`，★ 并用 `collect_geometry` 的
#    **面数**间接印证 —— 打孔会多出圆柱面）
# ② `insert_shut_off_surface` ⇒ ★ **特征树增量非空**（★ 不再只是"回 Feature"）
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\shut-off-surface-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_part import (current_sketch_name, end_sketch, extrude_boss,
                         sketch_corner_rectangle, start_sketch)
    import sw_hole_features as HF
    import sw_mold as M
    import sw_surface_features as SF

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 25.0)
        ev["steps"]["doc"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}
        faces_before = len(get_com_member(get_com_member(doc, "GetBodies2", 0, False)[0], "GetFaces") or [])
        #: ① 打通孔（★ 关断面要盖的就是它）
        try:
            #: ★ 按**契约**调（实测签名：`(model, center, diameter, plane_name, name)`）
            HF.create_through_hole(doc, (0.0, 0.0), 8.0)
            faces_after = len(get_com_member(get_com_member(doc, "GetBodies2", 0, False)[0], "GetFaces") or [])
            ev["steps"]["through_hole"] = {"ok": faces_after > faces_before,
                                           "faces": [faces_before, faces_after]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["through_hole"] = {"ok": False,
                                           "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}
        #: ①b ★★ **轮 391 的假设**：`shut_off` 属于**模具流程的一环** ⇒ 先建**分型线 + 分型面**
        #:   （★ 轮 390/391 两次都只打孔、没建它们）。★ 手法照事实 306：mark=1 选方向、mark=4 按**中点**选边。
        ext = get_com_member(doc, "Extension")
        callout = sw_connect.create_empty_dispatch_variant()
        doc.ClearSelection2(True)
        ext.SelectByID2("前视基准面", "PLANE", 0, 0, 0, False, 1, callout, 0)
        ms = []
        for b in (get_com_member(doc, "GetBodies2", -1, True) or []):
            for e in (get_com_member(b, "GetEdges") or []):
                try:
                    a = [float(x) for x in get_com_member(
                        get_com_member(e, "GetStartVertex"), "GetPoint")]
                    c = [float(x) for x in get_com_member(
                        get_com_member(e, "GetEndVertex"), "GetPoint")]
                    ms.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                except Exception:                              # noqa: BLE001
                    continue
        ztop = max(m[2] for m in ms) if ms else None
        for m in ms:
            if ztop is not None and abs(m[2] - ztop) < 1e-9:
                ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, 4, callout, 0)
        try:
            ev["steps"]["pre_parting_line"] = {"ok": True,
                                               "feature": str(M.insert_parting_line(doc))[:40]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["pre_parting_line"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}
        try:
            ev["steps"]["pre_parting_surface"] = {
                "ok": True, "feature": str(M.insert_parting_surface(doc))[:40]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["pre_parting_surface"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}

        #: ② 关断面（★ 零参）
        before = SF.feature_names(doc)
        try:
            r = M.insert_shut_off_surface(doc)
            after = SF.feature_names(doc)
            new = [n for n in after if n not in before]
            ev["steps"]["shut_off_surface"] = {"ok": bool(new), "returned": (r is not None),
                                               "new_features": new[-2:],
                                               "tree": [len(before), len(after)]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["shut_off_surface"] = {"ok": False,
                                               "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 官方该页 **Remarks 为空** ⇒ 只能真机试；★ 推测是「关断面要盖住**通孔**」"
                      "（轮 390 的件是实心方块、没有孔）⇒ 本轮先打 8 mm 通孔再试。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1200])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
