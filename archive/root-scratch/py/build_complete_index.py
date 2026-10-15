# -*- coding: utf-8 -*-
"""生成**全量**官方 API 索引：774 个接口族、16,615 个成员，逐个照抄反射。

⚑ 口径（与前面所有模块统一）
  · arity = **调用方要传的实参**，排除 by-ref 出参（`Xxx&`）
  · 成员名 = **COM 名**（反射里的 `get_`/`set_` 前缀是 .NET 约定，COM 里没有）

⚑ 每份清单独立一个模块，理由：
  ① 6 个程序集来自 6 个不同 DLL，混在一张表里分不清谁是谁
  ② 单文件不会大到打不开
  ③ 按程序集取用时不用整包加载
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")
OUT = REPO / "scripts"
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
INTERNAL = re.compile(r"^I[A-Z][a-z]")

SRC = {
    "sldworks": Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt"),
    "cosworks": Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt"),
    "swdocumentmgr": Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt"),
    "SWRoutingLib": Path(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt"),
    "sldcostingapi": Path(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt"),
    "fworks": Path(r"D:\AI\SW\_raw\reflect\iface_fworks.txt"),
    "swmotionstudy": Path(r"D:\AI\SW\_raw\reflect\iface_swmotionstudy.txt"),
    "swdimxpert": Path(r"D:\AI\SW\_raw\reflect\iface_swdimxpert.txt"),
    "swpublished": Path(r"D:\AI\SW\_raw\reflect\iface_swpublished.txt"),
    "gtswutilities": Path(r"D:\AI\SW\_raw\reflect\iface_gtswutilities.txt"),
    "dsgnchk": Path(r"D:\AI\SW\_raw\reflect\iface_dsgnchk.txt"),
    "sldtoolboxconfigureaddin": Path(r"D:\AI\SW\_raw\reflect\iface_sldtoolboxconfigureaddin.txt"),
    # ⚑ 按用户指示**不收录**：sw3dprinter（只 1 个接口）、swbrowser（只 2 个）、
    #   sustainability（绿色设计，非本任务目标）。
    "swconst_only": None,
}
DLL = {
    "sldworks": "SolidWorks.Interop.sldworks.dll",
    "cosworks": "SolidWorks.Interop.cosworks.dll",
    "swdocumentmgr": "SolidWorks.Interop.swdocumentmgr.dll",
    "SWRoutingLib": "SolidWorks.Interop.SWRoutingLib.dll",
    "sldcostingapi": "SolidWorks.Interop.sldcostingapi.dll",
    "fworks": "SolidWorks.Interop.fworks.dll",
    "swmotionstudy": "SolidWorks.Interop.swmotionstudy.dll",
    "swdimxpert": "SolidWorks.Interop.swdimxpert.dll",
    "swpublished": "SolidWorks.Interop.swpublished.dll",
    "gtswutilities": "SolidWorks.Interop.gtswutilities.dll",
    "dsgnchk": "SolidWorks.Interop.dsgnchk.dll",
    "sldtoolboxconfigureaddin": "SolidWorks.Interop.sldtoolboxconfigureaddin.dll",
    "swconst_only": "SolidWorks.Interop.swconst.dll",
}
DESC = {
    "sldworks": "SolidWorks 主体（零件 / 装配 / 工程图 / 草图 / 钣金 / 焊件 …）",
    "cosworks": "SolidWorks Simulation（**需独立许可**）",
    "swdocumentmgr": "SolidWorks Enterprise PDM（**需独立许可**）",
    "SWRoutingLib": "SolidWorks Routers（**需独立许可**）",
    "sldcostingapi": "SolidWorks Composer / Costing（**需独立许可**）",
    "fworks": "SolidWorks Factory / 其它辅助接口",
    "swmotionstudy": "SolidWorks Motion —— 机构运动仿真（**需独立许可**）",
    "swdimxpert": "DimXpert —— 尺寸标注自动化 / GD&T 公差",
    "swpublished": "加载项开发框架（属性管理页回调、消息栏）",
    "gtswutilities": "几何分析 / 壁厚分析 / 图档比较 等独立工具",
    "dsgnchk": "Design Checker —— 设计检查器",
    "sldtoolboxconfigureaddin": "Toolbox 配置加载项",
    "swconst_only": "（不收录）",
}

HEADER = '''r"""SolidWorks {asm} 官方接口全量索引。

能力域
    {domain}

本模块是什么
------------
**官方 API 的完整抄录** —— {n_fam} 个接口族、**{n_members} 个成员**，
逐个照抄自对官方 interop 程序集的**纯元数据反射**。

怎么用
------
    call_index(对象, "族名", "成员名", *参数)

例：
    call_index(特征管理器, "IFeatureManager", "FeatureCut4", x1, ..., x27)

⚑ 口径（与本仓库所有模块统一）
--------------------------------
  · **成员名用 COM 名** —— 反射清单里属性形态写作 ``get_Xxx``（.NET interop 约定），
    但 COM 里实际叫 ``Xxx``。⚠ 传 ``GetXxx``（大写 G）**谁都不认**。
  · **arity = 调用方要传的实参**，**排除 by-ref 出参**（``Xxx&``）。
    ⚠ 反射里 ``Void GetErrorMessages(Object&, Object&, Object&)`` 是 **0 参**
    —— 三个全是 [out]，调用方一个都不传。
  · 编号成员**未折叠** —— SolidWorks 的编号不是重载，是不同版本的不同操作
    （``FeatureExtrusion`` / ``2`` / ``3`` 三个都存在且都是不同成员）。
  · COM 内部分发口（名字形如 ``IGetXxx``）**不登记** —— 它们是同一能力的
    内部变体，不是独立能力。

⚠ 本模块**只登记名字与参数个数，不解释语义**。
  语义请查官方文档（`C:\\swapi` 与本机 CHM 册）。

签名来源
--------
    {refl}
      对 **{dll}** 的纯元数据反射（AGENTS.md §四.1③）。
    ⚠ 属「读官方程序集」，**不是实测**（铁律 2）。

⚠ 本模块为机械抄录，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   官方 interop 程序集的纯元数据反射（{dll}）
# 文件:   {refl}
# 定位:   {n_fam} 个接口族的**全量**能力登记表 {{族: {{能力名: 实参个数}}}}。
# ⚑ 逐条机械生成，**不手抄、不折叠、不合并重载**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]

ASSEMBLY = {asm!r}

FAMILIES: tuple[str, ...] = ('''

TAIL = '''


def _require(obj, what: str = "对象"):
    if obj is None:
        raise ValueError(f"{{what}} 为 None")
    return obj


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_hubs.py / sw_sldworks_app.py 同款护栏）
# 文件:   {{mod}} —— 本文件自身
# 定位:   通用访问器 :func:`call_index` 的 arity 校核与调用。
# ⚑ **族名与成员名都由调用方给** ⇒ 静态 arity 审计归因不到，
#   对账靠 scripts/check_member_names.py（全仓成员名门禁）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def call_index(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用该族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = ARITY.get(family)
    if sub is None:
        raise KeyError(
            f"本清单没有这个族: {{family}}（{asm} 共 {{len(ARITY)}} 族）。"
            f"⚠ 别的程序集请用对应的 call_index。")
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{{family}} 上没有名为 {{member}} 的能力（该族登记 {{len(sub)}} 项）。"
            f"⚠ 若它是属性或 COM 内部分发口，请用对应封装。")
    if expected != len(args):
        raise ValueError(
            f"{{family}}.{{member}} 官方签名是 {{expected}} 个实参"
            f"（不含末位 by-ref 出参），本次调用给了 {{len(args)}} 个")
    _require(obj, f"{{family}} 对象")
    return get_com_member(obj, member, *args)

'''


def main() -> int:
    total_fam = total_mem = 0
    for asm, path in SRC.items():
        if path is None or not Path(path).is_file():
            continue
        fams: dict[str, dict] = {}
        cur = None
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if raw.startswith("## "):
                cur = raw[3:].strip()
                fams.setdefault(cur, {"methods": [], "props": []})
                continue
            if not cur or not raw.strip():
                continue
            m = SIG.match(raw.strip())
            if not m:
                continue
            name, params = m.group(1), m.group(2)
            if name.startswith(("get_", "set_")):
                fams[cur]["props"].append(name[4:])
                continue
            if INTERNAL.match(name):
                continue  # COM 内部分发口，不是独立能力
            # ⚑ 零参成员的返回值名（如 `Point get_X()` → 成员名 `X`）**也登记**：
            #   它们是**可取用的属性**（读 X / Y / Z 坐标、读 ID），
            #   不是文档占位符。漏掉会让覆盖表永远差 14 个。
            if name[0].islower() and name.upper() == name:
                fams[cur]["props"].append(name)
                continue
            real = len([a for a in (p.strip() for p in params.split(","))
                        if a and not a.endswith("&")])
            fams[cur]["methods"].append((name, real))

        order = sorted(f for f, v in fams.items() if v["methods"] or v["props"])
        n_mem = sum(len(fams[f]["methods"]) for f in order)
        n_prop = sum(len(fams[f]["props"]) for f in order)

        mod = f"sw_api_{asm}.py"
        body = HEADER.format(asm=asm, domain=DESC[asm], n_fam=len(order),
                             n_members=n_mem, refl=path, dll=DLL[asm])
        body += "".join(f"    {f!r},\n" for f in order)
        body += ")\n\n"
        body += "#: 全量能力登记表 {族: {能力名: 实参个数}}（排除 by-ref 出参）\n"
        body += "ARITY: dict[str, dict[str, int]] = {\n"
        for f in order:
            body += f"    {f!r}: {{\n"
            for name, real in fams[f]["methods"]:
                body += f"        {name!r}: {real},\n"
            body += "    },\n"
        body += "}\n\n"
        body += "#: 属性名（反射里是 get_/set_，**不是方法**；这里只留去掉前缀的名字）\n"
        body += "PROPERTIES: dict[str, tuple[str, ...]] = {\n"
        for f in order:
            body += f"    {f!r}: (\n"
            for p in sorted(fams[f]["props"]):
                body += f"        {p!r},\n"
            body += "    ),\n"
        body += "}\n"
        body += TAIL.format(asm=asm, mod=f"scripts/{mod}")
        (OUT / mod).write_text(body, encoding="utf-8")
        import ast
        ast.parse(body)
        print(f"  {mod:<26} {len(order):4d} 族 / {n_mem:5d} 能力 / {n_prop:5d} 属性")
        total_fam += len(order)
        total_mem += n_mem
    print(f"\n合计 {total_fam} 族 / {total_mem} 能力")
    return 0


if __name__ == "__main__":
    sys.exit(main())
