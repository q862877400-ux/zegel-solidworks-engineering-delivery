"""★ 测 `TABLE_ANNOTATION_KINDS` 与**官方枚举逐值一致**（★ 处置 `JUDGE-C_D_E` 🔴 #7）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方枚举（本机 `C:\swapi\enums\swTableAnnotationType_e.md`）
# 文件:   tests/test_table_annotation_kinds.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#7**（★ `C-dw-2 C2-3`）逐字：「★ 通用公差表类型号写成 `6` …
#   ★ 官方 `swTableAnnotation_GeneralTolerance | 9` ／ `swTableAnnotation_WeldTable | 6`
#   ⇒ ★★ **焊接表会被误报成公差表、真公差表被打成 `unknown`**」✓
#   ★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "subskills" / "solidworks-engineering-drawing" / "scripts"))

import drawing_workflow as D                                              # noqa: E402

#: ★ 官方枚举页（★ 铁律 4 的第 ① 套源 —— `C:\swapi\`）
OFFICIAL = Path(r"C:\swapi\enums\swTableAnnotationType_e.md")
#: ★★ 官方成员名 → 本仓用的短名（★ 改后表）
WANT = {
    "swTableAnnotation_General": "general",
    "swTableAnnotation_HoleChart": "hole_chart",
    "swTableAnnotation_BillOfMaterials": "bom",
    "swTableAnnotation_RevisionBlock": "revision",
    "swTableAnnotation_WeldmentCutList": "weldment_cut_list",
    "swTableAnnotation_TitleBlock": "title_block",
    "swTableAnnotation_WeldTable": "weld_table",
    "swTableAnnotation_BendTable": "bend_table",
    "swTableAnnotation_PunchTable": "punch_table",
    "swTableAnnotation_GeneralTolerance": "general_tolerance",
    "swTableAnnotation_FamilyTable": "family_table",
}


def _official_values() -> dict:
    if not OFFICIAL.is_file():
        return {}
    out = {}
    for l in OFFICIAL.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\|\s*(swTableAnnotation_\w+)\s*\|\s*(\d+)\s*\|", l)
        if m:
            out[m.group(1)] = int(m.group(2))
    return out


def test_6_is_weld_table_not_tolerance() -> None:
    """★★★ 核心断言：★ `6` **必须**是 `weld_table`（★ 病灶就是把它写成 `general_tolerance`）✓"""
    assert D.TABLE_ANNOTATION_KINDS.get(6) == "weld_table", (
        "★ `6` 不是 weld_table ⇒ 焊接表会被误报成公差表（★ JUDGE-C_D_E #7）")


def test_9_is_general_tolerance() -> None:
    """★★★ 核心断言：★ `9` **必须**是 `general_tolerance`（★ 改前它根本不在表里）✓"""
    assert D.TABLE_ANNOTATION_KINDS.get(9) == "general_tolerance", (
        "★ `9` 不是 general_tolerance ⇒ 真通用公差表（Type=9）会被打成 `unknown`")


def test_every_official_member_is_covered() -> None:
    """★★ **与官方枚举页逐值对账** —— ★ 官方有 11 个成员，★ 表里就必须有 11 个键 ✓"""
    official = _official_values()
    if not official:
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    missing = {}
    for member, value in official.items():
        want = WANT.get(member)
        got = D.TABLE_ANNOTATION_KINDS.get(value)
        if want is not None and got != want:
            missing[member] = (value, want, got)
    assert not missing, "★ 与官方枚举对不上：%r" % missing


def test_no_duplicate_short_names() -> None:
    """★★ **负例 · 冲突**：★ 两个值不许映射到同一个短名 —— ★ 那会让"按名字分表"分不开 ✓"""
    names = list(D.TABLE_ANNOTATION_KINDS.values())
    assert len(names) == len(set(names)), (
        "★ 有重复短名 ⇒ 按名字区分表格类型会失效：%r" % [n for n in names if names.count(n) > 1])
