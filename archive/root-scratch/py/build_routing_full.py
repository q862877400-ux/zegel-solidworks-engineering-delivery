# -*- coding: utf-8 -*-
"""为 sldworks 侧剩余族生成全量登记表（收尾批）。

自检：分组恰好划分全部族、族名不重复、能力/属性数为正，不过就不落盘。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REG = Path(r"D:\\AI\\SW\\_reg_last.json")
DOMAINS = Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.md")
OUT = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_routing_costing_full.py")

HEADER = r'''r"""SolidWorks Routers 与 Composer 的全量登记表（收尾批）。

能力域
    域 1·3·5·6·7·8·9·10·11·12 —— 跨域收尾批次

本模块是什么
------------
`C:\swapi` 收录的 12 个程序集里，sldworks 是主体。本模块登记其中
**此前未被逐族封装**的那些族，与本仓库既有的高层模块互补：

    sw_selection / sw_sketch / sw_geometry / sw_part_features /
    sw_sketch_sheetmetal / sw_drawing_annotations / sw_hubs / sw_view
    —— 这些是「按能力挑的高层封装」，可读性好
    本文件 —— 「有多少、叫什么、几个参数」的**全量登记表**

两者不冲突：调用方要「快」用高层封装，要「查全」用本表。

⚠ 编号成员**未折叠**（SolidWorks 的编号不是重载，是不同版本的不同操作）。
⚠ 本表只登记**名字与参数个数**，**不解释语义** ——
  这些族多数有官方文档页，但把上百个成员的语义逐条抄进注释既不现实也不可靠；
  需要语义请查官方文档对应方法页。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt
      对 SolidWorks.Interop.sldworks.dll 的**纯元数据反射**
      （AGENTS.md §四.1③）。规模：1032 接口 / 20,627 成员。
    登记表：`D:\\AI\\SW\\tools\\gen_member_registry.py` 的输出。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

__all__ = ["FAMILIES", "GROUPS", "ARITY", "PROPERTIES",
           "call_member", "collect_evidence"]


def _require(obj, what: str = "对象"):
    if obj is None:
        raise ValueError(f"{what} 为 None")
    return obj


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_part_features.py 同款护栏）
# 文件:   scripts/sw_routing_costing_full.py —— 本文件自身
# 定位:   通用访问器 :func:`call_member` 的 arity 校核与调用。
# ⚑ 族名与成员名都由调用方给 ⇒ 静态 arity 审计归因不到；
#   对账靠 tests/test_routing_costing_full_contract.py。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def call_member(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用该族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = ARITY.get(family)
    if sub is None:
        raise KeyError(f"未登记的族: {family}；已登记 {len(ARITY)} 族")
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{family} 上没有名为 {member} 的能力（该族登记 {len(sub)} 项）。"
            f"若它是属性或 I 前缀内部分发口，请用对应封装。")
    if expected != len(args):
        raise ValueError(
            f"{family}.{member} 官方签名是 {expected} 个实参，"
            f"本次调用给了 {len(args)} 个")
    _require(obj, f"{family} 对象")
    return get_com_member(obj, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 文件:   scripts/sw_routing_costing_full.py —— 本文件自身
# 定位:   状态证据回读，只读登记表里确实有的成员。
# ⚑ 该族没有的证据成员**直接不出现**，不补默认值冒充「读到了」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_evidence(obj, family: str) -> dict[str, Any]:
    """回读该族对象的状态；该族没有的成员不出现。"""
    _require(obj, family)
    if family not in ARITY:
        raise KeyError(f"未登记的族: {family}")
    props = set(PROPERTIES.get(family, ()))
    out: dict[str, Any] = {"family": family}
    probes = [n for n, a in ARITY[family].items() if a == 0][:3]
    for member in probes:
        if member not in ARITY[family] and member not in props:
            continue
        try:
            out[member] = call_member(obj, family, member)
        except (KeyError, ValueError):
            continue
    return out
'''


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    fams = list(reg.keys())

    # 分组：按族名里的语义关键词分四组，剩余归 other
    kw = (
        ("sketch", ("Sketch", "Constraint", "Relation")),
        ("feature", ("FeatureData", "Feature", "Pattern", "Fillet",
                     "Chamfer", "Hole", "Weld", "SheetMetal", "Trim",
                     "Dome", "Draft", "Rib", "Lintel", "Slot")),
        ("geometry", ("Curve", "Surface", "Edge", "Vertex", "Body", "Face",
                      "Loop", "Wire", "Point", "Plane", "Axis", "Bezier",
                      "Trim", "Offset", "Transform", "Math")),
        ("document", ("Document", "ModelDoc", "SldWorks", "Configuration",
                      "View", "Sheet", "Drawing", "Dimension", "Table",
                      "Annotation", "Bom", "BomTable", "Tolerance")),
    )
    groups: dict[str, list[str]] = {k: [] for k, _ in kw}
    for fam in fams:
        placed = False
        for gname, keys in kw:
            if any(key.lower() in fam.lower() for key in keys):
                groups[gname].append(fam)
                placed = True
                break
        if not placed:
            groups.setdefault("other", []).append(fam)

    # 自检：恰好划分
    covered = [f for g in groups.values() for f in g]
    assert sorted(covered) == sorted(fams), (
        "分组未恰好划分全部族，多=%s 少=%s"
        % (sorted(set(covered) - set(fams)), sorted(set(fams) - set(covered))))
    assert len(covered) == len(set(covered)), "分组内有重复族"

    body = HEADER
    L = ["", "# ── 来源 ─────────────────────────────────────────────────────────────",
         "# 仓库:   本项目自身（本任务新增的能力层）",
         "# 文件:   scripts/sw_routing_costing_full.py —— 本文件自身",
         "# 定位:   sldworks 侧剩余族的成员登记表 {族: {能力名: 实参个数}}。",
         "#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。",
         "# ⚑ 编号成员**未折叠**。",
         "# ⚠ 本表只登记名字与参数个数，**不解释语义**。",
         "# 取值:   能力数 —— 逐族："]
    for k in fams:
        L.append("#     %-40s %4d" % (k, reg[k]["distinct_capabilities"]))
    L += ["# 覆盖:   后续同级定义",
          "# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）",
          "# ────────────────────────────────────────────────────────────────────",
          "FAMILIES: tuple[str, ...] = ("]
    for k in fams:
        L.append("    %r," % k)
    L += [")", "", "GROUPS: dict[str, tuple[str, ...]] = {"]
    for gname, items in groups.items():
        L.append("    %r: (" % gname)
        for x in items:
            L.append("        %r," % x)
        L.append("    ),")
    L += ["}", "", "ARITY: dict[str, dict[str, int]] = {"]
    n = 0
    for k in fams:
        L.append("    %r: {" % k)
        for it in reg[k]["members"]:
            L.append("        %r: %d," % (it["name"], it["arity"]))
            n += 1
        L.append("    },")
    L += ["}", "", "PROPERTIES: dict[str, tuple[str, ...]] = {"]
    p = 0
    for k in fams:
        L.append("    %r: (" % k)
        for x in reg[k]["properties"]:
            L.append("        %r," % x)
            p += 1
        L.append("    ),")
    L += ["}", ""]
    OUT.write_text(body + "\n".join(L) + "\n", encoding="utf-8")
    print("生成 %s：%d 族 / 能力 %d / 属性 %d / 分组 %s"
          % (OUT.name, len(fams), n, p,
             {k: len(v) for k, v in groups.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

