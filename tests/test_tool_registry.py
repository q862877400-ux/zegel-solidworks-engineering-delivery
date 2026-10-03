"""声明式注册器的契约测试（**不需要 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_registry.py
# 定位:   `docs/T-011-expose-capabilities-assessment.md` 的实现层测试；
#         AGENTS.md 判据 A3（五统一门禁）在「注册期」的落地。
# 官方签名依据: 不适用（纯 Python 层）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本测试**不导入 mcp 库**（它是宿主依赖）⇒ 用一个最小的假 mcp 对象。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "mcp-server" / "tool_registry.py"


def _load():
    spec = importlib.util.spec_from_file_location("tool_registry_under_test", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tool_registry_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


# ── 假宿主（够用即可：只记录注册了什么）─────────────────────────────
class _FakeMcp:
    def __init__(self):
        self.registered = {}

    def tool(self, name=None, title=None, annotations=None):
        def deco(fn):
            self.registered[name] = {"fn": fn, "title": title, "annotations": annotations}
            return fn
        return deco


from pydantic import BaseModel, ConfigDict


class _FakeBase(BaseModel):
    """**真** Pydantic 基类。

    ⚠ 第一版这里写的是一个普通类 ⇒ `build_input_model` 生成的模型**实例化不了**
    （`TypeError: ...() takes no arguments`），三条测试因此假红。
    **⇒ 替身要替到「被依赖的那部分行为」为止**：本模块依赖的是 Pydantic 的字段语义，
    不是「有个类就行」。
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


from enum import Enum


class _RF(str, Enum):
    """`response_format` 的替身 —— **必须是真 Enum**。

    ⚠ 第二版这里写的是普通类（`JSON = "json"`）⇒ Pydantic 无法为它生成 schema
    （`PydanticSchemaGenerationError: Unable to generate pydantic-core schema`）。
    **⇒ 与 `_FakeBase` 同一条教训：替身要替到「被依赖的那部分行为」为止。**
    """

    JSON = "json"
    MARKDOWN = "markdown"


def _ok_spec(mod):
    return mod.ToolSpec(
        name="solidworks_topology_create_study",
        title="Create Topology Study",
        module="sw_topology",
        function="create_topology_study",
        params=[mod.Param("study_name", str, default="S1", description="研究名")],
        doc="建拓扑研究。",
    )


# ── ① 门禁：规则 1 命名 ────────────────────────────────────────────
@pytest.mark.parametrize("bad", [
    "topology_create_study",            # 缺前缀
    "solidworks-Topology-Create",       # 非蛇形
    "Solidworks_topology_create",       # 大寫开头
    "solidworks_topology_create_研究",   # 非 ASCII
])
def test_rule1_bad_names_rejected(bad):
    mod = _load()
    s = _ok_spec(mod)
    object.__setattr__(s, "name", bad)
    with pytest.raises(mod.GateError, match="规则 1"):
        mod.check_spec(s)


def test_rule1_accepts_cadstudio_headless_names():
    mod = _load()
    s = _ok_spec(mod)
    object.__setattr__(s, "name", "cadstudio_write_open_format")
    object.__setattr__(s, "load_automation", False)
    mod.check_spec(s)  # 不抛即为过


# ── ② 门禁：规则 3 禁裸坐标 ───────────────────────────────────────
#: ★★★ 2026-10-03（轮 470）**把 `x_mm` 从本名单移除** ——
#:   轮 433 在门禁里**已经判定**过这件事（`mcp-server/tool_registry.py` L120-129，逐字）：
#:   > ★★★ **"裸"的定义就是「没有单位信息」** —— 而 `_mm` 后缀**恰恰携带着单位信息**
#:   > （★ 规则 2 **要求**长度参数以 `_mm` 结尾）⇒ ★★ 所以**以 `_mm` 结尾的坐标不是裸坐标** ⇒ 放过。
#:   > ★★★ 矛盾在**精确黑名单**那三个条目（`x_mm`/`y_mm`/`z_mm`）：**两条规则自相矛盾** ⚠（本轮查明）
#:   > ⇒ ★ 而**无单位**的（`x` · `boundary_z` · `d1_x` · `major_y`）**照旧拦** ✓
#:   ⇒ ★★ 即 `x_mm` **本就该放过**（★ 否则"规则 2 要求带 `_mm`"与"规则 3 拦 `_mm`"打架）——
#:     ★ 本测试只更新在轮 433 **之后**（★ 它从那时起就一直红）。
#:   ★ 反过来 ★ **改门禁去拦 `x_mm` 是错的** —— 那会**把两条规则的自相矛盾重新引回来** ⚠
@pytest.mark.parametrize("bad_param", ["x", "y", "z", "point"])
def test_rule3_bare_coordinates_rejected(bad_param):
    mod = _load()
    s = mod.ToolSpec(
        name="solidworks_topology_create_study", title="t",
        module="sw_topology", function="f",
        params=[mod.Param(bad_param, float, default=0.0)],
    )
    with pytest.raises(mod.GateError, match="规则 3"):
        mod.check_spec(s)


def test_rule3_named_entity_selection_is_ok():
    mod = _load()
    s = mod.ToolSpec(
        name="solidworks_simulation_select_face", title="t",
        module="sw_simulation", function="select_face_at",
        params=[mod.Param("selection", str, default="fixed_face")],
    )
    mod.check_spec(s)


# ── ③ 门禁：不混用 solidworks_/cadstudio_ ────────────────────────
def test_mixing_headless_flag_with_solidworks_prefix_rejected():
    mod = _load()
    s = _ok_spec(mod)
    object.__setattr__(s, "load_automation", False)
    with pytest.raises(mod.GateError, match="headless"):
        mod.check_spec(s)


# ── ④ 门禁：没有可执行体 / 重复参数 / 自己声明 response_format ────
def test_missing_body_rejected():
    mod = _load()
    with pytest.raises(mod.GateError, match="没有可执行体"):
        mod.check_spec(mod.ToolSpec(name="solidworks_a_b", title="t"))


def test_duplicate_param_rejected():
    mod = _load()
    s = mod.ToolSpec(name="solidworks_a_b", title="t", module="m", function="f",
                     params=[mod.Param("study_name", str, default="x"),
                             mod.Param("study_name", str, default="y")])
    with pytest.raises(mod.GateError, match="重复"):
        mod.check_spec(s)


def test_declaring_response_format_rejected():
    mod = _load()
    s = mod.ToolSpec(name="solidworks_a_b", title="t", module="m", function="f",
                     params=[mod.Param("response_format", str, default="json")])
    with pytest.raises(mod.GateError, match="response_format"):
        mod.check_spec(s)


# ── ⑤ `check_specs` 不短路：一次报出全部问题 ──────────────────────
def test_check_specs_reports_all_problems_not_just_first():
    mod = _load()
    bad1 = mod.ToolSpec(name="nope", title="t", module="m", function="f")
    bad2 = mod.ToolSpec(name="solidworks_ok_name", title="t")           # 缺可执行体
    bad3 = mod.ToolSpec(name="solidworks_ok_name", title="t", module="m", function="f")
    problems = mod.check_specs([bad1, bad2, bad3])
    assert len(problems) >= 3, problems
    assert any("规则 1" in p for p in problems)
    assert any("没有可执行体" in p for p in problems)
    assert any("重复" in p for p in problems)


# ── ⑥ 生成：模型字段与函数形状 ────────────────────────────────────
def test_build_input_model_fields():
    """模型有正确的字段与默认值。

    ⚠ 第三版这里直接读了 `model.study_name`（**类**属性）⇒ `AttributeError`。
    Pydantic v2 里字段值属于**实例**，类上只有 `model_fields`。
    **⇒ 又一次同一教训：替身/断言要对着真实行为写。**
    """
    mod = _load()
    model = mod.build_input_model(_ok_spec(mod), _FakeBase, _RF)
    # 类上查字段声明
    assert "study_name" in model.model_fields
    assert "response_format" in model.model_fields
    assert model.model_fields["study_name"].default == "S1"
    # 实例上查字段值
    inst = model()
    assert inst.study_name == "S1"
    assert inst.response_format == _RF.JSON
    # 必填字段缺失应当报错（证明它真是必填）
    spec_req = mod.ToolSpec(
        name="solidworks_topology_create_study", title="t",
        module="sw_topology", function="f",
        params=[mod.Param("study_name", str)],   # 无默认 ⇒ 必填
    )
    model_req = mod.build_input_model(spec_req, _FakeBase, _RF)
    with pytest.raises(Exception):
        model_req()


def test_generated_function_calls_module_function_with_kwargs(monkeypatch):
    mod = _load()
    calls = {}

    fake = type(sys)("scripts.sw_topology")
    def create_topology_study(**kw):
        calls.update(kw)
        return {"study": "ok"}
    fake.create_topology_study = create_topology_study
    monkeypatch.setitem(sys.modules, "scripts.sw_topology", fake)

    captured = {}

    def run_locked(op, rf, load_automation=True):
        captured["load_automation"] = load_automation
        return op()

    spec = _ok_spec(mod)
    model = mod.build_input_model(spec, _FakeBase, _RF)
    fn = mod.make_tool_function(spec, model, run_locked)
    got = fn(model(study_name="Hello", response_format="json"))
    assert calls == {"study_name": "Hello"}
    assert captured["load_automation"] is True
    assert got == {"study": "ok"}


def test_register_all_or_nothing(monkeypatch):
    mod = _load()
    mcp = _FakeMcp()
    good = _ok_spec(mod)
    bad = mod.ToolSpec(name="bad_name", title="t", module="m", function="f")
    with pytest.raises(mod.GateError, match="未注册任何工具"):
        mod.register(mcp, [good, bad], _FakeBase, _RF, lambda op, rf, load_automation=True: op())
    assert mcp.registered == {}, "有坏声明时不得注册任何一个"


def test_register_happy_path_records_annotations(monkeypatch):
    mod = _load()
    mcp = _FakeMcp()
    fake = type(sys)("scripts.sw_topology")
    fake.create_topology_study = lambda **kw: {"ok": True}
    monkeypatch.setitem(sys.modules, "scripts.sw_topology", fake)

    spec = _ok_spec(mod)
    spec.read_only = True
    names = mod.register(mcp, [spec], _FakeBase, _RF,
                         lambda op, rf, load_automation=True: op())
    assert names == [spec.name]
    assert spec.name in mcp.registered
    ann = mcp.registered[spec.name]["annotations"]
    assert ann["readOnlyHint"] is True
    assert ann["destructiveHint"] is False
    assert ann["openWorldHint"] is False


# ── ⑦ 逃生口：有自定义后处理的工具仍可注册 ────────────────────────
def test_extra_op_escape_hatch():
    mod = _load()
    seen = {}

    def custom(params):
        seen["hit"] = params.study_name
        return {"custom": True}

    spec = mod.ToolSpec(
        name="solidworks_topology_create_study", title="t",
        params=[mod.Param("study_name", str, default="S")],
        extra_op=custom,
    )
    mod.check_spec(spec)
    model = mod.build_input_model(spec, _FakeBase, _RF)
    fn = mod.make_tool_function(spec, model, lambda op, rf, load_automation=True: op())
    assert fn(model(response_format="json")) == {"custom": True}
    assert seen["hit"] == "S"
