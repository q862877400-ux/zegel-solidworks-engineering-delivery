"""★ 契约测试：语义引用 → 稳定选择器（★ 本仓缺的那一层）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_reference_resolver.py
# 定位:   规格 `specs/334-reference-resolver` 的契约测试。
#           ★★★★★ 触发它的是 `mech-design` 自述「**我 30+ 轮踩坑的总答案**」的一篇：
#           `知识库/10-零件建模/ReferenceResolver语义引用与稳定选择器.md`
# 官方依据: 该篇（★ 只读借鉴**思想**）
#           ★ **借鉴来源**：`github.com/eyfel/mcp-server-solidworks`
#             （355★ · **AGPL-3.0**）⇒ ★★ **只读思想、绝不抄代码**（铁律 6）
# 许可:   本仓库 MIT。★ **无第三方代码引入**。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import reference_resolver as R                 # noqa: E402


#: ★ 一个 **40×40×20** 盒体的 6 个面（★ 纯数据 —— ★ 不碰 COM）
def _box_faces() -> list:
    return [
        R.FaceInfo(0, (0, 0, 1), (20, 20, 20)),      #: +Z 顶
        R.FaceInfo(1, (0, 0, -1), (20, 20, 0)),      #: -Z 底
        R.FaceInfo(2, (1, 0, 0), (40, 20, 10)),      #: +X
        R.FaceInfo(3, (-1, 0, 0), (0, 20, 10)),      #: -X
        R.FaceInfo(4, (0, 1, 0), (20, 40, 10)),      #: +Y
        R.FaceInfo(5, (0, -1, 0), (20, 0, 10)),      #: -Y
    ]


#: ══ ★★★ 主判据：语义 → index ═══════════════════════════════════════

def test_direction_selectors_resolve_to_indices() -> None:
    """★★★ **方向语义返回 index**（★ 不做坐标选取）。"""
    assert R.resolve("+z", _box_faces())["index"] == 0
    assert R.resolve("-z", _box_faces())["index"] == 1
    assert R.resolve("+x", _box_faces())["index"] == 2
    assert R.resolve("-x", _box_faces())["index"] == 3


def test_top_face_picks_max_centroid_along_axis() -> None:
    """★★★ **`top_face` = 法向 +Y >= 0.9 者取质心 Y 最大**（★ 逐字）。

    ★★ 为什么这样判（★ 逐字）：★ 「用**几何事实**（法向 + 质心位置），
      **而不是「我以为的拉伸方向」** ⇒ ★ **不会被方向怪癖骗到**」。
    """
    f = R.resolve("top_face", _box_faces())
    assert f["index"] == 4
    #: ★ 判据字符串要**说明判法**（★ 法向 + 质心）
    assert "法向" in f["by"] and "质心" in f["by"]


def test_resolver_returns_index_not_coordinates() -> None:
    """★★★ **返回的是 `index`** —— ★ 让上层工具**直接选**。

    ★★ 判据（★ 逐字）：★ 「returns face/edge **INDICES** that
      `create_sketch(on_face, face_index)` / `add_edge_feature(edge_indices)`
      select directly — **no fragile coordinate pick**」。
    """
    r = R.resolve("+z", _box_faces())
    assert "index" in r and isinstance(r["index"], int)
    #: ★ 而**不**返回坐标
    assert "point" not in r and "xyz" not in r


#: ══ ★★ 几何锚点（★ 跨重建稳定）══════════════════════════════════════

def test_face_anchor_hits_the_plane() -> None:
    """★★ **面锚点：平面包含匹配**（★ 逐字）。"""
    r = R.resolve("near:20,20,20", _box_faces())
    assert r["kind"] == "face" and r["index"] == 0


def test_face_anchor_unresolved_when_off_any_plane() -> None:
    """★★ **点不在任何面上 ⇒ `REFERENCE_UNRESOLVED`**。

    ★★ 判据（★ 逐字）：★ 「**找不到 ⇒ 必须报，不要退化到坐标选取**」。
    """
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("near:20,20,10", _box_faces())     #: ★ 盒体中心
    assert ei.value.code == "REFERENCE_UNRESOLVED"


def test_edge_anchor_needs_exactly_one_midpoint() -> None:
    """★★ **边锚点：容差球内必须恰好一条**（★ 逐字）。"""
    edges = [R.EdgeInfo(0, (0, 0, 0)), R.EdgeInfo(1, (40, 0, 0)),
             R.EdgeInfo(2, (40, 40, 0))]
    r = R.resolve("near:40,0,0", _box_faces(), edges=edges)
    assert r["kind"] == "edge" and r["index"] == 1


def test_edge_anchor_ambiguous_when_two_in_tolerance() -> None:
    """★★★ **两条边在容差内 ⇒ `REFERENCE_AMBIGUOUS`**。

    ★★ 判据（★ 逐字）：★ 「**多个候选 ⇒ 必须由上层消歧（不要猜）**」。
    """
    #: ★ 故意让两条边的中点相距 0.001mm（★ 都在默认容差 1e-3 内）
    edges = [R.EdgeInfo(0, (10.0, 0.0, 0.0)),
             R.EdgeInfo(1, (10.0, 0.0005, 0.0))]
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("near:10,0,0", _box_faces(), edges=edges)
    assert ei.value.code == "REFERENCE_AMBIGUOUS"
    assert "不要猜" in ei.value.detail


def test_face_anchor_ambiguous_when_two_distinct_planes() -> None:
    """★★★ **两个【不同】平面都匹配 ⇒ `REFERENCE_AMBIGUOUS`**（★ 逐字）。

    ★ 而**共面的面**之间**不算歧义**（★ 逐字：「共面面之间对 up-to-surface
      是等价的 ⇒ 取最近的代表点」）。
    """
    #: ★ 两个**不同法向**的面都过同一点 ⇒ 歧义
    faces = [R.FaceInfo(0, (0, 0, 1), (0, 0, 0)),
             R.FaceInfo(1, (0, 1, 0), (0, 0, 0))]
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("near:0,0,0", faces)
    assert ei.value.code == "REFERENCE_AMBIGUOUS"


def test_coplanar_faces_are_not_ambiguous() -> None:
    """★ **共面的多个面不算歧义** —— ★ 取**最近**的代表点。"""
    faces = [R.FaceInfo(0, (0, 0, 1), (0, 0, 0)),
             R.FaceInfo(1, (0, 0, 1), (5, 5, 0))]
    r = R.resolve("near:1,1,0", faces)
    assert r["index"] in (0, 1)          #: ★ 取最近的，不报歧义


#: ══ ★★★ 三个诚实限制 ═══════════════════════════════════════════════

def test_limitations_are_declared() -> None:
    """★★★ **三条限制必须如实回**（★ 逐字承 `mech-design`）。

    ★★ 第 1 条最关键：**索引不跨编辑保持** ⇒
      ★ **改完模型后，之前算出来的 index 全部作废，必须重查**。
    """
    lims = R.limitations()
    assert len(lims) == 3
    blob = " ".join(lims)
    assert "不跨编辑" in blob, "★ 缺「索引不跨编辑保持」"
    assert "hint" in blob, "★ 缺「hint 不被读」"
    assert "单体" in blob, "★ 缺「v0 只支持单体」"


def test_index_not_durable_is_stated_verbatim() -> None:
    """★ 第 1 条的**逐字**英文原文在（★ 可核）。"""
    blob = " ".join(R.limitations())
    assert "NOT durable across edits" in blob
    assert "fresh-doc replay" in blob


#: ══ 错误路径 ═════════════════════════════════════════════════════════

def test_unknown_selector_raises_invalid() -> None:
    """★ 未知选择器 ⇒ `REFERENCE_INVALID`（★ 列出合法值）。"""
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("nonsense", _box_faces())
    assert ei.value.code == "REFERENCE_INVALID"


def test_bad_near_syntax_raises_invalid() -> None:
    """★ `near:` 参数个数不对 ⇒ `REFERENCE_INVALID`。"""
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("near:1,2", _box_faces())
    assert ei.value.code == "REFERENCE_INVALID"


def test_only_three_error_codes() -> None:
    """★★ **只有三个封闭错误码**（★ 借鉴来源的做法 —— ★ 语义明确）。"""
    assert R.ResolverError.CODES == (
        "REFERENCE_AMBIGUOUS", "REFERENCE_UNRESOLVED", "REFERENCE_INVALID")


def test_no_faces_raises_unresolved() -> None:
    """★ 空面表 ⇒ `REFERENCE_UNRESOLVED`（★ 不静默回空）。"""
    with pytest.raises(R.ResolverError) as ei:
        R.resolve("+z", [])
    assert ei.value.code == "REFERENCE_UNRESOLVED"


#: ══ 元信息 ═══════════════════════════════════════════════════════════

def test_selectors_listed() -> None:
    """★ 语义清单可查（★ 供工具层暴露）。"""
    s = R.selectors()
    assert len(s["directions"]) == 6
    assert "top_face" in s["semantic"]
    assert any("near:" in a for a in s["anchors"])


def test_six_directions_match_existing_tool() -> None:
    """★ 六个方向**与既有 `solidworks_select_face_selector` 对齐**
    （★ `+x`/`-x`/`+y`/`-y`/`+z`/`-z`）。
    """
    assert set(R.DIRECTIONS) == {"+x", "-x", "+y", "-y", "+z", "-z"}


def test_doc_exists() -> None:
    """★ 借鉴文档在（★ 记录思想出处与 AGPL 只读）。"""
    p = (ROOT / "specs" / "332-known-facts-triage"
         / "reference-resolver.md")
    assert p.is_file()
    t = p.read_text(encoding="utf-8")
    for k in ("AGPL", "只读思想", "top_face", "不跨编辑"):
        assert k in t, "★ 文档缺 `%s`" % k
