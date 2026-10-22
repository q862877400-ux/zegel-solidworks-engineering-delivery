"""★ 真机验证 `solidworks_fillet` 的 `pre_call`：★ 声明式 `selection` ⇒ 选上 ⇒ **建成**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的质量线。
# 文件:   tools/probe_fillet_precall_e2e.py
# 定位:   ★★★ 事实 503 的正解是「前置写成 `pre_call`」（★ 只有它跑在注入之后），
#   而仓内**最早、最规范**的那份就是 `solidworks_fillet` / `solidworks_chamfer` 用的
#   `_select_edge` ⇒ ★ 本探针**按工具层契约**调 `solidworks_fillet`，看那条路真的能建成。
# ★ 若成 ⇒ ★ 这是「**`pre_call` + `resolve_selection` 对零件特征有效**」的**第一条端到端
# 证据**；
#   ★ 若不成 ⇒ ★ 把它记成**否定结果**，并说明卡在哪一步。
# 官方依据: `c:\\swapi\\types\\IFeatureManager\\FeatureFillet3.md`（★ 末位是变体数组，非
# 预选）
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
from scripts import sw_part as P  # noqa: E402

OUT = REPO / "output" / "fillet-precall-e2e-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    import importlib

    rc = importlib.import_module("register_capabilities")
    spec = next(
        (s for s in rc.all_specs() if getattr(s, "name", None) == "solidworks_fillet"),
        None,
    )
    if spec is None:
        R["err"] = "★ 找不到 solidworks_fillet"
        OUT.write_text(
            json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
        )
        return 0
    R["call_path"] = "module=%s function=%s inject=%s pre_call=%s" % (
        spec.module,
        spec.function,
        spec.inject,
        getattr(spec.pre_call, "__name__", None),
    )
    R["params"] = [getattr(p, "name", None) for p in (spec.params or [])]
    for sel in ("index:0", "index:4"):
        doc = None
        row: dict = {"selection": sel}
        try:
            doc = c.new_document(sw, "part")
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
            row["tree_before"] = list(P.feature_names(doc) or [])
            #: ★★ **按工具层契约调**：param_alias → 注入 → pre_call → derived_args → 目
            #: 标函数
            args = {"selection": sel, "radius_mm": 2.0}
            alias = dict(getattr(spec, "param_alias", None) or {})
            want = {getattr(p, "name", None) for p in (spec.params or [])}
            kwargs = {}
            for k, v in args.items():
                if k in want:
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
            pre_ok = None
            try:
                if getattr(spec, "pre_call", None) is not None:
                    pre_ok = spec.pre_call(pr)  #: ★ 这是本探针要验的那一步
                row["pre_call_returned"] = pre_ok
                row["sel_after_precall"] = int(
                    _g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0
                )
            except Exception as exc:  # noqa: BLE001
                row["pre_call_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
            if getattr(spec, "derived_args", None) is not None:
                kwargs.update(spec.derived_args(pr) or {})
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            ret = getattr(mod, spec.function)(**kwargs)
            #: ★ 修：`ret` 不一定是 dict（★ 上一版直接 `.items()` ⇒ `AttributeError: <un
            #: known>.items`）。
            row["ret_type"] = type(ret).__name__
            row["ret_ok"] = bool(isinstance(ret, dict) and ret.get("ok"))
            if isinstance(ret, dict):
                row["ret_keys"] = {
                    k: str(v)[:70]
                    for k, v in ret.items()
                    if k
                    in (
                        "ok",
                        "ret_name",
                        "ret_type",
                        "new_features",
                        "err",
                        "error",
                        "preconditions_held",
                        "selection",
                        "feature_name",
                    )
                }
            else:
                row["ret_repr"] = str(ret)[:120]
            #: ★ 修：树要在 **CloseDoc 之前**读（★ 上一版读到 0 —— 文档已关）。
            row["tree_after"] = list(P.feature_names(doc) or [])
            row["new_features"] = [
                n for n in row["tree_after"] if n not in row["tree_before"]
            ]
            row["ok"] = len(row["new_features"]) > 0
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
