"""规则 3 的**第二句**守卫：`selection` 必须是声明式（`str`）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_rule3_declarative_selection_is_enforced.py
# 定位:   2026-10-01 轮 218（**地基③**）。★ 规则 3 在文档里有**三句**，机器**只验过第一句**
#         （参数名不是裸坐标）⇒ 后两句无人看守（事实 153）。
# 官方依据: 不适用（本项目内部纪律）
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ⚠⚠ **本文件的范围是刻意收窄的，理由要记下来**（否则下一个人会又来加两条）：
#   规则 3 的三句里，**能被机器判的只有两句**：
#     句1「不许裸坐标」     ⇒ 参数名黑名单（`test_tool_registry.py` 已覆盖）
#     句2「必须是声明式选择」⇒ **本文件**：声明式选择在参数上就是 `selection: str`
#     句3「按 mark 分配」   ⇒ ★ **静态判不了** —— 那是**运行行为**
#                             （多引用特征读 mark 0/1/2，不读选择顺序）⇒ 只能靠真机证据
#   ★ 我一度还加了「说明里必须写合法取值」「mark 必须说明」两条，**已撤掉**：
#     那是**我自己的好习惯，不是规则的内容**。撤掉的证据是既有的
#     `test_rule3_named_entity_selection_is_ok` —— 它断言「`Param("selection", str)`
#     无说明也应通过」，编码的是**本意**。
#   ★ 定则：**门禁只验规则真正要求的**，不把偏好伪装成规则。
#
# ⚠ 核心断言（**含负例**）：
#   ① `selection` 声明成 `float`/`int` ⇒ **拒绝**（传数字不是声明式选择）
#   ② 正例：`selection: str`（**有无说明都行**）⇒ **通过**（不假阳性）
# ⚠ 判据刻意收窄 —— 避免重蹈事实 74（跨模块语义门禁实测 4/4 假阳性）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT / "mcp-server", REPO_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tool_registry import GateError, Param, ToolSpec, check_spec   # noqa: E402


def _spec(**kw) -> ToolSpec:
    base = dict(name="solidworks_x_y", title="t", module="sw_part",
                function="add_dimension", params=[], doc="")
    base.update(kw)
    return ToolSpec(**base)


#: ── 负例：必须被拒（句2 的真实错法）─────────────────────────────
REJECTED = [
    ("selection 声明成 float（把数字当选择传）",
     [Param("selection", float, description="__current_selection__")]),
    ("selection 声明成 int（把序号当选择传）",
     [Param("selection", int, description="index:0")]),
    ("selection 声明成 bool",
     [Param("selection", bool, default=False, description="x")]),
]


@pytest.mark.parametrize("label,params", REJECTED, ids=[c[0] for c in REJECTED])
def test_rule3_rejects_non_declarative_selection(label, params):
    """★ 这三条是**负例** —— 每一条对应一种真实的错法，必须被拦住。"""
    with pytest.raises(GateError) as e:
        check_spec(_spec(params=params))
    assert "规则 3" in str(e.value), str(e.value)


#: ── 正例：不许假阳性 ─────────────────────────────────────────────
ACCEPTED = [
    ("selection=str 且说明写了取值",
     [Param("selection", str, default="__current_selection__",
            description="Declarative EDGE selection: '__current_selection__' or 'index:<n>'.")]),
    ("★ selection=str 但**没有说明** —— 也必须通过（既有测试编码的本意）",
     [Param("selection", str, default="__current_selection__", description="")]),
    ("没有任何 selection 参数",
     [Param("depth_mm", float, default=1.0, description="depth in mm")]),
    ("有 mark 参数但没有说明 —— ★ 句3 静态不可判，不许在这里拦",
     [Param("mark", int, default=0, description="")]),
]


@pytest.mark.parametrize("label,params", ACCEPTED, ids=[c[0] for c in ACCEPTED])
def test_rule3_accepts(label, params):
    """★ 这 4 条是**正例** —— 判据不许在这里假阳性（事实 74 的教训）。"""
    check_spec(_spec(params=params))          #: 不抛即通过


def test_mark_assignment_is_not_statically_checkable():
    """★ 把「句3 静态不可判」这件事**写成一条断言**，免得别人以为它被漏掉了。

    句3 是「按 mark 分配」—— 那是**运行行为**（多引用特征读 mark 0/1/2，不读选择顺序）。
    ⇒ 静态检查**做不到**；它的证据只能来自真机（本仓真机证据见 `tools/capture_*.py`）。
    """
    #: 「声明 mark 但无说明」必须**通过** —— 因为说明不是规则要求
    check_spec(_spec(params=[Param("mark", int, default=0, description="")]))
    #: 而「mark 作为裸参数」也不在 `_BARE_COORD_NAMES` 里 —— 这正是句3 无判据的体现
    from tool_registry import _BARE_COORD_NAMES
    assert "mark" not in _BARE_COORD_NAMES


def test_existing_tools_still_pass():
    """★ 回归：全量注册表必须仍能通过 —— 新判据不许拦住**已挂出去**的工具。"""
    from register_capabilities import all_specs

    for s in all_specs():
        check_spec(s)
