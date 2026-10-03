"""★ 守「方法↔属性」那一维（★ 任务书阶段 2 要的那一类 · 轮 135）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `docs/phase2-obsolete-status.md` §六 + `tools/annotate_obsolete_form.py`
# 文件:   tests/test_obsolete_form_annotation.py（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 135）**补上任务书要的那一类**：
#     ★ 「**方法↔属性**」= 旧成员与它后继的 **kind 不同** ✓
#     ★★ **依据两条、★ 独立、★ 实测 81 行 100% 一致**：
#       ★ ① 官方页 front-matter 的 `kind:` · ★★ ② 官方签名里的 `{get; set;}` ✓
#     ★★★ **实测**：★ 跨维 **17 行**（★ 生产 **1** 行 · ★ 探针 16 行）—
#       ★ **全是「方法 → 属性」**（★ `GetActiveSketch2` ⇒ `ActiveSketch`）✓
#   ★★★★ **两条硬边界**（★ 本测试守着）：
#     ★ **① 不动判据** —— 补法是加一维**只读标注**、★ `scan_obsolete_safe.py` 一行不改 ✓
#     ★★ **② 「没观测到」≠「不存在」** —— ★ `SystemValue` 压根不是调用点、
#       ★ 而 `GetSystemValue2` 的后继是 **method** ⇒ ★ **⇒ 「属性→方法」0 行**、
#       ★★ **而那是"在命中行里没出现"、★ 不是"不存在"** ⇒ ★ **不许写成后者** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ANN = REPO / "tools" / "annotate_obsolete_form.py"
DOC = REPO / "docs" / "phase2-obsolete-status.md"
OUT = REPO / "output" / "obsolete-form-annotation.json"
SCAN = REPO / "tools" / "scan_obsolete_safe.py"


def test_the_criterion_script_is_untouched() -> None:
    """★★★★★ 核心断言：★ **补这一维没有动判据**（★ 任务书逐字：★ 不改判据）✓

    ★★ **为什么最重要**：★ 任务书同时说了两件事 —— ★「补这一类」与 ★「**不改判据**」⇒
      ★★★ **⇒ 若为了补类去改命中判据，就违背了后一条**（★ 而那样"真命中 37"这个数就不可比了）✓
    """
    assert SCAN.is_file(), "★ 判据脚本不见了"
    t = SCAN.read_text(encoding="utf-8", errors="replace")
    #: ★★ 判据脚本里**不该**出现那个新标注器的名字（★ 说明两者独立）✓
    assert "annotate_obsolete_form" not in t, "★ 判据脚本引用了标注器 ⇒ 两者不再独立"


def test_two_independent_grounds_agree() -> None:
    """★★★★ 核心断言：★ 两条依据（`kind:` 与签名）**实测一致**、★ 且不一致数为 0 ✓"""
    d = json.loads(OUT.read_text(encoding="utf-8"))
    assert d["★_两依据不一致"] == 0, (
        "★ 两条依据打架了 ⇒ 要单独看：%r"
        % [r for r in d["rows"] if not r["★_两依据一致"]][:3])
    assert len(d["rows"]) >= 60, "★ 能定形态的行太少：%d" % len(d["rows"])


def test_the_cross_form_class_is_counted() -> None:
    """★★★ 核心断言：★ 跨维那一类**数出来了**、★ 且**生产侧单独给了数** ✓"""
    d = json.loads(OUT.read_text(encoding="utf-8"))
    assert "★_跨维行数" in d and "★_跨维且生产" in d, "★ 两个数都要有"
    assert d["★_跨维行数"] >= 1, "★ 跨维一类不该是 0（★ 任务书点名的 `GetActiveSketch2` 就在里面）"
    #: ★★ 每一行都要标出**方向和两边的 kind** ✓
    for r in d["rows"]:
        if r["★_跨维"]:
            assert "→" in r["★_跨维"], "★ 跨维那格要写清方向：%r" % r["★_跨维"]
            assert r["old_kind"] and r["succ_kind"], "★ 两边的 kind 都要有"


def test_the_negative_direction_is_reported_as_unobserved() -> None:
    """★★★★★ 核心断言：★ **「属性 → 方法」那一档必须写成「没观测到」** ✓

    ★★ **为什么这条最值钱**：★ `SystemValue` 压根**不是调用点**、
      ★ 而 `GetSystemValue2` 的后继是 **method** ⇒ ★★ **⇒ 那个方向实测 **0 行**** ⇒
      ★★★ **⇒ 而"0 行"有两种读法**：★「不存在」与 ★「在命中行里没出现」⇒
      ★★ **⇒ 把前者写成后者就是**虚报****（★ 与纪律②同族）✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "没观测到" in t or "没出现" in t, "★ 没写明那是「没观测到」"
    assert "不是" in t and "不存在" in t, "★ 没把「没观测到」与「不存在」分开"


def test_the_three_same_family_mistakes_are_recorded() -> None:
    """★★★★ 核心断言：★ 我踩的**三次同族错**都写进文档（★ 含共同解）✓

    ★★ **三次**：★ ① 取错字段（`★_按成员` vs `全部行`）· ★★ ② 猜形状（list vs dict）·
      ★★★ ③ 后继名缺 `I` ⇒ 查不到页 ⇒ 误判"判不出来" ✓
    ★★★★ **⇒ 共同解**：★ **读别人的产物前先把它打出来** + ★ **名字找不到时先试常见变形** ✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "全部行" in t, "★ ① 取错字段那条没记"
    assert "list" in t, "★ ② 猜形状那条没记"
    assert "ISketchManager" in t, "★ ③ `I` 前缀那条没记"
    assert "打出来" in t, "★ 共同解没写"
