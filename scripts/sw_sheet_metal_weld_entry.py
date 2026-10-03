"""★ 钣金/焊件/曲面 5 项「直入法」入口（斜接法兰 / 闭合角 / 顶端盖 / 角撑板 / 中面）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_sheet_metal_weld_entry.py
# 定位:   ★ 2026-10-03 承 `specs/202-user-coverage-gaps` 的 **T-C2**：钣金/焊件 5 项
#   **「直入法」**（★ 即"直接调一个方法把特征建出来"，★ **不是** `CreateDefinition`+`CreateFeature` 那条）。
#
#   ★★★ 为什么这一批**必须写直入法**、而不是走 `CreateDefinition`（事实 43 一族的反面）：
#     本仓 `scripts/sw_sheet_metal.py` 已经有 `create_gusset` 走 `swFmSMGusset(118)` 那条，
#     ★ 而那是**钣金**加强筋；★ **焊件**角撑板与**焊件**顶端盖**没有**对应的 `swFm*` 入口，
#     ★ 它们在官方只有 `IFeatureManager.InsertGussetFeature3` / `InsertEndCapFeature3`
#     这类「一步到位」方法 ⇒ ★ **直入法是它们唯一的建模入口**。
#
#   ======================  ==============================  ==========================================
#   功能                    官方入口（★ 非废弃）                ★ 本批逐条核到的「前置」
#   ======================  ==============================  ==========================================
#   斜接法兰                `IFeatureManager.                  ★ **官方页无 `## Remarks` 段**
#                            InsertSheetMetalMiterFlange`（14）  ⇒ ★ 前置**查不到**（铁律 5）★
#                                                                  只回读选区计数，不编前置
#   闭合角                  `IModelDoc2.                       ★ **官方页无 `## Remarks` 段** ⇒ 同上
#                            InsertSheetMetalClosedCorner()`（0）
#   焊件顶端盖              `IFeatureManager.                  ★「Before calling this method, **select
#                            InsertEndCapFeature3`（10）          one or more end faces of a structural
#                                                                  member in the graphics area.」
#   焊件角撑板              `IFeatureManager.                  ★「…you must call SelectByID2 to select
#                            InsertGussetFeature3`（20）         **two faces** that are the supporting legs
#                                                                  of this gusset **with a Mark of 1**」
#   曲面中面                `IFeatureManager.                  ★「The **pPartDocIn** parameter is the
#                            InsertMidSurface`（4）              component's model document … and the
#                                                                  **pBody** parameter is the body of that
#                                                                  component.」
#   ======================  ==============================  ==========================================
#
#   ★★★★★ **本批逐条查到的「废弃链」**（★ 铁律 4 的核心工作，★ 也是本批最容易栽的地方）：
#     ① `IModelDoc2.InsertSheetMetalMiterFlange` —— **Obsolete**，逐字
#        「Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].」
#        ★★ **同名两份页、参数完全不同**（那份 11 参且**回 void**；可用那份 **14 参、回 Feature**）
#          ★ ⇒ **用错接口 = 参数个数对不上**，★ 而不只是"没反应"。
#     ② `IFeatureManager.InsertEndCapFeature` —— **Obsolete** → 后继 `InsertEndCapFeature3`（10 参）。
#        ⚠ 但 **`InsertEndCapFeature2`（7 参、末位是 `System.object Faces`）不在这条链上**
#          —— ★ 官方页**无** Obsolete 句，★ 且其 Remarks 明写它是「用 Faces 数组」的**并列**入口
#          ⇒ ★ **不是** `1 → 2 → 3` 的线性继承（★ 这一点极易想当然）。
#     ③ `IFeatureManager.InsertGussetFeature` —— **Obsolete** → 后继 **`InsertGussetFeature3`**。
#        ⚠ ★★ **官方在此处断链**：`InsertGussetFeature2` 的页**没有** Obsolete 句
#          ⇒ ★ 第 1 代**直接**指向第 3 代，★ 中间那代的废弃状态**官方没写**。
#          ⇒ ★★ **别写「Gusset 有三代线性链」** —— ★ 那是想当然（★ 已踩过的形态：事实 53）。
#     ④ `IModelDoc2.InsertMidSurfaceExt` —— **Obsolete** → 后继 `IFeatureManager::InsertMidSurface`（链闭合）。
#     ⑤ `IModelDoc2.IInsertMidSurfaceExt` —— **Obsolete** → 后继点名 `IFeatureManager::IInsertMidSurface`，
#        ★★ **而那一页官方没写**（`C:\swapi\types\` 全库只有 3 个 `*MidSurface*` 文件）
#        ⇒ ★★ **链 B 断在这里、无后继签名可抄** ⇒ ★ 本模块**只走 `InsertMidSurface`（非 `I` 前缀）**，
#          ★ **不拿它顶替**（铁律 5）。
#
#   ★★ **Gusset 的两个同名接口，官方分类逐字抄自各自 front matter**（★ 已知事实 36 的原型）：
#     | | `IGussetFeatureData` | `ISMGussetFeatureData` |
#     |---|---|---|
#     | category | Feature Interfaces/**Weldments** | Feature Interfaces/**Sheet Metal** |
#     | 描述 | "Allows access to a **weldment** gusset feature." | "Allows access to a **sheet metal** gusset feature." |
#     | 属性数 | 14 | 28 |
#     | 方法数 | 4 | 2 |
#     ★⇒ 本模块的角撑板是**焊件**那个（`InsertGussetFeature3` + `IGussetFeatureData`）
#       ⇒ ★ **不碰** `ISMGussetFeatureData`（★ 那个本仓 `sw_sheet_metal.create_gusset` 已经在走
#       ★ `CreateDefinition` 路线，★ **不是**本模块这条、★ 也不算本项的实现）。
#
#   ★★ **单位**（规则 2 · 逐条有官方例子佐证）：
#     · **距离一律米**：官方例子 `InsertGussetFeature3(0.005, …, 0.025, 0.025, 0.015, …, 0.0125, …)`
#       ⇒ 5 mm / 25 mm / 12.5 mm；`Insert_Weldment_End_Cap_Example_VB` 读回时写
#       `swEndCap.ChamferDistance * 1000# & " mm"` ⇒ ★ **官方自己乘 1000 才是 mm**。
#       ⇒ 本模块**对外收毫米、只在边界除 1000**（`sw_connect.mm`）。
#     · **角度一律弧度**：官方例子 `InsertGussetFeature3(…, 0.78539816339745, …, …, 0.785398163397452, …)`
#       ⇒ **0.78539816339745 = π/4 = 45°** ⇒ ★ 官方吃**弧度** ⇒ 本模块**对外收度**、
#       边界换算一次（`sw_connect.deg`）。
#     · ⚠ **两个比例量不换算**：`WallThicknessRatio`（官方例子 `0.6`）与中面 `Placement`
#       （官方只说 "the placement position"、★ **没给单位**）⇒ ★ 原样透传（★ 铁律 5）。
#
#   ★★ **判据一律"可回读的量"**（规则 6 · 不能只有"返回非 None"）：
#     · **特征树增量** —— 走 `sw_feature_readback.feature_names`（★ 本仓已验证的那一条；
#       ⚠ **不要**自己拼 `GetFeatureCount`+`FeatureByPositionReverse`，★ 那条真机回 `None`）。
#     · **回读刚建出的那个 `IFeature`**：`GetDefinition()` + 官方例子读的那些属性。
#     · **体积 / 面数 / 曲面体数增量** —— 独立于特征树的第二判据。
#       ⚠ 闭合角官方**回 `void`** ⇒ ★ 它**没有**返回对象可读 ⇒ ★ 树增量 + 面数/体积增量**是唯一判据**。
#
#   官方依据（三源互证 · 铁律 4）:
#     · `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`（14 参 · Returns `Feature`）
#       ★★ 其 `PCBA` 形参的语义**逐字**是「**non-NULL** ⇒ Pointer to `ICustomBendAllowance`
#         object for which required values have been set；**NULL** ⇒ Parent bend's bend allowance is used」
#         ⇒ ★ 本模块**传空 Dispatch（= NULL 语义）**，★ 用本仓事实 12 那条
#         `create_empty_dispatch_variant()`，★ **不伪造一个没设过必需值的 ICustomBendAllowance**。
#       ★ 对照废弃那份：`C:\swapi\types\IModelDoc2\InsertSheetMetalMiterFlange.md`（11 参 · 回 void · Obsolete）
#     · `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`（**零参 · 回 void** · 无 Remarks）
#     · `C:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`（10 参 · Returns `IFeature` · **有 Remarks**）
#       + `C:\swapi\enums\swEndCapThicknessDirection_e.md`（Outward=0 / Inward=1 / **SpecifyInset=2**）
#       + `C:\swapi\examples\Insert_Weldment_End_Cap_Example_VB.md`（调用序 + 米制 + 读回写法）
#     · `C:\swapi\types\IFeatureManager\InsertGussetFeature3.md`（20 参 · **有 Remarks** · mark=1 逐字）
#       + `C:\swapi\enums\swGussetThicknessType_e.md`（Inner=0 / BothSides=1 / Outer=2）
#       + `C:\swapi\enums\swGussetProfileLocationType_e.md`（Start=0 / Center=1 / End=2）
#       + `C:\swapi\examples\Insert_Gusset_Feature_Example_VB.md`（**`SelectByID2(..., True, 1, ...)`**
#         ⇒ ★ mark=1 与 Append=True 的**双证据**；★ 角度=弧度、距离=米的数值佐证）
#     · `C:\swapi\types\IFeatureManager\InsertMidSurface.md`（4 参 · 前两位是 **`Body2` / `ModelDoc2` 对象**）
#       + `C:\swapi\types\IModelDoc2\InsertMidSurfaceExt.md`（Obsolete）
#       + `C:\swapi\types\IModelDoc2\IInsertMidSurfaceExt.md`（Obsolete；★ 其后继页**官方没写**）
#     · ★ arity 与官方签名**逐条互证**（反射 dump `scripts/sw_api_sldworks.py`，第三源）：
#       `'InsertSheetMetalMiterFlange': 14`（IFeatureManager）· `'InsertSheetMetalClosedCorner': 0`
#       · `'InsertEndCapFeature3': 10` · `'InsertGussetFeature3': 20` · `'InsertMidSurface': 4` ✓✓✓✓✓
#   许可:   本仓库 MIT。★ **无第三方代码引入**（只照官方签名与官方示例写）。
#   覆盖:   全文件
# ⚠ 本文件为**静态签名比对后新写**，**未在本机实测**（铁律 2：真机由 Lead 独家执行）。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

try:                                                                # 包内载入（mcp-server 走这条）
    from .sw_connect import create_empty_dispatch_variant, deg, get_com_member, mm
    from .sw_feature_readback import feature_names as _tree_names
except ImportError:                                                 # 顶层载入（脚本 / 探针）
    from sw_connect import create_empty_dispatch_variant, deg, get_com_member, mm  # noqa: F401
    from sw_feature_readback import feature_names as _tree_names                   # noqa: F401

__all__ = [
    "insert_sheet_metal_miter_flange",
    "insert_sheet_metal_closed_corner",
    "insert_weldment_end_cap",
    "insert_weldment_gusset",
    "insert_mid_surface",
    "SHEET_METAL_WELD_ENTRY_STATUS",
]

# ── 官方枚举（★ 逐字数值，来源写在每组后面的注释里）──────────────────────────────
#: `swSheetMetalReliefTypes_e`（`C:\swapi\enums\swSheetMetalReliefTypes_e.md`，5 个成员）
SW_RELIEF_RECTANGULAR = 1      # swSheetMetalReliefRectangular = 1
SW_RELIEF_TEAR = 2            # swSheetMetalReliefTear        = 2
SW_RELIEF_OBROUND = 3         # swSheetMetalReliefObround     = 3
SW_RELIEF_NONE = 4            # swSheetMetalReliefNone        = 4
SW_RELIEF_TEAR_BEND = 5       # swSheetMetalReliefTearBend    = 5

#: `swFlangePositionTypes_e`（`C:\swapi\enums\swFlangePositionTypes_e.md`，6 个成员）
SW_FLANGE_MATERIAL_INSIDE = 1      # swFlangePositionTypeMaterialInside  = 1
SW_FLANGE_MATERIAL_OUTSIDE = 2     # swFlangePositionTypeMaterialOutside = 2
SW_FLANGE_BEND_OUTSIDE = 3         # swFlangePositionTypeBendOutside     = 3
SW_FLANGE_BEND_CENTER_LINE = 4     # swFlangePositionTypeBendCenterLine  = 4
SW_FLANGE_BEND_SHARP = 5           # swFlangePositionTypeBendSharp       = 5（"Bend from virtual sharp"）
SW_FLANGE_BEND_TANGENT = 6         # swFlangePositionTypeBendTangent     = 6（⚠ 官方注明对
                                    #   "Up To Edge And Merge" 长度终止条件无效）

#: `swEndCapThicknessDirection_e`（`C:\swapi\enums\swEndCapThicknessDirection_e.md`，3 个成员）
SW_END_CAP_OUTWARD = 0         # swExtendOutward = 0
SW_END_CAP_INWARD = 1          # swExtendInward  = 1
SW_END_CAP_SPECIFY_INSET = 2   # swSpecifyInset  = 2 ★ 官方 `DepthOffset` 逐字「valid only if
                                #   BIsEndCapInward **= 2**」⇒ ★★ 与官方例子传的 `2` 对得上 ✓

#: `swGussetThicknessType_e`（`C:\swapi\enums\swGussetThicknessType_e.md`，3 个成员）
SW_GUSSET_THICKNESS_INNER = 0       # swGussetThicknessInner      = 0
SW_GUSSET_THICKNESS_BOTH_SIDES = 1  # swGussetThicknessBothSides = 1（★ 官方例子用的就是它）
SW_GUSSET_THICKNESS_OUTER = 2       # swGussetThicknessOuter      = 2

#: `swGussetProfileLocationType_e`（`C:\swapi\enums\swGussetProfileLocationType_e.md`，3 个成员）
SW_GUSSET_PROFILE_START = 0     # swGussetProfileLocationStart  = 0
SW_GUSSET_PROFILE_CENTER = 1    # swGussetProfileLocationCenter = 1（★ 官方例子用的就是它）
SW_GUSSET_PROFILE_END = 2       # swGussetProfileLocationEnd    = 2


#: ★ 本模块覆盖到的 5 项 ⇒ 官方入口（★ 与 `tools/audit_gap_implementations.py` 对齐用）
SHEET_METAL_WELD_ENTRY_STATUS = {
    "钣金/斜接法兰": "IFeatureManager.InsertSheetMetalMiterFlange（14 参）"
                    "★ 废弃的是同名那份 IModelDoc2 版（11 参 · 回 void）",
    "钣金/闭合角": "IModelDoc2.InsertSheetMetalClosedCorner（零参 · 回 void）",
    "焊件/顶端盖": "IFeatureManager.InsertEndCapFeature3（10 参）"
                  "★ 废弃的是 InsertEndCapFeature（6 参）；★ InsertEndCapFeature2 是并列入口、不在链上",
    "焊件/角撑板": "IFeatureManager.InsertGussetFeature3（20 参 · 焊件 IGussetFeatureData）"
                  "★ 废弃的是 InsertGussetFeature（15 参）；★ 官方**断链**，中间代无 Obsolete 标注",
    "曲面/中面": "IFeatureManager.InsertMidSurface（4 参）"
                 "★ 废弃的是 IModelDoc2.InsertMidSurfaceExt / IInsertMidSurfaceExt；"
                 "★★ 后者点名的后继 IFeatureManager::IInsertMidSurface **官方没写**（查不到）",
}


# ── 判据用的小工具（★ 读不到就回 None，★ 不静默成 0 / 不猜）──────────────────────

def _tree(model) -> list[str] | None:
    """★ 特征名清单（★ 委托本仓已验证的 `sw_feature_readback.feature_names`）。

    ⚠ **为什么不用 `sw_part.feature_names`**：`sw_curve_and_split._tree_names` 去
      `from sw_part import feature_names`，★ 而 `sw_part` 里**没有**这个定义
      （★ 本轮实测：只有 `sw_feature_readback.feature_names` 是真的）⇒ ★ 那条路会让判据
      **静默降级成 None**。★ 本模块**只走真存在的那一条**。
    """
    try:
        return [str(x) for x in (_tree_names(model) or [])]
    except Exception:                                                # noqa: BLE001
        return None


def _new_features(before, after) -> list[str] | None:
    """★ 新增的特征名；★ 任一侧读不到就回 `None`（★ 判据降级，不猜）。"""
    if before is None or after is None:
        return None
    return [x for x in after if x not in before]


def _body_face_count(model) -> int | None:
    """★ 实体体的**面数合计** —— ★ 独立于特征树的第二判据（★ 闭合角唯一可用的那一类）。"""
    try:
        bodies = list(get_com_member(model, "GetBodies2", 0, True) or [])
    except Exception:                                                # noqa: BLE001
        return None
    total = 0
    for b in bodies:
        try:
            total += len(list(get_com_member(b, "GetFaces") or []))
        except Exception:                                            # noqa: BLE001
            continue
    return total


def _surface_body_count(model) -> int | None:
    """★ **曲面体**数 —— ★ 中面（midsurface）的专属判据。

    ★ 官方 `InsertMidSurface` 的 Remarks 逐字：「Each reference surface is considered a
      **sheet body**.」⇒ ★ 它产出的是**曲面体**，★ 而**实体面数**对它没有意义。
    """
    for member in ("GetSurfaceBodies", "GetSurfaceBodyCount"):
        try:
            value = get_com_member(model, member)
        except Exception:                                            # noqa: BLE001
            continue
        try:
            return len(list(value or []))
        except TypeError:
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


def _volume_mm3(model) -> float | None:
    """★ 体积（**mm³**）—— ★ 委托 `sw_mass_property.mass_properties`。

    ★ 那条路用的是 `CreateMassProperty2`（★ **`CreateMassProperty` 官方标 Obsolete** ⇒ 不用它）。
    ★ 取不到就回 `None`（★ 不静默成 0 —— 那样会变成"假没变"）。
    """
    try:
        from .sw_mass_property import mass_properties
    except ImportError:                                             # pragma: no cover
        from sw_mass_property import mass_properties
    try:
        value = mass_properties(model).get("volume")
    except Exception:                                                # noqa: BLE001
        return None
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _delta(before, after) -> int | float | None:
    """★ before/after 之差；★ 任一侧读不到回 `None`（★ 判据降级，不猜）。"""
    if before is None or after is None:
        return None
    return after - before


def _selection_marks(model) -> dict | None:
    """★ **按标记分组**的选区计数 —— ★ 本批的"前置有没有备好"的回读依据。

    ★ 依据：本仓事实 8 —— ★ `SelectByID2` 的 bool 返回值不可信，★ **只有计数算数**。
    ★ ★ 为什么按 mark 分组：角撑板官方逐字要求 **mark = 1**（两个支撑腿面），
      ★ 而闭合角/顶端盖官方**没给 mark**（官方例子用的是 mark 0）⇒ ★ 分组报出来，
      ★ 调用者能**看见自己备的是哪一档**，而不用猜。
    """
    try:
        sm = get_com_member(model, "SelectionManager")
    except Exception:                                                # noqa: BLE001
        return None
    if sm is None:
        return None
    out = {}
    for mark in (0, 1, 2, 4):
        try:
            out[str(mark)] = int(get_com_member(sm, "GetSelectedObjectCount2", mark))
        except Exception:                                            # noqa: BLE001
            out[str(mark)] = -1
    try:
        out["all"] = int(get_com_member(sm, "GetSelectedObjectCount2", -1))
    except Exception:                                                # noqa: BLE001
        out["all"] = -1
    return out


def _feature_name(feature) -> str | None:
    try:
        value = get_com_member(feature, "Name")
    except Exception:                                                # noqa: BLE001
        return None
    return None if value is None else str(value)


def _read_definition(feature, members, scale_mm: bool = True):
    """★ `feature.GetDefinition()` + 逐条读属性 —— ★ **回读刚建出的那个特征本身**。

    :param members: 形如 ``[("ChamferDistance", 1000.0), ("IsEndCapInward", None)]``：
      第二位是**读出来要乘的系数**（★ mm → 官方回的是**米** ⇒ 乘 1000），
      ★ 传 `None` 表示**原样回读**（枚举/布尔）。
    ★ 读不到就记进 `unreadable`，★ **不静默丢**。
    """
    out, unreadable = {}, []
    try:
        definition = get_com_member(feature, "GetDefinition")
    except Exception as exc:                                         # noqa: BLE001
        return {}, ["GetDefinition: %s" % str(exc)[:80]]
    if definition is None:
        return {}, ["GetDefinition 回 None"]
    for name, factor in members:
        try:
            raw = get_com_member(definition, name)
        except Exception as exc:                                     # noqa: BLE001
            unreadable.append("%s(%s)" % (name, str(exc)[:60]))
            continue
        if raw is None:
            unreadable.append("%s(读不到)" % name)
            continue
        if factor is None:
            out[name] = raw
            continue
        try:
            out[name] = float(raw) * float(factor)
        except (TypeError, ValueError):
            out[name] = raw
    return out, unreadable


# ── ① 钣金/斜接法兰（★ 走 IFeatureManager 那份，★ 别走 IModelDoc2 那份废弃的）────────

def insert_sheet_metal_miter_flange(model, *,
                                    use_default_radius: bool = True,
                                    global_radius_mm: float = 0.0,
                                    rip_gap_mm: float = 0.0,
                                    use_default_relief: bool = True,
                                    use_relief_ratio: bool = False,
                                    relief_ratio: float = 0.0,
                                    relief_width_mm: float = 0.0,
                                    relief_depth_mm: float = 0.0,
                                    relief_type: int = SW_RELIEF_RECTANGULAR,
                                    trim_side_bends: bool = False,
                                    flange_pos: int = SW_FLANGE_MATERIAL_INSIDE,
                                    offset_dist1_mm: float = 0.0,
                                    offset_dist2_mm: float = 0.0) -> dict:
    """★ **钣金斜接法兰**：`IFeatureManager.InsertSheetMetalMiterFlange(14 参)` → `Feature`。

    :param use_default_radius: 官方逐字「True to use **default bend radius**, false to use GlobalRadius」。
    :param global_radius_mm: 全局折弯半径（**毫米**；★ 仅 `use_default_radius=False` 时有意义）。
    :param rip_gap_mm: 切口间隙（**毫米**）。
    :param use_default_relief: 官方逐字「True to use **parent bend's ratio**」。
    :param use_relief_ratio: True 用自定义**让位比**、False 不用。
    :param relief_ratio: 让位比（★ **比例量、不换算**；官方逐字「If useReliefRatio is True …」）。
    :param relief_width_mm / relief_depth_mm: ★ 官方对这两个形参**写的是同一句**
      「If UseReliefRatio is True and ReliefType is swSheetMetalReliefRectangular or
      swSheetMetalReliefObround, then specify relief **depth**」⇒ ★ **官方这两句自相矛盾**
      （`ReliefWidth` 的说明也写 "relief depth"）⇒ ★ 本模块**原样透传、不替官方调和**（铁律 5）。
    :param relief_type: `swSheetMetalReliefTypes_e`（**Rectangular=1 · Tear=2 · Obround=3
      · None=4 · TearBend=5**）。
    :param trim_side_bends: True 裁剪侧折弯。
    :param flange_pos: `swFlangePositionTypes_e`（**MaterialInside=1 · MaterialOutside=2
      · BendOutside=3 · BendCenterLine=4 · BendSharp=5 · BendTangent=6**；★ 官方注明
      `BendTangent` 对 "Up To Edge And Merge" 终止条件**无效**）。
    :param offset_dist1_mm / offset_dist2_mm: 部分法兰的起/止偏移（**毫米**）。

    ★★★ **关于末位 `PCBA`**：★ 它是**对象形参**（`CustomBendAllowance`），★ 而官方把它的
      语义写成了二选一（逐字）：**non-NULL** ⇒ "Pointer to `ICustomBendAllowance` object **for
      which required values have been set**"；**NULL** ⇒ "Parent bend's bend allowance is used"。
      ⇒ ★ 本模块**传空 Dispatch**（＝ NULL 语义，★ 本仓事实 12 的
      `create_empty_dispatch_variant()`）★★ **不伪造一个"没设过必需值"的
      `ICustomBendAllowance`** —— ★ 那正是官方那句话在防的事。
      ★⇒ 因此本工具**不接受自定义 PCBA**，★ 将来要支持得另开一条入口。

    ⚠⚠★ **前置：官方页**没有 `## Remarks` 段**（逐字段核过：全文只有 `#` 标题 / `## Parameters`
      / `## Returns` / `## See Also`）⇒ ★★ **前置查不到** ⇒ ★ 本模块**不编前置**
      （铁律 5），★ 只**回读选区计数**并如实标 `preconditions_held: None`
      （★ **不是** `False` —— ★ 官方没说要什么，★ 判"没备好"是本模块自己加的）。
    """
    if model is None:
        return {"ok": False, "op": "insert_sheet_metal_miter_flange", "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "op": "insert_sheet_metal_miter_flange",
                "error": "取不到 FeatureManager"}
    before = _tree(model)
    before_faces = _body_face_count(model)
    #: ★ 空 Dispatch（= 官方 PCBA 那一列的 **NULL** 分支）★ 见上文逐字理由
    null_dispatch = create_empty_dispatch_variant()
    feature = get_com_member(
        fm, "InsertSheetMetalMiterFlange",
        bool(use_default_radius),
        mm(float(global_radius_mm)),
        mm(float(rip_gap_mm)),
        bool(use_default_relief),
        bool(use_relief_ratio),
        float(relief_ratio),                 #: ★ 比例量，不换算
        mm(float(relief_width_mm)),
        mm(float(relief_depth_mm)),
        int(relief_type),
        bool(trim_side_bends),
        int(flange_pos),
        mm(float(offset_dist1_mm)),
        mm(float(offset_dist2_mm)),
        null_dispatch,                        #: ← 第 14 位，★ 对象形参（NULL 语义）
    )
    after = _tree(model)
    after_faces = _body_face_count(model)
    added = _new_features(before, after)
    return {
        "ok": bool(added) and feature is not None,
        "op": "insert_sheet_metal_miter_flange",
        "entry_point": "IFeatureManager.InsertSheetMetalMiterFlange（★ 14 参 · 非废弃）",
        "obsolete_note": "★ 同名的 IModelDoc2.InsertSheetMetalMiterFlange（11 参 · 回 void）"
                         "**已 Obsolete** ⇒ 本模块**不调**它",
        "returned_is_none": feature is None,
        "returned_name": _feature_name(feature),
        "tree_before": before, "tree_after": after, "new_features": added,
        "face_count_before": before_faces, "face_count_after": after_faces,
        "face_count_delta": _delta(before_faces, after_faces),
        "pcba_passed": "★ 空 Dispatch（= 官方 PCBA 那一列的 NULL 分支）⇒ 用父折弯的折弯补偿",
        "unit_assumption": "★ 官方未给单位；按 SolidWorks 惯例当**米**、对外收毫米、边界换算一次",
        "selection_marks": _selection_marks(model),
        "preconditions_held": None,
        "precondition_note": "★★ **官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ 本模块**不编前置**"
                             "（铁律 5）；★ 只回读选区计数，★ `preconditions_held` 如实报 None",
        "verified_by": "feature tree delta + IFeature non-None + solid face-count delta",
    }


# ── ② 钣金/闭合角（★ 官方零参、回 void ⇒ 判据只能靠树/几何增量）──────────────────

def insert_sheet_metal_closed_corner(model) -> dict:
    """★ **钣金闭合角**：`IModelDoc2.InsertSheetMetalClosedCorner()` → **`void`**（★ 零参）。

    ⚠⚠★ **这是本批判据最紧的一条**，★ 因为官方**同时**给了「**零参数**」与「**回 `void`**」：
      ⇒ ★ **没有返回对象可读** ⇒ ★ "返回非 None" **这条判据在本函数上根本不存在**
      ⇒ ★ 判据**只能**是：**特征树增量** + **实体面数增量** + **体积增量**（后两个互相独立）。

    ⚠⚠ **前置**：★ 官方页**无 `## Remarks` 段** ⇒ ★★ **前置查不到**（铁律 5）⇒ 本模块
      **不编前置**，★ 只回读选区计数并如实标 `preconditions_held: None`。
      ★ （★ 该族另有 `IClosedCornerFeatureData` 这条指针路，★ 其 `## Remarks` 只讲
      ★ **事后修改**时怎么进/出回滚态，★ **不是**建模前置 —— ★ 不要把两件事混起来。）

    ⚠ **另一个坑（已知事实 36 一族）**：`IClosedCornerFeatureData` 里
      `IAccessSelections` 已 Obsolete、后继是 `IAccessSelections2` ⇒ ★ 而 `AccessSelections`
      那一族是**进程内指针接口**，★ 本仓 pywin32 后端**到不了**（事实 47）
      ⇒ ★ 本模块**只走直入法**，★ **不碰**那族（★ 这也正好符合本批「直入法」的定位）。
    """
    if model is None:
        return {"ok": False, "op": "insert_sheet_metal_closed_corner", "error": "model 为 None"}
    before = _tree(model)
    before_faces = _body_face_count(model)
    before_vol = _volume_mm3(model)
    #: ★ 官方**零参** ⇒ 一个实参都不传（★ 官方 Signature 逐字 `void InsertSheetMetalClosedCorner()`）
    get_com_member(model, "InsertSheetMetalClosedCorner")
    after = _tree(model)
    after_faces = _body_face_count(model)
    after_vol = _volume_mm3(model)
    added = _new_features(before, after)
    face_delta = _delta(before_faces, after_faces)
    vol_delta = _delta(before_vol, after_vol)
    #: ★★ 官方回 void ⇒ ★ "至少一个可回读的量变了"才是判据（★ 而不是"返回非 None"）
    changed = any(x is not None for x in (added, face_delta, vol_delta))
    return {
        "ok": bool(changed and (bool(added) or (face_delta or 0) != 0 or (vol_delta or 0) != 0)),
        "op": "insert_sheet_metal_closed_corner",
        "entry_point": "IModelDoc2.InsertSheetMetalClosedCorner（★ 零参 · **回 void**）",
        "returns_void": True,
        "returned_is_none": None,          # ★ 官方回 void ⇒ ★ 这个字段**无意义**，如实置 None
        "tree_before": before, "tree_after": after, "new_features": added,
        "face_count_before": before_faces, "face_count_after": after_faces,
        "face_count_delta": face_delta,
        "volume_mm3_before": before_vol, "volume_mm3_after": after_vol,
        "volume_mm3_delta": vol_delta,
        "selection_marks": _selection_marks(model),
        "preconditions_held": None,
        "precondition_note": "★★ **官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ 不编前置（铁律 5）",
        "pointer_family_note": "★ IClosedCornerFeatureData.IAccessSelections 已 Obsolete → IAccessSelections2；"
                               "★ ★ 而该族是**进程内指针接口**，★ 本仓 pywin32 后端到不了（事实 47）⇒ 本模块不碰",
        "verified_by": "feature tree delta + solid face-count delta + volume delta"
                       "（★ 官方回 void ⇒ 三个都是必要的）",
    }


# ── ③ 焊件/顶端盖（★ InsertEndCapFeature3，★ 前置逐字 = 先选端面）────────────────

def insert_weldment_end_cap(model, depth_mm: float, *,
                            is_given_offset: bool = False,
                            is_chamfer: bool = False,
                            offset_value_mm: float = 0.0,
                            wall_thickness_ratio: float = 0.0,
                            chamfer_value_mm: float = 0.0,
                            is_corner_treatment: bool = False,
                            depth_offset_mm: float = 0.0,
                            is_reverse: bool = False,
                            is_end_cap_inward: int = SW_END_CAP_OUTWARD) -> dict:
    """★ **焊件顶端盖**：`IFeatureManager.InsertEndCapFeature3(10 参)` → `IFeature`。

    :param depth_mm: 顶端盖厚度（**毫米**）。
    :param is_given_offset: 官方逐字「True to provide an **offset value**, false to provide a
      **thickness ratio**」。
    :param is_chamfer: 官方逐字「True if end cap feature is **chamfered**, false if **filleted**」。
    :param offset_value_mm: 边偏移（**毫米**；★ 官方逐字「valid **only if** `BIsGivenOffset` is true」）。
    :param wall_thickness_ratio: 壁厚比（★ **比例量、不换算**；★ 官方逐字「valid only if
      `BIsGivenOffset` is **false**」⇒ ★ 与 `offset_value_mm` **二选一**）。
    :param chamfer_value_mm: 倒角距离（`is_chamfer=True` 时）/ 圆角半径（False 时）（**毫米**）。
    :param is_corner_treatment: 官方逐字「…valid **only if** `BIsGivenOffset` is false」。
    :param depth_offset_mm: 内插距离（**毫米**；★ 官方逐字「valid **only if**
      `BIsEndCapInward` **= 2**」⇒ ★★ 与 `swEndCapThicknessDirection_e.swSpecifyInset = 2`
      ★ **对得上**（★ 官方例子也确实传了 `2`）✓）。
    :param is_reverse: 反转偏移或厚度比。
    :param is_end_cap_inward: `swEndCapThicknessDirection_e`：
      **0=swExtendOutward · 1=swExtendInward · 2=swSpecifyInset**。

    ★★★ **官方前置（`## Remarks` 逐字）**：
      > Before calling this method, **select one or more end faces** of a structural member
      > in the graphics area.
      ⇒ ★★ 调用前必须在图形区**选中一个或多个端面**；★ 本模块**不代选**
      （★ 面没有可用名字，本仓事实 32；★ 且规则 3 禁裸坐标），★ 只**回读选区计数**。
      ⚠ ★★ **官方这一句**没有给 mark**：★ 官方例子用的是
      `SelectByID2("", "FACE", …, True, **0**, Nothing, 0)` ⇒ ★ **mark = 0**
        ⇒ ★ **与角撑板的 mark=1 不一样** ⇒ ★ 两个入口的 mark **不能互相套用**（★ 回读里分组报出来）。

    ★ 判据 = **特征树增量** + **`GetDefinition()` 读回 11 个属性里能读到的那几个**（官方例子读法）。
    """
    if model is None:
        return {"ok": False, "op": "insert_weldment_end_cap", "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "op": "insert_weldment_end_cap", "error": "取不到 FeatureManager"}
    before = _tree(model)
    marks = _selection_marks(model)
    feature = get_com_member(
        fm, "InsertEndCapFeature3",
        mm(float(depth_mm)),
        bool(is_given_offset),
        bool(is_chamfer),
        mm(float(offset_value_mm)),
        float(wall_thickness_ratio),     #: ★ 比例量，不换算
        mm(float(chamfer_value_mm)),
        bool(is_corner_treatment),
        mm(float(depth_offset_mm)),
        bool(is_reverse),
        int(is_end_cap_inward),
    )
    after = _tree(model)
    added = _new_features(before, after)
    #: ★ 回读的成员名与单位换算**逐条照官方例子**（`swEndCap.X * 1000# & " mm"` ⇒ 官方回米）
    definition, unreadable = ({}, [])
    if feature is not None:
        definition, unreadable = _read_definition(feature, [
            ("Thickness", 1000.0),
            ("OffsetDistance", 1000.0),
            ("ChamferDistance", 1000.0),
            ("DepthDistance", 1000.0),
            ("ThicknessRatioForOffset", None),
            ("IsEndCapInward", None),
            ("UseChamferCorners", None),
            ("UseCornerTreatment", None),
            ("UseReverse", None),
            ("UseThicknessRatioForOffset", None),
        ])
    total_selected = (marks or {}).get("all", -1)
    return {
        "ok": bool(added) and feature is not None,
        "op": "insert_weldment_end_cap",
        "entry_point": "IFeatureManager.InsertEndCapFeature3（★ 10 参 · 非废弃）",
        "obsolete_note": "★ InsertEndCapFeature（6 参）**已 Obsolete** → 后继 3；"
                         "★ ★ InsertEndCapFeature2（7 参 · 末位 System.object Faces）是**并列**入口、"
                         "**不在**这条链上（★ 官方页无 Obsolete 句）",
        "returned_is_none": feature is None,
        "returned_name": _feature_name(feature),
        "definition_readback_mm": definition,
        "definition_unreadable": unreadable,
        "tree_before": before, "tree_after": after, "new_features": added,
        "selection_marks": marks,
        "preconditions_held": bool(total_selected >= 1),
        "precondition_note": "★ 官方逐字：'Before calling this method, **select one or more end "
                             "faces** of a structural member in the graphics area.'"
                             "★ ★ 官方**没给 mark**，★ 官方例子用的是 mark=**0**",
        "unit_assumption": "★ 官方未给单位；按米收、对外收毫米、边界换算一次"
                           "（★ 官方例子读回时自己 `* 1000#` 才成 mm ⇒ 官方回的确实是米）",
        "verified_by": "feature tree delta + IFeature non-None + GetDefinition() 属性回读",
    }


# ── ④ 焊件/角撑板（★ InsertGussetFeature3，★ 前置逐字 = 两个面 + mark=1）───────────

def insert_weldment_gusset(model, depth_mm: float, *,
                           dir_type: int = SW_GUSSET_THICKNESS_BOTH_SIDES,
                           loc_type: int = SW_GUSSET_PROFILE_CENTER,
                           is_profile: bool = False,
                           profile_d1_mm: float = 0.0,
                           profile_d2_mm: float = 0.0,
                           profile_d3_mm: float = 0.0,
                           profile_angle_deg: float = 45.0,
                           profile_d4_mm: float = 0.0,
                           offset_reference_plane: bool = False,
                           d_profile_offset_mm: float = 0.0,
                           crv_index: int = 0,
                           reverse_dir: bool = False,
                           reverse_face: bool = False,
                           use_len_dim: bool = False,
                           profile_d5_mm: float = 0.0,
                           profile_d6_mm: float = 0.0,
                           profile_chamfer_angle_deg: float = 45.0,
                           use_len_dim_for_chamfer: bool = False,
                           need_chamfer_in_gusset: bool = False) -> dict:
    """★ **焊件角撑板**：`IFeatureManager.InsertGussetFeature3(20 参)` → `IFeature`。

    :param depth_mm: 角撑板厚度（**毫米**）。
    :param dir_type: 官方 `DirType`（**`System.short`**）：`swGussetThicknessType_e`
      —— **0=Inner · 1=BothSides · 2=Outer**。
    :param loc_type: 官方 `LocType`（**`System.short`**）：`swGussetProfileLocationType_e`
      —— **0=Start · 1=Center · 2=End**。
    :param is_profile: 官方逐字「True to use a **polygon** profile, false to use a **triangle** profile」。
    :param profile_d1_mm / d2 / d3: 轮廓距离 1/2/3（**毫米**）。
    :param profile_angle_deg: 轮廓角（**度**；★ 边界换算成**弧度**）。★ 官方逐字
      「valid **only if** `BUseLenDim` is **false**」。
    :param profile_d4_mm: 轮廓距离 4（**毫米**；★ 官方逐字「valid **only if** `BUseLenDim` is **true**」）。
    :param offset_reference_plane: 官方 `BOffset` —— 偏置角撑板草图的参考平面。
    :param d_profile_offset_mm: 参考平面偏置值（**毫米**）。
    :param crv_index: 多条相交边时用哪一条（官方 `CrvIndex`）。
    :param reverse_dir / reverse_face: 官方 `BReverseDir` / `BReverseFace`。
    :param use_len_dim: 官方 `BUseLenDim` —— True 用 `ProfileD4`、False 用 `ProfileAngle`。
    :param profile_d5_mm / d6_mm: 倒角距离 5/6（**毫米**；★ 官方逐字 `ProfileD6`
      「valid **only if** `BNeedChamferInGusset` **and** `BUseLenDimForChamfer` are **both** true」）。
    :param profile_chamfer_angle_deg: 倒角角（**度**；★ 官方逐字「valid only if
      `BUseLenDimForChamfer` is **false** **and** `BNeedChamferInGusset` is **true**」）。
    :param use_len_dim_for_chamfer / need_chamfer_in_gusset: 官方 `BUseLenDimForChamfer` /
      `BNeedChamferInGusset`（后者逐字「…to allow room for a **weld bead** under the gusset」）。

    ★★★ **官方前置（`## Remarks` 逐字，本批最硬的一条）**：
      > Before calling this method, you must call `IModelDocExtension::SelectByID2` to select
      > **two faces** that are the supporting legs of this gusset **with a Mark of 1**.

      ⇒ ★★ 调用前必须**选两个面**、★ 且 **mark = 1**（★ 不是 0！）
      ⇒ ★ 本模块**按 mark 分组回读选区计数**，`preconditions_held` 判的是
      ★ **`marks["1"] >= 2`**（★ 两个支撑腿）⇒ ★ 调用者能一眼看见"mark 1 上只有 1 个面"这种失败。
      ★ ★ 官方例子把 mark 1 与 `Append=True` **一起**用（`SelectByID2(..., True, 1, Nothing, 0)`）
      ⇒ ★ 本模块**照抄**：两次都 Append、**都用 mark 1**（★ 不自己挑一个"看起来对"的组合）。

    ⚠ **别认错接口**：★ 这是**焊件**角撑板（`IGussetFeatureData`，官方描述逐字
      "Allows access to a **weldment** gusset feature."）⇒ ★ **不是**钣金那个
      `ISMGussetFeatureData`（"Allows access to a **sheet metal** gusset feature."，28 属性 / 2 方法）
      ⇒ ★ 用错时**连读都读不到**（已知事实 36）。★ 本模块**只走 `InsertGussetFeature3`**。

    ⚠ `DirType` / `LocType` 的官方类型是 **`System.short`** —— ★ pywin32 迟到绑定传的是
      VT_I4，★ 本模块按 `int()` 透传并**在这里声明这一点**（★ 不假装类型已经对上）。
    """
    if model is None:
        return {"ok": False, "op": "insert_weldment_gusset", "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "op": "insert_weldment_gusset", "error": "取不到 FeatureManager"}
    before = _tree(model)
    before_faces = _body_face_count(model)
    marks = _selection_marks(model)
    feature = get_com_member(
        fm, "InsertGussetFeature3",
        mm(float(depth_mm)),
        int(dir_type),                        #: ★ 官方 System.short，本仓按 int 透传（已声明）
        int(loc_type),                        #: ★ 同上
        bool(is_profile),
        mm(float(profile_d1_mm)),
        mm(float(profile_d2_mm)),
        mm(float(profile_d3_mm)),
        deg(float(profile_angle_deg)),        #: ★ 官方吃**弧度**（例子 0.78539816339745 = 45°）
        mm(float(profile_d4_mm)),
        bool(offset_reference_plane),
        mm(float(d_profile_offset_mm)),
        int(crv_index),
        bool(reverse_dir),
        bool(reverse_face),
        bool(use_len_dim),
        mm(float(profile_d5_mm)),
        mm(float(profile_d6_mm)),
        deg(float(profile_chamfer_angle_deg)),#: ★ 同上，弧度
        bool(use_len_dim_for_chamfer),
        bool(need_chamfer_in_gusset),
    )
    after = _tree(model)
    after_faces = _body_face_count(model)
    added = _new_features(before, after)
    mark1 = (marks or {}).get("1", -1)
    return {
        "ok": bool(added) and feature is not None,
        "op": "insert_weldment_gusset",
        "entry_point": "IFeatureManager.InsertGussetFeature3（★ 20 参 · 非废弃 · **焊件**）",
        "obsolete_note": "★ InsertGussetFeature（15 参）**已 Obsolete** → 后继 **3**；"
                         "★ ★ 官方**断链**：InsertGussetFeature2 的页**没有** Obsolete 句 ⇒ "
                         "★ 第 1 代直接指向第 3 代，★ 中间那代的废弃状态**官方没写**",
        "interface_family": "★ 焊件 IGussetFeatureData（14 属性 / 4 方法）"
                            "—— ★ **不是**钣金 ISMGussetFeatureData（28 属性 / 2 方法）"
                            "⇒ ★ 用错时连读都读不到（已知事实 36）",
        "returned_is_none": feature is None,
        "returned_name": _feature_name(feature),
        "tree_before": before, "tree_after": after, "new_features": added,
        "face_count_before": before_faces, "face_count_after": after_faces,
        "face_count_delta": _delta(before_faces, after_faces),
        "selection_marks": marks,
        "selection_mark_1_count": mark1,
        "preconditions_held": bool(mark1 >= 2),
        "precondition_note": "★ 官方逐字：'…must call SelectByID2 to select **two faces** that are "
                             "the supporting legs of this gusset **with a Mark of 1**'"
                             "★ ★ 官方例子两次都 **Append=True 且 mark=1** ⇒ 本模块照抄这个组合",
        "short_param_note": "★ DirType / LocType 官方类型是 System.short；★ pywin32 迟到绑定传 "
                            "VT_I4 ⇒ 本模块按 int 透传并**声明这一点**（不假装类型已对上）",
        "unit_assumption": "★ 距离按米收、对外毫米（官方例子 0.005/0.025/0.0125 即 5/25/12.5 mm）；"
                           "★ 角度官方吃**弧度**（例子 0.78539816339745 = π/4 = 45°）⇒ 对外收度、边界换算一次",
        "verified_by": "feature tree delta + IFeature non-None + solid face-count delta"
                       " + mark-1 选区计数",
    }


# ── ⑤ 曲面/中面（★ 前两位是对象形参 ⇒ 工具层 Param 表达不了 ⇒ 只在能力层）─────────

def insert_mid_surface(model, body, part_doc, *,
                       placement: float = 0.0,
                       knit_flag: bool = False) -> dict:
    """★ **曲面中面**：`IFeatureManager.InsertMidSurface(4 参)` → `System.object`。

    :param body: 官方 `Body2 PBodyIn` —— ★ **对象形参**（`IBody2` 实例）。
    :param part_doc: 官方 `ModelDoc2 PPartDocIn` —— ★ **对象形参**（`IModelDoc2` 实例）。
    :param placement: 参考面的位置（★ 官方逐字「The **placement position** of the reference
      surface is controlled by the `placement` parameter」—— ★ **既没说单位也没说量纲** ⇒
      ★ 本模块**原样透传、不换算**，★ 并把这点写进返回值（铁律 5）。
    :param knit_flag: True 把所有参考面**缝合成一张**（官方逐字「all the reference surfaces are
      **sewn** into a single reference surface if `knitFlag` is set to true」）。

    ★★★ **官方前置（`## Remarks` 逐字）**：
      > The **pPartDocIn** parameter is the **component's model document** where you want to add
      > the midsurface feature, and the **pBody** parameter is the **body of that component**.

      ⇒ ★★ 它要的是**"那个零件"的文档与"那个零件"里的体** ⇒ ★ **`part_doc` 必须是零件文档**，
        ★ 而**不是**装配文档 / 当前活动文档 ⇒ ★ 本模块**不替调用者猜**，★ 只回读并报告
        ★ 实参是什么、以及调用前后的**曲面体数**。

    ★★ **为什么工具层不给它建 ToolSpec**：`Param` 只能表达 **str / float / int / bool**
      ⇒ ★ `Body2` / `ModelDoc2` 两个**对象形参**表达不了 ⇒ ★ **能力层写、工具层不建**
      （★ 将来要暴露，正确形态是带 `extra_op` 的 ToolSpec，★ 而不是把对象硬塞进 `Param`）。

    ★ 判据 = **曲面体数增量**（★ 官方逐字「Each reference surface is considered a **sheet body**」
      ⇒ ★ 它产出的是曲面体，★ 而实体面数对它没有意义）+ **返回对象非 None** + **树增量**。
    """
    if model is None:
        return {"ok": False, "op": "insert_mid_surface", "error": "model 为 None"}
    if body is None:
        return {"ok": False, "op": "insert_mid_surface",
                "error": "body 为 None —— ★ 官方 PBodyIn 是对象形参，★ 取不到 body 就没有调用序",
                "no_tool_spec_reason": "★ Param 表达不了 Body2 / ModelDoc2 两个对象形参"}
    if part_doc is None:
        return {"ok": False, "op": "insert_mid_surface",
                "error": "part_doc 为 None —— ★ 官方 PPartDocIn 是对象形参（**组件的模型文档**）",
                "no_tool_spec_reason": "★ Param 表达不了 Body2 / ModelDoc2 两个对象形参"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "op": "insert_mid_surface", "error": "取不到 FeatureManager"}
    before = _tree(model)
    before_sb = _surface_body_count(model)
    result = get_com_member(
        fm, "InsertMidSurface",
        body,                   #: ★ 位置 1：Body2 PBodyIn（对象）
        part_doc,               #: ★ 位置 2：ModelDoc2 PPartDocIn（对象）
        float(placement),       #: ★ 官方未给单位/量纲 ⇒ 原样透传
        bool(knit_flag),
    )
    after = _tree(model)
    after_sb = _surface_body_count(model)
    added = _new_features(before, after)
    sb_delta = _delta(before_sb, after_sb)
    return {
        "ok": bool(sb_delta and sb_delta > 0) and result is not None,
        "op": "insert_mid_surface",
        "entry_point": "IFeatureManager.InsertMidSurface（★ 4 参 · 非废弃）",
        "obsolete_note": "★ IModelDoc2.InsertMidSurfaceExt（2 参）与 IModelDoc2.IInsertMidSurfaceExt"
                         "（2 参）**都 Obsolete**；★ ★ 后者点名的后继 "
                         "**`IFeatureManager::IInsertMidSurface` 官方没写**（全库只有 3 个 "
                         "`*MidSurface*` 页）⇒ ★ **链断、无后继签名可抄** ⇒ ★ 不拿非 `I` 前缀那份顶替",
        "returned_is_none": result is None,
        "tree_before": before, "tree_after": after, "new_features": added,
        "surface_body_count_before": before_sb,
        "surface_body_count_after": after_sb,
        "surface_body_count_delta": sb_delta,
        "preconditions_held": bool(body is not None and part_doc is not None),
        "precondition_note": "★ 官方逐字：'The **pPartDocIn** parameter is the **component's model "
                             "document** … and the **pBody** parameter is the **body of that component**'"
                             " ⇒ ★ part_doc 必须是**零件**文档、★ 不是装配文档 / 当前活动文档",
        "no_tool_spec_reason": "★★ Param 只能表达 str/float/int/bool ⇒ **Body2 / ModelDoc2 两个对象形参"
                               "表达不了** ⇒ 能力层写、工具层不建 ToolSpec",
        "unit_assumption": "★ `placement` 官方只说 'the placement position'、**既没给单位也没给量纲**"
                           " ⇒ 原样透传、**不换算**（铁律 5）",
        "verified_by": "surface-body-count delta + returned object non-None + feature tree delta",
    }


# ── ★★ 本模块**不做**的，以及为什么（★ 铁律 4 + 铁律 5）────────────────────────────
#
# ① **`IModelDoc2.InsertSheetMetalMiterFlange`（11 参 · 回 void）**：
#    ★ 官方逐字 `Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].`
#    ⇒ 本模块**只走** `IFeatureManager` 那份（14 参 · 回 `Feature`）。
#    ★ ⚠ 这两条**参数个数都不同**（11 vs 14）⇒ ★ 用错**不只是"没反应"**，而是**个数对不上**。
#
# ② **`IFeatureManager.InsertEndCapFeature`（6 参）**：★ Obsolete → 后继 3 ⇒ 不做。
#    ★⚠ 但 **`InsertEndCapFeature2`（7 参 · 末位 `System.object Faces`）不是废弃成员**
#    ⇒ ★ 它是**并列**入口，★ 而末位是**数组形参** ⇒ **工具层 `Param` 表达不了**
#    ⇒ ★ 本模块**不做**（★ 不是"不实现"，★ 是"不在这一批的直入法范围内"）。
#
# ③ **`IFeatureManager.InsertGussetFeature`（15 参）**：★ Obsolete → 后继 3 ⇒ 不做。
#    ★⚠ `InsertGussetFeature2`（16 参 · 末位 `System.object Faces`）同理 —— **不是废弃**，
#      ★ 但**官方在此断链**（中间代页无 Obsolete 句）⇒ ★ 本模块**只做 3**，并把断链写进返回值。
#
# ④ **`IModelDoc2.InsertMidSurfaceExt` / `IInsertMidSurfaceExt`**：★ 都 Obsolete ⇒ 不做。
#    ★★ 而 `IInsertMidSurfaceExt` 点名的后继 `IFeatureManager::IInsertMidSurface`
#      **官方没写**（全库只有 3 个 `*MidSurface*` 页）⇒ ★ **查不到** ⇒ ★ 不顶替（铁律 5）。
#
# ⑤ **`IClosedCornerFeatureData` / `IEndCapFeatureData` / `IGussetFeatureData` /
#    `ISMGussetFeatureData` / `IMiterFlangeFeatureData` 那几条「指针路」**：
#    ★ 它们的 `AccessSelections` 是**进程内指针接口**，★ 本仓 pywin32 迟到绑定**到不了**
#      （本仓已知事实 47：`ISketchedBendFeatureData.AccessSelections` 等七种形态全部
#      `类型不匹配` / `0x80010105`）⇒ ★ 本模块**只做直入法**，★ 不碰指针族。
#    ★★ 但**不得**因此断言"这两个族建不出来" —— ★ **反例就在本批**：
#      `ISplitLineFeatureData` 同样是 `AccessSelections` 族，★ 而它的**直入法真机建成了**
#      （本仓已知事实 484）⇒ ★★ **"带 AccessSelections" 不等于 "建不出来"**，
#      ★ 判据永远是**"这条直入路本身能不能走"**，★ 不是"接口上有没有那个指针方法"。


def create_midsurface(model, *, body_index: int = 0, placement: float = 0.0,
                      knit: bool = False) -> dict:
    """★ **曲面中面（按体号给的入口）** —— 把 `insert_mid_surface` 那两个**对象形参**解析成可声明的入参。"""
    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（**转接层** —— 实现仍在同文件的 `insert_mid_surface`，本函数不重写实现）
    # 文件:   scripts/sw_sheet_metal_weld_entry.py
    # 定位:   ★★ **为什么要这一层**：`insert_mid_surface(model, body, part_doc, …)` 的 `body` / `part_doc`
    #   是 `IBody2` / `IModelDoc2` **对象** ⇒ ★ `ToolSpec.Param` 只能表达 str/float/int/bool
    #   ⇒ ★ 没有这一层，中面**挂不上工具**。★ 而它是 `capabilities.yaml` 里 `level: verified`
    #   却**没暴露成工具**的一条（见 `specs/202-user-coverage-gaps/recon/scan-S2b-ledger-vs-tools.md` 的 A 表）。
    #   ★ 做法（★ 与仓内既有"按序号给对象"同一手法）：
    #     · `body_index` = **实体体号** ⇒ 用 **`IPartDoc.GetBodies2(Int32 Type, Boolean VisibleOnly)`**
    #       （★ 仓内 `sw_hole_features.py:883` / `sw_curve_and_split.py:138` 用的就是这个形态，
    #        `Type=0` = `swSolidBody`）
    #     · `part_doc` = **同一个 `model`** —— ★ 官方 Remarks 逐字：`pPartDocIn` 是**该组件的模型文档**
    #       ⇒ ★ 在本工具的口径下就是**当前活动文档** ⇒ ★ 本函数**要求活动文档是零件**，并**如实报告**取到几个体。
    # 官方依据: `C:\swapi\types\IFeatureManager\InsertMidSurface.md`
    #   ★ 逐字前置：「The **pPartDocIn** parameter is the **component's model document** where you want to
    #   add the midsurface feature, and the **pBody** parameter is the **body of that component**.」
    #   ★ 逐字语义：「Each reference surface is considered a **sheet body**」·
    #     「all the reference surfaces are **sewn** into a single reference surface if `knitFlag` is true」
    #   ★ `placement` 官方**既没说单位也没说量纲** ⇒ ★ 原样透传（铁律 5）。
    # 许可:   本仓库 MIT。★ 无第三方代码引入。
    # 覆盖:   全文件
    # ─────────────────────────────────────────────────────────────────
    if model is None:
        return {"ok": False, "op": "create_midsurface", "error": "model 为 None"}
    try:
        bodies = list(get_com_member(model, "GetBodies2", 0, False) or [])
    except Exception as exc:                                            # noqa: BLE001
        return {"ok": False, "op": "create_midsurface", "route": "GetBodies2(0, False)",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    out = {"op": "create_midsurface", "route": "GetBodies2(0, False)",
           "body_count": len(bodies), "body_index": int(body_index),
           "verified_by": "曲面体数增量 + 返回对象非 None + 树增量（★ 由 insert_mid_surface 回读）"}
    if not bodies:
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = ("★ 前置未成立：`GetBodies2(0, False)` 回空 ⇒ ★ 活动文档可能**不是零件**，"
                        "或该零件没有实体体")
        return out
    if not (0 <= int(body_index) < len(bodies)):
        out["ok"] = False
        out["preconditions_held"] = False
        out["error"] = ("★ 前置未成立：body_index=%d 越界（该文档有 %d 个体）"
                        % (body_index, len(bodies)))
        return out
    out["preconditions_held"] = True
    res = insert_mid_surface(model, bodies[int(body_index)], model,
                             placement=float(placement), knit_flag=bool(knit))
    out["ok"] = bool(res.get("ok")) if isinstance(res, dict) else bool(res)
    out["inner"] = res
    return out