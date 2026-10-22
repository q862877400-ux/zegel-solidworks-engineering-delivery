"""★ 真机取证：`sw_part.fillet` 的返回**过不了 `_result` 的 `json.dumps`**（MCP 层会误报 error）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/probe_result_serializer.py
# 定位:   真机取证：`sw_part.fillet` 的返回**过不了 `_result` 的 `json.dumps`**（MCP 
#           层会误报 error）。
# 官方依据: ★ 判的是**本仓** `_result` 的 `json.dumps` 兼容性，★ 不涉官方签名
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "result-serializer-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    R: dict = {}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.04, -0.03, 0.0, 0.04, 0.03, 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (names[-1] if names else "草图1"), 15.0)
        #: ★ 选一条边（★ 用仓内声明式解析）
        import register_capabilities as rc
        from scripts.sw_selection_spec import resolve_selection
        R["selected"] = resolve_selection(doc, "index:0", "EDGE")
        from scripts.sw_part import fillet
        ret = fillet(doc, 2.0)
        R["ret_type"] = type(ret).__name__
        R["ret_repr"] = str(ret)[:90]
        R["new_features"] = [n for n in (P.feature_names(doc) or [])
                            if str(n).startswith(("圆角", "Fillet"))]
        #: ★★★ 复刻 `server.py::_result` 的那一行（`json.dumps(payload, ensure_ascii=Fal
        #: se, indent=2)`）
        try:
            json.dumps(ret, ensure_ascii=False, indent=2)
            R["json_dumps"] = "★ 竟然过了"
        except TypeError as exc:
            R["json_dumps"] = "★★ TypeError: %s" % str(exc)[:120]
        #: 再看 markdown 分支（它会 `payload.get("status", ...)`）
        try:
            ret.get("status", "result")
            R["dict_get"] = "★ 竟然有 .get"
        except AttributeError as exc:
            R["dict_get"] = "★★ AttributeError: %s" % str(exc)[:90]
        R["verdict"] = ("★★ 结论：能力建成了（见 new_features），而 MCP 层会把它变成一条 error"
                        if "TypeError" in R["json_dumps"] else "★ 序列化没问题")
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
