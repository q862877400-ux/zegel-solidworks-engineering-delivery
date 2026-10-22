"""零件质量属性**读数**（砌墙 W5 / Spec Kit `138`）。

## ★★★ 为什么需要它：又是「能写不能读」
```
· `sw_export.set_mass_property_override`（**改**覆盖值）—— 已有。
· ★ 而**读不出实际质量属性** —— MCP 与能力层里都没有（见事实 166 的核查）。
⇒ 而「这个零件多重 / 体积多少 / 重心在哪」是**最常被问的问题之一**。
★ 与 W3「能写自定义属性却读不回来」（`specs/133`）**同一个形状**。
```

## ★★★ 取法与单位由**真机探针**定死（`tools/probe_mass_property_reads.py`，轮 233）
```
① 取法：★ **`model.Extension.CreateMassProperty` 是属性**（当属性取就拿到对象）
   ⚠⚠ **与 W3 的 `Extension.CustomPropertyManager` 相反**（那个**必须当方法调用**，
     当属性取会拿到一个 **method 对象**，见事实 161）
   ⇒ ★ 定则：**同一个父对象的不同成员，取法也可能不同** —— 上一个接口的教训**不能照搬**。

② 单位：★ 实测是**「毫米系」**（盒 40×20×10 mm ⇒ 读回 Volume **8000**、SurfaceArea **2800**、
   CenterOfMass z = **−5**）—— **不是** SI 米
   ⇒ 与既有事实 73 的 `IBody2.GetBodyBox`（**毫米**）一致；
     而**与官方其余几何接口惯用的"米"不同**（所以本模块**不做任何换算**）。

③ ⚠⚠ **`Mass` 的物理单位**没有确证**（如实记，不猜）**：
     盒的读数：`Volume = 8000`（mm³）· `Density = 1000.0` · `Mass = 7999999.999999999`
     ★ 而 `8000 × 1000 = 8,000,000` ⇒ **`Mass` 恰好等于 `Volume(mm³) × Density`**
     ⇒ 若 Volume 是 mm³、Density 是 kg/m³，质量应是 **8 g = 0.008 kg** ⇒ **不是 8e6**
     ⇒ ★★ **三个读数各自"像对的"，但乘起来量纲不成立** ⇒
       ★ **本模块照实透传 `Mass`，并在工具说明里写明它的物理单位未确证**；
       ★ **不换算、不猜、不给它安一个单位**。

④ ⚠ `IMassProperty2.AccuracyLevel` 实测 **`AttributeError`**（读不到）⇒ 本模块**不暴露**它。
```

## 后备路（`IModelDoc2.GetMassProperties`）为什么**不用**
```
官方那个回 **12 个 double**（实测次序 = [CX, CY, CZ, Volume, Area, Mass, Ixx, Iyy, Izz, …]）
★ 它比 `IMassProperty2` **少**（没有 Density，惯性矩只有一个分量），而且**要靠位置记次序**
⇒ ★ 用 `IMassProperty2`（成员**有名字**），**不靠位置**。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   scripts/sw_mass_property.py
# 定位:   砌墙 W5（Spec Kit `138`）的能力层：读零件质量属性。
# 官方依据: `IModelDocExtension.CreateMassProperty` · `IMassProperty2` 的
#          `Mass` / `Volume` / `SurfaceArea` / `CenterOfMass` / `Density`
#          （swapi 里这 11 个成员**全是 `kind: property`** ⇒ 无 by-ref out）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机验证状态见 `output/mass-property-evidence.json`（铁律 2）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any

from sw_connect import get_com_member

__all__ = [
    "SWDOC_PART",
    "SWDOC_ASSEMBLY",
    "SWDOC_DRAWING",
    "require_mass_property_document",
    "mass_property_object",
    "mass_properties",
    #: ★ 规格 211 · B1-1「截面属性」
    "SECTION_STATUS",
    "SECTION_INDEX",
    "section_properties",
    "section_area_crosscheck",
    "require_section_document",
]

#: ★ 单位说明（**实测**，写在一个地方供工具说明引用）：
#:   `Volume` mm³ · `SurfaceArea` mm² · `CenterOfMass` mm（三分量）
#:   `Density` 官方惯用 kg/m³（★ 未实测确认）· `Mass` ★ **物理单位未确证**（见模块头 ③）
UNITS = {
    "volume": "mm^3",
    "surface_area": "mm^2",
    "center_of_mass": "mm",
    "density": "kg/m^3 (official convention; NOT verified on this machine)",
    "mass": "★ PHYSICAL UNIT NOT VERIFIED — see scripts/sw_mass_property.py module header",
}


#: `swDocumentTypes_e`：零件 1 / 装配 2 / **工程图 3**
#: ★ 质量属性对**零件与装配**都有意义；**工程图没有** ⇒ 只排除 3。
SWDOC_PART = 1
SWDOC_ASSEMBLY = 2
SWDOC_DRAWING = 3


def require_mass_property_document(model):
    """确认 `model` 是**零件或装配**（工程图没有质量属性），否则报错。

    ★★ 为什么要它（**真机验证的负例逼出来的**，2026-10-01 轮 234）：
      在**工程图**上调 `Extension.CreateMassProperty` **竟然也返回了一个带 `Mass`/`Volume`
      的对象** ⇒ 若只用"行为判据"（`hasattr(mp,"Mass")`）就会**静默通过**并返回
      **无意义的读数**。
      ⇒ ★ 教训：**行为判据证明"这个成员存在"，不证明"这个读数是这个文档的"**
        —— 它必须**配合文档类型判据**（事实 161/167 那条定则的边界）。
    ★ 同一纪律的镜像用法：`scripts/sw_drawing_query.require_drawing` 判的是"**必须是工程图**"；
      这里判的是"**不能是工程图**"。
    """
    if model is None:
        raise ValueError("model 为 None")
    try:
        doc_type = int(get_com_member(model, "GetType"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "读不到文档类型（GetType 失败）：%s" % str(exc)[:80]
        ) from exc
    if doc_type == SWDOC_DRAWING:
        raise RuntimeError(
            "当前文档是**工程图**，它没有质量属性（GetType()=3；"
            "质量属性只有零件(1)与装配(2)有）—— ★ 不要拿工程图的读数当零件用"
        )
    return model


def mass_property_object(model):
    """取 `IMassProperty2`。

    ★★ **当属性取即可**（真机实测）—— 与 `Extension.CustomPropertyManager`（要当方法调）**相反**。
    ⚠ 判据用**行为**（它有没有 `Mass`/`Volume`），**不用类型** ——
      类型判据判不出 method 对象，那正是事实 161 里假阳性的来源。
    ⚠⚠ **但行为判据不够**：实测在**工程图**上也会拿到一个"有 Mass/Volume 的对象"
      ⇒ 所以**先**做文档类型判据（见 `require_mass_property_document`）。
    """
    if model is None:
        raise ValueError("model 为 None")
    require_mass_property_document(model)  #: ★★ 先判类型（负例逼出来的）
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 model.Extension —— 无法读质量属性")
    #: ★★★★ 2026-10-01（轮 263，**修地基 D3 查出的真 bug**）：★ **必须先用 `CreateMassPr
    #: operty2`**。
    #:   ★ 真机对照实验（`tools/probe_mass_units_controlled.py`）证据：
    #:     · **老入口** `CreateMassProperty`（官方标注 **Obsolete**）拿到的对象
    #: ⇒ ★★ **`Recalculate` 不可达**（真机报 `<unknown>.Recalculate` —— **事实 36 的形态
    #: **：
    #:         名字在 `IMassProperty2` 里存在，但**挂在别的接口上**）；
    #:       ⇒ ★★★ **且 `Density` 恒为 `1000.0`，赋了 `AISI 1020`（≈7900 kg/m³）也不变**
    #:         ⇒ **读数是错的**（★ "看起来对、实际错" —— 最危险的一类）。
    #:     · **新入口** `CreateMassProperty2` ⇒ ★ `Recalculate` 可达 · ★ **`Density` 实测
    #:       `1000.0 → 7900.0`**（★ 随材料变，**与材料库一致**）。
    #:   ★ 官方依据：`C:\swapi\types\IModelDocExtension\CreateMassProperty.md`
    #:     「**Obsolete. Superseded by `IModelDocExtension::CreateMassProperty2`**」。
    #:   ★★ **顺序**：新入口优先，老入口**仅作兜底**（★ 且**不假装它等价**）。
    mp = None
    entry_used = None
    for _nm in ("CreateMassProperty2", "CreateMassProperty"):
        cand = get_com_member(ext, _nm)
        if cand is not None and (hasattr(cand, "Mass") or hasattr(cand, "Volume")):
            mp, entry_used = cand, _nm
            break
        #: 兜底：个别环境下可能被封成方法 ⇒ 再试一次（判据仍是行为，事实 161）
        if callable(cand):
            try:
                alt = cand()
                if hasattr(alt, "Mass") or hasattr(alt, "Volume"):
                    mp, entry_used = alt, _nm
                    break
            except Exception:  # noqa: BLE001
                pass
    if mp is None:
        raise RuntimeError(
            "取不到质量属性对象（CreateMassProperty2 / CreateMassProperty 既不像对象、"
            "调用后也不像对象；★ 判据是它有没有 Mass/Volume）"
        )
    #: ★ 把**用了哪个入口**记在对象上（★ 供调用方回读时如实报出 —— ★ 不静默）
    try:
        mp._dsh_entry_used = entry_used  # noqa: SLF001
    except Exception:  # noqa: BLE001
        pass
    return mp


#: ★★ **截面属性**（规格 211 · B1-1）—— 官方 24 元数组的**下标定义**
#: ★ 官方依据：`C:\swapi\types\IModelDocExtension\GetSectionProperties2.md` 的 `## Remar
#: ks`
#:   「The format of the returned array (retval) of size 24」+ 逐项下标 ✓
#: enum-gate: not-enum index
SECTION_INDEX = {
    "status": 0,
    "area": 1,
    "centroid_x": 2,
    "centroid_y": 3,
    "centroid_z": 4,
    "inertia_xx": 5,
    "inertia_yy": 6,
    "inertia_zz": 7,
    "inertia_xy": 8,
    "inertia_zx": 9,
    "inertia_yz": 10,
    "polar_moment": 11,
    "principal_axis_angle": 12,
    "principal_inertia_lx": 13,
    "principal_inertia_ly": 14,
}

#: ★★ 官方给的 `retval[0]`（status）取值与含义 ✓
SECTION_STATUS = {
    0: "success",
    1: "invalid input",
    2: "selected faces are not in the same or parallel planes",
    3: "unable to compute section properties",
}

#: ★★★ **本成员的副作用**（★ 官方逐字，★ 必须如实登记）：
#:   「**This method clears the selection set.**」
#: 「The objects in the `Sections` parameter **are added to the current selection set**.
#: 」
#:   ⇒ ★★ **它会清空并重写选择集** ⇒ ★ 按**规格 210** 的效应声明体系，
#:     ★★ **它不许被标 `read_only`** ✓
SECTION_SIDE_EFFECT = "clears_and_rewrites_selection"

#: ⚠⚠ ★★ **本模块实测到的一处"官方与真机不符"，如实记在这里**（铁律 5）：
#:   ★ 官方 `C:\swapi\types\IFace2\GetArea.md` 的 `## Returns` 写着
#:     「**Face area in square meters**」；
#:   ★★ 而真机（`tools/probe_spec211_section_units_cube.py`，20×20×20 正方体）读到：
#:     · **两个端面**读数 = **400** ⇒ ★ **正是 20×20 的真面积（mm²）** ✓
#:     · **四个侧面**读数 = **0.4** ⇒ ★ 而它们**也应是 400** ✗（差 **1000** 倍）
#:   ⇒ ★★★ **1000 不是任何面积换算**（1 cm² = 100 mm²）⇒ ★ 所以这不是"单位差"，
#:     而是 ★ **那四个面"读的不是同一个东西"** ✗
#:   ⇒ ★★ 处置：★ **不断言单位**；★ 调用方拿到 `units_verified: False`，★ 自己做判断 ✓
#:     ★（★ 铁律 5：**查不到就说查不到** —— 不许为了让返回值"好看"而编一个单位）✓
SECTION_UNIT_CAVEAT = (
    "★★ 面积单位**未确证**：正方体实验里端面读 400（= 20×20 的真值，mm²），"
    "而四个侧面读 0.4（应为 400，差 1000 倍）；★ 1000 不是面积换算 ⇒ "
    "★ 不是单位差、而是那类面读的不是同一个东西。★ 见 "
    "`output/spec211-b1-section-units-cube.json` 与 `tools/probe_spec211_section_units_cube.py`"
)

#: ★★★ 2026-10-07（规格 212 · E-1）：★ **统一到仓里的既有约定 `unit_assumption`** ✓
#:   ★ 发现经过：★ 我在规格 211 · B1-1 里**临时造**了 `units_verified` + `unit_caveat`，
#:     ★★ 而扫描时发现**仓里早有** `unit_assumption`（★ 7 处：★ `sw_curve_and_split.py` ·
#:     ★ `sw_drawing_create_missing.py` ×2 · ★ `sw_sheet_metal_weld_entry.py` ×4）✓
#:   ★ 依据**铁律 1「只缝合不发明」** ⇒ ★ **该用既有约定的键名** ✓
#:   ★★ **两个键并存、各有用途**（★ 不是二选一）：
#:     · `unit_assumption` = **说法**（★ 字符串、★ 人读、★ 格式统一 ✓）
#:     · `units_verified`  = **机器可判的布尔**（★ 供门禁与调用方**一眼判断** ✓）
#:   ★★ 三者的关系（★ 规格 212 · E-1 的判据）：★ `units_verified: False` ⇒
#:     ★ **必须同时**带 `unit_caveat` **与** `unit_assumption` ✓
SECTION_UNIT_ASSUMPTION = (
    "★ 官方 `IFace2.GetArea` 的 `## Returns` 说 **square meters**，★ 而真机读数与之**不符**"
    " ⇒ ★ **本模块不断言单位**；★ 已登记为「官方声明 vs 真机读数」冲突、★ 未解决"
    "（★ 见 `docs/unit-conflicts.md` 第 1 条）"
)


def require_section_document(model):
    """★ 截面属性**只对零件/装配有**（★ 工程图没有）—— ★ 判据同质量属性（先判类型）✓

    ★★ 为什么先判类型：★ 本模块的 `mass_property_object` 吃过这个亏 ——
      ★ 工程图上也能拿到一个"有 Mass/Volume 的对象"✗（见它的 docstring ①）✓
    """
    return require_mass_property_document(model)


def section_properties(
    model, selection: str = "", selection_kind: str = "FACE"
) -> dict[str, Any]:
    """读**当前选择集**的截面属性（★ 规格 211 · B1-1）。

    ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**加声明式选区入口** ——
      ★ 起因：★ 见下面 ②「**它用"当前选择集"当输入** ⇒ ★ 调用方必须先把东西选好」，
        ★ 而**注入解析器会清空选区**（**事实 503**）⇒ ★ 模型**没有任何办法**先选好 ✗
      ★ 规则 3 **不许收裸坐标** ⇒ ★ 收 `selection`（`index:<n>` / `__current_selection__`）+ `selection_kind` ✓
      ★★ **注意顺序**：★ 选完**立刻**读 —— ★ 本函数**自己有副作用**（★ 见 ③ 它**清空并重写**选择集），
        ★ 所以"选一次、读一次"这个配对**不能被打断** ✓

    :returns: `{ok, status, status_text, area, centroid, side_effect, units_verified,
               unit_caveat, entry_used, raw_len, error}`

    ★★★ **三个必须知道的真机事实**（全部有读数，见模块头与证据文件）：
      ① ★ **入口是"当属性取"** —— `type(getattr(ext, "GetSectionProperties2"))` 是 **`tuple`**、
         ★ `callable(...)` 为 **假**，★ **而求值即返回结果** ✓
         ★（★ 与仓里记的 `Extension` 上"有的成员当属性取"同型；★ 对照：`GetMassProperties2`
           是 `method` ⇒ ★★ **必须按行为判，不能按签名判**）✓
      ② ★★ **它用"当前选择集"当输入** —— ★ 所以**调用方必须先把东西选好** ✓
         ★（★ 属性形态**吃不到 `Sections` 形参** ⇒ ★★ **本包装只支持"用当前选择集"**，
           ★ **不支持显式传 `Sections`** —— ★ 如实记，不假装支持）✓
      ③ ★★★ **它有副作用**：★ 官方写它**清空并重写选择集** ⇒ ★ 见 `SECTION_SIDE_EFFECT` ✓

    ★ 判据（★ 一律回读，不看"有没有抛异常"）：
      · `retval[0]`（官方定义的 status）★ 且
      · ★★ 面积可与 `IFace2.GetArea()` **交叉验证**（★ 12/12 次完全相同）⇒ 见 `section_area_crosscheck` ✓
    """
    out = {
        "ok": False,
        "side_effect": SECTION_SIDE_EFFECT,
        #: ★★ 规格 212 · E-1：★ 三个键**必须同时出现**（★ 见 `SECTION_UNIT_ASSUMPTION
        #: ` 的注释）✓
        "units_verified": False,
        "unit_caveat": SECTION_UNIT_CAVEAT,
        "unit_assumption": SECTION_UNIT_ASSUMPTION,
        "entry_used": None,
        "error": "",
    }
    try:
        require_section_document(model)
        #: ★★★ 2026-10-07（接手轮 · 规格 216 T-216-07）按声明式选择器**重建**选区，
        #:   并让它**紧接**在下面那次读取之前（★ 本函数自己有"清空并重写选择集"的副作用，
        #:   所以"选一次、读一次"这个配对不能被打断）✓
        #:   ★ 依据：★ 注入解析器**会清空选区**（**事实 503**）⇒ 模型没法先选好 ✗
        if str(selection or "").strip():
            import sw_selection_spec as _ss

            try:
                _ss.resolve_selection(
                    model, str(selection), str(selection_kind or "FACE")
                )
            except Exception as exc:  # noqa: BLE001
                out["error"] = (
                    "选区未建立：%s: %s（★ 前置未成立、★ 与「求不出截面属性」是两件事）"
                    % (type(exc).__name__, str(exc)[:140])
                )
                return out
        ext = get_com_member(model, "Extension")
        if ext is None:
            out["error"] = "取不到 model.Extension"
            return out
        #: ★★ **行为判据认入口**：★ 先当**属性**取（★ 实测就是这一形态）✓
        vals, entry = None, None
        raw = getattr(ext, "GetSectionProperties2", None)
        if raw is not None and not callable(raw):
            try:
                vals, entry = tuple(raw), "GetSectionProperties2(property)"
            except Exception:  # noqa: BLE001
                vals = None
        #: ★ 兜底：若被包成方法 ⇒ 试一次**空实参**（★ 只作兜底，★ 不假装等价）✓
        if vals is None:
            try:
                cand = get_com_member(ext, "GetSectionProperties2", None)
                if cand is not None:
                    vals, entry = tuple(cand), "GetSectionProperties2(method)"
            except Exception as exc:  # noqa: BLE001
                out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        if vals is None:
            out["error"] = out["error"] or "两种形态都拿不到结果"
            return out
        out["entry_used"] = entry
        out["raw_len"] = len(vals)
        st = vals[SECTION_INDEX["status"]] if len(vals) > 0 else None
        out["status"] = st
        out["status_text"] = SECTION_STATUS.get(
            int(st) if st is not None else -1, "unknown"
        )
        if len(vals) > 1:
            out["area"] = vals[SECTION_INDEX["area"]]
        if len(vals) > 4:
            out["centroid"] = [
                vals[SECTION_INDEX[k]]
                for k in ("centroid_x", "centroid_y", "centroid_z")
            ]
        out["ok"] = (int(st) == 0) if st is not None else False
        return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        return out


def section_area_crosscheck(model) -> dict[str, Any]:
    """★ **交叉验证**：把当前选中面的 `IFace2.GetArea()` 与截面属性面积对照 ✓

    ★★★ 为什么值得做：★ 真机 **12/12 次**里 `retval[1]` 与 `IFace2.GetArea()`
      **完全相同** ⇒ ★★ 两个**独立的官方成员**给出同一个数 ⇒
      ★ 这比"单看一个返回值"强得多（★ 本仓"判据一律回读"的精神）✓
    ★⚠ 但**它们一致不等于单位已确证** —— ★ 见 `SECTION_UNIT_CAVEAT`（★ 侧面那 1000 倍仍无解释）✓
    """
    out = {"agree": None, "get_area": None, "area": None, "error": ""}
    try:
        sect = section_properties(model)
        out["area"] = sect.get("area")
        sm = get_com_member(model, "SelectionManager")
        face = get_com_member(sm, "GetSelectedObject6", 1, -1)
        if face is None:
            out["error"] = "当前没有选中对象（★ 截面属性吃选择集，★ 先选）"
            return out
        out["get_area"] = float(get_com_member(face, "GetArea"))
        if out["area"] is not None:
            out["agree"] = abs(float(out["area"]) - out["get_area"]) <= 1e-9
    except Exception as exc:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return out


def mass_properties(model) -> dict[str, Any]:
    """读**质量属性读数**。

    :returns: `{volume, surface_area, center_of_mass, density, mass, units}`
        ★ **不做任何换算**（单位见 `UNITS`；`mass` 的物理单位**未确证**）。
    """
    mp = mass_property_object(model)

    #: dispatch-guard: exempt internal-helper
    def _num(name):
        try:
            return float(get_com_member(mp, name))
        except Exception:  # noqa: BLE001
            return None

    com = None
    try:
        raw = get_com_member(mp, "CenterOfMass")
        com = [float(x) for x in raw]
    except Exception:  # noqa: BLE001
        com = None

    return {
        "volume": _num("Volume"),
        "surface_area": _num("SurfaceArea"),
        "center_of_mass": com,
        "density": _num("Density"),
        "mass": _num("Mass"),
        "units": dict(UNITS),
    }
