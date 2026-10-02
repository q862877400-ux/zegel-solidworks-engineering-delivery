"""第四批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch4.py
# 定位:   第四批（钣金 C2/C3）的守卫。重点：
#         ① `pre_call`（选择副作用）确实配齐；② ref 参数按实现**真实用法**处理；
#         ③ `create_draft` 的静默参数 `face_ref` 被**显式省略**。
# 官方签名依据: 不适用（纯静态核对 + dataclass 字段核对）
# 许可:   本仓库 MIT。无第三方代码引入。
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


def _derived_args_or_skip(spec, params):
    """调 `spec.derived_args(params)`；**若它碰了活 COM 就带原因 skip**。

    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（测试卫生修复）
    # 文件:   tests/test_tool_specs_batch4.py —— 本文件自身
    #         `mcp-server/tool_specs_batch4.py` 的 `_swept_refs_and_spec`
    # 定位:   ⚠⚠ **本文件的文档串承诺「不依赖 `mcp` 库、**不连 SolidWorks**」，
    #         而实际上有 spec 的 `derived_args` **会碰 COM**：
    #         `_swept_refs_and_spec` 里调 `resolve_entity(model, '__current_selection__',
    #         "EDGE")` —— 它**要求 SolidWorks 里已有一条**被选中的边**。**
    #
    #         **⇒ 后果：这两个测试在干净机器上**必然失败**（`RuntimeError: 没有活动文档`），
    #            而「以前能过」纯属**巧合** —— 2026-10-01（轮 44）发现：先前之所以绿，
    #            是因为我探测时**恰好选中过边**。**
    #
    #         **⇒ 三种处理，选了第三种：**
    #          ① 让它失败 ⇒ 干净机器上恒红，**且红得没有信息**（看着像代码 bug）；
    #          ② `skip` 但不说为什么 ⇒ 与事实 3「文档串与代码不符比没有文档更糟」同类；
    #          ③ **带**原因** skip**（本函数）—— 明说「这条 spec 的 derived_args 碰了活 COM」，
    #             让契约违约**可见**，而不是被吞掉。
    #         ⚠ **仍然只吞「碰 COM」这一类** —— 逻辑错误（`AssertionError` 等）照旧抛出去。
    # 许可:   本仓库 MIT。无第三方代码引入。
    # 覆盖:   后续同级定义
    # ────────────────────────────────────────────────────────────────────
    """
    try:
        return spec.derived_args(params)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        # 只认「碰 COM / 选择」这一类；**别的异常必须照旧炸出来**
        com_markers = ("没有活动文档", "活动文档", "__current_selection__",
                       "EDGE", "选择", "select", "COM", "Dispatch")
        if type(exc).__name__ == "EntitySelectionError" or any(m in msg for m in com_markers):
            pytest.skip(
                "spec %s 的 `derived_args` **碰了活 COM**（%s: %s）—— "
                "本文件的契约是「不连 SolidWorks」，故这一条**静态跑不了**；"
                "要覆盖它得在真机上跑，见 `D:\\AI\\SW\\probe_*`。"
                % (spec.name, type(exc).__name__, msg[:90])
            )
        raise


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
    return _load("tool_registry_b4", MCP_DIR / "tool_registry.py")


@pytest.fixture(scope="module")
def batch(registry):
    return _load("tool_specs_batch4", MCP_DIR / "tool_specs_batch4.py").SPECS_BATCH4


# ── ① 门禁与形状 ────────────────────────────────────────────────────
def test_batch_passes_its_own_gates(registry, batch):
    assert registry.check_specs(batch) == []


def test_all_declarative(batch):
    assert [s.name for s in batch if s.extra_op is not None] == []
    for s in batch:
        assert s.module and s.function, "%s 缺少 module/function" % s.name
        assert s.doc.strip()


def test_uses_selection_not_bare_coordinates(batch):
    """⭐ 规则 3：本批**必须**用声明式 `selection`，**不得**出现裸坐标入参。"""
    banned = {"x", "y", "z", "point", "normal", "axis", "origin"}
    for s in batch:
        names = {p.name for p in s.params}
        assert not (names & banned), "%s 出现了裸坐标 %r" % (s.name, sorted(names & banned))
        assert "selection" in names or {"path_selection", "profile_selection"} <= names, (
            "%s 没有声明式选择入参" % s.name
        )


# ── ② `pre_call`（选择副作用）必须配齐 ────────────────────────────
def test_c2_functions_declare_pre_call(batch):
    """实现里明写「调用前必须先选好」的，**必须**有 `pre_call`。

    ⚠ 这三条的实现分别是：
      `create_edge_flange` 文档串「调用前必须先用 _select_by_id 把目标边选入选区」
      `create_gusset`      来源块「支撑面须由调用方先用 SelectByID2 选好」
      `create_draft`       文档串「在已选中的面上创建」
    """
    c2 = {"solidworks_sheet_metal_create_edge_flange",
          "solidworks_sheet_metal_create_gusset",
          "solidworks_sheet_metal_create_draft"}
    for s in batch:
        if s.name in c2:
            assert s.pre_call is not None, "%s 缺 pre_call ⇒ 调用时没有选区" % s.name


def test_pre_call_runs_before_the_target(registry, batch, monkeypatch):
    """端到端（假宿主）：`pre_call` 必须在目标函数**之前**被调用。

    ⚠ 第一版直接写 `sys.modules[...] = fake` ⇒ **假模块泄漏到后面的用例**
    （它们要 import 真的 dataclass）⇒ 5 个用例连带失败。
    **⇒ 必须用 `monkeypatch.setitem`，测完自动还原。**
    """
    order: list[str] = []

    def fake_target(model, spec=None):
        order.append("target")
        return {"ok": True}

    # ⚠ 假模块**也要带上真的 dataclass** —— `derived_args` 会 `from ... import EdgeFlangeSpec`。
    #   第一版只塞了函数 ⇒ `ImportError: cannot import name 'EdgeFlangeSpec'`。
    from scripts.sw_sheet_metal import EdgeFlangeSpec as _RealSpec

    fake_mod = type(sys)("scripts.sw_sheet_metal")
    fake_mod.create_edge_flange = fake_target
    fake_mod.EdgeFlangeSpec = _RealSpec
    monkeypatch.setitem(sys.modules, "scripts.sw_sheet_metal", fake_mod)

    spec = next(s for s in batch if s.name.endswith("create_edge_flange"))
    original = spec.pre_call
    spec.pre_call = lambda p: order.append("pre")
    try:
        model_cls = registry.build_input_model(spec, _Base, _RF)
        fn = registry.make_tool_function(
            spec, model_cls,
            lambda op, rf, load_automation=True: op(),
            resolvers={"model": lambda _p: object()},
        )
        fn(_FakeParams(spec))
    finally:
        spec.pre_call = original
    assert order == ["pre", "target"], "顺序错：%r（pre_call 必须在目标函数之前）" % order


# ── ②b ★ 每个声明参数不能是「无主」的（否则真机会 TypeError）─────
def test_every_declared_param_is_either_passed_or_consumed(batch):
    """声明的参数只有两种合法归宿，**没有第三种**：
    ① 同名/别名**传给目标函数**；
    ② `param_alias[name] = None` **被显式消费**（如 `pre_call` 用的 `selection`）。

    ⚠ 这条是本批**实际抓到的 bug** 的守卫：`selection` 只声明、既不传也不消费
    ⇒ 注册器把它当 kwarg 传进 `create_edge_flange(model, spec)` ⇒ **TypeError**。
    """
    sys.path.insert(0, str(REPO_ROOT))
    injected = {"model", "sw_app", "study"}
    for s in batch:
        mod = __import__("scripts.%s" % s.module, fromlist=[s.function])
        real = {p.name for p in inspect.signature(getattr(mod, s.function)).parameters.values()}
        real -= injected
        real -= {"spec"}          # 由 derived_args 提供
        # ③ 由 `derived_args` 消费的 **spec 字段**（名字是 spec 字段 + 单位后缀）
        spec_fields: set[str] = set()
        if s.derived_args is not None:
            try:
                obj = s.derived_args(_FakeParams(s))["spec"]
                spec_fields = {f.name for f in dataclasses.fields(obj)}
            except Exception:  # noqa: BLE001
                spec_fields = set()
        for p in s.params:
            if p.name in s.param_alias:
                continue              # ① 显式映射（含 None = 被消费）
            base = p.name
            for suf in ("_mm", "_deg"):
                if base.endswith(suf):
                    base = base[: -len(suf)]
            if base in spec_fields:
                continue              # ② 由 derived_args 装进 spec
            assert p.name in real, (
                "工具 %s 的入参 %r **既没映射到真形参、也没被显式消费** —— "
                "真机会 `TypeError: unexpected keyword argument`。"
                "（若它由 pre_call 消费，请写 param_alias={%r: None}）"
                % (s.name, p.name, p.name)
            )


# ── ③ ref 参数按实现真实用法处理 ──────────────────────────────────
def test_omitted_face_ref_is_real_and_unused(batch):
    """`create_draft` 的 `face_ref`：**真是形参**，且在实现里**真的没被用到**。

    ⚠ 这条断言同时防止两类错：
      ① 省略一个不存在的参数（无效声明）；
      ② 把一个**实际有用**的参数误判为无用 —— 所以我们**读源码核实**。
    """
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sw_sheet_metal as SM

    spec = next(s for s in batch if s.name.endswith("create_draft"))
    assert "face_ref" in spec.omitted_params, "create_draft 应显式省略 face_ref"

    fn = SM.create_draft
    real = {p.name for p in inspect.signature(fn).parameters.values()}
    assert "face_ref" in real, "face_ref 不是真形参 ⇒ 无效的省略声明"

    src = inspect.getsource(fn)
    body = src.split("def ", 1)[1]
    # 函数**体**里不得出现 `face_ref`（签名那行除外）
    body_lines = [ln for ln in body.splitlines()[1:]]
    uses = [ln.strip() for ln in body_lines if "face_ref" in ln]
    assert uses == [], "face_ref 在函数体里被用到了 %r ⇒ 不该省略它" % uses


def test_swept_refs_are_not_omitted(batch):
    """`create_swept_flange` 的两个 ref 在实现里**真被用了** ⇒ **不得**省略。"""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sw_sheet_metal as SM

    spec = next(s for s in batch if s.name.endswith("create_swept_flange"))
    assert spec.omitted_params == (), "swept 的两个 ref 被真用了，不该省略"
    src = inspect.getsource(SM.create_swept_flange)
    assert "data.Path = path_ref" in src or "path_ref" in src
    assert "data.Profile = profile_ref" in src or "profile_ref" in src


# ── ④ spec 字段覆盖 + 单位换算（沿用 batch3 的纪律）───────────────
def test_every_spec_field_reachable_or_defaulted(batch):
    """spec 的每个字段要么有入参、要么有默认值（否则用户构造不出合法 spec）。"""
    sys.path.insert(0, str(REPO_ROOT))
    for s in batch:
        if s.derived_args is None:
            continue
        obj = _derived_args_or_skip(s, _FakeParams(s))["spec"]
        declared = {p.name for p in s.params}
        for f in dataclasses.fields(obj):
            base = f.name
            cands = {base, base + "_mm", base + "_deg", base + "_selection"}
            if cands & declared:
                continue
            assert f.default is not dataclasses.MISSING, (
                "工具 %s：spec 字段 %r 既没入参也没默认值" % (s.name, f.name)
            )


def test_lengths_convert_mm_to_metres(batch):
    """长度 mm→m（本会话已在 `CreateMesh` 上踩过毫米当米）；角度**不**换算。"""
    sys.path.insert(0, str(REPO_ROOT))
    for s in batch:
        if s.derived_args is None:
            continue
        p = _FakeParams(s)
        d = _derived_args_or_skip(s, p)
        obj = d["spec"]
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if val is None:
                continue
            # 长度类字段：入参 mm ⇒ 装出来是 m
            if f.name in ("bend_radius", "flange_length", "thickness", "depth",
                          "profile_distance_1", "profile_distance_2",
                          "start_offset", "end_offset"):
                arg = getattr(p, f.name + "_mm", None)
                if arg is None:
                    continue
                assert abs(val * 1000.0 - float(arg)) < 1e-9, (
                    "工具 %s 字段 %r：入参 %r mm ⇒ 装出 %r m（应 %r）"
                    % (s.name, f.name, arg, val, float(arg) / 1000.0)
                )
            # 角度字段：**不**换算
            if f.name in ("angle", "profile_angle"):
                src_name = f.name + "_deg"
                arg = getattr(p, src_name, None)
                if arg is None:
                    continue
                assert abs(val - float(arg)) < 1e-9, (
                    "工具 %s 的角度字段 %r 被错误换算：%r ≠ %r" % (s.name, f.name, val, arg)
                )


class _FakeParams:
    """`derived_args` / `pre_call` 用的替身：长度给 2.5、角度给 90。"""

    def __init__(self, spec):
        for p in spec.params:
            if p.name.endswith("_mm"):
                setattr(self, p.name, 2.5)
            elif p.name.endswith("_deg"):
                setattr(self, p.name, 90.0)
            elif p.name.endswith("_selection"):
                setattr(self, p.name, "__current_selection__")
            elif p.name == "selection":
                setattr(self, p.name, "__current_selection__")
            elif p.name == "flange_position":
                setattr(self, p.name, 1)
            elif isinstance(p.default, bool):
                setattr(self, p.name, p.default)
            elif p.default not in (..., None):
                setattr(self, p.name, p.default)
            else:
                setattr(self, p.name, None)
        self.response_format = _RF.JSON
