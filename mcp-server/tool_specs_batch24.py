"""第二十四批 MCP 工具声明：**读质量属性** 1 个（砌墙 W5 / Spec Kit `138`）。

## ★★★ 本批补的又是一个**真空白**（与 W3 同型）
```
· `sw_export.set_mass_property_override`（**改**覆盖值）—— 已有。
· ★ 而**读不出实际质量属性**（MCP 与能力层都没有，见事实 166 的核查）
⇒ 而「这个零件多重 / 体积多少 / 重心在哪」是**最常被问的问题之一**。
★ 与 W3「能写自定义属性却读不回来」（`specs/133`）**同一个形状**。
```

## ★ 为什么只有 **1** 个工具
```
`Volume` / `SurfaceArea` / `CenterOfMass` / `Density` / `Mass` 这几样**总是被一起问**
（"这零件多重、多大、重心在哪"）⇒ ★ 拆成 5 个工具只会让 AI 多调 4 次拿同一件事。
★ 与 W3 的定则一致（`count`/`names` 已被"读全部"包含 ⇒ 不重复挂）。
```

## ★★★ 三条由真机探针定死的形态（`tools/probe_mass_property_reads.py`，轮 233）
```
① 取法：★ **`model.Extension.CreateMassProperty` 是属性**（当属性取就拿到对象）
   ⚠⚠ **与 `Extension.CustomPropertyManager` 相反**（那个**必须当方法调用**，见事实 161）
   ⇒ ★ 定则：**同一个父对象的不同成员，取法也可能不同** —— 教训**不能照搬**。

② 单位：★ 实测是**「毫米系」**（盒 40×20×10 mm ⇒ Volume **8000** · SurfaceArea **2800** ·
   CenterOfMass z = **−5**）—— **不是** SI 米。⇒ 本工具**不做任何换算**。
   ★ `Volume` mm³ · `SurfaceArea` mm² · `CenterOfMass` mm。

③ ⚠⚠ **`Mass` 的物理单位**未确证** ⇒ 工具说明里明写，**不猜**（见模块头）。
   ★ 读数本身照实透传（它是 SolidWorks 给的数，不是我算的）。
```

## ⚠ 不暴露的东西（有据）
```
· `IMassProperty2.AccuracyLevel` —— 实测 **`AttributeError`**（读不到）⇒ 不暴露
· `IModelDoc2.GetMassProperties`（12 个 double 的后备）—— ★ **不用**：
  它比 `IMassProperty2` **少**（没有 Density），而且**要靠位置记次序**
  ⇒ 用**有名字**的成员，不靠位置。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch24.py
# 定位:   「孤立能力暴露」第二十四批 / 砌墙 W5（Spec Kit `138`）。
# 官方签名依据: 不适用（只做参数搬运）；取法与单位依据是真机探针
#          `tools/probe_mass_property_reads.py`（见上）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import ToolSpec

__all__ = ["SPECS_BATCH24"]


SPECS_BATCH24 = [
    ToolSpec(
        name="solidworks_part_mass_properties",
        title="Read Part Mass Properties",
        module="sw_mass_property", function="mass_properties",
        #: ★★★ 2026-10-03（轮 461）**这里原本漏了 inject** —— 真机表现：
        #:   `TypeError: mass_properties() missing 1 required positional argument: 'model'`。
        #:   同类：`solidworks_part_bounding_box` 写的是 `inject='model'` ✓
        #:   ⇒ ★ 而未声明注入时，调用不带文档 ⇒ 包装拿到 0 个实参 ⇒ 必炸。
        #:   ★★ 而**没有门禁查这件事**（`check_param_binding` 判的是「声明名 ∈ 形参」，
        #:      不判「注入的对象覆盖了包装的**必需**形参」）⇒ 故它静静躺在柜台上。
        inject="model",
        params=[],
        doc="Read the mass properties of the ACTIVE part, without any conversion: volume (mm^3), "
            "surface area (mm^2), centre of mass (mm, three components) and density. "
            "★★ IMPORTANT: the API is measured to return MILLIMETRE-based values (a 40x20x10 mm box "
            "reports volume 8000 and surface area 2800), NOT SI metres — so nothing here is scaled. "
            "⚠★ `mass` is passed through as reported, but ITS PHYSICAL UNIT IS NOT VERIFIED: on the "
            "test box its value equals volume(mm^3) x density, which does not form a consistent "
            "unit with either mm^3 or m^3 — treat the number as unverified rather than assume a unit. "
            "⚠ `AccuracyLevel` is not exposed (the member is not readable on this build). "
            "★ Reading only; writing overrides is a different capability.",
    ),
]
