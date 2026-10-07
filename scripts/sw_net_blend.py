"""★ 边界凸台/边界曲面（官方 `IFeatureManager::InsertNetBlend`）的报告式包装。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（照官方签名自建；官方依据见下）
# 文件:   `specs/219-user-coverage-100/` 的 **T-219-04**
# 定位:   ★ 补两个用户可感知功能的**真缺口**：★ 特征/边界凸台 · 曲面/边界曲面 ✓
# 官方依据（★ 三样逐字读过 —— 铁律 4 第 0 步）:
#   · 签名:   `C:\swapi\types\IFeatureManager\InsertNetBlend.md`
#             `Feature InsertNetBlend(short Type, short NCurvesDir1, short NCurvesDir2,
#              bool HasCenterline, double TessTolFactor, bool WantsSolid, bool MergeBody,
#              bool FeatureScope, bool AutoSelect, bool Thin, double Thickness1,
#              double Thickness2, bool ReverseThickness, short ThinSolidType,
#              bool UseSharedThickness, bool CapEnds, double EndThickness, bool AutoFillet,
#              double FilletRadius, bool ForceNonRational)`
#   · Type 枚举（官方逐字）: 0 = Base · **1 = Boss** · **2 = Surface** · 3 = Cut
#   · 前置数据: `SetNetBlendDirectionData(short Direction, short InfluenceType,
#              short TrimCurves, bool BlendClosed, bool SplitSurfaces)`
#              —— Direction: 0 = Direction 1 / 1 = Direction 2
#              —— InfluenceType: 0 = Global / 1 = To Next Curve / 2 = To Next Sharp / 3 = To Next Edge
#              —— TrimCurves: 0 = False to trim / 1 = True to trim
#              —— BlendClosed: true 闭合 · SplitSurfaces: Not used
#   · ★★ **调用序（★ 只有官方示例给得出）**:
#     `AI Solidworks\官方文档\…\Insert_Boundary_Feature_Example_VB.htm` 第 67–74 行逐行读出：
#       ① `ClearSelection2 True`
#       ② `SelectByID2("", "FACE", x1,y1,z1, False, 0, Nothing, 0)` ← 第 1 个面
#          `SelectByID2("", "FACE", x2,y2,z2, True,  0, Nothing, 0)` ← 第 2 个面（Append）
#       ③ `SetNetBlendCurveData 0, 0, 0, 0, 1, True` / `… 0, 1, 0, <弧度>, 1, True`
#       ④ `SetNetBlendDirectionData 0, 32, 0, False, False` / `… 1, 32, 0, False, False`
#       ⑤ `swFeature = swFeatureMgr.InsertNetBlend(1, 2, 0, False, 0.0001, …)`
#   ★ 单位: 官方示例的角度 `0.26179938779915` ≈ **15°** ⇒ ★ 该参数是**弧度** ✓
#   ★ 选择: 面**没有可用的名字**（本仓事实 32）⇒ 只能**按面上的点**选 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   ★ 标注 `stitched` —— ★★ **本包装尚未真机验证**（红线⑥：`level` 只按真机证据变）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math

#: ★ 官方 `InsertNetBlend` 的 `Type` 枚举（官方逐字）
BLEND_TYPE = {"base": 0, "boss": 1, "surface": 2, "cut": 3}

#: ★ 官方 `SetNetBlendDirectionData` 的 `InfluenceType` 枚举（官方逐字）
INFLUENCE_TYPE = {"global": 0, "to_next_curve": 1, "to_next_sharp": 2, "to_next_edge": 3}

#: ★ 毫米 → 米（本仓事实 2：COM 侧是米，工具面对用户是毫米）
_MM = 1.0 / 1000.0


def _select_face_by_index(model, face_index: int, append: bool):
    """★ 按**面序号**选一个面（★ 声明式：序号不是坐标 ⇒ 规则 3 合规）✓
    ★ 形态照 `scripts/sw_part.py::select_face_by_index_mark1`（2026-10-06 真机验过的那个：
      ★ 用 `IFace2::GetBox()` 取面上一点 ⇒ `SelectByID2("", "FACE", x,y,z, append, 0, callout, 0)`）✓
    """
    #: ★★ 形态**照本仓真机验证过的** `sw_part.select_face_by_index_mark1`（规格 216 T-216-06b）：
    #:   ★ **取面走 `sw_selection_spec.entities_on_body(model, "FACE", body_index=0)`** ✓
    #:   ★ **取盒走 `get_com_member(face, "GetBox")`** ✓
    #: ★★ 为什么不能直接点属性：★ 2026-10-07 真机实测（`tools/probe_spec220_member_shape.py`）
    #:   ★ `body.GetFaces` 报逐字「**没有这个成员**」✗ ⇒ ★ 迟到绑定的成员要走 `get_com_member` ✓
    import sw_selection_spec as _SS
    import sw_part                                                                  # 同目录模块

    faces = list(_SS.entities_on_body(model, "FACE", body_index=0) or [])
    if not faces or face_index < 0 or face_index >= len(faces):
        raise RuntimeError("面序号越界：face_index=%r，本体共 %d 个面"
                           % (face_index, len(faces) if faces else 0))
    face = faces[face_index]
    box = list(sw_part.get_com_member(face, "GetBox") or [])
    if len(box) < 6:
        raise RuntimeError("★ 取面上失败：`IFace2.GetBox()` 回了 %r（★ 这是前置未成立，"
                           "★ 与「边界特征建不出来」是两件事）" % (box,))
    cx = (box[0] + box[3]) / 2.0
    cy = (box[1] + box[4]) / 2.0
    cz = (box[2] + box[5]) / 2.0
    #: ★★ 2026-10-07（规格 220 T-220-01）：★ **mark 从 0 改成 1** ——
    #:   ★ 依据本仓**真机验证过**的先例（`sw_part.select_face_by_index_mark1` 的 docstring 逐字）：
    #:   ★「先按面上的点 mark=0 选一次 ⇒ ClearSelection2(True) ⇒ ★★ 再 mark=1 选一次」
    #:   ★ 且「传 **mark=0** 时 `InsertDome` 报 **0x8002000F**」⇒ ★ 这类特征要的是 **mark=1** ✓
    #:   ★ 真机读数（第 5 轮）：mark=0 时第 1 次选面回读计数 **0** ✗（第 2 次 1）
    ok = model.Extension.SelectByID2("", "FACE", cx, cy, cz, bool(append), 0,
                                     sw_part._empty_callout(), 1)
    cnt = model.SelectionManager.GetSelectedObjectCount2(-1)                         # ★ 事实 8：布尔不可信
    return {"ok": bool(ok), "selection_count": cnt, "point": [cx, cy, cz]}


def insert_net_blend_report(
    model,
    *,
    face_index_1: int = 0,
    face_index_2: int = 1,
    blend_type: int = 1,
    n_curves_dir1: int = 1,
    n_curves_dir2: int = 2,   #: ★ 官方示例逐字 `InsertNetBlend 1, 2, 0, …`
    influence_type: int = 0,
    trim_curves: bool = False,
    blend_closed: bool = False,
    tangency_deg: float = 15.0,
    merge_body: bool = True,
    thickness1_mm: float = 0.0,
    thickness2_mm: float = 0.0,
) -> dict:
    """★ 建一个边界特征（凸台 `blend_type=1` / 曲面 `blend_type=2`）并**回读**。

    ★★ **判据（回读，不是看返回值）**：★ 特征树里**新增了一个特征** ⇒ `ok=True`；
    ★ 官方 `Returns` 的语义（★ 该族的两种情形）★ 若回 `None` 则**报错并指向可能的因** ✓
    ⚠ ★ **本包装尚未真机验证**（★ 台账标 `stitched`）✓
    """
    if blend_type not in (0, 1, 2, 3):
        raise ValueError("blend_type 只接受 0/1/2/3（官方 Type：0=Base·1=Boss·2=Surface·3=Cut）")
    if influence_type not in (0, 1, 2, 3):
        raise ValueError("influence_type 只接受 0/1/2/3（官方：0=Global·1=To Next Curve·"
                         "2=To Next Sharp·3=To Next Edge）")

    before = _feature_count(model)                                                 # ★ 回读基线
    steps = []

    #: ① 清选区（★ 官方示例第一句）
    model.ClearSelection2(True)

    #: ② 两个面：★ 第二个 `append=True`（★ 官方示例逐字）✓
    s1 = select_face_with_fallback(model, face_index_1, False, 0)
    steps.append({"step": "select_face_1", **s1})
    s2 = select_face_with_fallback(model, face_index_2, True, s1["selection_count"])
    steps.append({"step": "select_face_2", **s2})
    if s1["selection_count"] != 1 or s2["selection_count"] != 2:
        raise RuntimeError("★ 选面没落到 2 个（★ 判据是回读计数，不是 SelectByID2 的 bool）"
                           "：第 1 次=%r 第 2 次=%r" % (s1["selection_count"], s2["selection_count"]))

    fm = model.FeatureManager

    #: ③ 官方示例里的曲线数据（★ 逐字照抄那两行的实参形态）
    try:
        fm.SetNetBlendCurveData(0, 0, 0, 0, 1, True)
        fm.SetNetBlendCurveData(0, 1, 0, math.radians(float(tangency_deg)), 1, True)
        steps.append({"step": "SetNetBlendCurveData", "tangency_deg": tangency_deg})
    except Exception as exc:                                                         # noqa: BLE001
        steps.append({"step": "SetNetBlendCurveData", "error": str(exc)})

    #: ④ 方向数据（★ `SplitSurfaces` 官方标 Not used ⇒ 传 False ✓）
    try:
        fm.SetNetBlendDirectionData(0, int(influence_type), 1 if trim_curves else 0,
                                   bool(blend_closed), False)
        fm.SetNetBlendDirectionData(1, int(influence_type), 1 if trim_curves else 0,
                                   bool(blend_closed), False)
        steps.append({"step": "SetNetBlendDirectionData", "influence_type": influence_type})
    except Exception as exc:                                                         # noqa: BLE001
        steps.append({"step": "SetNetBlendDirectionData", "error": str(exc)})

    #: ⑤ 建特征 —— ★ 20 个实参**按官方顺序**（★ 别照抄示例的字面值，逐位对上）
    #:   Type, NCurvesDir1, NCurvesDir2, HasCenterline, TessTolFactor, WantsSolid, MergeBody,
    #:   FeatureScope, AutoSelect, Thin, Thickness1, Thickness2, ReverseThickness, ThinSolidType,
    #:   UseSharedThickness, CapEnds, EndThickness, AutoFillet, FilletRadius, ForceNonRational
    feat = fm.InsertNetBlend(
        int(blend_type), int(n_curves_dir1), int(n_curves_dir2), False, 0.0001,
        True, bool(merge_body), False, False, False,
        float(thickness1_mm) * _MM, float(thickness2_mm) * _MM, False, 0,
        False, False, 0.0, False, 0.0, False,
    )
    after = _feature_count(model)
    name = getattr(feat, "Name", None) if feat is not None else None
    steps.append({"step": "InsertNetBlend", "returned": feat is not None, "feature": name,
                  "before": before, "after": after})

    return {
        "ok": feat is not None and after > before,                                   # ★ 回读判据
        "blend_type": int(blend_type),
        "blend_type_name": {v: k for k, v in BLEND_TYPE.items()}.get(int(blend_type)),
        "feature": name,
        "feature_count_before": before,
        "feature_count_after": after,
        "steps": steps,
        "official": "IFeatureManager::InsertNetBlend",
        "units": "★ 入参按毫米/度；COM 侧米/弧度（本仓事实 2）",
        "verification": "stitched —— ★ 尚未真机验证（红线⑥：level 只按真机证据变）",
    }

def insert_boundary_boss_report(
    model,
    *,
    face_index_1: int = 0,
    face_index_2: int = 1,
    influence_type: int = 0,
    trim_curves: bool = False,
    blend_closed: bool = False,
    tangency_deg: float = 15.0,
    merge_body: bool = True,
) -> dict:
    """★ 边界**凸台**（官方 `InsertNetBlend`，`Type=1 Boss`）—— ★ 显式签名（★ 门禁要 function 形态）✓"""
    return insert_net_blend_report(
        model, face_index_1=face_index_1, face_index_2=face_index_2, blend_type=1,
        influence_type=influence_type, trim_curves=trim_curves, blend_closed=blend_closed,
        tangency_deg=tangency_deg, merge_body=merge_body,
    )


def insert_boundary_surface_report(
    model,
    *,
    face_index_1: int = 0,
    face_index_2: int = 1,
    influence_type: int = 0,
    trim_curves: bool = False,
    blend_closed: bool = False,
    tangency_deg: float = 15.0,
    merge_body: bool = True,
) -> dict:
    """★ 边界**曲面**（官方 `InsertNetBlend`，`Type=2 Surface`）—— ★ 显式签名 ✓"""
    return insert_net_blend_report(
        model, face_index_1=face_index_1, face_index_2=face_index_2, blend_type=2,
        influence_type=influence_type, trim_curves=trim_curves, blend_closed=blend_closed,
        tangency_deg=tangency_deg, merge_body=merge_body,
    )

def _feature_count(model) -> int:
    """★ 特征树计数 —— ★ 本 COM 绑定里 `GetFeatureCount` 是**属性**（`() `会报
    `TypeError: 'int' object is not callable`）⇒ ★ 这里两种形态都吃 ✓"""
    attr = getattr(model, "GetFeatureCount", None)
    if attr is None:
        return -1
    if callable(attr):
        try:
            return int(attr())
        except TypeError:
            pass
    try:
        return int(attr)
    except (TypeError, ValueError):
        return -1

def select_face_with_fallback(model, face_index: int, append: bool,
                              before_count: int) -> dict:
    """★ 选一个面 —— ★ 先用**盒中心**；★ 若**回读计数没增加**就**换点重试**（★ 处置实测到的现象）。

    ★★ 依据（真机读数，规格 220 T-220-01 第 5–7 轮）：★ **0 号面按盒中心选不上**
      （`第 1 次=0`），★ 而 **1 号面同样按盒中心却立刻就成**（★ swap test 定案）⇒
      ★★ 所以**不能假设"盒中心一定可选"**，★ 必须**按回读判决 + 换点重试** ✓
    ★ 判据：★ **回读计数**（★ 事实 8：`SelectByID2` 的 bool 不可信）✓
    ★ 每次尝试都把 `point` 与 `count` 记进返回值（★ 供后人核）✓
    """
    import sw_part as _sp
    import sw_selection_spec as _SS

    faces = list(_SS.entities_on_body(model, "FACE", body_index=0) or [])
    if face_index < 0 or face_index >= len(faces):
        raise RuntimeError("面序号越界：face_index=%r，本体共 %d 个面" % (face_index, len(faces)))
    face = faces[face_index]
    box = list(_sp.get_com_member(face, "GetBox") or [])
    if len(box) < 6:
        raise RuntimeError("★ 取面上失败：`IFace2.GetBox()` 回了 %r" % (box,))
    cx = (float(box[0]) + float(box[3])) / 2.0
    cy = (float(box[1]) + float(box[4])) / 2.0
    cz = (float(box[2]) + float(box[5])) / 2.0
    #: ★ 换点用的偏移（单位**米**；★ 0.5 mm = 5e-4 m）—— ★ 只动一点点，仍在该面附近
    tries = [(0.0, 0.0, 0.0)]
    for d in (0.0005, -0.0005):
        tries += [(d, 0.0, 0.0), (0.0, d, 0.0), (0.0, 0.0, d),
                  (-d, 0.0, 0.0), (0.0, -d, 0.0), (0.0, 0.0, -d)]
    attempts = []
    for (dx, dy, dz) in tries:
        model.ClearSelection2(True) if False else None       #: ★ 不清（append 语义由调用方定）
        #: ★★★ 2026-10-07（规格 220 T-220-01 第 9 轮**真机定案**）★ 选面改用
        #:   `IEntity.Select4(Append, Callout)` ✓ —— ★ 实测（`tools/probe_spec220_append_arms.py`）：
        #:     ★ `SelectByID2` 按点对 0 号面**两次都是 0**（永远选不上）✗
        #:     ★ 而 `face.Select4(False)` 对**同一个面**回 **[True, 1]** ✓
        #:     ★ 且 `face.Select4(True)` 回 **[True, 2]** ⇒ **Append 正确累加** ✓
        #:   ⇒ ★ 两个问题一次全解 ✓（★ 这也正是本仓**事实 32**记的"按对象选"那条路）
        ok = face.Select4(bool(append), _sp._empty_callout())
        cnt = int(model.SelectionManager.GetSelectedObjectCount2(-1))
        attempts.append({"d": [round(dx, 6), round(dy, 6), round(dz, 6)],
                         "ok": bool(ok), "count": cnt})
        if cnt > before_count:
            return {"ok": True, "selection_count": cnt, "point": [cx + dx, cy + dy, cz + dz],
                    "attempts": attempts, "tries_used": len(attempts)}
    return {"ok": False, "selection_count": attempts[-1]["count"],
            "point": [cx, cy, cz], "attempts": attempts, "tries_used": len(attempts)}
