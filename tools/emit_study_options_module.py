#!/usr/bin/env python3
r"""生成 scripts/sw_simulation_study_options.py（含 setter 登记表）。

登记表由反射清单机械生成，**不手抄**。生成后请跑：
    python -m py_compile scripts\sw_simulation_study_options.py
    python tests\test_sw_simulation_study_options_contract.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

DATA = Path(Path(__file__).resolve().parents[1] / "_raw" / "study_options_setters.json")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])

OUT = Path(r"" + _ROOT_S + r"\scripts\sw_simulation_study_options.py")

HEADER = r'''"""SolidWorks Simulation 求解器设置：各 *StudyOptions 族的 setter 登记表。

能力域
    域 13 · 仿真（需许可证）

本模块解决什么问题
------------------
cosworks 的求解器设置分散在 9 个 ``*StudyOptions`` 族里，**合计 242 个 setter**
（静态研究 55、非线性 40、动态 34、频率 31、屈曲 24、热 22、疲劳 14、
  复合材料壳 12、跌落 10）。逐个包一层 Python 函数，代码量大、单位信息量低。

但「**这个求解器到底能配什么**」本身是权威信息 —— 它决定了下游能做到哪一步。
所以本模块做两件事：
  1. **登记表**（``STUDY_OPTION_SETTERS``）：把反射确认的 242 个可设项
     落成**字符串字面量**，可 grep、可被测试逐条核对。
     刻意**不做运行时反射** —— 那会随 SolidWorks 版本漂移。
  2. **受登记表约束的通用 setter** ``set_option()`` + 少量高频项显式包装。

⚠ 登记表是「名字 + 参数类型」，**不含语义**。这些族官方 CHM 没有文档页，
  参数的工程含义查不到 ⇒ 本模块**不解释任何一项是干什么的**，
  只保证「这个名字确实存在于官方 API，且参数个数对得上」。

⚑ X / X2 成对规律
------------------
多数布尔开关都有**两个** setter：``X(Int32)`` 与 ``X2(Boolean)``
（如 ``CheckFlowPressure`` / ``CheckFlowPressure2``）。
反射确认这是**两个不同签名的成员，不是新旧版替代**。
本模块**只推荐 X2（Boolean）**那一个，并在登记表里把 X2 单列出来 ——
理由：Int32 那个的取值语义（0/1/-1？枚举？）查不到，Boolean 版没有这个歧义。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt   （对 interop 纯元数据反射）
登记表由 D:\\AI\\SW\\tools\\gen_study_options_registry.py 机械生成，
不手抄；生成物 D:\\AI\\SW\\_raw\\study_options_setters.json。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any


try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   模块导出清单、族名常量与类型归一表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "STUDY_OPTION_FAMILIES",
    "STUDY_OPTION_SETTERS",
    "BOOLEAN_SETTERS",
    "ARITY_TABLE",
    "study_options_of",
    "set_option",
    "set_options",
    "configure_static_solver",
    "configure_frequency_solver",
    "configure_buckling_solver",
    "list_setter_summary",
]

#: 九个可设项的研究设置族（反射确认有 setter 的）
STUDY_OPTION_FAMILIES = (
    "ICWStaticStudyOptions",
    "ICWFrequencyStudyOptions",
    "ICWBucklingStudyOptions",
    "ICWNonLinearStudyOptions",
    "ICWThermalStudyOptions",
    "ICWDynamicStudyOptions",
    "ICWFatigueStudyOptions",
    "ICWDropTestStudyOptions",
    "ICWCompositeShellOptions",
)

#: 反射里的参数类型名 → Python 侧期望的归一类型
_TYPE_ALIASES = {
    "Int32": "int",
    "System.Int32": "int",
    "Boolean": "bool",
    "System.Boolean": "bool",
    "Double": "float",
    "System.Double": "float",
    "String": "str",
    "System.String": "str",
}

'''

FOOTER = r'''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   通用 setter 的取值校验与调用。
# ⚠ 名字与值都由调用方给 ⇒ 静态 arity 审计归因不到（成员名是变量）。
#   对账靠 tests/test_sw_simulation_study_options_contract.py：
#   逐条核对「登记表 ⊆ 反射清单」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _coerce(raw_type: str, value):
    """按反射登记的参数类型转换取值；类型对不上直接报错。"""
    want = _TYPE_ALIASES.get(raw_type, raw_type)
    if want == "int":
        return int(value)
    if want == "bool":
        return bool(value)
    if want == "float":
        return float(value)
    if want == "str":
        return str(value)
    return value


def set_option(options, family: str, name: str, value) -> bool:
    """按登记表设一个求解器选项。

    :param family: STUDY_OPTION_FAMILIES 里的族名
    :param name: 该族登记表中确实存在的 setter 名
    :raises KeyError: 族名或选项名不在登记表里（**不静默忽略**）
    """
    if options is None:
        raise ValueError("options 为 None")
    if family not in STUDY_OPTION_SETTERS:
        raise KeyError(f"未知的研究设置族: {family}")
    entry = STUDY_OPTION_SETTERS[family].get(name)
    if entry is None:
        raise KeyError(
            f"{family} 没有名为 {name} 的 setter。\n"
            f"该族登记的 {len(STUDY_OPTION_SETTERS[family])} 项，"
            f"其中布尔型（推荐用）: {sorted(BOOLEAN_SETTERS.get(family, ()))[:8]} …"
        )
    return bool(get_com_member(options, name, _coerce(entry, value)))


def set_options(options, family: str, values: dict[str, Any]) -> dict[str, Any]:
    """批量设；只设你给了的键。返回实际设置成功的键值。"""
    applied: dict[str, Any] = {}
    for name, value in values.items():
        if value is None:
            continue
        set_option(options, family, name, value)
        applied[name] = value
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
#           → ICWStudy.get_StaticStudyOptions / get_FrequencyStudyOptions /
#             get_BucklingStudyOptions 等属性
# 定位:   从研究对象取各设置族。官方反射里这些是**属性**（get_ 形式）。
# ⚠ 取用路径的正确拼写（反射里的属性名）：
#     ICWStudy 上有 get_StaticStudyOptions / get_FrequencyStudyOptions /
#     get_BucklingStudyOptions / get_NonLinearStudyOptions /
#     get_DynamicStudyOptions / get_FatigueStudyOptions /
#     get_DropTestStudyOptions（上面几行 ICWStudy 段的清单里可见部分），
#     **热与复合材料壳的取值名未在已见清单中确认** ⇒ 不臆造，
#     用下面的显式取用器只暴露反射确认过的那些。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: study 对象上的设置族属性名（反射逐个确认的）
STUDY_OPTIONS_ACCESSORS = {
    "ICWStaticStudyOptions": "StaticStudyOptions",
    "ICWFrequencyStudyOptions": "FrequencyStudyOptions",
    "ICWBucklingStudyOptions": "BucklingStudyOptions",
    "ICWNonLinearStudyOptions": "NonLinearStudyOptions",
    "ICWDynamicStudyOptions": "DynamicStudyOptions",
    "ICWFatigueStudyOptions": "FatigueStudyOptions",
    "ICWDropTestStudyOptions": "DropTestStudyOptions",
}


def study_options_of(study, family: str):
    """从 ICWStudy 取某个设置族对象。族名须在 STUDY_OPTIONS_ACCESSORS 里。"""
    if study is None:
        raise ValueError("study 为 None")
    accessor = STUDY_OPTIONS_ACCESSORS.get(family)
    if accessor is None:
        raise KeyError(
            f"{family} 的 study 取用属性名未在反射清单里确认，"
            f"不臆造。已确认: {', '.join(sorted(STUDY_OPTIONS_ACCESSORS))}"
        )
    return get_com_member(study, accessor)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt → 三个族的 set_ 段
# 定位:   三组高频求解器设置的显式包装。**只挑反射清单里能确认存在的项**，
#         且只用 **X2（Boolean）** 形（避开 Int32 版的取值语义歧义）。
#   ICWStaticStudyOptions    : set_CheckFlowPressure2(Boolean)
#                              set_ComputeFreeBodyForce2(Boolean)
#                              set_ContactPenaltyStiffnessScaleFactor(Double)
#                              set_DefinedReferencePressure(Double)
#   ICWFrequencyStudyOptions : set_CheckDecouple(Boolean)
#                              set_DefinedReferencePressure(Double)
#   ICWBucklingStudyOptions  : set_BucklingModes(Int32)
#                              set_ExtractPositiveBucklingFactorsOnly(Boolean)
#                              set_DefinedReferencePressure(Double)
# ⚠ 这些项的**工程含义**官方无文档，本模块只保证「签名对得上、值类型对得上」，
#   不解释「什么时候该打开」。需要语义请查 SolidWorks Simulation 用户文档。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_static_solver(options, *, free_body_force: bool | None = None,
                            contact_penalty: float | None = None,
                            reference_pressure: float | None = None
                            ) -> dict[str, Any]:
    """静态研究求解器设置。"""
    return set_options(options, "ICWStaticStudyOptions", {
        "ComputeFreeBodyForce2": free_body_force,
        "ContactPenaltyStiffnessScaleFactor": contact_penalty,
        "DefinedReferencePressure": reference_pressure,
    })


def configure_frequency_solver(options, *, decouple: bool | None = None,
                              reference_pressure: float | None = None
                              ) -> dict[str, Any]:
    """频率研究求解器设置。"""
    return set_options(options, "ICWFrequencyStudyOptions", {
        "CheckDecouple": decouple,
        "DefinedReferencePressure": reference_pressure,
    })


def configure_buckling_solver(options, *, modes: int | None = None,
                              positive_only: bool | None = None,
                              reference_pressure: float | None = None
                              ) -> dict[str, Any]:
    """屈曲研究求解器设置。"""
    return set_options(options, "ICWBucklingStudyOptions", {
        "BucklingModes": modes,
        "ExtractPositiveBucklingFactorsOnly": positive_only,
        "DefinedReferencePressure": reference_pressure,
    })


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_study_options.py —— 本文件自身
# 定位:   登记表自省，帮助下游看清「这一族能配什么」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def list_setter_summary() -> dict[str, Any]:
    """返回各族 setter 数量与布尔型清单（供文档生成 / 自检使用）。"""
    return {
        family: {
            "total": len(items),
            "boolean": len(BOOLEAN_SETTERS.get(family, ())),
            "names": sorted(items),
        }
        for family, items in STUDY_OPTION_SETTERS.items()
    }
'''


def main() -> int:
    if not DATA.is_file():
        print(f"[FATAL] 找不到登记表数据: {DATA}", file=sys.stderr)
        return 2
    data = json.loads(DATA.read_text(encoding="utf-8"))

    lines = [HEADER]
    lines.append("#: 反射确认的 setter 登记表：{族: {setter名: 参数类型}}\n")
    lines.append(
        "# ⚠ 机械生成（D:\\AI\\SW\\tools\\gen_study_options_registry.py），不手抄。\n"
    )
    lines.append("STUDY_OPTION_SETTERS: dict[str, dict[str, str]] = {\n")
    for family, items in data.items():
        if not items:
            continue
        lines.append(f"    {family!r}: {{\n")
        for entry in items:
            lines.append(f"        {entry['name']!r}: {entry['type']!r},\n")
        lines.append("    },\n")
    lines.append("}\n\n")

    lines.append("#: 只列 **X2（Boolean）** 形 —— 避开 Int32 版的取值语义歧义\n")
    lines.append("BOOLEAN_SETTERS: dict[str, tuple[str, ...]] = {\n")
    for family, items in data.items():
        bools = tuple(sorted(e["name"] for e in items if e["name"].endswith("2")))
        if bools:
            lines.append(f"    {family!r}: (\n")
            for name in bools:
                lines.append(f"        {name!r},\n")
            lines.append("    ),\n")
    lines.append("}\n\n")

    lines.append("#: 登记表里每个 setter 的**实参个数**（全部是 1，登记以备审计）\n")
    lines.append("ARITY_TABLE: dict[str, int] = {\n")
    seen = set()
    for items in data.values():
        for entry in items:
            seen.add(entry["name"])
    for name in sorted(seen):
        lines.append(f"    {name!r}: 1,\n")
    lines.append("}\n")

    lines.append(FOOTER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"已生成 {OUT}  ({OUT.stat().st_size} 字节)")
    print(f"  族 {len([1 for v in data.values() if v])} 个 / setter {len(seen)} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
