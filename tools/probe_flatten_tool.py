"""★ 真机验证：新工具 `solidworks_flatten_surface` 能否**按工具层契约**建成曲面展平。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。规格 `specs/202-user-coverage-gaps` 的 **R6+**。
# 文件:   tools/probe_flatten_tool.py
# 定位:   ★ 本轮把「真机已建成过、代码只在探针里」的**曲面展平**抬成了工具
#   （`scripts/sw_feature_entry_ops.create_flatten_surface` + `tool_specs_batch76.py`）⇒
#   ★★ **不能只靠旧探针的读数就宣布工具能用** —— 本探针**按 ToolSpec 的契约**调一次。
#   官方依据: `C:\swapi\types\IFeatureManager\InsertFlattenSurface2.md`（**2 参**；
#     `## Remarks` 给五种 mark：面=1 · 锚点=16 · 引导边=2 · 映射边=4 · 撕裂边=8）
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

import register_capabilities as RC                                        # noqa: E402
from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402
from scripts import sw_surface_features as SF                             # noqa: E402

OUT = REPO / "output" / "flatten-tool-evidence.json"
TOOL = "solidworks_flatten_surface"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _mk_surface(doc):
    """★ 造一张曲面体（★ 与 `prove_flatten_with_anchor.py::_mk_surface` 同一手法，**照抄**）。"""
    try:
        _g(doc, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    _g(_g(doc, "SketchManager"), "CreateLine", -0.03, 0.0, 0.0, 0.03, 0.0, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("草图") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "草图1", "草图1", "Sketch1"):
        try:
            return SF.create_extruded_surface_report(doc, 40.0, sketch_name=cand)
        except Exception:                                                 # noqa: BLE001
            continue
    return {}


def main() -> int:
    started = time.time()
    row: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "tool": TOOL}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["mk_surface"] = bool((_mk_surface(doc) or {}).get("ok"))
        row["surface_bodies"] = len(list(_g(doc, "GetBodies2", 1, True) or []))
        spec = {getattr(s, "name", None): s for s in RC.all_specs()}.get(TOOL)
        if spec is None:
            row["ok"] = False
            row["err"] = "★ 工具没注册"
        else:
            args = {"accuracy_factor": 4, "should_use_tears": False, "body_type": "surface"}
            #: ★★ **按 ToolSpec 的契约调**（复刻 `tool_registry.make_tool_function` 的三
            #: 步）
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            fn = getattr(mod, spec.function)
            kwargs = {}
            want = {getattr(pp, "name", None) for pp in (spec.params or [])}
            for k, v in args.items():
                if k in want:
                    kwargs[k] = v
            kwargs[spec.inject] = RC.RESOLVERS[spec.inject](None)
            row["call_path"] = "module=%s function=%s inject=%s params=%s" % (
                spec.module, spec.function, spec.inject, sorted(kwargs))
            ret = fn(**kwargs)
            row["ret_type"] = type(ret).__name__
            if isinstance(ret, dict):
                for k in ("ok", "preconditions_held", "ret_name", "ret_type", "ret_is_none",
                          "new_features", "body_count", "anchor_selected", "error"):
                    if k in ret:
                        row[k] = ret[k]
                row["ret_ok"] = ret.get("ok")
            row["ok"] = bool(row.get("ret_ok"))
    except Exception as exc:                                              # noqa: BLE001
        row["ok"] = False
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    row["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
