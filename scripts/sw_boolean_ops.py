"""★ 零件级**布尔 / 多体**操作 —— 相交（`PreIntersect2` → `PostIntersect`，官方两步）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」· 铁律 3（落在 `scripts/` 白名单内）
# 文件:   scripts/sw_boolean_ops.py（**新建** —— 本仓既有零件特征模块里**没有多体/布尔这一族**；
#   ★ 裁决书 §九 指定的落点就是它）✓
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-3** · 外部项目 idx **181 `interse
#           ct`**。
#   ★★ 裁决书逐字：「真名是**两步** `PreIntersect2` → `PostIntersect`；RegionType 三值表 +
#   示例 mark=0 + 排除数组形状齐备；★ 读侧 `IIntersectFeatureData` **零指针族** ⇒
#   ★ 唯一要实测的只有 `System.object` 布尔 **SafeArray 的包装**」✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
#   · `C:\swapi\types\IFeatureManager\PreIntersect2.md` ——
#     `System.object PreIntersect2(System.bool CapPlanar, System.int RegionType)`
#     ★ `## Parameters` 逐字给出 **RegionType 三值**：
#       `0 = Intersecting regions` · `1 = Internal regions` · `2 = Intersecting and internal regions`
#     ★★ `## Remarks` 逐字：「**Before calling this method, you must select the intersecting
#       surfaces, solids, or planes** that make up the intersect feature.」+
#       「After calling this method, call `IFeatureManager::PostIntersect` to create the intersect feature.」
#   · `C:\swapi\types\IFeatureManager\PostIntersect.md` ——
#     `Feature PostIntersect(System.object IntersectionsToExclude, System.bool Merge, System.bool Consume)`
#     ★ `## Parameters` 逐字：`IntersectionsToExclude` 是「**Array of booleans** indicating which
#       bodies returned by `PreIntersect` to **exclude**」· `Merge` = 合并成一个体 ·
#       `Consume` = 把输入曲面从特征树里**移除**
#   · `C:\swapi\types\IIntersectFeatureData\{GetIntersectionsCount,GetIntersections,CapPlanar,Merge,Consume}.md`
#     —— ★ 读侧（`GetIntersectionsCount()` **零参回 int** ⇒ 本模块拿它当回读判据；
#       ⚠ `GetIntersections(out Excluded)` 有 **out 参** ⇒ 本模块**不用它**，见 limitations）✓
#   · ★★ `C:\swapi\examples\Create_Intersect_Feature_Example_VB.md` —— **调用序**（逐字）：
#     ```
#     status = swModelDocExt.SelectByID2("Shell1", "SOLIDBODY", 0,0,0, True, 0, Nothing, 0)
#     status = swModelDocExt.SelectByID2("Plane6", "PLANE",     0,0,0, True, 0, Nothing, 0)   ← 都 mark 0
#     bodyArray = swFeatureMgr.PreIntersect2(False, 1)          ← CapPlanar=False, 内部区域
#     swModel.ClearSelection2 True
#     nbrBodies = UBound(bodyArray)
#     ReDim bodyExcludeArray(nbrBodies)                         ← ★ 元素数 = 体数
#     For i = 0 To nbrBodies : bodyExcludeArray(i) = False : Next
#     excludeArray = bodyExcludeArray
#     Set swFeature = swFeatureMgr.PostIntersect(excludeArray, True, False)
#     ```
# 许可:   本仓库 MIT。无第三方代码引入（★ 全部按官方签名与官方示例自建）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **数组实参必须包 `VARIANT`**（★ 本仓的既有教训，不是猜的）：
#   `scripts/sketch_relations.py` 逐字记着「★★★ **必须包 `VARIANT(VT_ARRAY | VT_R8)`** ——
#   裸 `list`/`tuple` 会**静默返回 `None`**（轮 183 实测）」⇒ ★ 本模块的布尔数组
#   一律包 **`VARIANT(VT_ARRAY | VT_BOOL)`** ✓
#   ⚠ 而 `PostIntersect` 的第 1 参是 **`System.object`** ⇒ ★★ **它到底吃不吃这个包装**，
#     是**本轮唯一要真机验的东西**（裁决书原话）✓
# ★★ **判据**（规则 6）：① `PreIntersect2` 回的**体数组长度**（★ 它回 `System.object`）；
#   ② **特征树增量**（`PostIntersect` 回的 `IFeature` **不当判据**）；
#   ③ ★ **`IIntersectFeatureData::GetIntersectionsCount()`**（零参回 int）✓

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _p in (_HERE.parent, _HERE.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from sw_connect import get_com_member  # noqa: E402
from sw_preflight import import_com_dependencies  # noqa: E402

pythoncom, win32com, VARIANT = import_com_dependencies()

__all__ = ["REGION_TYPES", "as_bool_variant", "create_intersect"]

#: ★ 官方 `PreIntersect2` 的 `RegionType` **三值表**（★ 逐字抄自该页 `## Parameters`；★ **不许跨条复制**）
#: enum-gate: member PreIntersect2
REGION_TYPES = {
    "intersecting": 0,                 # Intersecting regions
    "internal": 1,                     # Internal regions
    "intersecting_and_internal": 2,    # Intersecting and internal regions
}


def as_bool_variant(values) -> "object":
    """★ 把布尔序列包成 **`VARIANT(VT_ARRAY | VT_BOOL)`**（★ 裸 list 会**静默回 None**）。

    ★★ 依据：本仓 `scripts/sketch_relations.py` 的真机教训（轮 183）——
      「数组实参**必须包 `VARIANT`**，裸 `list`/`tuple` 会静默返回 `None`」✓
    """
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_BOOL, [bool(v) for v in values])


def _feature_names(model) -> list:
    out = []
    feat = get_com_member(model, "FirstFeature")
    n = 0
    while feat is not None and n < 4096:
        out.append(str(get_com_member(feat, "Name") or ""))
        feat = get_com_member(feat, "GetNextFeature")
        n += 1
    return out


def create_intersect(model, selection: str = "__current_selection__", *,
                     cap_planar: bool = False,
                     region_type: str = "intersecting_and_internal",
                     exclude: str = "", merge: bool = True,
                     consume: bool = False) -> dict:
    """★ **相交（Intersect）**：官方**两步** `PreIntersect2` → `PostIntersect`。

    :param selection: **声明式选择器**（★ 规则 3）：
        · `"__current_selection__"` —— 用当前选区（★ 调用方自己先选好）；
        · 或**逗号分隔的 `<类型>:<名字>`**（★ 官方示例就是按**名字 + 类型**选：
          `SelectByID2("Shell1", "SOLIDBODY", …)` / `SelectByID2("Plane6", "PLANE", …)`），
          例如 `"SOLIDBODY:凸台-拉伸1,PLANE:上视基准面"`；★ 省略类型时默认 `SOLIDBODY`。
    :param cap_planar: 官方 `CapPlanar` —— `True` 把曲面的平面开口**封盖**成闭合体积。
    :param region_type: `"intersecting"`(0) / `"internal"`(1) / `"intersecting_and_internal"`(2)。
    :param exclude: **要排除的体序号**（逗号分隔，0 基）—— 对应官方 `IntersectionsToExclude`
        那个**布尔数组**（★ 本函数替你把它拼成**与体数等长**的数组）✓
    :param merge: 官方 `Merge` —— 把所有相交区域**合并成一个体**。
    :param consume: 官方 `Consume` —— 把**输入曲面从特征树里移除**（⚠ 有副作用）。
    :returns: `{ok, entry_used, selection_count, pre_bodies, exclude_array_len, exclude_flagged,
        feature, tree_before, tree_after, new_features, intersections_count, error}`

    ★★ **判据（规则 6）**：① `PreIntersect2` 回的**体数组长度**（★ 它回 `System.object`）；
      ② **特征树增量**（★ `PostIntersect` 回的 `IFeature` **不当判据**）；
      ③ ★ **`IIntersectFeatureData::GetIntersectionsCount()`**（零参回 int）✓
    """
    from sw_part import _empty_callout                                 # noqa: E402
    out: dict = {
        "ok": False, "entry_used": "IFeatureManager::PreIntersect2 → PostIntersect",
        "selection": str(selection)[:120], "selection_count": None, "pre_bodies": None,
        "exclude_array_len": None, "exclude_flagged": None, "feature": None,
        "feature_type": None, "tree_before": None, "tree_after": None, "new_features": None,
        "intersections_count": None, "region_type": None, "error": None, "note": None,
        "★": "判据 = **PreIntersect2 回的体数** + **特征树增量** + "
             "**`IIntersectFeatureData::GetIntersectionsCount()`**；★ 不拿回的那个 IFeature 当判据",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    rt = str(region_type).strip().lower()
    if rt not in REGION_TYPES:
        out["error"] = ("未知的 region_type %r；合法：%s"
                        % (region_type, ", ".join(sorted(REGION_TYPES))))
        return out
    out["region_type"] = rt
    try:
        names_before = _feature_names(model)
        out["tree_before"] = len(names_before)
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = "前置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    sel = str(selection or "").strip() or "__current_selection__"
    try:
        #: ★ 官方示例的调用序：**先选相交的面/实体/基准面**（都 mark 0）
        get_com_member(model, "ClearSelection2", True)
        if sel != "__current_selection__":
            ext = get_com_member(model, "Extension")
            for k, item in enumerate([x.strip() for x in sel.split(",") if x.strip()]):
                type_name, _, name = item.partition(":")
                if not name:                                           #: 只给名字 ⇒ 默认实体
                    type_name, name = "SOLIDBODY", type_name
                get_com_member(ext, "SelectByID2", name.strip(), type_name.strip().upper(),
                               0.0, 0.0, 0.0, bool(k > 0), 0, _empty_callout(), 0)
        out["selection_count"] = int(
            get_com_member(get_com_member(model, "SelectionManager"),
                           "GetSelectedObjectCount2", -1) or 0)
        if out["selection_count"] <= 0:
            out["error"] = ("选完**回读计数为 0** ⇒ 没有可相交的对象在选区里（★ 事实 8）"
                            "—— ★ 官方 Remarks 逐字要求**先选中**相交的曲面/实体/基准面")
            return out
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = "选择失败：%s: %s" % (type(exc).__name__, str(exc)[:180])
        return out
    #: ① PreIntersect2
    try:
        fm = get_com_member(model, "FeatureManager")
        bodies = get_com_member(fm, "PreIntersect2", bool(cap_planar), int(REGION_TYPES[rt]))
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = "PreIntersect2 失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    body_list = [b for b in (bodies or [])] if bodies is not None else []
    out["pre_bodies"] = len(body_list)
    if not body_list:
        out["error"] = ("`PreIntersect2` **一个相交体都没回**（★ 它回 `System.object`）"
                        "⇒ 前置可能不成立（选的对象不相交 / cap_planar 与 region_type 组合不产生区域）"
                        "—— ★ 本函数**不据此继续调 PostIntersect**（那只会造出一个空特征）")
        return out
    #: ★ 官方示例：清选区 → 拼**与体数等长**的布尔数组（全 False = 一个都不排除）
    try:
        get_com_member(model, "ClearSelection2", True)
        want_exclude = {int(x) for x in str(exclude).split(",") if x.strip()}
        flags = [(i in want_exclude) for i in range(len(body_list))]
        out["exclude_array_len"] = len(flags)
        out["exclude_flagged"] = [i for i, f in enumerate(flags) if f]
        wrapped = as_bool_variant(flags)                #: ★★ 唯一要真机验的包装
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = "拼排除数组失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    #: ② PostIntersect
    try:
        feature = get_com_member(fm, "PostIntersect", wrapped, bool(merge), bool(consume))
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = ("PostIntersect 失败：%s: %s（★ 这一路只有 `System.object` 一个变量 —— "
                        "布尔 SafeArray 的包装）" % (type(exc).__name__, str(exc)[:200]))
        return out
    out["feature"] = str(get_com_member(feature, "Name") or "") if feature is not None else None
    if feature is None:
        out["error"] = ("`PostIntersect` 回 None ⇒ **相交特征没建出来**（★ 在 pywin32 下"
                        "返回 None 就是失败，★ 不靠「没报错」下结论）")
    #: ③ 回读：特征树增量 + `GetIntersectionsCount()`
    try:
        names_after = _feature_names(model)
        out["tree_after"] = len(names_after)
        out["new_features"] = [n for n in names_after if n not in names_before]
    except Exception as exc:                                           # noqa: BLE001
        out["error"] = "后置回读失败：%s" % str(exc)[:150]
        return out
    try:
        if feature is not None:
            data = get_com_member(feature, "GetDefinition")
            if data is not None:
                out["intersections_count"] = int(
                    get_com_member(data, "GetIntersectionsCount") or 0)
    except Exception as exc:                                           # noqa: BLE001
        out["note"] = "IIntersectFeatureData 读回失败（不影响主判据）：%s" % str(exc)[:120]
    built = (out["tree_after"] > out["tree_before"]) and bool(out["new_features"])
    out["ok"] = bool(built and feature is not None)
    if not out["ok"] and not out["error"]:
        out["error"] = ("回读判据未过：特征树 %r → %r · 新特征 %r · 相交数 %r"
                        % (out["tree_before"], out["tree_after"], out["new_features"],
                           out["intersections_count"]))
    return out
