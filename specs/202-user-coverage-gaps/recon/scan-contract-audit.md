# T-A2 官方契约抄本对账报告（只查不改）

审计对象：`specs/202-user-coverage-gaps/recon/api/` 下 **30 份**官方契约抄本。
对账源：`C:\swapi\types\<接口>\<成员>.md`。
**30 份全部核对完毕**（不是抽样）。

| 项 | 值 |
|---|---|
| 抄本总数 | 30 |
| 实际核对 | **30** |
| 未核对 | 0 |
| 判定口径 | 见下 §2 |
| 可信 / 有缺 / 不可信 | **17 / 13 / 0** |

---

## 1. 结论摘要（一句话）

★ **两个批次泾渭分明**：**第一批 13 份（工程图族）100% 不达标**，**第二批 17 份 100% 达标**。
⇒ 任务书里的「已知风险」**部分成立、部分被高估**：

| 已知风险 | 核实结果 |
|---|---|
| 「第一批 13 份**系统性**丢掉 `Obsolete` 行」 | ⚠️ **被高估** —— 不是 13 份全丢，是 **13 份里 3 份丢了**（`InsertBreak` / `InsertHoleTable2` / `SetupSheet5`）。另 10 份的官方页**本来就没有** `Obsolete` 句，抄本不写是对的 |
| 「把 `sw_api_sldworks.py` 当成本仓实现」 | ✔ **完全成立，且是 13/13 全中**。这才是第一批的主缺陷 |
| Signature 抄错 | ❌ **不成立** —— 30 份签名**全部逐字正确**，含 13 份问题抄本 |
| Remarks 判定错 | ❌ **不成立** —— 30 份的「有 Remarks 就逐字抄、没有就说没有」**全部正确** |
| 编造内容 | ❌ **不成立** —— 17 份第二批所断言的每一个签名都能在其引用的官方页里逐字找到 |

---

## 2. 判定口径

| 判定 | 定义 |
|---|---|
| **可信** | 四项全过：① Signature 逐字一致 ② 官方有 `Obsolete` 则抄本有、官方无则不写 ③ Remarks「有则逐字、无则明说无」且与官方一致 ④ 「本仓现状」**不把反射索引当实现** |
| **有缺** | Signature / Remarks 均正确，但存在**实质性遗漏**（漏 `Obsolete` 行，或把反射索引列成现状而不加标注） |
| **不可信** | Signature 与官方不一致、Remarks 判定与官方相反、或凭空编造官方没有的内容 |

> 依据：`sw_api_sldworks.py` 是**生成的反射索引**，非实现 —— 该文件第 1 行 `r"""SolidWorks sldworks 官方接口全量索引。`，第 8–9 行逐字写着「**官方 API 的完整抄录** —— 523 个接口族、**8210 个成员**，逐个照抄自对官方 interop 程序集的**纯元数据反射**」。命中它**不等于**本仓有实现。

---

## 3. 逐份判定总表（30 份）

图例：Sig=Signature 逐字 · Obs=漏 `Obsolete` · Rmk=Remarks 判定 · 反射=把反射索引当实现

### 3.1 第一批 · 工程图族（13 份）

| # | 抄本文件 | 官方页（行数） | Sig | Obs | Rmk | 反射 | 判定 |
|---|---|---|---|---|---|---|---|
| 1 | `CreateSectionViewAt5.md` | `IDrawingDoc\CreateSectionViewAt5.md` (56) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 2 | `CreateAuxiliaryViewAt2.md` | `IDrawingDoc\CreateAuxiliaryViewAt2.md` (34) | ✔ | — 官方无 | ✔ 「无」正确 | ✘ | 有缺 |
| 3 | `CreateDetailViewAt4.md` | `IDrawingDoc\CreateDetailViewAt4.md` (48) | ✔ | — 官方无 | ✔ 「无」正确 | ✘ | 有缺 |
| 4 | `CreateDrawViewFromModelView3.md` | `IDrawingDoc\CreateDrawViewFromModelView3.md` (58) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 5 | `AutoBalloon5.md` | `IDrawingDoc\AutoBalloon5.md` (45) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 6 | **`SetupSheet5.md`** | `IDrawingDoc\SetupSheet5.md` (50) | ✔ | **✘ 漏** | ✔ 逐字 | ✘ | **有缺（重）** |
| 7 | **`InsertBreak.md`** | `IView\InsertBreak.md` (52) | ✔ | **✘ 漏** | ✔ 逐字 | ✘ | **有缺（重）** |
| 8 | `InsertCenterMark3.md` | `IDrawingDoc\InsertCenterMark3.md` (30) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 9 | **`InsertHoleTable2.md`** | `IView\InsertHoleTable2.md` (73) | ✔ | **✘ 漏** | ✔ 逐字 | ✘ | **有缺（重）** |
| 10 | `InsertNote.md` | `IModelDoc2\InsertNote.md` (53) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 11 | `InsertDatumTag2.md` | `IModelDoc2\InsertDatumTag2.md` (28) | ✔ | — 官方无 | ✔ 「无」正确 | ✘ | 有缺 |
| 12 | `InsertRevisionTable2.md` | `ISheet\InsertRevisionTable2.md` (40) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |
| 13 | `InsertSurfaceFinishSymbol3.md` | `IModelDocExtension\InsertSurfaceFinishSymbol3.md` (46) | ✔ | — 官方无 | ✔ 逐字 | ✘ | 有缺 |

**批次小计：可信 0 · 有缺 13（其中重 3）· 不可信 0**

### 3.2 第二批（17 份）

| # | 抄本文件 | 引用官方页数 | Sig | Obs | Rmk | 反射 | 判定 |
|---|---|---|---|---|---|---|---|
| 14 | `assembly_explode.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 15 | `feature_combine_intersect.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 16 | `feature_scale.md` | 3 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 17 | `feature_thicken.md` | 8 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 18 | `macro_run.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 19 | `sm_closed_corner.md` | 5 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 20 | `sm_flat_dxf.md` | 5 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 21 | `sm_hem.md` | 4 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 22 | `sm_jog.md` | 6 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 23 | `sm_miter_flange.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 24 | `sm_unfold.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 25 | `surface_midsurface.md` | 3 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 26 | `surface_trim.md` | 2 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 27 | `weld_end_cap.md` | 6 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 28 | `weld_gusset.md` | 8 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 29 | `weld_symbol.md` | 7 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |
| 30 | `weld_trim_extend.md` | 15 | ✔ | ✔ | ✔ | ✔ 已排除 | **可信** |

**批次小计：可信 17 · 有缺 0 · 不可信 0**

---

## 4. 缺什么 —— 逐条给官方那一行

### 4.1 漏掉的 `Obsolete` 句（3 份，**最严重**）

三份抄本都**只字未提** `Obsolete`，而官方页第 12 行都有。照抄本实现会直接写到废弃 API 上：

| 抄本 | 官方文件:行号 | 官方原文（逐字） |
|---|---|---|
| `SetupSheet5.md` | `C:\swapi\types\IDrawingDoc\SetupSheet5.md:12` | `Obsolete. Superseded by [[IDrawingDoc::SetupSheet6]].` |
| `InsertBreak.md` | `C:\swapi\types\IView\InsertBreak.md:12` | `Obsolete. Superseded by [[IView::InsertBreak2]].` |
| `InsertHoleTable2.md` | `C:\swapi\types\IView\InsertHoleTable2.md:12` | `Obsolete. Superseded by [[IView::InsertHoleTable3]].` |

★ 三份抄本**连一个 `Obsolete` 字样都没有**（已全文 grep 确认）。**没有任何挽救性说明**，属实质误导。

### 4.2 把生成的反射索引当成本仓实现（13/13，第一批主缺陷）

13 份第一批抄本的「本仓现状」段**清一色只列 `scripts/sw_api_sldworks.py:<行号>`**，且**没有任何一处**说明那是生成的反射索引。对照第二批的写法（正确示范）：

- `sm_closed_corner.md:205` —「该文件是 `scripts/sw_api_*.py` 系列的**生成的反射索引**，**不是实现** ⇒ 命中它**不算**「本仓有实现」（仅反射索引，不算实现）。」
- `feature_combine_intersect.md:160` — 引 `sw_api_sldworks.py` 首行 docstring 逐字作证。
- `weld_symbol.md:318-339` — 22 行逐条标注「**（仅反射索引，不算实现）**」，并在 `:345` 给出「除反射索引外调用实现 = 0 处」的结论。

⇒ **第一批 13 份的「本仓现状」不能直接采信**；要重抄须照第二批的写法加标注。

★ 唯一例外：`InsertBreak.md:5` 除反射索引外还列了 `D:\AI\SW\scripts\sw_drawing_view.py:273`（`'InsertBreak3': 6,`）—— 但那是**反射 arity 登记条目**（无调用节点），仍非真实现。

### 4.3 其它小瑕疵（不单独影响判定）

- `CreateDrawViewFromModelView3.md:18-20` —— Examples 只抄了显示名「Insert Model Annotations (C#)」，**丢了官方 L38-40 的目标文件名** `Insert_Model_Annotations_Example_CSharp.md`。另 12 份都带文件名。
- `InsertSurfaceFinishSymbol3.md:9-12` —— Remarks 被包在 ``` 代码块里且连 `## Remarks` 标题一起吞掉，渲染成一整块；内容本身与官方 L35-36 逐字一致。

---

## 5. 查不到的 / 拿不准的（按铁律 5 如实登记）

| # | 事项 | 状态 |
|---|---|---|
| 1 | 抄本里 3 个路径**不是字面文件**，本审计无法当作官方页打开 | `C:\swapi\types\**\CreateExplodedView*.md`（`assembly_explode.md`）· `C:\swapi\types\**\*WeldSymbol*.md`（`weld_symbol.md`）· `C:\swapi\types\*\*.md`（`weld_trim_extend.md:见引用处`）—— **均为通配搜索式**，非路径抄错 |
| 2 | `surface_trim.md:197` 的 `C:\swapi\types\IModelDoc2\{Pre,Post}TrimSurface.md` | 花括号简写；实测 `IModelDoc2\PreTrimSurface.md` 与 `PostTrimSurface.md` **两份都存在**。该行抄本是**转引本仓注释的说法**，并已自注「不是官方答案」⇒ 处理正确 |
| 3 | `surface_midsurface.md` 声称后继页 `IFeatureManager\IInsertMidSurface` **不存在** | **已独立复核：确实不存在**（全库 `*MidSurface*` 仅 3 份，均在 `IModelDoc2\`）。抄本 `:105-106` 写「官方没写」「未用相近名字顶替」—— **诚实，判定正确** |
| 4 | 第二批 17 份的 **Remarks 逐行全量 diff** | **未做**（见 §6）。只做了：所引官方页**全部存在**、所断言的**每个签名**都能在所引页面内逐字命中、**每处「无 Obsolete」断言**均与官方一致 |
| 5 | `feature_thicken.md:342` 关于 `IThickenFeatureData\IAccessSelections.md`「无 Obsolete」的断言 | **已单独复核：该页存在且确无 Obsolete** ⇒ 正确 |
| 6 | `sm_hem.md:127` 关于 `IHemFeatureData\` 下**没有** `IAccessSelections2.md` 的断言 | **已单独复核：该文件确实不存在** ⇒ 正确 |

---

## 6. 审计方法与自查边界

**做了什么**
1. 从 30 份抄本抽出各自声称的官方页 → 逐个 `Test-Path` → 全部命中。
2. 对 13 份第一批：把官方页全文（≤73 行）逐行读入，与抄本做
   - Signature 归一化后**逐字符比对**（剔除反引号与 `**Signature**:` 前缀后）；
   - 官方页 `Obsolete` 出现位置 vs 抄本是否提及；
   - `## Remarks` 存在性 + 正文逐行包含性检查；
   - `## Examples` 目标文件名包含性检查。
3. 对 17 份第二批：所引页面全量扫描（Signature 行号、`Obsolete`、`## Remarks`），
   并反向校验抄本断言的签名是否真实存在于所引页面（防编造）；
   逐条核对「无 Obsolete」类断言。

**没做什么（不得据此认为第二批已完全无瑕）**
- 第二批 17 份的 **Remarks 正文逐行 diff** 未做 —— 它们的版式是内嵌官方原文代码块，逐字性依赖抄写，本轮未做全量比对，只在抽样与结构层核对。
- **未核对**抄本里 `## Parameters` / `## Returns` 段（任务书四查未含此项）。
- 未跑 SolidWorks、未跑 pytest，未改动任何已有文件。

**自查纠错记录（本审计自身）**
- 首轮 Signature 比对把 13 份全判 `DIFF`，实为**我的正则**未剥掉反引号与 `**Signature**:` 残留所致；归一化后 **13/13 逐字一致**。
- 第二批首轮「签名不在所引页面内」告警若干条，实为**正则跨行捕获**把散文一起吞了；逐条回原文核对后确认 **0 例编造**。
- ⇒ 上述两处若未自查，会产出**假阳性**。已按铁律 5 记录，未掩。

---

## 7. 建议（不改，仅登记）

1. **3 份重抄本属优先**：`InsertBreak` / `InsertHoleTable2` / `SetupSheet5` —— 补官方 L12 的 `Obsolete` 句与后继名。
2. **13 份第一批的「本仓现状」段全部需按第二批口径重写** —— 加「（仅反射索引，不算实现）」标注，并在无真实现时明写「本仓无实现」。
3. 抄录模板**已经修好**（第二批即为证据）⇒ 只需对 13 份旧件按新模板重抄，不必再改模板。
4. 建议在 `recon/api/` 下加一道门禁：`sw_api_*.py` 命中必须带「仅反射索引」标注，否则拦截。

---

## 8. 统计

```
抄本总数        30
实际核对        30   （未核对 0）

可信           17
有缺           13   （其中漏 Obsolete 的重缺陷 3）
不可信          0
────────────────
合计           30 ✔

按批次：
  第一批（工程图 13 份）  可信  0 · 有缺 13 · 不可信 0
  第二批（其余   17 份）  可信 17 · 有缺  0 · 不可信 0
```

★ **零「不可信」**：没有任何一份抄本把签名抄错、把 Remarks 判反、或编造官方内容。
问题集中在**元信息层**（漏废弃标记 + 把反射索引当实现），不是**契约层**。

---

*只查不改审计。产出仅本文件；未触碰 `recon/api/` 下任何抄本，未运行 SolidWorks / pytest。*