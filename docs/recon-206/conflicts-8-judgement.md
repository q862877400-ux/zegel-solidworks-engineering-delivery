# T4-1 第三步 · 判读结论：8 个「我们用到」的成员 / 10 条冲突

> ★ 本文是**判读结论**（人的判断 + 逐条证据），**不是**生成物 ⇒ 可手改；
> 材料来源见 [`conflicts-8-judge-materials.md`](conflicts-8-judge-materials.md)（生成物，别手改）。
> ★ 完成于 2026-10-04 接手轮。**材料文件里的模板行仍空** —— 结论**落在这里**，理由见 §四。

## 一 · ★★ 口径（★ 先写「不算什么」）

| 项 | 值 |
|---|---|
| 判读条目 | **10**（8 个成员；`FeatureLinearPattern4` / `InsertSewRefSurface` 各 2 条）|
| 三态 | **成立 / 不成立 / 查不到** —— ★ 不许用「大概是」|
| 「我们用的是哪一边」的判据 | ★ 读**我们那一行真代码**（`ast` 定位的真调用），**不是**读注释与文档串 |
| 官方侧 | ★ 逐字回查 `C:\swapi\types\**` 与 `C:\swapi\examples\**`（★ 不采信另一个对话的转述）|

★★ **本文「不算什么」**（三条，★ 都是本轮实测撞到的边界）：

1. ★ **「同一节里我们『用到了』」≠「产品代码里有真调用」** —— 8 个成员里 **2 个只出现在探针/散文**（`SetupSheet6`、`InsertWeldmentTrimFeature2`）。
   ⇒ ★★ 判「产品有没有这个风险」**必须分开数** ✓
2. ★ **「官方示例与 Remarks 打架」≠「我们错了」** —— 本轮 10 条里 **只有 2 条**真的指到我们的代码（`AutoDimension2` / `SetSystemValue3`）；
   其余 8 条是**官方自身两处不自洽**，我们**两边都没用**或**用的那一边有官方依据** ✓
3. ★ **「我们没照示例写」≠「我们错了」** —— 官方 `## Remarks` 是**契约**、示例是**一个调用序**；
   ★ 当两者打架时，**照 Remarks 写是合理选择**，但**必须记下"我们无法用示例交叉验证它"** ✓

---

## 二 · ★★ 判读表（10 行，全部填满）

| # | 成员 | 类 | ★ 我们用的是哪一边 | 结论 | 证据 |
|---|---|---|---|---|---|
| 1 | `AutoDimension2` | mark_diff | ★★ **Remarks 那一边**（★ 我们**有**打 mark）—— 见 §三.1 的**更正** | ★★ **冲突成立**，★ **但落点不是"没打 mark"**；★★ 我们的**真缺陷是**：退路 `Select4` **静默丢 mark** + 返回码**不译** | `scripts/sw_part.py:745-758` 用 `Select3(append, mark=2/4)`；退路 `Select4(append, callout)` **没有 mark 形参** ⇒ ★ 那条路上 mark 丢失 ⇒ 官方 `swAutodimStatusDatumNotSupplied = 11` |
| 2 | `FeatureCircularPattern4` | unit_diff | ★★ **Remarks 那一边**（★ 把第 2 参当**总角/弧度**）| ★★ **不成立**（★ 我们**没踩**这个冲突）| `scripts/sw_part.py:1441` 传 `angle_rad` + `equal_spacing`；MCP 面 `tool_specs_batch17.py:94` 声明 "**Total pattern angle in DEGREES**" ⇒ ★ 与 Remarks 逐字「total angle in radians **if EqualSpacing is true**」**一致** |
| 3 | `FeatureLinearPattern4` | unit_diff | ★★ **Remarks 那一边**（★ `Spacing*` 按**米**）| ★★ **不成立**（★ 已经修过）| 官方 Parameters 逐字「Spacing1: Spacing **in meters**」；我方 `linear_pattern` docstring 逐字记着「**修正**了一处差 1000 倍的错」并按米换算 ✓ |
| 4 | `FeatureLinearPattern4` | mark_diff | ★ 我们**两边都没用**该 mark | ★ **查不到**（★ 我们**没试过** `FromCentroid=False` 那条路）| 官方 Remarks 逐字「8388608 to mark a seed instance reference **when FromCentroid1 or FromCentroid2 is false**」；★ 我方 `linear_pattern` 传 `FromCentroid1/2 = False` ⇒ ★★ **按 Remarks 该补一个 mark=8388608 的种子参考，而我们没补** ⇒ ★ 记为**未验证的潜在前置**（★ 不据此改代码：★ 那条路**没跑过**，改了也无从判对错）|
| 5 | `InsertProtrusionBlend2` | mark_diff | ★ 我们**按轮廓选 mark=1**（★ Remarks 表） | ★★ **冲突在我们身上不成立** | 我方 `scripts/sw_loft.py:79-87`：进调用前**校验 mark=1 上 ≥ 2 个轮廓**；★ 官方示例那处 `4098` 用在**引导曲线**（我们**不用引导线**）⇒ ★ 触及不到 ✓ |
| 6 | `InsertSewRefSurface` | unit_diff ① | ★ **Remarks 那一边**（★ 容差按**毫米**收，边界换算成米）| ★★ **不成立** | 我方 `scripts/sw_surface_features.py:251` 逐字卡 `0.0001 <= tol <= 0.1`（★ 官方 Remarks 的上下限）+ `:263-264` 注释「★ 容差换算：毫米 ⇒ 米（★ 唯一的换算处）」✓ |
| 7 | `InsertSewRefSurface` | unit_diff ② | 同上（★ 我们**没有**照 `Fill_Holes` 示例传 `3.001639406912E-05`）| ★★ **不成立** | 同 #6；★ 示例那个裸值按米口径 = 0.03 mm、按 mm 口径低于下限 ⇒ ★ **官方示例是自相矛盾的那一边** ✓ |
| 8 | `InsertWeldmentTrimFeature2` | mark_diff | ★★ **查不到**（★ 我们**只在探针里**按位置选，**没有**显式打 mark 1/2）| ★ **冲突成立，但我们是"未实现"不是"写错"** | 我方真调用在 `tools/probe_t302_four_families_v2.py:190`（★ **探针**）；★ 官方 Remarks 逐字「**1 = Body or bodies to trim** · **2 = Trimming boundaries**」，★ 而官方示例**先选者打 2**（落 `v1=BodiesToTrim`）⇒ ★★ **示例与 Remarks 正好相反** ⇒ ★ **单源不可判**，★ 我**不据此改代码** |
| 9 | `SetSystemValue3` | unit_diff | ★★ **Remarks 那一边**（★ 按**文档单位**写，而非示例的"弧度"）| ★★ **不成立** —— ★★ 但**带一条新发现**（见 §三.2）| 我方 `scripts/sw_document_data.py:353,366` 用 `_document_length_unit_scale(model)`（毫米文档 ⇒ **1.0**，**不是**硬编码 1000）⇒ ★ 与真机读数一致；★ 官方示例那条 `4.72 radians` 是**角度**尺寸，★ 我们**没有**角度的处理路径 ⇒ ★ 见 §三.2 |
| 10 | `SetupSheet6` | unit_diff | ★ **不适用**（★ `ast` 判：**真调用 0 处**，只在散文里被提及）| ★ **N/A** | `docs/recon-206/conflicts-25-crosscheck.md` §5.2 逐字：`SetupSheet6`（文本命中 2 处，**真调用 0 处**）⇒ ★ **不为它改任何代码** ✓ |

---

## 三 · ★★ 两条真发现（★ 本轮的全部价值所在）

### 3.1 ★★★ 更正：上一轮对 `AutoDimension2` 的判读**说错了我们自己的代码**

上一轮（`conflicts-8-judge-materials.md` 模板第 1 行）写的是：

> 「★ **调用前没有「选基准边并打 `swAutodimMark*`」这一步**」

★★ **本轮逐行读 `scripts/sw_part.py` ⇒ 那句话与代码不符** ✓

```
★ 代码实际做了（:743-758）：
    model.ClearSelection2(True)
    for segment, mark in ((vertical, 2), (horizontal, 4)):
        segment.Select3(selected > 0, mark, _empty_callout())   # ★ 真的打了 2 / 4
        ↓ 只有 Select3 抛异常时才退到
        segment.Select4(selected > 0, _empty_callout())          # ★ 这条没有 mark 形参
```

⇒ ★★ **更正为**：我们**有**打 mark（**Remarks 那一边**），但**退路会静默丢 mark** ✓
★★ **教训（与本规格定则 ⑦ 同族）**：上一轮那句结论来自**读注释/材料**，★ 而**代码就在盘上** ——
   ★ **判「我们有没有做某一步」必须读那一行代码**，不能读围绕它的散文 ✓

★ **可操作的余量（★ 已定位、未改 —— 因为它是行为改动且要真机验）**：
- ★ 退路 `Select4` **丢 mark** ⇒ 那条路上官方 `swAutodimStatusDatumNotSupplied = 11` 可达；
  ★★ 而我们**不译**那个返回码 ⇒ **用户看到 `11` 也不知道是"基准没供上"**；
- ★★ 而 `swAutodimStatus_e`（19 个成员）**官方页就在盘上**（`C:\swapi\enums\swAutodimStatus_e.md`）⇒ ★ **有据可译** ✓

### 3.2 ★★★ 新发现（★ 不在那 25 条里）：`update_dimension_mm` 把**角度**尺寸当**长度**收

★ 触发：判 `SetSystemValue3` 时回到**官方示例**逐字 ——

```vbnet
' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72 radians)
errors = swDim.SetSystemValue3(4.72, swThisConfiguration, Nothing)
```

★ **示例把同一个入参当弧度用** ⇒ ★ 官方页「in meters」对**角度尺寸**不适用 ✓
★★ **而我们这一条路上没有"角度"这个概念**：

```
★ MCP 面（tool_specs_batch33.py:126）逐字：Param("value_mm", … "New value in MILLIMETRES.")
★ 实现（sw_document_data.py:366）逐字：float(value_mm) / _scale     ← ★ 一律按长度换算
```

⇒ ★★★ **把 `D3@LocalCirPattern1`（角度）这样的名字传进来时**：
  - 传 `270`（本意 270°）⇒ ★ 数值上**恰好**是对的（270° = 4.712 rad ≈ 4.72）—— ★ **纯属巧合**；
  - ★ 而那**不是**我们的换算给的：★ 我们做的是 `270 / 1.0`，★ 换算是**恒等的**；
  - ★★★ **一旦文档单位不是毫米**（`_scale` ≠ 1）⇒ ★ 同一个调用**立刻错**；
  - ★★ 且**口径也不对**：★ 工具说收**毫米**、★ 角度**没有毫米** ✓

★★ **可操作的修法（★ 一行就能判，官方枚举支持）**：

```
types/IDimension/GetType.md 逐字：Returns ⇒ swDimensionParamType_e
enums/swDimensionParamType_e.md 逐字：
    swDimensionParamTypeDoubleLinear  = 0
    swDimensionParamTypeDoubleAngular = 1     ← ★ 就是它
⇒ ★ 在 update_dimension_mm 里判 GetType()==1 ⇒ **显式拒绝并说明**（★ 别静默按长度写）
   ★★ 依据：本轮定则 ⑦ 的推论 —— ★ 「静默接受一个它理解不了的量」比「报错」更坏 ✓
```

★★ **本轮不改它**（★ 两条理由，★ 都按本规格的纪律）：
① ★ 这是**行为改动**（新增拒绝路径）⇒ ★ 要先有**真机证据**（★ 得先造一个角度尺寸）；
② ★ 按 D-5 / 铁律，★ 改 `scripts/` 里别人的实现**必须有证据** —— ★ 而本轮两次判读里
   ★ 我已经**没有**再犯「凭文本判断就动手」那个错（★ 见 §3.1）✓
⇒ ★ **它在 `conflicts-25` 那 25 条里查不到**（★ 那 25 条是 `unit_diff`/`mark_diff` 的机械抽取）
  ★★ ⇒ ★ 本文是**第一条**把它记下来的地方 ✓

---

## 四 · ★ 为什么结论写在这里，而不填进材料文件的模板行

★★ **材料文件 `conflicts-8-judge-materials.md` 是生成物**（★ 头两行逐字：「由 tools/t4_judge_materials.py 产出，**不要手改**」）✓
⇒ ★ 往它的模板行里填字，**下次重跑那个脚本就会被覆盖**（★ 与事实 531 那个"探针写坏真交付物"同族）✓
★★ **⇒ 定则（★ 本规格第 11 条）**：
```
★ 生成物里可以**留空模板**，但**结论要另立一份非生成物** ——
  ★ 否则"填了又被覆盖"会让结论**看起来存在而实际消失**（★ 比没填更坏）✓
```

---

## 五 · ★★ 下一步（★ 按价值）

| 优先 | 事 | 起手处 |
|---|---|---|
| ★★★ | ★ 给 `swAutodimStatus_e` **19 个码加译名**（★ 有官方页 ⇒ 有据可译）| `scripts/sw_part.py:805` 的返回体 |
| ★★★ | ★ 给 `update_dimension_mm` 加**角度拒绝**（`GetType()==1`）| `scripts/sw_document_data.py` + 一条真机证据 |
| ★★ | ★ 那 **258 个** `example_more_specific` 成员的逐条判（★ 本表只判了 8 个）| `docs/recon-206/more-specific-audit.md` |
| ★ | ★ 退路 `Select4` 丢 mark 的处置（★ 要么带上 mark 的等价路径、要么显式报"这条路不可用"）| `scripts/sw_part.py:754-758` |
