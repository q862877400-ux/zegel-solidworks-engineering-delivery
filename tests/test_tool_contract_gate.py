"""★ 工具定义契约门禁的契约测试 + **双侧负例**（该报的报、不该报的不报）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_tool_contract.py`（被测门禁）
#         `specs/352-tool-definition-contract/spec.md` §二（判据 K1–K5 / K9 / K10）
# 定位:   ★ 事实 62（**负例是门禁有效的唯一证明**）在这里落地 ——
#         ★ 本门禁前两次（`specs/215` 的「只加一行首句」）**没治好**，就是因为
#         判据只覆盖「不可用 / 内部件」两类标记；这次判的是**形态本身**
#         ⇒ ★ 每条判据都必须有「该报」与「不该报」两侧样本，否则它会变成
#         一处误伤 498 条的机器 ✓
# 官方依据: DSH `agent-experience`（「Describe behavior, not implementation」）
#         + `@local/dsh-lean-mode/index.mjs` L130-131（lean 下 `description = firstLine`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_tool_contract.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


G = _load("tool_contract_gate_under_test", GATE)
OLD = _load(
    "lean_first_line_gate_for_parity",
    ROOT / "scripts" / "check_lean_first_line_caveat.py",
)

GOOD = (
    "Create an extruded boss from an existing sketch. "
    "The depth is in millimetres and is converted once at this boundary; "
    "the tool does not save the document."
)


def _p(name, description="", default=..., required=None):
    return SimpleNamespace(name=name, description=description, default=default, required=required)


def _spec(doc, params=(), read_only=None, writes=None, name="solidworks_demo"):
    return SimpleNamespace(name=name, doc=doc, params=list(params), read_only=read_only, writes=writes)


def codes(spec) -> list:
    return [c for c, _ in G.judge_spec(spec)]


# ── ① 断句口径与插件一致（★ 门禁与插件必须数同一件事）────────────────────
def test_lean_window_uses_the_shared_implementation():
    """★★ 「rem 口径只许有一个家」：本门禁**不重新实现**断句，而是调
    `scripts/check_lean_first_line_caveat.py::lean_first`（`specs/215` 的第一落点）。

    ★★ 为什么这条必须是断言：两处各写一遍断句 ⇒ 两道门禁会数**不同的事情**
    （`check_repo_uniformity.py` 的跨文件同函数体判据实测抓到过这一处）✓
    """
    src = GATE.read_text(encoding="utf-8")
    assert "from check_lean_first_line_caveat import lean_first" in src
    #: ★ 关键事实（`specs/215` 已踩过）：`firstLine()` **只按 `。` 与换行断句，ASCII `.` 不算**
    #:   ⇒ 英文 doc 的「第一段」就是**整段**，再整体截到 120 字符。
    #: ★ 逐条给出**期望值**（不是自比自 —— 那种断言等于没断言）
    assert OLD.lean_first("第一句。第二句。") == "第一句"
    assert OLD.lean_first("换行\n后面的都不算") == "换行"
    assert len(OLD.lean_first("A" * 200)) == 120
    #: ★ 英文 doc **没有** `。` 也没有换行 ⇒ 整段被截到 120（这才是真正的失败条件）
    assert OLD.lean_first(GOOD) == GOOD[:120]
    assert OLD.lean_first("★ 元数据。后面还有。") == "★ 元数据"
    assert G.LEAN_CHARS == 120
    assert len(OLD.lean_first("A" * 200)) == 120


def test_first_sentence_is_the_first_english_sentence():
    """★ 英文的「首句」按 `.` / `!` / `?` 断 —— 因为 `firstLine()` 不认 ASCII 句号，
    英文 doc 在 lean 下会**整段**被截到 120 ⇒ 真正的失败条件是「第一个英文句子超长」。"""
    assert G.first_sentence("Create a box. It does not save.") == "Create a box."
    assert len(G.first_sentence("A" * 200)) == 200
    #: ★ 中文句号**不是**英文首句的断点（英文 doc 里不该出现它 —— K1 会单独报 doc-cn-period）
    assert G.first_sentence("Create a box。It does not save.") == "Create a box。It does not save."


def test_compliant_spec_has_no_violations():
    assert codes(_spec(GOOD)) == []


def test_read_only_tool_passes_when_it_says_read_only():
    assert codes(_spec("Read back the weldment cut-list folders. Read-only.", read_only=True)) == []


def test_param_with_default_that_states_it_passes():
    doc = GOOD
    p = _p("depth_mm", "Extrusion depth in millimetres; defaults to 10.", default=10.0)
    assert codes(_spec(doc, [p])) == []


# ── ③ 该报的（每条判据的正面样本）────────────────────────────────────
def test_metadata_first_line_is_reported():
    got = codes(_spec("★ 官方签名（逐字，来自 AddMate5.md）：… Second sentence."))
    assert "first-meta" in got


def test_metadata_first_line_does_not_double_report_as_not_verb():
    """★ 一个病根只报一条 —— 否则棘轮会把「改好了」读成「降了两条」，进度虚高。"""
    got = codes(_spec("★ 官方签名（逐字）：… Second sentence."))
    assert "first-meta" in got
    assert "first-not-verb" not in got


def test_cjk_doc_is_reported():
    got = codes(_spec("建一个拉伸凸台。深度按毫米。"))
    assert "doc-cjk" in got
    assert "doc-cn-period" in got


def test_newline_in_doc_is_reported():
    assert "doc-newline" in codes(_spec("Create a box.\nSecond line."))


def test_trailing_period_is_required():
    assert "doc-no-period" in codes(_spec("Create a box. It does not save the file"))


def test_first_line_over_window_is_reported():
    doc = ("Create a box " + "with many words " * 12).strip() + ". It does not save."
    assert len(G.first_sentence(doc)) > 120
    assert "first-too-long" in codes(_spec(doc))


def test_first_line_must_start_with_a_verb():
    assert "first-not-verb" in codes(_spec("Sheet overview of the active drawing. Read-only."))


def test_hyphenated_prefix_is_accepted_as_a_verb():
    """★ `Auto-create` / `Re-run` 都是合法祈使句 ⇒ 去掉前缀再比（防误伤）。"""
    assert "first-not-verb" not in codes(_spec("Auto-create shut-off surfaces. It does not save."))
    assert "first-not-verb" not in codes(_spec("Re-run the solver. It does not save."))


def test_one_sentence_doc_is_reported():
    assert "doc-one-sentence" in codes(_spec("Create a box."))


def test_too_long_doc_is_reported():
    doc = GOOD + " " + ("It does not save the document. " * 25)
    assert len(doc) > G.DOC_CHARS
    assert "doc-too-long" in codes(_spec(doc))


def test_param_without_description_is_reported():
    assert "param-no-desc" in codes(_spec(GOOD, [_p("depth_mm")]))


def test_param_description_must_end_with_a_period():
    assert "param-desc-no-period" in codes(_spec(GOOD, [_p("depth_mm", "Depth in mm")]))


def test_param_description_must_be_english():
    assert "param-desc-cjk" in codes(_spec(GOOD, [_p("depth_mm", "深度，毫米.")]))


def test_param_default_must_be_stated():
    assert "param-default-unstated" in codes(
        _spec(GOOD, [_p("depth_mm", "Extrusion depth in millimetres.", default=10.0)])
    )


def test_write_tool_must_state_its_side_effect():
    """★★ DSH **不转发** MCP annotations（只转 name/description/parameters/output）
    ⇒ ★ 副作用只能写在描述里，否则模型看不见。"""
    plain = "Create a fillet on the selected edge. Use it after selecting an edge."
    assert "side-effect-unstated" in codes(_spec(plain, read_only=False))
    assert "side-effect-unstated" in codes(_spec(plain, writes=("document",)))


def test_read_only_tool_must_say_read_only():
    doc = "Read the feature list. It returns names and types."
    assert "side-effect-unstated" in codes(_spec(doc, read_only=True))


# ── ④ 棘轮语义（★ 只许降不许升）──────────────────────────────────────
def test_ratchet_accepts_known_violations_and_flags_new_ones():
    old = _spec("★ 元数据。 Second.", name="solidworks_old")
    fresh = _spec("★ 元数据。 Second.", name="solidworks_new")
    rows_old = [dict(name="solidworks_old", code=c, subject="", why="") for c in codes(old)]
    baseline = {"count": 1, "rows": rows_old}
    rows = [dict(name="solidworks_old", code="first-meta", subject="", why="")] + [
        dict(name="solidworks_new", code="first-meta", subject="", why="")
    ]
    new = G.compare_with_baseline(rows, baseline)
    assert [r["name"] for r in new] == ["solidworks_new"]
    #: ★ 空基线 ⇒ 全部算新增（迁移收敛后基线应为空，`--strict` 复核 498/498）
    assert len(G.compare_with_baseline(rows, {})) == 2
    assert fresh.name == "solidworks_new"


def test_param_level_violations_are_keyed_by_parameter_name():
    """★ 同一工具的两个坏参数不能塌成一个键 —— 否则修掉一个就被判「已收敛」。"""
    rows = [
        {"name": "t", "code": "param-desc-cjk", "subject": "a", "why": ""},
        {"name": "t", "code": "param-desc-cjk", "subject": "b", "why": ""},
    ]
    baseline = {"count": 1, "rows": [rows[0]]}
    assert [r["subject"] for r in G.compare_with_baseline(rows, baseline)] == ["b"]


# ── ⑤ 真跑一遍注册表（★ 防「门禁存在但没接线」的第四张面孔）───────────
def test_scan_sees_the_real_registry():
    rows, checked = G.scan()
    assert checked >= 300, "注册表没加载全 ⇒ 这个绿不可信"
    assert isinstance(rows, list)
