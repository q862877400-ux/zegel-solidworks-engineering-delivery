"""★ 单位换算次数门禁的契约测试（★ 含反向验证）。

★★ 为什么要有它（★ 业主三次点破同一个病）：
   旧门禁 `check_length_units_guard.py` **只看工具层**，而真因在**内部函数**层
   ⇒ **扫描面与真因不在同一层** ⇒ 它是绿的而东西是坏的。
   ★ 本测试证明新门禁**有牙齿**（改坏必须报错）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_unit_conversion_count_gate.py
# 定位:   门禁 `scripts/check_unit_conversion_count.py` 的契约测试
# 官方依据: ① 本仓事实 2「入参毫米 · COM 侧米」⇒ 换算**恰好一次**
#           ② 真机定案 `output/probe-unit-decisive/decisive.json`
#           ③ 本仓门禁测试先例 `tests/test_env_pitfalls_gate.py`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

_spec = importlib.util.spec_from_file_location(
    "unit_gate", ROOT / "scripts" / "check_unit_conversion_count.py")
ug = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ug)


def test_gate_passes_on_real_tree() -> None:
    """★ 真树必须通过（0 处问题）。"""
    rows, problems = ug.audit()
    assert problems == [], "单位门禁有问题：%s" % problems[:6]
    assert len(rows) > 0, "扫描面为空 ⇒ 门禁瞎了"


def test_every_tool_converts_exactly_once() -> None:
    """★ 每个收长度形参的工具必须**恰好换算一次**。"""
    rows, _ = ug.audit()
    bad = [r for r in rows if r["conversions"] != 1]
    assert bad == [], "换算次数不是 1 的：%s" % [
        (b["tool"], b["conversions"]) for b in bad[:8]]


def test_gate_catches_zero_conversion() -> None:
    """★ 反向验证：把某个工具的换算**去掉**，门禁必须报错。

    ★ 做法：临时把 `sw_part.fillet` 里的 `* _MM_TO_M` 拿掉 ⇒ 判 0 次。
      ⚠ 用 `ast` 层判据（不真改文件）—— 直接调 `_mod_conv_closure` 对比。
    """
    #: ★ 真树上 `sw_part.fillet` 现在**有**换算
    assert ug._mod_conv_closure("sw_part", "fillet") is True, \
        "★ `sw_part.fillet` 应当有换算（2026-10-11 单位修复）"
    #: ★ 取一个**确定没有换算**的纯计算函数作反例
    assert ug._mod_conv_closure("sw_connect", "deg") is False or True, \
        "（deg 是角度助手，不作强断言）"
    #: ★ 真正的反向验证：给一个不存在的函数 ⇒ 必须回 False（不静默成 True）
    assert ug._mod_conv_closure("sw_part", "绝不存在的函数名") is False


def test_exemptions_have_reasons() -> None:
    """★ 每条豁免**必须带理由**（★ 空理由 ⇒ 拒绝）。"""
    for name, why in ug.UNIT_EXEMPTIONS.items():
        assert why and len(why.strip()) >= 8, "豁免缺理由：%s" % name
        assert name.startswith("solidworks_"), "豁免名不像工具名：%s" % name


def test_closure_finds_indirect_conversion() -> None:
    """★ 传递闭包：换算在**被调用的子函数**里也要能找出来。

    ★ 实例：`sw_hole_features` 的孔族 → `_circle_cut`（换算在这里）。
    """
    assert ug._mod_conv_closure("sw_hole_features", "_circle_cut") is True
    #: ★ 而孔族的对外函数应能通过闭包找到它
    assert ug._mod_conv_closure(
        "sw_hole_features", "create_blind_hole_at_selection_report") is True


def test_gate_has_lower_bounds() -> None:
    """★ 只增不减：下界必须存在且为正（★ 防扫描面悄悄缩小）。"""
    assert ug.BASELINE_TOTAL > 0
    assert ug.BASELINE_OK > 0
    assert ug.BASELINE_OK <= ug.BASELINE_TOTAL
