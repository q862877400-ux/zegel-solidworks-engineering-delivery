# 曲面/中面（surface_midsurface）

命中页（`C:\swapi\types\` 递归按候选名查找，共 **3 份**，逐份抄录）：

| # | 页路径 | 归属接口 | 是否废弃 |
|---|---|---|---|
| 1 | `C:\swapi\types\IFeatureManager\InsertMidSurface.md` | `IFeatureManager` | 否（页内无 Obsolete 句） |
| 2 | `C:\swapi\types\IModelDoc2\InsertMidSurfaceExt.md` | `IModelDoc2` | **是** |
| 3 | `C:\swapi\types\IModelDoc2\IInsertMidSurfaceExt.md` | `IModelDoc2` | **是** |

候选名 `InsertMidSurface` / `InsertMidSurfaceExt` / `IInsertMidSurfaceExt` **三份全部命中**（`IInsertMidSurfaceExt` 是 `IModelDoc2` 上的方法页，不是独立接口页；`C:\swapi\types\` 下无 `IInsertMidSurfaceExt` 接口目录）。

---

## 页头逐字段（逐字）

### 页 1 · `C:\swapi\types\IFeatureManager\InsertMidSurface.md`

（文件开头 → `**Signature**:` 那一行，逐字）

```text
---
type: IFeatureManager
member: InsertMidSurface
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertMidSurface

Inserts a midsurface feature.

**Signature**: `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )`
```

### 页 2 · `C:\swapi\types\IModelDoc2\InsertMidSurfaceExt.md`

```text
---
type: IModelDoc2
member: InsertMidSurfaceExt
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertMidSurfaceExt

Obsolete. Superseded by [[IFeatureManager::InsertMidSurface]].

**Signature**: `System.object InsertMidSurfaceExt( System.double Placement, System.bool KnitFlag )`
```

### 页 3 · `C:\swapi\types\IModelDoc2\IInsertMidSurfaceExt.md`

```text
---
type: IModelDoc2
member: IInsertMidSurfaceExt
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.IInsertMidSurfaceExt

Obsolete. Superseded by [[IFeatureManager::IInsertMidSurface]].

**Signature**: `MidSurface2 IInsertMidSurfaceExt( System.double Placement, System.bool KnitFlag )`
```

---

## Signature（逐字）

| 页 | Signature 逐字 |
|---|---|
| 1 `IFeatureManager\InsertMidSurface.md:14` | `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )` |
| 2 `IModelDoc2\InsertMidSurfaceExt.md:14` | `System.object InsertMidSurfaceExt( System.double Placement, System.bool KnitFlag )` |
| 3 `IModelDoc2\IInsertMidSurfaceExt.md:14` | `MidSurface2 IInsertMidSurfaceExt( System.double Placement, System.bool KnitFlag )` |

### - Obsolete:

- 页 1 `IFeatureManager\InsertMidSurface.md`：**无**（该页「Inserts a midsurface feature.」之后直接是 Signature，无 Obsolete 句）。
- 页 2 `IModelDoc2\InsertMidSurfaceExt.md:12`，逐字：`Obsolete. Superseded by [[IFeatureManager::InsertMidSurface]].`
- 页 3 `IModelDoc2\IInsertMidSurfaceExt.md:12`，逐字：`Obsolete. Superseded by [[IFeatureManager::IInsertMidSurface]].`

### 废弃链（逐级追）

**链 A（追到不再废弃，闭合）**

1. `IModelDoc2::InsertMidSurfaceExt` —— **Obsolete**，逐字：`Obsolete. Superseded by [[IFeatureManager::InsertMidSurface]].`
   → 后继页 `C:\swapi\types\IFeatureManager\InsertMidSurface.md` **存在**，Signature 逐字：
   `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )`
   → 该页**无 Obsolete 句** ⇒ **链在此终止（不再废弃）**。

**链 B（后继页本仓未收录 ⇒ 官方没写）**

1. `IModelDoc2::IInsertMidSurfaceExt` —— **Obsolete**，逐字：`Obsolete. Superseded by [[IFeatureManager::IInsertMidSurface]].`
   → 逐级追：`C:\swapi\types\` 递归按 `*MidSurface*` 枚举，**全库只有上述 3 个文件**；
   `Test-Path 'C:\swapi\types\IFeatureManager\IInsertMidSurface.md'` ⇒ **False**。
   ⇒ **后继页 `IFeatureManager::IInsertMidSurface` 官方没写（本套 md 源未收录）** ⇒ **链 B 到此断，无后继 Signature 可抄**。
   ⇒ ★ 不拿 `IFeatureManager::InsertMidSurface`（无 `I` 前缀、参数个数不同、返回类型不同）代替。

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

三份页**均有 `## Remarks` 标题**，逐字全文如下。

### 页 1 · `IFeatureManager\InsertMidSurface.md:25-30`

```text
## Remarks
The pPartDocIn parameter is the component's model document where you want to add the midsurface feature, and the pBody parameter is the body of that component.

A midsurface feature is calculated from the solid body in your part document. This method first finds all parallel pairs of faces from the part solid. For each pair of parallel faces found, it creates a neutral reference surface between the two faces. The placement position of the reference surface is controlled by the placement parameter. This process repeats itself until all parallel body faces are processed. At the end of this process, all the reference surfaces are sewn into a single reference surface if knitFlag is set to true.

The hierarchy of a midsurface feature is a midsurface feature contains one or more reference surfaces. If sewn successfully using the KnitFlag = True option, then the midsurface feature contains only one reference surface. Each reference surface is considered a sheet body. The sheet body has the normal topology that you would expect to find on a body object (for example, faces, edges, and so on). See [[IMidSurface3]] for methods that provide access to this topology.
```

### 页 2 · `IModelDoc2\InsertMidSurfaceExt.md:23-28`

```text
## Remarks
A midsurface feature is calculated from the solid body in your part document. This method first finds all parallel pairs of faces from the part solid. For each pair of parallel faces found, it creates a neutral reference surface between the two faces. The placement position of the reference surface is controlled by the placement parameter. This process repeats itself until all parallel body faces are processed. At the end of this process, all the reference surfaces are sewn into a single reference surface if knitFlag is set to True.

The hierarchy of a midsurface feature is:

A midsurface feature contains one or more reference surfaces. If sewn successfully using the knitFlag = True option, then the midsurface feature contains only one reference surface. Each reference surface is considered a sheet body. The sheet body has the normal topology that you would expect to find on a body object (for example, faces, edges, and so on). See the [[IMidSurface2]] object for methods that provide access to this topology.
```

### 页 3 · `IModelDoc2\IInsertMidSurfaceExt.md:23-28`

```text
## Remarks
A midsurface feature is calculated from the solid body in your part document. This method first finds all parallel pairs of faces from the part solid. For each pair of parallel faces found, it creates a neutral reference surface between the two faces. The placement position of the reference surface is controlled by the placement parameter. This process repeats itself until all parallel body faces are processed. At the end of this process, all the reference surfaces are sewn into a single reference surface if knitFlag is set to True.

The hierarchy of a midsurface feature is:

A midsurface feature contains one or more reference surfaces. If sewn successfully using the knitFlag = True option, then the midsurface feature contains only one reference surface. Each reference surface is considered a sheet body. The sheet body has the normal topology that you would expect to find on a body object (for example, faces, edges, and so on). See the [[IMidSurface2]] object for methods that provide access to this topology.
```

---

## Examples

### 页 1 · `IFeatureManager\InsertMidSurface.md:32-38` —— **有 `## Examples` 段**，6 个例子（逐字照抄，含原文里 `MidSurface` / `FAces` 的大小写与拼写差异）：

```text
## Examples
- [Insert MidSurface in Component (C#)](../../examples/Insert_MidSurface_in_Component_Example_CSharp.md)
- [Insert MidSurface in Component (VB.NET)](../../examples/Insert_MidSurface_in_Component_Example_VBNET.md)
- [Insert MidSurface in Component (VBA)](../../examples/Insert_MidSurface_in_Component_Example_VB.md)
- [Get Areas of Midsurface Faces (C#)](../../examples/Get_Areas_of_MidSurface_Faces_Example_CSharp.md)
- [Get Areas of Midsurface Faces (VB.NET)](../../examples/Get_Areas_of_MidSurface_FAces_Example_VBNET.md)
- [Get Areas of Midsurface Faces (VBA)](../../examples/Get_Areas_of_MidSurface_Faces_Example_VB.md)
```

例子文件名（去目录）：

1. `Insert_MidSurface_in_Component_Example_CSharp.md`
2. `Insert_MidSurface_in_Component_Example_VBNET.md`
3. `Insert_MidSurface_in_Component_Example_VB.md`
4. `Get_Areas_of_MidSurface_Faces_Example_CSharp.md`
5. `Get_Areas_of_MidSurface_FAces_Example_VBNET.md`
6. `Get_Areas_of_MidSurface_Faces_Example_VB.md`

### 页 2 · `IModelDoc2\InsertMidSurfaceExt.md` —— **无**

该页段落顺序为 `## Remarks` → `## See Also`，**无 `## Examples` 标题**。

### 页 3 · `IModelDoc2\IInsertMidSurfaceExt.md` —— **无**

该页段落顺序为 `## Remarks` → `## See Also`，**无 `## Examples` 标题**。

---

## 指针族 / 本仓现状

### 指针族

**⚠ 指针族（命中 1 处 · 页 3）** —— 判据：候选名 `IInsertMidSurfaceExt` 自身就是 `I` 前缀的指针变体，
且其 Signature 返回 `MidSurface2`（`IFeatureManager\InsertMidSurface` 返回 `System.object`，是同一族里**无指针前缀**的那一支）。

`AccessSelections` 全文搜索结果（对全部 3 份命中页）：

| 搜索范围 | 结果 |
|---|---|
| `C:\swapi\types\IFeatureManager\InsertMidSurface.md`（全文 43 行） | **无命中** |
| `C:\swapi\types\IModelDoc2\`（整目录，覆盖页 2 与页 3 两份全文，各 34 行） | **无命中** |

⇒ 三份页的正文里**都不出现 `AccessSelections`**（只有 `I` 前缀与 `MidSurface2` 返回类型这两个指针族信号）。

### 本仓现状

搜索范围：`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`，grep 串 `InsertMidSurface`（精确候选名族）。

| 目录 | 命中 | 位置明细 |
|---|---|---|
| `D:\AI\SW\mcp-server\` | **0** | 无任何命中 |
| `D:\AI\SW\scripts\` | **6** | **全部 6 处都在 `scripts/sw_api_sldworks.py`** |

命中明细（全部在 `scripts/sw_api_sldworks.py`）：

| 行号 | 逐字 |
|---|---|
| 4410 | `'InsertMidSurface': 4,` |
| 5697 | `'InsertMidSurfaceExt': 2,` |
| 6314 | `'InsertMidSurfaceExt': 2,` |
| 21167 | `'InsertMidSurface': 149,` |
| 22434 | `'InsertMidSurfaceExt': 65792,` |
| 23051 | `'InsertMidSurfaceExt': 65792,` |

⇒ ★★ **`scripts/sw_api_sldworks.py` 命中 `scripts/sw_api_*.py` ⇒ 是生成的反射索引，不是实现 ⇒
这 6 处「（仅反射索引，不算实现）」。**

⇒ ★★ **结论：本仓没有 `InsertMidSurface` / `InsertMidSurfaceExt` / `IInsertMidSurfaceExt` 的实现。**
（`mcp-server/` 0 命中；`scripts/` 0 处真实实现，6 处命中全部落在反射索引里。）

**非命中项的排除说明（避免误计）**：`scripts/sw_simulation.py:185` 与 `scripts/sw_simulation_study.py:119`
各有一行 `"mid_surface": 1, # swsMeshTypeMidSurface` —— 那是**网格类型枚举 `swsMeshTypeMidSurface`** 的常量映射，
与本能力项的三个成员名**不是同一个东西**，不计入上表命中。
（仓内另有 `docs/ROADMAP.md:58`、`tools/audit_gap_implementations.py:48`、`specs/202-user-coverage-gaps/research.md:53`、
`specs/202-user-coverage-gaps/recon/surface.md` 等处提及 `InsertMidSurface`，均落在 `docs/` / `tools/` / `specs/`，
不在本次限定的 `scripts/` 与 `mcp-server/` 实现范围内。）

### 拿不准 / 官方没写

- `IFeatureManager::IInsertMidSurface`（页 3 Obsolete 句点名的后继）—— **官方没写**：`C:\swapi\types\` 下无该页，全库仅 3 个 `*MidSurface*` 文件。**未用相近名字顶替。**
- 页 2 / 页 3 的 Remarks 提到 `[[IMidSurface2]]`、页 1 提到 `[[IMidSurface3]]` —— 这些是**返回对象的后继查询接口**，
  不在本次候选名（`InsertMidSurface` / `InsertMidSurfaceExt` / `IInsertMidSurfaceExt`）范围内，故未展开抄录。
