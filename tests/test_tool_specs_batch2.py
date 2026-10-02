"""第二批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch2.py
# 定位:   第二批的守卫 + **分类表的自洽性检查**。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 核心断言：声明参数与真实签名一致；**分类表里点到的函数必须真存在**
#   （分类是**判断**，但「判断指向的函数是否存在」是机器可验的）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"


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
    return _load("tool_registry_b2", MCP_DIR / "tool_registry.py")


@pytest.fixture(scope="module")
def batchmod(registry):
    return _load("tool_specs_batch2", MCP_DIR / "tool_specs_batch2.py")


@pytest.fixture(scope="module")
def batch(batchmod):
    return batchmod.SPECS_BATCH2


# ── ① 门禁与形状 ────────────────────────────────────────────────────
def test_batch_passes_its_own_gates(registry, batch):
    assert registry.check_specs(batch) == []


def test_names_unique_and_prefixed(batch):
    names = [s.name for s in batch]
    assert len(names) == len(set(names))
    for s in batch:
        assert s.name.startswith("solidworks_"), s.name


def test_all_declarative_no_extra_op(batch):
    leftovers = [s.name for s in batch if s.extra_op is not None]
    assert leftovers == [], "不应再有 extra_op：%r" % leftovers


def test_every_spec_has_injection_and_doc(batch):
    for s in batch:
        assert (s.inject or s.needs_model), "%s 没有注入方式" % s.name
        assert s.doc.strip(), "%s 没有 doc" % s.name


# ── ② 声明与**真实签名**一致 ──────────────────────────────────────
def test_declared_params_match_real_signature(batch):
    """与 batch1 同一条纪律：声明是手抄的，手抄会漂移。"""
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
        declared = set()
        for p in spec.params:
            if p.name in spec.param_alias:
                dst = spec.param_alias[p.name]
                if dst is None:
                    continue
                declared.add(dst)
            else:
                declared.add(p.name)
        assert declared == expected, (
            "工具 %s 折算后 %r ≠ %s.%s 的真实形参 %r"
            % (spec.name, sorted(declared), spec.module, spec.function, sorted(expected))
        )
        checked += 1
    assert checked >= 4


def test_omitted_params_are_real_and_documented(batch):
    """`omitted_params` 必须**真是**那个函数的形参（否则是无效的省略声明）。"""
    sys.path.insert(0, str(REPO_ROOT))
    for spec in batch:
        if not spec.omitted_params:
            continue
        mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
        fn = getattr(mod, spec.function)
        real = {p.name for p in inspect.signature(fn).parameters.values()}
        for name in spec.omitted_params:
            assert name in real, (
                "工具 %s 声明省略 %r，但 %s.%s 没有这个形参"
                % (spec.name, name, spec.module, spec.function)
            )


# ── ③ ★ 分类表的自洽性（机器可验的部分）───────────────────────────
def test_classification_functions_all_exist(batchmod):
    """分类是**判断**，但「判断指向的函数存在吗」是**机器可验**的。

    ⚠ 这条能抓住最糟的一类错：分类表里写了一个**不存在**的函数名
    （看起来像做过功课，实际是编的）。
    """
    sys.path.insert(0, str(REPO_ROOT))
    missing: list[str] = []
    seen = 0
    for cls, payload in batchmod.CLASSIFICATION.items():
        for module, fns in payload.items():
            if module in ("判据", "理由", "缺的基础设施"):
                continue
            try:
                mod = __import__("scripts.sw_%s" % module, fromlist=["_"])
            except ImportError:
                missing.append("模块 scripts.sw_%s 不存在（分类表 %s）" % (module, cls))
                continue
            for fn_name in fns:
                seen += 1
                if not hasattr(mod, fn_name):
                    missing.append("scripts.sw_%s.%s 不存在（分类表 %s）"
                                   % (module, fn_name, cls))
    assert missing == [], "分类表指向了不存在的函数：\n  - " + "\n  - ".join(missing)
    assert seen >= 30, "分类表覆盖的函数太少（%d），可能没认真填" % seen


def test_classification_covers_the_four_kinds(batchmod):
    kinds = set(batchmod.CLASSIFICATION)
    for expect in ("A_直接可暴露", "B_需声明式选择解析",
                   "C_需spec展平层", "D_不该暴露"):
        assert expect in kinds, "分类表缺 %s" % expect


def test_every_class_states_its_criterion(batchmod):
    """每一类都要写**判据**（A 类是「判据」键；B/C 是「缺的基础设施」；D 是「理由」）。

    ⚠ 没有判据的分类就是「凭感觉分堆」—— 那样后续批次无法照办。
    """
    for cls, payload in batchmod.CLASSIFICATION.items():
        keys = set(payload)
        assert keys & {"判据", "缺的基础设施", "理由"}, (
            "分类 %s 没写判据/理由/缺什么 ⇒ 后续无法照办" % cls
        )


def test_classified_functions_do_not_overlap(batchmod):
    """同一个函数**不得**同时落在两类里（A 与 B/C/D 互斥）。"""
    seen: dict[str, str] = {}
    clashes: list[str] = []
    for cls, payload in batchmod.CLASSIFICATION.items():
        for module, fns in payload.items():
            if module in ("判据", "理由", "缺的基础设施"):
                continue
            for fn in fns:
                key = "%s.%s" % (module, fn)
                if key in seen and seen[key] != cls:
                    clashes.append("%s 同时在 %s 与 %s" % (key, seen[key], cls))
                seen[key] = cls
    assert clashes == [], "\n  - ".join(clashes)
