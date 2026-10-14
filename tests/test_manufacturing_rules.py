"""★ 契约测试：把仓库里**早就有的**制造规则接进工具层。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_manufacturing_rules.py
# 定位:   `scripts/engineering/manufacturing_rules.py` 的契约测试。
#           ★★★ 触发它的是 2026-10-14 业主：「继续搜索你本项目内部已经有的东西，
#             说不定**还有很多我早就提供给你了**，你只是**文件太多给忘了**。」
#           ★ 实测：`manufacturing_rules.yaml`（★ 螺纹底孔 + 间隙孔 + 特征顺序）
#             **只被一个测试引用**，★ **工具层完全没用**。
# 官方依据: ① `subskills/solidworks-vibecad/knowledge/manufacturing_rules.yaml`
#           ② `subskills/solidworks-fillet-chamfer-cnc/references/
#              cnc-fillet-chamfer-lessons.md`
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

from scripts.engineering import manufacturing_rules as M                 # noqa: E402


#: ══ ★★ 主判据：**规则来自仓库内既有文件**（★ 不是新写的）════════════

def test_rules_come_from_an_existing_file() -> None:
    """★★★ 判据：**规则文件在仓库里**（★ 证明「早就有了」）。"""
    assert M.RULES_FILE.is_file(), (
        "★★ 规则文件不见了 —— ★ 而本模块的**全部意义**就是"
        "「用它，不要重写」")
    assert "subskills" in str(M.RULES_FILE)


def test_rules_file_is_the_single_source() -> None:
    """★★ 判据：**只读那一份**（★ 不在代码里复制一份数值）。"""
    import inspect                                                      # noqa: PLC0415
    src = inspect.getsource(M)
    #: ★ 底孔数值**不得**硬编码在代码里（★ 必须从表查）
    assert "6.8" not in src.replace('"6.8"', ""), (
        "★★ M8 底孔 6.8 被硬编码进代码 ⇒ 那不是「用表」")
    assert "tap_drill" in src, "★ 代码里没出现 `tap_drill` ⇒ 可能没在读表"


#: ══ 螺纹底孔 ════════════════════════════════════════════════════════

def test_thread_sizes_present() -> None:
    """★ 表里该有 M3~M12 七个规格。"""
    sizes = M.thread_sizes()
    for s in ("M3", "M4", "M5", "M6", "M8", "M10", "M12"):
        assert s in sizes, "★ 表里缺 %s" % s


def test_m8_tap_drill() -> None:
    """★★ **M8 底孔 = 6.8mm**（★ 这是表里的值 —— ★ 不凭记忆）。"""
    spec = M.thread_spec("M8")
    assert spec["pitch"] == 1.25
    assert spec["tap_drill"] == 6.8
    assert spec["default_mouth_chamfer"] == 0.8


def test_unknown_thread_size_raises() -> None:
    """★ 表里没有的规格 ⇒ **响亮报错**（★ 不猜一个值）。"""
    with pytest.raises(M.RuleError) as ei:
        M.thread_spec("M99")
    assert ei.value.code == "not-in-table"


#: ══ 间隙孔 ══════════════════════════════════════════════════════════

def test_clearance_holes_are_bigger_than_nominal() -> None:
    """★★ **间隙孔 > 公称直径**（★ M6 通孔是 6.6，★ 不是 6.0）。

    ★ 判据：★ 这是**通孔让螺栓穿过**用的 —— ★ 打 6.0 就穿不过去。
    """
    for s, nominal in (("M3", 3), ("M4", 4), ("M5", 5), ("M6", 6), ("M8", 8)):
        assert M.clearance_hole(s) > nominal, (
            "★★ %s 的间隙孔 %.1f 不大于公称 %d" % (s, M.clearance_hole(s), nominal))


def test_m6_clearance_is_6_6() -> None:
    """★ M6 间隙孔 = **6.6mm**。"""
    assert M.clearance_hole("M6") == 6.6


#: ══ ★★ 特征顺序（★ 大圆角在孔槽之前）════════════════════════════════

def test_feature_order_has_13_steps() -> None:
    """★ 既有表里的特征顺序是 **13 步**。"""
    seq = M.feature_order()
    assert len(seq) == 13, "★ 步数变了：%d" % len(seq)


def test_fillet_comes_before_holes() -> None:
    """★★★ **大圆角/外轮廓倒角在孔槽之前** —— ★ 这是既有规则的核心。

    ★★ 依据逐字（`cnc-fillet-chamfer-lessons.md`）：
      「如果步骤 3 放在**孔槽之后**，SolidWorks 可能在**复杂拓扑上求解很久**。」
    """
    r = M.fillet_before_holes()
    assert r["ok"] is True, "★★ 倒角排到了孔之后 ⇒ 复杂拓扑会求解很久"
    assert r["fillet_index"] < r["hole_index"]


def test_feature_order_starts_with_close_and_new() -> None:
    """★ 第 1 步是**关同名文档**（★ 否则保存会失败 —— `SaveAs` 错误码 1）。"""
    seq = M.feature_order()
    assert seq[0] == "close_same_name_documents"
    assert seq[1] == "new_part"


def test_unknown_order_kind_raises() -> None:
    """★ 没有的顺序类型 ⇒ 报错。"""
    with pytest.raises(M.RuleError):
        M.feature_order("nonexistent_kind")


#: ══ 槽 / 口袋 ═══════════════════════════════════════════════════════

def test_slot_min_end_radius() -> None:
    """★ 槽端部最小半径 = **1.5mm**（★ 加工下限）。"""
    assert M.slot_min_end_radius() == 1.5


def test_pocket_limits() -> None:
    """★ 口袋最小壁厚 **3.0** · 最小底厚 **2.0**。"""
    p = M.pocket_limits()
    assert p["min_wall"] == 3.0
    assert p["min_floor"] == 2.0


#: ══ ★★ 降级策略（★ 来自 lessons 文件）═══════════════════════════════

def test_degrade_ladder_is_100_75_50() -> None:
    """★★ 降级阶梯 = **100% / 75% / 50%**（★ 逐字承 lessons 文件）。"""
    assert M.DEGRADE_FACTORS == (1.0, 0.75, 0.5)
    assert M.degrade_ladder(2.0) == [2.0, 1.5, 1.0]


def test_degrade_has_a_floor() -> None:
    """★ **最小不低于 0.1mm**（★ 逐字）。"""
    assert M.DEGRADE_FLOOR_MM == 0.1
    ladder = M.degrade_ladder(0.15)
    assert all(v >= 0.1 for v in ladder), ladder


def test_strict_mode_does_not_degrade() -> None:
    """★★ **`strict` 只试请求尺寸**（★ 尺寸不可协商时用）。"""
    assert M.degrade_ladder(2.0, strict=True) == [2.0]


def test_degradation_record_has_three_fields() -> None:
    """★★★ **降级不是静默修复** —— 必须记录三个字段（★ 逐字要求）。"""
    r = M.degradation_record(requested_mm=2.0, actual_mm=1.5)
    assert r["requested_value_mm"] == 2.0
    assert r["actual_value_mm"] == 1.5
    assert r["status"] == "degraded"
    assert "实际尺寸" in r["★"]


def test_no_degradation_marks_as_requested() -> None:
    """★ 没降级 ⇒ 标 `as_requested`。"""
    r = M.degradation_record(requested_mm=2.0, actual_mm=2.0)
    assert r["status"] == "as_requested"


#: ══ 推荐半径 ════════════════════════════════════════════════════════

def test_fillet_default_ranges() -> None:
    """★ 五处推荐范围（★ 逐字承 lessons 文件）。"""
    assert M.fillet_range("base_plate_corner") == (6.0, 10.0)
    assert M.fillet_range("boss_corner") == (3.0, 6.0)
    assert M.fillet_range("outer_chamfer") == (0.8, 2.0)
    assert M.fillet_range("boss_top_chamfer") == (0.5, 1.0)
    assert M.fillet_range("hole_mouth_chamfer") == (0.3, 0.8)


def test_unknown_fillet_place_raises() -> None:
    """★ 没登记的位置 ⇒ 报错。"""
    with pytest.raises(M.RuleError):
        M.fillet_range("nope")


#: ══ 总报告 ══════════════════════════════════════════════════════════

def test_report_is_complete() -> None:
    """★ 总报告**七块都在**。"""
    r = M.rules_report()
    for k in ("source", "thread_sizes", "clearance_sizes", "feature_order_len",
              "fillet_before_holes", "slot_min_end_radius", "pocket"):
        assert k in r, "★ 缺 %s" % k


def test_harvest_doc_exists() -> None:
    """★ 盘点文档在（★ 记录「仓库里早就有」这件事）。"""
    p = (ROOT / "specs" / "315-eval-corpus"
         / "modeling-conventions-harvest.md")
    assert p.is_file()
    t = p.read_text(encoding="utf-8")
    for k in ("早就有", "键槽", "阶梯轴", "对称孔"):
        assert k in t, "★ 盘点文档缺 `%s`" % k
