# 官方源**自身的错**（★ 共享清单）

> ★ **为什么有这张表**：2026-10-04（接手轮）处置 `workflow-15` 的 **B-5** 时建的。
> 裁判逐字：「★ 建一条共享的「**官方源自身的错**」清单，★ 供两份摘要抄录时**对照**」✓
>
> ★★ **用途**：我们抄官方原文时，★ **遇到这几处不要"照抄"** —— ★ 因为**官方自己写错了**。
> ★★★ **判据**：本表每一条都**逐字给了官方原文**，★ 且**另一套官方源（或同源的后继页）给出了正确的写法** ⇒
> **可复核、不靠印象** ✓

---

## 一 · `ISheet.GetProperties` —— 说 **seven**、却列 **8** 个（★ 且末项**没有定义**）

| ★ | ★ 内容 |
|---|---|
| ★ **错的页** | `C:\swapi\types\ISheet\GetProperties.md` |
| ★★ **逐字** | 「The return value is the following array of **seven** doubles:」<br>`[ paperSize, templateIn, scale1, scale2, firstAngle, width, height, `**`sameCustomPrp`**` ]` |
| ★★★ **错在哪** | ① 说 **seven**、★ **列了 8 个**（★ 自相矛盾）；② 末项拼作 `sameCustomPrp`、★ 且**全页没有它的定义**（★ `paperSize` / `height` 等都有） |
| ★★★★ **正确写法在哪儿** | ★ 同源的**后继页** `C:\swapi\types\ISheet\GetProperties2.md` 逐字：「…array of **eight** doubles:」· 列 8 个 · ★ **名字是 `sameCustomProp`**（★ 不是 `Prp`）· ★ **并补上了定义**：「`*sameCustomProp* = Value is a boolean packed into a double and returns true if the **Same as sheet specified in Document Properties** in the Sheet Properties dialog is selected, false if not`」 |
| ★ **抄录时怎么办** | ★ **抄 `…2` 那一页**；★ 若要引 `GetProperties`，★ **必须同时注明它这三处与 `…2` 不一致** ✓ |

---

## 二 · `IDrawingDoc` 及同族页里的 **8 个死链**（★ 链接目标页不存在）

★ 判据：★ 扫 `C:\swapi\types\IDrawingDoc\*.md` 里**全部** `[[接口::成员]]` 链接，
★ 逐个去 `types\<接口>\<成员>.md` 找 ⇒ ★ **找不到的就是死链** ✓

★★★ **而"找不到"有**四种**成因 —— 逐条实测后分列**（★ 不猜）：

| # | ★ 出现于 | ★ 链接写的 | ★★ 成因 | ★★★ 实测 |
|---|---|---|---|---|
| 1 | `Create1stAngleViews.md` | `IDrawingDoc::1stAngleViews2` | ★ **成员名错** | ★ 真名 **`IDrawingDoc::Create1stAngleViews2`**（★ 存在 ✓；★ `1stAngleViews2` 不是合法成员名 —— 以数字开头） |
| 2 | `CreateCustomSymbol.md` | `ISkethcManager::MakeSketchBlockFromFile` | ★ **接口名拼错** | ★ 真名 **`ISketchManager::MakeSketchBlockFromFile`**（★ 存在 ✓；★ `ISkethc` → `ISketch`） |
| 3 | `GetBlockDefinition.md` | `SketchManager::GetSketchBlockDefinitions` | ★ **接口名缺 `I`** | ★ 真名 **`ISketchManager::GetSketchBlockDefinitions`**（★ 存在 ✓） |
| 4 | `ActivateSheet.md` | `IDrawing::IGetCurrentSheet` | ★ **接口名缺 `Doc`** | ★ 真名 **`IDrawingDoc::IGetCurrentSheet`**（★ 存在 ✓） |
| 5 | `ForceRebuild.md` | `IModel2::ForceRebuild3` | ★ **接口名错** | ★ 真名 **`IModelDoc2::ForceRebuild3`**（★ 存在 ✓） |
| 6 | `ActivateSheet.md` | `IDrawingView::ActivateView` | ★★ **成员在**别的接口**** | ★ 实测：`ActivateView` 在 **`IDrawingDoc`** 或 **`IFeatMgrView`** 上（★ **`IDrawingView` 上确实没有**） |
| 7 | `CreateBlockDefinition.md` | `ISketchManager::MakeSketchBlockSelected` | ★★★ **成员名全仓查不到** | ★ 扫**全部 566 个接口** ⇒ ★ **`MakeSketchBlockSelected` 一个都没有** |
| 8 | `SetupSheet6.md` | `IDrawingDoc::SetSelectedSheets` | ★★★ **成员名全仓查不到** | ★ 同上 ⇒ ★ **`SetSelectedSheets` 一个都没有** |

★★★ **实测口径**：★ **唯一死链目标 8 个**（★ 裁判汇总里记的是「5 处」—— ★ 那是**它抽查时点到的条数**；
★★ **本表给的是"扫全部后的唯一目标数"**，★ 两者**不矛盾、口径不同**）✓

★★★★ **这条自校抓出了我自己的错**：★ 我第一版给 #6/#7/#8 都写了"接口名错了"，
★ 而**自校**（`tools/selfcheck_official_source_errors.py`）逐个去官方核那些"真名" ⇒
★★ **3 条"真名"官方也没有** ⇒ ★★★ **我把一种错换成了另一种** ✓
⇒ ★ **修法**：★ 加一栏「**成因**」，★ 并按**实测**分四类（★ 见下）✓

★ **抄录时怎么办**：★ **凡本表列出的链接，不要照抄**；★ 按「实测」一栏改成真名；
★★ 而 #6/#7/#8 那三条**改不出来**（★ 成员要么在别处、要么全仓没有）⇒
★★★ **只能引那一页自己的正文**（★ 正文往往是对的，★ 错的只是那个 see-also 链接）✓

---

## 三 · `swLoftedBendFacetOptions_e` —— 只有 **4** 个成员

| ★ | ★ 内容 |
|---|---|
| ★ **页** | `C:\swapi\enums\swLoftedBendFacetOptions_e.md` |
| ★★ **实测成员** | ★ **正好 4 个**：`swChordTolerance`(0) · `swBendsPerTransitionSegment`(1) · `swMaxSegmentLength`(2) · `swAngleBetweenSegments`(3) |
| ★★★ **为什么记它** | ★ 裁判逐字：「★ `swSegmentLength` / `swSegmentAngle` **两套官方源都没有**」⇒ ★ **所以这两个名字是"查不到"，不是"有但没写"**（★ 铁律 5）✓ |
| ★★ **抄录时怎么办** | ★ **不要**因为别处见过 `swSegmentLength` 就当它存在 ⇒ ★ **查不到就写查不到** ✓ |

---

## 四 · ★★ 可复用判据（★ 从这三条里提出来）

> ★★★★ **官方源也会写错，★ 而"错"有**四种可核的形态****：
> ① ★ **自相矛盾** —— ★ 说 seven、列八个（★ §一）
> ② ★ **名字错** —— ★ 接口名（`ISkethcManager` · `SketchManager` · `IDrawing` · `IModel2`）·
>   ★ 或成员名（`1stAngleViews2`）（★ §二 #1–#5）
> ③ ★★ **目标根本不存在** —— ★ `MakeSketchBlockSelected` · `SetSelectedSheets`
>   **扫全部 566 个接口都找不到**（★ §二 #7/#8）⇒ ★ **那不是"名字写错"，★ 是"抄了一个不存在的东西"**
> ④ ★★ **成员在**别的接口**上** —— ★ `ActivateView` 在 `IDrawingDoc` / `IFeatMgrView`（★ §二 #6）✓
>
> ★★ **配套纪律**：★ **凡抄官方原文，遇到这四种形态，★ 要记"不一致"，★ 不要单选一边**；
> ★★★ **且优先信"能自洽的那一页"**（★ 如 `…2` 既说 eight、★ 又列八个、★ 还给了定义）✓
>
> ★★★★★ **而这张表本身也要自校** —— ★ 我第一次写它时，给 #6/#7/#8 都猜了"接口名错了"，
> ★★ 自校（`tools/selfcheck_official_source_errors.py`）逐个去官方核那些"真名" ⇒
> ★★★ **3 条"真名"官方也没有** ⇒ ★ **我把一种错换成了另一种** ✓
> ⇒ ★★ **定则**：★★★ **"改正"这个动作必须可核 —— 否则"改正"与"改错"在文本上长得一模一样** ✓
