"""★ 阶段 1 契约测试：统一目录 + 名字解析 + 参数绑定（规格 316 的 C1/C3/C4）。

★★ 含**反向验证**（★ 规格 §5 的 M1 / M2）：
   M1 把规范名改回**裸名** ⇒ 定点测试必须失败
   M2 把深度绑定 **×1000** ⇒ 定点测试必须失败
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage1_registry.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C1/C3/C4 契约测试
# 官方依据: ① 规范名真源 `register_capabilities.all_specs()`（476 个）
#           ② `mcp-server/server.py` 的 `@mcp.tool(name=..., annotations=...)`（45 个）
#           ③ 本仓**事实 53**（启发式 ≥3 次修补即回退 ⇒ 名字解析只用确定性规则）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import registry as R                          # noqa: E402


@pytest.fixture(scope="module")
def reg():
    return R.build_registry()


#: ══ C1 统一目录 ═══════════════════════════════════════════════════════

def test_registry_covers_both_sources(reg) -> None:
    """★ SC-010：**两种注册来源均进入清单**（不漏 45 个上游入口）。"""
    a = [d for d in reg.values() if d.source == "all_specs"]
    b = [d for d in reg.values() if d.source == "server_py"]
    assert len(a) == 476, "all_specs 来源应 476 个，实得 %d" % len(a)
    assert len(b) == 45, "server_py 来源应 45 个，实得 %d" % len(b)


def test_registry_not_empty(reg) -> None:
    """★ 目录不许为空（★ 防「静默通过」）。"""
    assert len(reg) == 521


def test_admitted_implies_implementation_address(reg) -> None:
    """★ 不变式 I3/I4：准入 ⇒ 有裸步名 + 有实现地址。"""
    bad = [d.canonical_name for d in reg.values()
           if d.admitted and not (d.step_name and d.module and d.function)]
    assert bad == [], bad


def test_not_admitted_has_reason(reg) -> None:
    """★ 不变式 I2：未准入 ⇒ **理由非空**（★ 不许空）。"""
    bad = [d.canonical_name for d in reg.values()
           if not d.admitted and not d.reject_reason.strip()]
    assert bad == [], bad


def test_unknown_effect_never_admitted(reg) -> None:
    """★ 不变式 I5：**效应未知 ⇒ 不得准入**（★ 未知副作用不自动执行）。"""
    bad = [d.canonical_name for d in reg.values()
           if d.effect == "unknown" and d.admitted]
    assert bad == [], bad


#: ══ C3 名字解析 ═══════════════════════════════════════════════════════

def test_resolve_all_method_steps(reg) -> None:
    """★ SC-003：**方法库的每一步都解析为唯一规范工具**（★ 子方法除外）。"""
    from scripts.engineering import compiler as C
    bad = []
    for mid, m in C.METHOD_LIBRARY.items():
        for s in m.steps:
            try:
                R.resolve_step_name(s, reg)
            except R.RegistryError as e:
                #: ★ `hole_group` 是**另一个方法 id** ⇒ 属阶段 2 的子方法展开，不算错
                if e.code != "sub-method-not-expanded":
                    bad.append((mid, s, e.code))
    assert bad == [], "未解析的步骤：%s" % bad


def test_resolve_is_deterministic(reg) -> None:
    """★ 解析规则只有一条（去前缀）⇒ 同一输入恒同一输出。"""
    for s in ("sketch_start", "extrude_boss", "chamfer"):
        a = R.resolve_step_name(s, reg)
        b = R.resolve_step_name(s, reg)
        assert a == b == "solidworks_" + s


def test_resolve_unknown_raises(reg) -> None:
    """★ FR-002：解析不到 ⇒ **显式抛**（★ 不静默、不猜）。"""
    with pytest.raises(R.RegistryError) as ei:
        R.resolve_step_name("绝不存在的步名", reg)
    assert ei.value.code == "unresolved-step-name"


def test_resolve_bare_canonical_name_raises(reg) -> None:
    """★ 传**规范全名**也解析不到（★ 步名就是裸名 —— ★ 防两类名字混用）。"""
    with pytest.raises(R.RegistryError) as ei:
        R.resolve_step_name("solidworks_sketch_add_circle", reg)
    assert ei.value.code == "unresolved-step-name"


def test_sub_method_gets_its_own_code(reg) -> None:
    """★ `hole_group` 是方法 id ⇒ 专属码（★ 免得后人按错字排查）。"""
    with pytest.raises(R.RegistryError) as ei:
        R.resolve_step_name("hole_group", reg)
    assert ei.value.code == "sub-method-not-expanded"


#: ══ C4 参数绑定 ═══════════════════════════════════════════════════════

def test_bind_rejects_unknown_param(reg) -> None:
    """★ FR：参数不在声明形参里 ⇒ `unknown-param`（★ 多一个就拒绝）。"""
    st = R.PlanStep(step="extrude_boss", params={"sketch_name": "草图1",
                                                 "depth_mm": 20.0,
                                                 "绝不存在的参数": 1},
                    tool="solidworks_extrude_boss")
    with pytest.raises(R.RegistryError) as ei:
        R.bind_params(st, reg)
    assert ei.value.code == "unknown-param"


def test_bind_rejects_missing_required(reg) -> None:
    """★ FR：缺必填形参 ⇒ `missing-required-param`。"""
    st = R.PlanStep(step="extrude_boss", params={"depth_mm": 20.0},
                    tool="solidworks_extrude_boss")
    with pytest.raises(R.RegistryError) as ei:
        R.bind_params(st, reg)
    assert ei.value.code == "missing-required-param"


def test_bind_accepts_valid(reg) -> None:
    """★ 正例：形参齐 ⇒ 通过。"""
    st = R.PlanStep(step="extrude_boss",
                    params={"sketch_name": "草图1", "depth_mm": 20.0},
                    tool="solidworks_extrude_boss")
    assert R.bind_params(st, reg) == {"sketch_name": "草图1", "depth_mm": 20.0}


def test_bind_requires_resolved_tool(reg) -> None:
    """★ 不变式 I6：`tool` 为空 ⇒ 拒绝（★ 必须先 `resolve_plan`）。"""
    with pytest.raises(R.RegistryError) as ei:
        R.bind_params(R.PlanStep(step="extrude_boss", params={}), reg)
    assert ei.value.code == "unresolved-step-name"


#: ══ 反向验证 M1：把规范名改回裸名 ⇒ 必须失败 ═══════════════════════

def test_m1_bare_name_must_fail(reg) -> None:
    """★★ **M1**：把计划里的 `tool` 改回**裸名** ⇒ 授权/绑定必须失败。

    ★ 做法：构造一个 `tool` 为裸名的 `PlanStep` ⇒ `bind_params` 必须抛
      （★ 因为目录里没有那个键）。
    """
    bad = R.PlanStep(step="extrude_boss", params={"sketch_name": "s", "depth_mm": 1.0},
                     tool="extrude_boss")            #: ★ 裸名，不是规范名
    with pytest.raises(R.RegistryError):
        R.bind_params(bad, reg)


#: ══ 反向验证 M2：深度 ×1000 ⇒ 单位门禁必须抓 ═══════════════════════

def test_m2_depth_times_1000_is_detectable() -> None:
    """★★ **M2**：把 `extrude_boss` 的深度绑定 **×1000** ⇒ 单位门禁必须报错。

    ★ 判据：`scripts/check_unit_conversion_count.py` 的 `_spec_conv` 检查
      `derived_args` 里有没有换算。×1000 会让**换算次数变 2**（工具层原本一次）。
    ★ 本测试用**真源**判：`solidworks_extrude_boss` 的 `derived_args` 现在**恰好一次**。
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "unit_gate", ROOT / "scripts" / "check_unit_conversion_count.py")
    ug = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ug)

    import register_capabilities as rc
    by = {s.name: s for s in rc.all_specs()}
    s = by["solidworks_extrude_boss"]
    #: ★ 工具层**有**换算（`_m_of_mm`）
    assert ug._spec_conv(s) is True, "★ extrude_boss 的工具层应当有换算"
    #: ★ 内部函数**没有**换算（★ 那是设计 —— 换算只在工具层做一次）
    assert ug._mod_conv_closure("sw_part", "extrude_boss") is False
    #: ⇒ 合计**恰好一次**（★ 0 次 = 放大 1000 倍；2 次 = 缩小 1000 倍）
    rows, _ = ug.audit()
    hit = [r for r in rows if r["tool"] == "solidworks_extrude_boss"]
    assert hit and hit[0]["conversions"] == 1, hit
