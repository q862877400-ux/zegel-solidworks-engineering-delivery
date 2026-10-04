# 100 路扫描：Bunny 一致指出我给的判据有系统性缺陷

> 来源：2026-10-04 用 `workflow` 扇出 **100 路**子代理（`provider=opencode-zen` / `model=space-bunny-free`），
> 每路读一个接口族的全部成员 `.md`，按我给的**三条判据**计数。
> **实际回 99 路、失败 1 路**（`ILocalLinearPatternFeatureData`）。
>
> 这份文件记的是**那 99 路的共同发现**：判据本身有洞，不是某一族的偶发。

## 一、我的三条判据（派活时给的原文）

1. **废弃**：只看页头（`**Signature**` **之前**）是否出现**行首** `Obsolete.`；
2. **指针接口**：`## Returns` 段是否含 `in-process, unmanaged C++`；
3. **零参可读**：签名形如 `X()`（括号内为空）**或该成员没有括号**，且非废弃、非指针。

## 二、99 路报出的四个洞（每条都带具体族与个数）

### 洞① 指针串**常常不在** `## Returns` 段

按判据 2 只看 `## Returns` ⇒ **系统性漏计**。报出这件事的族里，最极端的两例：

- `IMacroFeatureData`：全族 **17 个**文件带那个串，**17 个全在 `## Parameters` 段**的 out/ref 形参下，
  `## Returns` 段里**一个都没有** ⇒ 报 `pointer = 0`，而实质是 17 个指针接口。
- `ILoftFeatureData`：报 4 个在 `## Returns`、另有 **3 个**（`ISetFeatureScopeBodies` / `ISetGuideCurves`
  / `ISetProfiles`）**全文无 `## Returns` 段**，串落在 `## Parameters` 的嵌套条目里 ⇒ 按字面不计。
- `IModelDocExtension`：**9 个**在 `## Parameters` 而非 `## Returns`（`IPrintOut2`、`IPrintOut3`、
  `IGetSearchData`、`IGetOLEObjects`、`IListExternalFileReferences` 等）；
  即 `pointer=10` 而不是 19。
- 同类还有：`ISweepFeatureData`（2 个，且那两个文件根本没有 `## Returns` 段）、
  `IFace2`（3 个，改按全文命中则 16 → 19）、`ILinearPatternFeatureData`（4 个 `ISet*`，全文命中则 4 → 8）、
  `IComponent2`（2 个）、`ISldWorks`（2 个）、`IAnnotation`（1 个）、`IPartDoc`（1 个）。
- **`IView`（B1 那一路）**：`ISetBodies` 的 `ref Body2 BodyArray` 标记在 `## Parameters` 上 ⇒
  字面 45、全文 46。

⇒ **这不是个别现象**：在上限 100 族里，凡是 `ISet*` / `IGet*` 成对出现的族，几乎都会命中这个洞。

### 洞② 废弃标记有**变体**，严格「行首 `Obsolete.`」会漏计

- `INote`：**13 个**页头是行首 `Obsolete.`（带句点），另 **18 个**是
  `Obsolete for documents created in SOLIDWORKS 2016 and later.`（行首 `Obsolete` **但无紧跟句点**）
  ⇒ 严格判 `obsolete = 13`，合并语义则 **31**。
- `IModelView`：页头行首 `Obsolete.` 有 11 个；另 **4 个**写的是
  `Obsolete and not superseded. Functionality no longer implemented.` ⇒ 严格不计，
  而其中 `GetStereoSeparation` / `IGetStereoSeparation` **因此被算进了「零参可读」**
  （按语义判则 `obsolete` 应为 15、零参应为 43）。
- 各族的**宽松复核结果并不总是一致**：`IConfiguration`、`IAssemblyDoc`、`IBody2`、`ISketch` 等报
  「宽松搜索与严格结果完全一致，无差异」⇒ **这个洞只影响一部分族**，不能一刀切说全部漏计。

### 洞③ 「零参可读」把**属性**也算进去 ⇒ 虚增（且幅度极大）

判据 3 的第二个分句「**或该成员没有括号**」会把 `T Name {get;}` / `{get; set;}` 形态的属性全收进来：

- `IDSPBRMaterial`：**52 个成员 `zero_arg_read = 52`** —— 而它直说
  「kind 全部是 property、签名**全部**形如 `System.T Name {get; set;}`」
  ⇒ **这个数退化成等于 `members_total`，不代表有 52 个可调用的零参方法**。
- `IRayTraceRendererOptions`：`zero_arg_read = 35`，其中 **34 个是属性**，真方法只有 `UpdateGraphics` 一个
  ⇒ 它自己注明「若只认 `X()` 则 `zero_arg_read = 1`」。
- `IWizardHoleFeatureData2`：65 里只有 **5 个是真方法**，另 60 个是属性。
- `IAnnotation`：55 里 **18 个是属性**；`ISketch`：45 里 2 个是属性；`IGtol`：37 里 2 个是属性。

⇒ **同一个列名在两族里含义完全不同**（一族 52 个方法级的 0，一族 52 个属性）⇒ **不能跨族比较**。

### 洞④ 官方原文里有**笔误**，字面串匹配会漏

- `IDrawingDoc` 的 `IGetPenInfo`：`## Returns` 原文写的是 **`in-porcess, unmanaged C++`**
  （`process` 拼成 `porcess`）⇒ 按字面串判**不算指针**，
  于是它被算进了「零参可读」。该路自己注明：按纠正笔误口径则 `pointer` 应为 4、零参应为 78。
- 反向的也有：`IAnnotation` 报 `IGetAttachedEntityTypes` 与 `IGetLeaderPointsAtIndex` 的原文把
  `in-process` **重复写成** `in-process, in-process, unmanaged C++`（仍含目标子串，故仍计入）。

## 三、另外两类必须单列的页（不是判据的洞，是数据本身的形状）

- **空壳页**：整页只有 YAML frontmatter + 标题，**无 `**Signature**`、无 `## Returns`** ⇒ 三条判据全部判不出。
  报出它的族至少：`IView`（`RootDrawingComponent2`）· `IModelDoc2`（**7 个**：`CustomInfo`、`CustomInfo2`、
  `ILightSourcePropertyValues`、`LightSourcePropertyValues`、`LightSourceUserName`、`PrintSetup`、`SummaryInfo`）·
  `IModelDocExtension`（9 个 property 页）· `IDrawingDoc`（`Sheet`）· `IDisplayDimension`（`ChamferPrecision`）·
  `IComponent2`（`CustomPropertyManager`）· `IConfiguration`（`DimXpertManager`）· `IFeatureManager`（`FeatureName`）。
  ⇒ 这些页**计入 `members_total` 但不落任何一类**，所以「三类之和 ≠ 成员总数」是**应然**的。
- **大量成员没有 `## Returns` 段**：`IView`（166/220 有）· `IModelDoc2`（多数 `void` 成员）·
  `IDrawingDoc`（162 个）· `ISldWorks`（104 个）· `IMacroFeatureData`（38/84）· `IModelView`（…）⇒
  判据 2 在这些文件上**无从适用**，各族都按「无该字符串」记为非指针，并在 notes 里写明。

## 四、结论（怎么用这批数据）

1. **这一批的直接产出是「判据有洞」**，不是可用的缺口地图。
   `zero_arg_read` 这一列**两个方向都会错**：洞③ 让它**虚增**（属性算成方法），洞① 让它**虚增**
   （真正读不到的指针接口留在里面）。⇒ **不许拿它排优先级。**
2. **它证明了一件事：把判据交出去批量执行，能得到我自己读不出来的样本量。**
   洞①在 8 个以上的族里独立复现、洞③ 让一族整列退化 —— 这些靠我逐个读是发现不了的。
3. **重跑已按这四个洞把口径拆开**（`obsolete_strict` / `obsolete_loose` ·
   `pointer_returns` / `pointer_params_only` · `zero_arg_methods` / `properties_no_paren`），
   并改成**每路自写一个 json 文件**（上一批 175 KB 的结果挂在 job 返回通道上，**被截断在 60 KB 丢了**）。

## 五、这个洞的修法（待定，不擅改已发布的数字）

- **指针**：改成**两段分别报**（`## Returns` 命中 / 仅别处命中），**不合并** —— 合并会立刻改变
  已发布的 `pointer` 数（45 → 46 等），那是主线的数字。
- **废弃**：同时报严格与宽松两个数，**由主线决定采用哪个**（`INote` 13 vs 31 差一倍多）。
- **零参**：拆成 `zero_arg_methods` 与 `properties_no_paren`，**永不合并** ——
  `IDSPBRMaterial` 的 52 = 52 属性就是合并的后果。
