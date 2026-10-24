"""第一批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch1.py
# 定位:   `docs/history/T-011-expose-capabilities-assessment.md` 第一批的守卫；
#         确保「声明里写的 module/function/参数」与 `scripts/` 里的**真实签名**一致。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本测试的**核心价值**：声明是**手抄**的，而手抄会漂移。
#   故这里用 `inspect.signature` 对着真实函数核 —— 声明与实现不一致就红。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
from enum import Enum
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"


class _RF(str, Enum):
    """`response_format` 的**真** Enum 替身。

    ⚠ 用普通类会得到 `PydanticSchemaGenerationError`（本项目已踩过一次）——
    **替身要替到「被依赖的那部分行为」为止。**
    """

    JSON = "json"


class _Base:
    """最小基类；本文件的断言不依赖 Pydantic 的字段行为。

    ⚠ 必须带 `response_format` —— 生成的函数体在调用 `run_locked` 时会读它。
    （第一版没有 ⇒ `AttributeError: '_P' object has no attribute 'response_format'`。）
    """

    response_format = _RF.JSON


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def registry():
    if str(MCP_DIR) not in sys.path:
        sys.path.insert(0, str(MCP_DIR))
    return _load("tool_registry_b1", MCP_DIR / "tool_registry.py")


@pytest.fixture(scope="module")
def batchmod(registry):
    return _load("tool_specs_batch1", MCP_DIR / "tool_specs_batch1.py")


@pytest.fixture(scope="module")
def batch(batchmod):
    return batchmod.SPECS_BATCH1


@pytest.fixture(scope="module")
def resolvers(batchmod):
    return batchmod.SIM_RESOLVERS


# ── ① 门禁全过 ──────────────────────────────────────────────────────
def test_batch_passes_its_own_gates(registry, batch):
    assert registry.check_specs(batch) == []


def test_batch_names_are_unique_and_nonempty(batch):
    assert len(batch) >= 5
    names = [s.name for s in batch]
    assert len(names) == len(set(names))


# ── ② **全声明式**（这是本次改动的目标）───────────────────────────
def test_no_spec_needs_extra_op_anymore(batch):
    """加了 `inject` 之后，本批**不该**再有任何 `extra_op`。

    ⚠ 这条断言就是「注入语义建模」的目的：让**声明式覆盖到真实函数**，
    而不是靠逃生口把注入逻辑写死在声明文件里。
    """
    leftovers = [s.name for s in batch if s.extra_op is not None]
    assert leftovers == [], "仍有工具走 extra_op：%r" % leftovers


def test_every_spec_declares_an_injection_kind(batch):
    for spec in batch:
        inj = spec.inject or ("model" if spec.needs_model else "")
        assert inj, "工具 %s 既没 inject 也没 needs_model" % spec.name


def test_injection_kinds_have_resolvers(batch, resolvers):
    """声明用到的每种注入，都必须有对应解析器 —— 否则运行期才炸。"""
    used = {s.inject or ("model" if s.needs_model else "") for s in batch}
    used.discard("")
    missing = used - set(resolvers)
    assert missing == set(), "这些注入没有解析器：%r" % missing


# ── ③ 声明与**真实签名**一致（防手抄漂移）─────────────────────────
def test_declared_functions_exist_and_params_match(batch):
    """凡走 `module`/`function` 的声明，其参数必须**真是**那个函数的形参。

    ⚠ 本文件最重要的断言：声明是手抄的，手抄会漂移。
    核验时剔除三类**不由声明参数直传**的名字：
      1. 注入型参数（`model` / `sw_app` / `study`）—— 注册器负责传
      2. `omitted_params` —— **显式声明省略**的
      3. `param_alias` 里映射为 `None` 的 —— 由**解析器**消费、不进目标函数
    """
    sys.path.insert(0, str(REPO_ROOT))
    injected = {"model", "sw_app", "study"}
    checked = 0
    for spec in batch:
        if not spec.module or not spec.function:
            continue
        mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
        fn = getattr(mod, spec.function)
        real = {p.name for p in inspect.signature(fn).parameters.values()}
        expected = real - injected - set(spec.omitted_params)
        declared_targets = set()
        for p in spec.params:
            if p.name in spec.param_alias:
                dst = spec.param_alias[p.name]
                if dst is None:
                    continue
                declared_targets.add(dst)
            else:
                declared_targets.add(p.name)
        assert declared_targets == expected, (
            "工具 %s 折算后的目标参数 %r 与 %s.%s 的真实形参 %r 不一致"
            % (spec.name, sorted(declared_targets), spec.module, spec.function, sorted(expected))
        )
        consumed = {k for k, v in spec.param_alias.items() if v is None}
        assert consumed <= {p.name for p in spec.params}, (
            "工具 %s 的 param_alias 指向未声明参数" % spec.name
        )
        checked += 1
    assert checked >= 4, "至少应核到 4 条走 module/function 的声明（实际 %d）" % checked


def test_injected_params_are_not_declared(batch):
    """注入型参数**不得**出现在声明里（否则会从 Pydantic 模型里暴露出去）。"""
    banned = {"model", "sw_app", "study", "params", "response_format"}
    for spec in batch:
        for p in spec.params:
            assert p.name not in banned, "工具 %s 不该声明 %r" % (spec.name, p.name)


# ── ④ 命名与语义的正确性（这几条容易写错，值得钉住）───────────────
def test_every_name_is_solidworks_prefixed(batch):
    for spec in batch:
        assert spec.name.startswith("solidworks_"), spec.name
        assert spec.load_automation is True, "%s 需要 SolidWorks" % spec.name


def test_mesh_units_are_named_mm(batch):
    """网格尺寸/容差参数**必须**带 `_mm` 后缀（规则 2）。

    ⚠ 这条不是形式主义：本项目刚在 `CreateMesh` 上踩过「毫米当米」
    ⇒ 1950 万单元 / 20–25 GB。
    """
    for spec in batch:
        for p in spec.params:
            low = p.name.lower()
            if "element_size" in low or "tolerance" in low:
                assert p.name.endswith("_mm"), (
                    "工具 %s 的 %r 是长度参数却没带 _mm 后缀" % (spec.name, p.name)
                )


def test_at_least_one_spec_uses_param_alias(batch):
    """至少有一条真的用了 `param_alias`（否则这个机制没被覆盖）。"""
    assert any(s.param_alias for s in batch)


def test_read_only_tools_declare_no_side_effects(batch):
    ro = [s.name for s in batch if s.read_only]
    assert "solidworks_topology_evidence" in ro
    assert "solidworks_mold_evidence" in ro


def test_every_spec_has_a_doc(batch):
    for spec in batch:
        assert spec.doc.strip(), "%s 没有 doc（会变成空工具描述）" % spec.name


# ── ⑤ 端到端：注入真的按**关键字**传进了目标函数 ──────────────────
def test_injection_reaches_the_target_function(registry, batch, monkeypatch):
    """用假解析器跑 `solidworks_mold_evidence`：`model` 必须按名字传进目标函数。"""
    seen = {}

    def fake_evidence(model):  # 形参名必须与 inject 值一致
        seen["model"] = model
        return {"ok": True}

    fake_mod = type(sys)("scripts.sw_mold")
    fake_mod.mold_evidence = fake_evidence
    monkeypatch.setitem(sys.modules, "scripts.sw_mold", fake_mod)

    spec = next(s for s in batch if s.name == "solidworks_mold_evidence")
    sentinel = object()
    model_cls = registry.build_input_model(spec, _Base, _RF)
    fn = registry.make_tool_function(
        spec, model_cls,
        lambda op, rf, load_automation=True: op(),
        resolvers={"model": lambda _p: sentinel},
    )
    assert fn(_Base()) == {"ok": True}   # 替身要带 response_format
    assert seen["model"] is sentinel


def test_param_alias_none_consumes_without_passing(registry, batch, monkeypatch):
    """`param_alias[x] = None` 的参数**不得**进目标函数（由解析器消费）。"""
    captured_kwargs = {}

    def fake_run(study, *, units=0, element_size=0.0, tolerance=0.0):
        captured_kwargs.update(study=study, units=units,
                               element_size=element_size, tolerance=tolerance)
        return 0

    fake_mod = type(sys)("scripts.sw_topology")
    fake_mod.run_topology_study = fake_run
    monkeypatch.setitem(sys.modules, "scripts.sw_topology", fake_mod)

    spec = next(s for s in batch if s.name == "solidworks_topology_run")

    class _P:
        response_format = _RF.JSON
        study_name = "S1"
        units = 0
        element_size_mm = 4.9
        tolerance_mm = 0.245

    model_cls = registry.build_input_model(spec, _Base, _RF)
    study_sentinel = object()
    fn = registry.make_tool_function(
        spec, model_cls,
        lambda op, rf, load_automation=True: op(),
        resolvers={"study": lambda _p: study_sentinel},
    )
    fn(_P())
    assert captured_kwargs["study"] is study_sentinel
    # 对外名 `_mm` 被折算回实现里的裸名
    assert captured_kwargs["element_size"] == 4.9
    assert captured_kwargs["tolerance"] == 0.245
    # `study_name` 由解析器消费 ⇒ 不该出现在传给函数的关键字里
    assert "study_name" not in captured_kwargs
