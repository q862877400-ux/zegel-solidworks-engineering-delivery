"""★ 真机验证 `part_loft` 的修复：★ 带 `profile_sketches` 走**契约** ⇒ 前置过不过、建不建得成。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的质量线。
# 文件:   tools/probe_loft_fixed_e2e.py
# 定位:   ★★★ 上一轮真机证出「显式拒」四件套**经工具层必然失败**；★ 本轮给 `part_loft` 加了
#   `profile_sketches`（mark=1、**按顺序**）+ `pre_call=_pre_loft_profiles`。
#   ★ 本探针**按工具层契约**调（`param_alias` → 注入 → `pre_call` → 目标函数）。
#   官方依据: `scripts/sw_loft.py` 的 docstring（轮廓 mark=1 · 顺序即语义）·
#     `C:\\swapi\\types\\IFeatureManager\\InsertProtrusionBlend2.md`（18 参）
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

OUT = REPO / "output" / "loft-fixed-e2e-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    import register_capabilities as rc
    spec = next((s for s in rc.all_specs()
                 if getattr(s, "name", None) == "solidworks_part_loft"), None)
    if spec is None:
        R["err"] = "★ 找不到 solidworks_part_loft"
        OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        return 0
    R["spec_params"] = [getattr(p, "name", None) for p in (spec.params or [])]
    R["pre_call"] = getattr(getattr(spec, "pre_call", None), "__name__", None)
    R["param_alias"] = dict(getattr(spec, "param_alias", None) or {})
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: ★ 两个轮廓：★ 前视面一个圆、上视面一个圆 —— ★ **不同平面**（真机验过这种能建成）
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.015)
        P.end_sketch(doc)
        P.start_sketch(doc, plane_name="Top Plane")
        _g(_g(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.008)
        P.end_sketch(doc)
        names = list(P.feature_names(doc) or [])
        R["features_before"] = names
        sketches = [n for n in names if n.startswith(("草图", "Sketch"))]
        R["sketches_found"] = sketches
        if len(sketches) < 2:
            R["skip"] = "★ 只找到 %d 个草图" % len(sketches)
            OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
            return 0
        profiles = sketches[:2]
        R["profile_sketches"] = profiles
        try:
            _g(doc, "ClearSelection2", True)
        except Exception:                                                 # noqa: BLE001
            pass
        args = {"profile_sketches": profiles, "closed": False, "use_selected_profiles": True}
        alias = dict(getattr(spec, "param_alias", None) or {})
        kwargs = {}
        for k, v in args.items():
            if k in alias and alias[k] is None:
                continue
            kwargs[alias.get(k, k)] = v
        kwargs[spec.inject] = rc.RESOLVERS[spec.inject](None)

        class _P:
            pass

        pr = _P()
        for k, v in args.items():
            setattr(pr, k, v)
        pr.response_format = None
        try:
            if getattr(spec, "pre_call", None) is not None:
                R["pre_call_ret"] = spec.pre_call(pr)
        except Exception as exc:                                          # noqa: BLE001
            R["pre_call_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        R["marks_after_precall"] = {str(m): int(_g(_g(doc, "SelectionManager"),
                                                   "GetSelectedObjectCount2", m) or 0)
                                    for m in (1, 2, 4)}
        mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
        ret = getattr(mod, spec.function)(**kwargs)
        R["ret_type"] = type(ret).__name__
        if isinstance(ret, dict):
            R["ret_raw"] = {k: str(v)[:120] for k, v in ret.items()}
            R["ret_ok"] = bool(ret.get("ok"))
        R["features_after"] = list(P.feature_names(doc) or [])
        R["new_features"] = [n for n in R["features_after"] if n not in names]
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:250])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["built"] = bool(R.get("new_features"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
