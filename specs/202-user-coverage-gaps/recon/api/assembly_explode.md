# 装配/爆炸视图（assembly_explode）

- 官方路径：`C:\swapi\types\IAssemblyDoc\CreateExplodedView.md`（主）+ `C:\swapi\types\IPartDoc\CreateExplodedView.md`
- 找页过程：递归搜 `C:\swapi\types\**\CreateExplodedView*.md` ⇒ 0 份；改搜 `*Explod*.md` ⇒ 0 份；全文搜 `ExplodedView` ⇒ 命中 100 处，据此定位到 **2 份同名页**（`IAssemblyDoc` / `IPartDoc`）⇒ 同名多接口，两份都抄。
- 命中数：**2 份**（`IAssemblyDoc.CreateExplodedView` / `IPartDoc.CreateExplodedView`）

## 页头逐字段（逐字）

★ 「页头前五行到 Signature 那一行」整段逐字。

**【IAssemblyDoc 页】`C:\swapi\types\IAssemblyDoc\CreateExplodedView.md` 第 1–14 行：**

```
---
type: IAssemblyDoc
member: CreateExplodedView
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IAssemblyDoc.CreateExplodedView

Creates an explode view of the active assembly configuration.

**Signature**: `System.bool CreateExplodedView()`
```

**【IPartDoc 页】`C:\swapi\types\IPartDoc\CreateExplodedView.md` 第 1–14 行：**

```
---
type: IPartDoc
member: CreateExplodedView
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.CreateExplodedView

Creates an explode view of this multibody part.

**Signature**: `System.bool CreateExplodedView()`
```

## Signature（逐字）

**【IAssemblyDoc 页】**

```
**Signature**: `System.bool CreateExplodedView()`
```

**【IPartDoc 页】**

```
**Signature**: `System.bool CreateExplodedView()`
```

**【IAssemblyDoc 页 · Returns 段逐字】**

```
## Returns
True if the explode view is successfully created, false if not
```

**【IPartDoc 页 · Returns 段逐字】**

```
## Returns
True if the explode view is successfully created, false if not
```

- Obsolete: **无**（`IAssemblyDoc` 页逐字）—— ★ 已核对上面那段整段原文（第 1–14 行），**其中没有任何 Obsolete 句**，故不存在后继链。
- Obsolete: **无**（`IPartDoc` 页逐字）—— ★ 同上，第 1–14 行整段中无任何 Obsolete 句，故不存在后继链。

## Remarks（逐字，或「本页无 ## Remarks 段」）

**【IAssemblyDoc 页】★ 本页**有** `## Remarks` 标题 ⇒ 以下为该段全文：**

```
## Remarks
Call this method multiple times to add multiple explode views to the active assembly configuration.

Perfect explode views often require user interaction. This method attempts to create a perfect explode view based on the current mate conditions.
```

**【IPartDoc 页】本页无 `## Remarks` 段**（★ 判据：该页第 1–29 行全文只有 front matter、`#` 标题、描述行、`**Signature**`、`## Returns`、`## See Also` —— ★ 没有 `## Remarks` 这个标题）。

## Examples

**【IAssemblyDoc 页】`## Examples` 段列出的例子文件名（3 个）：**

- `Create_Exploded_Views_Example_VB.md` —— 原文：`[Create Exploded Views of an Assembly (VBA)](../../examples/Create_Exploded_Views_Example_VB.md)`
- `Create_Exploded_Views_Example_VBNET.md` —— 原文：`[Create Exploded Views of an Assembly (VB.NET)](../../examples/Create_Exploded_Views_Example_VBNET.md)`
- `Create_Exploded_Views_Example_CSharp.md` —— 原文：`[Create Exploded Views of an Assembly (C#)](../../examples/Create_Exploded_Views_Example_CSharp.md)`

**【IPartDoc 页】无**（该页无 `## Examples` 段）

## 指针族 / 本仓现状

**指针族**：**—**（★ 两份页全文均无 `AccessSelections` —— `IAssemblyDoc` 页 44 行、`IPartDoc` 页 29 行全文搜索 0 命中 ⇒ 不是指针族）

**本仓现状**（搜 `D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`，成员名 `CreateExplodedView`）：

| # | 位置 | 命中形态 | 算不算实现 |
|---|---|---|---|
| 1 | `D:\AI\SW\scripts\sw_assembly_doc.py:110` | `'CreateExplodedView': 0,` —— 位于 `ASSEMBLY_DOC_ARITY: dict[str, int]` **字典字面量**内（该表**机械生成、不手抄**，生成器 `D:\AI\SW\tools\gen_member_registry.py`，见该文件第 80–82 行的来源块） | ★ **不算实现** —— ★ 是「能力名 → 实参个数」的**登记表条目**，**没有任何 COM 调用节点** |
| 2 | `D:\AI\SW\scripts\sw_api_sldworks.py:89, 1744, 1780, 7272, 10025, 17543, 18457, 18667, 18703, 23999` 等 | `'CreateExplodedView': 0,` 等 | ★★ **（仅反射索引，不算实现）** —— ★ 这是**生成的反射索引**，本条纪律明令排除 |
| 3 | `D:\AI\SW\mcp-server\` | **无命中**（★ 按 `Explode` 全文搜 0 命中 ⇒ MCP 工具层**没有**任何爆炸视图工具） | — |

**结论（只陈述抄到的事实，不做设计判断）**：

- ★ 本仓**没有** `CreateExplodedView` 的实现 —— `scripts/` 里唯一的非索引命中是 `sw_assembly_doc.py` 的**机械生成 arity 登记表条目**（无调用节点），`mcp-server/` 里 0 命中。
- ★ 旁证（本仓自带的 AST 审计脚本 `D:\AI\SW\tools\audit_gap_implementations.py`，第 11–12 行逐字）：「实测：`CreateExplodedView` / `InsertProtrusionBlend2` / `InsertRevolvedRefSurface` 在 grep 下"有实现"，★ 而**逐行看是在文档串里**」—— ★ 该脚本的判据是 **AST 只看真调用节点**（`get_com_member(o,"M")` 与 `o.M`）。
  ⚠ 注意：该脚本位于 `tools\`，**不在本次指定的搜索范围**（`scripts\` / `mcp-server\`）内，★ 此处仅作旁证列出，不计入上表的命中数。