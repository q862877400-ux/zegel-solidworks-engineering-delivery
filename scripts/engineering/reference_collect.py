"""★ 从真实模型读出 `FaceInfo` / `EdgeInfo` —— 给 `reference_resolver` 供料。

## 为什么单独一个模块

`scripts/engineering/reference_resolver.py` 是**纯模块**（只 import math + dataclasses），
所以它的 18 条测试不连 SolidWorks 也能跑。那个纯度**要保住**。

而把面法向、面质心、边中点从 COM 读出来，必然要碰 COM。
⇒ 那部分放这里，`reference_resolver` 保持纯。

## 三源互证的来源（铁律 4）

| 成员 | `C:\\swapi` | 出厂反射 | 结论 |
|---|---|---|---|
| `IFace2.Normal` | `System.object`，Returns「Array of 3 doubles (i,j,k)」 | `Object get_Normal()` | ✅ 平面法向 |
| `IFace2.GetBox` | `System.object`，Returns「array of 6 doubles」 | `Object GetBox(Int32)` | ✅ 包围盒 |
| `IFace2.GetSurface` → `ISurface.IsPlane` | `System.bool IsPlane()` | `Boolean IsPlane()` | ✅ 是否平面 |
| 面质心 | **查不到** | **无** | ❌ **不存在** |
| `IEdge.GetStartVertex` / `GetEndVertex` → `IVertex.GetPoint` | 既有用法 | 既有用法 | ✅ 边中点（两点均值） |

## ★★ 两条必须写在代码里的近似

① **面质心是近似的**：API 没有面质心成员（三源确认），只能用 `GetBox()` 盒中心。
   官方 `GetBox` 的 Remarks 逐字：「The box dimensions enclose the face and are
   **typically close to the minimum possible size, but this is not guaranteed**」。
   ⇒ 平面矩形面上盒中心 == 质心；曲面/异形面上不等价。

② **`top_face` 因此有适用边界**：它的语义是「法向 +Y 且质心 Y 最大」。
   对首件的平面安装板成立；对曲面/异形件可能选错。
   ⇒ `resolve_semantic()` 返回里带 `centroid_is_approximate: True`，
     让调用方能看见这个前提，而不是悄悄用。

## 只读

全部是读操作（`Normal` / `GetBox` / `GetSurface` / `GetStartVertex` / `GetEndVertex` /
`GetPoint`），不改模型。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/reference_collect.py
# 定位:   specs/350-first-part-delivery T009 第②段 —— 把真实模型读成
#          FaceInfo / EdgeInfo，给 reference_resolver（纯模块）供料。
# 官方依据: IFace2.Normal / IFace2.GetBox / ISurface.IsPlane 三源互证
#           （C:\swapi + _raw/reflect/iface_sldworks.txt）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from engineering.reference_resolver import (  # noqa: E402
    DIRECTIONS,
    EdgeInfo,
    FaceInfo,
    ResolverError,
    resolve,
)

#: ★ `planar` 判不出来的面记这个 —— **不猜**成 True
PLANAR_UNKNOWN = False


def _numbers(value) -> list:
    """★ 把 COM 回来的数组（可能是 tuple/list/safearray）转成 float 列表。"""
    if value is None:
        return []
    try:
        return [float(v) for v in list(value)]
    except (TypeError, ValueError):
        return []


def collect_faces(model, *, body_index: int = 0) -> list:
    """★ 把体上的面读成 `list[FaceInfo]`。

    ★ 读不到的项**如实留空/标记**，不编：
      - `Normal` 读不到 ⇒ 法向留 `(0,0,1)` 且 `planar=False`（不让它被当成「朝上」）
      - `GetBox` 读不到 ⇒ 质心留 `(0,0,0)`；该面在 `near:` 锚点上会被算成很远
    """
    from sw_connect import get_com_member
    from sw_selection_spec import entities_on_body

    out: list = []
    faces = entities_on_body(model, "FACE", body_index=body_index)
    for i, face in enumerate(faces):
        info = {"index": i}

        normal = _numbers(get_com_member(face, "Normal"))
        if len(normal) >= 3:
            info["normal"] = (normal[0], normal[1], normal[2])
        else:
            #: ★ 读不到法向 ⇒ 不能假装朝 +Z
            info["normal"] = (0.0, 0.0, 1.0)
            info["normal_missing"] = True

        bbox = _numbers(get_com_member(face, "GetBox"))
        if len(bbox) >= 6:
            info["bbox"] = tuple(bbox[:6])
            #: ★ 面质心只能近似：盒中心。见模块头两条近似说明。
            info["centroid"] = (
                (bbox[0] + bbox[3]) / 2.0,
                (bbox[1] + bbox[4]) / 2.0,
                (bbox[2] + bbox[5]) / 2.0,
            )
        else:
            info["bbox"] = None
            info["centroid"] = (0.0, 0.0, 0.0)
            info["centroid_missing"] = True

        surface = get_com_member(face, "GetSurface")
        is_plane = get_com_member(surface, "IsPlane") if surface is not None else None
        info["planar"] = bool(is_plane) if is_plane is not None else PLANAR_UNKNOWN

        out.append(FaceInfo(**info))
    return out


def collect_edges(model, *, body_index: int = 0) -> list:
    """★ 把体上的边读成 `list[EdgeInfo]`。

    ★ 边中点是**精确的**：取 `GetStartVertex` / `GetEndVertex` 两点的均值，
      不需要新的 COM 成员（`entity_geometry` 已用同一对成员）。
    """
    from sw_connect import get_com_member
    from sw_selection_spec import entities_on_body

    out: list = []
    edges = entities_on_body(model, "EDGE", body_index=body_index)
    for i, edge in enumerate(edges):
        pts = []
        for member in ("GetStartVertex", "GetEndVertex"):
            v = get_com_member(edge, member)
            p = get_com_member(v, "GetPoint") if v is not None else None
            nums = _numbers(p)
            pts.append(nums[:3] if len(nums) >= 3 else None)
        info = {"index": i}
        if pts[0] and pts[1]:
            info["midpoint"] = tuple(
                (pts[0][k] + pts[1][k]) / 2.0 for k in range(3)
            )
        else:
            info["midpoint"] = (0.0, 0.0, 0.0)
            info["midpoint_missing"] = True
        out.append(EdgeInfo(**info))
    return out


def resolve_semantic(
    model, selector: str, kind: str, *, body_index: int = 0
) -> dict:
    """★ 把**语义选择器**解析成下标（真机版）。

    `kind` 取 `"FACE"` / `"EDGE"`。语义形态见 `reference_resolver.DIRECTIONS` /
    `top_face` / `near:<x>,<y>,<z>`。

    返回 `reference_resolver.resolve()` 的 dict，**另加**两个字段：

    | 字段 | 含义 |
    |---|---|
    | `centroid_is_approximate` | 面质心是盒中心近似（真机没有质心 API） |
    | `planar_required` | `top_face` 只在平面上有意义 |

    ★ 这是为了让调用方**看见前提**，而不是悄悄依赖一个近似值。
    """
    k = str(kind).upper()
    if k == "FACE":
        items = collect_faces(model, body_index=body_index)
        got = resolve(selector, items)
        got["centroid_is_approximate"] = True
        got["planar_required"] = selector == "top_face"
        return got
    if k == "EDGE":
        items = collect_edges(model, body_index=body_index)
        got = resolve(selector, [], edges=items)
        got["centroid_is_approximate"] = False
        got["planar_required"] = False
        return got
    #: ★ 用封闭码里的 REFERENCE_INVALID（输入本身不合法）——
    #:   ResolverError.CODES 只有三个码，不新造第四个
    raise ResolverError(
        "REFERENCE_INVALID",
        "★ 语义选择器只支持 FACE / EDGE，收到 %r" % (kind,),
    )


def is_semantic_selector(selector) -> bool:
    """★ 判断一个 `selection` 字符串是不是语义形态。

    ★ 被 `sw_selection_spec.resolve_entity()` 用来分流：
      语义形态 → 本模块解析；其余（`index:` / `__current_selection__` / COM 对象）
      → 走原有路径。
    """
    if not isinstance(selector, str):
        return False
    s = selector.strip()
    return s in DIRECTIONS or s == "top_face" or s.startswith("near:")


def limits() -> dict:
    """★ 如实报本模块的能力边界（供报告与文档引用）。"""
    return {
        "face_normal": "IFace2.Normal（三源互证）",
        "face_centroid": "近似：IFace2.GetBox 盒中心（API 无质心成员，三源确认）",
        "face_planar": "IFace2.GetSurface → ISurface.IsPlane（三源互证）",
        "edge_midpoint": "精确：GetStartVertex/GetEndVertex 两点均值",
        "top_face_caveat": (
            "只在平面上成立；曲面/异形面上盒中心 ≠ 质心 ⇒ 可能选错"
        ),
    }
