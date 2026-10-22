"""@brief 把拓扑优化登记进 capabilities.yaml（护城河域）。

# ── 来源 ──
# 仓库:   本项目自身（护城河域的能力登记）
# 文件:   tools/register_topology_capability.py
# 定位:   AGENTS.md A2/A4 的载体 —— 每条并入/新增能力都要在 capabilities.yaml
#         里有 id / level / backends / limitations，level 取自五级枚举。
#         docs/capabilities-schema-proposal.md §五 R5/R6/R11。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 本工具只改清单，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "capabilities.yaml"

ENTRY = {
    "id": "topology_optimization",
    "label": "拓扑优化（非参数化找形）",
    # ⚠ level=stitched 是**如实**的：代码与契约测试都在，但**从未在 SolidWorks 上跑过**
    # 。
    #   按五级枚举，stitched = 「代码已并入，从未运行」；升 verified 必须补我们自己的
    #   运行证据（真机跑出 Material Mass 结果）。低报是对的，高报违反 A7。
    "level": "stitched",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "SolidWorks Simulation 加载项", "pywin32"],
    "limitations": [
        "代码与 8 条契约测试就位，但**未在本机实测**：升 verified 需真机跑出拓扑结果（Material Mass 图）",
        "拓扑优化只能对**单个实体零件**做（官方 CHM 原话："
        "'You can only perform topology optimization for only one single-body part at a time.'），"
        "装配体要先另存为零件",
        "官方 UI 教程依赖「预建 Selection Set」，但 SolidWorks API **没有创建选择集的方法**"
        "（sldworks interop 反射 1032 接口 / 20627 成员核对：ISelectionSet 族只读只删不能建）"
        "⇒ 夹具与外载必须先把实体选好再调 Add*，不能照搬 UI 流程",
        "结果读取（Material Mass 图、收敛数据、Export Smoothed Mesh）**未实现**："
        "反射里未核到对应成员，按铁律 5 不编",
        "本模块走 pywin32 迟到绑定；ICWTopologyStudyManager 与每条约束的 BeginEdit/EndEdit "
        "事务纪律是必需项（不包事务的 Set* 会静默不落地），但该纪律**未在真机上验证过**",
    ],
    "allowed_modes": ["interactive", "reviewed"],
}


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c["id"] == ENTRY["id"] for c in caps):
        print("  · %s 已存在，未改动" % ENTRY["id"])
        return 0
    caps.append(ENTRY)
    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "  ✓ 已登记 %s（level=%s）⇒ 共 %d 条" % (ENTRY["id"], ENTRY["level"], len(caps))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
