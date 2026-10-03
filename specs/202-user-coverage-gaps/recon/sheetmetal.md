<!-- domain: 钣金 -->

> ★★★★★ **2026-10-04（接手轮）整表重写** —— 处置 `JUDGE-C_D_E.md` 的 🔴 **#11**（★ `C-sm-1 V-5`）：
> ★ 裁判逐字：「★ `recon/sheetmetal.md` 把**已实现且官方有入口**的斜接/闭合角记成「**官方没写**」
> ⇒ ★★ **会把后来人引到错误结论**」✓
> ★★ **而原表**五行**全是「官方没写」** —— ★ 我**实测复核后**发现那是**错的**：
>   · ★ `C:\swapi\types` 里**有**那一整套（★ 含 `I*FeatureData`）：★
>     `InsertSheetMetalMiterFlange` / `IMiterFlangeFeatureData` · ★
>     `InsertSheetMetalClosedCorner` / `IClosedCornerFeatureData` · ★
>     `GetJogParameters` 一族 · ★ `InsertFlattenSurface`/`ISurfaceFlattenFeatureData` ✓
>   · ★★ 而**本仓也已实现**：★ `scripts/sw_sheet_metal_weld_entry.py` 的
>     `insert_sheet_metal_miter_flange` / `insert_sheet_metal_closed_corner` ·
>     ★ `mcp-server/tool_specs_batch74.py` 挂成两个 MCP 工具 ✓
> ★★★ **⇒ 原表那五格是把"我们**当时**没查"写成了"**官方**没有"** ——
>   ★★ 那是**两种完全不同的结论**，★ 而它**看起来一样** ✓
>   （★ 与**轮 69–70 的事实 518** 同族：★ **「我这张表里没有」≠「它不存在」**）✓
> ★★★★ **∴ 本表按**实测**重填**；★ **查不到的写「查不到」、★ 不许再写「官方没写」** ✓

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 斜接法兰 | ★ `IFeatureManager.InsertSheetMetalMiterFlange` | ★ **查不到**（本机 `C:\swapi` 有页面、★ 但本轮未逐字抄签名 ⇒ **按铁律 5 不填**） | ★ 查不到 | ★★ **已实现**：`scripts/sw_sheet_metal_weld_entry.py::insert_sheet_metal_miter_flange` · ★ 挂成 `tool_specs_batch74` 的工具 | ★ `IMiterFlangeFeatureData`（★ 另有 `MiterGap` / `MiterMergeCondition` / `MiterTrimPlanePoint`） |
| 闭合角 | ★ `IFeatureManager.InsertSheetMetalClosedCorner` | ★ **查不到**（同上） | ★ 查不到 | ★★ **已实现**：`scripts/sw_sheet_metal_weld_entry.py::insert_sheet_metal_closed_corner` · ★ 挂成工具 | ★ `IClosedCornerFeatureData` |
| 转折 | ★ `GetJogParameters` / `IGetFirstMultiJogLeader` / `ConvertToMultiJog` | ★ **查不到**（同上） | ★ 查不到 | ★ **未查**（★ 本轮**没有**核本仓有没有 —— ★ **不许写成"无"**） | ★ 那一族**只有方法页、没看到 `I*FeatureData`** ⇒ ★ 待核 |
| 褶边 | ★ **查不到**（★ 按 `Hem` 扫到的都是 `*Scheme` 之类**无关页**） | ★ 查不到 | ★ 查不到 | ★ **未查**（★ 同上 —— ★ **不许写成"无"**） | ★ 待核 |
| 展开折叠 | ★ `InsertFlattenSurface` / `InsertFlattenSurface2` | ★ **查不到**（同上） | ★ 查不到 | ★ **已在别处用**：`scripts/sw_feature_entry_ops.py` / `sw_loft.py` 等含 `Flatten` | ★ `ISurfaceFlattenFeatureData` · ★ `FlattenAlongPath` / `FlattenToSingleFolder` |
| 平板型式导出DXF | ExportFlatPatternView | **Signature**: `System.bool ExportFlatPatternView( System.string FilePath, System.int Options )` | 无 | `scripts/sw_api_sldworks.py:7312` | — |

> ★★ **本表的三条填写纪律**（★ 本轮定）：
> ① ★ **「官方成员」** 只写**我实际在 `C:\swapi` 里看到过**的名字 —— ★ 签名没逐字抄就写「**查不到**」，
>    ★★ **不许用"看起来像的名字"顶上** ✓
> ② ★★ **「本仓现状」** 只写**我实际搜到**的模块名 —— ★ **没搜过的写「未查」**、
>    ★★ **绝不许写「无」** ✓（★ 原表的错就出在这儿）
> ③ ★★★ **「没有」与「没查」必须用不同的词** —— ★ 而**原表把两者都写成了「官方没写」** ✓
