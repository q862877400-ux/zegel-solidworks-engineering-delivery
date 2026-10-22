#!/usr/bin/env python3
"""生成 scripts/sw_drawing_view.py（IView 成员登记表 + 通用访问器）。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

DATA = Path(Path(__file__).resolve().parents[1] / "_raw" / "iview_members.json")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])

OUT = Path(r"" + _ROOT_S + r"\scripts\sw_drawing_view.py")

HEADER = r'''"""SolidWorks 工程图视图：IView 成员登记表 + 通用访问器。

能力域
    域 9 · 工程图

⚠⚑ 本模块为什么是「登记表」而不是 207 个手写函数
-----------------------------------------------
``IView`` 是全库**最大的单个接口族**。对 ``iface_sldworks.txt`` 逐行解析
（不用正则切段 —— 前瞻会提前截断）的实测构成：

    原始成员                  496
    ├ I 前缀内部分发口        134   （27%，COM 运行时用，不给调用方）
    ├ 属性（get_/set_）         61
    └ 方法签名                301
        └ 编号历史变体         94   （X2 / X3 形态）
    ── 归约到基础名后 = **207 个不同能力**

207 个手写函数代码量大、单位信息量低；而且其中大量是
``GetXxxCount`` / ``GetXxx`` 的固定配对（前 40 个能力里占了 20 个）。

⇒ 与 ``sw_simulation_study_options.py`` 同一套做法：
  1. **登记表** ``VIEW_MEMBER_ARITY``：207 个能力名 → 实参个数。
     机械生成（``D:\\AI\\SW\\tools\\gen_iview_registry.py``），
     **不手抄**，可被测试逐条对回反射清单。
  2. **受登记表约束的通用访问器** :func:`call_view` —— 传成员名，
     先查表校核实参个数，通过才发起调用。
  3. 少量高频能力做显式包装（:func:`get_view_name` / :func:`set_view_scale` 等）。

⚠ **登记表只说「这个名字存在、参数个数对得上」，不解释它干什么。**
  官方 CHM 对 IView 的语义说明是按「方法页」分散的，
  逐条抄进注释不现实也不可靠 ⇒ 需要语义请查官方 API 文档对应方法页。

⚠ **编号变体的取舍**：官方 ``GetFirstView`` / ``GetFirstView2`` /
  ``GetFirstView3`` 这类变体，官方未说明差别。本模块的登记表把它们
  **折叠到基础名**并保留**实参最多的那一条** ⇒ 调用时传基础名。
  这是一��**明确声明的取舍**，不是「它们等价」。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IView 段
      —— 对 SolidWorks.Interop.sldworks.dll 的纯元数据反射
         （AGENTS.md §四.1③）。
    登记表数据：``D:\\AI\\SW\\_raw\\iview_members.json``（由上述脚本生成）。

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
# 文件:   scripts/sw_drawing_view.py —— 本文件自身
# 定位:   模块导出清单与成员登记表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "VIEW_MEMBER_ARITY",
    "VIEW_PROPERTY_NAMES",
    "call_view",
    "call_view_no_args",
    "get_view_scale",
    "set_view_scale",
    "get_view_name",
    "get_first_view",
    "get_next_view",
    "get_annotation_count",
    "get_annotations",
    "get_visible_component_count",
    "get_scale_decimal",
    "get_orient_toward",
    "collect_view_evidence",
]
'''

FOOTER = r'''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（发布门禁同款护栏）
# 文件:   scripts/sw_drawing_view.py —— 本文件自身
# 定位:   通用访问器 :func:`call_view` 的 arity 校核与调用。
# ⚠ 成员名与取值都由调用方给 ⇒ 静态 arity 审计**归因不到**（成员名是变量）。
#   对账靠 tests/test_sw_drawing_view_contract.py：把登记表逐条对回反射清单。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def call_view(view, member: str, *args):
    """按登记表校核实参个数，通过后调用该成员。

    :param member: VIEW_MEMBER_ARITY 里的能力名
    :raises KeyError: 名字不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数与登记表对不上（在**发起调用之前**就报）
    """
    if view is None:
        raise ValueError("view 为 None：须先由 IDrawingDoc/Sheet 取得 IView")
    expected = VIEW_MEMBER_ARITY.get(member)
    if expected is None:
        raise KeyError(
            f"IView 上没有名为 {member} 的能力（登记表共 "
            f"{len(VIEW_MEMBER_ARITY)} 项）。若它是属性或 I 前缀内部分发口，"
            f"请用对应的专用封装。"
        )
    if expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参，本次调用给了 {len(args)} 个"
        )
    return get_com_member(view, member, *args)


def call_view_no_args(view, member: str):
    """调用零参成员（表格里绝大多数是这种）。"""
    return call_view(view, member)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IView 段
# 定位:   下面几个是工程出图里最高频的视图操作。**全部逐条照抄反射签名**：
#     Double get_Scale() / set_Scale(Double)          ← **属性**
#     String get_Name()                               ← **属性**
#     View   GetFirstView()                           ← **零参**
#     View   GetNextView()                            ← **零参**
#     Int32  GetAnnotationCount()                     ← **零参**
#     Object GetAnnotations()                         ← **零参**
#     Int32  GetVisibleComponentCount()               ← **零参**
#     Int32  GetScaleDecimal()                        ← **零参**
#     Boolean OrientToward(View, Double, Double)      → 2
# ⚑ 前七项里除 `GetFirstView` / `GetNextView` 外都是**属性或零参**，
#   迟到绑定下加括号会 TypeError（AGENTS.md §六 事实 4）。
# ⚠ `OrientToward` 的后两个 Double 单位官方未说明 ⇒ 原样透传。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_view_scale(view) -> float:
    """取视图比例。⚑ 官方是**属性**（get_Scale）。"""
    if view is None:
        raise ValueError("view 为 None")
    return float(get_com_member(view, "Scale") or 0.0)


def set_view_scale(view, scale: float) -> bool:
    """设视图比例。⚑ 官方是**属性**（set_Scale）。"""
    if view is None:
        raise ValueError("view 为 None")
    get_com_member(view, "Scale", float(scale))
    return True


def get_view_name(view) -> str:
    """取视图名。⚑ 官方是**属性**（get_Name）。"""
    if view is None:
        raise ValueError("view 为 None")
    return str(get_com_member(view, "Name") or "")


def get_first_view(drawing):
    """取图纸第一张视图。**零参**。"""
    if drawing is None:
        raise ValueError("drawing 为 None：须先取得 IDrawingDoc")
    return get_com_member(drawing, "GetFirstView")


def get_next_view(view):
    """取下一张视图。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return get_com_member(view, "GetNextView")


def get_annotation_count(view) -> int:
    """视图里的注释数。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return int(get_com_member(view, "GetAnnotationCount") or 0)


def get_annotations(view) -> list[Any]:
    """视图里的注释列表。**零参**，返回 SAFEARRAY。"""
    if view is None:
        raise ValueError("view 为 None")
    value = get_com_member(view, "GetAnnotations")
    if value is None:
        return []
    try:
        return list(value)
    except TypeError:
        return [value]


def get_visible_component_count(view) -> int:
    """视图里可见的零件数。**零参**。"""
    if view is None:
        raise ValueError("view 为 None")
    return int(get_com_member(view, "GetVisibleComponentCount") or 0)


def get_scale_decimal(view) -> int:
    """比例的小数位设置。**零参**。⚠ 语义（位数？标志位？）官方未说明。"""
    if view is None:
        raise ValueError("view 为 None")
    return int(get_com_member(view, "GetScaleDecimal") or 0)


def get_orient_toward(view, target, angle_x: float, angle_y: float) -> bool:
    """把视图转向目标视图。⚠ 后两参单位官方未说明。"""
    if view is None:
        raise ValueError("view 为 None")
    if target is None:
        raise ValueError("target 为 None")
    return bool(get_com_member(view, "OrientToward", target,
                               float(angle_x), float(angle_y)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   视图状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_view_evidence(view) -> dict[str, Any]:
    """回读工程图视图状态。"""
    if view is None:
        raise ValueError("view 为 None")
    return {
        "name": get_view_name(view),
        "scale": get_view_scale(view),
        "annotation_count": get_annotation_count(view),
        "visible_component_count": get_visible_component_count(view),
        "scale_decimal": get_scale_decimal(view),
        "rotation": float(get_com_member(view, "Rotation") or 0.0),
        "xform": get_com_member(view, "Xform") is not None,
    }
'''


def main() -> int:
    if not DATA.is_file():
        print(f"[FATAL] 找不到登记表: {DATA}", file=sys.stderr)
        return 2
    data = json.loads(DATA.read_text(encoding="utf-8"))

    lines = [HEADER]
    lines.append("#: IView 能力登记表：{能力名: 实参个数}。机械生成，不手抄。\n")
    lines.append("# ⚠ 编号变体已折叠到基础名（保留实参最多的那一条）。\n")
    lines.append("VIEW_MEMBER_ARITY: dict[str, int] = {\n")
    for item in data["members"]:
        lines.append(f"    {item['name']!r}: {item['arity']},\n")
    lines.append("}\n\n")

    lines.append("#: IView 上的属性名（反射里是 get_/set_，**不是方法**）。\n")
    lines.append("# ⚑ 它们的实参个数不在上面那张表里 —— 赋值是单参数、读取是零参。\n")
    lines.append("VIEW_PROPERTY_NAMES: tuple[str, ...] = (\n")
    for name in sorted({n for n in _props(data)}):
        lines.append(f"    {name!r},\n")
    lines.append(")\n")

    lines.append(FOOTER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"已生成 {OUT}  ({OUT.stat().st_size} 字节)")
    print(f"  能力登记表 {len(data['members'])} 项")
    return 0


def _props(data: dict) -> list[str]:
    """属性名从反射再取一次（生成器只落了方法）。"""
    path = Path(
        Path(__file__).resolve().parents[1]
        / "_raw"
        / "reflect_sldworks"
        / "iface_sldworks.txt"
    )
    current, out = None, []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            if current == "IView":
                break
            current = raw[3:].strip()
            if current == "IView":
                out = []
        elif current == "IView" and raw.strip():
            m = re.match(r"^\S+\s+(get_|set_)(\w+)\s*\(", raw.strip())
            if m:
                out.append(m.group(2))
    return out


if __name__ == "__main__":
    raise SystemExit(main())
