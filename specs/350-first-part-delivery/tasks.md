# Tasks: S2–S6 — 首件交付族

**Feature**: `350-first-part-delivery`

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

**前置**：`specs/348-s0-restore-official-path/` 与 `specs/349-e1-e7-acceptance/` 必须已完成。

## Phase 1: S2 — 冻结首件需求与最小规则包

- [ ] **T001** [US1] 建首件需求冻结表：功能/接口/主参数/可修改域/材料/工艺/图样/交付目的
  → 验收: `python -B -c "import io; print(len(io.open('specs/350-first-part-delivery/requirements.md',encoding='utf-8').read()))"`

- [ ] **T002** [US1] 每条硬要求标注执行承担者与验收承担者；缺一即红
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T003** [US1] 从需求倒推最小规则集合（不搬整个标准库）
  → 验收: `python -B -c "import sys; sys.path.insert(0,'scripts'); from engineering.rules import list_rules; print(len(list_rules()))"`

- [ ] **T004** [US1] 规则登记 → 参数输入 → 计算/检查 → 引用 → 验收结果的闭环
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T005** [US1] 消除关键参数的静默默认值；缺失必须提问
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T006** [US1] 换材料/工艺/规则版本时旧批准失效
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

## Phase 2: S3 — 板件真过 E1–E3

- [ ] **T007** 按铁律 4 三源互证查清 E1 所需的草图求解状态成员，查不到即停线
  → 验收: `python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" member ISketch GetSketchState`

- [ ] **T008** [US2] 板件改为尺寸与关系驱动：位置/方向/大小完整约束，不得全固定
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T009** [US2] 主尺寸/基准/孔位建立稳定语义引用，跨重建不依赖选区或下标
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T010** [US2] 孔型/孔位逐项回读，不只比较总切除体积
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T011** [US2] 在**已交付件副本**上改板宽 100→120，孔位联动、特征无错、保存重开仍成立
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_feature_edit_e2e.py`

- [ ] **T012** [US2] E1–E3 名义件与扰动件三态全绿
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q -k "e1 or e2 or e3"`

- [ ] **T013** [US2] 同步做 E5 最难的一个必需尺寸/基准标注小验证（避免等装配后才发现 API 到不了）
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_drawing_tools_e2e.py`

## Phase 3: S4 — 装配、图样、工艺

- [ ] **T014** [P] [US3] 装配有地件、有功能配合；回读配合目标与实际剩余运动
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_mate5_vs_createmate.py`

- [ ] **T015** [P] [US3] 干涉检查与关键间隙，从实际几何取数
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_pin_asm_component_faces.py`

- [ ] **T016** [US3] 必要标注清单由功能/制造/检验要求生成，逐项绑定真实图纸对象
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T017** [US3] 移除 `drawing_run` 写死的材料与公差文字，改为取批准需求
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T018** [US3] 用冻结工艺检查实际几何；不能机器判的部分列人工义务及签核
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T019** [US3] 原生重开全套文件，核关联、BOM、标注与实际 PDF 版面
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_drawing_tools_e2e.py`

- [ ] **T020** [US3] E1–E7 全部适用义务有实证；E4/E6 不得靠列「不适用」通过
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

## Phase 4: S5 — 真实 DeepSeek 端到端

- [ ] **T021** [US4] 把工程服务接入当前宿主；真实模型接收需求、补问、产出结构化提议
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T022** [US4] 受控高层入口：提议/校验需求、列方法、编译计划、执行已批准版本、查状态与证据
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T023** [US4] 同义/歧义/缺项/域外四类表达的理解测试
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T024** [US4] 计划冻结后改参数/改文件/换配置/取消/断网/超时/保存失败的处置
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T025** [US4] 人工接管单独记录，不藏在成功率里
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T026** [US4] 一个真实自然语言任务通过完整链并交付首件
  → 验收: `python tools\sw_guard.py --timeout 900 -- python tools\probe_feature_edit_e2e.py`

## Phase 5: S6 — 限定发布

- [ ] **T027** [US5] 发布说明写明支持的参数域、工艺、SW 版本/配置、规则包版本、人工审核条件
  → 验收: `python -B -c "import io; t=io.open('specs/350-first-part-delivery/release.md',encoding='utf-8').read(); print(all(k in t for k in ['参数域','工艺','版本','规则包','审核']))"`

- [ ] **T028** [US5] 超出已发布参数域的请求被拒绝，不勉强生成
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T029** [US5] 规则/方法升级能识别受影响交付并使旧证据失效
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T030** [US5] 干净环境复现（安装/恢复/交付）
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

## Phase 6: 收口

- [ ] **T031** 首件 E1–E7 状态表 + 证据清单 + 人工批准记录
  → 验收: `python -B -c "import io; print(len(io.open('specs/350-first-part-delivery/acceptance.md',encoding='utf-8').read()))"`

- [ ] **T032** 发布门禁仍绿
  → 验收: `python -B scripts/release_check.py`

## Dependencies & Execution Order

- **前置**：348 与 349 必须完成
- Phase 1（S2）→ Phase 2（S3）→ Phase 3（S4）→ Phase 4（S5）→ Phase 5（S6）**严格串行**
- 所有真机任务串行，不并发控制同一 SolidWorks 会话
- Phase 3 内 T014/T015 可并行（只读探测）

## 停线条件（遇到就停，不自行拍板）

1. E1 所需的草图求解状态取不到
2. 主参数改动不联动
3. 只能导入实体而无编辑历史
4. 必需图样绑定不可实现
5. 图纸只能导出但核不了语义
6. 工艺无法说明
7. 引用原文缺失

## 明确不做

- 不把 E4/E6 列「不适用」来通过 S4
- 不用「新建另一份相同外形模型」冒充 E2/E3
- 不用测试脚本代填工具序列冒充 S5
- 不写「机械设计全覆盖」
- 不杜撰任何 SolidWorks 成员名
