"""把 `costing` 从 `stitched` 升到 `verified`（**附真机证据**）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

NEW_LIMITS = [
    "⚑ **护城河域之一** —— `AGENTS.md §〇`：「经核实真正全网空白的只有**拓扑优化、动画导出（AVI）、Costing** 三个」。",
    "⚑ **2026-10-01（轮 61）完整闭环真机跑通**（SW 2026 SP4.1）：自建 100×60×20 mm 单实体板 → "
    "`Extension.GetCostingManager()` 拿到 CostManager → 两个类别共 **4 条模板路径**（`.sldctc` / `.sldcts`）"
    " → 默认材质 **`普通碳钢`** / 材质类 **`钢`** → `CostingModel`＝`CostPart`（**1 个 body**）"
    " → `GetCostAnalysis()` 非空 → **`total_to_manufacture = 3.2714499345031918`（USD）**。"
    "证据文件：`D:\\AI\\SW\\output\\costing-evidence.json`（含时间戳与版本）。",
    "⚑ **验收命令**（可复跑）：`python tools/verify_costing_e2e.py` ⇒ 期望 `verdict: pass`。",
    "⚠⚠ **本条的入口问题曾被写错、并因此长期停在 `stitched`**：旧文写「CostManager 由 **Composer 加载项**给出，"
    "**本机没装 Composer**，ProgID 查不到 ⇒ 本模块接收调用方传入的对象」。"
    "**两条硬证据推翻**：① 官方反射里**有** `IModelDocExtension::GetCostingManager()`；"
    "② 注册表里**有** `swcCostingAddin.SwcAddin`（`.34`）等 8 个 ProgID ⇒ **Costing 加载项本机装了**。"
    "ⓘ **「4 个 ProgID 全返 None」这个观察是对的**，但**结论「所以拿不到」是错的** —— "
    "`GetAddInObject` 本来就不是正解。**⇒ 把「某条路走不通」写成「对象拿不到」，会让模块放弃唯一的正解。**",
    "⚠ **`CreateCostAnalysis(name)` 返 `None` 但分析确实建了**（SolidWorks「返回码撒谎」家族的又一例）"
    "⇒ 判据取 `GetCostAnalysis() is not None`，**不看** `CreateCostAnalysis` 的返回值。",
    "⚠ **`UpdateCostForAllBodies` 在 `CostingModel` 对象上取不到**（`AttributeError`），"
    "虽然反射里它挂在 `ICostPart` 上；而 `GetBodies` / `GetBodyCount` / `GetCostAnalysis` 在同一个对象上**都通**。"
    "⇒ 暂按「`CostingModel` 就是 `CostPart`」用，**不额外调 `UpdateCostForAllBodies`**（成本由 `GetCostAnalysis()` 直接给出）。",
    "✅ **2026-10-01（轮 61）修掉一个真缺陷**：`read_cost_analysis` 等 7 处写的是 `int(x or -1)` —— "
    "`CostingType` 真值为 **`0`** 时会被吞成 **`-1`**（把「机加工」误报成「未知」）。"
    "⇒ 改用 `_num()`（**只有 `None` 才回落**）。**修复由真机证明**：修前 `costing_type=-1`，修后 **`0`**。"
    "⚠ 全仓**同族共 45 处 / 11 个模块**（其余 38 处**如实记录、未改**，见 ROADMAP 游标）。",
    "⚠ **`scripts/sw_api_sldcostingapi.py`（486 行）是 API 索引，不是实现** —— 两者不要混。",
    "⚠ **`GetTemplateCount` / `GetTemplatePathnames` 的 Int32 参数语义官方无文档**（本机实测：0 ⇒ 多实体类，1 ⇒ 钣金类）。",
]

EV = [
    "python tools/verify_costing_e2e.py（⇒ verdict: pass；证据 output/costing-evidence.json）",
]


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "往返不是逐字节相同 ⇒ 停"

    c = next(x for x in d["capabilities"] if x["id"] == "costing")
    old_level = c["level"]
    c["level"] = "verified"
    c["verified_versions"] = ["2026"]
    c["limitations"] = NEW_LIMITS
    c["evidence"] = EV
    #: 真机证据 ⇒ 授权可放宽到 unattended（与其它 verified 一致）
    c["allowed_modes"] = ["interactive", "reviewed", "unattended"]
    c["source"] = "original"
    c["source_evidence"] = (
        "唯一实现模块 `scripts/sw_costing.py` **不在** `origin/main`"
        "（硬证据 `git cat-file -e origin/main:scripts/sw_costing.py` 不通过）"
        "⇒ 代码是我们新增的；且**无** `provenance` ⇒ 与 `source: original` 自洽（R13）。"
        "2026-10-01（轮 61）真机跑通完整闭环 ⇒ 升 verified")

    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    a = next(x for x in after["capabilities"] if x["id"] == "costing")
    from collections import Counter
    print("  costing: level %s → **%s** · verified_versions=%s · evidence=%d 条"
          % (old_level, a["level"], a["verified_versions"], len(a["evidence"])))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    print("  护城河三域：")
    for mid in ("topology_optimization", "costing", "animation_export"):
        x = next(y for y in after["capabilities"] if y["id"] == mid)
        print("    %-24s %s / %s" % (mid, x["level"], x["source"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
