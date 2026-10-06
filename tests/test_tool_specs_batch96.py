"""★ 批次 96 的契约测试：模型标注插入 + ★★ 官方 26 个标注类型一个不漏 + 调用序契约。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch96.py` · `scripts/sw_drawing_create_missing.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-5（idx 205）**；本文件钉四件事：
#         ① 契约：spec 能解析、必填形参全声明 ✓
#         ② ★★ **官方 `swInsertAnnotation_e` 的 26 个成员一个不漏、逐值对齐**
#            （★ 同 hem 那条纪律：**一个不漏** —— 少一个就是静默的能力缺口）✓
#         ③ ★ **官方 `swImportModelItemsSource_e` 四值**逐值对齐 ✓
#         ④ ★★ **调用序契约**：**`AllViews=False` 时必须把视图留在选区里**
#            （★ 我真机踩过：清掉选区 ⇒ 回空数组）✓
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
import tool_specs_batch96 as b96                              # noqa: E402

EXPECTED = 1

#: ★★ 官方 `swInsertAnnotation_e` 的**全部 26 个成员**（逐值抄自 `C:\\swapi\\enums\\swInsertAnnotation_e.md`）
OFFICIAL_ANNOTATION_BITS = {
    "swInsertCThreads": 1, "swInsertDatums": 2, "swInsertDatumTargets": 4,
    "swInsertDimensions": 8, "swInsertInstanceCounts": 16, "swInsertGTols": 32,
    "swInsertNotes": 64, "swInsertSFSymbols": 128, "swInsertWelds": 256,
    "swInsertAxes": 512, "swInsertCurves": 1024, "swInsertPlanes": 2048,
    "swInsertSurfaces": 4096, "swInsertPoints": 8192, "swInsertOrigins": 16384,
    "swInsertDimensionsMarkedForDrawing": 32768,
    "swInsertHoleWizardProfileDimensions": 65536,
    "swInsertHoleWizardLocationDimensions": 131072, "swInsertRefPoints": 262144,
    "swInsertDimensionsNotMarkedForDrawing": 524288, "swInsertholeCallout": 1048576,
    "swInsertWeldBeads": 2097152, "swInsertSketches": 4194304,
    "swInsertWeldBeads_ET": 8388608, "swInsertTolerancedDims": 16777216,
    "swInsertCenterOfMass": 33554432,
}


def test_batch96_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch96"' in t


def test_one_spec_declared_and_resolves():
    assert len(b96.SPECS_BATCH96) == EXPECTED, len(b96.SPECS_BATCH96)
    s = b96.SPECS_BATCH96[0]
    assert s.name == "solidworks_drawing_insert_model_items", s.name
    assert s.module == "sw_drawing_create_missing", s.module
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.module, s.function)
    assert s.inject == "model"


def test_required_params_are_all_declared():
    s = b96.SPECS_BATCH96[0]
    sig = inspect.signature(
        importlib.import_module("scripts.sw_drawing_create_missing").insert_model_annotations)
    declared = {p.name for p in s.params}
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty and n != "model"]
    assert not [n for n in required if n not in declared], (required, declared)


def test_annotation_bit_table_is_complete_and_exact():
    """★★★ 官方 `swInsertAnnotation_e` 是 **26 个成员的位掩码** —— ★ **一个不漏、逐值相等**。

    ★ 为什么这条重要：★ 少抄一个成员 = **一个静默的能力缺口**（调用方传那个名字会被拒，
      而官方明明有）⇒ ★ 与 hem 那条「五成员一个不漏」**同一纪律** ✓
      ⚠ ★ 本用例**故意把官方名单写在测试里**（而不是从被测模块读）——
      ★ 否则「表抄漏了」和「断言读的是同一张错表」就分不开了 ✓
    """
    from sw_drawing_create_missing import ANNOTATION_TYPE_BITS
    assert len(OFFICIAL_ANNOTATION_BITS) == 26, len(OFFICIAL_ANNOTATION_BITS)
    assert ANNOTATION_TYPE_BITS == OFFICIAL_ANNOTATION_BITS, (
        sorted(set(OFFICIAL_ANNOTATION_BITS) - set(ANNOTATION_TYPE_BITS)),
        sorted(set(ANNOTATION_TYPE_BITS) - set(OFFICIAL_ANNOTATION_BITS)))


def test_model_item_source_table_matches_official():
    from sw_drawing_create_missing import MODEL_ITEM_SOURCES
    assert MODEL_ITEM_SOURCES == {"entire_model": 0, "selected_feature": 1,
                                  "selected_component": 2, "assembly_only": 3}, MODEL_ITEM_SOURCES


def test_mask_helper_or_s_the_bits_and_rejects_unknown_names():
    """★ 位掩码是**按位或**；★ 未知类型名**必须报错**（★ 铁律 5：不猜、不静默忽略）✓"""
    from sw_drawing_create_missing import _annotation_mask
    assert _annotation_mask("Planes,Origins") == 2048 | 16384
    assert _annotation_mask("swInsertDimensions, swInsertGTols") == 8 | 32
    assert _annotation_mask("") == 0 and _annotation_mask(None) == 0
    try:
        _annotation_mask("swInsertTeapots")
        raise AssertionError("★ 未知类型名应当报错")
    except ValueError as exc:
        assert "26" in str(exc), str(exc)[:150]


def test_call_order_keeps_the_view_selected_when_all_views_is_false():
    """★★ 调用序契约：**官方示例走 `AllViews=True` 所以它清选区**；而 `AllViews=False` 时
    官方摘要要的是「**currently selected drawing view**」⇒ ★★ **必须把视图留在选区里** ——
    ★ 我真机踩过：无脑清掉 ⇒ `InsertModelAnnotations4` **回空数组**（一个指不出真因的现象）✓"""
    src = inspect.getsource(
        importlib.import_module("scripts.sw_drawing_create_missing").insert_model_annotations)
    assert "ActivateView" in src, "★ 官方示例独有的那一步不能少"
    assert "if all_views:" in src, "★ 清选区必须**以 AllViews 为条件**"


def test_refuses_when_nothing_is_asked_for():
    """★ 两个 `insert_all_*` 都 False 且 `types` 空 ⇒ **官方逐字说此时 Types 才有意义**
    ⇒ ★ 本函数**如实拒绝**（★ 不猜调用方要什么）✓"""
    from sw_drawing_create_missing import insert_model_annotations
    r = insert_model_annotations(None)
    assert r["ok"] is False, r
    r2 = insert_model_annotations(object())                    # ★ 先撞"什么都没让它插"
    assert r2["ok"] is False and "Types" in (r2["error"] or ""), r2


def test_tool_total_grew_by_one():
    assert len(rc.all_specs()) == 445, len(rc.all_specs())
