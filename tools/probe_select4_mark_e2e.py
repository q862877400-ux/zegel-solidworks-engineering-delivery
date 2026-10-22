"""★ 真机验证 `_select_com_object` 的 **Select4 + ISelectData** 新路径：mark 真的写得进去吗。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的质量线。
# 文件:   tools/probe_select4_mark_e2e.py
# 定位:   ★★★ bunny 读官方文档指出：官方 `IEntity/Select2.md` 逐字「**Obsolete. Supers
#           eded by
# [[IEntity::Select4]].**」，而 `Select4(bool Append, **SelectData** Data)` 的第 2 参是 
# `ISelectData`
#   —— ★★ 而仓内 `_select_com_object` 原先给 `Select4` 传的是**空 VARIANT**
#   ⇒ **`Select4` 分支的 `Mark` 永远是 0**（靠 `Select2` 排前面才没暴露）。
#   ★ 本探针验：★ 走**新路径**（`model=` 传进去）时，`mark` 是否真的落到选区上。
# 官方依据: `C:\\swapi\\types\\IEntity\\Select4.md`（签名）· `IEntity/Select2.md`（Obsol
# ete 那句）·
#     `C:\\swapi\\examples\\Exclude_Faces_Before_Flattening_Example_CSharp.md`
#     （`data.Mark = 1; entity.Select4(true, data);`）
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

OUT = REPO / "output" / "select4-mark-e2e-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.04, -0.03, 0.0, 0.04, 0.03, 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (names[-1] if names else "草图1"), 15.0)
        faces = []
        for b in list(_g(doc, "GetBodies2", 0, True) or []):
            faces.extend(list(_g(b, "GetFaces") or []))
        R["face_count"] = len(faces)

        def cnt(m):
            return int(_g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", m) or 0)

        #: ★ 三种调用形态各试 mark=1 与 mark=4
        for label, kwargs in (("★新路径（带 model ⇒ Select4 + ISelectData）", {"model": doc}),
                              ("旧路径（不带 model ⇒ 先 Select2）", {})):
            for mark in (1, 4):
                row: dict = {"how": label, "mark": mark}
                try:
                    _g(doc, "ClearSelection2", True)
                except Exception:                                         # noqa: BLE001
                    pass
                if not faces:
                    row["skip"] = "★ 没有面"
                    R["cases"].append(row)
                    continue
                ok = P._select_com_object(faces[0], append=False, mark=mark, **kwargs)
                row["ret"] = bool(ok)
                row["readback_mark"] = cnt(mark)
                row["readback_all"] = cnt(-1)
                row["mark_landed"] = row["readback_mark"] >= 1
                R["cases"].append(row)
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["new_path_ok"] = all(c.get("mark_landed") for c in R["cases"]
                           if c.get("how", "").startswith("★"))
    R["old_path_ok"] = all(c.get("mark_landed") for c in R["cases"]
                           if not c.get("how", "").startswith("★"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
