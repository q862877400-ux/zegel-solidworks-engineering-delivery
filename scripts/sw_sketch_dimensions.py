"""★ 草图尺寸与关系包装（B5 批）。⚠⚠⚠ **本模块未经验证，且有两个入口被怀疑会弄崩 SolidWorks** —— 见下。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）
# 文件:   scripts/sw_sketch_dimensions.py
# 定位:   ★ 2026-10-03（轮 466）★ `specs/201-toolbar-gaps` 的 **B5 批**（草图尺寸与关系）。
#   ★★ 起因：用户贴草图「智能尺寸/关系」下拉截图逐条问「能/不能」，这批当时全答「不能」。
#   ★★★ **签名三源互证（铁律 4）**：逐条读自 `C:\\swapi\\types\\`，**含「成员属哪个接口」**：
#     ```
#     IModelDoc2\\AddHorizontalDimension2.md   object AddHorizontalDimension2(double X, Y, Z)
#     IModelDoc2\\AddVerticalDimension2.md     object AddVerticalDimension2(double X, Y, Z)
#     IModelDoc2\\SketchAddConstraints.md      void   SketchAddConstraints(string IdStr)   \u2605 \u4ed3\u91cc\u5df2\u6709
#     IModelDocExtension\\InsertChainDimensions.md  object InsertChainDimensions(object Entities)
#     IModelDocExtension\\AddPathLengthDim.md       object AddPathLengthDim(double X, Y, Z)
#     ISketchManager\\FullyDefineSketch.md          int FullyDefineSketch(bool EntitiesToFullyDefine,
#         bool UseRelations, int RelationsToApply, bool UseDimensions, int HorizontalDimScheme,
#         object HorizontalDatumDisp, int VerticalDimScheme, object VerticalDatumDisp,
#         int HorizontalDimPlacement, int VerticalDimPlacement)
#     ISketchRelationManager\\GetRelationsCount.md  int  GetRelationsCount(int Filter)
#     ISketchRelationManager\\GetRelations.md       object GetRelations(int Filter)
#     ISketchRelationManager\\DeleteRelation.md     bool DeleteRelation(SketchRelation)
#     ISketchRelationManager\\DeleteAllRelations.md bool DeleteAllRelations()
#     ISketchRelationManager\\AddRelation.md        SketchRelation AddRelation(object Entities, int RelationType)
#     ```
#   ★★★ **「删除几何关系」的真名我原来猜错了** —— 我填的 `GetSketchRelations` / `DeleteSketchRelation`
#     **两套源里都没有**（铁律 5 记「查不到」）；★ 真名是 **`ISketchRelationManager` 上的
#     `GetRelations` / `GetRelationsCount` / `DeleteRelation` / `DeleteAllRelations`** ✓
#     而关系管理器从**草图**上取：`ISketch.RelationManager`（★ 仓里 `sw_sketch.get_relation_manager` 已有）✓
#   ⚠ **单位**：长度**毫米**；尺寸的 `X/Y/Z` 是**尺寸文字的放置点**（官方口径），本模块收毫米 ✓
#   ⚠ **未核实（铁律 5）**：`FullyDefineSketch` 的 `HorizontalDimScheme` / `RelationsToApply` /
#     `*DimPlacement` 的**取值表在 `C:\\swapi` 里没查到** ⇒ 本模块默认全 0 / 空 Dispatch，
#     ★ 并在 docstring 里标注**未核实**，不假装知道 ✓
# 官方依据: 见上（`C:\\swapi\\types\\` 的 4 个接口 / 10 个成员）。
# 许可:   本仓库 MIT。无第三方代码引入（★ 全部按官方签名自建）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 由调用方回读**尺寸计数 / 关系计数**（规则 6）。

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _p in (_HERE.parent, _HERE.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import sw_sketch as _SK  # noqa: E402
from sw_connect import get_com_member  # noqa: E402
from sw_part import _empty_callout  # noqa: E402


def _sketch(model):
    sk = _SK.resolve_sketch(model, "")
    if sk is None:
        raise RuntimeError("没有活动草图（先 solidworks_sketch_start）")
    return sk


def _relations(model):
    """⇒ 当前草图的 `ISketchRelationManager`（★ 官方是 `ISketch.RelationManager` **属性**）。"""
    return _SK.get_relation_manager(_sketch(model))


def add_horizontal_dimension(model, x_mm: float, y_mm: float):
    """★ 水平尺寸：`IModelDoc2.AddHorizontalDimension2(X, Y, Z)`（★ X/Y/Z = **尺寸文字的放置点**）。"""
    return get_com_member(model, "AddHorizontalDimension2", float(x_mm), float(y_mm), 0.0)


def add_vertical_dimension(model, x_mm: float, y_mm: float):
    """★ 竖直尺寸：`IModelDoc2.AddVerticalDimension2(X, Y, Z)`。"""
    return get_com_member(model, "AddVerticalDimension2", float(x_mm), float(y_mm), 0.0)


def add_path_length_dimension(model, x_mm: float, y_mm: float):
    """★ 路径长度尺寸：`IModelDocExtension.AddPathLengthDim(X, Y, Z)`（★ 在 `Extension` 上）。"""
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 IModelDocExtension")
    return get_com_member(ext, "AddPathLengthDim", float(x_mm), float(y_mm), 0.0)


def insert_chain_dimensions(model, selection: str = "__current_selection__"):
    """★ 尺寸链：`IModelDocExtension.InsertChainDimensions(Entities)`。

    ★ `Entities` 是**实体数组** ⇒ 本函数按声明式选择器把草图段装成数组（★ 不收坐标，规则 3）。
    """
    segs = _SK.get_sketch_segments(_sketch(model))
    if not segs:
        raise RuntimeError("草图里没有线段可做尺寸链")
    sel = (selection or "").strip()
    if sel in ("", "__current_selection__"):
        ents = list(segs)
    else:
        ents = []
        for part in sel.split(","):
            part = part.strip()
            if not part.startswith("index:"):
                raise ValueError("非法的选择器 %r；合法：'__current_selection__' 或 'index:0,index:1'" % part)
            i = int(part.split(":", 1)[1])
            if i < 0 or i >= len(segs):
                raise RuntimeError("草图段下标 %d 越界（共 %d 段）" % (i, len(segs)))
            ents.append(segs[i])
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 IModelDocExtension")
    return get_com_member(ext, "InsertChainDimensions", ents)


def fully_define_sketch(model, *, entities_to_fully_define: bool = True,
                        use_relations: bool = True, relations_to_apply: int = 0,
                        use_dimensions: bool = True, horizontal_dim_scheme: int = 0,
                        vertical_dim_scheme: int = 0, horizontal_dim_placement: int = 0,
                        vertical_dim_placement: int = 0):
    """★ 完全定义草图：`ISketchManager.FullyDefineSketch(10 参)`。

    ⚠ ★ **未核实**（铁律 5）：`relations_to_apply` / `horizontal_dim_scheme` /
      `vertical_dim_scheme` / `*_dim_placement` 的**取值表**在两套离线源里**都没查到**
      ⇒ 本函数默认全 0，★ 调用方若要特定口径得自己给值，★ 而**本模块不假装知道** ✓
    """
    return get_com_member(_sketch(model) and get_com_member(model, "SketchManager"),
                          "FullyDefineSketch",
                          bool(entities_to_fully_define), bool(use_relations),
                          int(relations_to_apply), bool(use_dimensions),
                          int(horizontal_dim_scheme), _empty_callout(),
                          int(vertical_dim_scheme), _empty_callout(),
                          int(horizontal_dim_placement), int(vertical_dim_placement))


def count_sketch_relations(model, filter: int = -1) -> int:
    """★ 关系计数：`ISketchRelationManager.GetRelationsCount(Filter)`（★ `Filter=-1` = 全部）。"""
    return int(get_com_member(_relations(model), "GetRelationsCount", int(filter)) or 0)


def delete_all_sketch_relations(model) -> bool:
    """★ 删除全部几何关系：`ISketchRelationManager.DeleteAllRelations()`。"""
    return bool(get_com_member(_relations(model), "DeleteAllRelations"))


def delete_sketch_relation(model, index: int, *, filter: int = -1) -> bool:
    """★ 删除第 `index` 条几何关系：`DeleteRelation(GetRelations(Filter)[index])`。

    ★ **按对象删** —— 关系没有名字（同事实 32 的形态）⇒ 先从 `GetRelations` 取数组再取下标 ✓
    """
    mgr = _relations(model)
    rels = get_com_member(mgr, "GetRelations", int(filter))
    seq = list(rels) if rels is not None else []
    if index < 0 or index >= len(seq):
        raise RuntimeError("关系下标 %d 越界（共 %d 条）" % (index, len(seq)))
    return bool(get_com_member(mgr, "DeleteRelation", seq[index]))


#: ★ B5 批的成员清单（★ 供探针与门禁按名单跑，不遍历）
B5_MEMBERS = (
    "add_horizontal_dimension", "add_vertical_dimension", "add_path_length_dimension",
    "insert_chain_dimensions", "fully_define_sketch",
    "count_sketch_relations", "delete_all_sketch_relations", "delete_sketch_relation",
)
