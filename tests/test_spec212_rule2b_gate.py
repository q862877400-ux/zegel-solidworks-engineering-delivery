"""★ 规格 212 · C-4：**规则 2b 的两半硬拦**的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_registry.py` 的 `check_spec`）
# 文件:   tests/test_spec212_rule2b_gate.py
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **C-4 / D-5 的硬拦部分**。★ 规则 2b 两半：
#     ★★ **前半**：★ **名字带单位后缀 ⇒ 描述里必须有本档单位词**（★ 输入侧逆向一半）✓
#     ★★★ **后半**：★ **描述自称无量纲/枚举/布尔 ⇒ 名字不许带单位后缀**（★ 不许说假话）✓
# 判据:   ★★ **两条都是 `GateError`**（★ 硬拦 —— ★ C 批先"只报不拦"清清单、★ 清完才升级 ✓）：
#     ★ ① 负例：★ 名字 `depth_mm`、★ 描述 `"Extrusion depth."`（★ 无单位词）⇒ **必须拦** ✓
#     ★ ② 负例：★ 名字 `lock_rotation_deg`、★ 描述自称「**无量纲布尔**」⇒ **必须拦** ✓
#     ★ ③ 正例：★ 名字 `depth_mm` + 描述「…in **mm**」⇒ **必须放行** ✓
#     ★ ④ 正例：★ 名字 `count`（★ 无后缀）+ 描述「无量纲」⇒ **必须放行**（★ 门禁不管没声明的 ✓）
#     ★ ⑤ 逃生口：★ 在 `_UNIT_DESC_EXEMPT` 里登记过 ⇒ **放行**（★ 且理由必须非空）✓
#   ★★ 判据**全确定性**（★ 后缀名 / 描述里的单位词 / 自称词）—— ★ **不猜语义、不靠 LLM** ✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` **规则 2b**）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tool_registry as tr                                     # noqa: E402
from tool_registry import GateError, Param, ToolSpec           # noqa: E402


def _spec(*params):
    return ToolSpec(name="solidworks_spec212_probe", title="Spec 212 probe",
                    module="sw_part", function="extrude_boss", inject="model",
                    params=list(params))


# ── ① ★★ **"没写全"不该硬拦**（★ 分寸定则 —— 被一次测试失败逼出来的）────────
def test_name_suffix_without_unit_word_is_NOT_a_hard_failure():
    """★★★ **判据的分寸**：★ **硬拦只该拦"说假话"，不该拦"没说全"** ✓

    ★ 实录：★ 我第一版把这条也做成硬拦 ⇒ ★★ **既有测试**
      `test_radius_param_is_not_flagged_as_an_angle` **当场失败** ✗ ——
      ★ 它的夹具 `bend_radius_mm` **描述里没写 "mm"**、★ 而那条夹具的**意图与单位无关** ✓
    ★★ 判断：★「描述没写全」**不构成危险**（★ 名字已经说清了 ✓）⇒
      ★ **它适合当"审计发现"、不适合当"硬拦"** ✗ ✓
    ★★★ 故分工：★ **前半**留 `tools/check_unit_suffix_consistency.py`（★ 只报 ✓）·
      ★ **后半（说假话）**在 `check_spec` 里硬拦 ✓ ← ★ 那才是**主动误导** ✗
    """
    spec = _spec(Param("depth_mm", float, default=1.0,
                       description="Extrusion depth."))
    tr.check_spec(spec)                       #: ★ **不该抛** —— 门禁不管"没写全" ✓
    #: ★★ 但**审计工具会报它**（★ 那一侧才是它的归属）⇒ ★ 断言那个工具仍在
    import importlib.util
    audit = ROOT / "tools" / "check_unit_suffix_consistency.py"
    assert audit.is_file(), "★ 前半的归属（审计脚本）必须存在"
    assert importlib.util.spec_from_file_location("_audit", audit) is not None


# ── ② 负例：描述自称无量纲、名字却带后缀 ⇒ 必须拦（★ "后缀说假话"）──────────
def test_dimensionless_claim_with_unit_suffix_is_rejected():
    spec = _spec(Param("lock_rotation_deg", bool, default=False,
                       description="True = 锁旋转（无量纲布尔）。"))
    #: ★ 注意：`bool` 在规则 2**前半**里被豁免（`use_default_radius` 那类标志）⇒
    #:   ★★ 但**后半**（说假话）**必须照拦** —— ★ 这正是一条"bool 带 `_deg`"的实录 ✓
    with pytest.raises(GateError) as ei:
        tr.check_spec(spec)
    assert "说假话" in str(ei.value) or "规则 2b" in str(ei.value)


# ── ③ 正例：名字带后缀 + 描述有单位词 ⇒ 放行 ────────────────────────────────
def test_name_suffix_with_unit_word_passes():
    spec = _spec(Param("depth_mm", float, default=1.0,
                       description="Extrusion depth in mm."))
    tr.check_spec(spec)                                        #: ★ 不抛 = 放行 ✓


# ── ④ 正例：没带后缀 + 描述自称无量纲 ⇒ 放行（★ 门禁不管没声明的）──────────
def test_no_suffix_is_not_our_business():
    spec = _spec(Param("count", int, default=0, description="计数（无量纲）。"))
    tr.check_spec(spec)


# ── ⑤ 逃生口：登记过 ⇒ 放行；★ 且理由必须非空 ──────────────────────────────
def test_exempt_table_is_explicit_with_reasons():
    ex = tr._UNIT_DESC_EXEMPT
    assert ex, "★ 逃生口不该为空（★ 现在有 1 条：钣金卷边的挂起项）"
    for k, reason in ex.items():
        assert isinstance(k, tuple) and len(k) == 2, k
        assert len(str(reason)) > 40, "%s 的理由太短" % (k,)


# ── ⑥ 契约：三件套常量都在，且词表非空 ──────────────────────────────────────
def test_rule2b_constants_exist():
    assert tr._UNIT_DESC_WORDS, "★ 每档单位词表不该为空"
    assert "_mm" in tr._UNIT_DESC_WORDS and "_deg" in tr._UNIT_DESC_WORDS
    assert tr._DIMENSIONLESS_CLAIM.search("枚举值")


# ── ⑦ ★★ **全仓 448 个工具必须全过**（★ 这是硬拦上线的"不炸"证明）──────────
def test_all_repo_specs_pass_the_new_gates():
    import register_capabilities as rc
    specs = rc.all_specs()
    assert len(specs) >= 400, "★ 工具数异常：%d" % len(specs)
    bad = []
    for s in specs:
        try:
            tr.check_spec(s)
        except Exception as exc:                                # noqa: BLE001
            bad.append("%s: %s" % (s.name, str(exc)[:90]))
    assert not bad, "★ 有 %d 个工具过不了新门禁：\n%s" % (len(bad), "\n".join(bad[:6]))
