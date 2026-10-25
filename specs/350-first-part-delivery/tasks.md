# Tasks: S2–S6 — 首件交付族

**Feature**: `350-first-part-delivery`

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

**前置**：`specs/348-s0-restore-official-path/` 与 `specs/349-e1-e7-acceptance/` 必须已完成。

---

## ★ 本清单的勾选口径（2026-10-25 第 24 轮重写）

这份清单在到第 23 轮为止**一个勾都没打**，而实际上 T007/T008/T011 早已有真机证据。
同时多条 `→ 验收:` 指向 `tests/test_stage4_planner.py` —— 那个文件测的是**规划器**
（IR 码表 / 歧义 / 域外 / 量级荒谬），**与建模与回读类任务无关**。

⇒ 本轮按「验收必须真能验它」重写每条验收，并按证据打勾。勾选口径：

| 标记 | 含义 | 要求 |
|---|---|---|
| `[x]` | **已完成** | 必须有真机读数或通过的测试，且写在验收里 |
| `[~]` | **部分完成** | 机制通了但有明确的未达项，写清差什么 |
| `[ ]` | 未完成 | — |
| `[!]` | **阻塞** | 卡在外部输入或已知工具链退化，写清卡点与依据 |

★ `[~]` 与 `[!]` **都不是通过**。本仓不接受「差不多」。

---

## Phase 1: S2 — 冻结首件需求与最小规则包

- [!] **T001** [US1] 建首件需求冻结表：功能/接口/主参数/可修改域/材料/工艺/图样/交付目的
  → 验收: `python -B -m pytest tests/test_first_part_requirements.py -q`
  → **阻塞**：表已建、判据已可跑，但**八项全部未定**（`specs/350-first-part-delivery/requirements.md`）。
    按 `ENGINEERING-PATH` 第 85 行「不得偷偷填默认值」，必须由工程负责人给。
    **待你回答的问卷**：`specs/350-first-part-delivery/s2-question-sheet.md`

- [!] **T002** [US1] 每条硬要求标注执行承担者与验收承担者；缺一即红
  → 验收: `python -B -m pytest tests/test_first_part_requirements.py -q`
  → **阻塞**：依赖 T001（没有要求就没有承担者可标）

- [ ] **T003** [US1] 从需求倒推最小规则集合（不搬整个标准库）
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`
  → 规则倒推需要 T001 的要求作为输入，当前无输入可倒推

- [ ] **T004** [US1] 规则登记 → 参数输入 → 计算/检查 → 引用 → 验收结果的闭环
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`（规划器侧已测）；闭环另一端依赖 T001

- [~] **T005** [US1] 消除关键参数的静默默认值；缺失必须提问
  → 验收: `python -B -m pytest tests/test_stage4_planner.py tests/test_s2_shape_problems.py -q`
  → **部分完成**：缺项只报不填（`missing_confirmations`）+ 形状不可核也报（`shape_problems`）已落地；
    但需要 T001 的实际值才能验证「填了就不该再问」

- [ ] **T006** [US1] 换材料/工艺/规则版本时旧批准失效
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`
  → 依赖 T001（没有冻结版本就无从失效）

## Phase 2: S3 — 板件真过 E1–E3

- [x] **T007** 按铁律 4 三源互证查清 E1 所需的草图求解状态成员，查不到即停线
  → 验收: `python -B -m pytest tests/test_acceptance_e1_enum.py -q`
  → **已完成**。成员是 **`ISketch.GetConstrainedStatus()`**（不是 `GetSketchState`，
    那条是原清单写错的）；三源互证（`C:\swapi` + CHM + 出厂反射）通过；
    真机读数 2=欠定义 / 3=完全定义已实测。
  → 证据：`specs/349-e1-e7-acceptance/coverage.md` · `docs/state/facts/R-engineering-path.md` R-19

- [~] **T008** [US2] 板件改为尺寸与关系驱动：位置/方向/大小完整约束，不得全固定
  → 验收: `python -B -m pytest tests/test_acceptance_e1_enum.py -q` + 真机 `tools/probe_s3_t008_dimension_driven.py`
  → **部分完成**。已验成：`AutoDimension2(1,1,-1,1,-1)` 能加驱动尺寸（状态 2→3）、
    改尺寸真的改几何（包围盒 100→120 mm）、E1 判据能拒「全固定」（状态 3 + 零驱动尺寸 ⇒ fail）。
    **未达**：只有 1 个尺寸（宽度），高度与孔位都不是参数。
  → 证据：`specs/350-first-part-delivery/s3-t008-dimension-driven.md`

- [~] **T009** [US2] 主尺寸/基准/孔位建立稳定语义引用，跨重建不依赖选区或下标
  → 验收: `python -B -m pytest tests/test_semantic_selection.py -q`
  → **部分完成**。语义选择器（`+x`…`-z` / `top_face` / `near:x,y,z`）已接进 `resolve_entity`；
    `planner.py` 三处 `index:0` 待换成语义选择器。
  → **阻塞在需要你定的那件事**：倒角倒**哪条**边（外轮廓 / 四条竖边 / 其他）；轴类倒**哪端**。
    多边支持也要定（`resolve_entity` 只选一个实体，而板有 12 条边）。

- [~] **T010** [US2] 孔型/孔位逐项回读，不只比较总切除体积
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q` + 真机 `tools/run_s3_acceptance.py`
  → **部分完成**。已接进验收运行器并真机跑通：
    **孔数 4/4 相符**、**孔径与孔位 4/4 逐项通过**（位置容差 0.1mm、孔径容差 0.05mm）。
    **第 28 轮更新**：孔已换成**异型孔向导**生成 ⇒ 孔型**测到了**
    （`hole_params` → `Type=25 / EndCondition=1`）⇒ 判据从 `unknown` 变成 **`fail`**，
    原因不再是「测不到」，而是「**要求里的孔型为空**」。
    ★ 真正的缺口因此变成 **S2 的 `interface` 未冻结**（要求什么孔型未知）。
      拿实测值回填 `requested` 是循环论证（产物当要求），不做。
  → 根因是**生成方式**不是 API：孔是**切除-拉伸**做的（E3 读到 `type=ICE`），
    而孔型只存在于**异型孔向导**特征的参数里。`hole_wizard` / `feature_hole_wizard5`
    都是 verified ⇒ 有路，但要改 `build_plan()` 并重跑 E1/E2/E3 三条证据（单列一轮）。
  → 证据：`specs/350-first-part-delivery/s3-t011-edit-delivered.md` 第九节

- [~] **T011** [US2] 在**已交付件副本**上改板宽 100→120，孔位联动、特征无错、保存重开仍成立
  → 验收: `python tools\sw_guard.py --timeout 300 -- python tools\probe_t011_edit_delivered_plate.py`
  → **部分完成，三条达标一条不达标**：
    ✅ 改已交付件 · ✅ 保存真的落盘（sha 变） · ✅ 保存重开仍成立（100→120→120）
    ❌ **孔位联动**：孔心位移 `[0,0,0,0]`（期望 +20）⇒ **E2 判 fail**
  → 证据：`specs/350-first-part-delivery/s3-t011-edit-delivered.md` 第八节更正

- [~] **T012** [US2] E1–E3 名义件与扰动件三态全绿
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q` + 真机 `tools/run_s3_acceptance.py`
  → **2 绿 1 红**：E1 pass · E3 pass · **E2 fail**（孔未随板宽变化）
  → 机器生成的报告：`specs/350-first-part-delivery/s3-acceptance.md`（总体 fail）

- [ ] **T013** [US2] 同步做 E5 最难的一个必需尺寸/基准标注小验证（避免等装配后才发现 API 到不了）
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_drawing_tools_e2e.py`
  → 未做。★ 而且**先要避开已退化的一族**：新建尺寸（`AddDimension2` / `AddHorizontalDimension2`）
    本机崩进程（事实 560）⇒ E5 的标注验证要么等环境恢复，要么另找入口

## Phase 3: S4 — 装配、图样、工艺

- [!] **T014** [P] [US3] 装配有地件、有功能配合；回读配合目标与实际剩余运动
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q`（判定器侧）
  → **阻塞**：`IAssemblyDoc.AddComponent5` 回 `None`，三种前置已排除（路径可见 / 文档类型=2 /
    已保存），加不进组件 ⇒ 装配建不出来，配合无从谈起
  → 证据：`specs/350-first-part-delivery/s4-assembly-blocked.md`

- [!] **T015** [P] [US3] 干涉检查与关键间隙，从实际几何取数
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q`（判定器侧）
  → **阻塞**：依赖 T014。判定器本身是好的（要求 `mates ≥ 1`，空装配判 fail）

- [ ] **T016** [US3] 必要标注清单由功能/制造/检验要求生成，逐项绑定真实图纸对象
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q`（判定器侧）
  → 判定器已有；真机侧依赖 T001（图样范围未定）与 T013（标注 API 退化）

- [ ] **T017** [US3] 移除 `drawing_run` 写死的材料与公差文字，改为取批准需求
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`
  → 依赖 T001（没有批准需求可取代写死值）

- [ ] **T018** [US3] 用冻结工艺检查实际几何；不能机器判的部分列人工义务及签核
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py -q`（判定器侧）
  → 依赖 T001（工艺路线未定）

- [ ] **T019** [US3] 原生重开全套文件，核关联、BOM、标注与实际 PDF 版面
  → 验收: `python tools\sw_guard.py --timeout 600 -- python tools\probe_drawing_tools_e2e.py`
  → 依赖 T014/T016

- [ ] **T020** [US3] E1–E7 全部适用义务有实证；E4/E6 不得靠列「不适用」通过
  → 验收: `python -B -m pytest tests/test_acceptance_e1_e7.py tests/test_acceptance_contract.py -q`
  → 当前 E4 阻塞、E5/E6 未跑

## Phase 4–5: S5 / S6

> ⚠ 以下两个 phase 的任务**未在本轮改动**（原文保留）——
> 它们的前置（S2 冻结 / S3 全绿 / S4 装配）都还没通，现在改验收指向没有意义。

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
