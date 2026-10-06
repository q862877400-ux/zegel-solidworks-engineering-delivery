"""★ 规格 213 · B2b/B3（后半）的契约与负例：爆炸直线 · SpeedPak · 曲线驱动阵列（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_assembly_doc.py` · `scripts/sw_pattern.py` ·
#         `mcp-server/tool_specs_batch102.py`）
# 文件:   tests/test_spec213_batch102_tools.py
# 定位:   ★ 规格 `specs/213-hook-up-tools/` 的 **B2b + B3 后半**（★ B 类 5 项的收尾 ✓）
# 判据（★ 一正多负，★ 事实 62：★ 门禁只靠负例证明）：
#   ★ **正例①**：★ 3 个 ToolSpec 过 `check_spec` ✓
#   ★ **正例②**：★ 3 个都进 `all_specs()` ✓ · ★ 工具数**不少于** 456 + 3 ✓ · ★ 无重名 ✓
#   ★ **正例③（B 类特有）**：★ 三个声明的**模块函数真的存在** ✓ · ★ **签名对得上官方参个数** ✓
#   ★★ **负例①（本批最要紧的一条）**：★★ **`curve_driven_pattern` 的登记等级必须是 `stitched`** ✗
#     —— ★ 官方页第一行就是 `Obsolete` ✓，★ 且真机两档有效读数皆不建 ✓
#     ⇒ ★★★ **A7 逐字：★ 全文不许把 `stitched` 写成 `verified`** ✓
#   ★★ **负例②**：★ 爆炸直线的判据**必须是「侧变化」**、★ **不是「现在有」** ✗ ——
#     ★★★ 本批真机对照原探针才发现我第一版判据**太弱** ✓
#   ★★ **负例③**：★ SpeedPak 的判据**必须带**前后两个字段 ✓（★ 「这次建成了」与
#     「它一直是开的」要分开 ✓）
#   ★★ **负例④**：★ 长度参数必须 `_mm` 结尾（规则 2）· ★ 而枚举/布尔**不许**带单位后缀（规则 2b）✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                    # noqa: E402
import tool_registry as R                                             # noqa: E402
import tool_specs_batch102 as B                                       # noqa: E402

WANTED = ("solidworks_insert_explode_line_sketch", "solidworks_create_speedpak",
          "solidworks_insert_local_curve_driven_pattern")
#: ★★ 基线是**实测**的：★ `batch101` 挂完后 `len(all_specs()) == 456` ✓
BASE_TOOL_COUNT = 456
UNIT_SUFFIXES = ("_mm", "_mm2", "_mm3", "_deg", "_px", "_s", "_kg", "_m2", "_rad")


def _spec(name: str):
    return next(s for s in B.SPECS_BATCH102 if s.name == name)


#: ── 正例① ───────────────────────────────────────────────────────────────
def test_all_three_pass_check_spec():
    """★ **正例①**：★ 3 个 ToolSpec 过 `check_spec`（★ 规则 2 / 2b / 3 都在里面 ✓）。"""
    assert len(B.SPECS_BATCH102) == 3
    for s in B.SPECS_BATCH102:
        R.check_spec(s)


#: ── 正例② ───────────────────────────────────────────────────────────────
def test_all_three_are_in_all_specs():
    """★ **正例②**：★ 3 个都进 `all_specs()` ✓ · ★ 总数**不少于** 456 + 3 ✓ · ★ 无重名 ✓

    ★★ **钉关系、不钉数字**（★ 本规格在 batch100 那里栽过一次 ✗）：★ 写死绝对值的话，
    ★ 下一批再挂工具就会让这条变红 ✓
    """
    names = [getattr(s, "name", "") for s in RC.all_specs()]
    assert len(names) >= BASE_TOOL_COUNT + 3, "★ 期望 ≥ %d、实际 %d" % (BASE_TOOL_COUNT + 3, len(names))
    missing = [w for w in WANTED if w not in names]
    assert not missing, "★ 没进 all_specs：%r" % missing
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, "★ 重名：%r" % dupes


#: ── 正例③（B 类特有）────────────────────────────────────────────────────
@pytest.mark.parametrize("name", WANTED)
def test_declared_module_function_exists(name):
    """★ **正例③（B 类特有）**：★ 声明的**模块函数真的存在** ✓ —— ★ 它们是**本批新写的** ✓。"""
    spec = _spec(name)
    import importlib
    mod = importlib.import_module(spec.module)
    assert callable(getattr(mod, spec.function, None)), (
        "★ %s.%s 不存在 —— 声明与实现脱节" % (spec.module, spec.function))


def test_explode_line_function_takes_only_the_document():
    """★ **正例④**：★ `insert_explode_line_sketch_report` **只有一个形参** ✓ ——
    ★★ 因为官方 `ISketchManager::InsertExplodeLineSketch` 是**零参** ✓。"""
    import sw_assembly_doc as A
    ps = list(inspect.signature(A.insert_explode_line_sketch_report).parameters)
    assert ps == ["doc"], ps


def test_curve_driven_function_matches_official_arity_13():
    """★ **正例⑤**：★ 参数式曲线驱动阵列的形参**对得上官方 13 参** ✓。

    ★ 官方 `FeatureLocalCurveDrivenPattern` 逐字 13 参：`FlipDir1 · Num1 · EqualSpacing1 ·
    Spacing1 · ReferencePoint · CurveMethod · AlignMethod · Direction2 · FlipDir2 · Num2 ·
    EqualSpacing2 · Spacing2 · PatternSeedOnly` ✓
    ★★ 加上本仓的两处**选择参**（★ 官方 mark 表：1 = Components to pattern ·
    2 = Curve/edge/sketch for Direction 1 ✓）
    """
    import sw_pattern as P
    got = set(inspect.signature(P.insert_local_curve_driven_pattern_report).parameters)
    want = {"flip_dir1", "num1", "equal_spacing1", "spacing1_mm", "reference_point",
            "curve_method", "align_method", "direction2", "flip_dir2", "num2",
            "equal_spacing2", "spacing2_mm", "pattern_seed_only",
            "seed_feature", "curve_sketch"}
    assert want <= got, "★ 缺 %r" % (want - got)


#: ── 负例①（★ 本批最要紧）────────────────────────────────────────────────
def test_curve_driven_pattern_doc_declares_obsolete_and_stitched():
    """★★★ **负例①**：★ `curve_driven_pattern` 的文档串**必须**同时点明两件事 ✓

    ★★★ **A7 逐字**：「全文没有一处把 `source_verified` 或 `stitched` 写成 `verified`」✗
    ⇒ ★★ 本项的真实状态是 **`stitched`**，★ 两条**独立**理由：
      ★ ① 官方页第一行就是 **`Obsolete`**（★ 逐字指向 `CreateFeature` + `ILocalCurvePatternFeatureData` ✓）
      ★ ② 真机**两档有效读数皆不建**（★ `mark1=True · mark2=True · 选区=2` 而新增 `[]` ✓）
    ★★ **所以文档串里必须能 grep 到 `stitched` 与 `Obsolete`** —— ★ 缺一个就算"写成 verified" ✗
    """
    doc = _spec("solidworks_insert_local_curve_driven_pattern").doc
    assert "stitched" in doc, "★ 文档串没写 `stitched` ⇒ 会被读成 verified ✗"
    assert "Obsolete" in doc, "★ 文档串没点明官方 `Obsolete` ⇒ 理由不全 ✗"


def test_verified_items_do_not_claim_obsolete():
    """★★ **负例①的对照**：★ 另两项**不许**出现 `Obsolete`（★ 它们是真机建成的 ✓）。"""
    for nm in WANTED[:2]:
        assert "Obsolete" not in _spec(nm).doc, "★ %s 不该提 Obsolete ✗" % nm


#: ── 负例②（★ 本批真机发现的那一处）──────────────────────────────────────
def test_explode_line_uses_side_change_not_presence():
    """★★ **负例②**：★ 爆炸直线的判据**必须用「侧变化」**、★ **不是「现在有」** ✗

    ★★★ 事由：★ 我第一版只记 `active_sketch_present`（★ "现在有没有" ✗）⇒
    ★★ **那分辨不了「这次插入了」与「本来就开着」** ✗ ——
    ★ 而**原探针**的判据是 `active_sketch_before=False → active_sketch_after=True` ✓
    ⇒ ★ 本测试把**修好后的形态钉住**：★ 源码里必须出现 `active_sketch_side_changed` ✓，
      ★ 且判据用的是它 ✓
    """
    src = (ROOT / "scripts" / "sw_assembly_doc.py").read_text(encoding="utf-8")
    assert "active_sketch_side_changed" in src, "★ 少了「侧变化」这个字段 ⇒ 判据退化成「现在有」 ✗"
    assert "bool(added) or side_changed" in src, "★ 判据必须用 `side_changed` ✓"
    #: ★ 而 `active_sketch_before` / `after` 两个都要在（★ 少了就分辨不了 ✓）
    assert "active_sketch_before" in src and "active_sketch_after" in src, src[:0]


#: ── 负例③ ───────────────────────────────────────────────────────────────
def test_speedpak_verdict_requires_before_and_after():
    """★★ **负例③**：★ SpeedPak 的判据**必须带前后两个字段** ✓

    ★★ 理由：★ 顶层**特征树看不见 SpeedPak** ✗ ⇒ 唯一判据是 `IComponent2::IsSpeedPak` 的回读 ✓；
    ★★★ 而★ **只记"之后"是不够的** —— ★「这次建成了」与「它一直是开的」**要分开记** ✗
    """
    src = (ROOT / "scripts" / "sw_assembly_doc.py").read_text(encoding="utf-8")
    assert "is_speedpak_before" in src and "is_speedpak_after" in src, "★ 缺前后字段 ✗"
    assert "is_sp_after is True and is_sp_before is not True" in src, (
        "★ 判据必须排除「本来就开着」那一种 ✓")


#: ── 负例④ ───────────────────────────────────────────────────────────────
def test_length_params_end_with_mm_and_enums_do_not():
    """★★ **负例④**：★ 长度 `_mm` 结尾（规则 2）· ★ 枚举/布尔**不许**带单位后缀（规则 2b）✓。"""
    spec = _spec(WANTED[2])
    wire = {p.name for p in spec.params}
    #: ★ `spacing1_mm` / `spacing2_mm` 是**长度**（官方 Remarks 说 "Distance between pattern instances" ✓）
    assert "spacing1_mm" in wire and "spacing2_mm" in wire, wire
    #: ★ 而**枚举/布尔**一个都不许带单位后缀
    for p in spec.params:
        if p.kind in (bool, int) and p.name not in ("num1", "num2"):
            bad = [s for s in UNIT_SUFFIXES if p.name.endswith(s)]
            assert not bad, "★ %r 是布尔/枚举却带单位后缀 %r ⇒ 规则 2b 会拦" % (p.name, bad)


#: ── 负例⑤ ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("name", WANTED)
def test_none_are_declared_read_only(name):
    """★★ **负例⑤**：★ 三项都**不许**声明 `read_only=True` —— ★ 它们都会改模型/装配 ✓。"""
    assert not R.effective_read_only(_spec(name)), "★ %s 被声明成只读、而它真的会改状态 ✗" % name
