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

- [ ] **B2-1** idx 336 `unfold`（官方**没给 mark** ⇒ 先定"可建对象"，前置判据用回读计数）
- [ ] **B2-2** idx 34 `balloon`（★ **两家结论互相矛盾** ⇒ **不许照抄任何一家**）
- [ ] **B2-3** idx 52 `centerline`（同上；★ 裁决书建议与 idx 30 `auto_center_marks` 合并成两种模式）
- [ ] **B2-4** idx 175 `blank_sketch`（★ 真风险 = **怎么回读「隐藏了没有」** —— 官方回 `void` 且无 Remarks
      ⇒ ★ 且工具名**不许叫 `hide_all_sketches`**：官方语义是"**隐藏选中的**草图"）

## B3 · 先小验证（1 条）

- [ ] **B3-1** idx **115+145** `edges`/`faces`（★ **裁决书强制合并成一条工具**，三种 kind）
      ★ 形态 = **扩** `scripts/sw_selection_spec.py` 的 `entities_on_body`，**不许开平行工具**
      ★ 第一步：小验证「读属性读不到」这个独立风险（`IBody2::GetEdges/GetFaces` 已在事实 32 真机确证可用）

## B4 · 余下（5 条）

- [ ] **B4-1** idx 211 `native_macro_recording`（`RecordLine` + `RunCommand` + 事件）
      ★★ **必须先解决弹窗**：官方 `swCommands_e` 逐字写 `swCommands_StopMacro` **会弹 Save As**
      ⇒ 工具**必须**在 `CommandInProgress` + 弹窗护栏下跑，并把"要写盘"这件事**显式要求调用方给路径**
- [ ] **B4-2** idx 173 `hem`（真名 `IFeatureManager::InsertSheetMetalHem2`，**16 形参**）
      ★★ 别家三处错误（成员名零命中 · `hem_type` 把 `Open=0`/`Closed=1` **正好互换** · **漏掉 `Double=4`**）
      ⇒ ★ 裁决书要求做成 **L2/L3 静态断言**（谁再照它抄就当场抓住）
- [ ] **B4-3** idx 181 `intersect`（两步 `PreIntersect2` → `PostIntersect`）
      ★ 唯一要实测的只有 `System.object` 布尔 **SafeArray 的包装**
- [ ] **B4-4** idx 155 `fold`（★ mark 表 `Fold=0/1/4`，**与本批另两条都不同**）
- [ ] **B4-5** idx 205 `model_annotations`（`InsertModelAnnotations4`）★ 复用工程图注解那族的读侧助手

## 收尾

- [ ] **SC-3** 全部 15 件活收口后跑一次**全量** `pytest`（★ 只在发布前 / 改了门禁本体时才跑）
- [x] 更新 `docs/HANDOFF.md`（★ 交接给下一个会话 —— 本版 §一~§五 就是）
