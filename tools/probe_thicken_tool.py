"""★ 真机验证：新工具 `solidworks_thicken` 能否**按工具层契约**建成加厚。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。规格 `specs/202-user-coverage-gaps` 的 **R6+**。
# 文件:   tools/probe_thicken_tool.py
# 定位:   ★ 本工具是 **R4「E 类换名重查」** 的产出落地（`recon/r4-e-class-rename-looku
#           p.md`）：
#   `IFeatureManager.FeatureBossThicken`（**7 参·未废弃**）/ `FeatureCutThicken`（**6 参·未废弃**）。
#   ★★ **必须真机验**：这两个成员**此前从没在本仓跑过**。
#   官方依据: `C:\swapi\types\IFeatureManager\FeatureBossThicken.md` · `FeatureCutThicken.md`
#     （Remarks 逐字：参考面必须按 **mark=1** 选中 · `FillVolume=true` 时**其余参数被忽略**且**必须闭合曲面**）
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

OUT = REPO / "output" / "thicken-tool-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _mk_surface(doc):
    """★ 造一张曲面体（★ 与展平那条探针同一手法）。"""
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
    row: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    specs = {getattr(s, "name", None): s for s in RC.all_specs()}
    for tool, args in (("solidworks_thicken", {"thickness_mm": 2.0, "cut": False, "direction": 0,
                                               "fill_volume": False, "merge": True,
                                               "use_feat_scope": True, "use_auto_select": True}),):
        r: dict = {"tool": tool}
        doc = None
        try:
            doc = C.new_document(sw, "part")
            r["mk_surface"] = bool((_mk_surface(doc) or {}).get("ok"))
            r["surface_bodies"] = len(list(_g(doc, "GetBodies2", 1, True) or []))
            spec = specs.get(tool)
            if spec is None:
                r["ok"] = False
                r["err"] = "★ 工具没注册"
            else:
                mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
                fn = getattr(mod, spec.function)
                want = {getattr(pp, "name", None) for pp in (spec.params or [])}
                kwargs = {k: v for k, v in args.items() if k in want}
                kwargs[spec.inject] = RC.RESOLVERS[spec.inject](None)
                r["call_path"] = "module=%s function=%s inject=%s params=%s" % (
                    spec.module, spec.function, spec.inject, sorted(kwargs))
                ret = fn(**kwargs)
                if isinstance(ret, dict):
                    for k in ("ok", "preconditions_held", "ret_name", "ret_type", "ret_is_none",
                              "new_features", "body_type", "member", "error"):
                        if k in ret:
                            r[k] = ret[k]
                r["ok"] = bool(r.get("ok"))
        except Exception as exc:                                          # noqa: BLE001
            r["ok"] = False
            r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:                                             # noqa: BLE001
                pass
        row[tool] = r
    row["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
