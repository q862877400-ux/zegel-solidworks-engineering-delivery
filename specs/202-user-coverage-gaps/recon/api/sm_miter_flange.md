# 钣金/斜接法兰（sm_miter_flange）

- 检索范围：`C:\swapi\types\` 递归，候选成员名 `InsertSheetMetalMiterFlange` / `IMiterFlangeFeatureData`
- 命中页数：**2**（同名成员分属两个接口，两份都抄）
  - 命中① `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`
  - 命中② `C:\swapi\types\IModelDoc2\InsertSheetMetalMiterFlange.md`
  - （`C:\swapi\types\IMiterFlangeFeatureData\` 目录存在，是命中① See Also 指向的数据接口，见末节「附带事实」）

---

## 页头逐字段（逐字）

### 命中① `C:\swapi\types\IFeatureManager\InsertSheetMetalMiterFlange.md`

以下为该文件**开头至 Signature 行**（第 1–14 行）逐字：

```
---
type: IFeatureManager
member: InsertSheetMetalMiterFlange
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertSheetMetalMiterFlange

Inserts a meter flange in a sheet metal part.

**Signature**: `Feature InsertSheetMetalMiterFlange( System.bool UseDefaultRadius, System.double GlobalRadius, System.double RipGap, System.bool UseDefaultRelief, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth, System.int ReliefType, System.bool TrimSideBends, System.int FlangePos, System.double OffsetDist1, System.double OffsetDist2, CustomBendAllowance PCBA )`
```

### 命中② `C:\swapi\types\IModelDoc2\InsertSheetMetalMiterFlange.md`

以下为该文件**开头至 Signature 行**（第 1–14 行）逐字：

```
---
type: IModelDoc2
member: InsertSheetMetalMiterFlange
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertSheetMetalMiterFlange

Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].

**Signature**: `void InsertSheetMetalMiterFlange( System.bool UseReliefRatio, System.bool UseDefaultGap, System.bool UseAutoRelief, System.double GlobalRadius, System.double RipGap, System.double AutoReliefRatio, System.double AutoReliefWidth, System.double AutoReliefDepth, System.int ReliefType, System.int RipLocation, System.bool TrimSideBends )`
```

---

## Signature（逐字）

- 命中①（`IFeatureManager`）：`Feature InsertSheetMetalMiterFlange( System.bool UseDefaultRadius, System.double GlobalRadius, System.double RipGap, System.bool UseDefaultRelief, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth, System.int ReliefType, System.bool TrimSideBends, System.int FlangePos, System.double OffsetDist1, System.double OffsetDist2, CustomBendAllowance PCBA )`
- 命中②（`IModelDoc2`）：`void InsertSheetMetalMiterFlange( System.bool UseReliefRatio, System.bool UseDefaultGap, System.bool UseAutoRelief, System.double GlobalRadius, System.double RipGap, System.double AutoReliefRatio, System.double AutoReliefWidth, System.double AutoReliefDepth, System.int ReliefType, System.int RipLocation, System.bool TrimSideBends )`

### Obsolete

- 命中①：`无`（该页正文与页头均无 Obsolete 句）
- 命中②：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].`

### 废弃链（逐级追到不再废弃）

1. `IModelDoc2.InsertSheetMetalMiterFlange` —— **Obsolete**，官方指定后继为 `IFeatureManager::InsertSheetMetalMiterFlange`（逐字：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalMiterFlange]].`）
2. `IFeatureManager.InsertSheetMetalMiterFlange` —— 该页无 Obsolete 句 ⇒ **链止于此**

⇒ 链共 2 级，无更多后继。**当前（非废弃）入口 = `IFeatureManager.InsertSheetMetalMiterFlange`，14 个形参，返回 `Feature`**。

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

- 命中①：**本页无 ## Remarks 段**（该文件全部标题逐字为：`# IFeatureManager.InsertSheetMetalMiterFlange` · `## Parameters` · `## Returns` · `## See Also`；无 `## Remarks`）
- 命中②：**本页无 ## Remarks 段**（该文件全部标题逐字为：`# IModelDoc2.InsertSheetMetalMiterFlange` · `## Parameters` · `## See Also`；无 `## Remarks`）

---

## Examples

- 命中①：**无**（该文件无 `## Examples` 段；全文亦无 `Example` 字样）
- 命中②：**无**（该文件无 `## Examples` 段；全文亦无 `Example` 字样）

---

## 指针族 / 本仓现状

### 指针族

- 命中①：全文搜 `AccessSelections` ⇒ 0 命中 ⇒ **—**
- 命中②：全文搜 `AccessSelections` ⇒ 0 命中 ⇒ **—**

**附带事实（★ 非命中页内容，仅记录目录事实，不作为入口页内容、不用于代替命中页）**：
`C:\swapi\types\IMiterFlangeFeatureData\` 目录下确实存在 `AccessSelections.md` / `IAccessSelections.md` / `IAccessSelections2.md` / `ReleaseSelectionAccess.md` 等文件（该接口目录共 23 个 `.md`）。命中① 的 `See Also` 逐字列出：`[[IMiterFlangeFeatureData Interface]]`。

### 本仓现状（`D:\AI\SW\scripts\` + `D:\AI\SW\mcp-server\`）

**结论：本仓无 `InsertSheetMetalMiterFlange` 的实现。**

| 命中位置 | 性质 | 是否算实现 |
|---|---|---|
| `scripts\sw_api_sldworks.py:345, 4454, 5369, 5728, 6350, 13578, 21211, 22106, 22465, 23087` | 生成反射索引 | **否（仅反射索引，不算实现）** |
| `scripts\__pycache__\sw_api_sldworks.cpython-314.pyc` | 上一项的编译缓存 | **否（仅反射索引的缓存，不算实现）** |
| `scripts\sw_sheet_metal.py:299-300` | 仅注释 | 否（无任何调用） |

`scripts\sw_sheet_metal.py:299-300` 逐字：

```
# ⚠ 查不到故不编: swFeatureNameID_e 中**没有** Hem / MiterFlange 对应项，
#   故本批不提供翻边与斜接法兰的 CreateDefinition 入口。
```

⇒ 该注释是**本仓自己的记录**，不是官方原文；本页不据此断言官方枚举有无该项。

### 已排除的同名/近名命中（★ 不作为替代）

- `scripts\sw_weldment.py:23`（`SW_END_CONDITION_MITER = 1`）、`:163`（`corner_treatment_type: int = SW_END_CONDITION_MITER`）、`:194`（`group.MiterMergeCondition = False`）—— 属**焊件端部处理**族（官方类型为 `ITwoMemberCornerTreatmentFeatureData` 等），**与钣金斜接法兰不是同一入口**，按死规矩不拿它代替。
- `scripts\toolbox_index.json` 中的 `"straight miter gear"` 系列 —— Toolbox 零件名，无关。

### 命中数 / 判定汇总

| 项 | 值 |
|---|---|
| 官方命中页数 | **2**（`IFeatureManager` 1 份 + `IModelDoc2` 1 份；同名多接口，两份都抄） |
| 是否废弃 | **部分** —— `IModelDoc2` 那份废弃；**当前有效入口是 `IFeatureManager` 那份（非废弃）** |
| 是否指针族 | **—**（两份命中页全文均无 `AccessSelections`） |
| 拿不准 | **无**（两份页的页头、Signature、标题、Example、AccessSelections 全部为逐字核对；未使用任何相近名字代替） |