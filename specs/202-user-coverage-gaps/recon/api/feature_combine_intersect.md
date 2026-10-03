# 特征/组合·相交（feature_combine_intersect）

> **候选名查找结果（先说结论，不代替下面的逐字抄录）**
> - `InsertCombineFeature` ⇒ 命中 **2 份**（同一方法的两个 COM 入口，一份正常调用 + 一份指针族）：`C:\swapi\types\IFeatureManager\InsertCombineFeature.md`、`C:\swapi\types\IFeatureManager\IInsertCombineFeature.md`。
> - `InsertIntersect` ⇒ **官方没写**（在 `C:\swapi\types\` 全树按文件名与全文两种方式检索，0 命中）。
> - `CombineFeatureData` ⇒ **官方没写**（同上，0 命中；不以 `ICombineBodiesFeatureData` / `IIntersectFeatureData` 等相近名字顶替）。
> - 两份命中页的 `## See Also` 均逐字写着 `[[ICombineBodiesFeatureData Interface]]`（见下），但**该接口页本身不是本次候选名的命中页**，故不在本文件逐字抄录范围内。

---

## 页头逐字段（逐字）

### 命中页 A — `C:\swapi\types\IFeatureManager\InsertCombineFeature.md`（第 1–14 行，逐字）

```markdown
---
type: IFeatureManager
member: InsertCombineFeature
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertCombineFeature

Combines the specified bodies in the multibody part to create a combine feature.

**Signature**: `Feature InsertCombineFeature( System.int OperationType, Body2 MainBody, System.object ToolVar )`
```

### 命中页 B — `C:\swapi\types\IFeatureManager\IInsertCombineFeature.md`（第 1–14 行，逐字）

```markdown
---
type: IFeatureManager
member: IInsertCombineFeature
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.IInsertCombineFeature

Combines the specified bodies in the multibody part to create a combine feature.

**Signature**: `Feature IInsertCombineFeature( System.int OperationType, Body2 MainBody, System.int ToolsCount, ref Body2 ToolsArr )`
```

---

## Signature（逐字）

- 命中页 A：`Feature InsertCombineFeature( System.int OperationType, Body2 MainBody, System.object ToolVar )`
- 命中页 B：`Feature IInsertCombineFeature( System.int OperationType, Body2 MainBody, System.int ToolsCount, ref Body2 ToolsArr )`

- Obsolete: **无** —— 两份命中页的页头五项（`type` / `member` / `kind` / `assembly` / `namespace` / `category`）与正文均**没有** Obsolete 句；对两份命中页全文 grep `Obsolete` / `obsolete` 也是 0 命中。⇒ **不判为废弃，无后继链可追。**（`InsertIntersect` / `CombineFeatureData` 两个候选名：官方没写，无页可判废弃。）

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

### 命中页 A 的 `## Remarks`（全文，逐字）

```markdown
## Remarks
You can either call this method, directly passing in the bodies with MainBody and ToolVar, or you can:

1. Select the bodies using [[IModelDocExtension::SelectByID2]] as follows:

To select...
Use Mark...

MainBody
1

ToolVar bodies
2

2. Call this method, setting MainBody to Nothing or null and ToolVar to an empty array.

See the SOLIDWORKS Help for more information about the combine feature.
```

### 命中页 B 的 `## Remarks`（全文，逐字）

```markdown
## Remarks
You can either call this method, directly passing in the bodies with MainBody and ToolVar, or you can:

1. Select the bodies using [[IModelDocExtension::SelectByID2]] as follows:

To select...
Use Mark...

MainBody
1

ToolVar bodies
2

2. Call this method, setting MainBody to Nothing or null and ToolVar to an empty array.

See the SOLIDWORKS Help for more information about the combined feature.
```

（两页都有 `## Remarks` 标题，故两段全粘；差异仅在最后一句 —— A 为 `combine feature`，B 为 `combined feature`，逐字保留。）

---

## Examples

### 命中页 A 的 `## Examples` 段（逐字）

```markdown
## Examples
- [Combine Bodies (C#)](../../examples/Combine_Bodies_Example_CSharp.md)
- [Combine Bodies (VB.NET)](../../examples/Combine_Bodies_Example_VBNET.md)
- [Combine Bodies (VBA)](../../examples/Combine_Bodies_Example_VB.md)
```

三个例子文件名（均在 `C:\swapi\examples\` 下**实测存在** = True）：

1. `Combine_Bodies_Example_CSharp.md`
2. `Combine_Bodies_Example_VBNET.md`
3. `Combine_Bodies_Example_VB.md`

### 命中页 B 的 `## Examples` 段

**无** —— `IInsertCombineFeature.md` 全文**没有 `## Examples` 标题**。

### AccessSelections 全文检索

- 命中页 A `InsertCombineFeature.md`：**无**（对 `AccessSelections` 全文 grep = 0 命中）⇒ **—**
- 命中页 B `IInsertCombineFeature.md`：**无**（同上 0 命中）⇒ **—**

---

## 指针族 / 本仓现状

### 指针族判定

- **命中页 A `InsertCombineFeature`：不是指针族。** 官方 `## Parameters` 对 `ToolVar` 的逐字写法是 `Array of [[bodies]] to combine (see **Remarks**)`，实参形态为 `System.object`（VBA / C# 可用）。
- **命中页 B `IInsertCombineFeature`：⚠ 指针族。** 官方 `## Parameters` 逐字写着：
  - `ToolsCount`: `Number of bodies to combine`
  - `ToolsArr`:
    - `in-process, unmanaged C++: Pointer to an array of [[bodies]] to combine of size ToolsCount (see **Remarks**)`
    - `VBA, VB.NET, C#, and C++/CLI: Not supported`
    - `See [In-process Methods](<../../docs/Programming with the SOLIDWORKS API/In-process Methods.md>) for details about this type of method.`

  ⇒ 该页自身即官方标注的 in-process 非托管 C++ 指针入口（`I` 前缀 + `ref Body2 ToolsArr` 数组 + 显式「Not supported」），与本仓库已知的后端限制同类。
- `AccessSelections` 在两份命中页里都不存在（见上）⇒ **本页不涉及 `AccessSelections` 指针族**。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`）

对 `InsertCombineFeature|IInsertCombineFeature|CombineFeatureData` 全量检索，**唯一命中文件**：

- `D:\AI\SW\scripts\sw_api_sldworks.py` —— 命中 4 处（`:4352` / `:7370` / `:21109` / `:24097`，均为 `InsertCombineFeature` 的登记条目，形如 `'InsertCombineFeature': 3,` / `: 36,` / `: 129,`）。
  ★★ **按死规矩排除**：该文件首行 docstring 逐字写着「**官方 API 的完整抄录** —— 523 个接口族、**8210 个成员**，逐个照抄自对官方 interop 程序集的**纯元数据反射**」⇒ **它是生成的反射索引，不是实现（仅反射索引，不算实现）**。
  ⇒ **本仓无该成员的实现**：`scripts/` 与 `mcp-server/` 里没有任何调用 `InsertCombineFeature` 的代码。
- `IInsertCombineFeature` 在该反射索引里 **0 命中**（其 docstring 自述「COM 内部分发口（名字形如 `IGetXxx`）**不登记**」）⇒ 与该页自标的 in-process 指针族属性一致。