"""★ 决定性对照：**mark 不同**时，`RESOLVERS["model"]` 会不会清掉选区。

★ 背景：★ 第 17 轮（`diag_selection_lifetime.py`）在**焊件件**上用 **mark=1 选面** ⇒ 解析器之后 `2 → 0`；
  ★ 第 28 轮（`probe_selection_count_e2e.py`）在**普通件**上用 **mark=0 选边** ⇒ 解析器之后 `1 → 1`（**没掉**）。
★ 本脚本把两个变量**分开**测：★ 同一个件上，**mark=0** 与 **mark=1** 各选一次，各调一次解析器。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/probe_resolver_mark_matrix.py
# 定位:   决定性对照：**mark 不同**时，`RESOLVERS["model"]` 会不会清掉选区。
# 官方依据: ★ 判的是**本仓** `register_capabilities.RESOLVERS` 的运行时行为（事实 503 一
#           族），★ 不涉官方签名
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

OUT = REPO / "output" / "resolver-mark-matrix-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    import register_capabilities as rc

    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (names[-1] if names else "草图1"), 15.0)
        import scripts.sw_part as SP

        faces, edges = [], []
        for b in list(_g(doc, "GetBodies2", 0, True) or []):
            faces.extend(list(_g(b, "GetFaces") or []))
            edges.extend(list(_g(b, "GetEdges") or []))

        def count(m):
            try:
                return int(
                    _g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", m) or 0
                )
            except Exception:  # noqa: BLE001
                return -1

        for kind, pool in (("FACE", faces), ("EDGE", edges)):
            for mark in (0, 1, 2, 4):
                for n in (1, 2):
                    row: dict = {"kind": kind, "mark": mark, "count": n}
                    _g(doc, "ClearSelection2", True)
                    picked = 0
                    for obj in pool:
                        if picked >= n:
                            break
                        try:
                            SP._select_com_object(obj, append=(picked > 0), mark=mark)
                            got = count(mark)
                            if got > picked:
                                picked = got
                        except Exception:  # noqa: BLE001
                            continue
                    row["picked"] = picked
                    row["before"] = count(mark)
                    row["all_before"] = count(-1)
                    rc.RESOLVERS["model"](None)
                    row["after_resolver"] = count(mark)
                    row["all_after"] = count(-1)
                    row["dropped"] = row["after_resolver"] < row["before"]
                    R["rows"].append(row)
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    R["dropped_count"] = sum(1 for r in R["rows"] if r.get("dropped"))
    R["total"] = len(R["rows"])
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
