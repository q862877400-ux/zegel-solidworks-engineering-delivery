r"""@brief 验收命令：`costing` 的端到端真机闭环（**A9 的可跑工程实现**）。

## 为什么有它
`capabilities.yaml` 的 `costing` 是护城河三域里**唯一有实现却停在 `stitched`** 的一条 ——
因为**没有测试、没有运行证据**（`AGENTS.md §一 A4`：`verified` 必须有我们自己的运行证据）。

本脚本就是那条证据：**从零建零件 → 拿 CostManager → 读模板/材质 → 出成本数字 → 收尾**，
并把结果落成 `output/costing-evidence.json`（**含时间戳与版本**，可复核）。

## 已知的坑（都在本脚本里处理了）
1. **入口是 `GetCostingManager()`，不是 `GetAddInObject(<ProgID>)`** ——
   实测 4 个 ProgID（含 `swcCostingAddin.SwcAddin`）**全返 None**。
2. **`CreateCostAnalysis(name)` 返 None 但分析确实建了**（SolidWorks「返回码撒谎」家族）
   ⇒ 判据取 `GetCostAnalysis() is not None`，**不看** `CreateCostAnalysis` 的返回值。
3. **`CostingModel` 就是 `CostPart`**（duck-typing）；`UpdateCostForAllBodies` 在它上面**取不到**
   ⇒ 不做那一步，成本由 `GetCostAnalysis()` 直接给出。
4. **数值不能用 `or` 取**（`0 or -1` ⇒ `-1`）—— 本脚本用修好的 `read_cost_analysis`。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_costing_e2e.py
# 定位:   `capabilities.yaml` 的 `costing` 条目里 `evidence` 字段指向的就是本脚本。
# 官方签名依据: `IModelDocExtension::GetCostingManager` / `ICostManager` / `ICostPart` /
#         `ICostAnalysis` 的官方反射（`D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt` 等）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只用自己新建的文档**；收尾恢复 CommandInProgress 并关自己的文档。
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import (
    sw_costing,  # noqa: E402
    sw_part,  # noqa: E402
)
from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
)

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "costing-evidence.json")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收脚本的执行体）
# 文件:   tools/verify_costing_e2e.py → main()
# 定位:   端到端取证：建零件 → GetCostingManager（**唯一正解**）→ 模板/材质默认值
#         → CostingModel（= CostPart）→ GetCostAnalysis → read_cost_analysis 出成本数字。
# ⚠ **来源块为什么又写一份在 main() 前面**：`scripts/check_provenance.py` 的
#   `_module_docstring_lines()` 会把**模块 docstring 里的行整段跳过**（视为散文），
#   所以写在 docstring 内的那一份**不被认作覆盖** —— 而这个文件的主要代码在 `main()` 里。
#   ⇒ 覆盖没上去 ⇒ 门禁报「72 行新增代码没有可追溯的出处」（2026-10-01 轮 61 实测）。
# ⚠ 判据（本函数里全部照官方反射，**不猜**）：
#   * `IModelDocExtension::GetCostingManager()` **零参**，返回 `Object`；
#   * `ICostManager`：`get_CostingDefaults` / `get_CostingModel` /
# `GetTemplateCount(Int32)` / `GetTemplatePathnames(Int32)` / `Close()` / `WaitForUIUpda
# te()`；
# * `ICostPart`：`GetBodyCount()` / `GetBodies()` / `GetCostAnalysis()` / `CreateCostAna
# lysis(String)`；
# * `ICostAnalysis`：23 个成员（`get_CostingType` / `GetMaterialCost` / `GetTotalCostToM
# anufacture` …）。
# ⚠ **判据不看 `CreateCostAnalysis` 的返回值** —— 它返 `None` 但分析确实建了
#   （SolidWorks「返回码撒谎」家族）；判据取 `GetCostAnalysis() is not None`。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只用自己新建的文档；收尾恢复 CommandInProgress。
# 覆盖:   本文件全部代码
# ────────────────────────────────────────────────────────────────────
def main() -> int:
    sw, _m, meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    evidence: dict = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        #: ★★ 2026-10-07（接手轮 · 规格 216）：★ 原来是 `str(meta.get("revision", ""))`
        #: ——
        #: ★ 两处都不稳：① `connect_solidworks` 的 metadata **当时根本没有 `revision` 键
        #: **
        #: （★ 已在 `scripts/sw_connect.py` 补上）；② ★ 万一值为 `None`，`str(None)` 会
        #: 写成
        #: **字符串 `"None"`** ✗ ⇒ ★ 这里加 `or ""`：★ **取不到就是空串，不写 `"None"`**
        #:  ✓
        "solidworks_revision": str((meta or {}).get("revision") or ""),
        "verdict": "unknown",
        "steps": {},
    }
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        evidence["steps"]["build_part"] = {
            "title": str(title),
            "size_mm": [100, 60, 20],
        }

        # ① 入口（**唯一正解**）
        mgr = sw_costing.get_costing_manager(model)
        evidence["steps"]["get_costing_manager"] = {"ok": mgr is not None}
        if mgr is None:
            evidence["verdict"] = "fail: GetCostingManager 返回 None"
            return 1

        # ② 模板（两个类别）
        tpl: dict = {}
        for cat in (0, 1):
            tpl[str(cat)] = {
                "count": sw_costing._checked(mgr, "GetTemplateCount", cat),
                "pathnames": [
                    str(p)
                    for p in (
                        sw_costing._checked(mgr, "GetTemplatePathnames", cat) or ()
                    )
                ],
            }
        evidence["steps"]["templates"] = tpl

        # ③ 默认值（材质 / 材质类 / 加工方式）
        defaults = sw_costing.get_costing_defaults(mgr)
        evidence["steps"]["defaults"] = {
            "template_name_0": str(
                get_com_member(defaults, "GetTemplateName", 0) or ""
            ),
            "material_name_0": str(
                get_com_member(defaults, "GetMaterialName", 0) or ""
            ),
            "material_class_0": str(
                get_com_member(defaults, "GetMaterialClass", 0) or ""
            ),
            "manufacturing_method_0": int(
                sw_costing._num(defaults, "GetManufacturingMethod", -1, 0)
            ),
        }

        # ④ 部分 + 成本（⚠ 判据是 GetCostAnalysis 非 None，**不看** CreateCostAnalysis
        # 的返回）
        part = sw_costing.get_costing_model(mgr)
        evidence["steps"]["bodies"] = {
            "count": sw_costing.get_body_count(part),
        }
        sw_costing.create_cost_analysis(part, "MCP_COSTING_E2E")
        analysis = sw_costing.get_cost_analysis(part)
        if analysis is None:
            evidence["verdict"] = "fail: GetCostAnalysis 返回 None"
            return 1
        costs = sw_costing.read_cost_analysis(analysis)
        evidence["steps"]["cost_analysis"] = costs

        sw_costing.close_costing(mgr)
        evidence["steps"]["close"] = {"ok": True}

        # ⑤ 判据：**出得来成本数字** + `costing_type` **没有被 -1 吞掉**
        total = float(costs.get("total_to_manufacture") or 0.0)
        ct = costs.get("costing_type")
        ok = total > 0 and ct is not None and ct >= 0
        evidence["verdict"] = (
            "pass"
            if ok
            else ("fail: total_to_manufacture=%.6f, costing_type=%r" % (total, ct))
        )
        evidence["assertions"] = {
            "total_to_manufacture_gt_0": total > 0,
            "costing_type_is_a_real_value": ct is not None and ct >= 0,
            "template_is_a_costing_template": ".sldct"
            in str(costs.get("template", "")),
        }
        return 0 if ok else 1
    finally:
        evidence["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print("  证据已写: %s" % OUT)
        print("  verdict: %s" % evidence["verdict"])
        for k in ("total_to_manufacture", "costing_type", "template", "currency_name"):
            if k in evidence.get("steps", {}).get("cost_analysis", {}):
                print("    %-24s = %r" % (k, evidence["steps"]["cost_analysis"][k]))


if __name__ == "__main__":
    raise SystemExit(main())
