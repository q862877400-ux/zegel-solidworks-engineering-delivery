# 曲面/剪裁曲面（surface_trim）

> 抄录对象：SolidWorks 功能项 **曲面/剪裁曲面**（slug = `surface_trim`）
> 候选成员名（线索，不是答案）：`InsertCutSurface` / `InsertTrimSurface` / `ITrimSurfaceFeatureData` / `ICutSurfaceFeatureData`
> 检索根：`C:\swapi\types\`（递归）

## 找页结果

| 候选名 | 命中页 | 处置 |
|---|---|---|
| `InsertCutSurface` | **2 份** —— `IFeatureManager\InsertCutSurface.md` + `IModelDoc2\InsertCutSurface.md` | 同名多接口 ⇒ **每份都抄**（见下） |
| `InsertTrimSurface` | **0 份** | 递归 `InsertTrimSurface*.md` 命中为空 ⇒ **官方没写** |
| `ITrimSurfaceFeatureData` | **0 份** | `C:\swapi\types\ITrimSurfaceFeatureData\` 目录不存在 ⇒ **官方没写** |
| `ICutSurfaceFeatureData` | **0 份** | `C:\swapi\types\ICutSurfaceFeatureData\` 目录不存在 ⇒ **官方没写** |

★ 命中页共 **2 份**，以下分两节**各自整段逐字抄**（页头 → Signature 行，不省略、不改写）。

---

## 页 A · `C:\swapi\types\IFeatureManager\InsertCutSurface.md`

## 页头逐字段（逐字）

```
---
type: IFeatureManager
member: InsertCutSurface
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertCutSurface

Inserts a surface-cut feature using the preselected surface or plane.

```

## Signature（逐字）

```
**Signature**: `Feature InsertCutSurface( System.bool Flip, System.int KeepPieceIndex, System.bool UseFeatScope, System.bool UseAutoSelect, System.object Bodies, out System.int Error )`
```

- Obsolete: 无

★ 本页**不是**废弃页，无后继要追。

## Remarks（逐字）

★ 本页**有** `## Remarks` 标题 ⇒ 全文逐字：

```
## Remarks
When there is ambiguity in the result of a cut, KeepPieceIndex is used to resolve which of the possible results is used. This can be set to -1 if there is no ambiguity; otherwise, it should be the index of the result, starting from 0 (up to one less than the possible number of outcomes).
```

（附）本节 `## Parameters` / `## Returns` / `## See Also` 逐字：

```
## Parameters
- **Flip**: True to flip the direction of the cut, false to not
- **KeepPieceIndex**: Piece to keep if there is ambiguity (see **Remarks**)
- **UseFeatScope**: True to cut only the bodies passed to Bodies that intersect with the cut, false to cut all bodies that intersect with the cut
- **UseAutoSelect**: True to automatically cut all bodies that intersect with the cut, false to cut only the bodies passed to Bodies that intersect with the cut
- **Bodies**:
  - Array of specific [[bodies]] that intersect with the cut

    - UseFeatScope = true

    - UseAutoSelect = false

  - or -

  - Empty array indicating to cut all bodies that intersect with the cut

    - UseFeatScope = false

    - UseAutoSelect = true
- **Error**: Status of the cut as defined in [[swSurfaceCutFeatureError_e]]

## Returns
Surface-cut [[feature]]
```

```
## See Also

- [[IFeatureManager Interface]]
- [[IFeatureManager Members]]
- [[ISurfaceCutFeatureData Interface]]
```

## Examples

本页**有** `## Examples` 段，列出例子文件名：

- `Insert_Surface-cut_Feature_Example_CSharp.md`
- `Insert_Surface-cut_Feature_Example_VBNET.md`
- `Insert_Surface-cut_Feature_Example_VB.md`

★ 三个文件在 `C:\swapi\examples\` 下**均实际存在**（已核对文件名）。

---

## 页 B · `C:\swapi\types\IModelDoc2\InsertCutSurface.md`

## 页头逐字段（逐字）

```
---
type: IModelDoc2
member: InsertCutSurface
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertCutSurface

Obsolete. Superseded by [[IFeatureManager::InsertCutSurface]].

```

## Signature（逐字）

```
**Signature**: `void InsertCutSurface( System.bool Flip, System.int KeepPieceIndex )`
```

- Obsolete: `Obsolete. Superseded by [[IFeatureManager::InsertCutSurface]].`（逐字，同页正文第 12 行）

★ **本页判为废弃** ⇒ 后继是 **`IFeatureManager::InsertCutSurface`**（即页 A）⇒ **后继的 Signature 已逐字抄在页 A**。
★ 后继页 **无 Obsolete 句** ⇒ 整条链到此终止，不再往上追。

**废弃链（逐级）**

```
IModelDoc2.InsertCutSurface            (Obsolete · void InsertCutSurface(bool Flip, int KeepPieceIndex))
  └─→ IFeatureManager.InsertCutSurface (非 Obsolete · Feature InsertCutSurface(bool Flip, int KeepPieceIndex, bool UseFeatScope, bool UseAutoSelect, object Bodies, out int Error))   ← 链尾
```

## Remarks（逐字）

★ 本页**有** `## Remarks` 标题 ⇒ 全文逐字：

```
## Remarks
When there is ambiguity in the result of a cut, KeepPieceIndex is used to resolve which of the possible results is used. This can be set to -1 if there is no ambiguity; otherwise, it should be the index of the result, starting from 0 (up to one less than the possible number of outcomes).
```

（附）本节 `## Parameters` / `## See Also` 逐字：

```
## Parameters
- **Flip**: True to flip the direction, false to not
- **KeepPieceIndex**: Piece to keep if there is ambiguity
```

```
## See Also

- [[IModelDoc2 Interface]]
- [[IModelDoc2 Members]]
- [[ISurfaceCutFeatureData Interface]]
```

## Examples

本页**无 `## Examples` 段** ⇒ **无**。

---

## 指针族 / 本仓现状

### 指针族（`AccessSelections` 全文搜）

- 页 A `IFeatureManager\InsertCutSurface.md`：**全文无 `AccessSelections`** ⇒ **—**
- 页 B `IModelDoc2\InsertCutSurface.md`：**全文无 `AccessSelections`** ⇒ **—**

⇒ **两页命中均非「⚠ 指针族」**。
★ 事实备注（不是本项结论）：`AccessSelections` 只出现在两页 `See Also` 所指的 `ISurfaceCutFeatureData` / `ISurfaceTrimFeatureData` 接口目录下，**不在这两个命中页里**。

### 本仓现状

检索范围：`D:\AI\SW\scripts\` + `D:\AI\SW\mcp-server\`，`**/*.py`。

**① 有真实现（非反射索引）**

`D:\AI\SW\scripts\sw_surface_features.py` —— 真实 COM 调用，不是索引：

- `sw_surface_features.py:1103` —— `get_com_member(fm, "InsertCutSurface", bool(flip), int(keep_piece_index), bool(use_feat_scope), bool(use_auto_select), [], err_out)`，在 `cut_surface_report(...)`（`sw_surface_features.py:1031`）内。
- `sw_surface_features.py:696` / `:917` / `:922-925` —— 注释明确记「`InsertTrimSurface` ★ **swapi 里查不到** → T607（★ 铁律 5）」，与本页「`InsertTrimSurface` 官方没写」一致。
- `sw_surface_features.py:1004-1028` —— 来源块注释，已抄录本页 A 的官方描述与参数语义。
- `sw_surface_features.py:914-944` —— 注释把**「剪裁曲面」**指向 `IFeatureManager.PreTrimSurface` + `PostTrimSurface`（两段式），并记 `C:\swapi\types\IModelDoc2\{Pre,Post}TrimSurface.md` 与 CHM `IFeatureManager~PreTrimSurface.html`。★ 这是**本仓注释自己的说法**，不是本项候选名的官方答案（候选 `InsertTrimSurface` 官方无页）。

**② 仅反射索引（★ 按规矩不算「本仓有实现」）**

`D:\AI\SW\scripts\sw_api_sldworks.py` —— 命中 **14 处**，全部是生成的反射索引条目，**不含实现**：

- `:529` `'ISurfaceCutFeatureData',`
- `:537` `'ISurfaceTrimFeatureData',`
- `:4364` / `:5672` / `:6286` `'InsertCutSurface': …`
- `:9094` / `:25781` `'ISurfaceCutFeatureData': {`
- `:9133` / `:25818` `'ISurfaceTrimFeatureData': {`
- `:16351` `'ISurfaceCutFeatureData': (`
- `:16459` `'ISurfaceTrimFeatureData': (`
- `:21121` `'InsertCutSurface': 216,`
- `:22409` / `:23023` `'InsertCutSurface': 65975,`

⇒ **（仅反射索引，不算实现）**

**③ 结论**

- 候选 `InsertCutSurface`：**本仓有真实现**（`scripts\sw_surface_features.py:1103`）。
- 候选 `InsertTrimSurface` / `ITrimSurfaceFeatureData` / `ICutSurfaceFeatureData`：**官方没写**，本仓**也无实现**（仅在 `sw_surface_features.py` 的注释里被记为「查不到」）。