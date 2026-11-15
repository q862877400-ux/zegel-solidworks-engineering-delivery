# Tasks: 造环节 —— 从需求到可交付模型

**Input**: Design documents from `/specs/354-make-side-generation/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: 按 user story 分组，每条可独立实现与验证。

**落点**：`research/text-to-cad-and-parametric-plugins/proto/`（方法层孵化区，验证通过后整体搬入 `scripts/`）

---

## Phase 1: Setup

**Purpose**: 确认前置条件，不改任何现有代码

- [ ] T001 确认当前 24 条离线测试基线全绿 → 验收: `cd research\text-to-cad-and-parametric-plugins\proto && python -m pytest -q` 输出 `24 passed`
- [ ] T002 [P] 确认 SolidWorks 可连接 → 验收: `python -B tools\guard_run.py --timeout 60 -- python scripts\sw_connect.py --probe` 输出 `VERDICT: OK`
- [ ] T003 [P] 读 `scripts/sw_review.py` 的 `save_review_previews` 签名，确认返回路径列表 → 验收: `Select-String -Path scripts\sw_review.py -Pattern "def save_review_previews" -Context 0,10`

---

## Phase 2: Foundational

**Purpose**: 三个「未解决项」必须先核，否则 execute 写不对

**⚠️ CRITICAL**: 这三条不解决，US4 无法开始

- [ ] T004 核 `mass_properties()["volume"]` 的真实单位（`UNITS` 写 `mm^3`，但函数自述「不做任何换算」）→ 验收: 建一个 10×10×10 的方块，读 volume，若得 1000 则单位确认为 mm³
- [ ] T005 [P] 核 `ForceRebuild3(False)` 是否必须（归档实现调了，但未验不调会怎样）→ 验收: 建齿轮，一次调、一次不调，比较 `solid_body_extent_mm` 结果
- [ ] T006 [P] 核 `save_review_previews` 出的 BMP 还是 PNG（默认 views 是 4 个：isometric/front/top/right）→ 验收: 建一个件跑一次，看 `output\views\` 下文件扩展名

**Checkpoint**: T004-T006 全部有实测结论后，US4 才能开始

---

## Phase 3: User Story 1 - 非专业用户两句话得齿轮 (Priority: P1)

**Goal**: 已有能力，本阶段只做回归确认，不新写

**Independent Test**: `python -m pytest test_gear_method.py -q` → 9 passed

- [ ] T007 [US1] 回归确认 `derive()` 的 13 行参数表输出 → 验收: `python -c "from gear_method import GearRequest, derive, render; print(render(derive(GearRequest(ratio=3.0, center_mm=40.0))))"` 输出含 13 行、六类来源标记、【未覆盖】段
- [ ] T008 [US1] 回归确认无解路径 → 验收: `python -c "from gear_method import GearRequest, derive; d=derive(GearRequest(ratio=3.0, center_mm=30.0)); print(d.ok, d.diagnostics)"` 输出 `False` + 含「最小可行中心距 34」

---

## Phase 4: User Story 2 - 工程师锁定参数 (Priority: P1)

**Goal**: 已有能力，回归确认

**Independent Test**: `python -m pytest test_gear_method.py -q -k pinned` → 1 passed

- [ ] T009 [US2] 回归确认锁定语义 → 验收: `python -c "from gear_method import *; d=derive(GearRequest(ratio=2.5, center_mm=43.0, pin_z1=20)); print([(r.key,r.source) for r in d.rows if r.key in ('z1','m','z2')])"` 输出 z1 来源为 `锁`、m/z2 为 `选`/`算`

---

## Phase 5: User Story 3 - 计划可离线验证 (Priority: P1)

**Goal**: 已有能力；本阶段**改一处**：轮廓点数从 700 降到 200（research §U5）

**Independent Test**: `python -m pytest test_build_plan.py -q` → 8 passed 且草图实体 200

- [ ] T010 [US3] 把 `plan_spur_gear` 的轮廓点数改为按容差反算，默认 5 µm → 200 点 → 验收: `python build_plan.py` 输出「草图实体 200 个」
- [ ] T011 [US3] 确保体积判据跟着变（面积×齿宽，点数变了面积会微变）→ 验收: `python -m pytest test_build_plan.py -q` 8 passed，且 `test_expected_volume_equals_shoelace_times_width` 仍绿
- [ ] T012 [P] [US3] 加一条测试守「点数由容差决定」→ 验收: 新增 `test_point_count_follows_tolerance`，`pytest test_build_plan.py -q` 9 passed

---

## Phase 6: User Story 4 - 计划变成真模型且量得准 (Priority: P1) ★核心

**Goal**: 写 `execute.py` + `verify.py`，让齿轮真机建成，体积偏差 <1%

**Independent Test**: `python execute.py --gear i=3 a=40` → 体积 3064.56±1%、包围盒 22×22×10、三视图 4/4

### 契约测试先行

- [ ] T013 [P] [US4] 写 `test_execute.py` 的前置条件测试（units≠mm / 空实体 / 坐标越界 → 各抛 ValueError）→ 验收: `pytest test_execute.py -q -k precondition` 通过
- [ ] T014 [P] [US4] 写 `test_verify.py` 的判据测试（喂假数据，偏差 0.5% 过、1.5% 不过）→ 验收: `pytest test_verify.py -q -k deviation` 通过

### execute 实现

- [ ] T015 [US4] 写 `execute.py` 的 `FailureRecord` 落盘函数（写 `output/execute_failures/<ts>.json`）→ 验收: 故意抛异常跑一次，文件存在且含 `exception_type`/`stage`/`plan_snapshot`
- [ ] T016 [US4] 写 `execute()` 主体：开草图 → 画线/圆 → 拉伸 → 改名 → rebuild，全程单位按契约表 → 验收: `python execute.py --gear i=3 a=40` 建成，`feature_present(model, "SpurGear_m1_z20")` 为真
- [ ] T017 [US4] 加 `SketchManager.AddToDB` / `DisplayWhenAdded` 的 try/finally 还原 → 验收: 跑完后读这两个属性，与原值一致
- [ ] T018 [US4] 异常分支：失败必须落 FailureRecord 并尽力导现场 PNG → 验收: 喂一个坐标越界的 plan，`output/execute_failures/` 下有 json

### verify 实现

- [ ] T019 [US4] 写 `verify.py` 的 `Verification` dataclass（字段按 data-model.md §4）→ 验收: `python -c "from verify import Verification; print(Verification.__dataclass_fields__.keys())"` 含 9 个字段
- [ ] T020 [US4] 实现体积比对（用 `mass_properties`，不用 `IFeature.GetBox`）→ 验收: 真机跑一次，`volume_deviation_pct` 有值且 <1.0
- [ ] T021 [US4] 实现包围盒比对（用 `solid_body_extent_mm`）→ 验收: 真机跑一次，`bbox_deviation_mm` 三个都 <0.5
- [ ] T022 [US4] 实现三视图导出（用 `save_review_previews`）→ 验收: `output\views\` 下 4 个文件非空
- [ ] T023 [US4] 三条判据合成 `ok`，失败时 `failure` 按 `; ` 拼接不掩盖 → 验收: 喂偏差 3% 的假数据，`ok=False` 且 `failure` 非空

### 端到端

- [ ] T024 [US4] ~~真机跑齿轮全流程~~ → **作废**：该判据针对的 `plan_spur_gear` 是折线模拟渐开线，按业主 2026-11-07 令删除（AGENTS.md 十四之五）。齿轮族无可用生成器，本任务不再有验收对象。
- [ ] T025 [US4] **人工目视三视图**（看悬空草图/缺面/齿形）→ 验收: 报告里写「已目视，无异常」或「未目视」（不许写「自动过了=验收过了」）

**Checkpoint**: T024 通过 = **造环节成立**

---

## Phase 7: User Story 5 - 第二族证明骨架可复制 (Priority: P2)

**Goal**: 写 `shaft_method.py`，用同一套 FeaturePlan + execute + verify

**Independent Test**: `python execute.py --shaft T=120 L=300` → 体积偏差 <1%

- [ ] T026 [P] [US5] 写 `shaft_method.py` 的 `ShaftRequest` 与 `derive_shaft()`（扭转强度算轴径）→ 验收: `python -c "from shaft_method import ShaftRequest, derive_shaft; d=derive_shaft(ShaftRequest(torque_nm=120.0, length_mm=300.0)); print(d.ok, d.d1_mm, d.d2_mm)"` 输出 `True 28.0 40.0`
- [ ] T027 [US5] 写 `plan_shaft()`：旋转体轮廓（**不是**闭合轮廓拉伸，原语 2）→ 验收: 输出 `FeaturePlan` 且 `features[0]` 是 `Revolve` 而非 `Extrude`
- [ ] T028 [US5] 扩 `execute()` 支持 Revolve（复用 `sw_part` 的旋转函数）→ 验收: `feature_present(model, "Shaft_d28_L300")` 为真
- [ ] T029 [US5] 真机跑轴全流程 → 验收: `python -B tools\guard_run.py --timeout 400 -- python -B "research\text-to-cad-and-parametric-plugins\proto\execute.py" --shaft T=120 L=300` 三条判据全绿
- [ ] T030 [US5] 量代码改动比例，确认 <30% → 验收: `git diff --stat` 相对齿轮族新增行数，轴族 <30%

**Checkpoint**: 两族都过 = 抽象成立

> ⚠ **2026-11-07 状态**：轴族已真机通过（体积 300084.9 / 预期 300084.93 = 偏差 0.00%，
> 包围盒 40×300×40 三向 0.000，三视图 4/4）。**齿轮族已作废**：其生成器 `plan_spur_gear`
> 是折线模拟渐开线，按业主 2026-11-07 令删除（AGENTS.md 十四之五），齿轮族回到
> stitched 且**不得**再升 verified。本 spec 的「两族都过」判据需由业主重新界定。

---

## Phase 8: User Story 6 - 标准号现行版 (Priority: P2)

- [ ] T031 [US6] 清掉 `research/.../_evidence/scan/_recheck.py` 的三处**脚本缺陷**（不是数据错）→ 验收: `python -B research\text-to-cad-and-parametric-plugins\proto\recheck.py` 输出的「错误」逐条给出现行替代号，且行标（JB/T）如实标「无检索入口」而不是判失败
- [ ] T032 [P] [US6] 把 `recheck.py` 抽成可被 execute/derive 调用的小函数 → 验收: `python -c "import sys; sys.path.insert(0,'research/text-to-cad-and-parametric-plugins/proto'); from recheck import assert_current; assert_current('GB/T 1356')"` 不抛异常

---

## Phase 9: Polish

- [ ] T033 [P] 更新 `research/.../README.md` 的 proto 文件表（加 execute/verify/shaft_method）→ 验收: 文件表 8 行
- [ ] T034 [P] 写 `15-造环节验证报告.md`（L3 数值 + L4 目视结论 + 未覆盖项）→ 验收: 文件存在，含实测体积与偏差
- [ ] T035 跑完整 quickstart 六个场景 → 验收: 六个场景的判据全绿（人工目视那项如实标注）
- [ ] T036 ~~若 T024 通过：更新 `capabilities.yaml` 的 `external_spur_gear_geometry` 为 `verified`~~ → **作废**：齿轮族生成器是折线实现，按业主 2026-11-07 令删除；该条保持 `stitched` 并在 limitations 首条写明「没有可用实现」，**不得升 verified**。→ 新验收: `python -c "import json,io; d=json.load(io.open('capabilities.yaml',encoding='utf-8')); c=[x for x in d['capabilities'] if x['id']=='external_spur_gear_geometry'][0]; assert c['level']=='stitched'; assert '折线' in c['limitations'][0]"` 不抛异常

---

## Dependencies

```
Phase 1 Setup
  ↓
Phase 2 Foundational (T004-T006)  ← 阻塞 US4
  ↓
Phase 3/4/5 (US1/US2/US3)  可并行，都是回归
  ↓
Phase 6 (US4) ★核心  ← 没有它，整个特性不成立
  ↓
Phase 7 (US5)  ← 证明抽象
  ↓
Phase 8 (US6)  可并行
  ↓
Phase 9 Polish
```

## Parallel Opportunities

| 组 | 任务 | 为什么不冲突 |
|---|---|---|
| A | T013 / T014 | 两个不同测试文件 |
| B | T026 / T031 / T033 / T034 | 不同文件，不同族 |
| C | T004 / T005 / T006 | 三条独立验证 |

## MVP 定义

**MVP = Phase 1 + Phase 2 + Phase 6（T024 通过）。**

这 24 条之外的核心新增是：`execute.py` + `verify.py` + 真机跑通一次齿轮。

**其余（US5 轴族、US6 国标、Polish）都是加固。**

## 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| T004 单位判断错 | 体积偏差算错，全盘误判 | 用 10×10×10 方块做基准 |
| T005 rebuild 必须但没调 | 体积读到旧值 | 两条都跑，比对 |
| 真机 COM 死锁 | 卡住整个流程 | 全程 `guard_run.py` 包裹 |
| 中文路径 | SW 丢文件 | 中间文件落 ASCII 临时目录 |
| 200 点精度不够 | 体积偏差 >1% | 点数按容差可调，必要时回 400 |

## 统计

- **总任务**：36
- **US1** 2 · **US2** 1 · **US3** 3 · **US4** 13 · **US5** 5 · **US6** 2
- **Setup** 3 · **Foundational** 3 · **Polish** 4
- **可并行**：8 条
