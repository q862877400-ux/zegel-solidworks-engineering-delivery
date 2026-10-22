"""★ 逐面矩阵：顶端盖到底要**哪一张面**才建得出来（★ 单变量：一次只换选中的面）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机矩阵探针）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**
# 。
# 文件:   tools/probe_endcap_face_matrix.py
# 定位:   ★★ 前置（选面）已经成立（事实 503 的修法生效，工具回读 `{'0':1,'all':1}`），
#   ★ 而 API 仍**静默回 `None`** ⇒ ★ 下一个变量是「**选中了哪一张面**」。
#   ★ 本探针**逐张面**试一遍（一次只换一张），看哪一张能建成 —— ★ 单变量、可复算。
#   官方依据: `c:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`
# （Remarks 逐字「select one or more **end faces**」；★ **没给 mark**，官方例子用 **0**
# ）
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

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p  # noqa: E402

OUT = REPO / "output" / "endcap-face-matrix-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def _cnt(doc, mark):
    try:
        return int(
            _g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", mark) or 0
        )
    except Exception:  # noqa: BLE001
        return -1


def _profile() -> str:
    for root in (r"c:\ProgramData\SOLIDWORKS", r"c:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            if "weldment profiles" in str(h).lower():
                return str(h)
    return ""


def _all_faces(doc):
    out = []
    for body in list(_g(doc, "GetBodies2", 0, True) or []):
        out.extend(list(_g(body, "GetFaces") or []))
    return out


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    prof = _profile()
    R["profile"] = prof
    for i in range(6):  #: ★ 最多试前 6 张面
        row: dict = {"face_index": i}
        doc = None
        try:
            doc = c.new_document(sw, "part")
            p.start_sketch(doc, plane_name="Front Plane")
            _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
            p.end_sketch(doc)
            names = [
                n
                for n in (p.feature_names(doc) or [])
                if n.startswith("草图") or n.lower().startswith("sketch")
            ]
            from scripts.sw_weldment import create_structural_member_from_sketch

            sm_res = create_structural_member_from_sketch(
                doc, sketch_name=(names[-1] if names else "草图1"), profile_path=prof
            )
            row["weldment_ok"] = bool(isinstance(sm_res, dict) and sm_res.get("ok"))
            faces = _all_faces(doc)
            row["face_count"] = len(faces)
            if i >= len(faces):
                row["skip"] = "★ 该体没有第 %d 张面" % i
                R["cases"].append(row)
                continue
            try:
                _g(doc, "ClearSelection2", True)
            except Exception:  # noqa: BLE001
                pass
            import scripts.sw_part as sp

            sp._select_com_object(faces[i], append=False, mark=0)
            row["selected_all"] = _cnt(doc, -1)
            if row["selected_all"] < 1:
                row["skip"] = "★ 这张面没选上（回读 0）"
                R["cases"].append(row)
                continue
            before = list(p.feature_names(doc) or [])
            ret = _g(
                _g(doc, "FeatureManager"),
                "InsertEndCapFeature3",
                0.005,
                False,
                False,
                0.0,
                0.0,
                0.0,
                False,
                0.0,
                False,
                0,
            )
            row["returned_is_none"] = ret is None
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
            after = list(p.feature_names(doc) or [])
            row["new_features"] = [n for n in after if n not in before]
            row["ok"] = bool(row["new_features"] or row.get("ret_type"))
        except Exception as exc:  # noqa: BLE001
            row["ok"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:  # noqa: BLE001
                pass
        R["cases"].append(row)
    R["passed"] = sum(1 for r in R["cases"] if r.get("ok"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
