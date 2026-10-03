# 工程图 8 条工具端到端探针 · 三候选裁决

★ 裁判：`codex` · 日期 2026-10-03 · 规格 `specs/202-user-coverage-gaps`（R1）
★ 候选：`recon/probe-drawing-tools-cand-a.py.txt` · `-b` · `-c`（三份均**未执行**）

---

## 〇 · 契约基准（打分的事实来源，**逐字**）

`mcp-server/tool_specs_batch75.py` 声明的 8 条 ToolSpec —— **全部 `Param` 没给默认值 ⇒
`Param.is_required`（`tool_registry.py:234-236`）全为真 ⇒ `build_input_model`（`:458-465`）
把每一个都建成 `Field(...)` **必填**项**：

| # | 工具 | **声明的必填参数**（逐字） | 能力层真签名（`scripts/sw_drawing_expose.py`） |
|---|---|---|---|
| 1 | `…create_projected_view` | `part_path` `view_name` `x_mm` `y_mm` `scale` | `:64` `(drawing_model, part_path, *, view_name="*Front", x_mm=140.0, y_mm=120.0, scale=0.0)` |
| 2 | `…create_section_view` | `x_mm` `y_mm` | `:104` |
| 3 | `…create_detail_view` | `x_mm` `y_mm` `scale` `label` `shape_intensity` | `:115` |
| 4 | `…set_sheet_format` | `format_path` | `:131` |
| 5 | `…add_note` | `x_mm` `y_mm` `text` | `:173`（`function="add_drawing_note"`） |
| 6 | `…create_hole_table` | `view_name` `x_mm` `y_mm` **`anchor_type`** **`start_value`** `template` **`tag_order`** **`tag_type`** | `:212` · 走 **`IView.InsertHoleTable3`**（`:244`），**前置 = 官方 mark 表 顶点1/孔边面2/X向4/Y向8**（`:222-224`，`:234` 据此判 `preconditions_held`） |
| 7 | `…create_revision_table` | `x_mm` `y_mm` **`anchor_type`** `template` **`shape`** **`auto_update_zoom_cells`** | `:256` · 走 **`ISheet.InsertRevisionTable2`**（`:273`） |
| 8 | `…insert_center_marks` | `requirements` | `:284` |

★ **没有** `projection`、**没有** `table_type`/`row`/`column`/`use_anchor_point` —— 这三个名字
在 `tool_specs_batch75.py` 里 **0 命中**（`grep` 逐行核过）。
★ `projection` 属**另一个函数** `create_three_standard_views`（`sw_drawing_expose.py:86-102`），
而它**没被挂成工具**（batch75 只 8 条）。

★ 调用路径基准：`make_tool_function(spec, input_model, run_locked, resolve_model=None,
resolvers=None, inject_as=None)`（`tool_registry.py:474-477`），`op()` 内 `:492-498` 按
`spec.params` **同名直传**、`:507` `kwargs[inject_as or inj] = resolver(params)`、
`:524-525` `__import__("scripts.%s")` + `getattr(mod, fn)(**kwargs)`；
注入键 = `effective_inject(spec)` = `"drawing_model"` → `register_capabilities.py:136`
→ `resolve_model`（`:53-60`）= **`sw.ActiveDoc`**。

---

## 一 · 评分表（每维 5 分，满分 20）

| 候选 | 调用路径按契约 | 判据可回读 | 三态分得清 | 真机能跑（无编造 API） | **总分** |
|---|---|---|---|---|---|
| **A** | **4** | **5** | **5** | 4 | **18** |
| **C** | 3 | 4 | 4 | 4 | 15 |
| **B** | 2 | 4 | 2 | 3 | 11 |

---

## 二 · 逐份判读（判据指到行）

### A — 胜者（18）

**调用路径 4/5**
- ★ **入口完全正确**：`load_tool_functions()`（`:224-257`）走 `register_capabilities.all_specs()`
  → `tool_registry.build_input_model` → `make_tool_function(spec, model, _run_locked, None, RESOLVERS)`
  （`:250-255`，五位位置与 `tool_registry.py:474-477` 的形参逐位对齐 ✓）。失败才退回
  `SPECS_BATCH75` 且**把退回原因记进 `notes`**（`:240-245`）—— 不静默换来源 ✓。
- ★ **`_run_locked` 本地镜像（`:197-217`）签名对得上** `make_tool_function:527-528` 的调用形状
  （`operation` / `response_format` / `load_automation=`），且异常→`{"status":"error"}` ✓。
  `_base_input_cls()`（`:147-154`）用真 pydantic 基类 + `extra="forbid"` ✓。
- ★ **三份里唯一在跑真机之前做静态契约对差的**：`contract_report()`（`:260-314`）拿
  `inspect.signature` 与声明逐名比，报 `NOT_accepted_by_capability` / `contract_ok`。
  main 里 `:1554-1558` 把它落进 `ev["static_contract_mismatched"]`。
- ✘ **扣分：实参仍照旧版**。`case_projected_view:838-841` 传 `{"part_path", "projection"}`；
  `case_hole_table:1245-1248`、`case_revision_table:1360-1363` 传 `table_type/row/column/use_anchor_point`。
  ⇒ pydantic `extra="forbid"` ⇒ `ValidationError`。**3/8 格在到达能力层之前就断了。**
- ★★ **最尖锐的自相矛盾**：A 的 `_diag_hole_table` 注释（`:1295-1298`）写着
  「它真实签名要 `view_name` + `anchor_type`，工具层**两个都没暴露**」——
  **这句话是错的**：`tool_specs_batch75.py:138-147` 两个都暴露了。也就是说 A **写了对差工具
  却没用它去改实参**：只要真跑一遍 `contract_report`，`NOT_accepted_by_capability` 就会当场打出
  `['anchor_type','start_value','tag_order','tag_type','view_name']`。
- ★ A 唯一做对的一件同类事：`_prep_hole_table_marks`（`:1272-1291`）**按官方 mark 表**选了
  顶点 mark 1 + 面 mark 2 —— 这是三份里唯一与当前能力层（`InsertHoleTable3`）对得上的前置准备。

**判据可回读 5/5**
- 视图数 `DQ.list_views`（`:450-455`）；注解三族 `GetNoteCount`/`GetTableAnnotationCount`/
  `GetCenterMarkCount2`（`:507-511`），**真视图 / 整条视图链各算一份**（`_anno_totals:514-538`），
  量不到就回 `None` 而不是猜 0（`_delta:541-550`）✓。
- 图纸格式用 `DQ.current_sheet_info` 前后 diff（`:1151-1153`），不是「返回非 None」。
- ★ **`built` 一律要求「返回值 `ok=True` **且** 读数真的涨」**（`:858-859`、`:944-945`、`:1057-1058`、
  `:1162-1163`、`:1212-1214`、`:1264-1265`、`:1474-1475`）—— 规则 6 落得最紧的一份。
- ★ `_finish`（`:808-814`）只认 `verdict` + `ok`，前置单独记（事实 496 的口径）。

**三态 5/5**
- 五态（`:62-72` / `:1523-1530`）：`built` / `precondition_not_met` / `true_negative` /
  **`tool_layer_contract_mismatch`** / `probe_error`，并**解释了为什么契约不匹配不能塞进三态**
  （塞「真阴性」= 冤枉能力层，塞「前置未成立」= 撒谎）—— 三份里唯一想清楚这件事的。
- ★ **A 是唯一把「pydantic 拒收实参」判成 `probe_error` 的**：`_call_and_parse:779-782` 造模型失败
  ⇒ `(None, err)` ⇒ `:856-857` `return _finish(row,"probe_error",…)`。
  **B/C 在同一处都判成了「真阴性」** —— 这是三态维度上拉开差距的决定性一条。
- ★ 每格都**写明缺哪个前置**：`:735`（零件/图纸不在）、`:739`（`GetModelViewNames` 回空）、
  `:948`（选区为空 + 为什么空）、`:1134`（找不到 `.slddrt`）、`:1352`（`GetCurrentSheet` 回 None）、
  `:1470-1473`（能力层回 `DRAWING_CENTER_MARK_REQUIREMENT_UNRESOLVED`）。

**真机能跑 4/5**
- 核过的调用全是真的：`C.VARIANT` / `C.pythoncom`（`sw_connect.py:16` 导出）✓、
  `P.feature_names`（`sw_part.py:28` 从 `sw_feature_readback` 转出）✓、
  `HF.create_hole_wizard_at_selection_report(model, selection, size)`（`sw_hole_features.py:1077-1079`）✓、
  `DQ.list_views/current_sheet_info` ✓、`_find_files` 全程 `is_dir()`/`OSError` 兜底 ✓。
- ★ `_activate_doc`（`:355-387`）判据是**回读 `sw.ActiveDoc` 的标题**，不采信 `ActivateDoc3` 返回值
  （事实 8 口径）；并先 `ActivateDoc3` 后 `ActivateDoc2` 兜底。
- ✘ 扣分：8 格里 3 格因实参错拿不到读数（不是崩，是白跑）；且 `case_center_marks:1426-1476`
  **没存盘** —— 能力层空路径会回 `DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED`，这一格等于白跑。

---

### C — 落选（15），可并入的最多

**调用路径 3/5**
- ★ 路径与 A 同级且同样正确：`_tool_callers`（`:192-210`）用真 `build_input_model` +
  `make_tool_function(spec, model, _run_locked, resolvers=RC.RESOLVERS)`（`:200-201`）。
- ★ `_ProbeBase` / `_ResponseFormat`（`:113-131`）**引了 `tests/test_tool_registry.py:49-74`
  的具体行号**说明「必须是真 pydantic 基类 / 真 Enum」，依据可指认 ✓。
- ★ `_collect_expose_specs`（`:160-189`）按 `module == "sw_drawing_expose"` 过滤。
  已核：`sw_drawing_expose` 在 `mcp-server/` 下**只被 batch75 用**（grep 4 处命中全在注释/常量）
  ⇒ 这个过滤恰好等于那 8 条，不会带进别的批次 ✓；并把 inject/params/必填性落进
  `info["contracts"]`（`:178-188`）✓。
- ✘ 实参同样照旧版：`case_t1_projected:706` 传 `projection`；`_ensure_parent_view:496` 也传
  （⇒ **连前置准备都坏**）；`case_t6/t7:869-871, 892-894` 传 `table_type/row/column/use_anchor_point`。
- ✘✘ **C 独有的调用错**：`_ensure_parent_view:504` 向**图纸文档**问 `GetModelViewNames` ——
  官方那是**模型**文档（`IModelDoc2`）的成员；注释（`:506`）却写「★ 视图名**向模型问**」。
  ⇒ 兜底路径几乎必然拿不到名字 ⇒ 剖视图 / 局部视图 / 中心符号线三格的前置连锁垮掉。

**判据可回读 4/5**
- `_readout`（`:300-354`）最全：视图数/名单、四族计数器（多一个 `GetAnnotationCount`）、
  `sheet_info`、`selection_counts` 按 mark 分组、`drawing_path`、`active_doc_title` +
  `active_doc_is_target`。`_DELTA_PATHS`（`:359-368`）+ `_deltas`（`:380-393`）通用增量表 ✓。
- ✘ **`_classify`（`:396-406`）判据串味**：`for value in (row["deltas"]).values(): if >=1 → built`。
  T2 剖视图的 `deltas=("views","selection")`（`:739`）⇒ **选区计数一变也会被判 `built`**，
  会把「前置没成立」伪装成「建成」。

**三态 4/5**
- ★ `harness_error` 作**第四态独立于三态**（`:40-41`、`:675-678`），判读纪律最清楚的一份。
- ★ **前置不成立 ⇒ 默认不调**（`:601-606` `call_even_if_pre_fails=False`）——
  这是三份里最干净的一条（避免制造假阴性）。
- ★★ **T2 特意 `call_even_if_pre_fails=True`**（`:717-740`），目的是**验工具层有没有把
  `preconditions_held` 透出来** —— 这正是事实 496 的核心，A 目前完全没验这一条。
- ✘ `_case` 对**调用期异常不短路**：`tool_call_error` 非空（ValidationError）时流程照走，
  `deltas` 全 0 ⇒ `_classify` 落 **`true_negative`**（`:614-642` 无短路）⇒ 探针接线错被判真阴性。

**真机能跑 4/5**
- `C.connect_solidworks(wait_seconds=30, return_metadata=True)` ⇒ 三元组（`sw_connect.py:690`）✓。
- 官方成员全部核对过真名，`_COUNTERS` 注明抄自已跑过的 `tools/prove_drawing_batch.py` ✓。

---

### B — 落选（11）

**调用路径 2/5**
- ✘✘ **不调 `make_tool_function`**：`call_tool`（`:448-477`）手工组装 kwargs、手工调
  `RESOLVERS[inject]`、手工 `getattr(mod, fn)(**kwargs)`。
  ⇒ **绕过了 pydantic 输入模型、`run_locked` 的异常包装、`response_format`** ——
  它验的是「参数能不能进能力层」，**不是「经工具层能不能跑通」**，而那正是本任务要验的东西。
- ★ 诚实之处：文件头 `:19-22` **自认** `extra_op` / `derived_args` / `pre_call` 三个注册器钩子
  没实现，并把结果写进 `contract.registry_only_hooks`（`:419-420`、`:1242-1243`）✓ 值得肯定。
- ✘✘ **`projection` 那一整套认知属于另一个函数**：B 的 T1/T2（`:623-698`）整段建立在
  `projection="third_angle"/"first_angle"` + `Create3rdAngleViews2`/`Create1stAngleViews2` 上。
  batch75 的这条工具**没有 `projection` 参数**；那个成员名限制属 `create_three_standard_views`
  （`sw_drawing_expose.py:86-102`），**且它没被挂成工具**（spec doc `:70-72` 自己就写了
  「★ 该限制**未**挂成工具」）⇒ B 花掉整整一格去验一条**不在被测契约里**的限制。
- ✘ `_build_kwargs` 遇缺参数直接 raise（`:442-445`），而 `case_t1/t2/…` 的 `except`
  把它记成 **`TRUE_NEGATIVE`**（`:723-724` 等）⇒ **探针接线错被判成「真阴性」**。

**判据可回读 4/5**
- ★ 四族零参计数器（`:224-229`，比 A 多一个 `GetAnnotationCount`）+ 真视图/整链两份 ✓。
- ★ `tool_ok_vs_readback` 单列成独立栏（`:1300-1305`），并在 `:1297-1299` 点名
  「`create_projected_view`：能力层回的是 `status/created` 而不是 `ok`」——
  这条**对当前能力层已经过期**（`_result:55-56` 现在会推导 `ok`），但**把结论与依据分开记**的写法是对的。
- ✘ T3/T4 判据用 `view_delta == 1`（`:801`、`:876`）—— 恰好 +1 才算 built，
  建出 0 或多张都落 `true_negative`，判据偏脆。

**三态 2/5**
- ✘ **接线错一律记 `TRUE_NEGATIVE`**（`:659-661`、`:723-724`、`:804-806`、`:879-881`、
  `:935-937`、`:988-990`、`:1074-1076`、`:1186-1188`）——**这是本维度最重的失分**：
  一个探针 bug 会以「能力不成」的姿态进证据，正是事实 496 那类污染。
- ★ T2（`:670-698`、`:712-721`）**预期 blocked** 的写法本身很好：回读运行期
  `getattr(doc,"CreateFirstAngleViews2")` / `"Create1stAngleViews2"` 各存不存在，
  把「结论」与「依据」分开——**这个片段值得并进 A**（见下）。

**真机能跑 3/5**
- `C.out_i4(0)`（`sw_connect.py:511`）✓、`C.new_document(..., template_path=)`（`:826`）✓、
  `DQ.current_sheet_name/current_sheet_info` ✓、官方成员名全部核对过 ✓。
- ✘ 能起来，但**验的不是工具层** ⇒ 按本任务口径只值 3。

---

## 三 · 胜者

> **A 胜出（18 / 20）。**
> 理由：**它是唯一一份「入口走真 `make_tool_function`、判据一律零参官方回读成员、
> 且把「实参被 pydantic 拒收」如实判成 `probe_error` 而不是伪装成「真阴性」的探针**；
> 另两份在同一处失守 —— B 的 `_build_kwargs` raise 被 `except` 吞成 `TRUE_NEGATIVE`
> （`:723-724`），C 的 `_classify` 对 `tool_call_error` 不短路（`:614-642`）
> ⇒ **一个纯探针接线错会以「能力不成」的姿态进证据**，而这正是事实 496 记的拖垮整批的那种污染。

---

## 四 · 该把落选者的哪些片段并进 A

| # | 来源 | 片段（行） | 为什么必须并 |
|---|---|---|---|
| 1 | **C** | `case_t8_center_marks` 的 `setup`（`:916-922`）：**先把工程图存盘**再调 | A 的 `case_center_marks:1426-1476` **没存盘** ⇒ 能力层空路径必回 `DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED` ⇒ 这一格**白跑**。A 现在是「忘了自己的前置」，不是三态问题。 |
| 2 | **C** | `_case` 的 `call_even_if_pre_fails`（`:601-606`）+ T2 的 `call_even_if_pre_fails=True`（`:717-740`） | A 目前前置不成立就 `return`（如 `:834`、`:1134`）⇒ **验不到工具层有没有把 `preconditions_held` 透出来** —— 而那是事实 496 的核心问题。 |
| 3 | **B** | `_revision_table_readback`（`:291-302`）回读 `ISheet.RevisionTable` | 官方 `InsertRevisionTable2` 的 Returns **就是它**（B `:1068-1070` 自己写明）。A 的 `case_revision_table` 只看 `GetTableAnnotationCount` + 从 payload 里读 `raw_is_none`（`:1380-1387`）⇒ 分不出「建了通用表」和「建了修订表」。 |
| 4 | **B** | T2 的**预期值 + 回读运行期成员存在性**（`:694-698`、`:712-721`） | 写法本身对：把「结论」与「依据」分栏。⚠ 但**必须换掉它的对象** —— `projection` 不在契约里（B `:26-31` 那套 `1st` vs `First` 的分析对应 `create_three_standard_views`，不是这条工具）。并进 A 时改成**单变量对照**：同一前置、同一组合法实参，只变一个量。 |
| 5 | **B** | `check_inject_is_active_doc`（`:487-499`）+ `call` 里记 `inject_host_title/path/type`（`:470-472`） | A 只在自己调 `_activate_doc` 时回读（`:383-387`），**没把「注入进去的那个对象」本身记进证据**。判据要求证明「注入的确实是目标图纸」，B 这一栏更直接。 |
| 6 | **B** | `contract_of` 的 `registry_only_hooks`（`:419-420`）与 `main` 里的汇总（`:1242-1243`） | A 的 `contract_report:260-314` 缺这一栏。补上就能自证「这 8 条没用 `extra_op`/`derived_args`/`pre_call` ⇒ 探针等价」，把 A 的静态对差从「半件」变成「整件」。 |
| 7 | **C** | `_invoke`（`:213-233`）把**调用期异常 / 响应是不是 str / JSON 解析失败**三者分开报 | A 的 `_call_and_parse:765-792` 把「造模型失败」和「返回不是 JSON」压成一个 err 串。★ 补一条**专门识别 pydantic `ValidationError`** 的判据，报「实参未按 `spec.params` 组装 + 差集」—— 这正是三份共有错在 A 身上的表现（见 §五），当场暴露而不是混进格子结果。 |
| 8 | **C / B** | `GetAnnotationCount` 进计数器组（C `:238-243`、B `:224-229`） | A 的 `_COUNTER_MEMBERS:507-511` 只有三族。注解类多一个口径作交叉核，低优先但零成本。 |

---

## 五 · ★ 三份共有的错（同一个错，三处重犯）

> **三份都照着一份「旧版 / 想象的」ToolSpec 调参 —— 8 条里有 3 条在到达能力层之前必然失败。**

**错在哪**
- 三份都给 `…create_projected_view` 传了 **`projection`**：A `:840` · B `:609`/`:645`/`:701` · C `:496`/`:706`。
- 三份都给两个表工具传了 **`table_type` / `row` / `column` / `use_anchor_point`**：
  A `:1246-1247`/`:1361-1362` · B `:1051-1053` · C `:869-871`/`:892-894`。
- 而 `tool_specs_batch75.py` 逐字是：**没有 `projection`**（`:53-73`）、
  孔表是 `view_name/x_mm/y_mm/anchor_type/start_value/template/tag_order/tag_type`（`:132-156`）、
  修订表是 `x_mm/y_mm/anchor_type/template/shape/auto_update_zoom_cells`（`:157-175`）。

**为什么会断（三种不同的断法，同一个根因）**
- A、C 走真 `build_input_model`，基类 `extra="forbid"` ⇒ **pydantic `ValidationError`**。
  A 判 `probe_error`（`:856-857`）· **C 落 `true_negative`**（`:614-642` 不短路）。
- B 不走 pydantic，被自己的 `_build_kwargs` 抛 `RuntimeError`（`:442-445`）⇒ **落 `TRUE_NEGATIVE`**（`:723-724`）。

**派生出的第二个共有错：对孔表入口的认知也停在旧版**
B `:1044-1047` 写「`official_mark_table_applies = False`，因为能力层走通用 `InsertTableAnnotation`」，
C `:864-865`/`:873-876` 写「本工具走通用 `InsertTableAnnotation`，★ 故不当前置」——
**当前能力层早就改走 `IView.InsertHoleTable3`**（`sw_drawing_expose.py:244`），
且 `:234` 正是按官方 mark 表（顶点 1 / 孔边面 2）判 `preconditions_held`。
**只有 A 的代码路径对得上**（`_prep_hole_table_marks:1272-1291` 按 mark 1/2 选），
但 A 的**实参**仍是旧版 —— 而且 A 的 `_diag_hole_table:1295-1298` 注释还断言
「工具层没给 `view_name`/`anchor_type`」，**这句本身也是错的**（spec `:138-140` 两个都给了）。
⇒ 换句话说：**A 写了对差工具却没用它改实参**，这与 B、C 是同一个病。

**根因（三份一致）**：都从**实现层的记忆**或**另一条工具的契约**反推参数名，没有一处
在构造实参前把 `spec.params` 逐条打印出来核对（A 有 `contract_report` 却没接到实参上）。
⇒ **修法（一句话）**：实参**只能**从 `[p.name for p in spec.params]` 生成，
多一个少一个都当场判 `probe_error` 并列出差集；**不许出现 spec 里没有的名字**。