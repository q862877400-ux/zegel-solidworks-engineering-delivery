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
           "extrude_depth"]


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
