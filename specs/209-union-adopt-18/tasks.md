# 规格 209 · 任务 checklist

> `[ ]` 未做 · `[x]` 已做且**过判据** · 每条后面写「怎么知道的」。★ 未过判据的不许写 `[x]`。
> ★ 判据编号（SC-x）见 [spec.md](spec.md) §四。

## B1 · 最干净的 5 件活

- [x] **SC-1** 15 件活的分批与裁决依据逐条落表 —— `spec.md` §1.1（★ 且**明写了** bunny 建议与 Lead 裁决的 3 处差异）
- [x] **B1-1** idx **235+236** `rebuild`（★ **裁决书强制合并成一条三档 mode**）
      ⇒ `scripts/sw_session.py::rebuild_report` + `solidworks_session_rebuild`
      ★ 怎么知道的：真机三档全过（`edit`/`force`/`all` 都 `ok=True` · `needs_rebuild 0→0` · `tree 7→7` ·
      `bbox_changed=False`）+ 负例 `mode='nonsense'` 被入口拒 ⇒ `output/union-adopt-b1-evidence.json` 的 T1 格
- [x] **B1-2** idx **79** `construction_geometry` ⇒ `scripts/sw_sketch_edit_ops.py::sketch_set_construction_geometry`
      + `solidworks_sketch_set_construction_geometry`
      ★ 怎么知道的：真机双向全过（置位 `ok=True`、复位 `ok=True`、逐段回读 `[false,false]→[true,false]→[false,false]`）
      + 负例 `index:99` ⇒ `ok=False` + 越界原因 ⇒ T2 格
- [x] **B1-3** ★★ **回答裁决书要求先定的那个问题**：`CreateConstructionGeometry` 连调两次是**切换**还是**置位**
      ★ 怎么知道的：真机 `[true,false] → [true,false]`（**不变**）⇒ **置位（幂等）** ⇒ `T2_toggle_probe` 格
- [x] **B1-4** idx **97** `display_states` ⇒ `scripts/sw_render_material.py::{list_display_states,apply_display_state}`
      + 两个工具
      ★ 怎么知道的：真机零件上 `['<默认>_显示状态 1'] → ['MCP_DS_PROBE','<默认>_显示状态 1']` ·
      激活另一条后 `active_before/after` **真的变了**（`changed=True`）+ 负例不存在的名字 ⇒ `ok=False` 不猜 ⇒ T3 格
- [x] **B1-5** idx **244** `referenced_documents` ⇒ `scripts/sw_document_data.py::document_dependencies`
      + `solidworks_document_dependencies`
      ★ 怎么知道的：真机自建 1 零件 + 1 装配 ⇒ `ok=True` · `count=1` · `raw_len=2`；开了只读信息 ⇒ `raw_len=3` ⇒ T4 格
- [x] **B1-6** idx **209** `move_body` ⇒ `scripts/sw_body_ops.py`（新）+ `solidworks_part_move_copy_body`
      ⇒ `scripts/sw_body_ops.py`（新）+ `solidworks_part_move_copy_body`
      ★ 怎么知道的：真机（★ 判据 = **包围盒变 / 实体个数增**，都回读）——
      移动 `25 mm` ⇒ 包围盒 x `-30/30 → -5/55`（**正好 25**）；复制 ⇒ **实体 1→2**；
      平移+旋转同给 ⇒ `both_given=True`；负例越界 ⇒ `ok=False` ⇒ T5 格
- [x] **B1-7** ★★ **真机定死两件官方没写的事**（★ 都随返回值带出，不写就是静默错）
      ★ 怎么知道的：① **长度是 mm 不是米**（先按"米"换算传 0.025 只挪了 0.025 ⇒ 那是**静默的 1000× 错**）；
      ② **角度是弧度**（传 30.0 得到约 81°）⇒ **一个调用里混两种口径**；
      ③ **官方参数名与实际作用轴 X↔Z 互换** —— 由 `T5b` 三格互证（只给一个角、看**哪一轴跨度不变**）定出，
      ★ 补偿后复验：`rotate_angle_z_deg=30` ⇒ 跨度 `[60,40,20] → [71.9615,64.641,20]`，
      而 `71.9615 = 60·cos30+40·sin30`、`64.641 = 60·sin30+40·cos30` **逐位吻合** ⇒ 单位与轴**同时被证**✓

## B1 · 门禁与登记（★ 与上面 5 件活同批收口）

- [x] **SC-2** 工具真正注册 —— `register_capabilities.all_specs()` 实测 **439** 个（本批 433 → 439，6 条）
      ★ 怎么知道的：`check_specs(all_specs())` 回 **0 个问题**
- [x] **SC-3** 本批过收尾链 —— `pwsh -File tools/round_chain.ps1 -Tests tests/test_tool_specs_batch92.py`
- [x] **SC-4** 真机证据文件落盘 —— `output/union-adopt-b1-evidence.json`（★ 判据全是**回读**，不是返回值）
- [x] **SC-5** ★★ **官方文档与真机读数不一致处逐条记账** —— `spec.md` §五 **6 条**：
      `EditRebuild3` 读即调（恒真）· 只读信息串真机回 `"FALSE"` 而官方例子是空串 ·
      `CreateConstructionGeometry` 实测是置位（官方没说）· 「第一个名字即活动」在装配里不成立 ·
      **`InsertMoveCopyBody2` 的长度是 mm 不是米** · **同一成员的 `RotAngle*` 是弧度且 X↔Z 互换**
- [x] **SC-6** `capabilities.yaml` 追加 **5 条**（`level: verified`，★ 各带 evidence + limitations）
      ★ 怎么知道的：第一次追加 139 行纯插入；第二次（更正 + 追加）**39 插入 / 1 删除**
      （★ 那 1 删除是 `session_rebuild` 的 `evidence[0]` 被替换 —— **是有意改的**，不是误删）✓
- [x] **B1-8** 契约测试 25 条全绿 —— `pytest tests/test_tool_specs_batch92.py -q`
      ★ 其中 **7 条是硬约束/自查项的回归**（`EditRebuild3` **真被调用** · 装配 `ambiguous` ·
      两入口读数不一致必须报 · 长度除不尽必须拒 · `"FALSE"` 必须判成 `False` 且认不出回 `None` ·
      **`bbox_comparable`：`None`（读不到）与 `False`（没变）必须分得开** ·
      **旋转轴补偿：要"绕 Z"就放进第 1 个角槽**）

## B2 · 须真机定前置（4 条）

> ★★ **本轮的执行顺序改过一次（我的拍板，记下来）**：先做 **B4-2（hem）**，因为它当时看起来是
> 「造出带折弯钣金件」的**唯一可达路径**（那是 unfold/fold 的前置）。★ 结果 **hem 五种形态全失败**，
> 而 unfold/fold **只要把 mark 摆对就能建出来** ⇒ ★ 顺序上的那一跳**没有白跑**：
> 它同时产出了「单位定案」「`IEdge` 没有长度成员」「`SetSelectedObjectMark` 的 Action」三条事实 ✓

- [x] **B2-1** idx 336 `unfold` ⇒ `scripts/sw_sheet_metal.py::create_unfold` + `solidworks_sheet_metal_create_unfold`
      ★ 怎么知道的：真机（`tools/probe_spec209_unfold_fold.py`）**建出 `展开1`** ——
      特征树 +1 · ★★ **选择契约逐条回读** `total_count=2 · marks=[1, 4]` ·
      平展型式 `GetFlatPatternCount` = 1 ⇒ `output/spec209-unfold-fold.json`
      ★★ **两条被真机纠正的**：① `mark 4` 的对象**不是必需的**（只给固定面 mark 1 也能建成）；
      ② 第一轮的"没建出来"**是我自己的 bug**（`SetSelectedObjectMark` 的 `Action` 传了 `-1`，要 `0`）
- [x] **B2-2** idx 34 `balloon`（`IDrawingDoc::AutoBalloon5`）⇒ 能力层**早已实现**
      （`sw_drawing_create_missing.auto_insert_balloons`）⇒ 本批做三件：**收紧判据 + 挂工具 + 真机定案**
      ⇒ `solidworks_drawing_insert_balloons`（★ level = `verified`）
      ★★ **定案（裁决书点名的那件事：两家结论互相矛盾）**：真机**两格独立对照**（自建装配 + **两张独立图纸**）⇒
      ① **没有 BOM 表** ⇒ `ok=True` · `GetNoteCount` **0→1（Δ=1）** · 返回数组长度 **1**；
      ② **先插 BOM 表** ⇒ `ok=True` · **Δ=1** · 返回 **1**
      ⇒ ★ **Slacker-LLC 的「静默无效」在本机不成立**；★ **Eduardof0nt 的 `bool(result)` 也不能当判据**
      ⇒ ★★ **判据只能是 `GetNoteCount` 的增量** ⇒ `output/spec209-balloon.json`
      ★★ **判据收紧**：原 `ok` 是 `bool(返回数组) and (delta >= 0)` ⇒ 现在
      `ok = (delta is not None and delta > 0)`（★ **差 0 = 什么都没插，却会通过** —— 旧判据太松）
      ★★ **我自己的假设被真机否证**：我按官方示例的 `Preconditions` 假设「没有 BOM 表 ⇒ 静默无效」
      ⇒ **错**。★ 已记进 `spec.md` §五 第 12 条：**`Preconditions` 是「例子的环境」、不是「API 的契约」** ✓
      ★★ **探针自身的一处设计缺陷**：第一版第二格与第一格**共用同一张图**（气泡已存在 ⇒
      `IgnoreMultiple` 只是没重复插）⇒ 那一格的 Δ=0 **不能当证据** ⇒ 改成**两张独立图纸**才得上面两格 ✓
      ★★ **原函数自述「不建 ToolSpec」的理由已过期**（那句说的是**底层成员**的 COM 形参；
      包装函数的形参**全是标量**）⇒ 本批把它挂成工具 ✓
- [x] **B2-3** idx 52 `centerline`（`IDrawingDoc::InsertCenterLine2`，零参）
      ⇒ `scripts/sw_drawing_create_missing.py::insert_center_lines` +
      `solidworks_drawing_insert_center_lines`（★ level = **`stitched`**）
      ★ 怎么知道的：真机（`tools/probe_spec209_b2_centerline.py`）圆柱零件的工程图视图 ⇒
      `GetVisibleEntities2` 回 **edge=1 · face=1**（silhouette/vertex 回 0）；`Select4` **按对象**选上后
      **选区回读 = 1**；而 `InsertCenterLine2` **回 `None`**、`GetCenterLineCount` **0→0（Δ=0）**
      ⇒ ★★ **「选中了也没产出」** ⇒ `output/spec209-centerline.json`
      ★★★ **两家矛盾的定案（各对一半）**：★ 说「**静默无效**」的**不准确**（它**并不静默** ——
      返回值就是 `None`）；★ 说 `bool(result)` 的**在本例里恰好对**，★ 但**不能通用**
      （"回非 None 而几何没变"那种只有**回读增量**抓得住）✓
      ★★ **为什么是 `stitched`（不是 verified）**：★ **官方前置只复现了一半** ——
      官方示例是**先选 `COMPONENT`、再按点选 `FACE`**，且**它的视图来自装配**
      （`cylinder20-9@Drawing View1`）⇒ ★ 本轮只复现了「选实体」那半、夹具是**零件**视图
      ⇒ ★ 结论**限定在这条路径上**；下一步 = 装配图 + 先选组件 + 再选面 ✓
      ★★ **我踩了已知事实 33 的同一形态**：`GetVisibleEntities2` 的 `LpViewComponent`
      **不能传 Python `None`**（⇒ `com_error -2147352571 类型不匹配`）—— 第一次四种类型全报它，
      ★ 看着像"读不到"、**实际是我传错了** ⇒ 现在包 `create_empty_dispatch_variant()` ✓
      ★★ **裁决书建议"与 idx 30 `auto_center_marks` 合并成一条工具两种模式" —— 我没照做**：
      两条入口**入参形状不同**（本条形参可全标量；`auto_center_marks` 收**结构化 requirements 列表**）
      ⇒ `Param` 表达不了 ⇒ ★ 硬合并会造出「一半参数对一半模式无意义」的工具 ⇒ **偏离已记账** ✓
      ⚠ **裁决书 §一 第 2 条点名的缺口**（批量路 `AutoInsertCenterMarks2` 从未单独真机验证）
      **本轮仍未补** ⇒ ★ 已列为下一轮的活 ✓
- [x] **B2-4** idx 175 `blank_sketch` ⇒ `scripts/sw_sketch.py::set_sketch_blanked`（+ `feature_visibility`）
      + `solidworks_sketch_set_blanked`（★ ★★★ **名字里没有 `all`** —— 见下）
      ★ 怎么知道的：真机（`tools/probe_spec209_b2_blank_sketch.py`）**双向都过**：
      按名字选中 `草图1` ⇒ 隐藏档 `IFeature::Visible` 回读 **`shown`(2) → `hide`(1)**、
      显示档 **`hide`(1) → `shown`(2)**；负例（名字不存在）⇒ 选区计数 **0** + 大声报
      ⇒ `output/spec209-blank-sketch.json`
      ★★★ **裁决书硬约束已照办**：官方摘要逐字「Hides the **selected** sketches」⇒
      **官方没有 "all"** ⇒ ★ 工具名 **`solidworks_sketch_set_blanked`**
      （★ 裁决书原建议是 `solidworks_sketch_set_all_blanked` —— **我按它自己给的理由去掉了 `all`**：
      那个名字同样会许下官方没有的语义；★ 已加静态断言：名字里不许出现 `all`）
      ★★ **本条的真正产出 = 把裁决书点名的「怎么回读隐藏了没有」定案**：
      ★ 官方回 `void`、那页既无 Returns 也无 Remarks、官方示例的判据**只有肉眼** ⇒
      ★★ 真机定出回读入口是 **`IFeature::Visible` → `swVisibilityState_e`**（Hide=1 · Shown=2 · Unknown=3）

## B3 · 先小验证（1 条）

- [x] **B3-1** idx **115+145** `edges`/`faces`（★ **裁决书强制合并成一条工具**，三种 kind）
      ★ 形态 = **扩** `scripts/sw_selection_spec.py` 的 `entities_on_body`，**不许开平行工具**
      ★ 怎么知道的：真机（`tools/probe_spec209_b3_entities.py`）20×20×10 盒 ⇒
      **FACE=6 · EDGE=12 · VERTEX=8** + ★★ **欧拉 `V−E+F=2` 成立**；逐条几何都读得到
      （EDGE 两端点 + **自己算的**边长 · FACE `GetArea()` · VERTEX `GetPoint()`）；
      负例（越界序号 / 非法 kind）都大声报 ⇒ `output/spec209-b3-entities.json`
      ★★ **真正修掉的缺口**：旧工具指向的 `entities_on_body` **返回 COM 对象** ⇒
      **过不了 MCP 的 JSON 边界** ⇒ 那条工具**经工具层拿不到东西**；修法 = **名字不变**、
      指向改成 `entities_report`（★ 清单这侧也不开平行条目，证据补进既有 `selection_helpers`）
      ★★ **本轮顺带拿到的**：`IEdge` **没有**长度成员（要自己用两个顶点算）—— 见 `spec.md` §五 第 7 条
      ⚠ 探针第一版的负例判据又写错一次（报告函数**回字典不抛**）⇒ 已按 B2 批的同一教训改正

## B4 · 余下（5 条）

- [x] **B4-1** idx 211 `native_macro_recording`（`ISldWorks::RecordLine` + `RunCommand`）
      ⇒ `scripts/sw_macro.py::toggle_macro_recording` / `record_line` / `record_macro_lines`
      + `solidworks_macro_record_lines`（★ level = **`stitched`**）
      ★★★ **裁决书点名的头号风险已绕开**：`swCommands_StopMacro`(31) 官方枚举页**逐字**
      「**opens the Save As dialog**」⇒ ★ 本模块**永不调 31**，停录制改走
      `swCommands_RecordPauseMacro`(29) 这个**切换**（★ 官方 `RecordLine` 的 Remarks 也正是用 29 开关录制）✓
      ★★ 怎么知道的：真机（`tools/probe_spec209_b4_macro_recording.py`）⇒
      ① ★★ **未开录制时 `RecordLine` 也回 `True`**；② 成对（29 → RecordLine ×3 → 29）⇒
      开 True · 逐行 [True,True,True] · 停 True；③ 空文本入口就拒；④ **31 一次都没调**、
      **0 弹窗** ⇒ `output/spec209-macro-recording.json`
      ★★★ **为什么是 `stitched`（这条读数最有价值）**：官方 Remarks 说「**只有录制开着才写得进去**」，
      而★ **真机"未开录制"也回 `True`** ⇒ ★★ **那个 bool 证明不了任何事**；
      ★ 要真证得看**落盘的宏文件**，那要 31 的 Save As ⇒ ★ 本条只到「成对调用可达」这一级 ✓
      ★★ 静态守卫：断言源码里**不许出现**把 31 传给 `RunCommand` 的调用（★ 只扫代码 ——
      注释里引用它是"防它的证据"）✓ ★ 并在 `finally` 里保证**录制一定被停掉** ✓
      ⚠ **未接**：裁决书提到的 `DSldWorksEvents::{BeginRecordNotify,EndRecordNotify}`（事件）⇒
      ★ 如实记「未接」（★ 铁律 5）✓
- [x] **B4-2** idx 173 `hem`（真名 `IFeatureManager::InsertSheetMetalHem2`，**16 形参**）
      ★★ 别家三处错误（成员名零命中 · `hem_type` 把 `Open=0`/`Closed=1` **正好互换** · **漏掉 `Double=4`**）
      ⇒ ★ **裁决书要求做成 L2/L3 静态断言 —— 已做**（`tests/test_tool_specs_batch93.py`：
      五个成员一个不漏 · 幻觉名不许进**代码**（★ 注释里引用它是**防它的证据**，要用
      `strip_comments_and_strings` 把"引用"与"断言"分开））
      ★★ **真机结论：建不出来**（五种形态全部回 `None`）⇒ 能力标 **`stitched`**、
      工具挂出来但 `require_verified` **调用前抛带原因的错误** ⇒ `output/spec209-hem-*.json`
- [x] **B4-3** idx 181 `intersect` ⇒ `scripts/sw_boolean_ops.py`（**新建** —— 本仓既有零件特征模块里
      没有多体/布尔这一族，★ 裁决书指定的落点就是它）+ `solidworks_part_intersect`
      ★ 怎么知道的：真机（`tools/probe_spec209_b4_intersect.py`）**四种组合**都跑了 ——
      不排除 ⇒ `PreIntersect2` 回 **1 个体** · `PostIntersect` 建出 **`相交1`** ·
      `GetIntersectionsCount()` 回 **1**（★ 两种 region_type 都成立）；
      ★★ **排除唯一的体** ⇒ `PostIntersect` 回 `None`、特征**没建出来** ⇒
      `output/spec209-intersect.json`
      ★★★ **裁决书点名「唯一要实测」的那件事已验**：`PostIntersect` 第 1 参是 `System.object`
      布尔 SafeArray ⇒ 包 **`VARIANT(VT_ARRAY | VT_BOOL)`**，★ 而真机是**双向**证实的 ——
      **排除的那个 `True` 真被 SW 读走了**（不是"参数被忽略却没报错"）✓
      ★ 另：判据用 **`GetIntersectionsCount()`（零参回 int）**，★ **不用**
      `GetIntersections(out Excluded)` —— 它有 out 参，而本仓已知 pywin32 下 out 参不保证回写
- [x] **B4-4** idx 155 `fold` ⇒ `scripts/sw_sheet_metal.py::create_fold` + `solidworks_sheet_metal_create_fold`
      ★ 怎么知道的：真机 `unfold → fold` 一条链 ⇒ **建出 `折叠1`**（树 +1 · `marks=[1, 4]`）
      ⇒ `output/spec209-unfold-fold.json`
      ⚠ **裁决书说它的 mark 表是 `Fold=0/1/4`** —— ★★ 真机读到的是 **`[1, 4]`**（外加前置特征 mark 0）
      ⇒ ★ **按读数记**（★ 这正是「不许跨条复制 mark 表」的又一处现场）
- [x] **B4-5** idx 205 `model_annotations`（`IDrawingDoc::InsertModelAnnotations4`，**8 参**）
      ⇒ `scripts/sw_drawing_create_missing.py::insert_model_annotations` +
      `solidworks_drawing_insert_model_items`（★ level = **`stitched`**）
      ★ 怎么知道的：真机（`tools/probe_spec209_b4_model_annotations.py`）**只验到"可达 + 回读可用"**：
      调用**不抛**、回的是数组（长度 **0**）· `IView::GetAnnotationCount()` 前后回读 **0→0** ·
      两个负例（空图纸 / 什么都没让它插）**都大声报** ⇒ `output/spec209-model-annotations.json`
      ★★★ **为什么是 `stitched` 而不是 `verified`（原因已查明）**：我们的零件是**纯坐标画出来的**
      ⇒ **一个尺寸都没有**；而本仓的 `add_horizontal_dimension` / `add_vertical_dimension`
      **都回 `None`**（官方 `AddDimension2` 摘要逐字「for **selected entities**」⇒ 要先选中实体）
      ⇒ ★★ **夹具里没有可插的东西** ⇒ ★ 这是**数据相关**的失败，**不是**后端到不了 ✓
      ★★ **落点偏离裁决书建议**（它说 `scripts/sw_drawing.py`）：★ 那只有 **29 行**、是**桥接壳**
      （`exec_module` 加载 subskill 再 `globals().update`）⇒ 往里加会被覆盖；
      ★ 实际落 `sw_drawing_create_missing.py` —— ★ 裁决书自己要求「复用该文件已有的读侧助手」✓
      ★★ **两处我自己写错并修掉的**（都已记进 `capabilities.yaml` 的 limitations）：
      ① 把 `_find_view` 的 **`(view, error)` 元组**当成视图对象用 ⇒ 报"取不到视图名"（指不出真因）；
      ② `AllViews=False` 时**无脑清选区** ⇒ 官方要的是「**currently selected** drawing view」⇒ 回空数组
      （★ 已加静态断言 `if all_views:` 钉住）

## 收尾

- [x] **SC-3** 全部 15 件活收口后跑一次**全量** `pytest`
      ★★ **已跑（两轮，共 ~15 分钟）**：首轮 **38 failed / 7 errors / 2078 passed** ⇒
      修掉我自己引入的三类（**R11 违规 4 条** · **7 个批测试的"绝对总数"断言** · **无人值守基线**）
      + **一处收集期导入失败**（`test_sw_part_sketch_selection.py` 的桩缺 `safe_get_com_member`）
      ⇒ 次轮 **18 failed / 2105 passed / 20 skipped（444.76 s）** ✓
      ★★ **首轮暴露的教训（★ 值得留下）**：★ 焦点测试每轮只跑本批那个文件，
      **跨文件的断言（总数 / 基线 / 模块身份）它看不见** ⇒ ★ **全量 pytest 不是形式** ✓
- [ ] **SC-4**（★ 收口时新发现，下一轮第一件）修掉剩下的全量红 ——
      ★ **第一件（根因已定性）**：`tests/test_sw_part_sketch_selection.py` **把假 `sys.modules["sw_connect"]`
      **泄漏给了后续测试**（导入完不还原）⇒ 后面的测试拿到假模块 ⇒ **成批变红**。
      ★ 证据：`pytest tests/test_tool_specs_batch92.py` ⇒ **25 passed**；跟在它后面跑 ⇒ **成批 FAILED**。
      ★ 修法：导入完 `sw_part` 后还原/删除那两个 `sys.modules` 假条目（★ 先确认 `sw_part` 不在调用期懒导入）
      ★ **其余红点（已逐条定性为"非本次改动"）**：`verify_union_349.py:112` 既有红 ·
      `test_rule2_length_suffix_is_enforced`（`view_set_frame/top_px` 理由措辞）·
      `test_sw_connect_open_document`（替身返回 bool）· `test_sketch_slot_params`（解析不出 `CreateSketchSlot` 实参）·
      `test_tool_specs_batch79`（17 个宏工具没全进 specs）
- [x] 更新 `docs/HANDOFF.md`（★ 交接给下一个会话 —— 本版 §一~§五 就是）
