# T-C 独立复核报告 · 工程图视图族 + 标注族（13 成员）

> 复核者：`rev-drawing`（reviewer 角色 · **只报告、不修代码**）
> 任务：`task-3`（依赖 `task-2`）
> 日期：2026-10-03
> 状态：**部分完成 —— 签名逐条比【尚未执行】**（被判对象还没落盘，见 §0）

---

## §0 ★★ 首要声明：实现未落盘 ⇒ 「拿官方原文逐条比」这一步**没做**

截至本报告落盘时，**被判的三个文件一个都不存在**：

| 被判文件 | 磁盘状态（2026-10-03 实查） |
|---|---|
| `scripts/sw_drawing_views.py` | **不存在**（task-3 原文指定的名字） |
| `scripts/sw_drawing_anno.py` | **不存在**（task-3 原文指定的名字） |
| `mcp-server/tool_specs_batch73.py` | **不存在**（`tool_specs_batch72.py` 是最后一个） |
| `scripts/sw_drawing_create.py` | **不存在**（Lead 2026-10-03 更正后的名字） |

实查命令（可复现）：

```
python -c "import pathlib as p;print([f.name for f in p.Path(r'D:\AI\SW\scripts').glob('sw_drawing*.py')])"
# -> ['sw_drawing.py', 'sw_drawing_query.py', 'sw_drawing_review.py', 'sw_drawing_view.py']
python -c "import pathlib as p;print([f.name for f in p.Path(r'D:\AI\SW\mcp-server').glob('tool_specs_batch7*.py')])"
# -> ['tool_specs_batch70.py', 'tool_specs_batch71.py', 'tool_specs_batch72.py']
```

⇒ ★★ **本报告不声称「已复核通过」**（铁律 5）。凡是实现落地后的逐条结论，本文**一律留空并标 `[待执行]`**。
★ 我**不做**两种偷懒：(a) 不假装比过；(b) 不拿「arity 表对得上」当「能力对」。

---

## §1 官方签名逐字抄录（13 条 · 三源之第一源）

来源：`C:\swapi\types\<接口>\<成员>.md` 的 `**Signature**:` 行，**逐字**（行号已核）。

| # | 成员 | 接口 | 官方签名原文（逐字） | 官方文件:行 |
|---|---|---|---|---|
| 1 | `CreateDrawViewFromModelView3` | `IDrawingDoc` | `View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )` | `C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView3.md:14` |
| 2 | `CreateSectionViewAt5` | `IDrawingDoc` | `View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )` | `...\IDrawingDoc\CreateSectionViewAt5.md:14` |
| 3 | `CreateDetailViewAt4` | `IDrawingDoc` | `System.object CreateDetailViewAt4( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline, System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )` | `...\IDrawingDoc\CreateDetailViewAt4.md:14` |
| 4 | `InsertBreak` | `IView` | `BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )` | `...\IView\InsertBreak.md:14` |
| 5 | `CreateAuxiliaryViewAt2` | `IDrawingDoc` | `System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )` | `...\IDrawingDoc\CreateAuxiliaryViewAt2.md:14` |
| 6 | `SetupSheet5` | `IDrawingDoc` | `System.bool SetupSheet5( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes )` | `...\IDrawingDoc\SetupSheet5.md:14` |
| 7 | `InsertSurfaceFinishSymbol3` | `IModelDocExtension` | `SFSymbol InsertSurfaceFinishSymbol3( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )` | `...\IModelDocExtension\InsertSurfaceFinishSymbol3.md:14` |
| 8 | `InsertDatumTag2` | `IModelDoc2` | `System.object InsertDatumTag2()` | `...\IModelDoc2\InsertDatumTag2.md:14` |
| 9 | `InsertNote` | `IModelDoc2` | `System.object InsertNote( System.string Text )` | `...\IModelDoc2\InsertNote.md:14` |
| 10 | `AutoBalloon5` | `IDrawingDoc` | `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )` | `...\IDrawingDoc\AutoBalloon5.md:14` |
| 11 | `InsertHoleTable2` | `IView` | `HoleTableAnnotation InsertHoleTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )` | `...\IView\InsertHoleTable2.md:14` |
| 12 | `InsertRevisionTable2` | `ISheet` | `RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )` | `...\ISheet\InsertRevisionTable2.md:14` |
| 13 | `InsertCenterMark3` | `IDrawingDoc` | `CenterMark InsertCenterMark3( System.int Style, System.bool Propagate, System.bool Slot )` | `...\IDrawingDoc\InsertCenterMark3.md:14` |

★ 参数名序列与 arity 的**机器可读**版本在 `recon/api-arity-drawing.md`（已入库 `f32b294`），
并**硬编码**进核对脚本 `recon/check_drawing_signatures.py` 的 `OFFICIAL` 表（防「表改了脚本没改」的静默漂移）。

---

## §2 ★ arity 表（成员 → 参数个数 → 参数名序列 → Obsolete/后继）

| 成员 | arity | 参数名序列 | Obsolete | 官方后继 | 后继 arity |
|---|---|---|---|---|---|
| `CreateDrawViewFromModelView3` | 5 | ModelName, ViewName, LocX, LocY, LocZ | 否 | — | — |
| `CreateSectionViewAt5` | 7 | X, Y, Z, SectionLabel, Options, ExcludedComponents, SectionDepth | 否 | — | — |
| `CreateDetailViewAt4` | 12 | X, Y, Z, Style, Scale1, Scale2, LabelIn, Showtype, FullOutline, JaggedOutline, NoOutline, ShapeIntensity | 否 | — | — |
| `InsertBreak` | 4 | Orientation, Position1, Position2, Style | **是** | `InsertBreak2` → `InsertBreak3` | 5 → **6** |
| `CreateAuxiliaryViewAt2` | 7 | X, Y, Z, NotAligned, Label, Showarrow, Flip | 否 | — | — |
| `SetupSheet5` | 11 | Name, PaperSize, TemplateIn, Scale1, Scale2, FirstAngle, TemplateName, Width, Height, PropertyViewName, RemoveModifiedNotes | **是** | `SetupSheet6` | **17** |
| `InsertSurfaceFinishSymbol3` | 14 | SymType, LeaderType, LocX, LocY, LocZ, LaySymbol, ArrowType, MachAllowance, OtherVals, ProdMethod, SampleLen, MaxRoughness, MinRoughness, RoughnessSpacing | 否 | — | — |
| `InsertDatumTag2` | **0** | （无） | 否 | — | — |
| `InsertNote` | 1 | Text | 否 | —（★ 官方**未**标 Obsolete） | — |
| `AutoBalloon5` | 1 | BalloonOptions | 否 | — | — |
| `InsertHoleTable2` | 6 | UseAnchorPoint, X, Y, AnchorType, StartValue, TableTemplate | **是** | `InsertHoleTable3` | **9** |
| `InsertRevisionTable2` | 7 | UseAnchorPoint, X, Y, AnchorType, TableTemplate, Shape, AutoUpdateZoomCells | 否 | — | — |
| `InsertCenterMark3` | 3 | Style, Propagate, Slot | 否 | — | — |

辅助入口（实现若走后继版，按这张表比）：

| 成员 | arity | 参数名序列 | 官方依据 |
|---|---|---|---|
| `InsertBreak2` | 5 | Orientation, Position1, Position2, Style, ShapeIntensity | `...\IView\InsertBreak2.md:14` |
| `InsertBreak3` | 6 | Orientation, Position1, Position2, Style, ShapeIntensity, **BreakSketchBlocks** | `...\IView\InsertBreak3.md:14` |
| `SetupSheet6` | 17 | …11 个同 SetupSheet5… , **ZoneLeftMargin, ZoneRightMargin, ZoneTopMargin, ZoneBottomMargin, ZoneRow, ZoneCol** | `...\IDrawingDoc\SetupSheet6.md:14` |
| `InsertHoleTable3` | 9 | UseAnchorPoint, X, Y, AnchorType, StartValue, Template, TagOrder, TagType, ManualTags | `...\IView\InsertHoleTable3.md:14` |
| `CreateAutoBalloonOptions` | 0 | （无） | `...\IDrawingDoc\CreateAutoBalloonOptions.md:14` |
| `InsertNewNote3` | 9 | UpperText, NoLeader, BentLeader, ArrowStyle, LeaderSide, Angle, BalloonStyle, BalloonFit, SmartArrow | `...\IModelDoc2\InsertNewNote3.md:14` |

---

## §3 机器核对脚本的用法与**本轮实测读数**

### 3.1 用法

```
python specs/202-user-coverage-gaps/recon/check_drawing_signatures.py \
    scripts/sw_drawing_create.py mcp-server/tool_specs_batch73.py
```

- 退出码：`0` = 无一不一致；`1` = 有 `MISMATCH` 或有文件不存在；`2` = 没给参数。
- 抽取三类调用形态（`ast` 为准，**注释与文档串不算**）：
  - `get_com_member(obj, "成员", a1, a2, …)` / `call_com_member` / `safe_get_com_member` ⇒ COM 实参 = `len(args) - 2`
  - `set_com_member(obj, "成员", value)` ⇒ COM 实参 = **0**（★ `scripts/sw_connect.py:581` 的第三参是**值**，不是 COM 实参）
  - `obj.成员(a1, a2, …)` ⇒ COM 实参 = `len(args)`
- 判定分级：`OK` / `MISMATCH`（少传·多传 ⇒ **必修**）/ `ZERO`（零实参 = 「取或调」语义，事实 84/144，**单列不判错**但 **不算建出来**）。

### 3.2 实测读数（本轮，两跑）

**跑 1 —— 控制组（★ 为证明脚本「真能抓到东西」，拿**既有**实现跑）**

```
python specs/202-user-coverage-gaps/recon/check_drawing_signatures.py \
    subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py
```

```
=== ...\drawing_workflow.py：共 69 个调用点，其中 6 个在这 13 成员/后继表内
  [OK      ] drawing_workflow.py:811   CreateDrawViewFromModelView3（COM 实参 5 / 官方 5）形态=attribute
  [OK      ] drawing_workflow.py:988   CreateDrawViewFromModelView3（COM 实参 5 / 官方 5）形态=attribute
  [OK      ] drawing_workflow.py:998   CreateSectionViewAt5（COM 实参 7 / 官方 7）形态=attribute
  [OK      ] drawing_workflow.py:1061  CreateDetailViewAt4（COM 实参 12 / 官方 12）形态=attribute
  [OK      ] drawing_workflow.py:1476  SetupSheet6（COM 实参 17 / 官方 17）形态=helper
  [OK      ] drawing_workflow.py:2053  SetupSheet6（COM 实参 17 / 官方 17）形态=helper
  ★ 按官方 arity 真调用到的：4 / 13
  ★ 未按官方 arity 调用到的：InsertBreak, CreateAuxiliaryViewAt2, SetupSheet5, InsertSurfaceFinishSymbol3, InsertDatumTag2, InsertNote, AutoBalloon5, InsertHoleTable2, InsertRevisionTable2, InsertCenterMark3
结论：★ 本表内无 arity 不一致
```
⇒ ★ **读法（重要，别误读）**：这**不是**「13 已复核通过」。它只说：**既有**那段代码碰到的 6 个调用点里，**没有一个 arity 不一致**；而**13 个里还有 10 个根本没被按签名调过**。
★ 这 6 个点全在 `subskills/` 里 —— `scripts/` / `mcp-server/` 里 **一个都没有**（见 §4）。

**跑 2 —— 被判对象（本轮）**

```
python specs/202-user-coverage-gaps/recon/check_drawing_signatures.py scripts/sw_drawing_views.py scripts/sw_drawing_anno.py
```

```
[MISS] D:\AI\SW\scripts\sw_drawing_views.py 不存在（★ 实现未落盘）
[MISS] D:\AI\SW\scripts\sw_drawing_anno.py 不存在（★ 实现未落盘）
结论：★ 有 MISMATCH/MISS，见上
```

退出码 `1`。⇒ **这就是「逐条比尚未执行」的机器证据**。

---

## §4 前置事实核查（已执行 · 与 T-B 的实现直接相关）

### 4.1 ★★ 缺口 ≠ 从零：工程图实现**本来就有**，只是不在覆盖率脚本的扫描范围内

| 事实 | 证据 |
|---|---|
| `CreateDrawViewFromModelView3` / `CreateSectionViewAt5` / `CreateDetailViewAt4` / `InsertNote` / `SetupSheet6` 在 `subskills` 里**已有可用实现** | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py:811`、`:988`、`:998`、`:1061`、`:1253`、`:1476`、`:2053` |
| `scripts/sw_drawing.py` 是**桥接**：把上述实现整体 re-export 成 `scripts.sw_drawing.*` | `scripts/sw_drawing.py:12-29`（`importlib` 加载 + `globals()[_name] = …`） |
| ★ 而 `tools/audit_gap_implementations.py` **只扫 `scripts` 与 `mcp-server`** ⇒ 判不出桥接过去的实现 | `tools/audit_gap_implementations.py:96-105`（`for d in ("scripts", "mcp-server")`） |
| ★ 故审计对 **全部 13 个工程图项**报 `implemented: false` | `output/gap-implementation-audit.json`：`工程图/投影视图`…`工程图/中心符号线` 共 13 行全 `false` |

⇒ ★★ **建议（给 T-B，优先级高于「新写」）**：这批的**首选来源**应是 `subskills/.../drawing_workflow.py` 的**既有实现**（宪法 §I 缝合优先 / 事实 201 的「已做成待办」），
`scripts/sw_drawing_create.py` 应当**薄封装 + 复用**，而不是**第二份实现** —— 否则同一个官方成员会有**两个家**（本仓已为此吃过亏）。
★ 这一条**我不能替你判**：它涉及「新文件该不该存在」，属设计与架构，请你定；我只报事实与风险。

### 4.2 ★★ 真机证据现状：13 个成员**一个都没有**成体系的证据；且已有一条**否证**

| 项 | 结果 |
|---|---|
| `output/*evidence*.json` 里**是否含**这 13 个成员名 | ★ **不含**。全 `output/` 下命中成员名的只有 3 个**索引类**文件：`output/_seealso.json`、`output/_called.json`（官方索引转储）、`output/gap-implementation-audit.json`（审计表） |
| `output/datum-tag-selfcontained2-evidence.json` | ★★ **存在，而且是「否证」**：`setup_a3_sheet.ok = true`，而 `add_view.ok = **false**`、`returned = "None"`、`verdict = "partial"` ⇒ 即 `SetupSheet6` **能**，`CreateDrawViewFromModelView3`（**arity 5/5 完全正确**）**在这一轮回 `None`** |

⇒ ★★ **两条结论，请 T-B 与业主都收下**：
1. **铁律 2**：在**没有**新证据落盘之前，这 13 项**任何**「能 / verified / 已实现」的说法都是**越级声称**。
2. ★ **arity 对 ≠ 能建成**：`datum-tag-selfcontained2` 就是**同一个人**在**arity 全对**的情况下拿到 `None` 的实证。
   ⇒ 静态比对是**前置筛查**，不是**通过判据**；把「arity 一致」说成「已验证」正是本仓栽过的那一类（事实 420/486）。

### 4.3 既有工程图测试已覆盖的 arity（T-B 不要造重复轮子，也不要覆盖成不一致）

| 既有断言 | 位置 |
|---|---|
| `CreateDetailViewAt4` **必须 12 参**（7 参会直接失败） | `tests/test_drawing_signature_contract.py:152-162`（`DETAIL_VIEW_AT4_PARAMS` 在 `:137`） |
| `InsertBomTable4` 必须经 `model.Extension` 且 **9 参** | `tests/test_drawing_signature_contract.py:202-219`（`INSERT_BOM_TABLE4_PARAMS` 在 `:144`） |
| `IModelViewManager` 剖视 4 成员 arity（`CreateSectionViewData` 0 · `CreateSectionView` 1 · `GetSectionViewData` 1 · `RemoveSectionView` 0） | `tests/test_drawing_signature_contract.py:445-463` |
| `scripts/sw_drawing_view.py` 内**自带** `IView` arity 表，且**已用后继版**（`'InsertBreak3': 6`、`'InsertHoleTable3': 9`、`'SetName2': 1`、`'GetName2': 0`） | `scripts/sw_drawing_view.py:273`、`:275`、`:304`、`:211` |
| ★ 而该表**不含** `InsertBreak`(4) / `InsertBreak2`(5) / `InsertHoleTable2`(6) / `SetupSheet5`(11) | 同表全文（`scripts/sw_drawing_view.py` 约 `:100-313`） |

★ **风险**：本仓将出现**两张** `IView` arity 表（`sw_drawing_view.py` 内嵌一张 + 我的 `check_drawing_signatures.py` 一张 + `recon/api-arity-drawing.md` 一张）。
⇒ 建议 T-B 的做法是**引用**其中一张，而不是**再写第四张**；否则「一个事实多个家」。

---

## §5 待复核清单（★ 实现落盘后，逐条跑；每条都给出「怎么查」）

> 格式：`编号 | 判据 | 命令/文件位置 | 现在状态`

| # | 判据（可机器核） | 怎么查 | 现在状态 |
|---|---|---|---|
| P1 | 13 个成员的 **COM 实参个数与顺序**与 §1/§2 一致 | `python specs/202-user-coverage-gaps/recon/check_drawing_signatures.py scripts/sw_drawing_create.py mcp-server/tool_specs_batch73.py` ⇒ 期望**无 MISMATCH** | **[待执行]** 文件不存在 |
| P2 | 三个 Obsolete 成员**没有被当作主入口**（`InsertBreak` / `SetupSheet5` / `InsertHoleTable2`） | `grep -n 'InsertBreak\b\|SetupSheet5\|InsertHoleTable2' scripts/sw_drawing_create.py` ⇒ 只应出现在**注释/来源块/对照表**里，**不应出现为调用目标** | **[待执行]** |
| P3 | 用的若是后继版，arity 是 **6 / 17 / 9** | 同 P1（脚本已把三个后继收进 `SUCCESSORS`） | **[待执行]** |
| P4 | ★ `InsertDatumTag2` 是**零参**、且工具有说明「要先选中」 | 官方 `InsertDatumTag2.md`（零参、无 Remarks）；★ 既有探针 `tools/probe_drawing_datum_tag2.py:85` 证明**不选中时回 `None`** | **[待执行]** |
| P5 | ★ `CreateDetailViewAt4` 前置是**先建局部圆**（`CreateDetailCircle`），不是直接调 | 官方 `CreateDetailViewAt4.md` 的 Examples 是 `Create_Detail_Circle_and_Detail_View_*` | **[待执行]** |
| P6 | ★ `CreateSectionViewAt5` 前置是**先选中剖切线** | 官方 `CreateSectionViewAt5.md:29` 逐字「Before calling this method, select the section line or lines to use as a section line.」 | **[待执行]** |
| P7 | ★ `InsertHoleTable2/3` 的选择 **mark 是 1/2/4/8** | 官方 `InsertHoleTable2.md:40-59` 的 mark 表 | **[待执行]** |
| P8 | ★ `AutoBalloon5` 必须**先 `CreateAutoBalloonOptions()`** 造选项对象 | 官方 `AutoBalloon5.md:25-33` 的四步；`CreateAutoBalloonOptions.md:14` 零参 | **[待执行]** |
| P9 | ★ `InsertSurfaceFinishSymbol3` 的定位参数**只在有引线时才用** | 官方 `InsertSurfaceFinishSymbol3.md:36` 逐字「uses the location parameters … only if the surface finish symbol has a leader leaderType != swNO_LEADER」 | **[待执行]** |
| P10 | ★ `InsertRevisionTable2` 已存在修订表时**回 null**（不是抛错） | 官方 `InsertRevisionTable2.md:26` 逐字「[[Revision table]] or null if a revision table already exists」 | **[待执行]** |
| P11 | ★ `InsertNote` 无选中时**无引线、独立、落在原点** | 官方 `InsertNote.md:31-37` | **[待执行]** |
| P12 | ★ 结构：**一行 docstring** + 来源块在三引号**之外**（写进去会 `SyntaxError`） | `python -c "import ast;ast.parse(open(r'scripts/sw_drawing_create.py',encoding='utf-8').read())"` + 人工看前 40 行 | **[待执行]** |
| P13 | ★ ToolSpec 工具名含约定关键词（覆盖率脚本按子串命中） | 读 `mcp-server/tool_specs_batch73.py` 的 `name=` | **[待执行]** |
| P14 | ★★ **越级声称**：凡写「能 / verified」处，必须有 `output/*evidence*.json` 支撑 | `grep -n 'verified\|已建成\|能建成' scripts/sw_drawing_create.py mcp-server/tool_specs_batch73.py`；再核 `output/` 里**有没有**对应读数的证据 | **[待执行]**（★ 现状：**无任何**支撑该 13 成员的证据文件，见 §4.2） |
| P15 | ★ 不引入**第二份家**：新模块是否复用 `subskills/.../drawing_workflow.py` | 读新模块的 import / 来源块；核 `scripts/sw_drawing.py` 是否已被复用 | **[待执行]**（★ 风险已记在 §4.1） |

---

## §6 已发现的问题（★ 每条给「文件:行号 + 官方依据 + 建议改法」）

### 6.1 必修 —— 落在**已有文件**里的真问题（不属 T-B 的改动，但会让 T-B 照着抄错）

| 严重度 | 文件:行号 | 问题 | 官方依据 | 建议改法 |
|---|---|---|---|---|
| **必修** | `specs/202-user-coverage-gaps/recon/api/CreateDetailViewAt4.md:9` | 写「**官方没写**（该文件没有 `## Remarks` 段；全文段序为 `## Parameters` / `## Returns` / `## Examples` / `## See Also`）」—— ★ **事实相反**：官方该文件**有** `## Remarks`，且里面写着 `ShapeIntensity` 的**两个取值约束** | `C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md:28` 逐字：「Intensity of jagged outline; valid range is **1 (most) to 5 (least)** and only valid if **JaggedOutline is true and NoOutline is false**」 | 把 `9` 行改成逐字抄的 Remarks；★ 并在实现里把 `ShapeIntensity` 的取值域与「仅当 `JaggedOutline=True` 且 `NoOutline=False` 才有效」写成**参数文档 + 入参校验** |
| **必修** | `specs/202-user-coverage-gaps/recon/api/InsertBreak.md`（**缺一行**）· `.../api/SetupSheet5.md`（缺）· `.../api/InsertHoleTable2.md`（缺） | ★★ 13 份 `recon/api/*.md` **系统性地丢掉**了官方页**标题后的第一句**（即 `Obsolete. Superseded by …`）—— 而这 3 个成员**恰好都是废弃的** ⇒ 照这份侦察实现的人**会看不出该用后继版** | `C:\swapi\types\IView\InsertBreak.md:12`「Obsolete. Superseded by [[IView::InsertBreak2]].」· `...\IDrawingDoc\SetupSheet5.md:12`「Obsolete. Superseded by [[IDrawingDoc::SetupSheet6]].」· `...\IView\InsertHoleTable2.md:12`「Obsolete. Superseded by [[IView::InsertHoleTable3]].」 | 13 份各补一行 `- Obsolete: <逐字句 + 后继>`（**含「否」**也要写，才能区分「查过」与「漏抄」）；★ 并加一条**生成器断言**：`recon/api/*.md` 必须含 `Obsolete:` 行 |
| **必修** | `specs/202-user-coverage-gaps/recon/api/*.md` 的 `本仓现状:` 行（13 份全有） | 把 `scripts/sw_api_sldworks.py` 的命中当成「本仓现状」—— ★ 那是**生成的反射索引**（成员名→序号/arity），**不是实现**；`tools/audit_gap_implementations.py:34` 的 `EXCLUDE_PREFIX = ("sw_api_",)` 明确把它排除。**真实的「本仓现状」是 `implemented: false`**（`output/gap-implementation-audit.json` 13 行全 false） | `tools/audit_gap_implementations.py:33-34`、`:96-105`；`output/gap-implementation-audit.json:191-308` | `本仓现状:` 行改为**两段**：① 「实现：无（`audit_gap_implementations` 判 false）」；② 「反射索引：`sw_api_sldworks.py:NNNN`（**不是实现**）」 |
| **必修** | `scripts/sw_drawing_view.py:415` | `get_com_member(view, "Name")` —— ★ `IView::Name` 官方**已废弃**（后继 `GetName2` / `SetName2`）；同文件 `:211` 已经登记了 `'GetName2': 0`、`:304` 登记了 `'SetName2': 1`，却在 `:415` 用废弃属性 ⇒ **同一文件内自相矛盾** | `C:\swapi\types\IView\Name.md:12`「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].」；`:14` `System.string Name {get;}`；`...\IView\GetName2.md:14` `System.string GetName2()` | `:415` 改为 `str(get_com_member(view, "GetName2") or "")`；★ 并把 `'Name'` 从 `VIEW_PROPERTY_NAMES`（`:334`）移到**废弃名单注释**里 |

### 6.2 ★ 我独立发现的其它 Obsolete / 异常（超出你已确认的 3 条链）

| 严重度 | 位置 | 发现 | 官方依据 |
|---|---|---|---|
| **必修** | `C:\swapi\types\IView\InsertBreak2.md:12` | ★ **废弃链是 3 级、不是 2 级**：`InsertBreak` → `InsertBreak2` → **`InsertBreak3`**。★ 只修到 `InsertBreak2` **等于没修**（2 也是 Obsolete） | `...\IView\InsertBreak2.md:12`「Obsolete. Superseded by [[IView::InsertBreak3]].」；`:14` 5 参；`...\IView\InsertBreak3.md:14` 6 参（多 `BreakSketchBlocks`）并**未**标 Obsolete |
| **建议** | `scripts/sw_drawing_view.py` 全表（`:100-313`） | 该表**只为「非废弃」成员登记**（`InsertBreak3` / `InsertHoleTable3` / `GetBreakLineCount2` / `GetName2`…），**废弃版一个都没有** ⇒ 「表里查不到」**不能推出「官方没这个成员」**。★ 对 T-B 的实际影响：新模块若照此表校验，会把 `InsertBreak`/`SetupSheet5`/`InsertHoleTable2` 判成「不存在」 | 该表 vs `C:\swapi\types\IView\` 的成员目录（两者数量不等）；事实 5 的同族 |
| **建议** | `specs/202-user-coverage-gaps/recon/api/CreateDrawViewFromModelView3.md:2` | 官方路径写成**裸文本** `C:\swapi\...`（未用反引号/代码块）⇒ markdown 里 `\t` `\I` 不会被转义，**人读会被误导**（其它 12 份用了反引号） | 同目录 `SetupSheet5.md:2`、`InsertRevisionTable2.md:2` 是正确写法（有反引号） |
| **建议** | `specs/202-user-coverage-gaps/recon/api/InsertCenterMark3.md:1-10` | 该份**没有** `## Examples` 与 `## Remarks` 之间的空行/分隔一致性（`:6-9` 连续无空行）；且 `:3` 的 Signature 行嵌套了重复的反引号（`` `**Signature**: `…` ``）—— 机械解析会切错 | 对比 `.../api/InsertSurfaceFinishSymbol3.md:4`（单层反引号，可解析） |

### 6.3 ★ 前置事实（不是 T-B 的错，但会直接决定它能不能过）

| 严重度 | 位置 | 事实 | 依据 |
|---|---|---|---|
| **必修（信息）** | `output/datum-tag-selfcontained2-evidence.json:11-14` | ★★ `CreateDrawViewFromModelView3` **arity 5/5 完全正确**，而真机**回 `None`**（`add_view.ok = false`、`verdict = "partial"`）。⇒ **arity 对不能当通过判据** | 该文件 `steps.add_view`；`note` 里的下一步是「判据是 `GetDatumTagCount()` 真的 +1」 |
| **建议** | `tools/probe_drawing_datum_tag2.py:7` | 既有探针已确认：`InsertDatumTag2()` 回了 `None`、`GetDatumTagCount` 0→0 ⇒ ★ **它也要先选中东西**（与官方零参签名不矛盾：位置来自**选区**） | `C:\swapi\types\IModelDoc2\InsertDatumTag2.md:12`「Inserts a datum tag symbol at a selected location.」（**at a selected location**） |
| **建议** | `specs/202-user-coverage-gaps/recon/api/CreateDetailViewAt4.md:11-13` | Examples 文件名点出**前置**是「Create Detail **Circle** and Detail View」⇒ `CreateDetailViewAt4` **不能独立调**，得先有局部圆 | `C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md:34-36` |

---

## §7 我**确认无误**的（避免只报问题显得偏）

1. **§1 的 13 条签名逐字正确** —— 我逐条与 `C:\swapi\types\...` 的 `**Signature**:` 行（均为 `:14`）对过，**无一处出入**。
2. **§2 的 arity 全部正确** —— 5 / 7 / 12 / 4 / 7 / 11 / 14 / 0 / 1 / 1 / 6 / 7 / 3。
3. **3 条废弃链的阶段正确**：`InsertBreak→2→3`、`SetupSheet5→6`、`InsertHoleTable2→3`（★ 而我**多查了一级**：2 也废弃）。
4. **`InsertNote` 确实未被标 Obsolete**（`InsertNote.md` 全文无 `Obsolete`）—— 所以用它是对的，**不要**因为「有 `InsertNewNote3`」就以为 `InsertNote` 废弃。
5. **`InsertDatumTag2` 确实是零参**（`InsertDatumTag2.md:14` 的 `()`），既有探针调法（`get_com_member(doc, "InsertDatumTag2")`）与此一致。
6. **核对脚本的控制组有效** —— 跑既有 `drawing_workflow.py` 拿到 6 个 `OK` 行并正确报出「4/13 到齐」，证明它**真的在抽实参个数**，不是空跑。

---

## §8 我拿不准的（如实列出，不猜）

1. ★ **`scripts/sw_drawing_create.py` 这个名字**：task-3 原文写的是 `scripts/sw_drawing_views.py` / `sw_drawing_anno.py`，Lead 后来更正为 `sw_drawing_create.py`。两者**都不是**现有命名（现有是 `sw_drawing_view.py` 单数 + `sw_drawing_query.py` / `sw_drawing_review.py`）。⇒ ★ **我按 Lead 的说法查了 `sw_drawing_create.py`，也未出现**；若实现落在别的名字上，我的脚本要重跑。
2. ★ **新模块 vs `subskills` 既有实现的边界**（§4.1）：我只报「会成两个家」这个**风险**，判不了「该不该新写」—— 那需要设计判断（属 Lead）。
3. ★ **`CreateDetailCircle` 的官方入口**我没查（不在 13 成员内）——P5 只说到「需要先建局部圆」，具体该调哪个成员**得 T-B 自己核**。
4. ★ **`SetupSheet5` 的 `RemoveModifiedNotes` 语义**：官方只说「True to delete modified notes, false to not」，**没写**它删的是**哪些**（谁的 modified notes）。⇒ 若 T-B 要暴露这个参数，文档里**不要**替官方补语义。
5. ★ **`InsertSurfaceFinishSymbol3` 的后 6 个 `System.string` 参数**（`MachAllowance`/`OtherVals`/`ProdMethod`/`SampleLen`/`MaxRoughness`/`MinRoughness`/`RoughnessSpacing`）的**合法取值格式**官方没给（只说类型是 string）⇒ 若 T-B 要建符号，**得先用空串试**，并把这当**未验**报告。

---

## §9 本轮**未执行**的（明确列出，避免被读成已做）

- ❌ **签名逐条比**（P1/P3/P4…P15 全部）：被判三个文件**不存在**。
- ❌ **越级声称判定**（P14）：**没有可判的对象**。★ 但我已把**判据与现状**备好：截至目前 `output/` 里**没有任何**文件含这 13 个成员的真机读数 ⇒ 实现落盘后若写「verified / 已建成」，**即判越级**。
- ❌ **真机 / pytest**：按 task-3 的约束，**不跑**（单源运行时，串行由 Lead 亲自做 —— spec.md §Assumptions）。

---

## §10 参考（本报告用到的全部官方依据与既有证据）

| 类别 | 路径 |
|---|---|
| 官方签名（13） | `C:\swapi\types\{IDrawingDoc,IView,ISheet,IModelDoc2,IModelDocExtension}\<成员>.md` 的 `**Signature**:` 行（均 `:14`） |
| 官方废弃句 | `...\IView\InsertBreak.md:12` · `...\IView\InsertBreak2.md:12` · `...\IDrawingDoc\SetupSheet5.md:12` · `...\IView\InsertHoleTable2.md:12` · `...\IView\Name.md:12` |
| 官方 Remarks（本报告引用处） | `CreateDetailViewAt4.md:28` · `CreateSectionViewAt5.md:29` · `InsertSurfaceFinishSymbol3.md:36` · `InsertRevisionTable2.md:26` · `InsertNote.md:31-37` · `InsertHoleTable2.md:40-59` · `AutoBalloon5.md:25-33` |
| 本仓既有实现 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py:811,988,998,1061,1253,1476,2053` |
| 本仓桥接 | `scripts/sw_drawing.py:12-29` |
| 本仓 IView arity 表 | `scripts/sw_drawing_view.py:211,273,275,304,334,415` |
| 既有 arity 契约测试 | `tests/test_drawing_signature_contract.py:137,144,152,202,445` |
| 覆盖率审计（真实现判据） | `tools/audit_gap_implementations.py:33-34,96-105` · `output/gap-implementation-audit.json:191-308` |
| 既有真机证据（否证） | `output/datum-tag-selfcontained2-evidence.json:11-14,20-21` |
| 既有真机探针（前置） | `tools/probe_drawing_datum_tag.py:79` · `tools/probe_drawing_datum_tag2.py:7,85` · `tools/probe_datum_tag_selfcontained.py:74` · `tools/probe_datum_tag_selfcontained2.py:81` |
| 本报告的机器核对脚本 | `specs/202-user-coverage-gaps/recon/check_drawing_signatures.py` |
| 本报告的 arity 表 | `specs/202-user-coverage-gaps/recon/api-arity-drawing.md` |

> 报告结束。★ 一句话：**前提与官方依据已备齐、机器核对脚本已在控制组上验证有效；被判对象未落盘 ⇒ 逐条比未执行**。
