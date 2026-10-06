"""★ 批次 93 的契约测试：钣金展开 / 折叠 / 折边（3 个）+ ★★ 裁决书强制的三处静态断言。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch93.py` · `scripts/sw_sheet_metal.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 SC-2/SC-3/SC-5；★ 本文件三层判据：
#         ① 契约：3 个 spec 都能解析到真实函数；★ 必填形参全声明（门禁口径）✓
#         ② ★★ **裁决书强制要求的 L2/L3 静态断言**（idx 173 的原话：
#            「这三处错误应做成 L2/L3 静态断言（谁再照它抄就会被当场抓住）」）：
#            · 别家用 `InsertHemFeature2` —— ★ 官方全树**零命中**（真名 `InsertSheetMetalHem2`）
#            · 别家把 `swHemTypes_e` 的 `Open=0` / `Closed=1` **正好互换**
#            · 别家**漏掉 `Double=4`**
#         ③ ★ 本轮实测出来的三条**契约常量**（mark 表 / mark action / 展开的 mark 不是必需）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch93 as b93                              # noqa: E402

EXPECTED = 3


def test_batch93_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch93"' in t


def test_three_specs_declared_and_resolve():
    assert len(b93.SPECS_BATCH93) == EXPECTED, len(b93.SPECS_BATCH93)
    for s in b93.SPECS_BATCH93:
        m = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(m, s.function, None)
        assert callable(fn), "%s → %s.%s" % (s.name, s.module, s.function)
        assert getattr(s, "inject", "") == "model", (s.name, getattr(s, "inject", ""))


def test_required_params_are_all_declared():
    for s in b93.SPECS_BATCH93:
        m = importlib.import_module("scripts.%s" % s.module)
        sig = inspect.signature(getattr(m, s.function))
        declared = {p.name for p in s.params}
        required = [n for n, p in sig.parameters.items()
                    if p.default is inspect.Parameter.empty and n != "model"]
        assert not [n for n in required if n not in declared], (s.name, required, declared)


# ── ★★ 裁决书强制的三处静态断言（idx 173 hem）─────────────────────────────────────

def test_hem_type_table_matches_official_enum_exactly():
    """★★★ 官方 `swHemTypes_e` 的**五个成员一个不漏**（`C:\\swapi\\enums\\swHemTypes_e.md`）。

    这条同时钉死别家的**两处错**：★ `Open`/`Closed` **互换**（官方是 Open=**0**、Closed=**1**）·
    ★ **漏掉 `Double=4`** ✓
    """
    from sw_sheet_metal import HEM_TYPES
    assert HEM_TYPES == {"open": 0, "closed": 1, "teardrop": 2, "rolled": 3, "double": 4}, HEM_TYPES
    assert len(HEM_TYPES) == 5, HEM_TYPES              # ★ 少一个（漏 Double）就红
    assert HEM_TYPES["open"] == 0 and HEM_TYPES["closed"] == 1   # ★ 互换就红


def test_hem_real_member_name_is_used_not_the_external_hallucination():
    """★★★ 别家调的 `InsertHemFeature2` 在官方全树**零命中** ⇒ ★ 本仓**不许**出现那个名字。

    ⚠ **本用例第一版把"防它的注释"也报成了违规**（★ 交接文档 trap 4 的同一形态：
    「会喊狼的守卫会被无视」）⇒ ★ 修法**照本仓既有的做法**：先用
    `scripts/check_env_pitfalls.strip_comments_and_strings` 把**注释与字符串**剥成等长空白
    —— ★ **把「引用」与「断言」分开**（★ 事实 61 定则④：写了个好用的工具函数，就要在所有同类场合用它）✓
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_env_pitfalls import strip_comments_and_strings
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8")
    code = strip_comments_and_strings(src)          # ★ 只留**代码**，散文/注释一律剥掉
    #: ★ 判据要**分开**：① **幻觉名**不许出现在**代码**里（注释里"引用它"是允许的，那正是防它的证据）；
    #:   ② **真名**必须出现在**字符串字面量**里（它正是 `get_com_member(..., "...")` 的实参）✓
    assert "InsertHemFeature2" not in code, "★ 那是**不存在**的成员名（官方真名 InsertSheetMetalHem2）"
    assert '"InsertSheetMetalHem2"' in src, "★ 必须用官方真名（作为成员名字符串）"


def test_hem_position_and_relief_tables():
    """★ 官方 `swHemPositionTypes_e`（Inside=1 · Outside=2）与 `swSheetMetalReliefTypes_e`
    （Rectangular=1 · Tear=2 · Obround=3 · None=4 · TearBend=5）逐值对齐 ✓"""
    from sw_sheet_metal import HEM_POSITIONS, HEM_RELIEFS, HEM_RELIEF_TEARS
    assert HEM_POSITIONS == {"inside": 1, "outside": 2}, HEM_POSITIONS
    assert HEM_RELIEFS == {"rectangular": 1, "tear": 2, "obround": 3, "none": 4,
                           "tear_bend": 5}, HEM_RELIEFS
    assert HEM_RELIEF_TEARS == {"rip": 1, "extend": 2}, HEM_RELIEF_TEARS


# ── ★ 本轮真机定出来的两条契约常量 ────────────────────────────────────────────

def test_unfold_mark_table_matches_the_official_example():
    """★★ mark 表取自官方示例（`Insert_and_Access_Fold_Feature_Example_VB.md`）：
    **固定面 mark 1 · 实体特征 mark 4** —— ★ **不许跨条复制**，本用例钉住这一条的值 ✓"""
    from sw_sheet_metal import UNFOLD_MARKS
    assert UNFOLD_MARKS == {"fixed_face": 1, "bends": 4}, UNFOLD_MARKS


def test_selection_mark_action_is_swselectionmarkset_zero():
    """★★★ 本仓亲自踩过的坑：`SetSelectedObjectMark` 的第 3 参是 `swSelectionMarkAction_e`，
    **要传 `swSelectionMarkSet`(0)** —— 传 `-1` 会**静默不生效**（返回 `false`、不报错）⇒
    那正是第一轮 unfold "没建出来" 的原因 ✓"""
    from sw_sheet_metal import SELECTION_MARK_ACTION
    assert SELECTION_MARK_ACTION["set"] == 0, SELECTION_MARK_ACTION


def test_unfold_runtime_status_is_true_and_hem_is_false():
    """★ 能力等级由**真机状态表**承载：unfold/fold **建成**（True）· hem **五种形态全失败**（False）✓"""
    from sw_sheet_metal import SHEET_METAL_RUNTIME_STATUS as ST
    assert ST["create_unfold"][0] is True, ST["create_unfold"]
    assert ST["create_fold"][0] is True, ST["create_fold"]
    assert ST["create_hem"][0] is False, ST["create_hem"]


def test_hem_refuses_by_default_and_names_the_reason():
    """★★ 已知不可用的入口 **默认先抛**、且**说清原因**（★ 不让用户吃裸 COM 错误）——
    ★ 复跑负实验要显式 `allow_unverified=True` ✓"""
    import sw_sheet_metal as SM
    try:
        SM.create_hem(None, "index:0")
        raise AssertionError("★ create_hem 应当先抛（require_verified）")
    except RuntimeError as exc:
        assert "create_hem" in str(exc) and "实测失败" in str(exc), str(exc)[:200]


def test_name_list_accepts_string_or_list():
    """★ 工具层传逗号分隔字符串、能力层收 list ⇒ 能力层**两种都收**（★ 换算/解析只在边界做一次）✓"""
    from sw_sheet_metal import _as_name_list
    assert _as_name_list("a, b ,c") == ["a", "b", "c"]
    assert _as_name_list(["a", " b "]) == ["a", "b"]
    assert _as_name_list(None) == [] and _as_name_list("") == []


def test_total_specs_count_grew_by_three():
    """★ SC-2：工具总数 = 439（批 92 后）+ 3 ✓"""
        #: ★★ 这里**故意不钉绝对总数** —— ★ 我原来钉的是 `== 442`，结果**每加一批就让
    #:   前面所有批次的测试全红**（★ 全量 pytest 时才暴露，焦点测试看不见）⇒
    #:   ★ **绝对总数只有一处权威断言**：`tests/test_server_wiring.py` ✓
    assert len(rc.all_specs()) >= 442
