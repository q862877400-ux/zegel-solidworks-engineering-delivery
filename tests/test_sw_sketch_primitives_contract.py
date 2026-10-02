"""★ 段 2 草图图元的契约：5 条声明齐 + 「非空名字不许静默回退」的锁。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_sketch_primitives_contract.py
# 定位:   ★ 2026-10-03（轮 398）24h 计划 v2 段 2 的契约测试。被锁的契约：
#   ① `mcp-server/tool_specs_batch54.py` 的 5 条声明**参数与函数形参对得上**
#      （★ 靠 `param_alias` —— 装配时每个声明的 Param 都会按别名传进去，★ 对不上就 `TypeError`）；
#   ② ★★ **`sw_sketch.resolve_sketch` 对非空但找不到的名字必须抛错** ——
#      ★ 先前它会**静默回退**到「特征树里最后一个草图」⇒ 调用方会在**另一个草图**上读/写；
#      ★ 而该函数的批头明写「选不中要报错，不静默」。
# 官方依据: `C:\swapi\types\ISketchManager\` 的 `CreateArc` / `CreateEllipse` / `CreatePolygon` /
#   `CreateSketchSlot` / `CreateCenterLine`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp-server"))

import sw_sketch as SK                                              # noqa: E402
import sw_part as P                                                # noqa: E402

#: ★ 工具名 ⇒ 目标函数名（★ 与 batch54 的声明一致）
EXPECTED = {
    "solidworks_sketch_add_arc": "sketch_arc",
    "solidworks_sketch_add_ellipse": "sketch_ellipse",
    "solidworks_sketch_add_polygon": "sketch_polygon",
    "solidworks_sketch_add_slot": "sketch_slot",
    "solidworks_sketch_add_centerline": "sketch_centerline",
}


def _specs():
    import tool_specs_batch54 as B                                  # noqa: PLC0415
    return {s.name: s for s in B.SPECS_BATCH54}


def test_all_five_specs_declared() -> None:
    """★ 5 条声明必须齐（★ 少一条就是一个没挂上的能力）。"""
    got = _specs()
    assert set(got) == set(EXPECTED)


@pytest.mark.parametrize("tool_name,fn_name", sorted(EXPECTED.items()))
def test_spec_alias_targets_real_parameters(tool_name: str, fn_name: str) -> None:
    """★★ 契约核心：★ `param_alias` 指的形参必须**真的存在于目标函数**上 ——
    ★ 否则装配时会把不存在的关键字传进去（`TypeError`），★ 而那是**运行期**才炸。"""
    spec = _specs()[tool_name]
    fn = getattr(P, fn_name)
    real = set(inspect.signature(fn).parameters)
    assert spec.function == fn_name
    assert spec.module == "sw_part"
    assert spec.inject == "model", "★ 这些图元要文档对象（★ 工具层 inject）"
    for tool_param, target in spec.param_alias.items():
        assert target in real, "%s 的别名 %s→%s 指向了不存在的形参" % (
            tool_name, tool_param, target)
    #: ★ 每个声明的 Param 都要么有别名、要么与形参同名（★ 装配逻辑就是这么做的）
    declared = {p.name for p in spec.params}
    assert declared <= set(spec.param_alias) | real, "声明的参数应有别名或与形参同名"


@pytest.mark.parametrize("fn_name", ["sketch_arc", "sketch_ellipse", "sketch_polygon",
                                     "sketch_slot", "sketch_centerline"])
def test_length_parameters_are_mm_named(fn_name: str) -> None:
    """★ 规则 2：★ 长度类对外参数名必须带 `_mm`（★ 别名映射到内部的短名）。"""
    spec = _specs()[next(n for n, f in EXPECTED.items() if f == fn_name)]
    lengths = [p for p in spec.params if p.name.endswith("_mm")]
    assert lengths, "长度参数必须带 _mm 后缀（规则 2）"


def test_resolve_sketch_rejects_non_empty_unknown_name() -> None:
    """★★ **缺陷锁**（轮 398 真机发现）：★ `resolve_sketch(model, "<不存在的名字>")`
    **必须抛错**，★ 不许回退到「特征树里最后一个草图」——
    ★ 先前那样做会让调用方在**另一个草图**上读 / 写，★ 而批头写着「选不中要报错，不静默」。
    ⚠ 本测试**不碰 COM**：★ 用 `model=None` 之外的路径走不到 —— 所以改成**读源码**断言守卫存在
    （★ 与"静态锁"同一手法；★ 真机行为由 `tools/prove_sketch_primitives.py` 的负例覆盖）。"""
    src = inspect.getsource(SK.resolve_sketch)
    assert "str(name or \"\").strip()" in src or "str(name or '').strip()" in src
    assert "raise RuntimeError" in src
    #: ★ 守卫必须在"特征树兜底"**之前**
    guard_at = src.find("非空名字不许回退")
    fallback_at = src.find("GetFeatureCount")
    assert guard_at != -1, "必须有那条守卫"
    assert fallback_at != -1
    assert guard_at < fallback_at, "★ 守卫必须在特征树兜底**之前**（否则拦不住）"


def test_spline_is_documented_as_not_doing() -> None:
    """★ 计划 §四：★ `sketch_spline` **不做**（事实 47/68 架构限制）——
    ★ 断言它的文档串**仍如实写着**建不出来（★ 免得将来有人当它是好的）。"""
    doc = inspect.getdoc(P.sketch_spline) or ""
    assert "建不出来" in doc, "spline 的文档串必须保留真机结论"
    #: ★ 而它**不许**出现在 batch54 的声明里（★ 不做就是不做）
    assert "sketch_spline" not in {s.function for s in _specs().values()}
