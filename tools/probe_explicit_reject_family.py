"""★ 真机取证：`solidworks_part_sweep` 等「显式拒」四条，**经工具层必然失败**（区无路可给）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的质量线。
# 文件:   tools/probe_explicit_reject_family.py
# 定位:   ★★★ bunny 的 `recon/preselect-family-merged.md` 点名这一族为「**显式拒**」：
#   目标函数**读到选区计数为 0 就 `return {"ok": False, "stage": "selection"}`**。
#   ★★ 而它们的 spec **既没有 `selection` 类参数、也没有 `pre_call`**（本探针先静态断言这一点）
#   ⇒ ★★ **调用方根本无从提供选区** ⇒ 经工具层**必然失败**（★ 与事实 502 的 11 条注入键同族）。
#   官方依据: `scripts/sw_sweep.py` 的 `create_sweep_report` docstring 逐字
#     「用选中的「轮廓（mark=1）+ 路径（mark=4）」建扫描特征」+
#     `C:\\swapi\\types\\IFeatureManager\\CreateDefinition.md`（`swFmSweep`）
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "explicit-reject-family-evidence.json"
FAMILY = ["solidworks_part_sweep", "solidworks_part_loft",
          "solidworks_part_axis", "solidworks_part_wrap"]


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "static": [], "calls": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    import register_capabilities as rc
    specs = {getattr(s, "name", None): s for s in rc.all_specs()}

    #: ★★ ① 静态：这一族**有没有给调用方留"给选区"的路**
    for n in FAMILY:
        s = specs.get(n)
        if s is None:
            R["static"].append({"tool": n, "registered": False})
            continue
        params = [getattr(p, "name", None) for p in (s.params or [])]
        R["static"].append({
            "tool": n, "registered": True, "inject": s.inject,
            "pre_call": getattr(getattr(s, "pre_call", None), "__name__", None),
            "derived_args": bool(getattr(s, "derived_args", None)),
            "params": params,
            "has_selection_like_param": any(
                k and ("select" in k.lower() or "sketch" in k.lower() or "face" in k.lower()
                       or "profile" in k.lower() or "path" in k.lower()) for k in params),
        })

    #: ★★ ② 真机：造一个"轮廓 + 路径"两条草图的件，★ **按契约调**（不预选任何东西）
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.01)
        P.end_sketch(doc)
        P.start_sketch(doc, plane_name="Right Plane")
        _g(_g(doc, "SketchManager"), "CreateLine", 0.0, 0.0, 0.0, 0.0, 0.06, 0.0)
        P.end_sketch(doc)
        R["setup_features"] = list(P.feature_names(doc) or [])
        try:
            _g(doc, "ClearSelection2", True)
        except Exception:                                                 # noqa: BLE001
            pass
        R["marks_before_call"] = {str(m): int(_g(_g(doc, "SelectionManager"),
                                                 "GetSelectedObjectCount2", m) or 0)
                                  for m in (0, 1, 2, 4)}
        for n in FAMILY:
            s = specs.get(n)
            row: dict = {"tool": n}
            if s is None:
                row["skip"] = "★ 没注册"
                R["calls"].append(row)
                continue
            try:
                kwargs = {s.inject: rc.RESOLVERS[s.inject](None)}
                mod = __import__("scripts.%s" % s.module, fromlist=[s.function])
                ret = getattr(mod, s.function)(**kwargs)
                row["ret_stage"] = (ret or {}).get("stage") if isinstance(ret, dict) else None
                row["ret_ok"] = (ret or {}).get("ok") if isinstance(ret, dict) else None
                row["ret_error"] = str((ret or {}).get("error", ""))[:150] if isinstance(ret, dict) else str(ret)[:80]
                row["new_features"] = [x for x in (P.feature_names(doc) or [])
                                       if x not in (R.get("setup_features") or [])]
            except Exception as exc:                                      # noqa: BLE001
                row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
            R["calls"].append(row)
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["any_has_selection_param"] = any(x.get("has_selection_like_param") for x in R["static"])
    R["any_has_pre_call"] = any(x.get("pre_call") for x in R["static"])
    R["verdict"] = ("★★ 四条**既无 selection 参数、又无 pre_call** ⇒ ★ 调用方无从给选区 ⇒ **经工具层必然失败**"
                    if not R["any_has_selection_param"] and not R["any_has_pre_call"]
                    else "★ 至少一条有给选区的路 —— 需逐条看")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
