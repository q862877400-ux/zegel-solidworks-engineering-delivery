规格 211 · B8 收口（七）：★★★ 五项可做未做的**宿主核实** —— ★ 抓到两处"宿主写错"

一、★★★★ **覆盖表这次的读数（★ 与前面几项**完全不同**）**
★ 这 5 项（★ 焊接符号 · 成形工具 · 爆炸直线 · 零部件阵列 · SpeedPak）在覆盖表里的**备注栏全是空的** ✓
⇒ ★★★ **说明没有"试死/回退"记录** ✓ —— ★★ **它们是**干净的缺口**** ✓
  ★（★ 对比：★ 剪裁曲面有"真机全不成"· ★ 平板型式有"已回退注册"· ★ 边界曲面有"待查" ✓）

★★ **而★ 本批又抓到两处"宿主写错"** ✗ —— ★ 与「曲线驱动阵列」那次**同型** ✓（★ 事实 36 ✓）

二、★★★★★ **「爆炸直线」⇒ 宿主是 `ISketchManager`，★ 不是 `IAssemblyDoc`** ✗
· ★★★ 官方页：**`C:\swapi\types\ISketchManager\InsertExplodeLineSketch.md`** ✓
  ```
  Signature: System.bool InsertExplodeLineSketch()
  Returns:   True if the explode line sketch is inserted or closed, false if not
  Examples:  ★★ 六份（VB.NET×2 · VBA×2 · C#×2）
  ```
· ★★ **示例名本身就说清了用法**：★「Insert Explode Line Sketch and **Route Line**」·
  ★「…and **Jog Line**」⇒ ★★★ **它是"先插图、再画线"两步** ✓
· ★★★ **而 `IAssemblyDoc` 下**没有**它** ✗ —— ★ 那里只有 `CreateExplodedView` / `AutoExplode` /
  `ShowExploded2` / `ViewExplodeAssembly` ✓（★ **那些是"爆炸视图"** ✓）
⇒ ★★★★ **所以「爆炸视图」与「爆炸直线」确实是两件事** ✓ ——
  ★ 覆盖表也分两行（★ 爆炸视图 ✅ · ★ **爆炸直线 ❌** ✓）

三、★★★★ **「SpeedPak」⇒ 入口与前置都核明了** ✓
· ★★★ 官方页 **`IAssemblyDoc::CreateSpeedPak`**：
  ```
  Signature: System.bool CreateSpeedPak( System.int SpeedPakType )
  Parameters: 1 = Mated · 2 = Graphics
  Returns:    True if SpeedPak is created for the active configurations of the
              ★ selected subassemblies in this assembly, false if not
  Remarks:    If a selected subassembly already has SpeedPak, then calling this method
              again does not create another SpeedPak, …
  Examples:   ★★ 三份（C# · VB.NET · VBA）
  ```
· ★★★ **前置逐字**：「for the active configurations of the **selected subassemblies**」✗
  ⇒ ★★ **它要"选中的**子装配**"** ✓ —— ★ 而不是"顶层零件" ✓
· ★★ **已有示例** ⇒ ★ 调用序可读 ✓

四、★★ **其余三项的宿主核实（★ 只做了列表扫描）**
| 项 | 已知 | 待做 |
|---|---|---|
| ★ **焊接符号** | ★★ **真宿主是 `IModelDoc2`**（★ `InsertWeldSymbol3`/`2`/`IInsertWeldSymbol3` ✓）**与 `IDrawingDoc::InsertWeldSymbol`** ✗ —— ★ 台账原先写作 `IFeatureManager` ✗ | ★ 定哪个宿主（★ **"焊接符号"是**工程图**标注 ⇒ `IDrawingDoc` 更可能** ✓）|
| ★ **成形工具** | ★ 待扫（★ `CreateFormTool2` / `InsertFormToolFeature` 未核）| ★ 全扫 `*FormTool*` |
| ★ **零部件阵列** | ★ 台账判"可做"（★ `swFmLocal*Pattern` ✓）| ★ 核它要不要 `AccessSelections`（★ 那会落到**事实 47** ✗）|

五、★★ **本批的方法论（★ 第三次奏效）**
★★★ **"宿主写错"是本规格的高频错型** —— 已经三次：
| # | 项 | 我以为的宿主 | 真宿主 |
|---|---|---|---|
| ★ 1 | 曲线驱动阵列 | `IFeatureManager` ✗ | ★ `IModelDoc2` ✗（★ 且**已 Obsolete** ✓）|
| ★ 2 | 焊接符号 | `IFeatureManager` ✗ | ★ `IModelDoc2` / `IDrawingDoc` ✓ |
| ★ 3 | **爆炸直线** | `IAssemblyDoc` ✗ | ★★ **`ISketchManager`** ✓ |
⇒ ★★★ **定则**：★ **判"可做"之前，先用 `Get-ChildItem -Recurse -Filter '*<名字>*'` 全扫一遍** ✓ ——
  ★ 那**一次就能拿到真宿主** ✓（★ 而★ 我三次都是"先在错的接口下查、查不到才全扫"✗ ✓）
★★ **为什么这条特别值**：★ 事实 36 明写「**同名接口分属不同族、用错接口 = 对象对任何成员都没反应**」✗，
  ★ 而 **`check_member_names.py` 抓不到这一类** ✗ ⇒ ★ **它是本仓**已知的盲区**** ✓

六、★ 交付物
· ★ 本记录：★ 五项宿主核实（★ 两处纠错 + 两处入口核明 ✓）
· ★ 台账待更新（★ 下一轮把这三项的"待核"落成结论 ✓）

七、★ 下一轮
★ ① **核完剩下三项**（★ 焊接符号定宿主 · 成形工具全扫 · 零部件阵列核 `AccessSelections` ✓）
★ ② ★**若三项都定性完成** ⇒ ★★ **21 项就只剩 PDM 一项待实测** ✓
★ ③ 然后 **B8 的文档部分**（★ `tasks.md` / `goal-bar.md` / `HANDOFF.md` ✓）


---

## ★★★★ 补充（★ 同批全扫出的结果：三项的宿主都拿到了）

| 项 | 真入口（★ 全扫所得） | 备注 |
|---|---|---|
| ★★ **成形工具** | ★ **`IFeatureManager::CreateFormTool`** · **`CreateFormTool2`** · ★★ **`InsertFormToolFeature`** ✓ | ★ 另有 `ILibraryFormToolFeatureData`（★ **属性式** ✗ ⇒ **要核它要不要 `AccessSelections`** ✗）|
| ★★ **零部件阵列** | ★★ **`IFeatureManager::FeatureLocalCurveDrivenPattern`** ✓（★ `*LocalPattern*` **全扫为空** ✗） | ★★★ **见下** |
| ★ **焊接符号** | ★ `IModelDoc2::InsertWeldSymbol3`/`2` · ★ `IDrawingDoc::InsertWeldSymbol` ✓ | ★★ **宿主待定**：★ "焊接符号"是**工程图**标注 ⇒ ★ **`IDrawingDoc` 更可能** ✓ |

### ★★★★ **一个必须点出的观察：「零部件阵列」与「曲线驱动阵列」共用同一个入口** ✗

· ★ 覆盖表把它们**分在两域**：★「特征 / **曲线驱动阵列**」· ★「装配 / **零部件阵列**」✓
· ★★★ 而**官方入口是同一个**：★ **`IFeatureManager::FeatureLocalCurveDrivenPattern`** ✓
  ★（★ 我早先查「曲线驱动阵列」时拿到的也是它 —— ★ 另有 `FeatureCurvePattern`（★ 在 `IModelDoc2`、
  ★ **已 `Obsolete`** ✗）✓）
⇒ ★★★ **所以这两项**很可能是同一个 API 的两个语境**** ✓（★ 特征语境 vs 装配语境 ✓）
★★★ **本批**不替它们下结论**** ✗ —— ★ 因为：
  ★ ① **它们是否真是同一件事**要**读那份 `## Remarks`** 才能定 ✓
  ★ ② ★ 而我判「曲线驱动阵列 = 不做」的**依据是"现代入口要 `AccessSelections`"** ✗ ——
    ★★ **若这条链路成立，那「零部件阵列」也该跟着是"不做"** ✓ —— ★ **而★ 那要**同一份证据**** ✓
  ★ ③ ★★ **不许因为"名字像"就推广**（★ 硬约束：★ **全称断言必须带同等数量运行记录** ✓）
⇒ ★★ **下一步**：★ **读 `FeatureLocalCurveDrivenPattern` 的 `## Remarks`** ⇒
  ★ **一处证据同时定两项** ✓（★ 那是最省的 ✓）

### ★★ 方法论补记（★ 这一批的核心收获）

★★★ **"宿主写错"是本规格的高频错型 —— 已经四次** ✗：
| # | 项 | 我以为的宿主 | 真宿主 |
|---|---|---|---|
| ★ 1 | 曲线驱动阵列 | `IFeatureManager` ✗ | `IModelDoc2` ✗（**且已 `Obsolete`** ✓）|
| ★ 2 | 焊接符号 | `IFeatureManager` ✗ | `IModelDoc2` / `IDrawingDoc` ✓ |
| ★ 3 | 爆炸直线 | `IAssemblyDoc` ✗ | ★★ **`ISketchManager`** ✓ |
| ★ 4 | （★ 成形工具）| — | ★ `IFeatureManager` ✓（★ 这次**对了** ✓）|

⇒ ★★★ **定则**：★ **判"可做"之前，先用 `Get-ChildItem -Recurse -Filter '*<名字>*'` 全扫一遍** ✓
★★ **为什么这条特别值**：★ **事实 36** 明写「同名接口分属不同族、**用错接口 = 对象对任何成员都没反应**」✗，
  ★★ 而 **`scripts/check_member_names.py` 抓不到这一类** ✗（★ 它判"名字在**某个**接口里存在" ✓）
  ⇒ ★★★ **那是本仓**已知的盲区**** ✓ —— ★ 而**全扫一次就能绕过它** ✓
