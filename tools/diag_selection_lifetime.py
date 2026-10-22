"""★ 单变量隔离：选区在 `_pick_faces` 之后、工具读取之前，**到底被哪一步清掉**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机诊断）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/diag_selection_lifetime.py
# 定位:   ★★ **为什么要有它**：R3 探针里，我选面后**回读为真**（`readback_mark=1/2`），
#   而**工具自己读到全 0** ⇒ ★ 选区在两步之间消失。本脚本把中间那几步**逐个**试一遍，
#   看**是哪一步清的**（★ 单变量，一次只加一步）。
# ★ 手续与探针一致：造结构构件（焊件）⇒ 选面 ⇒ 每步后回读 `GetSelectedObjectCount2(mark)
# `。
#   官方依据: `IFeatureManager.InsertEndCapFeature3`（「select one or more end faces」）
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "selection-lifetime-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _cnt(doc, mark):
    try:
        return int(_g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", mark) or 0)
    except Exception:                                                     # noqa: BLE001
        return -1


def _profile() -> str:
    for root in (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            if "weldment profiles" in str(h).lower():
                return str(h)
    return ""


def _pick(doc, count, mark):
    import scripts.sw_part as SP
    try:
        _g(doc, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked = 0
    for body in list(_g(doc, "GetBodies2", 0, True) or []):
        for face in list(_g(body, "GetFaces") or []):
            if picked >= count:
                break
            try:
                SP._select_com_object(face, append=(picked > 0), mark=mark)
                if _cnt(doc, mark) > picked:
                    picked = _cnt(doc, mark)
            except Exception:                                             # noqa: BLE001
                pass
        if picked >= count:
            break
    return picked


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: 造焊件（结构构件）
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("草图") or n.lower().startswith("sketch")]
        sk = names[-1] if names else "草图1"
        from scripts.sw_weldment import create_structural_member_from_sketch
        R["weldment"] = create_structural_member_from_sketch(
            doc, sketch_name=sk, profile_path=_profile())
        if isinstance(R["weldment"], dict):
            R["weldment"] = {k: R["weldment"].get(k) for k in ("ok", "preconditions_held", "error")}
        R["features"] = list(P.feature_names(doc) or [])

        def note(tag):
            R["steps"].append({"step": tag, "mark0": _cnt(doc, 0), "mark1": _cnt(doc, 1),
                               "all": _cnt(doc, -1)})

        note("造完焊件（未选）")
        R["picked"] = _pick(doc, 2, 1)
        note("选 2 个面 mark=1（刚选完）")
        #: ★★ 逐个加一步，看哪一步清掉它
        _ = list(P.feature_names(doc) or [])
        note("读了 feature_names 之后")
        _ = list(_g(doc, "GetBodies2", 0, True) or [])
        note("读了 GetBodies2 之后")
        for _b in list(_g(doc, "GetBodies2", 0, True) or []):
            _ = list(_g(_b, "GetFaces") or [])
        note("读了 GetFaces 之后")
        _ = _g(doc, "FeatureManager")
        note("取了 FeatureManager 之后")
        _ = _g(doc, "SelectionManager")
        note("取了 SelectionManager 之后")
        #: ★ 工具的 `_selection_marks` 走的是这条
        from scripts.sw_sheet_metal_weld_entry import _selection_marks
        R["tool_sees"] = _selection_marks(doc)
        note("调了工具的 _selection_marks 之后")
        #: ★★★ **决定性单变量**：探针的 `_call` 在调工具前会先跑 `RESOLVERS[inj](None)`
        #:   ⇒ ★ 本步把它**单独插进来**，看选区在不在。
        try:
            import register_capabilities as _RC
            _resolved = _RC.RESOLVERS["model"](None)
            R["resolved_type"] = type(_resolved).__name__
        except Exception as exc:                                          # noqa: BLE001
            R["resolver_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        note("调过 RESOLVERS['model'] 之后")
        R["tool_sees_after_resolver"] = _selection_marks(doc)
        note("解析器之后再调 _selection_marks")
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
