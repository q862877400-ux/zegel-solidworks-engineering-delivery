r"""@brief 探针 ②：走通 `CostManager → CostingModel/CostingDefaults → 模板名 → CostAnalysis`。

## 探针 ① 的结果（2026-10-01 轮 61，真机）
```
Extension.GetCostingManager() ⇒ **非 None**          ← 入口打通
CostingDefaults / CostingModel ⇒ COMObject
GetTemplateCount(0) ⇒ **2**                          ← 本机有 2 个模板
WaitForUIUpdate() ⇒ None（void）
GetAddInObject(<4 个 ProgID>) ⇒ **全 None**           ← 那条路死
```
⇒ 本探针继续往**出数字**走：模板名 → 建 CostAnalysis → 读成本。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_costing_flow.py
# 定位:   AGENTS.md 铁律 2 的第二关。签名依据 `IModelDocExtension::GetCostingManager` /
#         `ICostManager` / `ICostPart` / `ICostAnalysis` 的官方反射。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只用自己新建的文档**；收尾恢复 CommandInProgress 并关自己的文档。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(r"C:\swprojects\sw-skill-fork")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
)
from scripts import sw_part  # noqa: E402
from scripts import sw_costing  # noqa: E402


def try_(label, fn):
    """跑一个可能失败的动作 ⇒ 打印结果或异常（探针就是要看全部形态）。"""
    try:
        v = fn()
        print("   %-34s ⇒ %r" % (label, v))
        return v
    except Exception as exc:  # noqa: BLE001
        print("   %-34s ⇒ ✗ %s: %s" % (label, type(exc).__name__, str(exc)[:90]))
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("=== 自建零件: %r ===" % title)

        ext = get_com_member(model, "Extension")
        mgr = get_com_member(ext, "GetCostingManager")
        print("   CostManager ⇒ %s" % ("非 None" if mgr is not None else "None"))
        if mgr is None:
            return 1

        print()
        print("=== ① 模板（category 0 与 1 都试）===")
        for cat in (0, 1):
            try_("GetTemplateCount(%d)" % cat, lambda c=cat: sw_costing._checked(mgr, "GetTemplateCount", c))
            try_("GetTemplatePathnames(%d)" % cat,
                 lambda c=cat: sw_costing._checked(mgr, "GetTemplatePathnames", c))
        print()
        print("=== ② CostingDefaults 上有什么（读默认值）===")
        defaults = sw_costing.get_costing_defaults(mgr)
        if defaults is not None:
            for m in ("GetTemplateName", "GetMaterialName", "GetManufacturingMethod", "GetMaterialClass"):
                for cat in (0,):
                    try_("%s(%d)" % (m, cat), lambda mm=m, c=cat: get_com_member(defaults, mm, c))
        print()
        print("=== ③ CostingModel ⇒ CostPart ===")
        cmodel = sw_costing.get_costing_model(mgr)
        print("   CostingModel ⇒ %s" % ("非 None" if cmodel is not None else "None"))
        if cmodel is not None:
            part = try_("CostingModel.CostPart", lambda: get_com_member(cmodel, "CostPart"))
            if part is None:
                # 有的版本是 CostingModel 本身就是 CostPart
                part = cmodel
            try_("CostPart.Bodies", lambda: get_com_member(part, "Bodies"))
            try_("CostPart.GetBodies()", lambda: sw_costing.get_bodies(part))
            try_("CostPart.GetBodyCount()", lambda: sw_costing.get_body_count(part))
            print()
            print("=== ④ 建 CostAnalysis 并读成本 ===")
            analysis = sw_costing.create_cost_analysis(part, "MCP_COST_%s" % title)
            print("   create_cost_analysis ⇒ %s" % ("非 None" if analysis is not None else "None"))
            if analysis is not None:
                for m in ("TotalCost", "CostPerUnitMass", "CurrencyCode", "CostingType", "CostingTemplateName"):
                    try_("analysis.%s" % m, lambda mm=m: get_com_member(analysis, mm))
                try_("read_cost_analysis", lambda: sw_costing.read_cost_analysis(analysis))
            print()
            print("=== ⑤ 证据回读（模块的公开入口）===")
            try_("collect_costing_evidence", lambda: sw_costing.collect_costing_evidence(part))
        print()
        print("=== ⑥ Close（收尾）===")
        try_("close_costing", lambda: sw_costing.close_costing(mgr))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print()
        print("收尾完成（文档未保存；CommandInProgress 已恢复）")


if __name__ == "__main__":
    raise SystemExit(main())
