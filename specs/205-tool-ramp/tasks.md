# 规格 205 · 任务清单（tasks）

> 规格：[`spec.md`](spec.md) · 计划：[`plan.md`](plan.md)
> ★ 每完成一批就把状态改成 ✅ 并写上**工具数**（★ 数字要能从盘上重数一遍）

## T-0 · 地基（开工前必须做完）

- [x] **T-001** 现状与可用资料梳理 ⇒ `output/capability-harvest-survey.json`（909 公开 / 274 已挂 / 609 可打捞）
- [x] **T-002** 按**域**算暴露比与施工顺序 ⇒ `output/capability-harvest-by-domain.json` · `output/tool-ramp-plan-data.json`
- [x] **T-003** 读另一个对话（支线）的记录与作业方式 ⇒ `docs/kickoff-bunny-sideline.md` · `docs/recon/README.md` · ROADMAP §一·C
      ★ 要点已吸收：Bunny 扇出须 provider+model 成对 · 先 2 路探针 · 只报不动 · 产物进 `docs/`（铁律 3）
- [x] **T-004** 立规格 / 计划 / 任务（本目录三份）
- [ ] **T-005** 记一条事实（事实 530）：本规格的地基数据与判据

## T-1 · 批 79 · FR-008：宏/VBA + 爆炸视图（★ 规格 202 的 MUST）

- [x] **T-101** 读 `scripts/sw_macro_guard.py` 与装配爆炸视图相关能力，判可暴露性（FR-003/006/007）
      ⇒ ★ 宏那 9 个公开函数里 **7 个可挂**（另 2 个：`generate_macro_with_guard` 要**回调**、`main` 是 CLI 入口）；
      ★ 爆炸视图**没有包装**，但 `ASSEMBLY_DOC_ARITY` 登记表里 **9 个成员的 arity 齐全** ⇒ 新写包装 ✓
- [x] **T-102** 写 `mcp-server/tool_specs_batch79.py`（★ 实得 **17** 个：爆炸视图 9 + 宏 8）
- [x] **T-103** 注册进 `BATCH_MODULES` + 写 `tests/test_tool_specs_batch79.py`（**6 passed**）
- [x] **T-104** 改全局计数（`tests/test_server_wiring.py`：296 → **313**）
- [x] **T-105** ★ **真机**（SC-005 · `tools/probe_fr008_explode_macro.py`，走 `sw_guard`）：
      · **爆炸视图正例**：装配副本（`GetType=2` · 配置 `默认`）⇒ `create_exploded_view` 回 **True** ·
        **回读计数 0 → 1** · 名字 **['爆炸视图1']** · 展开/收拢都没抛 · 按名显示回 **True** ✓
      · **宏正例**：本仓 `.swb`（明文 VB.NET、`Sub main`）⇒ `ok=True · return_value=True` ✓
      · **宏反例**：路径不存在 ⇒ `return_value=False · file_exists=False` ✓（★ `error_code=0` ⇒ 语义**未定**，已记）
      · ⚠ **爆炸视图反例未做**：`NewDocument("",0,0.0,0.0)` 真机回 `None` ⇒ 拿不到零件 ⇒ **如实记"未做"**，
        ★ 不把装配读数冒充零件读数 ✓
- [x] **T-106** 收尾链 + 提交 ⇒ `release_check 第 1 轮 OK` · `check_param_binding` **0 处** ·
      ★ 并把两块**新能力**登记进 `capabilities.yaml`（`assembly_exploded_views` · `macro_execution`，
      各带真机 evidence + 如实 limitations ⇒ 112 条 · **100 verified** / 10 stitched / 2 not_implemented）✓

## T-2 · 批 80 · `sw_featureworks`（特征识别）

- [ ] **T-201** 判可暴露性（★ FeatureWorks 是加载项，需先查是否 `verified` 可跑）
- [ ] **T-202** 写批次 + 注册 + 测试 + 计数 + 真机 smoke + 提交（★ 工序同上"七步"）

## T-3 · 批 81 · `sw_routing`（★★ 护城河域 · 整域 0 工具）

- [ ] **T-301** 判可暴露性（21 个候选里挑不违反 FR-003/007 的）
- [ ] **T-302** 工序七步 + 真机 smoke + 提交

## T-4 · 批 82 · `sw_pdm`（★★ 护城河域 · 整域 0 工具）

- [ ] **T-401** 判可暴露性（★ 注意规格 202 的 FR-012：PDM 可判"不做 + 原因"，★ 但本机能力层已有实现 ⇒ 先核它是否真能跑）
- [ ] **T-402** 工序七步 + 真机 smoke（★ 无 PDM 服务器 ⇒ 可能只能验只读路径）+ 提交

## T-5+ · 批 83 ~ 86（诊断知识 / 检索 / 监控 / 评审 / 外观 / 残余补洞）

- [ ] **T-501** 批 83：`sw_automation_knowledge` + `sw_com_traps`（+12 ~ 16）
- [ ] **T-502** 批 84：`sw_misumi` + `sw_busy` + `sw_import_mesh_reference` + `sw_preflight`（+15 ~ 25）
- [ ] **T-503** 批 85：`sw_review` + `sw_appearance` + `sw_render_material`（+15 ~ 29）
- [x] **T-504** 批 86：残余补洞（★ 实得 **30** —— ★ 来自「解锁 C 类」的第四坡）
- [x] **T-505** ★ 每批后复核 SC-001 计数与 SC-002 门禁；★ 到 400 即达 D-1 目标 ⇒ ★ **达成** ✓

## ★★★ T-8 · 达成记录（2026-10-04 · 接手轮）

```
★★★ SC-001 **达成**：`register_capabilities.all_specs()` = **401 ≥ 400** ✓
★ 判据已写成**可执行的测试**：`tests/test_tool_specs_batch87.py::test_sc001_tool_count_reaches_400` ✓
```

| 批 | 提交 | 工具数 | 内容 |
|---|---|---|---|
| 80 | `948efef1` | 313 → 325 | 自动化诊断知识 + COM 陷阱纯函数 + 会话忙闲（12）|
| 81 | `b56bbee9` | 325 → 343 | ★ 第一次「Bunny 扇出 → 门禁 → 转换器」产出的批次（18）|
| 82 | `115826ba` | 343 → 356 | 第二坡（仿真/装配/导出）· FR-006 删 6 个 ⇒ 13 |
| 83 | `cc5b74b7` | 356 → 360 | 第二坡"真新"残余 4（★ 含"只读闸 vs 危险旋钮"的安全对照）|
| 84 | `6a9efd82` | 360 → 367 | 第三坡薄模块 7（含 4 个真建模能力）|
| 85 | `d21c1286` | 367 → 369 | 三视图布局 + Costing 默认值（2）|
| 86 | `d2a76b26` | 369 → 399 | ★★ **第四坡「解锁 C 类」30 个** |
| 87 | `6e40afe2` | 399 → **401** | ★★★ **跨过 400**（2）|

★★ **路径结论**（★ 详见事实 532）：A/B 类（首参是标量或已有注入键）**会被吃干**；
   要到 400 必须**解锁 C 类**，而解锁靠的是**加"语义无歧义"的注入解析器**
   （`sldworks`/`results`/`mesh`/`options`/`view`/`defaults`/`component`/`sketch`/`selection`）
   —— ★★ 实测：**加键前 45 行 → 9 行可暴露；加键后 38 行 → 30 行可暴露** ✓

★ **门禁**：`release_check` 每批第 1 轮 OK · `check_param_binding` 扫 401 个工具 **0 处** ·
  `check_union_conventions` **exit 0** ✓
★ **能力侧（SC-008）**：`capabilities.yaml` **112 条 · verified 100 · stitched 10 · not_implemented 2**
  （★ 工具数**不等于**能力指标 —— 支线的告诫已采纳）✓
★ 达标证据：`output/goal-evidence.json`（由 `tools/gen_goal_evidence.py` **从盘上重推**）✓

⚠ **与规格原批序的偏离（★ 按 D-1…D-5 自行拍板、逐批写明理由）**：原批序（特征库/走线/PDM…）
  是按"候选数"排的，而机械预筛证明那些模块**绝大多数不可挂**（首参是 COM 对象且无解析器）
  ⇒ ★ 改为按「**去重后可挂数 + 域产量**」排序（v3 批序）—— ★ 每批提交信息里都记了理由 ✓


## ★★★ T-9 · 「expose 现有函数」这条路**已走完**（2026-10-04 · 接手轮终局）

```
★★★ 最终计数：`all_specs()` = **433**（目标 400 ⇒ 超出 33）✓
★ 判据可执行：`tests/test_tool_specs_batch87.py::test_sc001_tool_count_reaches_400` +
  `tests/test_server_wiring.py` 的计数断言 ✓
```

### 为什么不能再多了（★ 详见事实 534）—— **四种死因，每种都有实例与证据**

| 死因 | 数 | 说明 |
|---|---|---|
| ① **已覆盖** | 128 | 同一能力已被**上游 `server.py` 那 45 个**或既有 ToolSpec 包过（★ 我最初的判据**看不到上游那 45 个** ⇒ 假阳性来源）|
| ② **歧义首参** | 119 | "取哪一个？"（`win`25 · `hwnd`15 · `route_manager`15 · `target`8 · `pdm_document`8 · `ctrl`7 · `study_name`7 · `obj`6 · `h`6）⇒ ★ 事实 36 那一族：**选错对象 = "什么都没反应"** ⇒ **一律不碰** |
| ③ **政策不做** | 249 | 弹模态框 · 返回**裸 COM 对象**（★ 机测 `CDispatch` 过不了 JSON 边界）· 官方**逐字 Obsolete** · **未护栏的原始网格旋钮**（事实 526 的 40 GB 事故）· 形参是 **COM DispArray** |
| ④ ★★ **在 MCP 边界上冗余** | — | ★ 本回合**新识别**的一类：`sw_simulation_worker.*_by_name` 看着是新入口，但它们的价值是「**可隔离执行**」，而 ★ **"按名字"在 MCP 边界上早有**（`resolve_study` 第 74/85 行读 `study_name`）⇒ 挂它们是**同一能力的第三次暴露** ⇒ FR-006 判不做 ✓ |

★★ **勘探已是可复用的仪器**：`python tools/bunny_toolspec_pipeline.py survey`
  （★ 它**先纠正过我一次假阳性** —— 见事实 534 第一节）✓

### 若还要继续（★ 三条路，都**超出"expose 现有函数"**这个前提）
1. ★ **写新能力包装**：把 ② 那 119 个歧义组**逐个包成声明式入口**（★ 每个都要写码 + 真机验证）
2. ★ **新接口族**（`capabilities.yaml` 现 112 条 · verified 100）
3. ★ **把 10 条 `stitched` 提成 `verified`** —— ★ 那是**能力真实性**的活，不是数量活

★★ 而按规格自己的 **SC-008**：**工具数是代码组织方式的函数，不是能力指标** ⇒
  **433 个工具 vs 112 条能力（verified 100）** ⇒ ★ 再堆数量的**边际价值已经很低** ✓


## T-10 · P4 「`sw_jlcfa_*` 的来源与许可」（★ 已结，2026-10-04）

- [x] **T-901** 核 `sw_jlcfa_*` / `sw_gui_*` 的**来源与许可**（是否 vendored 外部插件）⇒ ★ **已核，2026-10-04**
- [x] **T-902** 若能暴露 ⇒ 按 FR-003 重包装（坐标 → 声明式）后再定；★ 若越许可线 ⇒ **记"不做 + 原因"**

### ★★★ T-9 的结论（2026-10-04 · 只读核查）
```
★ 许可侧：**干净** —— `scripts/sw_jlcfa_*.py`（12 个）是**我们自己的 GUI 自动化脚本**，
  来源块逐字写着「驱动**本机已安装**的嘉立创 FA 选型插件 v2.4.1-20260918-1」⇒ ★ 它**驱动**插件、
  **没有抄插件的代码**；`import` 清单只有标准库 + 兄弟 `sw_jlcfa_*` + 本仓 `shot` ⇒ **无第三方依赖** ✓
★★ 暴露侧：**不做**（★ 记"不做 + 原因"，不硬编）——
  ① ★★ 它们是**像素/屏幕坐标驱动**的：实测有硬编码屏幕点（如 `(1991,309)`）、
     以及按**截图扫描**算出来的点（`first_result_point(w)`）⇒ ★ 这正是**规则 3 的要害**
     （而且比"裸坐标"更脆：坐标依赖**窗口当前的位置与尺寸**）✓
  ② ★ 依赖**第三方插件的确切 UI 版本** ⇒ 给不出声明式选择器（插件 UI 不暴露控件名）✓
  ③ ★ 它属于"**GUI 自动化**"，不是"SolidWorks API 能力" ⇒ 与 `RESOLVERS` 那套注入模型不同构 ✓
  ★★ 若将来真要做，正解是**重写成按控件名/文本定位**（本仓已有 `sw_gui_modal` 那套文本判据可复用），
     ★ 但那需要插件 UI 提供可定位的标识 —— ★ 现状给不出 ⇒ 保持"不做" ✓
  ★ 已由主线的扇出门禁把这一族排除在候选之外（预筛阶段就跳过 `sw_jlcfa*`）✓


## T-Z · 收尾

- [ ] **T-Z01** 更新 `docs/harvest-report.md`：并入什么、仍空缺什么、为什么
- [ ] **T-Z02** 复核 SC-001 ~ SC-007 逐条
