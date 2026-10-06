# 规格 209 · 规格 207 的 18 条采纳候选落地（Union Adopt 18）

**版本**：v1（2026-10-06）
**授权**：`docs/HANDOFF.md` §二逐字 —— 「**下一件该干的活：实现那 18 条**」；★ 排活顺序由
`docs/recon-207/adjudication.md` §二 给定（**B1 → B2 → B3**）。
**起点**：规格 207 只做「核实」不做「实现」（该规格 §六 逐字记着「18 条采纳候选未实现 ⇒ **该起新规格**」）。

---

## 一 · 来源与口径（★ 先把数字对齐，再动手）

```
规格 207 的四步（已在规格 207 内收口，本规格**只承接它的输出**）：
  ① 349 条「四家外部项目有、我们可能没有」的缺口清单 → 分类器自述 273/349 = 78.2% 打成「已有等价物」
  ② 273 条**逐条实测** ⇒ 确认已有 208 · 其实没有 62 · 查不到 3
  ③ deep 档 **76 条逐条读完**（bunny 逐条手写，带逐字官方签名与风险）
  ④ Lead 逐条裁决（D-4）⇒ tools/list_adoptable.py 实测：
       ★ **bunny 建议**：采纳 18 · 缓办 11 · 不做 47（合计 76 ✓）
```

★★ **本规格以 Lead 的裁决为准，不以 bunny 的建议为准** —— 两处差异**逐条列明**（★ 不静默改数）：

| # | bunny 建议 | Lead 裁决 | 依据（`adjudication.md`） |
|---|---|---|---|
| 273 | 采纳 | ★ **缓办** | §一：「域是「未分类」、且要 `ISheet::SetProperties2` 的**写入通道**…风险未定 ⇒ 不排活」 |
| 236 | 单列一条 | ★ **并入 235** | §一：「与 236 **合并成一条工具**（三档 mode），**不建两条**」 |
| 145 | 单列一条 | ★ **并入 115** | §六/§九：「与 #115 的 `GetEdges` **是同一件活的两种 kind** ⇒ **一条工具**（FACE/EDGE/VERTEX），**不许开两条**」 |

⇒ ★★ **采纳 17 条 ⇒ 实为 15 件活**（两对合并）。

### 1.1 十五件活与分批（★ 顺序照裁决书 §二 + §九）

| 批 | idx | op | 官方成员（逐字已核） | 落点 |
|---|---|---|---|---|
| **B1**（最干净） | 235+236 | `rebuild` | `IModelDoc2::EditRebuild3` / `ForceRebuild3` / `IModelDocExtension::ForceRebuildAll` | `scripts/sw_session.py` |
| B1 | 79 | `construction_geometry` | `ISketchManager::CreateConstructionGeometry`（零参） | `scripts/sw_sketch_edit_ops.py` |
| B1 | 97 | `display_states` | `IConfiguration::GetDisplayStates` / `ApplyDisplayState` | `scripts/sw_render_material.py` |
| B1 | 244 | `referenced_documents` | `ISldWorks::GetDocumentDependencies2` | `scripts/sw_document_data.py` |
| B1 | 209 | `move_body` | `IFeatureManager::InsertMoveCopyBody2` | `scripts/sw_body_ops.py`（新） |
| **B2**（须真机定前置） | 336 | `unfold` | `IModelDoc2::InsertSheetMetalUnfold`（零参 void） | `scripts/sw_sheet_metal.py` |
| B2 | 34 | `balloon` | `IDrawingDoc::AutoBalloon5` / `IModelDocExtension::InsertBOMBalloon2` | `scripts/sw_drawing_create_missing.py` |
| B2 | 52 | `centerline` | `IDrawingDoc::InsertCenterLine2` | 同上 |
| B2 | 175 | `blank_sketch` | `IModelDoc2::BlankSketch` / `UnblankSketch` | `scripts/sw_sketch.py` |
| **B3**（先小验证） | 115+145 | `edges` + `faces` | `IBody2::GetEdges` / `GetFaces` / `GetVertices` | ★ **扩** `scripts/sw_selection_spec.py`，**不许开平行工具** |
| **B4** | 211 | `native_macro_recording` | `ISldWorks::RecordLine` + `RunCommand` + 事件 | `scripts/sw_macro.py`（新） |
| B4 | 173 | `hem` | `IFeatureManager::InsertSheetMetalHem2`（16 形参） | `scripts/sw_sheet_metal.py` |
| B4 | 181 | `intersect` | `IFeatureManager::PreIntersect2` → `PostIntersect` | `scripts/sw_boolean_ops.py`（新） |
| B4 | 155 | `fold` | `IModelDoc2::InsertSheetMetalFold` | `scripts/sw_sheet_metal.py` |
| B4 | 205 | `model_annotations` | `IDrawingDoc::InsertModelAnnotations4` | `scripts/sw_drawing.py` |

⚠ **批次口径的说明（★ 明写，不静默）**：裁决书 §二 只给了 **B1/B2/B3**；**B4 是本规格新编的** ——
它收纳裁决书 §六/§八/§九 新裁的那 6 条（211/173/181/155/175/205），★ 其中 **175 被我放进 B2**
（理由：它的真风险与 B2 同类 —— **官方没给任何回读判据**，必须先真机定；见下）。

---

## 二 · 功能需求（FR）

| # | 需求 | 依据 |
|---|---|---|
| **FR-001** | 每件活 MUST **先读官方页三样**（签名 + `## Remarks` + `## Examples`）再动手；MUST NOT 照抄任何一家的实现 | 铁律 4 · `official-docs-first.md` |
| **FR-002** | **别家的成员名只当「该做哪个操作」的路标**，实现 MUST 从官方重推 | 裁决书 §七：别家「凭印象写成员名」是**跨来源**的（5 处虚构名零命中） |
| **FR-003** | 每件活 MUST 配**真机证据**才能标 `verified`；★ **一条真机都没验之前一律 `stitched`** | 裁决书 §四.2 · 规格 202 FR-009 |
| **FR-004** | 实现 MUST 落在**已有模块**；★ 只有确无落点时才新建，且**不许新起顶层目录** | 铁律 3 · 裁决书 §三.1「已有落点就别新开」 |
| **FR-005** | 工具名 MUST `solidworks_<域>_<动作>`；长度 `_mm`、角度 `_deg`；★ **不收裸坐标** | `docs/union-conventions.md` 规则 1/2/3 |
| **FR-006** | ★★ **不许跨条复制映射表**（mark 表 / 枚举值）—— 实测本批三条 mark 表**互不相同** | 裁决书 §九「三条横向结论」① |
| **FR-007** | ★ **合并项 MUST 合并**：235+236 一条工具（三档 mode）· 115+145 一条工具（三种 kind） | 裁决书 §一/§三.2/§六 |
| **FR-008** | ★ 官方声明与真机读数不一致时 ⇒ **以读数为准并逐条记账**（★ 不改读数去迁就文档） | 铁律 4 的口径 + 本规格 SC-5 |

---

## 三 · 非目标（明确不做）

```
★ 不做「不做」档的 47 条（★ 其中 4 条是**分类器输入噪声**：217 参数字典键名 / 221 文档类型串…）
★ 不做「缓办」的 11 条（273 / 33 / 82 / 146 / 170 / 182 / 191 / 219 / 225 / 227 / 241 / 316）
★ ★★ **`execute_workflow`（idx 123）不许当普通缺口补** —— 它字面承诺的 "parallel execution"
     **正面撞上事实 24**（单实例 COM 并发会死锁）；要么不做，要么明确重定义为「串行编排」
★ 不改规格 207 的任何已发布数字（★ 那批数字是**那批判据**的产物，改要单开规格）
```

---

## 四 · 验收判据（SC）

| # | 判据 | 怎么验（可 grep / 可复跑） |
|---|---|---|
| **SC-1** | 15 件活逐条有**落点**与**裁决依据** | 本篇 §1.1 表 + `docs/recon-207/adjudication.md` 对得上 |
| **SC-2** | 每件活的新工具都**真正注册**（`register_capabilities.all_specs()` 里数得到） | `python -c "…all_specs()…"` 计数与批次表一致 |
| **SC-3** | 每批 MUST 过全部门禁 | `pwsh -File tools/round_chain.ps1 -Tests tests/<本批>.py` 全绿 |
| **SC-4** | ★ 每件活 MUST 有**真机证据文件**，且判据是**回读**（不是返回值） | `output/union-adopt-*.json` 逐条带 `ok`/回读数 |
| **SC-5** | ★★ **官方文档与真机读数不一致处 MUST 逐条记账**（含"照文档写会错在哪"） | 本篇 §五 表 + 该能力的 `limitations` |
| **SC-6** | 每条能力在 `capabilities.yaml` 里的 `level` 取自五级枚举；★ 无真机证据者**不得** `verified` | `scripts/check_union_conventions.py` 退出码 0 |

---

## 五 · ★★ 官方文档与真机读数不一致处（SC-5 的台账 · 逐条记账）

| # | 出处 | 官方怎么写 | 真机怎么读 | 照文档写会错在哪 |
|---|---|---|---|---|
| 1 | `IModelDoc2::EditRebuild3` | 官方是**方法** `EditRebuild3()` | ★ pywin32 迟到绑定下 **`getattr` 本身就把它调掉** ⇒ `get_doc_member` 读到的**已经是返回值**（`bool`）、**恒为真** | ★ 别家统一当作**属性**读（`_get(doc,'EditRebuild3')`）⇒ 拿它当判据**永远为真** ⇒ 工具"看起来总是成功" |
| 2 | `ISldWorks::GetDocumentDependencies2` 的 `AddReadOnlyInfo` | 官方例子：**非只读**的文档跟的是**空串** | ★ 本机 SW 2026 SP4.1 回的是字符串 **`"FALSE"`** | ★★ 按「**非空即只读**」写判据 ⇒ **把非只读的判成只读**（`bool("FALSE") == True`） |
| 3 | `ISketchManager::CreateConstructionGeometry` | 摘要逐字是 "**Sets** … **instead of**"（★ **没说**再调一次会怎样） | ★★ **实测：连调两次 = 置位（幂等），不是 toggle** | ★ 若按"toggle"设计 ⇒ 第二次调用会把构造线**变回实体**（静默的语义错） |
| 4 | `IConfiguration::GetDisplayStates` | 「The **first name** in the list is the active display state」 | ★ 零件上成立（`['<默认>_显示状态 1']`）；★ 官方自己加了条件「**If more than one display state is active**」 | ★ 在**装配**里把"第一个"当活动状态 ⇒ 静默错答案（★ 本仓输出带 `ambiguous`） |

---

## 六 · 本规格不算什么（限度，必读）

1. ★ **15 件活不是一批做完的** —— 进度看 `tasks.md` 的勾，不看我记得什么。
2. ★ **`verified` 只表示「有我们自己的运行证据」**，不表示「代码是我们写的」（A2 的两层 provenance）。
3. ★ B2/B3/B4 的「后端可达」在**真机验过之前**都只是静态推断（裁决书 §四.2 的原话）。
