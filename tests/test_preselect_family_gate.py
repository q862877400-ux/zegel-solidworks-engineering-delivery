"""★ 测「预选族」门禁（`scripts/check_preselect_family.py`）—— ★ 含**负例**（事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_preselect_family_gate.py
# 定位:   ★ 事实 62：「一个门禁「写了」不等于它「有效」—— **负例测试是唯一的证明**」⇒
#           本测试的**负例是主角**：★ 喂一个「文档要求先选 ∧ 无 pre_call/derived_args ∧
#           无 selection 入参 ∧ 函数自己也不会选」的样本 ⇒ ★ **门禁必须命中** ✓
#         ★★ 另有**四条对照**（都必须**不**命中）—— 它们各自对应本门禁**实测踩过的一个假阳性**：
#           ① 函数**自己会选**（`create_fold` / `insert_replace_face` / `create_revolved_surface`）
#              ★ 加第 ④ 条判据前，这三条被误报 ✗
#           ② 文档里那句是**否定句**（`feature_cosmetic_thread` 逐字「调用方**不必**先选」）✗
#           ③ 同上，但**否定词被 Markdown 强调符劈开**（`不必**先选**`）⇒ ★ 第一版过滤看不见它 ✗
#           ④ spec **已有** `selection` 入参 或 已有 `pre_call` ⇒ 模型有办法选 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_preselect_family as gate                                    # noqa: E402

BASELINE = ROOT / "docs" / "preselect-family-baseline.json"

DOC_ZH = "★ **从当前选中的几何建一条参考轴**（★ 官方要求**先选中**几何：圆柱面 / 圆锥面 / 两点）。"
DOC_EN = "The caller must first select the pull-direction face/edge/plane."
FUNC_BARE = "def make_axis(model):\n    return model.InsertAxis2(True)\n"
FUNC_SELF = "def make_axis(model):\n    model.Extension.SelectByID2('', 'FACE', 0, 0, 0, False, 1, None, 0)\n    return model.InsertAxis2(True)\n"


def test_negative_bare_preselect_is_caught() -> None:
    """★★ **负例**（事实 62）：★ 文档要求先选、四条判据全中 ⇒ **必须命中** ✓"""
    snip = gate.judge(DOC_ZH, False, False, False, FUNC_BARE)
    assert snip, "★ 负例**没有**被拦住 ⇒ 门禁抓不到它真正要抓的东西（事实 62）"
    assert "先选中" in snip, "★ 命中要回**原文片段**（便于人工复核）：%r" % snip
    assert gate.judge(DOC_EN, False, False, False, FUNC_BARE), "★ 英文那句话也要认 ✓"


def test_function_that_selects_itself_is_not_flagged() -> None:
    """★ 对照①：★ 目标函数**自己会选** ⇒ 不许命中（★ 这是实测踩过的假阳性）✓"""
    assert gate.judge(DOC_ZH, False, False, False, FUNC_SELF) == "", \
        "★ 自建选区的工具被误报 ⇒ 又回到 21 条里混着 3 条假阳性那一版"


def test_helper_style_self_selection_is_not_flagged() -> None:
    """★★ 对照①**-bis**（★ 2026-10-07 规格 216 实测补的）：★ 用**本仓自己的选择助手**也算"自己会选" ✓

    ★ 起因：把 14 条逐条读函数体时，实测出**两条假阳性** —— 它们的函数体**逐字**是
      `_select_by_id(asm_model.Extension, component_name, "COMPONENT")` 与
      `SS.select_entity_by_index(model, "FACE", int(face_index))`，
      ★★ 而 token 集只认 `SelectByID2` / `Select4(` 这类**裸 COM 调用** ✗
      ⇒ ★ 于是「**自己会选**」被误报成「**没人能选**」✓
    ⚠ 这条是**负例**（★ 事实 62：负例是判据有效的唯一证明）—— ★ 它红 ⇒ 意味着
      ★ 又有一类"本仓自己的写法"没被认出来，★ 门禁会开始误报自己会选的工具 ✓
    """
    for helper in ("_select_by_id(model.Extension, 'Comp1', 'COMPONENT')",
                   "SS.select_entity_by_index(model, 'FACE', 0)",
                   "_select_faces_for(model, '+z')",
                   "_select_com_object(model, 'FACE', 0)",
                   "select_component_by_name(asm, 'Comp1')",
                   #: ★★ 2026-10-07 T-216-06b 实测补的两条 —— ★ 判据已收成**命名约定** `select_*`：
                   #:   ★ 起因：我给圆顶新写的自选助手叫 `select_face_by_index_mark1`，
                   #:     ★ 而**逐个点名的名单必然漏**（★ 本仓 `select_object` / `select_face_at` /
                   #:     `select_by_selector_report` 是一族）⇒ ★ 改成认"调用 `select_…(`" 这个约定 ✓
                   "select_face_by_index_mark1(model, 0)",
                   "select_object(model, obj)"):
        fn = "def f(model):\n    %s\n    return model.Something()\n" % helper
        assert gate.judge(DOC_ZH, False, False, False, fn) == "", (
            "★ `%s` 没被当成自选 ⇒ 门禁会误报自己会选的工具" % helper.split("(")[0])


def test_negated_requirement_is_not_flagged() -> None:
    """★ 对照②：★ 那句是**否定句**（「调用方不必先选」）⇒ 不许命中 ✓"""
    doc = "★ 本工具自己先把圆柱面按 mark=0 选中 ⇒ ★ 调用方**不必**先选中任何东西。"
    assert gate.judge(doc, False, False, False, FUNC_BARE) == "", \
        "★ 否定句被当成要求 ⇒ 与外部清单第 6 类（NOT deprecated 被判 deprecated）同型"


def test_markdown_split_negation_is_not_flagged() -> None:
    """★★ 对照③（**回归位**）：★ 否定词被 Markdown 强调符**劈开**时也必须认出来 ✓

    ⚠ 实测：`feature_cosmetic_thread` 的自述逐字是「调用方`**不必**先选`」——
      ★ **字面上没有 `不必先选` 这个连续子串** ⇒ ★ 第一版否定过滤**看不见它**、照报 ✗
    """
    doc = "★ 调用方**不必**先选；★ 找不到圆柱面时如实报 preconditions_held=False。"
    assert gate.judge(doc, False, False, False, FUNC_BARE) == "", \
        "★ 被 `**` 劈开的否定词没认出来 ⇒ 假阳性会再回来"


def test_selection_param_or_pre_call_suppresses() -> None:
    """★ 对照④：★ 已有 `selection` 入参 或 已有 `pre_call` ⇒ 模型有办法选 ⇒ 不许命中 ✓"""
    assert gate.judge(DOC_ZH, False, False, True, FUNC_BARE) == "", "★ 有 selection 入参仍被报"
    assert gate.judge(DOC_ZH, True, False, False, FUNC_BARE) == "", "★ 有 pre_call 仍被报"
    assert gate.judge(DOC_ZH, False, True, False, FUNC_BARE) == "", "★ 有 derived_args 仍被报"


def test_current_tree_matches_baseline() -> None:
    """★ 正例：★ 真仓当前的命中**必须逐条对上基线** —— ★ 新增即失败、基线腐坏也失败 ✓"""
    entries = json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]
    known = {e["tool"] for e in entries}
    got = {h["tool"] for h in gate.scan()}
    assert not (got - known), "★ 有**没登记**的命中（新犯的）：%r" % sorted(got - known)
    assert not (known - got), "★ 基线里认了、实际已不存在 ⇒ **名单腐坏**：%r" % sorted(known - got)
    for e in entries:
        for f in ("tool", "module", "function", "verdict", "reason"):
            assert str(e.get(f) or "").strip(), "★ 基线条目缺 `%s`：%r" % (f, e)
