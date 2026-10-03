# 任务 B · 核「30 份 audit-vs-official 里置信度为『高』的条目」

- **范围**：`D:/AI/SW/specs/202-user-coverage-gaps/recon/audit-vs-official/audit-*.md`（30 份）里「分歧表」中**置信度列 = 高**的行。置信度为「中 / 低」的一律不碰。
- **核两件事**：①「官方的原文」是否真的存在于官方文档（检索范围 `C:/swapi/types/**`、`C:/swapi/examples/**`；该族另引 CHM 解包目录 `D:/AI/SW/AI Solidworks/官方文档/SWhelp/**`、VB6 文档目录 `C:/cworks_vb6/`、出厂反射转储 `D:/AI/SW/_raw/**`，一并回原文核对）；②「我们的原文」是否真的在它点名的那份仓内文件里。
- **方法**：脚本逐行抽出 30 份文件里「置信度 = 高」的表格行（共 **93** 条），对每一格的每个反引号片段做**归一化子串比对**（去 `<br>` / `**` / 空白、省略号分段命中、HTML 标签剥离），再对**全部未命中项逐条人工回原文复核**——脚本初判的未命中里绝大多数是 markdown 转义、表格单元格折叠、CHM 标签残留造成的假阳性，已逐条排除并在下面写明。
- **纪律**：只读；未运行 SolidWorks；未跑 pytest；**未改动仓内任何文件**；本文件是本次唯一写入。查不到就写「查不到」。

---

## 一、总账

| 项 | 数 |
|---|---|
| 高置信条目总数（30 份文件） | **93** |
| **成立** | **89** |
| **不成立** | **3** |
| **存疑** | **1** |

**不成立的 3 条全部是同一类**：「我们的原文」引的那行代码**在当前工作树里已经不存在了** —— 仓内已按官方 `Obsolete. Superseded by` 的指向换成后继成员，并在注释里留了迁移记录。这 3 条报告的问题**本身已经不存在**，条目本身已过时。

---

## 二、逐条表

✔ = 回原文命中；✘ = 回原文**查不到**；△ = 命中但与原文有出入。

| # | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 | 备注 |
|---|---|---|---|---|---|
| 1 | `audit-01-surface-A.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-01-surface-A.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-01-surface-B.md` | ✔ | ✔ | 成立 | 官方例 `C:\swapi\examples\Create_Trimmed_Surface_Feature_Example_CSharp.md` 内 `SelectByID2("", "SURFACEBODY", …)` 的省略号是表格折叠，实文为 `0.0289416986472588, 0.00781827749557351, 0.0290635845400971` |
| 2 | `audit-01-surface-B.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-01-surface-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-01-surface-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-01-surface-C.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-01-surface-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-02-sheetmetal-A.md` | ✔ | ✔ | 成立 | 引用 `OneBendSpec.validate` 是「类名.方法名」路径式引用，非逐字代码；`class OneBendSpec:` 与 `def validate(self) -> None:` 都在 `scripts/sw_sheet_metal.py` |
| 2 | `audit-02-sheetmetal-A.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-02-sheetmetal-A.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-02-sheetmetal-B.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-02-sheetmetal-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-02-sheetmetal-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-02-sheetmetal-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-03-weldment-A.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-03-weldment-A.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-03-weldment-B.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-03-weldment-B.md` | ✔ | ✔ | 成立 | 条目把 CHM 例页写成 `C:/cworks_vb6/...`，实际命中的是 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\Insert_Weldment_Cut_List2_Example_VB.htm`，原文 `v = Part.GetBodies2(0, True)` 逐字命中 |
| 1 | `audit-03-weldment-C.md` | △ | ✔ | **存疑** | 引文一字之差，见 §三.1 |
| 2 | `audit-03-weldment-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-04-assembly-A.md` | ✔ | ✔ | 成立 | 条目称出厂反射 `## IMate2` 段「34 行」，实际 **35 行**（非空行）；「无 `Name`」由三源同证：`C:\swapi\index\members_by_type.md` 的 `IMate2` 段、`IMate2_members.html` 的 Public Properties 表（15 条）、`D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 的 `## IMate2` 段 |
| 1 | `audit-04-assembly-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 5 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 6 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 7 | `audit-04-assembly-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-05-drawing-A.md` | ✔ | ✔ | 成立 | 对照页 `C:\swapi\types\ISelectionMgr\GetSelectedObjectMark.md` 的 `System.int GetSelectedObjectMark( System.int AtIndex )` 逐字命中 |
| 1 | `audit-05-drawing-B.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-05-drawing-B.md` | ✔ | ✔ | 成立 | 本条是**否定式**结论：已回 `C:\swapi\types\ISheet\SetTemplateName.md` 确认该页 `## Remarks` 两句里**无** `ForceRebuild3` 字样 —— 与条目陈述一致 |
| 3 | `audit-05-drawing-B.md` | ✔ | ✔ | 成立 | 引用 `GetSelectedObjectCount2(-1)` 是简写；`scripts/sw_drawing_expose.py` 里实文为 `get_com_member(mgr, "GetSelectedObjectCount2", -1)` |
| 4 | `audit-05-drawing-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-05-drawing-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-05-drawing-C.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-05-drawing-C.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-05-drawing-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-06-features-A.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-06-features-B.md` | ✔ | ✔ | 成立 | 「我们的原文」格用 `**sw_part.py**` 加粗（不是反引号），脚本初判漏了文件名，按 `scripts/sw_part.py` 复核后全部命中 |
| 2 | `audit-06-features-B.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-06-features-B.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-06-features-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 5 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 6 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 7 | `audit-06-features-C.md` | ✔ | ✘ | **不成立** | 见 §三.2 |
| 8 | `audit-06-features-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | 官方例 `C:\swapi\examples\Sketch_Offset_Example_VB.md` 里 `SketchOffset2(0.00254, True, True, swSkOffsetCapEndType_e.swSkOffsetArcCaps, …)` 逐字命中 |
| 4 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | |
| 5 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | |
| 6 | `audit-07-sketch-A.md` | ✔ | ✔ | 成立 | `C:\swapi\types\IModelDoc2\SketchModifyFlip.md` 的 `## Parameters` 确实给了 `- X = 1` / `- Y = 2` |
| 1 | `audit-07-sketch-B.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-07-sketch-B.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-07-sketch-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-07-sketch-C.md` | ✔ | ✘ | **不成立** | 见 §三.3 |
| 2 | `audit-07-sketch-C.md` | ✔ | ✔ | 成立 | `scripts/sw_sketch_edit.py` 的 `def _seg_count():` 内先 `get_com_member(model, "GetActiveSketch2")`、下一行回退 `get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")`，逐字命中 |
| 3 | `audit-07-sketch-C.md` | ✔ | ✔ | 成立 | 引文里漏了代码里的反引号（原文是 `⚠ \`AxisFlag\` 的…`），其余逐字一致 |
| 4 | `audit-07-sketch-C.md` | ✔ | ✔ | 成立 | |
| 5 | `audit-07-sketch-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-08-mold-costing-A.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-08-mold-costing-B.md` | ✔ | ✔ | 成立 | `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` 的 Remarks 表里 `Direction of pull` / `Parting line edges` 两行逐字命中 |
| 3 | `audit-08-mold-costing-B.md` | ✔ | ✔ | 成立 | 引文把 `scripts/sw_mold.py` 模块 docstring 的两行（`# ⚠ **多个参数语义查不到**（CHM 无这些方法的独立说明页、\`C:\\swapi\` 未收录、` / `#   来源也未提供）⇒ 按铁律 5 **不猜**，逐个在 docstring 里标注「未查证」。`）折成一行并补了空格 |
| 1 | `audit-08-mold-costing-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-08-mold-costing-C.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-09-simulation-A.md` | ✔ | ✔ | 成立 | 条目写的 `C:/cworks_vb6/CosmosWorksLib~ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.htm` 这个**文件名不存在**；命中的实文在 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`（Next.js 载荷内），`Function GetLoadsAndRestraints( _`、`value = instance.GetLoadsAndRestraints(NIndex, ErrorCode)` 均逐字命中 |
| 2 | `audit-09-simulation-A.md` | ✔ | ✔ | 成立 | 同上路径名出入；`D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `CWEdgeWeldConnector GetEdgeWeldConnector(Int32, Int32&)` 逐字命中 |
| 3 | `audit-09-simulation-A.md` | ✔ | ✔ | 成立 | 条目写的 `C:/cworks_vb6/CosmosWorksLib~CWLoadsAndRestraints_members.htm` 扩展名不对（实为 `.html`）；该页确有 `EntityCount` 等属性行，且 `GetName` / `GetType` 在该页 **0 命中** —— 与条目陈述一致 |
| 1 | `audit-09-simulation-B.md` | ✔ | ✔ | 成立 | `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt` 逐字命中 |
| 2 | `audit-09-simulation-B.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-09-simulation-B.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-09-simulation-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-09-simulation-C.md` | ✔ | ✔ | 成立 | `…\cosworks\members_2021.html` 的 Next.js 载荷内逐字含 `Obsolete. Superseded by …ICWLoadsAndRestraintsManager::AddForce2` |
| 1 | `audit-10-misc-A.md` | ✔ | ✔ | 成立 | 反射段 `Object GetMassProperties(Double)` 逐字命中 |
| 1 | `audit-10-misc-B.md` | ✔ | ✔ | 成立 | `C:\swapi\types\IFeatureManager\InsertRefPlane.md` 的 `0 = First reference entity` / `1 = Second` / `2 = Third` 逐字命中 |
| 2 | `audit-10-misc-B.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-10-misc-B.md` | ✔ | ✔ | 成立 | |
| 1 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 2 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 3 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 4 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 5 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 6 | `audit-10-misc-C.md` | ✔ | ✘ | **不成立** | 见 §三.4 |
| 7 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 8 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 9 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |
| 10 | `audit-10-misc-C.md` | ✔ | ✔ | 成立 | |

---

## 三、对不上的地方（逐条给可搜索的原文位置）

### 3.1 `audit-03-weldment-C.md` #1 —— 官方原文**引错一个字**（存疑）

- **条目引的官方原文**：`C:\swapi\types\IFeature\GetErrorCode2.md` —— 「`- **IsWarning**: True if the error is a warning, false to not`」
- **该文件里的真文**：「`- **IsWarning**: True if the error is a warning, false if not`」
- **差在哪**：`false to not` 应为 `false if not`。
- **影响**：只影响这一行的引文准确性；条目主张的实质（`IFeature.GetErrorCode()` 带官方 `Obsolete. Superseded by [[IFeature::GetErrorCode2]].`、后继多一个 `out bool IsWarning`）**成立** —— `C:\swapi\types\IFeature\GetErrorCode.md` 首行与 `GetErrorCode2.md` 的 Signature 均逐字命中。
- **我们这边在不在**：`scripts/sw_weldment.py` 的 `get_com_member(feature, "GetErrorCode")` 在，✔。

### 3.2 `audit-06-features-C.md` #7 —— 我们的原文**已不存在**（不成立）

- **条目声称的原文**：`scripts/sw_part.py` 里有 `sk = get_com_member(model, "GetActiveSketch2")`（并称「我们实际调用」的 `IModelDoc2.GetActiveSketch2` 带官方 Obsolete 行）。
- **当前 `scripts/sw_part.py` 的真文**：`def _require_active_sketch(fn):` 里是
  `#: ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 \`get_com_member(model, "GetActiveSketch2")\`。`
  / `from sw_sketch import active_sketch as _active_sketch` / `sk = _active_sketch(model)`
  —— `GetActiveSketch2` 在该文件里只以**注释里的历史说明**出现，没有任何可执行调用。
- **官方那边在不在**：`C:\swapi\types\IModelDoc2\GetActiveSketch2.md` 首行 `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` ✔ 逐字命中。
- **结论**：条目报的问题**仓里已经修了**（`scripts/sw_sketch.py` 的 `def active_sketch(model):` docstring 逐字写着「走**后继入口** `ISketchManager.ActiveSketch`」）。条目本身**已过时**。

### 3.3 `audit-07-sketch-C.md` #1 —— 同一处迁移，条目已过时（不成立）

- **条目声称的原文**：`scripts/sw_sketch_modify_ops.py` 的 `_active_sketch_name()` 里是 `sk = get_com_member(model, "GetActiveSketch2")`，并断言「该函数只走这一条路，没有 `SketchManager.ActiveSketch` 回退」。
- **当前真文**：`def _active_sketch_name(model):` 内是
  `★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 \`get_com_member(model, "GetActiveSketch2")\`。`
  / `★ 官方 \`IModelDoc2/GetActiveSketch2.md\` 逐字：「**Obsolete. Superseded by [[SketchManager::ActiveSketch]].**」`
  —— 同一个文件里 `GetActiveSketch2` 只剩注释，无可执行调用。
- **官方那边在不在**：✔（同上）。
- **对比**：同域的 `audit-07-sketch-C.md` #2 说的是 `scripts/sw_sketch_edit.py` 的 `def _seg_count():`，那里**仍**是先 `GetActiveSketch2` 再回退 `ActiveSketch`，逐字命中 ⇒ #2 成立、#1 不成立。

### 3.4 `audit-10-misc-C.md` #6 —— 我们的原文**已不存在**（不成立）

- **条目声称的原文**：`scripts/sw_review.py` 的 `zoom_to_fit` 与 `clear_selection_for_preview` 里各有一次 `get_com_member(model, "GraphicsRedraw2")`。
- **当前真文**：`def _graphics_redraw(model) -> None:` 里是
  `view = get_com_member(model, "ActiveView")` / `get_com_member(view, "GraphicsRedraw", None)`；
  `def zoom_to_fit(model):` / `def clear_selection_for_preview(model):` 都只调 `_graphics_redraw(model)`。
  `GraphicsRedraw2` 在该文件里**只剩 docstring 里那行引官方的话**：`★ 官方 \`types/IModelDoc2/GraphicsRedraw2.md\` 逐字：「**Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].**」`
  —— 没有任何 `GraphicsRedraw2` 的调用。
- **官方那边在不在**：`C:\swapi\types\IModelDoc2\GraphicsRedraw2.md` 首行 ✔ 逐字命中。
- **结论**：与 §3.2 同型 —— 条目报的问题**已经修完**，条目已过时。

---

## 四、一条模式（不是建议，只是这批事实的形状）

**「不成立」的 3 条，指向的都是「我们调了官方标了 `Obsolete` 的成员」这一类分歧；而当前工作树里，这 3 处都已经换成了官方点名的后继入口，并在代码注释里留了迁移记录（含真机验证记录 `output/activesketch-successor-evidence.json`、`output/graphicsredraw-successor-evidence.json`）。**

也就是说：这批高置信条目在「官方原文在不在」这一半上**几乎全对（92/93，唯一出入是 §3.1 那个字的误引）**；对不上的是另一半 —— **「我们的原文」引的是修复前的快照**。

**查不到 / 未核的**：
- 置信度为「中 / 低」的行按要求**未核**（本次 30 份文件里另有 44 行非「高」，其中若干含 `中（仅一源…）` 一类）。
- `audit-04-assembly-A.md` #1 的「出厂类型库反射 `## IMate2` 段 34 行」这一**计数**未对上（实为 35 行）；该段首行 `Boolean ForceMisalignment()` 与末行 `Void SetUseMisalignedDeviationDocumentProperty(Boolean)` 均逐字命中，「无 `Name`」的结论另有 CHM 与 `C:\swapi` 两源同证，故不影响该条成立。
- `audit-09-simulation-A.md` #1/#2/#3 与 `audit-03-weldment-B.md` #2 里点的 CHM / VB6 **文件名有出入**（见表中备注），已用实际存在的同名页复核，引文本身逐字命中。