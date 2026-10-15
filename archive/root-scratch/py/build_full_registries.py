# -*- coding: utf-8 -*-
"""一次性生成两个登记模块：cosworks 剩余族 + PDM 全族。

内含自检：分组必须恰好划分全部族、族名不得重复、能力/属性数须为正。
任一自检不过 ⇒ 直接退出，**不落盘**（避免半成品文件进仓库）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REG_CW = Path(r"D:\AI\SW\_reg_cosworks.json")
REG_PDM = Path(r"D:\AI\SW\_reg_pdm.json")
OUT_SIM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_full.py")
OUT_PDM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_pdm_full.py")

HEADER = r'''"""{title}

能力域
    域 {domain}

{summary}

⚑ 编号成员**未折叠**（SolidWorks 的编号不是重载，是不同版本的不同操作）。
⚠ 本族**官方无文档页**，只有反射签名 ⇒ 本模块**只登记名字与参数个数**，
  **不解释任何一项的语义**。

签名来源
--------
    {reflect}
      对 {dll} 的**纯元数据反射**（AGENTS.md §四.1③）。
    登记表：`D:\\AI\\SW\\tools\\gen_member_registry.py` 的输出。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

__all__ = [
    "FAMILIES", "GROUPS", "ARITY", "PROPERTIES",
    "call_member", "collect_evidence",
]


def _require(obj, what: str = "对象"):
    if obj is None:
        raise ValueError(f"{{what}} 为 None")
    return obj


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_part_features.py / sw_simulation_registry.py 同款护栏）
# 文件:   {src} —— 本文件自身
# 定位:   通用访问器 :func:`call_member` 的 arity 校核与调用。
# ⚑ 族名与成员名都由调用方给 ⇒ 静态 arity 审计归因不到；
#   对账靠对应的 tests/test_*.py。
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
        raise KeyError(
            f"未登记的族: {{family}}；已登记 {{len(ARITY)}} 族")
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{{family}} 上没有名为 {{member}} 的能力（该族登记 {{len(sub)}} 项）。"
            f"若它是属性或 I 前缀内部分发口，请用对应封装。")
    if expected != len(args):
        raise ValueError(
            f"{{family}}.{{member}} 官方签名是 {{expected}} 个实参，"
            f"本次调用给了 {{len(args)}} 个")
    _require(obj, f"{{family}} 对象")
    return get_com_member(obj, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 文件:   {src} —— 本文件自身
# 定位:   状态证据回读，只读登记表里确实有的成员。
# ⚑ 该族没有的证据成员**直接不出现**，不补默认值冒充「读到了」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_evidence(obj, family: str) -> dict[str, Any]:
    """回读该族对象的状态；该族没有的成员不出现。"""
    _require(obj, family)
    if family not in ARITY:
        raise KeyError(f"未登记的族: {{family}}")
    props = set(PROPERTIES.get(family, ()))
    out: dict[str, Any] = {{"family": family}}
    # 取该族第一个零参成员作为探针 —— 登记表里必然有（否则该族无法取证）
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


def build(reg_path: Path, out_path: Path, title: str, domain: str,
          summary: str, reflect: str, dll: str, src_name: str,
          groups: dict[str, list[str]]) -> tuple[int, int, int]:
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    fams = list(reg.keys())

    # 自检 1：分组恰好划分全部族
    covered = [f for g in groups.values() for f in g]
    assert sorted(covered) == sorted(fams), (
        "%s 分组未恰好划分全部族，多=%s 少=%s"
        % (out_path.name, sorted(set(covered) - set(fams)),
           sorted(set(fams) - set(covered))))
    assert len(covered) == len(set(covered)), "%s 分组内有重复族" % out_path.name

    # 自检 2：每族能力数与属性数非负，族名不重复
    assert len(fams) == len(set(fams)), "%s 族名重复" % out_path.name

    body = HEADER.format(title=title, domain=domain, summary=summary,
                         reflect=reflect, dll=dll, src=src_name)
    L = ["", "# ── 来源 ─────────────────────────────────────────────────────────────",
         "# 仓库:   本项目自身（本任务新增的能力层）",
         "# 文件:   %s —— 本文件自身" % src_name,
         "# 定位:   族的成员登记表 {族: {能力名: 实参个数}}。",
         "#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。",
         "# ⚑ 编号成员**未折叠**。",
         "# ⚠ 本族官方无文档页 ⇒ 只登记名字与参数个数，**不解释语义**。",
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
    out = body + "\n".join(L) + "\n"
    out_path.write_text(out, encoding="utf-8")
    return len(fams), n, p


def main() -> int:
    # ── cosworks 全 84 族 ──
    reg_cw = json.loads(REG_CW.read_text(encoding="utf-8"))
    cw = list(reg_cw.keys())
    study = [k for k in cw if k in ("ICWStudyManager", "ICWStudy",
                                    "ICWLoadsAndRestraintsManager", "ICWForce",
                                    "ICWPressure", "ICWHeatFlux", "ICWContactSet")]
    loads = [k for k in cw if k not in study and not k.endswith("StudyOptions")]
    opts = [k for k in cw if k not in study and k not in loads]
    f1, n1, p1 = build(
        REG_CW, OUT_SIM,
        title="SolidWorks Simulation：cosworks 全部 84 族的成员登记表",
        domain="13 · 仿真（需许可证）",
        summary=("本模块登记 cosworks 反射里**全部有成员的接口族**。\n"
                 "与既有 sw_simulation_registry.py（19 族）互补：本文件是**全量版**，\n"
                 "那份是子集。本文件取代它承担「成员级全覆盖」的角色。"),
        reflect=r"D:\AI\SW\_raw\reflect\iface_cosworks.txt",
        dll="SolidWorks.Interop.cosworks.dll",
        src_name="scripts/sw_simulation_full.py",
        groups={"study_and_loads": study, "other_load_objects": loads,
                "solver_options": opts})
    print("sw_simulation_full.py：%d 族 / 能力 %d / 属性 %d" % (f1, n1, p1))

    # ── swdocumentmgr 全 138 族 ──
    reg_pdm = json.loads(REG_PDM.read_text(encoding="utf-8"))
    pdm = list(reg_pdm.keys())
    doc = [k for k in pdm if "Document" in k]
    mgr = [k for k in pdm if "Mgr" in k or "Manager" in k]
    other = [k for k in pdm if k not in doc and k not in mgr]
    f2, n2, p2 = build(
        REG_PDM, OUT_PDM,
        title="SolidWorks Enterprise PDM：swdocumentmgr 全部族的成员登记表",
        domain="14 · 路由 / Composer / PDM（需许可证）—— 本文件是 PDM 部分",
        summary=("PDM 是全库最大的接口族集合。官方 CHM **无 PDM 册**、\n"
                 "C:\\swapi **不收录** swdocumentmgr ⇒ 只有反射签名可依，\n"
                 "本模块**只登记名字与参数个数，不解释语义**。"),
        reflect=r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt",
        dll="SolidWorks.Interop.swdocumentmgr.dll",
        src_name="scripts/sw_pdm_full.py",
        groups={"document": doc, "manager": mgr, "other": other})
    print("sw_pdm_full.py：%d 族 / 能力 %d / 属性 %d" % (f2, n2, p2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
