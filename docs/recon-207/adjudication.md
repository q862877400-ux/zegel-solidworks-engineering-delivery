# 规格 207 · V8 主裁判裁决

> **来源**：`output/bunny-records-deep/*.json`（bunny 逐条手写，含逐字官方签名与风险）
> **裁决人**：Lead（spec.md 的 D-4 定「采纳与否由 Lead 逐条裁」）
> **本轮依据的记录数**：**51 / 76**（另 25 条仍在跑）⇒ ★ **本文件是部分裁决**，收齐后补裁。

## 一 · 裁决总表（10 条「建议采纳」候选）

| # | op | 官方成员（逐字已核） | 我的裁决 | 强制约束（落实现时必须满足） |
|---|---|---|---|---|
| 235 | `rebuild_document` | `IModelDoc2::EditRebuild3` / `IModelDocExtension::ForceRebuildAll` / `IModelDoc2::ForceRebuild3` | **采纳** | ★ 与 236 **合并成一条工具**（三档 mode），不建两条。★★ `EditRebuild3` 是**方法**不是属性 —— 三家都当属性读（`_get(doc,'EditRebuild3')`），照抄会拿到 bound method，**拿它当判据会永远为真** |
| 236 | `rebuild_model` | 同上 | **采纳（并入 235）** | 同上 |
| 97 | `display_states` | `IConfiguration::GetDisplayStates` / `ApplyDisplayState` | **采纳** | ★ 读侧落 `sw_render_material.py`（那一族已摸过，事实 286 真机 PASS）。★★ 官方逐字提示「第一个名字是活动显示状态」**只在单配置、无引用显示状态时干净** ⇒ 输出**必须带 `ambiguous` 标记**，不许替调用方猜 |
| 244 | `referenced_documents` | `ISldWorks::GetDocumentDependencies2` + `GetDocumentDependenciesCount` | **采纳** | ★ 补齐 `solidworks_pack_and_go` 一直枚举却不暴露的**读侧**。★★ 官方逐字：**Library features 不会返回** ⇒ doc 必须写明这个盲区（不写就是静默的错答案） |
| 336 | `unfold` | `IModelDoc2::InsertSheetMetalUnfold`（零参 void） | **采纳** | ★ 官方**没给 mark** ⇒ 必须先真机定出"可建对象"，且前置判据用**回读 `GetSelectedObjectCount2(-1)`**（事实 8），不许信返回值 |
| 79 | `construction_geometry` | `ISketchManager::CreateConstructionGeometry`（零参 void） | **采纳** | ★ 零参 + 普通 dispinterface ⇒ 后端可达性最高。落 `sw_sketch_edit_ops.py`，**复用**该文件已有的声明式选段包装（`sketch_offset/fillet/trim/stretch` 同族） |
| 34 | `balloon` | `IDrawingDoc::AutoBalloon5` / `IModelDocExtension::InsertBOMBalloon2` | **采纳（须真机定案）** | ★★ 两家结论**互相矛盾**（Slacker-LLC 说静默无效、Eduardof0nt 直接调并回 `bool(result)`）⇒ **不许照抄任何一家**，必须真机定案。落 `sw_drawing_create_missing.py`（该文件已有 `_view_by_name`/`_iter_views` 等读侧助手，**别新造**） |
| 52 | `centerline` | `IDrawingDoc::InsertCenterLine2` | **采纳（须真机定案）** | 同上；★ bunny 建议与 idx 30 `auto_center_marks` **合并成一条工具的两种模式**，我同意 |
| 115 | `edges` | `IBody2::GetEdges` | **采纳（形态改为"扩充"）** | ★ 不新建平行工具 ⇒ **扩已有的 `solidworks_entities_on_body`**。★★ 但本条真风险**不是后端到不了**，而是"**读属性读不到**"（事实 3x：`ActiveView.Name/Type` 报 `unknown.X`）⇒ 先单独做一条**小验证**再落 |
| 273 | `setup_template_positions` | `ISheet::ReloadTemplate` / `SetTemplateName` / `SetProperties2` | **缓办** | ★ 域是「未分类」、且要 `ISheet::SetProperties2` 的**写入通道**；bunny 自评置信「中」而风险未定 ⇒ 不排活，等有具体用例再评 |

**小结：采纳 9 条（其中 2 条合并 ⇒ 实为 8 件活）· 缓办 1 条 · 不做 0 条。**

## 二 · 排活顺序（依据：后端可达性 → 是否需真机定前置 → 是否需新模块）

| 批 | 条目 | 为什么这个顺序 |
|---|---|---|
| **B1**（最干净） | 79 · 235+236 · 97 · 244 | 零参或普通 COM、无指针/无 `AccessSelections`（事实 47 无关）；落点都是**已有模块**；判据可写成特征树/返回值 + 回读 |
| **B2**（要真机定前置） | 336 · 34 · 52 | 官方**没给 mark** 或**两家结论矛盾** ⇒ 必须先真机定出可建形态，才能写 verified |
| **B3**（先小验证） | 115 | 「读属性读不到」是独立风险，先验再落 |

## 三 · 我对 bunny 结论的两处修正（不照单全收）

1. **#115 的形态**：bunny 提了 `solidworks_entities_on_body_extended`（新名字），我改成**扩已有工具** —— 本仓纪律是「已有落点就别新开」，且平行工具会让调用方分不清用哪个。
2. **#235/#236 的条数**：bunny 建议「合并成一条三档 mode」，★ 我同意并**强制执行** —— 两条工具做同一件事会在能力清单里留下两条永远同进同退的条目。

## 四 · 本文件不算什么（限度，必读）

1. **不是 76 条的完整裁决** —— 只裁了已落盘的 51 条里那 10 条「建议采纳」；剩 25 条与其余 41 条的「缓办/不做」待补。
2. **一条真机都没验** —— ★ 全程离线静态（D-3：几十个 bunny 并发抢单实例 COM 会死锁）。所有「后端可达」都是**静态推断**，必须在真机复验后才能标 `verified`。
3. **官方签名是逐字抄的，但"照签名写就能成"没被证明** —— 本仓已有先例：`FeatureFillet3` 盒子边成、放样体静默失败（事实 556）⇒ 每件活落地时必须配**负例**。

## 五 · 第二批裁决（dp1 片 26 条到齐后补）

**★ 新增 3 条采纳（都进了 B1/B3 批）**，且 dp1 给的"为什么值得做"比我自己推的硬：

| # | op | 官方成员 | 裁决 | dp1 点到的**关键判据**（我采纳） |
|---|---|---|---|---|
| 97 | `display_states` | `IConfiguration::GetDisplayStates` + `ApplyDisplayState` | **采纳（升级为 B1 首件）** | ★ 读侧**真机证据已在事实 286**（回 `["MCP_DS1","<默认>_显示状态 1"]`）⇒ 一次真机可拿全 L1–L4。★ 但官方写明"多个显示状态同时活动时要用 `IComponent2::ReferencedDisplayState`" ⇒ **零件成立、装配不成立** |
| 79 | `construction_geometry` | `ISketchManager::CreateConstructionGeometry`（零参） | **采纳** | ★★ 官方摘要**没说**"再调一次是切换还是置位" ⇒ ★ **必须先定这个，否则会做出"第二次调用把构造线变回实体"的工具**（静默的语义错） |
| 115 | `edges` | `IBody2::GetEdges` + `IEdge::GetLength` | **采纳（形态=扩充）** | ★★ **Euler 校验 V−E+F=2 今天就能跑、不需新 API**；且**一次实测可顺手定案 30/52/97 都悬着的单位口径** ⇒ 我先做这条 |

**★★ 一条要标成「危险项」而不是缺口**：

> `execute_workflow`（idx 123）—— 别家是**空壳 + 自标 simulated**，而它字面承诺的 "parallel execution" **正面撞上事实 24**（单实例 COM 并发会死锁）⇒ ★ **不许把它当普通缺口去补**；要么不做，要么明确重定义为"串行编排"。

**dp1 的两条"本仓自相矛盾"（我接单，待修）**：

1. `RunMacro2` 的**官方页有 `## Remarks`**，而 `capabilities.yaml` 里写着"是空的" ⇒ **我们的记录与官方源不符**，按铁律 4 应以官方源为准并更正清单。
2. `auto_center_marks`：工具在，但**批量路 `AutoInsertCenterMarks2` 从未单独真机验证**（单点 `InsertCenterMark3` 已实测阴性）⇒ 现在的 `verified` 标签覆盖不到那条路。

**dp1 片的方向与数字（与 ① 档相反）**：verdict 已有 9 / 其实没有 8 / **查不到 9**；recommendation 采纳 5 / 缓办 2 / **不做 19**；分类器 **错-把已有的判成缺口 6/26 = 23%** ⇒ ★★ **深调档的错法是"悲观"方向，与 ① 档的"单向乐观"正好相反** —— 这是"两个方向都会错"的第二个实测样本。

