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
| 5 | `IFeatureManager::InsertMoveCopyBody2` 的**长度参数** | ★ **官方页没写单位** | ★★ 真机：按**文档长度单位（mm）**解释 —— 传 `25.0` 把包围盒 x 从 `-30.0/30.0` 挪到 `-5.0/55.0`（**正好 25 mm**）；★ 而先按"米"换算传 `0.025` 只挪了 **0.025** | ★★ 套「COM 惯例 = 米」⇒ **静默的 1000× 错误**：工具回 `ok=True` 而只挪了千分之一（★ 而它**能过**"包围盒变了"那条判据！） |
| 6 | 同一成员的 `RotAngle*` | ★ **官方页没写单位，也没说哪根轴** | ★★ 真机：COM 侧是**弧度**（传 `30.0` 得到约 **81°** ⇒ `30 rad ≡ 278.87° ≡ −81.1°`）⇒ ★★ **同一个调用里长度是 mm、角度是 rad** —— 一个接口**混两种口径** | ★ 同理静默错（要 30° 得到 81° 的转动）· ★ "哪根轴"另见探针 `T5b` 的三格互证 |
| 7 | `IEdge` 的**长度** | ★ **`IEdge` 上根本没有「长度」这个成员**（官方成员表逐条列过：`GetCurve` / `GetCurveParams` / `GetStartVertex` / `GetEndVertex` … **没有 Length**） | ★ 我读 `IEdge.GetLength` ⇒ **12 条边全部抛异常** | ★ 铁律 5 的正面用法：**名字缺席 = 官方没有** ⇒ ★ 长度只能由 `GetStartVertex` / `GetEndVertex` → `IVertex::GetPoint()` **自己算** |
| 8 | `ISelectionMgr::SetSelectedObjectMark` 的**第 3 参** | 官方签名是 `(AtIndex, Mark, Action)`，`Action` 取 `swSelectionMarkAction_e`（★ 官方两份示例都用 `swSelectionMarkSet`） | ★ 传 **`-1`** ⇒ 返回 **`false`**、**不报错**、**mark 没设上** ⇒ ★★ 我据此得出过「unfold 建不出来」的**错误结论** | ★★ 静默失效：★ **唯一能发现它的办法是"回读 mark"**（`GetSelectedObjectMark`），**不是看返回值** |
| 9 | 钣金 FeatureData 的**长度参数** | ★ **官方页没写单位** | ★★ 真机用**厚度棱的长度**量：传 `0.002` ⇒ 边长集合 `{0.002, 40, 60}`；传 `2.0` ⇒ `{2.0, 40, 60}` ⇒ **按文档单位（本机 mm）解释，不是米** | ★★ 与 `InsertMoveCopyBody2` **同族**（都是文档单位）⇒ ★ 本仓 `BaseFlangeSpec` 的「单位为米」**是错的**，既有调用点造的是 **0.002 mm 的箔片** |
| 10 | `ICustomBendAllowance::Type` | ★ `## Remarks` 逐字：「**If you do not set this property last**, the … property set last automatically **overrides** any previously set custom bend allowance type.」 | ★★ 官方示例本身顺序相反（先 `Type` 再 `KFactor`），**靠 `KFactor` 恰好也等于 2 而巧合成立** | ★ 不照 Remarks 写 ⇒ **`Type` 会被后设的属性覆盖**（静默） |
| 11 | `IModelDoc2::InsertSheetMetalUnfold` 的 `mark 4` | 官方 `## Remarks` **没给 mark**；★ 官方示例选了折弯特征并打 `mark 4` | ★★ 真机：**不选任何 `mark 4` 对象**（只给固定面 mark 1）时**照样建出 `展开1`** | ★ 把示例当「**必需**」读 ⇒ 会写出一条**多余的强约束**（甚至据此判「能力不可用」—— ★ **我一开始就是这么错的**） |

---

## 六 · ★★ 本批**自查**（★ 我自己写错、并当场修掉的 —— 记下来，因为不记就会被当成"本来就是对的"）

| # | 我写错了什么 | 怎么发现的 | 修法 |
|---|---|---|---|
| 1 | ★★ `rebuild_report` 的**包围盒判据是空转的**：`sw_part.get_bounding_box` 回的是**字典**，而我按可迭代对象写 ⇒ `float("min")` 抛异常被 `except` 吞掉 ⇒ 回 `None` ⇒ **`bbox_changed` 永远 `False`** | ★ **写 `move_copy_body` 时回头看同一模式** ⇒ 发现"读不到"与"没变"被混成同一个值 | ① 取对字段；② 返回值里**显式加 `bbox_comparable`**（`None`「读不到」与 `False`「没变」**必须分得开**）；③ 加回归测试 |
| 2 | 探针的 **T2 负例判据写错**：我以为越界会**抛异常**，而本函数**回字典不抛** ⇒ 那一格报"★ 没报错（不符预期）" | ★ 真机读数（★ 失败几乎总是我这边） | 负例判据改成看返回值的 `ok` / `error` |
| 3 | 探针的 **T3 判据太弱**：用**刚建的那条显示状态**去验"激活后变了没有" —— 而它**本来就是活动的** ⇒ `changed=False`，等于没验 | ★ 真机读数 | 改成激活**另一条**（`MCP_DS_PROBE` → `<默认>_显示状态 1`）⇒ `changed=True` |
| 4 | 探针的 **`EditRebuild3` 取证注释**照抄了裁决书的"拿到 bound method" | ★ 真机 `type()` 回的是 `bool` | ★ 按读数改口径（见 §五 第 1 条） |
| 5 | ★★ `move_copy_body` 的**单位按"COM 惯例"写成米** ⇒ 真机只挪了 **0.025 mm** | ★ 真机**包围盒读数**（★ 不是"没报错"） | 长度改成**原样传毫米**、角度改成 `deg()` 换算 —— ★ 并**两处都写进 `UNIT_FINDINGS` / `ROTATION_AXIS_FINDING` 随返回值带出** |
| 6 | ★★★ **B2 批（unfold/hem/fold）里我一次错得更深**：`SetSelectedObjectMark` 的 `Action` 传了 **`-1`**（要 `0`）⇒ **mark 静默没设上**，而我据此写下「unfold 建不出来」 | ★ **写 `create_unfold` 的"选择契约"回读时**（裁决书要求的那个回读判据）⇒ `mark_readback=1` 一出现，`展开1` **立刻就建出来了** | ① `Action` 改 `0`（`swSelectionMarkAction_e`）；② **判据从"返回值"改成"逐条回读 mark"**；③ 加回归测试钉住 `SELECTION_MARK_ACTION["set"] == 0` |
| 7 | ★★ `create_hem` 的**前置顺序反了**：我"先选边、再建 `CustomBendAllowance`"，而官方 `## Remarks` 的四步是**先建 CBA、最后选边** | ★ 读 Remarks 时发现的（★ **步序也是签名的一部分**） | 按 Remarks 重排；★ 重试后仍 `None` ⇒ ★ **按事实 53 停止**，如实记负结论（★ 不继续凑形态） |
| 8 | ★★ `create_fold` 的**前置特征选早了**：我把它塞在调用前，而选择函数开头有 `ClearSelection2` ⇒ **被清掉**（顺序错、静默失效） | ★ 写 `pre_select_names` 时想到的 | 把前置特征的选择挪到**清选区之后** ✓ |
| 9 | 探针读 **`IEdge.GetLength`** —— ★ 那个成员**在官方 API 里根本不存在** ⇒ 12 条边读数全 `None` | ★ 官方成员表逐条看出来的（★ 铁律 5） | 改用 `GetStartVertex`/`GetEndVertex` → `IVertex::GetPoint()` **自己算长度** |

⇒ ★★ **这九条的共同形态**：★ **判据看着在、其实没在判**（1/2/3/6）· **"惯例"顶替了实测**（4/5）·
**顺序/步序被当成"不重要"**（7/8）· **凭印象写成员名**（9）。
★ 都不是靠"更小心"避免的，★ 是靠**每次把回读数写进证据文件**才暴露的 ✓

---

## 七 · 本规格不算什么（限度，必读）

1. ★ **15 件活不是一批做完的** —— 进度看 `tasks.md` 的勾，不看我记得什么。
2. ★ **`verified` 只表示「有我们自己的运行证据」**，不表示「代码是我们写的」（A2 的两层 provenance）。
3. ★ B2/B3/B4 的「后端可达」在**真机验过之前**都只是静态推断（裁决书 §四.2 的原话）。
4. ★★ **本规格的探针是"一件活一格"** —— ★ 它**不覆盖**每件活的全部参数组合；
   没测到的分支一律写进该能力的 `limitations`（★ 例：旋转只验了"只给一个轴 30°"）✓
