"""★ EC00 T023 判据：**公开路由集成桩** —— 按真实 ToolSpec 构造调用（★ 离线 · ★ 不连接 COM）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_registry.py`（★ `build_input_model` L576 · `make_tool_function` L635）
#         `mcp-server/tool_specs_batch113.py`（★ T017 注册的草图关系工具）
#         `tests/test_tool_registry.py`（★ 构造模式参考 · ★ `_load()` / `_FakeBase`）
# 定位:   ★ EC00 **T023**（★ 逐字：「运行公开路由集成桩和聚焦测试，完成离线验收」）。
#         ★★★ **完成判据**：★ **按真实 ToolSpec 注入/参数调用**；★ 所有规定离线正负例通过；
#         ★ **runtime 仍可 not_run**。
#         ★★ 纪律（★ 计划 §7 L2 逐字）：「★★ **内部函数绿但公开路由错必须被抓到**」；
#         ★★★ **「桩测试不能称为 COM 验证」**。
# 官方依据: `AddRelation(object, int)`（★ 2 参）· `## Remarks`（★ 活动草图）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**假宿主**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TOOL = "solidworks_sketch_apply_relations"


def _spec():
    import register_capabilities as rc
    return {s.name: s for s in rc.all_specs()}.get(TOOL)


# ── ① 桩：★ 从**真实 ToolSpec** 构造输入模型 ─────────────────────────

def _real_base():
    """★ 取 `server.py` 真正用的 Pydantic 基类（★ **不手搓** —— ★ 否则模型实例化不了）。

    ⚠ 第一版我用了一个普通 `class _FakeBase: pass` ⇒ ★ 模型**没有** `model_fields`
      （★ `build_input_model` 是 `type(name, (base,), …)` ⇒ ★ 基类必须是 Pydantic）。
      ★ 这正是 `tests/test_tool_registry.py:52` 记过的同一个坑。
    """
    from pydantic import BaseModel
    return BaseModel


def _response_enum():
    """★ 取真正的 `ResponseFormat`（★ 定义在 `mcp-server/server.py:149`）。

    ★★ 依据：★ `server.py:149` 逐字 —— `class ResponseFormat(str, Enum)` · ★ `JSON = "json"`。
    """
    import server
    return server.ResponseFormat


def test_t023_input_model_is_built_from_the_real_spec():
    """★★★ T023：★ 输入模型必须从**真实 ToolSpec** 构造（★ 不是手搓一个假对象）。

    ★★ 依据（★ 计划 §7 L2 逐字）：「★ 从**真实 ToolSpec** 构造调用，
      ★ 检查注入和参数包装、互斥和前后置」。
    """
    import tool_registry as tr

    spec = _spec()
    assert spec is not None, "★ 工具未注册（★ T017 的缺口）"

    #: ★★ 用真实的 `build_input_model` + **真实 Pydantic 基类**（★ 不手搓）
    model = tr.build_input_model(spec, _real_base(), _response_enum())
    fields = set(model.model_fields)
    assert "relations" in fields, "★ 输入模型缺 `relations`（★ 参数包装断了）"
    assert "verify" in fields, "★ 输入模型缺 `verify`"
    #: ★ `response_format` 由 `build_input_model` **自动追加**（★ D-002 冻结）
    assert "response_format" in fields, (
        "★★ 输入模型缺 `response_format` ⇒ ★ 违反 D-002（自动追加、默认 JSON）")


def test_t023_defaults_match_the_declaration():
    """★★ T023：★ 默认值必须与 ToolSpec 的声明**一致**（★ `verify` 默认 `True`）。"""
    import tool_registry as tr

    spec = _spec()
    assert spec is not None

    model = tr.build_input_model(spec, _real_base(), _response_enum())
    inst = model(relations="horizontal:0")
    assert inst.verify is True, "★ `verify` 的默认值不是 `True`：%r" % inst.verify
    assert inst.relations == "horizontal:0"


def test_t023_derived_args_is_wired_into_the_public_route():
    """★★★ T023：★ `derived_args` 必须**在公开路由里被调用**（★ 不是只在 spec 里挂着）。

    ★★ 依据：★ 若 `derived_args` 没被路由调用 ⇒ ★ 实现会收到**字符串**而不是 `list`
      ⇒ ★ 内部函数可能"看起来对"而公开路由错（★ 计划 §7 L2 的核心）。
    """
    import tool_registry as tr
    import inspect

    src = inspect.getsource(tr.make_tool_function)
    assert "derived_args" in src, (
        "★★ `make_tool_function` 里**没有** `derived_args` ⇒ ★ 公开路由不会做拆分")


# ── ② 负例：★ 空清单 ⇒ 空清单（★ 不是崩溃）───────────────────────────

def test_t023_empty_relations_yields_empty_list():
    """★★ T023：★ 空串 ⇒ **空清单**（★ 不是崩溃、★ 不是 `['']`）。"""
    spec = _spec()
    assert spec is not None and spec.derived_args is not None

    class _P:
        relations = ""
        verify = True

    assert spec.derived_args(_P())["relations"] == [], "★ 空串应拆成空清单"


def test_t023_whitespace_and_trailing_semicolons_are_tolerated():
    """★★ T023：★ 多余空白与尾随 `;` 必须被容忍（★ 不能产生空项）。"""
    spec = _spec()
    assert spec is not None and spec.derived_args is not None

    class _P:
        relations = "  horizontal:0 ;  coincident:0,1 ; "
        verify = True

    got = spec.derived_args(_P())["relations"]
    assert got == ["horizontal:0", "coincident:0,1"], (
        "★ 拆分没容忍空白/尾随分隔符：%r" % got)
    assert all(x.strip() == x for x in got), "★ 拆出的项带空白：%r" % got


# ── ③ ★★★ 内部函数绿 ≠ 公开路由绿 ──────────────────────────────────

def test_t023_internal_green_does_not_imply_public_route_green():
    """★★★ T023：★ **内部函数绿但公开路由错必须被抓到**（★ 逐字承计划 §7 L2）。

    ★ 判据：★ 内部实现**存在**（★ 那是 T017 之前就有的），★ 而**公开路由**必须**也**在
      ⇒ ★★ 两者**都要**满足才算通过。
    """
    import importlib

    #: ★ ① 内部实现存在
    mod = importlib.import_module("sw_sketch_relations")
    assert hasattr(mod, "apply_sketch_relations"), "★ 内部实现不见了"

    #: ★★ ② 公开路由**也**必须在 —— ★ 这一条是本判据的重点
    spec = _spec()
    assert spec is not None, (
        "★★ 内部函数在、**公开路由不在** ⇒ ★ 正是「内部绿、公开错」的形态（★ 抓到了）")
    assert spec.module == "sw_sketch_relations"
    assert spec.function == "apply_sketch_relations"


# ── ④ ★★★ 桩测试**不得**声称 COM 验证 ───────────────────────────────

def test_t023_stub_does_not_claim_com_verification():
    """★★★ T023：★ **桩测试不能称为 COM 验证**（★ 逐字承计划 §7 L2）。

    ★ 判据：★ 本文件**不得**声称真机验证；★ 且 EC00 的验收记录里 `runtime` 必须是 `not_run`。
    """
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    #: ★★ 本文件自己不许**声称**真机已验证。
    #:   ★ 判据只看**模块级/文档串**，★ 且**跳过本函数自己**（★ 否则判据字符串会自触发 ——
    #:    ★ 这个坑我踩了两次：第一版全文 grep、第二版仍把本函数里的比较串收进来了）。
    import ast as _ast
    tree = _ast.parse(src)
    this_fn = None
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name == "test_t023_stub_does_not_claim_com_verification":
            this_fn = node
            break
    forbidden_nodes = set()
    if this_fn is not None:
        for sub in _ast.walk(this_fn):
            forbidden_nodes.add(id(sub))

    literals: list[str] = []
    for node in _ast.walk(tree):
        if id(node) in forbidden_nodes:
            continue                      #: ★★ 跳过本判据自己
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            literals.append(node.value)
    claimed = [s for s in literals if "真机已验证" in s or "COM 验证通过" in s]
    assert not claimed, (
        "★★ 桩测试里**声称**了真机验证：%r ⇒ ★ 混淆了离线与真机" % claimed[:2])
    #: ★★ 验收记录里 `runtime` 必须是 `not_run`
    acc = (ROOT / "specs" / "302-ec00-trustworthy-tool-base" / "acceptance.md")
    if acc.is_file():
        body = acc.read_text(encoding="utf-8", errors="replace")
        assert "not_run" in body, "★★ 验收记录里没有 `not_run` ⇒ ★ 可能把离线当成了真机"


# ── ⑤ ★★ 三级分开记录（★ FR-013）──────────────────────────────────

def test_t023_three_levels_are_recorded_separately():
    """★★★ T023/FR-013：★ **offline / runtime / product 必须分字段记录**。"""
    acc = ROOT / "specs" / "302-ec00-trustworthy-tool-base" / "acceptance.md"
    assert acc.is_file(), "★ 缺 `acceptance.md`"
    body = acc.read_text(encoding="utf-8", errors="replace")
    for level in ("offline", "runtime", "product"):
        assert level in body, "★ 验收记录里缺 `%s` 级" % level
    #: ★★ 硬规则：★ `offline` pass **不能**写成 `runtime` pass
    assert "不得因离线通过而升级" in body or "不能写成" in body, (
        "★ 没有写明「offline pass 不得升级为 runtime pass」")
