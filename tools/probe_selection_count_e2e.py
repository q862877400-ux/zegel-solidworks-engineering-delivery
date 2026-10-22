"""★ 验证 bunny 的洞察：★ 诊断型工具（`selection_count` 等）经工具层**永远报 0**（事实 503 的另一种受害者）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的质量线。
# 文件:   tools/probe_selection_count_e2e.py
# 定位:   ★★★ 这是 `recon/preselect-family-merged.md` §四 提出的**洞察**：
# `selection_count` / `resolve_selection` / `selection_point` / `resolve_entity` / `curr
# ent_selection`
#   **不是"缺 pre_call"**，而是 **`inject="model"` 本身会清空它们要读的选区**
#   （★ 事实 503：`RESOLVERS["model"]` 经 `connect_solidworks()` 清选区）
#   ⇒ ★★ **它们经工具层永远报 0** —— 而我的判据当时把它们归为"只报告 ⇒ 无关"（★ 漏了）。
#   ★ 本探针把两件事分开测：① **先选**、② **经解析器**（复刻工具层的顺序）⇒ 看计数掉不掉。
#   官方依据: 不适用（本仓机制，事实 503）
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

OUT = REPO / "output" / "selection-count-e2e-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    r: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        p.start_sketch(doc, plane_name="Front Plane")
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
        p.end_sketch(doc)
        names = [n for n in (p.feature_names(doc) or []) if n.startswith("草图")]
        p.extrude_boss(doc, (names[-1] if names else "草图1"), 15.0)
        #: ① 先**选上**一条边（用仓内声明式解析）
        from scripts.sw_selection_spec import resolve_selection

        r["selected"] = resolve_selection(doc, "index:0", "EDGE")

        def count():
            return int(
                _g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0
            )

        r["count_after_select"] = count()
        #: ② ★★ 复刻工具层的顺序：**调 RESOLVERS["model"]**（= `resolve_model`）⇒ 看计数
        import register_capabilities as rc

        _m = rc.RESOLVERS["model"](None)
        r["resolver_returned"] = type(_m).__name__
        r["count_after_resolver"] = count()
        #: ③ 走**真正的诊断型工具**：`selection_count` 的 inject 就是 `model`
        spec = next(
            (
                s
                for s in rc.all_specs()
                if getattr(s, "name", None) == "solidworks_selection_count"
            ),
            None,
        )
        r["spec_inject"] = getattr(spec, "inject", None) if spec else None
        if spec is not None:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            kwargs = {spec.inject: rc.RESOLVERS[spec.inject](None)}
            ret = getattr(mod, spec.function)(**kwargs)
            r["selection_count_ret"] = (
                ret if isinstance(ret, (dict, int, str)) else str(ret)[:120]
            )
        r["verdict"] = (
            "★★ 解析器把 %d 清成了 %d ⇒ **诊断型工具经工具层永远读到 0**"
            % (r["count_after_select"], r["count_after_resolver"])
            if r["count_after_resolver"] < r["count_after_select"]
            else "★ 计数没掉 —— bunny 的洞察**不成立**（如实记）"
        )
    except Exception as exc:  # noqa: BLE001
        r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    r["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
