r"""@brief 探针 ③：从 CostManager 走到**真实成本数字**（`read_cost_analysis` 的 17 项）。

## 探针 ①② 的结果（2026-10-01 轮 61，真机）
```
Extension.GetCostingManager() ⇒ 非 None
GetTemplateCount(0/1) ⇒ 2 / 2；GetTemplatePathnames 给出 4 条 .sldctc/.sldcts 路径
GetMaterialName(0) ⇒ '普通碳钢'；GetMaterialClass(0) ⇒ '钢'；GetManufacturingMethod(0) ⇒ 0
CostingModel ⇒ 非 None 且 **就是 CostPart**（GetBodies()/GetBodyCount() 在它上面通）
ⓘ CreateCostAnalysis(name) ⇒ None，而 GetCostAnalysis() ⇒ **非 None**
  ⇒ ⚠ SolidWorks「返回码撒谎」家族的又一例：**建了但返回 None**
```
⇒ 本探针补上**缺的那一步**：从 `GetCostAnalysis()` 拿对象，再 `read_cost_analysis` 出**真数字**。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_costing_numbers.py
# 定位:   AGENTS.md 铁律 2 的第二关。签名依据
#         `ICostAnalysis`（23 成员）/ `ICostPart` / `ICostManager` 的官方反射。
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


def step(label, fn):
    try:
        v = fn()
        print("   %-38s ⇒ %r" % (label, v))
        return v
    except Exception as exc:  # noqa: BLE001
        print("   %-38s ⇒ ✗ %s: %s" % (label, type(exc).__name__, str(exc)[:95]))
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

        mgr = get_com_member(get_com_member(model, "Extension"), "GetCostingManager")
        if mgr is None:
            print("   ⚠ CostManager 仍为 None ⇒ 停")
            return 1
        print("   CostManager ⇒ 非 None")

        part = sw_costing.get_costing_model(mgr)
        print("   CostPart（= CostingModel）⇒ %s" % ("非 None" if part is not None else "None"))
        if part is None:
            return 1

        print()
        print("=== ① 先让它算一遍成本 ===")
        step("UpdateCostForAllBodies()", lambda: sw_costing.update_cost_for_all_bodies(part))
        step("WaitForUIUpdate()", lambda: sw_costing.wait_for_ui_update(mgr))

        print()
        print("=== ② 从 GetCostAnalysis() 拿对象 ===")
        analysis = sw_costing.get_cost_analysis(part)
        print("   get_cost_analysis ⇒ %s" % ("**非 None**" if analysis is not None else "None"))
        if analysis is None:
            print("   ⚠ 仍为 None ⇒ 试 CreateCostAnalysis 后再取")
            step("CreateCostAnalysis('MCP_COST')",
                 lambda: sw_costing.create_cost_analysis(part, "MCP_COST"))
            analysis = sw_costing.get_cost_analysis(part)
            print("   再取 ⇒ %s" % ("非 None" if analysis is not None else "None"))
        if analysis is None:
            return 2

        print()
        print("=== ③ ★ 读真成本（read_cost_analysis 的 17 项）===")
        data = sw_costing.read_cost_analysis(analysis)
        for k in sorted(data):
            print("   %-24s = %r" % (k, data[k]))

        print()
        print("=== ④ 逐条直接读（对照 read_cost_analysis，防它自己有漏）===")
        for m in ("CostingTemplateName", "CostingType", "CurrencyCode", "CurrencyName",
                  "LengthUnit", "MassUnit", "LotSize", "TotalQuantity",
                  "MarkUpType", "MarkUpPercent", "GetMaterialCost",
                  "GetManufacturingCost", "GetSetupCost",
                  "GetTotalCostToManufacture", "GetTotalCostToCharge"):
            step("analysis.%s" % m, lambda mm=m: get_com_member(analysis, mm))

        print()
        print("=== ⑤ collect_costing_evidence（模块的门面）===")
        print("   %r" % sw_costing.collect_costing_evidence(part))

        print()
        step("close_costing()", lambda: sw_costing.close_costing(mgr))
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
