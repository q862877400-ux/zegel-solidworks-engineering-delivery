"""**建特征之后的回读判据**（本项目规则 6：「建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功」）。

## ★★★ 为什么单独一个模块
```
★ 规则 6 要求"建特征之后不静默成功"，★ 而**这条判据此前只散落在各模块里**：
    · `sw_document_data.py` 的三处 `EditRebuild3`（配置/尺寸那条线）
    · `sw_weldment.py` 的两处（焊件那条线）
  ⇒ ★★ **没有**一个"给任意特征用"的通用回读助手**（★ 这是 §5.0 的"找过"记录：
     查了 `sw_part` 的 33 个公开函数 + 全仓库 `EditRebuild3` / `GetWhatsWrong2` / `GetFeatureByName`）。
⇒ ★ 所以本模块补上它 —— ★ **它是"修地基"级别的**：往后每个建特征的工具都可以用它。
```

## ★★ 判据是什么（★ 不发明，照规则 6）
```
① **特征真的在特征树里**（按名回读 —— ★ 不信返回值）
② **`EditRebuild3` 回 True**
③ **`GetWhatsWrong2` 的错误数为 0**（★ 有错就把错的条目带回来）
⇒ ★ 三条都过才 `ok=True`。★ 任何一条不过 ⇒ **如实报，不静默**。
```

## ⚠ 为什么必须按名回读（本项目既有教训）
```
★ 已知事实 8：「`ISelectionMgr.AddSelectionListObject` 的 bool 返回值**不可信**，
  用 `GetSelectedObjectCount2(-1)` 回读」
★ 已知事实 40：「`IModeler.Create*Surface` 的返回值**跨次都变** ⇒ 修的只能是"让失败可见"」
⇒ ★★ 同一条铁律：**COM 返回值凡不能自证，一律以回读为判据**。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_feature_readback.py
# 定位:   通用"特征建成回读"判据（落实 `docs/union-conventions.md` 规则 6）。
# 官方依据: `IModelDoc2.EditRebuild3`（bool）· `IModelDoc2.GetWhatsWrong2`（按 by-ref 数组出参）
#          · `IModelDoc2.FirstFeature` / `IFeature.GetNextFeature`（遍历特征树按名找）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 只做**读取与重建**，不做保存。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import call_com_member, get_com_member, safe_get_com_member
except ImportError:                                            # pragma: no cover
    from sw_connect import call_com_member, get_com_member, safe_get_com_member

__all__ = ["feature_names", "feature_present", "whats_wrong", "feature_readback",
           "extrude_depth", "extrude_params", "pattern_params", "hole_params", "feature_info", "fillet_params", "csys_params", "base_flange_params", "shell_params", "rib_params", "dome_params", "sweep_params", "revolve_params", "loft_params"]


#: ★ FeatureManager 顶部的**容器节点**（不是特征）—— 实测回的是这些名字
#:   （2026-10-01 轮 249）。★ 但**枚举名字是脆的**（UI 语言一变就失效），
#:   所以真正的判据在下面：★ **用 `GetTypeName2` 判"它有没有特征类型"**（结构性判据）。
_CONTAINER_NODES = frozenset({
    "收藏", "历史记录", "选择集", "传感器", "设计活页夹", "注解", "材质",
    "标注", "光源与相机", "实体", "曲面实体", "备注", "方程式", "材质 <未指定>",
    "Favorites", "History", "Selection Sets", "Sensors", "Design Binder",
    "Annotations", "Material", "Callouts", "Lights and Cameras", "Solid Bodies",
    "Surface Bodies", "Notes", "Equations",
})


def _is_real_feature(feat) -> bool:
    """★ **结构性判据**：这个节点**有没有特征类型名**（`GetTypeName2`）。

    ★★ 为什么用它而不是只枚举中文名：★ **基准面（`RefPlane`）也是合法特征**，
      而容器节点（`实体` / `曲面实体` / `方程式` / `备注` …）**没有类型名**。
      ⇒ ★ 这样判**不依赖 UI 语言**（★ 枚举名字在英文界面下会全部失效）。
    """
    try:
        return bool(safe_get_com_member(feat, "GetTypeName2"))
    except Exception:                                          # noqa: BLE001
        return False


def feature_names(model, limit: int = 400) -> list[str]:
    """遍历特征树，回**有序的特征名清单**（★ 按名回读的基础）。

    ★★ **两层过滤**（2026-10-01 轮 249）：
      ① ★ **结构性**：只收 `GetTypeName2` 非空的节点（⇒ 容器被排除，**与 UI 语言无关**）；
      ② ★ **兜底**：再排除已知容器名（`_CONTAINER_NODES`）。
    ⚠ 不过滤会让"按名找特征"**假通过**（★ 名字撞上容器）。
    """
    names: list[str] = []
    try:
        feat = get_com_member(model, "FirstFeature")
        while feat is not None and len(names) < limit:
            n = safe_get_com_member(feat, "Name")
            if n and str(n) not in _CONTAINER_NODES and _is_real_feature(feat):
                names.append(str(n))
            feat = safe_get_com_member(feat, "GetNextFeature")
    except Exception:                                          # noqa: BLE001
        pass
    return names


def feature_present(model, feature_name: str) -> bool:
    """★ 按名判断特征**是否真的在特征树里**（★ 不信任何返回值）。"""
    if not feature_name:
        return False
    return str(feature_name) in feature_names(model)


def whats_wrong(model) -> dict[str, Any]:
    """取 「What's Wrong」的条目数（★ 数 0 才是好）。

    ★★ **成员名与宿主都核过两套官方源**（2026-10-01 轮 249）：
      · ★ `IModelDocExtension.` **`GetWhatsWrongCount`** —— 签名 ``System.int GetWhatsWrongCount()``
        （**零参、直接回个数** ⇒ ★ 比 `GetWhatsWrong`（三参 by-ref）简单得多）
      · ⚠ **`GetWhatsWrong2` 在本机两套源里都**不存在**** —— ★ 而
        `docs/union-conventions.md` **规则 6 的措辞**写的正是 `GetWhatsWrong2`
        ⇒ ★ **那是规则文本的一处失真**（★ 规则里写的成员名**也要核**）。
      · ⚠ 它**挂在 `IModelDocExtension` 上**（不是 `IModelDoc2`）⇒ ★ **必须从 `model.Extension` 取**
        （本函数初版直接对 model 调 ⇒ 取不到 ⇒ ★ 判据按设计报"不算通过"，**没有静默成 0**）。
    取不到时**如实报 "取不到"**（★ 不静默成 0 —— 那样就成了"假通过"）。
    """
    out: dict[str, Any] = {"count": None, "entries": [], "error": None,
                           "source_member": "IModelDocExtension.GetWhatsWrongCount"}
    try:
        ext = get_com_member(model, "Extension")
        out["count"] = int(call_com_member(ext, "GetWhatsWrongCount") or 0)
        if out["count"] > 0:
            #: ★ 有错时再去取明细（三参 by-ref；★ 取不到就只报数，不静默）
            try:
                import pythoncom
                from win32com.client import VARIANT

                v_f = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
                v_c = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
                v_w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
                call_com_member(ext, "GetWhatsWrong", v_f, v_c, v_w)
                feats = v_f.value
                if feats:
                    out["entries"] = [str(x)[:200] for x in list(feats)[:10]]
            except Exception as exc:                           # noqa: BLE001
                out["entries_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    return out


def feature_readback(model, feature_name: str, *, do_rebuild: bool = True) -> dict[str, Any]:
    """★ **建特征之后的回读判据**（项目规则 6）。

    :param model: 活动文档。
    :param feature_name: 期望出现的特征名（★ 中文 UI 下形如「抽壳1」/ 「筋1」/「圆顶1」）。
    :param do_rebuild: 是否先 `EditRebuild3`（默认 True —— 规则 6 要求）。
    :returns: ``{"ok", "feature_name", "present", "names_sample", "rebuild_ok",
                 "whats_wrong_count", "whats_wrong_entries", "reason"}``
        ★★ **`ok` 三条都真才算**：特征在树里 **且** 重建成功 **且** 查错数为 0。
    """
    res: dict[str, Any] = {"feature_name": str(feature_name), "present": False,
                           "rebuild_ok": None, "whats_wrong_count": None,
                           "whats_wrong_entries": [], "reason": "",
                           "★": "规则 6：特征在树里 + EditRebuild3 真 + GetWhatsWrong2 数 0"}
    try:
        if do_rebuild:
            res["rebuild_ok"] = bool(call_com_member(model, "EditRebuild3"))
        res["present"] = feature_present(model, feature_name)
        ww = whats_wrong(model)
        res["whats_wrong_count"] = ww.get("count")
        res["whats_wrong_entries"] = ww.get("entries") or []
        c = feature_names(model)
        res["names_sample"] = c[-12:]                          #: ★ 尾部（新特征在末尾）

        reasons = []
        if not res["present"]:
            reasons.append("特征名 %r 不在特征树里（★ 可能没建出来，或名字与 UI 语言不符）"
                           % feature_name)
        if do_rebuild and res["rebuild_ok"] is False:
            reasons.append("EditRebuild3 返回 False ⇒ 重建失败")
        if res["whats_wrong_count"] is None:
            reasons.append("GetWhatsWrong2 取不到（★ **不算通过** —— 不静默成 0）")
        elif res["whats_wrong_count"] > 0:
            reasons.append("GetWhatsWrong2 报 %d 条错：%s"
                           % (res["whats_wrong_count"], res["whats_wrong_entries"][:2]))
        res["reason"] = "；".join(reasons)
        res["ok"] = not reasons
    except Exception as exc:                                   # noqa: BLE001
        res["reason"] = "回读判据自身出错（★ 不算通过）：%s: %s" % (type(exc).__name__,
                                                                    str(exc)[:160])
        res["ok"] = False
    return res


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::extrude_depth`（★ 新增）
# 定位:   ★ 阶段 3（T2 缺口地图）⇒ ★★ 密度图算出 **查 × 特征 = 官方 451 · 我们 0** ⇒
#   ★★★ 而那一格实际有 **1008 个成员 / 174 个族**（★ 现算）⇒ ★ 本函数是**第一个** ✓
#   ★★★★ **官方逐字**（★ `IExtrudeFeatureData2/GetDepth.md`）：
#     ★ `System.double GetDepth( System.bool Forward )` ·
#     ★★ `## Parameters`：★ `Forward` = True for forward / false for reverse ·
#     ★★★ `## Returns`：★ 「**Depth of the extrusion**」——
#       ★★ **⚠ 官方**没写单位**** ⇒ ★ 铁律 5：★ **不许替它假定** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def extrude_depth(model, feature_name: str = "", *, forward: bool = True) -> dict:
    """★ 读**拉伸特征的深度**（★ `IExtrudeFeatureData2::GetDepth`）✓

    ★★★★★ **单位读数（★ 真机实测、★ 与"官方吃米"的假设**相反**）** ——
      ★ `tools/probe_extrudefeaturedata_getdepth.py`（★ `sw_guard` · ★ `sw_alive: true` ·
      ★ **零弹窗** ⇒ `output/extrudefeaturedata-getdepth-evidence.json`）：
      ★ **本仓用 `extrude_boss(depth=20)`（★ 本模块长度单位 = 毫米）建一个凸台** ⇒
        ★ 特征名 **`凸台-拉伸1`** · ★ 型 **`Extrusion`** ✓
      ★★ **`GetDepth(True)` 回 `20.0`** —— ★ **不是 0.02** ⇒
        ★★★ **⇒ 它随**文档单位**（★ 本机 `GetUnits() = [0, …]` ⇒ `LengthUnit = 0` = **毫米**）** ✓
      ★★★ **⚠ 而"独立锚点"那一步**失败得很有价值**：★ 我本想用 `IBody2::GetBodyBox` 锚定单位 ⇒
        ★★ **而它自己**混口径**** —— ★ 实测回 `[-0.05, -0.03, -20.0, 0.05, 0.03, 0.0]`：
        ★ **X 是 ±0.05（**米** = 100mm）· ★ Z 是 -20.0…0.0（**毫米** = 20mm）** ✓
        ⇒ ★★★ **⇒ 同一个成员的六个分量里混了两套口径** ⇒ **它不可当锚点** ✓
        ⇒ ★★★★ **可复用判据**：★★★ **"找一个独立的量来锚定单位"这条判据，
          要先证明**那个量自己是干净的**** ——
          ★ 否则**你会拿一个混口径的东西去校准另一个** ✓
          （★ 与**事实 40**同族：★ **一个读数如果看起来像正常值，比没有读数更糟**）✓
    ★★★★★ **⚠ 返回值带 `unit_source`** —— ★ **不许让调用方猜单位**：
      ★ `"document"` = 随文档单位（★ **本函数的实测结论**）；
      ★ 而**本函数不替调用方换算** ⇒ ★ 要毫米就自己按 `GetUnits()` 判 ✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out = {"feature": feature_name, "forward": bool(forward),
           "depth": None, "unit_source": "document", "definition": None,
           "end_condition": None, "error": None}
    try:
        feat = None
        if feature_name:
            #: ★★★★ **名字是 `FeatureByName`、★ 不带 `Get`** ——
            #:   我第一版写了 `GetFeatureByName` ⇒ ★★ **被成员名门禁抓到**
            #:   （★ `scripts/check_member_names.py`：★ 「1 个成员名在官方反射里查不到：
            #:     sw_feature_readback.py:230  GetFeatureByName」）✓
            #:   ★★★ **而本仓**27 处**用的都是 `FeatureByName`** ⇒
            #:     逐字见 `sw_assembly.py` L267 与 `sw_sweep.py` L165
            #:     （★ 后者还写明了「★ `IModelDoc2.FeatureByName(name)`（**方法**）」）✓
            #:   ★★★★ **可复用判据**：★★★ **"一个存在但没人用的守卫与没有守卫等价"**
            #:     （★ 事实 40 那一族）—— ★★ **而这里反过来：★ 门禁**确实抓到了一个真错**** ✓
            #:     ⇒ ★ **写新 COM 调用前，先在仓里搜**同名成员怎么用的**（★ 本仓 27 处现成例子）✓
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★ 兜底：★ 找**第一个**「凸台-拉伸」特征（★ 中文 UI 名含「凸台」、★ 也认 `Extrusion` 型）
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if "Extrusion" in tn:
                        feat, out["feature"] = f, str(safe_get_com_member(f, "Name") or "")
                        break
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到拉伸特征（★ 给了名字就按名字、★ 否则找第一个 `Extrusion`）"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        out["depth"] = get_com_member(fd, "GetDepth", bool(forward))
        try:
            out["end_condition"] = get_com_member(fd, "GetEndCondition", bool(forward))
        except Exception:                                                 # noqa: BLE001
            out["end_condition"] = None
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::extrude_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力（★ `查 × 特征` 那一格）⇒ ★ 本函数是**第二个** ✓
#   ★★ **官方逐字（★ 逐个成员读的 `## Returns`）**：
#     · ★ `GetEndCondition(bool Forward)` ⇒ 回 **`swEndConditions_e`**（★ 盲拉 = 0）✓
#     · ★★ **`GetDraftAngle(bool Forward)`** ⇒ 「Draft angle of the extrusion
#       **in radians**」⇒ ★★★ **官方**明写弧度**** ——
#       ★★ **与 `extrude_depth` 的"随文档单位"**相反**** ⇒
#       ★★★ **那正是「单位是**逐成员**的事」的又一例**（★ 本会话早先那条判据）✓
#     · ★ `GetContoursCount()` ⇒ 「Number of selected contours」（★ 一个闭合轮廓 = 1）✓
#     · ★ `ReverseDirection {get;set}` / `BothDirections {get;set}` ⇒ ★ **属性**（★ bool）✓
#     · ★★ `GetFace` ⇒ **已废弃** ⇒ ★ **不用**（★ T1 那批刚处理过）✓
#     · ★ `GetDirectionReference(out Ref1, out Type1, …)` ⇒ ★ **带 out 参数** ⇒
#       ★★ **pywin32 有风险**（★ 事实 47 那一族）⇒ **本函数不碰它** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def extrude_params(model, feature_name: str = "") -> dict:
    """★ 读**拉伸特征的一组参数**（★ 端条件 / 拔模角 / 轮廓数 / 两个方向开关）✓

    ★★★★★ **单位口径（★ 本函数的核心判断 —— 逐成员、★ 不是整族）**：
      ★ `GetDepth` ⇒ ★ **随文档单位**（★ 真机两轮：★ 20mm ⇒ 20.0 ⇒ `unit_source='document'`）✓
      ★★ `GetDraftAngle` ⇒ ★★ **官方明写 `in radians`** ⇒ ★ **不随文档单位** ✓
      ⇒ ★★★ **⇒ 所以本函数的返回值里**每个量各自带口径**、★ 而不是给一个全局口径** ✓
      ★★★★ **可复用判据**：★★★ **「单位口径」是**逐成员**的事 ——
        ★ 同一个接口里的两个成员可以一个随文档、★ 一个写死** ✓
        （★ 与本会话早先那条「官方吃米是逐成员的事、★ 不是整族的事」**同源**）✓
    ★★★ **⚠ `GetFace` 已废弃** ⇒ ★ **本函数不调它**；★ `GetDirectionReference` 带 out ⇒ **也不碰** ✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "forward": {}, "reverse": {}, "★_单位口径": {
                     "depth": "document（★ 真机：20mm ⇒ 20.0）",
                     "draft_angle": "radians（★ 官方逐字 in radians）",
                 }}
    try:
        feat = None
        if feature_name:
            #: ★★ 名字是 `FeatureByName`（★ **不带 `Get`**）——
            #:   ★ 我上一轮写错过、★ 被成员名门禁抓到（★ 见 `extrude_depth` 的说明）✓
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if "Extrusion" in tn:
                        feat, out["feature"] = f, str(safe_get_com_member(f, "Name") or "")
                        break
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到拉伸特征"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        for tag, fwd in (("forward", True), ("reverse", False)):
            row = {}
            for name in ("GetDepth", "GetDraftAngle", "GetEndCondition"):
                try:
                    row[name] = get_com_member(fd, name, fwd)
                except Exception as exc:                                  # noqa: BLE001
                    row[name] = "err: %s" % str(exc)[:60]
            out[tag] = row
        #: ★★ 两个**属性**（★ `{get;set}`）⇒ ★ 用 `get_com_member` 直接取 ✓
        for name in ("ReverseDirection", "BothDirections"):
            try:
                out[name] = bool(get_com_member(fd, name))
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:60]
        try:
            out["GetContoursCount"] = get_com_member(fd, "GetContoursCount")
        except Exception as exc:                                          # noqa: BLE001
            out["GetContoursCount"] = "err: %s" % str(exc)[:60]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ILinearPatternFeatureData\`）
# 文件:   `scripts/sw_feature_readback.py::pattern_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ 本函数是**第三个** ✓
#   ★★ **换了一个族**（★ 前两个都在 `IExtrudeFeatureData2`）⇒ ★ 覆盖面扩大 ✓
#   ★★★ **官方逐字（★ 逐个成员的 `## Returns`）**：
#     · ★★ **`D1Spacing` / `D2Spacing`** ⇒ 「Distance **in meters** between pattern instances」
#       ⇒ ★★★ **官方**明写米**** ✓
#     · ★ `D1TotalInstances` / `D2TotalInstances` ⇒ ★ `int`（★ 实例数）✓
#     · ★ `GetPatternFeatureCount()` ⇒ 「Number of **seed features**」✓
#     · ★ `GetPatternBodyCount()` ⇒ 「Number of **seed bodies**」✓
#     · ★ `GetSkippedItemCount()` ⇒ 「Number of **skipped instances**」✓
#     · ★ `GetD1AxisType()` ⇒ ★ 官方**给了取值表**（0 = axis or ref axis · 1 = edge …）✓
#     · ★ `IsDirection2Specified()` ⇒ 「True if direction 2 is specified」✓
#     · ★ `D1ReverseDirection` / `GeometryPattern` / `D2PatternSeedOnly` / `VarySketch` /
#       `BodyPattern` / `PropagateVisualProperty` ⇒ ★ **属性**（★ bool）✓
#   ★★★★ **⚠ 单位口径的**第三层****（★ 本会话已见三层）：
#     ★ **① `GetDepth`** ⇒ ★ **随文档单位**（★ 真机：20mm ⇒ 20.0）✓
#     ★★ **② `GetDraftAngle`** ⇒ ★ **写死 radians**（★ 官方逐字）✓
#     ★★★ **③ `D1Spacing` / `D2Spacing`** ⇒ ★★ **写死 meters**（★ 官方逐字）✓
#     ⇒ ★★★★★ **可复用判据**：★★★ **「官方 API 吃什么单位」是**逐成员**的事 ——
#       ★ 同一个仓里已经有**三种**口径**：★ **随文档 · 写死弧度 · 写死米**
#       ★★ ⇒ **每读一个量都要单独查它那一页的 `## Returns`** ✓
#       （★ 铁律 5：★ 查不到就写「查不到」、**不许按族推断**）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def pattern_params(model, feature_name: str = "") -> dict:
    """★ 读**线性阵列特征的一组参数**（★ 两个方向的实例数/间距 + 若干开关 + 计数）✓

    ★★★★★ **返回值里逐项标口径** —— ★ 本接口里**两个量是写死米的**：
      ★ `D1Spacing` / `D2Spacing` ⇒ ★ 官方 `## Returns` 逐字「Distance **in meters**」✓
      ★★ 而 `D1TotalInstances` 是**实例数**（★ 无量纲）✓
    ★★★ **⚠ 本函数不替调用方换算** —— ★ 米就是米 ⇒ ★ 要毫米自己乘 1000 ✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "★_单位口径": {
                     "D1Spacing": "meters（★ 官方逐字 in meters）",
                     "D2Spacing": "meters（★ 同上）",
                     "D1TotalInstances": "无量纲（★ 实例数，含原件）",
                     "D2TotalInstances": "无量纲",
                 }}
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★ 兜底：★ 找**最后一个**线性阵列特征（★ 类型名含 `LPattern`）
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if "LPattern" in tn:
                        feat, out["feature"] = f, str(safe_get_com_member(f, "Name") or "")
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到线性阵列特征"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ 属性一类（★ `{get;set}`）⇒ ★ 直接取 ✓
        for name in ("D1TotalInstances", "D1Spacing", "D2TotalInstances", "D2Spacing",
                     "D1ReverseDirection", "D2ReverseDirection", "GeometryPattern",
                     "D2PatternSeedOnly", "VarySketch", "BodyPattern",
                     "PropagateVisualProperty", "D1EndCondition"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ **方法**一类（★ 零参）⇒ ★ 也直接取 ✓
        for name in ("GetPatternFeatureCount", "GetPatternFaceCount", "GetPatternBodyCount",
                     "GetSkippedItemCount", "GetD1AxisType", "GetD2AxisType",
                     "IsDirection2Specified"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\\swapi\\types\\IWizardHoleFeatureData2\\`）
# 文件:   `scripts/sw_feature_readback.py::hole_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ **第四个**、★ **第三个族** ✓
#   ★★ **这一族的官方 `## Returns` **没写单位****（★ 逐个读都是「Hole diameter」这种光名字）⇒
#     ★★★ **铁律 5：★ 单位查不到 ⇒ ★ 返回值要**如实标 `unknown`**、★ 不猜** ✓
#   ★★★ **单位口径的**第四层****（★ 本会话已见四层）：
#     ★ ① `GetDepth` ⇒ **随文档** · ★★ ② `GetDraftAngle` ⇒ **写死 radians** ·
#     ★★★ ③ `D1Spacing` ⇒ **写死 meters** · ★★★★ ④ **本族** ⇒ **官方没写**（★ 未定）✓
#     ⇒ ★★★★★ **可复用判据**：★★★ **「没写单位」≠「随文档单位」** ——
#       ★ 前者是**官方没说**（★ 要真机测 / 如实标未知）、★★ 后者是**实测确认过** ⇒
#       ★★★ **两者在返回值里必须用不同的词** ✓
#   ★★★★ **官方逐字**：★ `Type` ⇒ `swWzdHoleTypes_e` · ★ `EndCondition` ⇒ `swEndConditions_e` ·
#     ★ `CosmeticThreadType` ⇒ `swWzdHoleCosmeticThreadTypes_e` · ★ `ThreadClass` ⇒ `1B`/`2B`/`3B` ·
#     ★ `GetSketchPointCount()` ⇒ 「Number of center-hole sketch points」·
#     ★★ `FastenerType` ⇒ **已废弃** ⇒ **不读** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def hole_params(model, feature_name: str = "") -> dict:
    """★ 读**异型孔向导特征的一组参数**（★ 尺寸 / 标准 / 类型 / 端条件）✓

    ★★★★★ **单位口径（★ 与前三个**都不同** —— ★ 而**本族内部还分裂**）**：
      ★ 本族成员的官方 `## Returns` **只写光名字**（「Hole diameter」）、★ **没写单位** ⇒
      ★★ **本函数如实标 `unknown（★ 官方 ## Returns 未写）`**、★ **不猜** ✓
      ★★★ **而真机测出来了**（★ `tools/probe_hole_params_recheck.py` · ★ `sw_guard` · ★ 零弹窗 ⇒
        `output/hole-params-capability-recheck.json`）——
        ★ 建一个 **`M8` 通孔**（★ 板厚 20mm）⇒ 逐字读数：
        | ★ 成员 | ★ 读数 | ★ 口径 |
        |---|---|---|
        | ★★ **`ThruHoleDiameter`** | ★ **0.008** | ★★ **米**（★ M8 = 8mm）✓ |
        | ★★ **`ThruHoleDepth`** | ★ **20.0** | ★★ **毫米**（★ 板厚 20mm）✓ |
        | ★ `HoleDiameter` | ★ `0.0` | ★ 通孔类型下**不使用它** ✓ |
        | ★ `Standard` / `FastenerSize` | ★ `"ANSI Metric"` / `"M8"` | ★ 字符串 ✓ |
        | ★ `Type` / `EndCondition` | ★ `25` / `1` | ★ 枚举 ✓ |
      ★★★★ **⇒ **同一个接口里两个量的口径不同**！！** ——
        ★ **`ThruHoleDiameter` 是米、★ 而 `ThruHoleDepth` 是毫米** ✓
      ★★★★★ **⇒ 本会话的**第五层**口径**（★ 也是最强的一层）：
        ★ ① `GetDepth` ⇒ **随文档** · ★ ② `GetDraftAngle` ⇒ **写死 radians** ·
        ★ ③ `D1Spacing` ⇒ **写死 meters** · ★ ④ 本族（官方没写）· ★ ⑤ **本族内部**就分裂 ✓
        ⇒ ★★★★ **可复用判据**：★★★ **「没写单位」≠「随文档单位」**、
          ★★ 而 **「同一个接口」也**不**保证同一口径** ——
          ★★★ **每读一个量都要单独真机验**（★ 官方没写时**只能这样**）✓
          （★ 铁律 5：★ 查不到就写「查不到」—— ★ 而本轮**测出来了**、
           ★★ 所以**把实测口径写进返回值**、★★★ 并**保留 "官方未写" 那个事实**）✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    UNK = "unknown（★ 官方 ## Returns 未写；★ 真机实测见 docstring 的表）"
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "★_单位口径": {k: UNK for k in (
                     "HoleDiameter", "HoleDepth", "ThreadDepth", "ThruHoleDiameter",
                     "CounterBoreDiameter", "CounterBoreDepth", "CounterSinkDiameter",
                     "CounterSinkAngle", "HeadClearance")}}
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★ 兜底：★ 找**最后一个**异型孔特征（★ 类型名含 `HoleWzd`）
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if "HoleWzd" in tn or "Wzd" in tn:
                        feat, out["feature"] = f, str(safe_get_com_member(f, "Name") or "")
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到异型孔向导特征"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ 属性（★ `{get;set}`）⇒ ★ 直接取；★ **`FastenerType` 已废弃 ⇒ 不读** ✓
        for name in ("HoleDiameter", "HoleDepth", "ThreadDepth", "ThruHoleDiameter",
                     "ThruHoleDepth", "CounterBoreDiameter", "CounterBoreDepth",
                     "CounterSinkDiameter", "CounterSinkAngle", "HeadClearance",
                     "Standard", "FastenerSize", "ThreadClass", "Type", "EndCondition",
                     "CosmeticThreadType", "ReverseDirection"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ 零参方法 ⇒ ★ 也取 ✓
        try:
            out["GetSketchPointCount"] = get_com_member(fd, "GetSketchPointCount")
        except Exception as exc:                                          # noqa: BLE001
            out["GetSketchPointCount"] = "err: %s" % str(exc)[:50]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\\swapi\\types\\IFeature\\`）
# 文件:   `scripts/sw_feature_readback.py::feature_info`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ **第五个**、★ **第四个族**（★ `IFeature` ×51）✓
#   ★★ **本族先用**新判据**重扫**（★ 上一轮修的 · `tools/check_obsolete_heuristic.py`）：
#     ★ **126 个成员** ⇒ ★ **真废弃 24** · ★★ **没废弃 102** ⇒
#     ★★★ **而旧判据会多报 2 个假阳性**：★ `GetTypeName` · ★ **`GetTypeName2`**
#       ⇒ ★★★★ **⇒ 而 `GetTypeName2` 正是本仓在用的那个** ⇒ **用它是对的** ✓
#   ★★★ **官方逐字（★ 逐个成员的 `## Returns`）**：
#     · ★ `GetID()` ⇒ 「Feature ID of this feature」⇒ **unique within the document** ✓
#     · ★ `GetFaceCount()` ⇒ 「Number of faces in this feature」✓
#     · ★ `Visible` ⇒ `swVisibilityState_e` · ★ `GetEditStatus()` ⇒ `swFeatureEditStatus_e` ✓
#     · ★ `GetMaterialIdName()` ⇒ 「Material name」· ★ `Description` / ★ `CreatedBy` ⇒ 字符串 ✓
#     · ★ `GetChildren()` ⇒ 「Array of child features」· ★ `GetParents()` ⇒ 父特征 ✓
#     · ★★ **`GetBox(out BBox)`** ⇒ ★★★ **官方 `## Remarks` 逐字**：
#       「**IMPORTANT:** The values returned are **approximate** and **should not be used for
#         comparison or calculation purposes**.」⇒ ★★★★ **⇒ **本函数**不用它**** ✓
#       （★ 而本仓 `part_bounding_box` 早已记着同一条 ⇒ **两处一致**）✓
#   ★★★★ **⚠ 废弃的那 24 个（★ 新判据）⇒ 一个都不碰**：
#     ★ `GetBody` / `GetErrorCode` / `GetSpecificFeature` / `IsSuppressed` / `Select` /
#     ★★ `SetBody` / `SetSuppression` / `MoveFreezeBarTo` … ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def feature_info(model, feature_name: str = "") -> dict:
    """★ 读**一个特征的一组通用属性**（★ 元数据 / 面数 / 可见性 / 子父特征）✓

    ★★★★★ **⚠ 本函数**不读 `GetBox`**** —— ★ 官方 `## Remarks` 逐字：
      「The values returned are **approximate** and **should not be used for comparison or
        calculation purposes**」⇒ ★★ **那是官方明说的"不可核"** ⇒
      ★★★ **要包围盒请用 `part_bounding_box`**（★ 它带着同一条警告）✓
    ★★★ **⚠ 也**不读那 24 个废弃成员****（★ 新判据扫出来的）✓
    ★★★★★★ **⚠ 而"取哪个特征"这条我改了**三次**（★ 值记 —— 三次都不是能力错）**：
      ★ ① 兜底取 `FirstFeature` ⇒ ★ 中文 UI 下回 **`收藏`**（★ `FavoriteFolder` · 容器）⇒
        `GetFaceCount = 0` ✓
      ★★ ② 加 `_is_real_feature` ⇒ ★★ 而它**只判"有没有类型名"**、
        ★ `收藏` 的 `FavoriteFolder` **是一个类型名** ⇒ **仍回 `收藏`** ⇒
        ★★ 改成**两层过滤**（★ 名字不在 `_CONTAINER_NODES` + ★ `_is_real_feature`）✓
      ★★★ ③ 过了两层 ⇒ 回 **`前视基准面`**（★ `RefPlane` · ★ **官方文档说基准面也是合法特征**）⇒
        ★★ **而 `GetFaceCount = 0` 是**应然的****（★ 基准面没有面）⇒
        ★★★ **⇒ 是我的判据「面数 = 6」只对**拉伸**成立** ⇒ **要按名字取那个拉伸** ✓
      ★★★★ **⇒ 三次全是**判据/兜底**的错、★ 能力一直是对的**（★ 事实 51 的第三次实例）✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "error": None}
    try:
        feat = None
        if feature_name:
            #: ★ 名字是 `FeatureByName`（★ **不带 `Get`**）✓
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★★★★ **兜底要过**两层**过滤**（★ 我第一版只过了第二层）——
            #:   ★ 真机回的是 **`收藏`**（★ `GetTypeName2 = FavoriteFolder`）⇒ ★★ **`GetFaceCount = 0`** ✓
            #:   ★★★ **根因**：★ `_is_real_feature` 只判"**有没有类型名**" ⇒
            #:     而 `收藏` 的 `FavoriteFolder` **是一个类型名** ⇒ **它漏了这类"有类型名的容器"** ✓
            #:   ★★★★ **修法**：★ **照 `feature_names()` 的**两层过滤**** ——
            #:     ① 名字不在 `_CONTAINER_NODES` 里 · ★★ ② `_is_real_feature` ✓
            #:     （★ 第一层就是 `feature_names` 早就在用的那个）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                nm = str(safe_get_com_member(f, "Name") or "")
                if nm not in _CONTAINER_NODES and _is_real_feature(f):
                    feat = f
                    break
                f = safe_get_com_member(f, "GetNextFeature")
            out["feature"] = str(safe_get_com_member(feat, "Name") or "") if feat is not None else ""
        if feat is None:
            out["error"] = "没有特征"
            return out
        #: ★★ 属性（★ `{get;}` / `{get;set}`）⇒ ★ 直接取 ✓
        for name in ("Name", "Description", "CreatedBy", "Visible", "GetMaterialIdName"):
            try:
                out[name] = get_com_member(feat, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ 零参方法 ⇒ ★ 也取 ✓
        for name in ("GetID", "GetFaceCount", "GetEditStatus", "GetTypeName2", "GetChildren",
                     "GetParents"):
            try:
                v = get_com_member(feat, name)
                #: ★ 数组类：★ 取长度（★ 回 `None` 就是空）✓
                if name in ("GetChildren", "GetParents"):
                    out[name] = len(list(v)) if v is not None else 0
                else:
                    out[name] = v
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★ **⚠ 读 `GetTypeName2` 是**对的**** —— ★ 上一轮修的判据证明它**没废弃** ✓
        #:   （★ 旧判据 `"Obsolete" in t` 会把它误报成废弃 ⇒ ★ **而本函数按新判据**）
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\\swapi\\types\\ISimpleFilletFeatureData2\\`）
# 文件:   `scripts/sw_feature_readback.py::fillet_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ **第六个**、★ **第五个族** ✓
#   ★★ **官方逐字（★ 逐个成员的 `## Returns`）**：
#     · ★ `DefaultRadius {get;set}` ⇒ 「Default radius of the **symmetric** fillet」✓
#     · ★ `Type {get;}` ⇒ `swSimpleFilletType_e` · ★ `OverflowType` ⇒ `swFilletOverFlowType_e` ✓
#     · ★ `GetEdgeCount()` ⇒ 「Number of edges」✓
#     · ★ `GetSetbackVerticesCount()` ⇒ 「Number of setback vertices」✓
#     · ★ `RoundCorners` / ★ `KeepFeatures` / ★ `ConstantWidth` /
#       ★ `PropagateToTangentFaces` ⇒ bool ✓
#     · ★★ `GetRadius(PFilletItem)` / ★ `GetDistance` / ★ `GetConicRhoOrRadius` ⇒
#       ★ **要一个 item 对象**（★ 得先 `IGetFilletEdgeAtIndex`）⇒ **本函数不碰**（★ 多一步）✓
#   ★★★ **单位口径（★ 第六层）**：★ `DefaultRadius` 的 `## Returns` **没写单位** ⇒
#     ★★ **按铁律 5：★ 如实标 `unknown`、★ 并真机测**（★ 见 `tools/probe_fillet_params_recheck.py`）✓
#   ★★★★ **⚠ 前置**：★ 本仓 `fillet(model, selection, radius_mm)` 需要**先选中一条边**
#     （★ 而边没有名字 ⇒ ★ 按 `index:<n>` 选 · ★ 见已知事实 32）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def fillet_params(model, feature_name: str = "") -> dict:
    """★ 读**简单圆角特征的一组参数**（★ 默认半径 / 类型 / 边数 / 若干开关）✓

    ★★★★★ **单位口径（★ 官方 `## Returns` **没写单位**）**：
      ★ `DefaultRadius` ⇒ ★ **本函数如实标 `unknown（★ 官方未写）`**、★ **不猜** ✓
      ★★ **真机测出来的口径写在 docstring 的历史里**（★ 见 `output/fillet-params-capability-recheck.json`）✓
    ★★★ **⚠ 本函数不碰那三个"要 item 对象"的成员**
      （★ `GetRadius` / ★ `GetDistance` / ★ `GetConicRhoOrRadius`）—— ★ 它们要先拿到 item ⇒
      ★★ **那是下一步的事**、★ **硬写会得到一个每次都不一样的结果** ✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "★_单位口径": {"DefaultRadius": "unknown（★ 官方 ## Returns 未写；★ 真机实测见证据）"}}
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★ 兜底：★ 找**最后一个**圆角特征（★ 类型名含 `Fillet`）——
            #:   ★★★ **⚠ 用两层过滤**（★ 上一轮的教训：★ 容器也可能有类型名）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    nm = str(safe_get_com_member(f, "Name") or "")
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if nm not in _CONTAINER_NODES and "Fillet" in tn:
                        feat, out["feature"] = f, nm
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到圆角特征"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ 属性（★ `{get;}` / ★ `{get;set}`）⇒ ★ 直接取 ✓
        for name in ("DefaultRadius", "Type", "OverflowType", "RoundCorners", "KeepFeatures",
                     "ConstantWidth", "PropagateToTangentFaces"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ 零参方法 ⇒ ★ 也取 ✓
        for name in ("GetEdgeCount", "GetSetbackVerticesCount"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\\swapi\\types\\ICoordinateSystemFeatureData\\`）
# 文件:   `scripts/sw_feature_readback.py::csys_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ **第七个**、★ **第六个族** ✓
#   ★★ **本族先逐个读官方页**（★ `output/_read_csys_members.py`）⇒
#     ★ **只有四个成员有页**、★ **其余一律「页不在」** ⇒
#     ★★★ **按铁律 5：★ 查不到就写「查不到」、★ 不许用相似名字蒙混** ✓
#   ★★★ **官方逐字**：★ `GetOriginEntityType()` ⇒ `swSelectType_e` ·
#     ★ 三个 `Get{X,Y,Z}AxisEntitiesCount()` ⇒ 「Number of entities for the x/y/z axis」·
#     ★ `Transform {get;}` ⇒ 回 `Math transform` ·
#     ★★ `AccessSelections(TopDoc, Component)` ⇒ 要两个入参 ⇒ **本函数不碰** ✓
#   ★★★★ **⚠ 本族**没有长度量****（★ 三是计数、★ 一是枚举、★ 一是变换对象）⇒
#     **不涉及单位口径** —— ★ **那本身是一条读数** ✓
#     （★ 对照本会话已见的六层：★ 随文档 · ★ radians · ★ meters · ★ 官方没写 ·
#       ★ 接口内部分裂 · ★ 随文档）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def csys_params(model, feature_name: str = "") -> dict:
    """★ 读**坐标系特征的一组参数**（★ 原点实体类型 / 三轴实体数 / 变换对象）✓

    ★★★★★ **⚠ 本族的"页不在"是**查不到**、★ 不是"没有"**：
      ★ `Flipped` / ★ `ReverseXDirection` / ★ `ReverseYDirection` / ★ `ReverseZDirection` /
      ★ `GetXAxisEntities` / ★ `GetYAxisEntities` / ★ `GetZAxisEntities` /
      ★ `GetXAxisEntitiesType` / ★ `GetYAxisEntitiesType` / ★ `GetZAxisEntitiesType` /
      ★ `GetOriginEntity` ⇒ ★★ **在 `C:\\swapi\\types\\ICoordinateSystemFeatureData\\`
        下**没有页** ⇒ ★★★ **按铁律 5：★ 本函数**不调**它们、★ 也不猜** ✓
      （★ 它们**可能存在**于别的源 —— ★ 那要另查；★ **不等于"不存在"**）✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "★_单位口径": "★ 本族**没有长度量**（★ 三是计数、★ 一是枚举、★ 一是变换对象）",
                 "★_页不在（★ 不调、★ 不猜）": [
                     "Flipped", "ReverseXDirection", "ReverseYDirection", "ReverseZDirection",
                     "GetXAxisEntities", "GetYAxisEntities", "GetZAxisEntities",
                     "GetXAxisEntitiesType", "GetYAxisEntitiesType", "GetZAxisEntitiesType",
                     "GetOriginEntity"]}
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★ 兜底：★ 找**最后一个**坐标系特征（★ 类型名含 `CoordSys`）——
            #:   ★★★ **两层过滤**（★ 前几轮的教训：★ 容器也可能有类型名）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    nm = str(safe_get_com_member(f, "Name") or "")
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if nm not in _CONTAINER_NODES and "CoordSys" in tn:
                        feat, out["feature"] = f, nm
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到坐标系特征"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ 零参方法（★ 官方逐字有页的那四个）⇒ ★ 直接取 ✓
        for name in ("GetOriginEntityType", "GetXAxisEntitiesCount",
                     "GetYAxisEntitiesCount", "GetZAxisEntitiesCount"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ `Transform` 是**属性**、★ 回一个**对象** ⇒ ★ 取它的 `ArrayData`（★ 16 个数）✓
        try:
            tr = get_com_member(fd, "Transform")
            out["Transform"] = type(tr).__name__ if tr is not None else None
            if tr is not None:
                arr = list(get_com_member(tr, "ArrayData") or [])
                out["Transform.ArrayData_len"] = len(arr)
                out["Transform.ArrayData_head"] = [round(float(x), 6) for x in arr[:4]]
        except Exception as exc:                                          # noqa: BLE001
            out["Transform"] = "err: %s" % str(exc)[:60]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\\swapi\\types\\IBaseFlangeFeatureData\\`）
# 文件:   `scripts/sw_feature_readback.py::base_flange_params`（★ 新增）
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ ★ **第八个**、★ **第七个族**、★ **钣金域** ✓
#   ★★ **官方逐字（★ 逐个成员的 `## Returns`）** ⇒ ★ **七个长度量**都没写单位****：
#     ★ `Thickness` ⇒ 「Value for thickness」· ★ `BendRadius` ⇒ 「Value of the bend radius」·
#     ★ `TableRadius` ⇒ 「Bend radius」· ★ `TableThickness` ⇒ 「Thickness」·
#     ★ `ReliefWidth` ⇒ 「Bend relief width」· ★ `ReliefDepth` ⇒ 「Bend relief depth」 ✓
#     ★★ （★ 与 `IWizardHoleFeatureData2` **同型** ⇒ ★ **按铁律 5：如实标 `unknown`、★ 真机测**）✓
#   ★★★ `KFactor` / ★ `TableKFactor` / ★ `ReliefRatio` ⇒ ★ **无量纲比例** ✓
#     ★ `ReliefType` ⇒ `swSheetMetalReliefTypes_e` · ★ `D1EndConditionType` ⇒
#       `swFlangeOffsetTypes_e` ✓
#   ★★★★ **⚠ `D1OffsetDistance` ⇒ **真废弃****（★ 新判据也认）⇒ **本函数不读** ✓
#   ★★★★★ **⚠ 本仓入口**（★ **按功能词搜出来的**）：★
#     `sw_sheet_metal.create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
def base_flange_params(model, feature_name: str = "") -> dict:
    """★ 读**钣金基体法兰特征的一组参数**（★ 厚度 / 折弯半径 / K 因子 / 释放槽 / 若干开关）✓

    ★★★★★ **单位口径（★ 第七个族 · ★ 与异型孔同型）**：
      ★ 官方 `## Returns` **只写光名字** ⇒ ★★ **本函数如实标 `unknown`、★ 不猜** ✓
      ★★★ **真机测出来的口径写在 docstring 的历史里**
        （★ 见 `tools/probe_base_flange_params_recheck.py` 与 `output/base-flange-params-capability-recheck.json`）✓
    ★★★ **⚠ 本函数不读 `D1OffsetDistance`**（★ 官方标**真废弃**）✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    UNK = "unknown（★ 官方 ## Returns 未写；★ 真机实测见证据）"
    out: dict = {"feature": feature_name, "definition": None, "error": None,
                 "★_单位口径": {k: UNK for k in (
                     "Thickness", "BendRadius", "TableRadius", "TableThickness",
                     "ReliefWidth", "ReliefDepth")},
                 "★_无量纲": ["KFactor", "TableKFactor", "ReliefRatio"],
                 "★_不读（★ 官方标真废弃）": ["D1OffsetDistance"]}
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★ 兜底：★ 找**最后一个**基体法兰特征（★ 类型名含 `BaseFlange`）——
            #:   ★★★ **两层过滤**（★ 前几轮的教训）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    nm = str(safe_get_com_member(f, "Name") or "")
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if nm not in _CONTAINER_NODES and "BaseFlange" in tn:
                        feat, out["feature"] = f, nm
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到基体法兰特征（★ 类型名含 `BaseFlange`）"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ **七个长度/比例量 + 三个开关类**（★ 全是有页的）⇒ ★ 直接取 ✓
        for name in ("Thickness", "BendRadius", "KFactor", "TableKFactor", "TableRadius",
                     "TableThickness", "ReliefType", "ReliefRatio", "ReliefWidth",
                     "ReliefDepth", "UseReliefRatio", "OverrideThickness", "OverrideRadius",
                     "OverrideKFactor", "UseGaugeTable", "UseDefaultBendAllowance",
                     "UseDefaultBendRelief", "SymmetricThickness", "ReverseDirection",
                     "ReverseThickness", "D1EndConditionType", "ThicknessTableName",
                     "OverrideDefaultSheetMetalParameters"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ 两个**计数**（★ 零参方法）⇒ ★ 也取 ✓
        for name in ("GetTableRadiiCount", "GetTableThicknessesCount"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out



#: ★★★★★★★ **族 → **真机打出来的**类型名**（★ 2026-10-04 轮 131 建）——
#:   ★ **为什么要这张表**：★ 本会话**连续两轮**栽在同一处 ——
#:     · ★ 轮 130：★ 我猜 `Revolve`、★ 而真机是 **`Revolution`**（★ `Revol`+`ution` vs `Revol`+`ve`）✗
#:     · ★★ 轮 131：★ 我猜 `Loft`、★ 而真机是 **`Blend`** ✗
#:   ★★★ **⇒ 两次都是"我以为类型名该叫什么"**（★ 而那**不是知识、是猜测**）⇒
#:     ★★ **⇒ 所以每个名字都要**有证据引用****（★ 本表每一行都指到一份 `output/*.json`）✓
#:   ★★★★ **⚠ `unknown` 的意思是**没核过**** —— ★ **不是**"大概是那个"（★ 铁律 5）✓
#:   ★★★★★ **⚠ 用法**：★ 新加一个族时**先跑一次真机、★ 把 `GetTypeName2` 打出来**、
#:     ★★ **再把那个字面量抄进本表** ⇒ ★ **不要凭记忆写** ✓
FEATURE_TYPE_NAMES = {
    #: ★ 证据：★ `output/rib-dome-params-capability-recheck.json`（★ `圆顶1`）
    "dome": "Dome",
    #: ★ 证据：★ `output/rib-dome-params-capability-recheck.json`（★ **⚠ 还没打出过真名**）
    "rib": "unknown（★ 未核 —— ★ 那个族至今没在真机建成过）",
    #: ★ 证据：★ `output/sweep-params-capability-recheck.json`（★ `扫描1` ⇒ `type_name=Sweep`）
    "sweep": "Sweep",
    #: ★ 证据：★ `output/revolve-params-capability-recheck.json`（★ `旋转1` ⇒ `Revolution`）
    "revolve": "Revolution",
    #: ★ 证据：★ `output/loft-params-capability-recheck.json`（★ `放样1` ⇒ `type_name='Blend'`）
    "loft": "Blend",
}

def _read_feature_params(model, feature_name: str, type_substring: str,
                         readable: tuple, container_label: str,
                         unit_note: dict | None = None) -> dict:
    """★ 共用帮手：★ 按**类型名子串**找特征 ⇒ ★ 取 `GetDefinition` ⇒ ★ 读给定成员 ✓

    ★★★★ **为什么抽出来**（★ 事实 60 定则④：★ 好用的函数要在**所有**同类场合用它）：
      ★ 本会话已写了 `csys_params` / `base_flange_params` / `shell_params` 三个
      **结构完全相同**的函数（★ 找特征 → 取定义 → 逐个读），★ 而每个都重抄了一遍
      "两层过滤兜底" ⇒ ★★★ **⇒ 本帮手把那一遍收成一处** ✓
      ★★ **⚠ 而既有那三个函数**本轮不动**（★ 它们已在多处被引用、
        ★ 重构的风险大于收益）—— ★ **只让**新写的**走本帮手** ✓

    ★ 参数：
      · `type_substring`：★ 类型名里含它即算（★ 如 `"Rib"` / `"Dome"`）✓
      · `container_label`：★ 找不到时报错的那句话 ✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    out: dict = {"feature": feature_name, "definition": None, "error": None}
    if unit_note:
        out["★_单位口径"] = unit_note
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★ 兜底：★ 找**最后一个**该类特征 —— ★★★ **两层过滤**（★ 容器也有类型名）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    nm = str(safe_get_com_member(f, "Name") or "")
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if nm not in _CONTAINER_NODES and type_substring in tn:
                        feat, out["feature"] = f, nm
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = container_label
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        for name in readable:
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


def rib_params(model, feature_name: str = "") -> dict:
    """★ 读**筋特征的一组参数**（★ 厚度 / 类型 / 拉伸方向 / 拔模角 / 若干开关）✓

    ★★★★★ **单位口径（★ 第九族）**：★ 官方 `IRibFeatureData2::Thickness` 的
      `## Returns` **只写 `Thickness of the rib`、★ 没写单位** ⇒
      ★★ **本函数如实标 `unknown`、★ 不猜** ✓

    ★★★★★★★ **⚠⚠ 本函数**至今没有真机读数** —— ★ 如实标、★ **不谎称** ✓
      ★ **真机读数**（★ `output/rib-dome-params-capability-recheck.json`）：
        ★ `rib_report ok=false` · ★ `created=null` · ★ **`error=""`** ⇒
        ★★ **⇒ **写侧**就没建成**（★ 那正是它自己 docstring 写的
          「真机表现是 **"不抛异常、也不建出特征"的静默失败**」）⇒
        ★★★ **⇒ 没有特征 ⇒ 本函数**量不到** ⇒ 口径**仍未定案**** ✓
      ★★ **⚠ 而那是**写侧**的问题**（★ 轮廓形态）—— 试过**两种**轮廓都不成：
        ① ★ 一条**悬空**的线（★ 没建板）⇒ `ok=false` ✓
        ② ★ 一条**板内**的线（★ 建了 60×40×10 的板）⇒ `ok=false` ✓
        ★★★ **⇒ 如实留给后人**：★ 筋的轮廓恐怕要**「板的一条边 + 一条外伸线」那种 L 形**
          ⇒ ★ **那要单独一轮去查官方示例** ✓
      ★★★ **⚠ 而同轮 `dome_params` **量到了**（★ `Height = 5.0` ⇒ 随文档单位）⇒
        ★★ **⇒ 两条**独立**、★ 不能因为圆顶成了就默认筋也成** ✓
      ★★★★ **⚠ `DraftAngle` 是**角度**⇒ ★ 官方只写 `Angle for the draft`、
        ★ **没写度还是弧度** ⇒ ★★ 本函数如实标 `unknown`** ✓
        （★ 本会话已有先例：★ `GetDraftAngle` 实测是 **radians** ⇒ **不套用**）✓

    ★★★★★ **⚠ 本函数只读那 12 个**有页且非指针**的成员**（★ 逐条查过官方页）✓
      | ★ 成员 | ★ 官方 `## Returns` |
      |---|---|
      | ★ `Thickness` | ★ `Thickness of the rib`（★ **无单位**）|
      | ★ `DraftAngle` | ★ `Angle for the draft`（★ **没写度/弧度**）|
      | ★ `Type` | ★ `Type as defined by swRibType_e` |
      | ★ `ExtrusionDirection` | ★ `Direction as defined in swRibExtrusionDirection_e` |
      | ★ `RefSketchIndex` | ★ `Index of the sketch segment that defines the draft direction` |
      | ★ `NextReference()` | ★ `Index of the entity that is used`（★ 零参方法）|
      | ★ 六个 bool | ★ `EnableDraft` · `DraftOutward` · `DraftFromWall` · `FlipSide` · `IsTwoSided` · `ReverseThicknessDir` |

    ★★★★★ **⚠ 不碰**：★ `Body`（★ `## Remarks` 指向「Accessing Selections」）·
      ★ `IAccessSelections` / ★ `AccessSelections` / ★ `ReleaseSelectionAccess`（★ 前置）✓
    """
    return _read_feature_params(
        model, feature_name, FEATURE_TYPE_NAMES["rib"],
        ("Thickness", "DraftAngle", "Type", "ExtrusionDirection", "RefSketchIndex",
         "NextReference", "EnableDraft", "DraftOutward", "DraftFromWall", "FlipSide",
         "IsTwoSided", "ReverseThicknessDir"),
        "找不到筋特征（★ 类型名含 `Rib`）",
        {"Thickness": "unknown（★ 官方未写单位；★ 真机实测见证据）",
         "DraftAngle": "unknown（★ 官方只说 `Angle for the draft`、未写度/弧度；"
                       "★ 真机实测见证据 —— ★ 本会话已有 `GetDraftAngle` 是 **radians** 的先例）"})


def dome_params(model, feature_name: str = "") -> dict:
    """★ 读**圆顶特征的一组参数**（★ 高度 / 是否椭圆 / 方向 / 面数）✓

    ★★★★★ **单位口径（★ 第十族）**：★ 官方 `IDomeFeatureData2::Height` 的
      `## Returns` **只写 `Height of the dome`、★ 没写单位** ⇒
      ★★ **本函数如实标 `unknown`、★ 不猜** ✓
      ★★★ **真机量过 · ★ 已定案**（★ `tools/probe_rib_dome_params_recheck.py` ·
        ★ `output/rib-dome-params-capability-recheck.json`）⇒
        ★ **管 40×40×10（毫米）⇒ 圆顶 `5 mm` ⇒ 读回 `Height = 5.0`** ⇒
        ★★★★ **⇒ 口径 = **随文档单位**（★ 毫米文档 ⇒ 毫米值）** ✓
      ★★★★★ **⚠ 而那次成功**靠的是三步选面序****（★ 那序**只在**
        `tools/verify_dome_smoke.py` 里、★ **签名与 Remarks 的散文都给不出**）：
        ① `SelectByID2("", "FACE", x,y,z, True, **0**, callout, 0)` ⇒
        ② `ClearSelection2(True)` ⇒ ③ **再按 `mark=1` 选一次** ✓
        （★ 官方 `InsertDome` 的 Remarks 只写「must select the face … using a
          **selection mark of 1**」—— ★ **那三步序是官方 C# 示例给的**）✓

    ★★★★★ **⚠ `ReverseDir` 的官方语义逐字**：★「**True for concave domes,
      false for convex domes**」⇒ ★★ **那是**语义**、★ 不是"反向开关"那种字面意思** ⇒
      ★★★ **⇒ 本函数把语义一并带回来**（★ 免得下一个人按名字猜）✓

    ★★★★★ **⚠ 不碰**：
      · ★ **`Face` / ★ `IFace`** ⇒ ★ **官方标**真废弃**** ✓
      · ★ **`IGetFaces`** ⇒ 官方 `## Returns` 逐字「**in-process, unmanaged C++:
        Pointer to an array** of …」⇒ ★★ **事实 47 那一族** ✓
      · ★ **`ISetFaces`** ⇒ ★ 含 `ref Face2` ⇒ 同上 ✓
      · ★ **`AccessSelections` / ★ `IAccessSelections` / ★ `ReleaseSelectionAccess`** ⇒ ★ 前置 ✓
      · ★ **`Faces` / ★ `Direction` / ★ `ConstraintPointOrSketch`** ⇒
        ★ 官方 `## Remarks` 指向「Accessing Selections that Define Features」✓
    """
    out = _read_feature_params(
        model, feature_name, FEATURE_TYPE_NAMES["dome"],
        ("Height", "Elliptical", "ReverseDir", "GetFaceCount"),
        "找不到圆顶特征（★ 类型名含 `Dome`）",
        {"Height": "unknown（★ 官方未写单位；★ 真机实测见证据）"})
    #: ★★★ 把 `ReverseDir` 的**官方语义**一并带回来（★ 免得下一个人按名字猜）✓
    out["★_ReverseDir_语义"] = {
        "True": "concave dome（★ 凹的圆顶）",
        "False": "convex dome（★ 凸的圆顶）",
        "★_出处": "官方 `IDomeFeatureData2/ReverseDir.md` 的 `## Returns` 逐字",
    }
    out["★_不读（★ 真废弃 / ★ 指针 / ★ 前置）"] = [
        "Face", "IFace", "IGetFaces", "ISetFaces",
        "AccessSelections", "IAccessSelections", "ReleaseSelectionAccess",
        "Faces", "Direction", "ConstraintPointOrSketch"]
    return out


def sweep_params(model, feature_name: str = "") -> dict:
    """★ 读**扫描特征的一组参数**（★ 类型 / 薄壁 / 圆轮廓直径 / 壁厚 / 扭转角 / 引导线数）✓

    ★★★★★★ **单位口径 —— ★ 本族的**两种量分开**（★ 那是本会话第一次遇到"同族里一半有写、一半没写"）**：
      | ★ 量 | ★ 官方 `## Returns` | ★ 口径 |
      |---|---|---|
      | ★★ **`GetTwistAngle()`** | ★「Angle of twist **in radians**」 | ★★ **radians（★ 官方**写了**）⇒ **不用量**** ✓ |
      | ★★ **`GetD2TwistAngle()`** | ★「Angle of twist **in radians** in Direction 2」 | ★★ 同上 ✓ |
      | ★ **`CircularProfileDiameter`** | ★「Diameter of the circular profile」（★ **无单位**）| ★ **unknown** ⇒ ★ **要真机量** ✓ |
      | ★ **`GetWallThickness(Forward)`** | ★「Wall thickness」（★ **无单位**）| ★ **unknown** ⇒ ★ **要真机量** ✓ |
      ★★ **⚠ **已真机跑过一轮、★ 而那两个量**仍未定案****（★ 轮 126 · 如实记）：
        ★ **真机读数**（★ `output/sweep-params-capability-recheck.json`）：
          ★ `CircularProfileDiameter = **0.0**` · ★ `GetWallThickness = {forward: 0.0, backward: 0.0}`
        ★★ **而那两个 `0.0` 是**应然的**** —— ★ 本探针用的是**草图轮廓**（★ `CircularProfile=false`）
          ⇒ **直径本就该是 0**；★ 而官方逐字说 `GetWallThickness`
          **「valid only if `ISweepFeatureData::IsThinFeature` is true」** ⇒ ★ **非薄壁时它不适用** ✓
        ★★★ **⇒ 要量那两个口径，必须**让它们非零****（★ 圆轮廓 / ★ 薄壁）✓

      ★★★★★★★ **✅ 其中一个已量出（★ 2026-10-04 轮 127 · ★ 第十一族）**：
        ★ **`CircularProfileDiameter` 的口径 = **随文档单位（★ 毫米文档 ⇒ 毫米值）** ✓
        **怎么量的**（★ 关键是**判据要独立** —— ★ 不能"写 `12.0` 再读回 `12.0`"那样自证）：
          · ★ 给扫描设 `CircularProfile = True` · ★ `CircularProfileDiameter = **12.0**` ⇒
            ★ 用 `IFeature::ModifyDefinition(Data, TopDoc, Component)` 落地 ⇒ **`modify_ok = true`** ✓
          · ★★ **再量**包围盒****（★ 那是**几何**、★ 与那个属性**互相独立**）：
            ★ `bbox_before = [**6.0, 6.0**, 40.0]`（★ 草图轮廓半径 3 ⇒ 直径 **6** · ★ 路径 40）⇒
            ★ `bbox_after  = [**12.0, 12.0**, 40.0]` ⇒
            ★★★ **⇒ 横截面从 **6** 变成 **12**、★ 正好等于我写进去的 `12.0`** ⇒
              ★★ **⇒ 口径 = 毫米**（★ 若口径是**米**，★ `12.0` 会是 **12 米** ⇒ 横截面 ≈**12000**）✓
          · ★★★ **两次读数**自洽**（★ 6.0 与 12.0 都能由各自的输入推出）⇒ **可信** ✓
        ★★★★ **⚠ 而那次成功卡在**第 3 参**上**（★ 值记）：
          ★ 传 `None` ⇒ ★ `com_error: (-2147352571, '**类型不匹配。**', None, **3**)` ⇒
          ★★ **⇒ 位置 3** 正是 `Component` ⇒ ★ **正解：★ 传
            `sw_connect.create_empty_dispatch_variant()`** ——
            ★ **事实 12/33 那一族**：★ 空 Dispatch 参数包**必须**用 `VARIANT(VT_DISPATCH, None)`、
            ★★ **传裸 `None` 会报「类型不匹配」、★ 而那个错误**看不出是哪个参数**** ✓

      ★★★★★ **⚠ 而 `GetWallThickness` 的口径**仍未定案**** —— ★ 官方逐字说它
        **「valid only if `ISweepFeatureData::IsThinFeature` is true」** ⇒
        ★★ **⇒ 要量它必须先有一个**薄壁**扫描** ✓

      ★★★★★★★ **✅ 而它**也量出来了（★ 2026-10-04 轮 129 · ★ **第十二族**）** ——
        ★ **`GetWallThickness` 的口径 = **随文档单位（★ 毫米文档 ⇒ 毫米值）** ✓

        **怎么量的**（★ 两步：★ 先在**正确的位置**设、★ 再用**几何**独立判）：
          ★★ **① 位置**：★ 轮 128 已证明「**先建后改**」**不存在**（★ 官方 `## Remarks`
            逐字：「You **cannot** make a thin-walled sweep feature after the sweep has
            been created … you **cannot** edit a sweep feature to make it thin walled」）⇒
            為此**给 `sw_sweep.create_sweep_report` 加了一个显式钩子 `mutate=None`**
            （★ 它在 `CreateDefinition` 之后、★ **`CreateFeature` 之前**被调用）⇒
            ★ **用那个钩子设**：★ `ThinFeature = True` · ★ `ThinWallType = 0` ·
            ★ `SetWallThickness(True, **0.002**)` ✓
          ★★★ **② 判据**：★ **最近候选分类**（★ 三个候选都摆上、★ **不许漏**）——
            ★ 轮廓半径 3 mm · ★ 路径 40 mm ⇒
            ★ **实体圆柱 = 1130.97** mm³ · ★ **米环带（0.002 m = 2 mm）= 1005.31** ·
            ★ **毫米环带（0.002 mm）= 1.51** ✓

        ★★★ **真机读数**（★ `output/sweep-wall-via-hook-recheck.json`）：
          · ★ `ok=true · feature = **扫描-薄件1** · type_name = Sweep` ✓
          · ★ 钩子里 `ThinFeature` 回读 = **true** ⇒ ★ **薄壁**这次真的设上了**** ✓
          · ★★ 读回：★ `IsThinFeature = **true**` · ★ `ThinFeature = **true**` ·
            ★ `GetWallThickness = {**forward: 0.002**, backward: 1e-07}` ✓
          · ★★★ **体积 = **1.508** mm³** ⇒ ★ 与**毫米环带 1.51** 距离 **0.002**、
            ★ **次近（1003.80）** ⇒ ★★★★ **⇒ 口径 = 毫米、★ 毫无歧义** ✓
          · ★ 而 `forward = **0.002**` **正是我写进去的那个数** ⇒ **两侧互相印证** ✓
          · ★★ `backward = 1e-07`（≈0）也**自洽** —— ★ 因为 `ThinWallType = 0` 是
            **One Direction** ⇒ ★ **只有方向 1 被设**（★ 官方逐字：
            「sets the thickness in Direction 1 and Direction 2, depending on `ThinWallType`」）✓

      ★★★★★★★ **✅ 而"薄壁扫描"这条路**已经查清（★ 2026-10-04 轮 128）** ——
        ★★ **结论：★ **不能"先建后改"****（★ 官方 `## Remarks` 逐字、★ **三条互相印证**）：
          ★ `ISweepFeatureData::ThinFeature` 的 `## Remarks`：
            「To make a thin sweep, you must set this property **before calling
             `IFeatureManager::CreateFeature`**. ★★ **You cannot make a thin-walled
             sweep feature after the sweep has been created**, and ★★ **you cannot edit
             a sweep feature to make it thin walled**.」✓
          ★ `ISweepFeatureData::IsThinFeature` 的 `## Remarks`：
            「you can make a sweep feature thin-walled **only by setting `ThinFeature`
             at the time of creation**」✓
        ★★★ **真机验证**（★ `output/sweep-wall-units-capability-recheck.json`）：
          ★ 建扫描后设 `ThinFeature = True` · ★ `ThinWallType = 0` ·
            ★ `SetWallThickness(True, 0.002)` ⇒ ★ `ModifyDefinition` 回 **`true`** ⇒
            ★★ **而体积**一点没变****：★ `before = **1130.973**` · ★ `after = **1130.973**` ⇒
            ★★★ 与「实体圆柱」的解析值 **1130.97** **距离 0.0**（★ 次近候选 125.664）⇒
              ★ **⇒ 判定**毫无歧义**：★ 薄壁**没被采纳**** ✓
        ★★★★ **⇒ 所以它是**能力层的形态问题**、★ 不是"读不读得到"的问题** ⇒
          ★ **要量那个口径，得改成"创建时就带薄壁"**（★ 即 `CreateFeature` 之前设）⇒
          ★★ **那要改 `sw_sweep` 的创建路径** ⇒ ★ **如实留作待办、★ 不谎称** ✓
        ★★★★★ **⚠ 而这一条是**我漏读 `## Remarks` 造成的**** —— ★ 我当时只读了
          `## Returns`（★ 「Wall thickness」）⇒ ★★ 而**前置条件全在 `## Remarks` 里** ✓
          ★★★ **⇒ 本仓 AGENTS.md 明写**「官方是第 0 步：★ **签名 + `## Remarks` + 例子**」✓

      ★★★★★ **而本轮的真机读数**（★ 建成了、★ 读回来了、★ **全部自洽**）：
        ★ `create_sweep_report` ⇒ ★ **`ok=True · type_name=**Sweep** · 树 9→10`** ✓
        ★★ **读回**：★ `SweepType = **17**`（★ 官方逐字 `swFmSweep` 是 swept boss）·
          ★ `IsBossFeature = true` · ★ `IsThinFeature = false` · ★ `ThinFeature = false` ·
          ★ `CircularProfile = false` · ★ `GetTwistAngle = 0.0` · ★ `GetPathType = 9` ·
          ★ `GetProfileType = 9` · ★ `GetGuideCurvesCount = 0` ✓
        ★★★ **⇒ 自洽性**：★ 每个值都能由「★ **草图轮廓** + ★ **非薄壁**」推出 ✓
      ★★★ **⇒ 可复用判据**：★★★ **同一个族里，"官方写没写单位"会**逐条不同**** ⇒
        ★ **不能按族一刀切** —— ★ **要一条一条看那一页的 `## Returns`** ✓
        （★ 而那是**本会话的固定动作**：★ 每加一个量、★ 先读它那一页）✓

    ★★★★★ **⚠ 本函数只读那 22 个**有页且非废弃、非指针**的成员**（★ 逐条查过官方页）✓
      ★ **类型/枚举**（★ 8 个）：★ `SweepType`（★ **只读** `{get;}`、`swFeatureNameID_e`）·
        ★ `Direction`(`swSweepDirection_e`) · ★ `StartTangencyType` / ★ `EndTangencyType`
        (`swTangencyType_e`) · ★ `PathAlignmentType` · ★ `ThinWallType` · ★ `TwistControlType` ·
        ★ `GetCutSweepOption()` · ★ `GetPathType()` / ★ `GetProfileType()`(`swSelectType_e`) ✓
      ★ **零参方法**（★ 4 个）：★ `IsBossFeature()` · ★ `IsThinFeature()` ·
        ★ `GetGuideCurvesCount()` · ★ `GetFeatureScopeBodiesCount()` ✓
      ★ **bool 量**（★ 11 个）：★ `AdvancedSmoothing` · ★ `AlignWithEndFaces` · ★ `AutoSelect` ·
        ★ `CircularProfile` · ★ `MaintainTangency` · ★ `Merge` · ★ `MergeSmoothFaces` ·
        ★ `ThinFeature` · ★ `FeatureScope` · ★ `TangentPropagation` ·
        ★ `D1ReverseTwistDir` / ★ `D2ReverseTwistDir` ✓

    ★★★★★ **⚠ 不碰**（★ 逐条给了理由）：
      · ★ **真废弃 6 个**（★ 官方标）：★ `EndDirectionVector` · ★ `IAccessSelections` ·
        ★ `IGetFeatureScopeBodies` · ★ `IGetGuideCurves` · ★ `IGetGuideCurvesType` ·
        ★ `ISetFeatureScopeBodies` ✓
      · ★ **`GetPathAlignmentDirectionVector(out int Type)`** ⇒ ★ **有 `out`** ⇒
        ★ 本仓既有记录说那族**在 pywin32 上到不了** ✓
      · ★ **`Path` / ★ `Profile` / ★ `GuideCurves` / ★ `FeatureScopeBodies`** ⇒ **对象数组**、
        ★ 且官方 `## Remarks` 指向「Accessing Selections that Define Features」✓
      · ★ **`SetTwistAngle` / ★ `SetWallThickness` / ★ `SetD2TwistAngle` /
        ★ `SetPathAlignmentDirectionVector`** ⇒ **那是写** ✓
      · ★ **`AccessSelections` / ★ `ReleaseSelectionAccess`** ⇒ **前置** ✓
    """
    out = _read_feature_params(
        model, feature_name, FEATURE_TYPE_NAMES["sweep"],
        ("SweepType", "IsBossFeature", "IsThinFeature", "ThinFeature", "ThinWallType",
         "CircularProfile", "CircularProfileDiameter",
         "GetTwistAngle", "GetD2TwistAngle", "TwistControlType",
         "D1ReverseTwistDir", "D2ReverseTwistDir",
         "Direction", "StartTangencyType", "EndTangencyType", "PathAlignmentType",
         "GetPathType", "GetProfileType", "GetCutSweepOption",
         "GetGuideCurvesCount", "GetFeatureScopeBodiesCount",
         "AdvancedSmoothing", "AlignWithEndFaces", "AutoSelect", "MaintainTangency",
         "Merge", "MergeSmoothFaces", "FeatureScope", "TangentPropagation"),
        "找不到扫描特征（★ 类型名含 `Sweep`）",
        {"CircularProfileDiameter": "unknown（★ 官方未写单位；★ 真机实测见证据）",
         "GetWallThickness": "unknown（★ 官方未写单位；★ 真机实测见证据）",
         "GetTwistAngle": "**radians**（★ 官方 `## Returns` 逐字写明 —— ★ **本族唯一写了单位的两条之一**）",
         "GetD2TwistAngle": "**radians**（★ 官方同款逐字）"})

    #: ★★★★★★ **`GetWallThickness` 要**带实参**调**（★ 轮 126 真机抓到的）——
    #: ★ 它官方签名是 `System.double GetWallThickness( System.bool Forward )` ⇒
    #: ★★ **⇒ 无参调不动、★ 而 `get_com_member` **不报错**、★ 把**成员本身**回了回来** ⇒
    #: ★★★ **⇒ 那个 bound method 会一路流到 `json.dumps` 才炸**
    #: （★ `TypeError: Object of type method is not JSON serializable`）✓
    #: ★★★★ **⇒ 所以两个方向都**显式带参**取** ✓
    if out.get("definition") is not None:
        try:
            from sw_connect import get_com_member as _g
            fd2 = _g(_g(model, "FeatureByName", str(out["feature"])), "GetDefinition") \
                if out.get("feature") else None
            if fd2 is not None:
                out["GetWallThickness"] = {
                    "forward": _g(fd2, "GetWallThickness", True),
                    "backward": _g(fd2, "GetWallThickness", False),
                    "★_单位口径": "unknown（★ 官方未写单位；★ 真机实测见证据）",
                }
        except Exception as exc:                                          # noqa: BLE001
            out["GetWallThickness"] = "err: %s" % str(exc)[:60]
    return out




def loft_params(model, feature_name: str = "") -> dict:
    """★ 读**放样特征的一组参数**（★ 轮廓数 / 引导线 / 起止相切 / 拔模角 / 薄壁 / 闭合）。★ 单位口径见下。

    ★★★★★★ **单位口径 —— ★ 本族有**四个**待量的量**（★ 第十四 ~ 十七族候选）**：
      | ★ 量 | ★ 官方 `## Returns` | ★ 口径 |
      |---|---|---|
      | ★ **`StartConstraintDraftAngle`** / ★ **`EndConstraintDraftAngle`** | ★「Draft angle」 | ★ **unknown** ⇒ ★ **要真机量**（★ **度 vs 弧度**）✓ |
      | ★ **`StartTangentLength`** / ★ **`EndTangentLength`** | ★「(Start/End) tangent length」 | ★ **unknown** ⇒ ★ **要真机量** ✓ |
      | ★★ **`GetWallThickness(Forward)`** | ★「Wall thickness」（★ **无单位**）| ★ **unknown** ⇒ ★ **要真机量** ✓ |
      ★★★ **⚠ 而两个拔模角有**前置****（★ 官方 `## Remarks` 逐字）：
        ★「This property is only valid if …`StartConstraint…`」⇒ ★ **只有开了那个起/止约束才有意义** ✓
      ★★★★ **⚠ 而 `NumberOfSections` 的类型是 `double`** —— ★ **可它存的是**个数****
        （★ `## Returns: Number of sections`）⇒ ★ **它**不带单位**（★ 本会话少见的一类）✓
      ★★★★★ **⚠ 可复用判据**：★★★ **"官方写没写单位"要一条一条看那一页的 `## Returns`** ——
        ★ 本会话已见 **十三族**（★ 从"随文档"到"radians"到"不涉及单位"）⇒ **不能按族一刀切** ✓

    ★★★★★ **⚠ 本函数只读那些**有页且非废弃、非指针**的成员**（★ 逐条查过官方页）✓
      ★ **计数/零参**：★ `GetProfileCount()` · ★ `GetGuideCurvesCount()` ·
        ★ `GetFeatureScopeBodiesCount()` · ★ `IsBossFeature()` · ★ `IsThinFeature()` ✓
      ★ **枚举**：★ `StartTangencyType` / ★ `EndTangencyType`（`swTangencyType_e`）·
        ★ `GuideCurveInfluence`（`swGuideCurveInfluence_e`）✓
      ★ **数量属性**：★ `NumberOfSections`（★ **个数**、★ 不带单位）✓
      ★ **bool 量**：★ `Close` · ★ `AdvancedSmoothing` · ★ `MaintainTangency` · ★ `Merge` ·
        ★ `FeatureScope` · ★ `AutoSelect` · ★ `ReverseStartTangentDirection` ·
        ★ `ReverseEndTangentDirection` · ★ `StartConstraintApplyToAll` ·
        ★ `EndConstraintApplyToAll` · ★ `StartConstraintDraftAngleDirection` ·
        ★ `EndConstraintDraftAngleDirection` ✓
      ★ **角度量**：★ `StartConstraintDraftAngle` · ★ `EndConstraintDraftAngle` ✓
      ★ **长度量**：★ `StartTangentLength` · ★ `EndTangentLength` ✓

    ★★★★★ **✅ 真机读数（★ 轮 131 · ★ 建成了 ⇒ 读回来了）**：
      ★ 建放样（★ 两个草图 · ★ 按 **mark=1** 选）⇒
        ★ **`ok=True · feature_name = **放样1** · **type_name = 'Blend'** · tree 7→8`** ✓
      ★★ **读回**：★ `GetProfileCount = **2**`（★ 两个轮廓 ⇒ **对**）·
        ★ `GetGuideCurvesCount = **0**`（★ 没引导线 ⇒ 对）· ★ `IsBossFeature = **true**` ·
        ★ `IsThinFeature = false` · ★ `Close = false` · ★ `StartTangencyType = 0` ·
        ★ `EndTangencyType = 0` · ★ `StartConstraintDraftAngle = **0.0**` ·
        ★ `StartTangentLength = **0.1**` ✓
      ★★★ **⚠ 而 `NumberOfSections = **1.0**` 与 `GetProfileCount = **2**` **不一致**** ⇒
        ★★ **⇒ 那**不是矛盾、★ 而是**两个不同的量**** —— ★ 官方那两个名字逐字是
        「Number of **sections**」与「Number of **profiles**」⇒ ★ **如实记** ✓
      ★★★★ **⚠ 那几个量的口径**仍 `unknown`**** —— ★ 它们**都带前置**
        （★ 拔模角要开起/止约束）⇒ ★ **本探针的几何没打开它们** ⇒ ★ **不谎称量到了** ✓

    ★★★★★ **⚠ 不碰**（★ 逐条给了理由）：
      · ★ **`Profiles` / ★ `GuideCurves` / ★ `Centerline` / ★ `PickPoints` /
        ★ `FeatureScopeBodies` / ★ `StartDirectionVector` / ★ `EndDirectionVector`** ⇒
        **对象或数组**、★ 且官方 `## Remarks` 指向「Accessing Selections that Define Features」✓
      · ★ **`ISetProfiles` / ★ `ISetGuideCurves` / ★ `ISetFeatureScopeBodies`** ⇒ **含 `ref`** ✓
      · ★ **`SetGuideTangencyType` / ★ `SetWallThickness`** ⇒ **那是写** ✓
      · ★ **`AccessSelections` / ★ `IAccessSelections` / ★ `ReleaseSelectionAccess`** ⇒ **前置** ✓
      · ★ **`GetGuideCurvesType()`** ⇒ ★ 官方 `## Returns` 是**数组** ⇒ ★ 本函数**不读** ✓
    """
    out = _read_feature_params(
        #: ★★★★★★★ 2026-10-04（轮 131）**真机打出来的类型名是 `Blend`、★ 不是 `Loft`** ——
        #:   ★ 真机读数：★ `create_loft_report` ⇒ `ok=True · feature_name=**放样1** ·
        #:     **type_name='Blend'** · tree 7→8`（★ `output/loft-params-capability-recheck.json`）✓
        #:   ★★ **⇒ 而与上一轮 `Revolve` vs `Revolution` **完全同型**** ——
        #:     ★ 而那一次我**刚记过**「先打出真名、★ 不要猜」⇒ ★★★ **⇒ 我记了、★ 却没做成机制** ✗
        #:   ★★★ **⇒ 机制见本模块的 `FEATURE_TYPE_NAMES`**（★ 每个名字都要有**证据引用**）✓
        model, feature_name, FEATURE_TYPE_NAMES["loft"],
        ("GetProfileCount", "GetGuideCurvesCount", "GetFeatureScopeBodiesCount",
         "IsBossFeature", "IsThinFeature",
         "StartTangencyType", "EndTangencyType", "GuideCurveInfluence",
         "NumberOfSections",
         "Close", "AdvancedSmoothing", "MaintainTangency", "Merge", "FeatureScope",
         "AutoSelect", "ReverseStartTangentDirection", "ReverseEndTangentDirection",
         "StartConstraintApplyToAll", "EndConstraintApplyToAll",
         "StartConstraintDraftAngleDirection", "EndConstraintDraftAngleDirection",
         "StartConstraintDraftAngle", "EndConstraintDraftAngle",
         "StartTangentLength", "EndTangentLength"),
        "找不到放样特征（★ 类型名含 `Loft`）",
        {"StartConstraintDraftAngle": "unknown（★ 官方未写度还是弧度；★ **要真机量**）",
         "EndConstraintDraftAngle": "unknown（★ 同上）",
         "StartTangentLength": "unknown（★ 官方未写单位；★ **要真机量**）",
         "EndTangentLength": "unknown（★ 同上）",
         "GetWallThickness": "unknown（★ 官方未写单位；★ **要真机量**）",
         "NumberOfSections": "★ **不带单位**（★ 官方逐字 `Number of sections` ⇒ **个数**；"
                             "★ 而它的 CLR 类型是 `double` ⇒ ★ **少见的一类**）"})

    #: ★★★★ **带实参的两个：★ 单独带参调**（★ 不能走那张"逐名读取"表）——
    #:   ★ 因为 `get_com_member` 对"必须带实参"的成员会**静默回 bound method** ✓
    if out.get("definition") is not None:
        try:
            from sw_connect import get_com_member as _g
            fd2 = _g(_g(model, "FeatureByName", str(out["feature"])), "GetDefinition") \
                if out.get("feature") else None
            if fd2 is not None:
                out["GetWallThickness"] = {
                    "forward": _g(fd2, "GetWallThickness", True),
                    "backward": _g(fd2, "GetWallThickness", False),
                    "★_单位口径": "unknown（★ 官方未写单位；★ 真机实测见证据）",
                }
                #: ★ `GetGuideTangencyType(short GuideIndex)` ⇒ ★ **逐条引导线** ✓
                n = out.get("GetGuideCurvesCount")
                if isinstance(n, int) and n > 0:
                    out["GetGuideTangencyType"] = [
                        _g(fd2, "GetGuideTangencyType", i) for i in range(min(n, 16))]
        except Exception as exc:                                          # noqa: BLE001
            out["★_带参量错误"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
    return out


def revolve_params(model, feature_name: str = "") -> dict:
    """★ 读**旋转特征的一组参数**（★ 角度 / 轴类型 / 方向 / 薄壁 / 轮廓数）✓

    ★★★★★★ **单位口径 —— ★ 本族有两个**待量的量**（★ 第十三四族）**：
      | ★ 量 | ★ 官方 `## Returns` | ★ 口径 |
      |---|---|---|
      | ★★ **`GetRevolutionAngle(Forward)`** | ★「Angle of revolution」（★ **无单位**）| ★ **unknown** ⇒ ★ **要真机量**（★ 度 vs 弧度）✓ |
      | ★★ **`GetWallThickness(Forward)`** | ★「Wall thickness」（★ **无单位**）| ★ **unknown** ⇒ ★ **要真机量** ✓ |
      ★★★ **⚠ 而两者都**带一个 `bool Forward` 实参**** ⇒ ★ 本函数**单独带参调**它们 ——
        ★ **因为 `get_com_member` 对"必须带实参"的成员会**静默回 bound method****
        （★ 轮 126 真机抓到的：★ 那个 bound method 一路流到 `json.dumps` 才炸）✓
      ★★★★ **⚠ 而 `GetWallThickness` 的官方 `## Remarks` 说**
        「**This method only affects thin features**」⇒ ★ **非薄壁时它不适用** ✓
      ★★★★★ **⚠ 而 `GetRevolutionAngle` 是**度还是弧度**必须量** ——
        ★ 本会话已有**先例**：★ `ISimpleFilletFeatureData2::GetDraftAngle` 官方写了 radians、
        ★★ 而**同族的 `GetRevolutionAngle` 官方**没写**** ⇒ ★ **不能套用** ✓

    ★★★★★ **⚠ 本函数只读那 14 个**有页且非废弃、非指针**的成员**（★ 逐条查过官方页）✓
      ★ **零参/属性**：★ `GetAxisType()`（`swSelectType_e`）· ★ `IsBossFeature()` ·
        ★ `IsThinFeature()` · ★ `GetContoursCount()` · ★ `GetFeatureScopeBodiesCount()` ·
        ★ `ThinWallType`（★ `int`）✓
      ★ **bool 量**：★ `ReverseDirection` · ★ `Merge` · ★ `FeatureScope` · ★ `AutoSelect` ·
        ★ `AutoSelectComponents` · ★ `AssemblyFeatureScope` · ★ `PropagateFeatureToParts` ✓
      ★ **带参量**：★ `GetRevolutionAngle(Forward)` · ★ `GetWallThickness(Forward)` ✓

    ★★★★★ **⚠ 不碰**（★ 逐条给了理由）：
      · ★ **`Axis` / ★ `Contours` / ★ `FeatureScopeBodies`** ⇒ **对象数组**、
        ★ 且官方 `## Remarks` 指向「Accessing Selections that Define Features」✓
      · ★ **`ISetContours` / ★ `ISetFeatureScopeBodies`** ⇒ ★ 含 `ref System.object` /
        `ref Body2` ⇒ ★ 指针变体那一族** ✓
      · ★ **`SetRevolutionAngle` / ★ `SetWallThickness`** ⇒ **那是写** ✓
      · ★ **`AccessSelections` / ★ `IAccessSelections` / ★ `ReleaseSelectionAccess`** ⇒ **前置** ✓
    """
    out = _read_feature_params(
        #: ★★★★★★★ 2026-10-04（轮 130）**真机打出来的是 `Revolution`、★ 不是 `Revolve`** ——
        #:   ★ 真机读数：★ `["旋转1", "Revolution", **false**]` ⇒
        #:     ★★ **⇒ 那个 `false` 是 `("Revolve" in "Revolution")` 的结果** ⇒
        #:       ★★★ **⇒ 它竟然是 `False`**（★ `Revol`+`ution` vs ★ `Revol`+`ve` ⇒ 在 `Revol` 后分岔）✓
        #:   ★★★★ **⇒ 而我先前**把它写成"本该是 True"**** ⇒ ★ **那正是"我以为"** ✗
        #:   ★★★★★ **⇒ 教训**：★★★ **"我以为一个子串在里面"不可靠 ⇒ 让机器判** ✓
        model, feature_name, FEATURE_TYPE_NAMES["revolve"],
        ("GetAxisType", "IsBossFeature", "IsThinFeature", "GetContoursCount",
         "GetFeatureScopeBodiesCount", "ThinWallType",
         "ReverseDirection", "Merge", "FeatureScope", "AutoSelect",
         "AutoSelectComponents", "AssemblyFeatureScope", "PropagateFeatureToParts"),
        #: ★ 标签里那个旧名也一并改掉 —— ★ 真机打出来的真名是 `Revolution` ✓
        "找不到旋转特征（★ 类型名含 `Revolution`）",
        #: ★★★★★★★ 2026-10-04（轮 130）**已量出：★ radians**（★ 第十三族）——
        #:   ★ **三条独立证据**（★ `output/revolve-params-capability-recheck.json`）：
        #:     ★ ① 传 `math.radians(30)` ⇒ 读回 `forward = **0.5235987755982988**`
        #:       ⇒ ★★ **那正是 **π/6 的精确值****（★ 若它回**度**、★ 该是 `30.0`）⇒
        #:       最近候选 π/6 · ★ **距离 0.000000** · ★ 次近 **29.476** ⇒ **毫无歧义** ✓
        #:     ★★ ② **几何独立验证**：★ 体积 `**785.398**` ⇒ 与「30° 扇形环」的解析值
        #:       `(30/360)·π·(20²−10²)·10 = **785.398**` **完全一致** ✓
        #:     ★★★ ③ **反面对照**：★ 我先前**误传度**（`30.0`）⇒ 读回
        #:       `**4.867259 rad = 278.8734°**`、★ 而 `30 rad mod 360° = **278.8734°**`
        #:       （★ 差 `0.000000°`）⇒ ★ **也印证同一件事** ✓
        {"GetRevolutionAngle": "**radians**（★ 官方**没写**；★ 三条独立证据定案 —— "
                               "★ 反面对照：误传**度**时读回 4.867259 rad = 278.8734°、"
                               "而 30 rad mod 360° 也正是 278.8734°）",
         #: ★★★★★★★ 2026-10-04（轮 138）**已量出：★ 随文档单位（毫米）** ——
         #:   ★ **怎么量的**：★ 建**薄壁旋转**（★ `revolve_boss(…, thin={"type": 0,
         #:     "thickness": **0.002**})`）⇒ ★ 特征名 **`旋转-薄壁1`**、★ 读回
         #:     `IsThinFeature = **true**` · ★ `ThinWallType = **0**` ·
         #:     ★★ **`GetWallThickness = {forward: 0.002, backward: 0.002}`** ✓
         #:   ★★ **而体积给出**精确判据****（★ **不是粗估** —— ★ 轮廓是折线 ⇒ 积分是初等的）：
         #:     ★ 矩形周长 2×(10+10) = **40 mm** · ★ 绕 x=0 转 30°（θ=π/6）⇒
         #:     ★ 扫掠面积 = ∫ r·θ ds = (10+20+15+15)·10·θ = **600θ = 100π = 314.159265 mm²** ⇒
         #:     ★★ 体积 = t × 314.159 ⇒ ★ **实测 `0.628444`** ⇒ **反推 t = 0.002000399** ✓
         #:     ★★★ **⇒ 与我写进去的 `0.002` 一致到 6 位**（★ 那 4e-7 偏差来自几何圆角化）✓
         #:   ★★★ **对照组**：★ 若口径是**米**（★ `0.002 m = 2 mm`）⇒ 体积该是 **628.319** ⇒
         #:     ★★ **⇒ 与实测差** 1000 倍**** ⇒ **⇒ 毫无歧义** ✓
         #:   ★★★★ **⇒ 而它与 `ISweepFeatureData::GetWallThickness` **同口径**** ✓
         #:   ★★★★★ **⚠ 而**方法**也值得记**：★ 我第一版把薄壁那两条候选当**粗估**、
         #:     说「只到生效这一层」⇒ ★★ **⇒ 而其实**可以算准**** ⇒
         #:     ★★★ **⇒ 判据**：★★★ **"估算不了"常常是**我没把几何写出来**、★ 而不是真估不了** ✓
         "GetWallThickness": "**随文档单位（★ 毫米文档 ⇒ 毫米值）** —— ★ 官方**没写**；"
                             "★ 真机定案：★ 写 `0.002` ⇒ 读回 `0.002`、★ 而**反推壁厚 "
                             "= 0.002000399**（★ 体积 0.628444 ÷ 扫掠面积 314.159265）· "
                             "★ 对照组：★ 若口径是**米**体积该是 **628.319**（★ 差 **1000 倍**）✓"})

    #: ★★★★ **两个带实参的：★ 单独带参调**（★ 不能走那张"逐名读取"表）✓
    if out.get("definition") is not None:
        try:
            from sw_connect import get_com_member as _g
            fd2 = _g(_g(model, "FeatureByName", str(out["feature"])), "GetDefinition") \
                if out.get("feature") else None
            if fd2 is not None:
                out["GetRevolutionAngle"] = {
                    "forward": _g(fd2, "GetRevolutionAngle", True),
                    "backward": _g(fd2, "GetRevolutionAngle", False),
                    "★_单位口径": "unknown（★ 官方未写单位；★ 真机实测见证据）",
                }
                out["GetWallThickness"] = {
                    "forward": _g(fd2, "GetWallThickness", True),
                    "backward": _g(fd2, "GetWallThickness", False),
                    "★_单位口径": "unknown（★ 官方未写单位；★ 真机实测见证据）",
                }
        except Exception as exc:                                          # noqa: BLE001
            out["★_带参量错误"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
    return out


def shell_params(model, feature_name: str = "") -> dict:
    """★ 读**抽壳特征的一组参数**（★ 厚度 / 方向 / 移除面数 / 多厚度面数与逐面厚度）✓

    ★★★★★ **单位口径（★ 第八个族）**：★ 官方 `IShellFeatureData::Thickness` 的
      `## Returns` **只写 `Shell thickness`、★ 没写单位** ⇒
      ★★ **本函数如实标 `unknown`、★ 不猜** ✓
      ★★★ **而真机量了**（★ 2026-10-04 轮 122 · ★ `tools/probe_shell_params_recheck.py`
        · ★ `output/shell-params-capability-recheck.json`）：
        ★ **板 60×40×10（毫米）⇒ 抽壳 `2 mm` ⇒ 读回 `Thickness = 2.0`** ⇒
        ★★★★ **⇒ 口径 = **随文档单位**（★ 毫米文档 ⇒ 毫米值）** ✓
      ★★★★★ **⚠ 而**写侧**也有同一口径的记录**（★ `scripts/sw_part.py::shell_report` 逐字：
        「★ `thickness` 在能力层的单位**随文档单位**（本项目零件按毫米 ⇒ 传毫米值）」）⇒
        ★★ **⇒ 两侧**实测一致** —— ★ **而那是量出来的、★ 不是把写侧口径套到读侧** ✓
        ★★★ 本会话已见过**同一接口内部就分裂**的先例（★ `IWizardHoleFeatureData2`：
          直径是**米**、深度是**毫米**）⇒ **⇒ 每一个量都要单独量** ✓

    ★★★★★ **⚠ 本函数只读那五个**有页且非指针**的成员**（★ 逐条查过官方页）：
      | ★ 成员 | ★ 官方签名 | ★ 官方 `## Returns` |
      |---|---|---|
      | ★ `Thickness` | ★ `System.double {get;set;}` | ★ `Shell thickness`（★ **无单位**）|
      | ★ `Direction` | ★ `System.int {get;set;}` | ★「**0 for inward shell, 1 for outward shell**」|
      | ★ `FacesRemovedCount` | ★ `System.int {get;}` | ★ `Number of removed faces` |
      | ★ `GetMultipleThicknessFacesCount()` | ★ `System.int` | ★ `Number of faces with multiple thickness` |
      | ★ `GetMultipleThicknessAtIndex(int)` | ★ `System.double` | ★ `Shell thickness`（★ **无单位**）|

    ★★★★★ **⚠ 本函数**不碰**下面这些**（★ 逐条给了理由，★ 免得下一个人再试一遍）：
      · ★ **`IGetFacesRemoved` / ★ `IGetMultipleThicknessFaces`** ⇒ 官方 `## Returns` 逐字
        「**in-process, unmanaged C++: Pointer to an array** of …」⇒
        ★★ **那正是**事实 47** 那一族（★ 指针接口、★ pywin32 到达不了）** ✓
      · ★ **`IAccessSelections` / ★ `ISetFacesRemoved` / ★ `ISetMultipleThicknessFaces`** ⇒
        ★ 同上（★ 含 `ref System.object` 或 `ModelDoc2`/**指针变体**）✓
      · ★ **`FacesRemoved` / ★ `MultipleThicknessFaces`** ⇒ 官方 `## Remarks` 指向
        「**Accessing Selections that Define Features**」⇒ ★ **那是**前置**、★ 不是"读参数"** ✓
      · ★ **`AccessSelections` / ★ `ReleaseSelectionAccess`** ⇒ ★ 同上（★ 成对的前置）✓
    """
    from sw_connect import get_com_member, safe_get_com_member
    UNK = "unknown（★ 官方 ## Returns 未写单位；★ 真机实测见证据）"
    out: dict = {
        "feature": feature_name, "definition": None, "error": None,
        "★_单位口径": {"Thickness": UNK, "GetMultipleThicknessAtIndex": UNK},
        "★_无量纲": ["Direction", "FacesRemovedCount",
                     "GetMultipleThicknessFacesCount"],
        "★_方向语义": {"0": "inward shell（★ 向内的抽壳）",
                       "1": "outward shell（★ 向外的抽壳）"},
        "★_不读（★ 要前置 / ★ 指针接口 / ★ 事实 47）": [
            "IGetFacesRemoved", "IGetMultipleThicknessFaces", "IAccessSelections",
            "ISetFacesRemoved", "ISetMultipleThicknessFaces",
            "FacesRemoved", "MultipleThicknessFaces",
            "AccessSelections", "ReleaseSelectionAccess"],
    }
    try:
        feat = None
        if feature_name:
            feat = safe_get_com_member(model, "FeatureByName", str(feature_name))
        if feat is None:
            #: ★★ 兜底：★ 找**最后一个**抽壳特征（★ 类型名含 `Shell`）——
            #:   ★★★ **两层过滤**（★ 前几轮的教训：★ 容器也有类型名）✓
            f = safe_get_com_member(model, "FirstFeature")
            while f is not None:
                try:
                    nm = str(safe_get_com_member(f, "Name") or "")
                    tn = str(safe_get_com_member(f, "GetTypeName2") or "")
                    if nm not in _CONTAINER_NODES and "Shell" in tn:
                        feat, out["feature"] = f, nm
                except Exception:                                         # noqa: BLE001
                    pass
                f = safe_get_com_member(f, "GetNextFeature")
        if feat is None:
            out["error"] = "找不到抽壳特征（★ 类型名含 `Shell`）"
            return out
        fd = get_com_member(feat, "GetDefinition")
        out["definition"] = type(fd).__name__ if fd is not None else None
        if fd is None:
            out["error"] = "`IFeature::GetDefinition` 回 None"
            return out
        #: ★★ **那五个可读的**（★ 逐条查过官方页）⇒ ★ 直接取 ✓
        for name in ("Thickness", "Direction", "FacesRemovedCount",
                     "GetMultipleThicknessFacesCount"):
            try:
                out[name] = get_com_member(fd, name)
            except Exception as exc:                                      # noqa: BLE001
                out[name] = "err: %s" % str(exc)[:50]
        #: ★★★ **逐面厚度**：★ 先数、★ 再按索引取（★ 官方 Remarks 说"先调计数"）✓
        #:   ★★ 设**上限**，★ 免得异常时死循环 ✓
        try:
            n = int(out.get("GetMultipleThicknessFacesCount") or 0)
        except Exception:                                                 # noqa: BLE001
            n = 0
        out["multiple_thickness"] = []
        for i in range(min(max(n, 0), 32)):
            try:
                out["multiple_thickness"].append(
                    get_com_member(fd, "GetMultipleThicknessAtIndex", i))
            except Exception as exc:                                      # noqa: BLE001
                out["multiple_thickness"].append("err: %s" % str(exc)[:50])
    except Exception as exc:                                              # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out
