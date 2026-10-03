<!-- domain: 曲面 -->

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 旋转曲面 | `InsertRevolvedRefSurface` | `Feature InsertRevolvedRefSurface( System.double Angle, System.bool ReverseDir, System.double Angle2, System.int RevType )` | 无 | `scripts/check_official_md_claims.py:102` · `scripts/check_official_md_claims.py:104` · `scripts/check_official_md_claims.py:109` · `scripts/sw_api_sldworks.py:4433` · `scripts/sw_api_sldworks.py:5717` · `scripts/sw_api_sldworks.py:6334` · `scripts/sw_api_sldworks.py:21190` · `scripts/sw_api_sldworks.py:22454` · `scripts/sw_api_sldworks.py:23071` · `scripts/sw_surface_ref_ops.py:13` · `scripts/sw_surface_ref_ops.py:19` · `scripts/sw_surface_ref_ops.py:35` · `scripts/sw_surface_ref_ops.py:66` · `scripts/sw_surface_ref_ops.py:75` · `scripts/sw_surface_ref_ops.py:107` · `scripts/sw_surface_ref_ops.py:133` · `mcp-server/tool_specs_batch69.py:13` · `mcp-server/tool_specs_batch69.py:22` · `mcp-server/tool_specs_batch69.py:37` | — |
| 剪裁曲面 | `InsertCutSurface` | `Feature InsertCutSurface( System.bool Flip, System.int KeepPieceIndex, System.bool UseFeatScope, System.bool UseAutoSelect, System.object Bodies, out System.int Error )` | 无 | `scripts/sw_api_sldworks.py:4364` · `scripts/sw_api_sldworks.py:5672` · `scripts/sw_api_sldworks.py:6286` · `scripts/sw_api_sldworks.py:21121` · `scripts/sw_api_sldworks.py:22409` · `scripts/sw_api_sldworks.py:23023` · `scripts/sw_surface_features.py:1004` · `scripts/sw_surface_features.py:1009` · `scripts/sw_surface_features.py:1014` · `scripts/sw_surface_features.py:1015` · `scripts/sw_surface_features.py:1022` · `scripts/sw_surface_features.py:1023` · `scripts/sw_surface_features.py:1033` · `scripts/sw_surface_features.py:1103` | — |
| 中面 | `InsertMidSurface` | `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )` | 无 | `scripts/sw_api_sldworks.py:4410` · `scripts/sw_api_sldworks.py:21167` | — |

## 取证过程（逐条事实）

### ① `C:\swapi\types\` 递归搜索结果

| 候选成员名 | 命中文件 |
|---|---|
| `InsertRevolvedRefSurface` | `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md` ＋ `C:\swapi\types\IModelDoc2\InsertRevolvedRefSurface.md` |
| `InsertTrimSurface` | 无 |
| `InsertCutSurface` | `C:\swapi\types\IFeatureManager\InsertCutSurface.md` ＋ `C:\swapi\types\IModelDoc2\InsertCutSurface.md` |
| `InsertMidSurface` | `C:\swapi\types\IFeatureManager\InsertMidSurface.md`（另有 `C:\swapi\types\IModelDoc2\InsertMidSurfaceExt.md`，**是另一个名字 `InsertMidSurfaceExt`，不是本候选名**） |

★ 表里逐字抄的三行 `**Signature**:` 取自 **`IFeatureManager\` 那三份**（`InsertRevolvedRefSurface` / `InsertCutSurface` / `InsertMidSurface` 均同时存在 `IFeatureManager` 与 `IModelDoc2` 两份，取 `IFeatureManager` 那份）。

`IModelDoc2\InsertRevolvedRefSurface.md` 全文第 12 行逐字为：`Obsolete. Superseded by [[IFeatureManager::InsertRevolvedRefSurface]].`
其 `**Signature**:` 逐字为：`void InsertRevolvedRefSurface( System.double Angle, System.bool ReverseDir, System.double Angle2, System.int RevType )`

### ② `**Signature**:` 整行照抄

- `InsertRevolvedRefSurface`（`IFeatureManager\InsertRevolvedRefSurface.md:14`）:
  `Feature InsertRevolvedRefSurface( System.double Angle, System.bool ReverseDir, System.double Angle2, System.int RevType )`
- `InsertCutSurface`（`IFeatureManager\InsertCutSurface.md:14`）:
  `Feature InsertCutSurface( System.bool Flip, System.int KeepPieceIndex, System.bool UseFeatScope, System.bool UseAutoSelect, System.object Bodies, out System.int Error )`
- `InsertMidSurface`（`IFeatureManager\InsertMidSurface.md:14`）:
  `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )`

### ③ `C:\swapi\examples\` 按文件名搜成员名

- `*InsertRevolvedRefSurface*` ⇒ 无文件
- `*InsertCutSurface*` ⇒ 无文件
- `*InsertMidSurface*` ⇒ 无文件

⇒ 三项「官方例子」列全部为 **无**。

★ 事实补记：`IFeatureManager\InsertCutSurface.md` 第 43–46 行有 `## Examples` 段，指向
`../../examples/Insert_Surface-cut_Feature_Example_CSharp.md` / `_VBNET.md` / `_VB.md`；
`IFeatureManager\InsertMidSurface.md` 第 32–38 行有 `## Examples` 段，指向
`../../examples/Insert_MidSurface_in_Component_Example_CSharp.md` / `_VBNET.md` / `_VB.md` 等 6 个。
**但这些文件名里都不含成员名** ⇒ 按本次判据（文件名含即可）仍记 **无**。

### ④ 全文搜 `AccessSelections`

- `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md`（全文 42 行）⇒ 无命中 ⇒ **—**
- `C:\swapi\types\IFeatureManager\InsertCutSurface.md`（全文 52 行）⇒ 无命中 ⇒ **—**
- `C:\swapi\types\IFeatureManager\InsertMidSurface.md`（全文 43 行）⇒ 无命中 ⇒ **—**

⇒ 三项「指针族」列全部为 **—**。

### ⑤ `D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` grep 结果

**`InsertRevolvedRefSurface`** —— 命中 19 处：

- `scripts\check_official_md_claims.py` 行 102 / 104 / 109
- `scripts\sw_api_sldworks.py` 行 4433 / 5717 / 6334 / 21190 / 22454 / 23071
- `scripts\sw_surface_ref_ops.py` 行 13 / 19 / 35 / 66 / 75 / 107 / 133
- `mcp-server\tool_specs_batch69.py` 行 13 / 22 / 37

**`InsertCutSurface`** —— 命中 14 处：

- `scripts\sw_api_sldworks.py` 行 4364 / 5672 / 6286 / 21121 / 22409 / 23023
- `scripts\sw_surface_features.py` 行 1004 / 1009 / 1014 / 1015 / 1022 / 1023 / 1033 / 1103
- `mcp-server\` 下 **0 处**

**`InsertMidSurface`**（精确名）—— 命中 2 处：

- `scripts\sw_api_sldworks.py` 行 4410 / 21167

★ 补记：`grep` 字符串 `InsertMidSurface` 另会命中同前缀的**另一个成员名 `InsertMidSurfaceExt`**，
逐行为：`scripts\sw_api_sldworks.py` 行 5697 / 6314 / 22434 / 23051。
该行表「本仓现状」列只抄精确名 `InsertMidSurface` 的命中。