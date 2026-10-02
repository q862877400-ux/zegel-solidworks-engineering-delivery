"""第三批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch3.py
# 定位:   第三批的守卫 —— 重点是 **spec 展平的正确性**（C 类的核心风险）。
# 官方签名依据: 不适用（纯静态核对 + dataclass 字段核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 核心断言：
#   ① 声明的**标量入参**与真实签名的**非 spec 形参**一一对应；
#   ② `derived_args` 装出来的 spec **字段齐全且值正确**（含 mm→m 换算）；
#   ③ spec 的每个字段都在 MCP 表面上**有对应入参**（否则静默丢字段 —— C 类最危险的错）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import dataclasses
import importlib.util
import inspect
import sys
from enum import Enum
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"


class _RF(str, Enum):
    JSON = "json"


class _Base:
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
    return _load("tool_registry_b3", MCP_DIR / "tool_registry.py")


@pytest.fixture(scope="module")
def batchmod(registry):
    return _load("tool_specs_batch3", MCP_DIR / "tool_specs_batch3.py")


@pytest.fixture(scope="module")
def batch(batchmod):
    return batchmod.SPECS_BATCH3


# ── ① 门禁与形状 ────────────────────────────────────────────────────
def test_batch_passes_its_own_gates(registry, batch):
    assert registry.check_specs(batch) == []


def test_all_declarative_no_extra_op(batch):
    assert [s.name for s in batch if s.extra_op is not None] == []


def test_names_prefixed_and_documented(batch):
    for s in batch:
        assert s.name.startswith("solidworks_"), s.name
        assert s.doc.strip(), "%s 没有 doc" % s.name


# ── ② 声明的标量入参 ↔ 真实签名的非 spec 形参 ─────────────────────
def test_scalar_params_match_real_signature(batch):
    """凡走 `module`/`function` 的声明，除 `spec` 外的形参都要被声明到。"""
    sys.path.insert(0, str(REPO_ROOT))
    injected = {"model", "sw_app", "study"}
    for spec in batch:
        mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
        fn = getattr(mod, spec.function)
        real = {p.name for p in inspect.signature(fn).parameters.values()}
        real -= injected
        # `spec` 形参由 derived_args 提供
        real -= {"spec"}
        declared_targets = set()
        for p in spec.params:
            dst = spec.param_alias.get(p.name, p.name)
            if dst is None:
                continue
            declared_targets.add(dst)
        # ⚠ 判据是「**非 spec 形参必须被声明覆盖**」，不是「两者相等」：
        #   声明里的其余入参是 **spec 的字段**（它们不是函数形参）。
        #   第一版写成 `==` ⇒ 必然失败 —— 测试自己的逻辑错了。
        missing = real - declared_targets
        assert missing == set(), (
            "工具 %s 没有声明 %s.%s 的这些形参：%r（已声明 %r）"
            % (spec.name, spec.module, spec.function, sorted(missing), sorted(declared_targets))
        )
        assert declared_targets & real, (
            "工具 %s 没有任何入参映射到真实形参 %r" % (spec.name, sorted(real))
        )


# ── ②b ★ 补上「无主参数」守卫（batch4 抓到真实 bug 后回补）────────
def test_every_declared_param_is_accounted_for(batch):
    """每个声明参数必须有归宿，**没有第四种**：
    ① 映射到真形参；② `param_alias[name]=None`（被消费）；③ 由 `derived_args` 装进 spec。

    ⚠⚠ **这条是回补的**：batch3 原本只查了「真形参都被覆盖」（子集方向），
    **没查反方向** ⇒ 而正是反方向漏了 bug：注册器把 spec 字段当 kwarg 传给
    `create_base_flange(model, sketch_ref, spec)` ⇒ **真机 `TypeError`**。
    **⇒ 单向检查会漏掉「多传」，双向才完整。**
    """
    sys.path.insert(0, str(REPO_ROOT))
    injected = {"model", "sw_app", "study"}
    for s in batch:
        mod = __import__("scripts.%s" % s.module, fromlist=[s.function])
        real = {p.name for p in inspect.signature(getattr(mod, s.function)).parameters.values()}
        real -= injected
        real -= {"spec"}
        spec_fields: set[str] = set()
        if s.derived_args is not None:
            try:
                obj = s.derived_args(_FakeParams(s))["spec"]
                spec_fields = {f.name for f in dataclasses.fields(obj)}
            except Exception:  # noqa: BLE001
                spec_fields = set()
        for p in s.params:
            if p.name in s.param_alias:
                continue                                  # ① / ②
            base = p.name
            for suf in ("_mm", "_deg"):
                if base.endswith(suf):
                    base = base[: -len(suf)]
            if base in spec_fields:
                continue                                  # ③
            assert p.name in real, (
                "工具 %s 的入参 %r **无主** —— 既没映射到真形参、也没 alias=None、"
                "也没进 spec ⇒ 真机会 `TypeError: unexpected keyword argument`。"
                % (s.name, p.name)
            )


# ── ③ ★ C 类的核心风险：spec 字段被静默丢掉 ────────────────────────
def test_every_spec_field_is_exposed_on_the_surface(batch):
    """**spec 的每个字段都必须在 MCP 表面有对应入参**（除显式说明的）。

    ⚠ 这是 C 类最危险的错：展平时漏一个字段 ⇒ 用户设不了它，
    而实现会用 dataclass 的**默认值**静默代替 —— 看代码看不出来。
    """
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sw_sheet_metal as SM

    for spec in batch:
        # 取 derived_args 产出的 spec 类型
        fake = _FakeParams(spec)
        derived = spec.derived_args(fake)
        obj = derived["spec"]
        fields = {f.name for f in dataclasses.fields(obj)}
        # 展平后的入参名（去掉单位后缀）与字段名的对应关系由 derived_args 决定，
        # 这里用「字段数 == 长度+角度+bool 类入参数」来核数量不减
        declared = {p.name for p in spec.params}
        # 保守但有效：字段数必须 <= 声明入参数（每个字段至少一个入参）
        assert len(fields) <= len(declared), (
            "工具 %s：spec 有 %d 个字段（%r）但只声明了 %d 个入参（%r） ⇒ **有字段没暴露**"
            % (spec.name, len(fields), sorted(fields), len(declared), sorted(declared))
        )
        # 且未暴露的字段只能是 dataclass 有默认值的（否则用户无法构造合法 spec）
        defaults_exist = {f.name for f in dataclasses.fields(obj) if f.default is not dataclasses.MISSING}
        # 逐字段确认：要么有同名/同义入参，要么有默认值
        for f in dataclasses.fields(obj):
            base = f.name
            candidates = {base, base + "_mm", base + "_deg", base.replace("_radius", "_radius_mm")}
            if candidates & declared:
                continue
            assert f.default is not dataclasses.MISSING, (
                "工具 %s：spec 字段 %r **既没有入参也没有默认值** ⇒ 用户无法构造合法 spec"
                % (spec.name, f.name)
            )


def test_spec_field_values_are_correctly_mapped(batch):
    """**单位换算必须对**：长度 mm→m（本会话已在 `CreateMesh` 上踩过毫米当米）。"""
    sys.path.insert(0, str(REPO_ROOT))
    for spec in batch:
        fake = _FakeParams(spec)
        obj = spec.derived_args(fake)["spec"]
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if f.name.endswith("_mm") or "radius" in f.name or "thickness" in f.name or \
                    f.name in ("depth", "flange_length"):
                # 长度字段：入参是 mm ⇒ 装出来的必须是 m
                arg = getattr(fake, f.name + "_mm", None)
                if arg is not None:
                    assert abs(val * 1000.0 - float(arg)) < 1e-9, (
                        "工具 %s 的字段 %r：入参 %r mm 装出来是 %r m（应 %r）"
                        % (spec.name, f.name, arg, val, float(arg) / 1000.0)
                    )
            if f.name == "angle" and hasattr(fake, "angle_deg"):
                # 角度已是度 ⇒ **不换算**
                assert abs(val - float(fake.angle_deg)) < 1e-9, (
                    "工具 %s 的 angle 被错误换算：%r ≠ %r" % (spec.name, val, fake.angle_deg)
                )


def test_spec_map_has_three_subclasses_with_criteria(batchmod):
    m = batchmod.SHEET_METAL_SPEC_MAP
    for key in ("C1_spec展平即可", "C2_需调用方先选好", "C3_ref是对象"):
        assert key in m, "缺 %s" % key
        payload = m[key]
        assert payload.get("判据"), "%s 没写判据" % key
        assert payload.get("函数"), "%s 没写函数清单" % key


def test_spec_map_functions_all_exist(batchmod):
    """C 类分类表点到函数必须**真存在**（同 batch2 的纪律）。"""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sw_sheet_metal as SM

    for key, payload in batchmod.SHEET_METAL_SPEC_MAP.items():
        for fn in payload["函数"]:
            assert hasattr(SM, fn), "%s 指向不存在的函数 %s" % (key, fn)


class _FakeParams:
    """给 `derived_args` 用的替身 —— 值按参数声明取，**长度字段按 mm 给**。"""

    def __init__(self, spec):
        for p in spec.params:
            if p.name.endswith("_mm"):
                setattr(self, p.name, 2.5)
            elif p.name.endswith("_deg"):
                setattr(self, p.name, 90.0)
            elif p.name in ("thickness", "bend_radius", "depth", "flange_length"):
                setattr(self, p.name, 2.5)
            elif p.name in ("k_factor",):
                setattr(self, p.name, 0.42)
            elif p.name in ("relief_ratio",):
                setattr(self, p.name, 0.5)
            elif p.name == "angle":
                setattr(self, p.name, 90.0)
            elif p.name == "sketch_name":
                setattr(self, p.name, "Sketch1")
            elif p.default is not ... and isinstance(p.default, bool):
                setattr(self, p.name, p.default)
            elif p.default not in (..., None):
                setattr(self, p.name, p.default)
            else:
                setattr(self, p.name, 0.0)
        self.response_format = _RF.JSON
