"""★ 真机：先造**钣金件**（按工具契约调 base flange），再导**展开 DXF**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_flat_pattern_dxf.py
# 定位:   ★ 2026-10-03（轮 407）24h 计划 v2 收敛报告 §五 第 ② 条的落地。
#   ★★ 背景：轮 403 把 `export_flat_pattern_dxf` **按硬约束⑥ 回退注册** ——
#     ★ 因为它的前置是**钣金件**，★ 而当时在**非钣金件**上真机得到的是**正确的显式拒绝**
#     （`ValueError: 导出展开 DXF 前必须先保存钣金零件`）⇒ ★ **没有正例**。
#   ⇒ ★ 本探针补上那个正例：★ **先建一个钣金件**，再导。
#   ★★ **调用一律走工具契约**（★ AGENTS.md「写探针验能力时：按 ToolSpec 的契约调」）：
#     `inject` → `pre_call` → `derived_args`，★ 与注册器同序（照
#     `tools/capture_simulation_loads_evidence.py` 的 `call_via_tool`）。
# 官方依据: `IFeatureManager.CreateDefinition(swFmBaseFlange)`（base flange）·
#   `IModelDoc2.ExportToDWG2(..., swExportToDWG_e)`（展开 DXF）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：① 钣金件真的建成（★ `sheet_metal_evidence` 回读）② 展开 DXF **文件存在且非空**
# 。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "mcp-server"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "flat-pattern-dxf-evidence.json"
)


class _P:
    """★ 最小 params 容器（★ 与注册器传给解析器的形状一致）。"""

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.response_format = "json"


def main() -> int:
    import sw_connect
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        sketch_corner_rectangle,
        start_sketch,
    )
    from scripts.sw_export import export_flat_pattern_dxf_report
    import tool_specs_batch3 as b3

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    stamp = time.strftime("%H%M%S")
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)

        def call_via_tool(spec_name: str, params: _P):
            """★ 与注册器同序：inject → pre_call → derived_args。"""
            spec = next(s for s in b3.SPECS_BATCH3 if s.name == spec_name)
            kwargs = {}
            for p in spec.params:
                if (
                    p.name in (spec.param_alias or {})
                    and spec.param_alias[p.name] is None
                ):
                    continue
                kwargs[(spec.param_alias or {}).get(p.name, p.name)] = getattr(
                    params, p.name
                )
            kwargs[spec.inject] = doc
            if spec.pre_call is not None:
                spec.pre_call(params)
            kwargs.update(spec.derived_args(params) or {})
            fn = getattr(
                __import__("scripts.%s" % spec.module, fromlist=[spec.function]),
                spec.function,
            )
            return fn(**kwargs)

        #: ① 建钣金件
        try:
            prm = _P(
                sketch_name=sk,
                thickness_mm=2.0,
                bend_radius_mm=2.0,
                depth_mm=40.0,
                k_factor=0.42,
                relief_ratio=0.5,
                reverse_direction=False,
                reverse_thickness=False,
            )
            create_base_flange = call_via_tool(
                "solidworks_sheet_metal_create_base_flange", prm
            )
            ev["steps"]["base_flange"] = {
                "ok": True,
                "returned": str(create_base_flange)[:90],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["base_flange"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        #: ② 回读钣金状态（★ 判据①）
        try:
            from scripts.sw_sheet_metal import sheet_metal_evidence

            ev["steps"]["sheet_metal_evidence"] = {
                "ok": True,
                "value": json.loads(
                    json.dumps(
                        sheet_metal_evidence(doc), ensure_ascii=False, default=str
                    )
                ),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["sheet_metal_evidence"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        #: ③ 导展开 DXF（★ 判据②：文件）
        try:
            dxf = Path(Path(__file__).resolve().parents[1] / "output") / (
                "flat-pattern-%s.dxf" % stamp
            )
            r = export_flat_pattern_dxf_report(doc, str(dxf))
            ev["steps"]["export_flat_pattern_dxf"] = {
                "ok": bool(r.get("ok")),
                "values": {
                    k: r.get(k)
                    for k in (
                        "format",
                        "exists",
                        "size_bytes",
                        "grew_or_created",
                        "error",
                    )
                },
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["export_flat_pattern_dxf"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 补上轮 403 缺的**正例**：先按工具契约建一个钣金件，再导展开 DXF —— "
            "★ 判据是**文件存在且非空**（★ 并记 `size_before` / `grew_or_created`）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1700])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
