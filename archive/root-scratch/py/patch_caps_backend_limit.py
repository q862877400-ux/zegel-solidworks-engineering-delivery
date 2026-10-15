"""把「pywin32 到不了」这条**具体化**写进 `capabilities.yaml`（清单承载状态）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单更新）+ SolidWorks 出厂类型库反射
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml
#         （44.7 KB / 1183 行，**内容是 JSON、扩展名是 yaml**；
#          已验证 `json.dumps(d, ensure_ascii=False, indent=2) + "\\n"` **与原文件逐字节相同**
#          ⇒ **JSON 往返编辑是安全的，不会重排**）
#         D:\\AI\\SW\\probe_setfixedface_forms.py / probe_setfixedface_overloads.py /
#         probe_access_selections.py（证据）
#         D:\\AI\\SW\\AGENTS.md 已知事实 43 / 44 / 47
# 定位:   事实 47 说「这是架构性限制」，而 `capabilities.yaml` 的
#         `backend_catalog["solidworks-com-pywin32"].limitations` 里**早就有一条抽象的**
#         「不能调用官方标记为仅进程内非托管 C++ 的指针接口」——
#         **本补丁把它**具体化**（点名到接口/成员 + 错误码 + 证据脚本），
#         并把 `sheet_metal` 条目的实测状态补齐。**
#         **⇒ 理由：状态该由**清单**承载（AGENTS.md §一说「进度与下一步看 capabilities.yaml」），
#         而不是只在文档与已知事实里。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。**改完立即回读核对**（事实 48 第 ② 条定则）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAPS = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

# ⚠ 事实 48 的定则：**短的单行字符串**，绝不跨行拼接
LIM_PYWIN32 = (
    "**具体化的实例（2026-10-01 实测）**：`ISketchedBendFeatureData` 的 "
    "`AccessSelections(Object, Object)` 与 `SetFixedFace(Double, Double, Double, Object)` "
    "在 pywin32 迟到绑定下**不可调用** —— `SetFixedFace` 的**七种数组包装 × 两个重载**"
    "全部报 `类型不匹配`（位置 1 或 4）；`AccessSelections(model, None)` 报 `类型不匹配`（位置 2）、"
    "改传 `VARIANT(VT_DISPATCH, None)` 报 **`服务器出现意外情况`（`0x80010105`）**"
    "（与 `IModeler.CreateBsplineSurface` 同码）。反射里那对 "
    "`IAccessSelections` / `IAccessSelections2` 正是本限制说的**指针变体**。"
    "⇒ **受此影响：`sw_sheet_metal` 的 `create_one_bend` / `create_edge_flange` / `create_gusset` "
    "在这条后端上到不了「建成」**（另有 `create_draft` 的常量不在官方 35 个内）。"
    "**⚠ 「换个参数试试」已穷尽（20+ 种），不要再试。**"
)

LIM_SHEET = (
    "**真机实测状态（2026-10-01，SW 2026 SP4.1）：6 个创建入口里 2 个可跑** —— "
    "✓ `create_base_flange`（但**只对闭轮廓成立**，开放折线的轮廓法兰实测失败）· "
    "✓ `sheet_metal_evidence`；"
    "✗ `create_one_bend` / `create_edge_flange` / `create_gusset` **受 pywin32 指针接口限制到不了**"
    "（见 `backend_catalog.solidworks-com-pywin32` 的相应条目）· "
    "✗ `create_draft` 用的 `swFmDraft(3)` **不在 `CreateDefinition` 接受的 35 个常量里**。"
    "**已修掉的缺陷**：`create_one_bend` 的常量（`swFmOneBend(33)` → `swFmSketchBend(35)`，"
    "报错前推到 `CreateFeature(35)`）；`create_gusset` **整步缺失的官方步骤 3**"
    "（`ProfileDimensionScheme` / `UseOffset` / `UseAngleDimForProfile`，"
    "真机**属性层 8/8 读回成功**）；`create_edge_flange` 的 `ReverseDirection` 跨接口泄漏。"
    "**⇒ 「属性设对了」与「特征建成了」是两件事，必须分开取证。**"
)


def main() -> int:
    raw = CAPS.read_text(encoding="utf-8")
    d = json.loads(raw)

    # ① backend_catalog：把抽象限制**具体化**
    bc = d["backend_catalog"]["solidworks-com-pywin32"]
    if LIM_PYWIN32 not in bc["limitations"]:
        bc["limitations"].append(LIM_PYWIN32)
        print("  ✓ ① backend_catalog[solidworks-com-pywin32] 的限制已具体化")
    else:
        print("  ⚠ ① 已存在")

    # ② sheet_metal 条目：补实测状态
    n = 0
    for c in d["capabilities"]:
        if c["id"] == "sheet_metal":
            if LIM_SHEET not in c["limitations"]:
                c["limitations"].append(LIM_SHEET)
                n += 1
    print("  ✓ ② sheet_metal 条目已补实测状态" if n else "  ⚠ ② 未改")

    # ③ **保持格式**：与已验证的 round-trip 一致
    CAPS.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ④ **回读核对**（事实 48 第 ② 条：不能只看 stdout）
    d2 = json.loads(CAPS.read_text(encoding="utf-8"))
    bc2 = d2["backend_catalog"]["solidworks-com-pywin32"]
    sm = next(c for c in d2["capabilities"] if c["id"] == "sheet_metal")
    print()
    print("  ── 回读核对 ──")
    print("    pywin32 limitations 条数: %d（原 2）" % len(bc2["limitations"]))
    print("    含「0x80010105」: %s" % ("是" if any("0x80010105" in s for s in bc2["limitations"]) else "**否**"))
    print("    sheet_metal limitations 条数: %d（原 1）" % len(sm["limitations"]))
    print("    含「2 个可跑」: %s" % ("是" if any("2 个可跑" in s for s in sm["limitations"]) else "**否**"))
    print("    文件行数: %d（原 1183）" % len(CAPS.read_text(encoding="utf-8").splitlines()))
    print("    仍是合法 JSON: 是")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
