"""★ 效应声明的契约与负例（规格 210 · B1）：判不出**不许**当成只读，且生成物必须新鲜。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/effect_rules.py` · `mcp-server/tool_registry.py` · `tools/gen_effect_declarations.py`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B1-2/B1-4/B1-5**。本文件钉四件事：
#     ① ★★ **要害性质**：`writes` 判不出（`None`）时，`effective_read_only` **必须为假** ——
#        ★ 绝不因为「扫不到成员名」就宣称只读 ✓
#     ② ★ `read_only` **由 `writes` 派生**（「确认无写」 ⇒ 只读；「确有写」 ⇒ 非只读）；
#        ★ 显式声明优先（人判 / 真机实证可以覆盖机械初判）✓
#     ③ ★ **生成物新鲜度**：`docs/effect-declarations.json` 必须等于**现算**的结果 ——
#        ★ 与 `level` 审计、生成物等既有做法同族（门禁查的是产物，不是承诺）✓
#     ④ ★ 动词规则的方向性：**宁可把读判成写，绝不反过来**（★ 保守方向）✓
# 官方依据: 七类状态由外部评审给出；动词规则见 `mcp-server/effect_rules.py` 的来源块
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
from tool_registry import ToolSpec, effective_read_only, effective_writes, _tool_annotations   # noqa: E402
from effect_rules import (STATE_CLASSES, classify_member, classify_members,   # noqa: E402
                          first_verb, load_kind_index)

TABLE = ROOT / "docs" / "effect-declarations.json"


def _spec(**kw) -> ToolSpec:
    base = dict(name="t_x", title="t", module="sw_part", function="noop")
    base.update(kw)
    return ToolSpec(**base)


# ── ① 要害性质：判不出 ≠ 只读 ────────────────────────────────────────────
def test_unknown_writes_is_never_reported_as_read_only():
    """★★★ **本规格的要害**：`writes` 未知（`None`）⇒ `effective_read_only` **假**。

    ★ 为什么这条最要紧：★ 真机跑里「只读工具可以在同一状态连续调用、不重载副本」，
    而「写工具」必须隔开（★ 否则会有副作用互相污染）；★ 一旦把写工具当只读，
    ★★ 既会**污染普查读数**，也会在 B4 里**开放不该开放的自动重试** ✓
    """
    s = _spec()
    object.__setattr__(s, "writes", None)              # ★ 显式模拟"表里也没有"
    assert effective_writes(s) is None
    assert effective_read_only(s) is False, "★ 判不出时绝不许宣称只读"


def test_confirmed_no_writes_is_read_only():
    s = _spec(writes=())
    assert effective_read_only(s) is True
    assert "destructiveHint" in _tool_annotations(s) and \
        _tool_annotations(s)["destructiveHint"] is False


def test_confirmed_writes_is_not_read_only():
    s = _spec(writes=("document",))
    assert effective_read_only(s) is False
    assert "destructiveHint" not in _tool_annotations(s), "★ 写工具未声明破坏性 ⇒ 不发（缺省=可能破坏）"


def test_explicit_declaration_wins_over_derivation():
    """★ 显式声明优先 —— ★ 人判 / 真机实证可以覆盖机械初判（★ 两个方向都要能覆盖）✓"""
    assert effective_read_only(_spec(read_only=True, writes=("document",))) is True
    assert effective_read_only(_spec(read_only=False, writes=())) is False


# ── ② 动词规则的方向性 ───────────────────────────────────────────────────
def test_verb_rule_is_conservative():
    """★ 判**写**的动词比判读的多；★ 且**未知动词不判读**（⇒ 计入 unclassified，不当作无写）✓"""
    assert first_verb("GetSelectedObjectCount2") == "get"
    assert first_verb("InsertSketch") == "insert"
    assert first_verb("CreateDefinition") == "create"
    v = classify_members(["GetName", "CreateSketch"])
    assert v["writes"] == ["document"], v
    unknown = classify_members(["FrobnicateThing"])
    assert unknown["writes"] is None, "★ 全是未知动词 ⇒ writes 未知（不是无写）"


def test_empty_members_is_unknown_not_pure_read():
    """★★ 空成员集 ⇒ **未知**（`None`），★ **不是** `[]` —— ★ 这个区分是整个 B1 的要害 ✓"""
    assert classify_members([])["writes"] is None
    assert classify_members(None)["writes"] is None


def test_state_classes_are_the_seven_from_the_review():
    assert tuple(STATE_CLASSES) == ("document", "filesystem", "selection", "active_doc",
                                    "edit_mode", "view", "rebuild")


# ── ③ 生成物新鲜度 ───────────────────────────────────────────────────────
def test_effects_table_is_fresh():
    """★ 生成物必须等于**现算**结果（★ 与 `level` 审计同族：门禁查产物，不查承诺）✓"""
    assert TABLE.exists(), "★ 缺生成物：跑 python tools/gen_effect_declarations.py"
    if not load_kind_index():
        import pytest
        pytest.skip("★ 本机无官方成员种类索引 ⇒ 现算结果必然不同，按铁律 5 记「查不到」")
    committed = json.loads(TABLE.read_text(encoding="utf-8"))
    import gen_effect_declarations as gen
    fresh = gen.build()
    assert committed.get("tools") == fresh.get("tools"), \
        "★ 效应表过期 ⇒ 跑 python tools/gen_effect_declarations.py"


def test_table_covers_every_tool():
    committed = json.loads(TABLE.read_text(encoding="utf-8"))
    names = {s.name for s in rc.all_specs()}
    assert names <= set(committed["tools"]), sorted(names - set(committed["tools"]))[:5]


def test_real_annotations_are_conservative():
    """★ 端到端：448 个真实工具里，★ **未声明只读的绝不出现 `readOnlyHint=True`**；
    ★ 且「未知」工具**不出现** `destructiveHint: False`（★ 那是「我确定不破坏」的口径）✓"""
    bad = []
    for s in rc.all_specs():
        w = effective_writes(s)
        ann = _tool_annotations(s)
        if ann.get("readOnlyHint") and getattr(s, "read_only", None) is None and w != ():
            bad.append((s.name, "readOnlyHint"))
        if ann.get("destructiveHint") is False and getattr(s, "destructive", None) is None \
                and not effective_read_only(s):
            bad.append((s.name, "destructiveHint"))
    assert bad == [], bad[:5]


# ── ④ 第二路（官方类型库）：属性看 {get; set;} ──────────────────────────────
def test_property_settable_is_a_write_by_type_library():
    """★★ 官方类型库那一路：★ 属性且可设（`{get; set;}`）⇒ **写** ⇒ ★ 该工具不许标只读 ✓"""
    idx = {"SomeWidget": {"kind": "property", "settable": True}}
    assert classify_member("SomeWidget", idx) == "write"
    v = classify_members(["SomeWidget"], kinds=idx)
    assert v["writes"] == ["document"], v


def test_property_get_only_is_a_read_by_type_library():
    """★ 属性且只读（`{get;}`）⇒ **读**（★ 这才算"认得"，可以让工具成为纯读）✓"""
    idx = {"SomeWidget": {"kind": "property", "settable": False}}
    assert classify_member("SomeWidget", idx) == "read"
    assert classify_members(["SomeWidget"], kinds=idx)["writes"] == []


def test_method_stays_unclassified_even_with_type_library():
    """★★ 评审的提醒必须成立：★ **普通方法没有读写标记** ⇒ ★ 即便查了类型库仍**判不出** ✓"""
    idx = {"SomeMethod": {"kind": "method", "settable": None}}
    assert classify_member("SomeMethod", idx) is None
    assert classify_members(["SomeMethod"], kinds=idx)["writes"] is None


def test_no_index_means_unknown_not_read():
    """★ 没有索引（干净机器 / 测试）⇒ 行为必须**确定**：★ 判不出仍是未知，★ 绝不是"读" ✓"""
    assert classify_member("SomeWidget", {}) is None
    assert classify_members(["SomeWidget"], kinds={})["writes"] is None


def test_second_path_actually_raises_coverage():
    """★ B1-7 的判据：★ 接上第二路后，**确认结论的覆盖率必须显著上升**（本机实测 20% → 41%）✓"""
    idx = load_kind_index()
    if not idx:
        import pytest
        pytest.skip("★ 本机没有成员种类索引 ⇒ 按铁律 5 记「查不到」，不假装测过")
    import register_capabilities as rc
    import gen_effect_declarations as gen
    fresh = gen.build()
    known = sum(1 for r in fresh["tools"].values() if r["writes"] is not None)
    assert known / max(1, len(fresh["tools"])) > 0.25, known
