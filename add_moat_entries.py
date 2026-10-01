"""补两条能力条目：`costing`（护城河，实现存在但清单里没有）与 `animation_export`（护城河，API 存在但无实现）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力清单收敛）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml
#         依据：`D:\\AI\\SW\\AGENTS.md §〇`（护城河三域）与 `§一 A1/A9`
# 定位:   2026-10-01（轮 60）。★ **起因**：上轮游标的下一步写着
#         「`original` 只有 2 条，而 AGENTS.md 说护城河是**三条**（拓扑/动画 AVI/Costing）
#          ⇒ 查 Costing 与动画落在哪条能力」—— 一查发现**两条都不在清单里**：
#
#   | 护城河域 | 实现 | 清单条目 | 判定 |
#   |---|---|---|---|
#   | 拓扑优化 | `scripts/sw_topology.py` | `topology_optimization` | 达标（verified + original）|
#   | Costing | `scripts/sw_costing.py`（388 行，我们新增）| **无** | ⇒ 本轮补 `stitched` |
#   | 动画 AVI | **无**（只有 `sw_api_*` 的**索引**登记）| **无** | ⇒ 本轮补 `not_implemented` |
#
#   ⚠ **这为什么是 A1/A9 的真实缺口**：
#     · A9 要「空白域护城河**有可跑的工程实现**，不是只有文档」—— 清单里看不见 Costing
#       ⇒ **A9 无法判它**；
#     · A1 要「域覆盖矩阵里每一格**都有来源，或写明「不做 + 原因」**」—— 动画 AVI
#       **既没实现也没写「不做」** ⇒ 那一格是**空白**。
#     ⇒ 本轮把两者都变成**清单里看得见的状态**。
#
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 先证明 JSON 往返逐字节相同；跑完按**事实 61**看 `git diff --stat`。
# ⚠⚠ **每条 limitation 必须是**单行字符串字面量**（相邻字面量隐式拼接）——
#     我第一版写成了「跨行字面量」⇒ `SyntaxError: unterminated string literal`（**事实 48**）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
CAP = REPO / "capabilities.yaml"


def up(rel: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", "origin/main:%s" % rel],
                          check=False, capture_output=True, text=True).returncode == 0


COSTING_LIMITS = [
    "⚑ **护城河域之一** —— `AGENTS.md §〇`：「经核实真正全网空白的只有**拓扑优化、动画导出（AVI）、Costing** 三个」。",
    "⚠ 2026-10-01（轮 60）**新增本条**：此前 `scripts/sw_costing.py`（**388 行 / 10+ 公开入口 / 我们新增，上游没有**）**不在能力清单里**"
    " ⇒ `AGENTS.md §一 A9` 要的「空白域护城河**有可跑的工程实现**」在清单上**看不见它**。本条把状态变成**可判**。",
    "⚠ **零测试**：`tests/` 下**没有** `*cost*` 测试文件 ⇒ 按 `§九.6` 与 A4，**我们没有运行证据 ⇒ 只能 `stitched`，不得标 `verified`**。",
    "⚑ **静态签名已过**：`scripts/audit_call_arity.py` 在**传全 15 份反射**时对本模块是 **0 存疑 / 0 查不到**。"
    "⚠ 这条有个方法学前提：Costing 的成员在 **`sldcostingapi`** 程序集里，**只传 `sldworks` + `cosworks` 两份会把它们误报成「查不到」**"
    "（见 `docs/signature-audit.md` 批次 7 的教训）—— 实测里正是这样误报过 26 处。",
    "⚠ **`scripts/sw_api_sldcostingapi.py`（486 行）是 API 索引，不是实现** —— 两者不要混。",
    "⇒ **升 `verified` 需要**：一条真机端到端（建 Costing 管理器 → 选模板 → 赋材质/工艺 → 出成本）并把证据落盘。**这是本域下一步的明确动作。**",
]

ANIMATION_LIMITS = [
    "⚑ **护城河域之一**（`AGENTS.md §〇`：真正全网空白的三个域是拓扑优化、动画导出 AVI、Costing）。",
    "⚠ 2026-10-01（轮 60）**新增本条**，`level: not_implemented` —— 按 `AGENTS.md §一 A1`「域覆盖矩阵里本仓库每一格**都有来源，或写明「不做 + 原因」**」，"
    "**此前这一格是空白**（既无实现也未写「不做」）。",
    "⚠ **现状：只有 API 索引登记，没有实现层**。全仓实测：`scripts/` 里 **0 个**动画导出实现"
    "（`sw_motion.py` 的 10 个公开入口里**没有**动画导出，其 `limitations` 也不提动画）。",
    "⚑ **官方 API 侧不是「查不到」** —— 反射里**有** `get_/set_SaveEntireAnimation`（Boolean 属性），"
    "`sw_api_sldworks.py` 登记了 `IAnimation` / `PlayAnimation`，`sw_api_swmotionstudy.py` 登记了 `SaveEntireAnimation`。"
    "⚠ **但「索引里登记了成员」不等于「有可用实现」** —— 那些 `sw_api_*` 模块是**索引层**。",
    "⚠ 严格说：**「AVI 文件由哪个成员真正写出」尚未查证到**。官方文档里只有 `swUserPreferenceToggle_e` 的 "
    "`swEDrawingsSaveAnimation*` 三个**枚举**（eDrawings 的开关，不是 SolidWorks 侧的导出入口）。"
    "⇒ 按**铁律 5 写「查不到」**，不拿 `SaveEntireAnimation` 这个名字蒙混（它是「是否保存整个动画」的属性，未必是导出动作）。",
    "⇒ **要做这一域，下一步是**：用 `C:\\swapi\\` + CHM 两套源查「SolidWorks 动画导出 AVI」的**确切成员名与签名**"
    "（很可能是 `IModelDocExtension` 的某个 `SaveAs` 变体或 Animation Controller），查不到就按 `§九.2` 标为「无法缝合」并写进报告的空缺段。",
]

COSTING = {
    "id": "costing",
    "label": "成本估算（Costing）",
    "level": "stitched",
    "backends": ["solidworks-com"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "SOLIDWORKS Costing 加载项", "pywin32"],
    "limitations": COSTING_LIMITS,
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "唯一实现模块 `scripts/sw_costing.py` **不在** `origin/main`"
                       "（硬证据 `git cat-file -e origin/main:scripts/sw_costing.py` 不通过）"
                       "⇒ 代码是我们新增的；且**无** `provenance` ⇒ 与 `source: original` 自洽（R13）",
}

ANIMATION = {
    "id": "animation_export",
    "label": "动画导出（AVI / 运动算例视频）",
    "level": "not_implemented",
    "backends": ["solidworks-com"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "SolidWorks Motion / 动画算例"],
    "limitations": ANIMATION_LIMITS,
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "**无实现**，故无第三方来源；标 `original` 表示「本仓自定的一条缺口记录」。"
                       "⚠ 若将来并入第三方实现，须改成对应的 `upstream`/`mixed` 并按 R13 补 `provenance`",
}


def main() -> int:
    RAW = CAP.read_text(encoding="utf-8")
    d = json.loads(RAW)
    assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "⚠ 往返不是逐字节相同 ⇒ 停下"
    print("  ✓ 往返逐字节相同（%d 字节）" % len(RAW))

    ids = [c["id"] for c in d["capabilities"]]
    for entry in (COSTING, ANIMATION):
        if entry["id"] in ids:
            print("  ! %s 已存在 ⇒ 跳过" % entry["id"])
            continue
        d["capabilities"].append(entry)
        print("  + 已加 %s（level=%s, source=%s）" % (entry["id"], entry["level"], entry["source"]))

    CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    caps = after["capabilities"]
    from collections import Counter
    print()
    print("  ── 落盘核对 ──")
    print("    条数: %d（原 29）" % len(caps))
    print("    source 分布: %s" % dict(Counter(c["source"] for c in caps)))
    print("    level  分布: %s" % dict(Counter(c["level"] for c in caps)))
    for mid in ("topology_optimization", "costing", "animation_export"):
        c = next((x for x in caps if x["id"] == mid), None)
        print("    护城河 %-24s ⇒ %s" % (mid, "%s / %s" % (c["level"], c["source"]) if c else "**缺**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
