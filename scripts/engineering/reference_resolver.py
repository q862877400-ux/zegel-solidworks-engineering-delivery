"""★ 语义引用 → 稳定选择器（★ 本仓缺的那一层）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/reference_resolver.py
# 定位:   规格 `specs/334-reference-resolver` —— **本仓缺的那一层**。★★★★★ 触发它的是
#           2026-10-14 全自动挖掘，`mech-design` 的一篇  自述「**我 30+ 轮踩坑的总答案**
#           」：  `知识库/10-零件建模/ReferenceResolver语义引用与稳定选择器.md`
#
#           ★★★ 它点破的结构性缺口（★ 逐字）：
#           > 「它的工具接口设计**与我一致**（`face_index` / `up_to_face_index` /
#           >   `edge_indices`），**区别在于它在上层多了一个 resolver
#           >   把语义翻译成索引**。
#           >   ⇒ ★★ **我缺的不是工具参数，是上面那一层「谁来算这个 index」**。」
#
#           ★★ 本仓已有 `solidworks_select_face_selector`（`+z`/`-z`），
#             ★ 而那**正是这一层的雏形** —— ★ 但**只有 6 个固定方向**；
#             ★ 本模块把它扩到**任意语义 + 几何锚点**。
#
# 官方依据: ① `~/.agents/skills/mech-design/知识库/10-零件建模/   ReferenceResolver语义
#           引用与稳定选择器.md`（★ 只读借鉴**思想**）② ★ **借鉴来源**：`github.com/eyfe
#           l/mcp-server-solidworks`   （355★ · **AGPL-3.0**）⇒ ★★ **只读思想、绝不抄代
#           码**   （★ 本仓铁律 6：AGPL 只读思想，不抄代码、不抄文本）③ `scripts/sw_sele
#           ction_spec.py`（★ 本仓既有的声明式选择）
# 许可:   本仓库 MIT。★ **无第三方代码引入**（★ 本模块按**思想**自建，
#           ★ 代码一行未抄；★ 来源块已注明借鉴出处与其 AGPL 许可）。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ **纯计算**（★ 不碰 COM）；★ 真机派发由调用方做。
# -----------------------------------------------------------------------------
from __future__ import annotations

import math
from dataclasses import dataclass

#: ★ 平面包含容差（毫米）—— ★ 借鉴来源用 `_PLANE_TOL`
PLANE_TOL_MM = 1e-3
#: ★ 边中点容差（毫米）—— ★ 借鉴来源用 `_EDGE_TOL`
EDGE_TOL_MM = 1e-3


class ResolverError(Exception):
    """★ 解析失败（★ 带**封闭码** —— ★ 借鉴来源的做法）。

    ★★ 判据：★ 错误码**只有三个**，★ 且**语义明确**：
      `REFERENCE_AMBIGUOUS`  ⇒ ★ **多个候选 ⇒ 必须由上层消歧（不要猜）**
      `REFERENCE_UNRESOLVED` ⇒ ★ **找不到 ⇒ 必须报，不要退化到坐标选取**
      `REFERENCE_INVALID`    ⇒ ★ 输入本身不合法
    """

    CODES = ("REFERENCE_AMBIGUOUS", "REFERENCE_UNRESOLVED", "REFERENCE_INVALID")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法解析码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、B-Rep 面/边的**几何描述**（★ 纯数据 —— 由调用方从 COM 读出来）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class FaceInfo:
    """★ 一个面的几何事实（★ **只用量测值** —— ★ 不存「我以为的方向」）。"""

    index: int
    #: ★ 面法向（单位向量）
    normal: tuple = (0.0, 0.0, 1.0)
    #: ★ 面质心
    centroid: tuple = (0.0, 0.0, 0.0)
    #: ★ 是否平面（★ `top_face` 只在平面上找）
    planar: bool = True
    #: ★ 面的包围盒（可选）
    bbox: tuple | None = None


@dataclass
class EdgeInfo:
    """★ 一条边的几何事实。"""

    index: int
    #: ★ 边的**中点**（★ 锚点匹配用它）
    midpoint: tuple = (0.0, 0.0, 0.0)


#: ══════════════════════════════════════════════════════════════════════
# 二、语义选择器（★ 确定性 —— ★ 不依赖建模方向）
#: ══════════════════════════════════════════════════════════════════════


def _dot(a: tuple, b: tuple) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(v: tuple) -> float:
    return math.sqrt(sum(x * x for x in v))


def _dist(a: tuple, b: tuple) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def top_face(
    faces: list, *, axis: tuple = (0.0, 1.0, 0.0), min_dot: float = 0.9
) -> FaceInfo:
    """★★★ **`top_face`** —— ★ 语义选择器（★ 确定性）。

    ★★★ 判据（★ 逐字承 `mech-design`）：
      「**PLANAR 面中法向 `+Y >= 0.9` 者，取质心 Y 最大的那个**」

    ★★★ **为什么这样判**（★ 逐字）：
      「它用**几何事实**（法向 + 质心位置），
       **而不是「我以为的拉伸方向」** ⇒ ★ **不会被 SolidWorks 的方向怪癖骗到**」
    """
    cands = [f for f in faces if f.planar and _dot(f.normal, axis) >= min_dot]
    if not cands:
        raise ResolverError(
            "REFERENCE_UNRESOLVED",
            "★ 没有平面的法向与 %s 的点积 >= %.2f（★ 共 %d 个面）"
            % (axis, min_dot, len(faces)),
        )
    #: ★★ 取**质心沿轴最大**的那个（★ 不是「第一个」—— ★ 顺序不稳定）
    return max(cands, key=lambda f: _dot(f.centroid, axis))


def faces_by_normal(faces: list, axis: tuple, *, min_dot: float = 0.9) -> list:
    """★ 法向匹配某个方向的所有面（★ 供 `REFERENCE_AMBIGUOUS` 判定用）。"""
    return [f for f in faces if f.planar and _dot(f.normal, axis) >= min_dot]


def face_near(faces: list, near: tuple, *, tol_mm: float = PLANE_TOL_MM) -> FaceInfo:
    """★★ **几何锚点：面**（★ 跨重建稳定的做法 —— ★ 这是核心）。

    ★★ 判据（★ 逐字）：
      「**平面包含匹配** —— 法向与 `near` 一致、且 `near` 到该平面的距离
        <= `_PLANE_TOL`」
      ★ **若多个【不同】平面都匹配 ⇒ `REFERENCE_AMBIGUOUS`**」
    """
    hits = []
    for f in faces:
        if not f.planar:
            continue
        #: ★ 点到平面距离 = |(near - centroid) · normal|
        d = abs(_dot(tuple(a - b for a, b in zip(near, f.centroid)), f.normal))
        if d <= tol_mm:
            hits.append((d, f))
    if not hits:
        raise ResolverError(
            "REFERENCE_UNRESOLVED",
            "★ `near=%s` 不在任何平面 %.4gmm 内" % (near, tol_mm),
        )
    #: ★★ **多个不同的平面 ⇒ 歧义**（★ 共面的等价 ⇒ 取最近的）
    planes = {f.normal for _, f in hits}
    if len(planes) > 1:
        raise ResolverError(
            "REFERENCE_AMBIGUOUS",
            "★ `near=%s` 落在 **%d 个不同平面**上（★ 法向 %s）"
            "⇒ ★ **必须由上层消歧，不要猜**" % (near, len(planes), sorted(planes)),
        )
    return min(hits, key=lambda x: x[0])[1]


def edge_near(edges: list, near: tuple, *, tol_mm: float = EDGE_TOL_MM) -> EdgeInfo:
    """★★ **几何锚点：边**（★ 跨重建稳定）。

    ★★ 判据（★ 逐字）：
      「**容差球内最近中点匹配** —— 必须【**恰好一条**】边中点在
        `_EDGE_TOL` 内。★ 否则 ⇒ `REFERENCE_UNRESOLVED` / `REFERENCE_AMBIGUOUS`」
    """
    hits = [(d, e) for e in edges if (d := _dist(e.midpoint, near)) <= tol_mm]
    if not hits:
        raise ResolverError(
            "REFERENCE_UNRESOLVED",
            "★ `near=%s` 的 %.4gmm 内**没有边的中点**" % (near, tol_mm),
        )
    if len(hits) > 1:
        raise ResolverError(
            "REFERENCE_AMBIGUOUS",
            "★ `near=%s` 的 %.4gmm 内有 **%d 条边**（★ 索引 %s）"
            "⇒ ★ **必须由上层消歧，不要猜**"
            % (near, tol_mm, len(hits), sorted(e.index for _, e in hits)),
        )
    return hits[0][1]


#: ══════════════════════════════════════════════════════════════════════
# 三、★★★ 三个必须知道的诚实限制（★ 逐字承 `mech-design`）
#: ══════════════════════════════════════════════════════════════════════

LIMITATIONS = (
    "★★★ **索引不跨编辑保持** —— ★ 逐字：「Anchors are exact for **fresh-doc "
    "replay**… but **NOT durable across edits**」"
    "⇒ ★ **改完模型后，之前算出来的 face/edge index 全部作废，必须重查**",
    "★★ **不要用 `hint`** —— ★ 逐字：「The optional `hint` field is "
    "**NEVER read** here」⇒ ★ 不要指望它",
    "★ **v0 只支持单体** —— ★ 逐字：「v0 has a single body, so 'the top face of "
    "node n' == the body's top face」",
)


def limitations() -> list:
    """★ 如实回**三条限制**（★ 逐字）—— ★ 不隐藏。"""
    return list(LIMITATIONS)


#: ══════════════════════════════════════════════════════════════════════
# 四、★ 语义表（★ 可直接用的选择器）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **六个方向语义**（★ 与 `solidworks_select_face_selector` 的 `+z`/`-z` 对齐）
DIRECTIONS: dict[str, tuple] = {
    "+x": (1.0, 0.0, 0.0),
    "-x": (-1.0, 0.0, 0.0),
    "+y": (0.0, 1.0, 0.0),
    "-y": (0.0, -1.0, 0.0),
    "+z": (0.0, 0.0, 1.0),
    "-z": (0.0, 0.0, -1.0),
}


def resolve(
    selector: str, faces: list, *, edges: list | None = None, near: tuple | None = None
) -> dict:
    """★★★ **主入口**：把**语义引用**翻成 **index**。

    ★★ 支持的形态：
      · `+z` / `-z` / `+x` …  ⇒ ★ 方向语义（★ 与既有工具一致）
      · `top_face`            ⇒ ★ 法向 +Y、质心 Y 最大
      · `near:<x>,<y>,<z>`    ⇒ ★ **几何锚点**（★ 跨重建稳定）

    ★★★ **判据**（★ 逐字）：★ 返回的是 **index**，
      ★ 让 `create_sketch(on_face, face_index)` / `extrude_feature(up_to_face_index)`
      / `add_edge_feature(edge_indices)` **直接选** —— ★ **不做脆弱的坐标选取**。
    """
    if selector in DIRECTIONS:
        f = top_face(faces, axis=DIRECTIONS[selector])
        return {
            "kind": "face",
            "index": f.index,
            "selector": selector,
            "by": "方向语义（法向 + 质心，★ 几何事实）",
        }
    if selector == "top_face":
        f = top_face(faces)
        return {
            "kind": "face",
            "index": f.index,
            "selector": selector,
            "by": "top_face（法向 +Y >= 0.9，取质心 Y 最大）",
        }
    if selector.startswith("near:"):
        if near is None:
            body = selector.split(":", 1)[1]
            parts = body.split(",")
            if len(parts) != 3:
                raise ResolverError(
                    "REFERENCE_INVALID", "★ `near:` 要三个数（★ 实得 %r）" % body
                )
            near = tuple(float(p) for p in parts)
        if edges:
            e = edge_near(edges, near)
            return {
                "kind": "edge",
                "index": e.index,
                "selector": selector,
                "by": "几何锚点（容差球内**恰好一条**边中点）",
            }
        f = face_near(faces, near)
        return {
            "kind": "face",
            "index": f.index,
            "selector": selector,
            "by": "几何锚点（平面包含匹配）",
        }
    raise ResolverError(
        "REFERENCE_INVALID",
        "★ 未知选择器 `%s`（有：%s · top_face · near:<x,y,z>）"
        % (selector, sorted(DIRECTIONS)),
    )


def selectors() -> dict:
    """★ **有哪些语义**（★ 供工具层暴露）。"""
    return {
        "directions": sorted(DIRECTIONS),
        "semantic": ["top_face"],
        "anchors": ["near:<x>,<y>,<z>"],
        "★": "★ 前两类**确定性**（几何事实）；★ 第三类**跨重建稳定**（锚点）",
    }
