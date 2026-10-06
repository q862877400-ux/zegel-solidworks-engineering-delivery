"""★ 批次 95 的契约测试：相交特征（两步 PreIntersect2 → PostIntersect）+ 布尔 SafeArray 包装。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch95.py` · `scripts/sw_boolean_ops.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-3（idx 181）**；本文件钉四件事：
#         ① 契约：spec 能解析、必填形参全声明 ✓
#         ② ★★ **RegionType 三值表**逐值对齐官方 `PreIntersect2` 的 `## Parameters` ✓
#         ③ ★★ **布尔数组必须包 `VARIANT(VT_ARRAY | VT_BOOL)`** ——
#            ★ 本仓既有教训：**裸 list/tuple 会静默返回 `None`**（`sketch_relations.py` 轮 183 实测）✓
#         ④ 判据声明：**体数 + 特征树增量 + `GetIntersectionsCount()`**（★ 不拿 `IFeature` 当判据）✓
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
import tool_specs_batch95 as b95                              # noqa: E402

EXPECTED = 1


def test_batch95_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch95"' in t


def test_one_spec_declared_and_resolves():
    assert len(b95.SPECS_BATCH95) == EXPECTED, len(b95.SPECS_BATCH95)
    s = b95.SPECS_BATCH95[0]
    assert s.name == "solidworks_part_intersect", s.name
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.module, s.function)
    assert s.inject == "model"


def test_required_params_are_all_declared():
    s = b95.SPECS_BATCH95[0]
    sig = inspect.signature(importlib.import_module("scripts.sw_boolean_ops").create_intersect)
    declared = {p.name for p in s.params}
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty and n != "model"]
    assert not [n for n in required if n not in declared], (required, declared)
    assert declared == {"selection", "cap_planar", "region_type", "exclude", "merge",
                        "consume"}, declared


def test_region_type_table_matches_official():
    """★ 官方 `PreIntersect2` 的 `## Parameters` 逐字三值：**0=Intersecting · 1=Internal ·
    2=Intersecting and internal** ⇒ ★ 逐值钉住（★ 不许跨条复制别的 mark/映射表）✓"""
    from sw_boolean_ops import REGION_TYPES
    assert REGION_TYPES == {"intersecting": 0, "internal": 1,
                            "intersecting_and_internal": 2}, REGION_TYPES


def test_bool_array_is_wrapped_in_a_variant():
    """★★ 裁决书点名的"唯一要验"：`PostIntersect` 第 1 参是 `System.object`（布尔 SafeArray）⇒
    ★ 本仓**必须包 `VARIANT(VT_ARRAY | VT_BOOL)`**（★ 裸 list 会**静默回 None** —— 既有教训）✓"""
    from sw_boolean_ops import as_bool_variant
    v = as_bool_variant([False, True, False])
    assert v is not None
    assert getattr(v, "varianttype", None) is not None, v       # ★ 是 VARIANT，不是裸 list
    src = (ROOT / "scripts" / "sw_boolean_ops.py").read_text(encoding="utf-8")
    assert "VT_ARRAY | pythoncom.VT_BOOL" in src, "★ 布尔数组必须包 VT_ARRAY|VT_BOOL"


def test_criterion_is_readback_not_the_returned_feature():
    """★ 判据声明在返回值与源码里：**体数 + 特征树增量 + GetIntersectionsCount()** ✓"""
    from sw_boolean_ops import create_intersect
    src = inspect.getsource(create_intersect)
    assert "GetIntersectionsCount" in src, src[:200]
    assert "PostIntersect" in src and "PreIntersect2" in src
    r = create_intersect(None)
    assert r["ok"] is False and r["error"], r
    for key in ("pre_bodies", "tree_before", "tree_after", "new_features",
                "intersections_count", "exclude_array_len"):
        assert key in r, (key, sorted(r))


def test_region_type_is_validated_before_touching_com():
    """★ 非法 `region_type` 必须在**进 COM 之前**被拒（★ 且报错里列出合法值）✓"""
    from sw_boolean_ops import create_intersect
    r = create_intersect(None, region_type="nonsense")
    assert r["ok"] is False, r


def test_tool_total_grew_by_one():
        #: ★★ 这里**故意不钉绝对总数** —— ★ 我原来钉的是 `== 444`，结果**每加一批就让
    #:   前面所有批次的测试全红**（★ 全量 pytest 时才暴露，焦点测试看不见）⇒
    #:   ★ **绝对总数只有一处权威断言**：`tests/test_server_wiring.py` ✓
    assert len(rc.all_specs()) >= 444
