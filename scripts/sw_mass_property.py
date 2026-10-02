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

__all__ = ["SWDOC_PART", "SWDOC_ASSEMBLY", "SWDOC_DRAWING",
           "require_mass_property_document", "mass_property_object",
           "mass_properties"]

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
    except Exception as exc:                                    # noqa: BLE001
        raise RuntimeError("读不到文档类型（GetType 失败）：%s" % str(exc)[:80]) from exc
    if doc_type == SWDOC_DRAWING:
        raise RuntimeError(
            "当前文档是**工程图**，它没有质量属性（GetType()=3；"
            "质量属性只有零件(1)与装配(2)有）—— ★ 不要拿工程图的读数当零件用")
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
    require_mass_property_document(model)          #: ★★ 先判类型（负例逼出来的）
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 model.Extension —— 无法读质量属性")
    #: ★★★★ 2026-10-01（轮 263，**修地基 D3 查出的真 bug**）：★ **必须先用 `CreateMassProperty2`**。
    #:   ★ 真机对照实验（`tools/probe_mass_units_controlled.py`）证据：
    #:     · **老入口** `CreateMassProperty`（官方标注 **Obsolete**）拿到的对象
    #:       ⇒ ★★ **`Recalculate` 不可达**（真机报 `<unknown>.Recalculate` —— **事实 36 的形态**：
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
            except Exception:                                  # noqa: BLE001
                pass
    if mp is None:
        raise RuntimeError(
            "取不到质量属性对象（CreateMassProperty2 / CreateMassProperty 既不像对象、"
            "调用后也不像对象；★ 判据是它有没有 Mass/Volume）")
    #: ★ 把**用了哪个入口**记在对象上（★ 供调用方回读时如实报出 —— ★ 不静默）
    try:
        mp._dsh_entry_used = entry_used                       # noqa: SLF001
    except Exception:                                          # noqa: BLE001
        pass
    return mp


def mass_properties(model) -> dict[str, Any]:
    """读**质量属性读数**。

    :returns: `{volume, surface_area, center_of_mass, density, mass, units}`
        ★ **不做任何换算**（单位见 `UNITS`；`mass` 的物理单位**未确证**）。
    """
    mp = mass_property_object(model)

    def _num(name):
        try:
            return float(get_com_member(mp, name))
        except Exception:                                      # noqa: BLE001
            return None

    com = None
    try:
        raw = get_com_member(mp, "CenterOfMass")
        com = [float(x) for x in raw]
    except Exception:                                          # noqa: BLE001
        com = None

    return {
        "volume": _num("Volume"),
        "surface_area": _num("SurfaceArea"),
        "center_of_mass": com,
        "density": _num("Density"),
        "mass": _num("Mass"),
        "units": dict(UNITS),
    }
