# 规格 204 · 任务清单（tasks）

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
- [ ] **T-504** 批 86：残余补洞（按 FR-006 去重后 +10 ~ 20）
- [ ] **T-505** ★ 每批后复核 SC-001 计数与 SC-002 门禁；★ 到 400 即达 D-1 目标

## T-9 · P4 待定（★ 需先核来源与许可）

- [ ] **T-901** 核 `sw_jlcfa_*` / `sw_gui_*` 的**来源与许可**（是否 vendored 外部插件）
- [ ] **T-902** 若能暴露 ⇒ 按 FR-003 重包装（坐标 → 声明式）后再定；★ 若越许可线 ⇒ **记"不做 + 原因"**

## T-Z · 收尾

- [ ] **T-Z01** 更新 `docs/harvest-report.md`：并入什么、仍空缺什么、为什么
- [ ] **T-Z02** 复核 SC-001 ~ SC-007 逐条
