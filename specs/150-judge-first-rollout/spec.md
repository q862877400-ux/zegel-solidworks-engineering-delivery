# 150 · 判据优先（judge-first）· spec

> ★ **本文是规格**：需求带来源，任务带 `→ 验收:`。作业单在 `docs/plan-200r-v3.md`。
> ★ 承接：`docs/plan-24h-v2-convergence.md` 的 §五（下一步）与 §二（没做成的）。

## 一、需求（★ 每条带来源）

| # | 需求 | 来源 |
|---|---|---|
| **R1** | ★★ **判据本身必须先被验**：凡"用某个回读去判某条能力"的探针，**必须先在已知成功的场景上**证明该回读能复现 `0→1`（或等价的正向信号） | ★ 上一轮五次事故（`known-facts.md` 事实 **320 / 323 / 329 / 330 / 332 / 333 / 334**）· 作业单 §三 硬约束 ⑪⑫ |
| **R2** | ★ 该纪律要**工具化**（不是只写在事实里）—— 并**接进门禁** | ★ 本仓既有的「把验证责任转移到静态比对」；★ 参照第 20/21 道门禁的做法 |
| **R3** | ★ **B 组两条连接件**（`link_connector` / `rigid_connector`）在**新判据下**若成 ⇒ 注册 | `plan-24h-v2-convergence.md` §二「没做成的」最后一行 · 事实 332 |
| **R4** | ★ **焊件族** `create_structural_member` 的完整链（型材文件 + 草图线段组），判据用**特征树** | 作业单 §一 段 2 · `scripts/sw_weldment.create_structural_member` |
| **R5** | ★ `scripts/sw_selection_tx.py` 的**残骸决断**：查那四个名字在**官方 API** 里是否存在 ⇒ **补全或删除**（二选一，写清依据） | 事实 316 的 `KNOWN_BROKEN` 登记 · `tools/check_undefined_names.py` |
| **R6** | ★ 剩余该挂**分批**清理（`sw_export` 6 条等），每批五件套 + **判据前置声明** | `plan-200r-v3.md` §一 段 4 · `output/real-gap-triage.json` |
| **R7** | ★ **收敛报告 v2**，数字**全从生成物**来 | `plan-200r-v3.md` §五 W7 |

★ **不做的（★ 写清原因，★ 见作业单 §四）**：`Hem`/`Jog`（API 里没有）· 工程图标注（撞红线/弹窗）·
`export_flat_pattern_dxf`（要"已保存"）· 拓扑升到能跑（缺许可）· 吃 COM 元素的配置器（拿不到实参）。

## 二、任务（★ 每个带 `→ 验收:`）

### T0 · 段 0：判据自检（★ 本 spec 的核心）
```
T0.1 ★ 先查有没有现成实现（★ 作业单 §五"先找后搓"）：
     ★ 在 `tools/` 与四家 MIT 克隆里搜 `preflight` / `judge` / `baseline` / `known-good` 之类。
→ 验收: ★ 写出"找到什么 / 没找到什么"的结论（★ 一条命令 + 它的输出）

T0.2 ★ 写 `tools/check_judge_preflight.py`（★ 名字待定，★ 而职责定死）：
     ★★ 职责：**读探针/包装里的"回读判据"，检查它有没有对应的"已知成功场景"证据。**
     ★ 判据的形态（★ 而这正是"先找后搓"要定的）：★ 最可能是**一张显式登记表**
       （判据 → 已知成功场景 → 那份 evidence 的路径与 verdict）。
→ 验收: ★ 脚本能跑出 exit 0/1，★ 且**对"缺登记"的情形真的会红**（★ 用负例自证 —— 事实 62 的手法）

T0.3 ★ 把三家探针（`judge_alternatives` / `loads_count_studytype` / `first_load_rule`）的结论
     ★ **沉淀成登记表的头几条**（★ 那是"判据不可用"的既知实例）。
→ 验收: ★ 登记表里至少 3 条，★ 每条写明"该判据在哪条路上不可用"与证据文件

T0.4 ★ 接进门禁（★ `release_check.py` + `docs/gate-classification.json`）
→ 验收: ★ `python scripts/release_check.py` ⇒ **exit 0**；★ `check_gate_wiring.py` ⇒ PASS
```

### T1 · 段 1：B 组两条连接件
```
T1.1 ★ 按 R1 先做**判据前置**：在一个**已知成功**的场景（如 `apply_force`）上，
     ★ 验"新判据"（不依赖 `Count` 属性那条）能复现 `0→1`。
→ 验收: ★ 该前置检查自己有一份 `output/*-evidence.json`，★ 且 `verdict: pass`

T1.2 ★ 用验过的判据重跑 `link_connector` / `rigid_connector`
→ 验收: ★ 若成 ⇒ 注册 + `verdict: pass`；★ 若不成 ⇒ **按硬约束⑥ 不注册**，★ 并把"哪一步不成"写清
```

### T2 · 段 2：焊件族
```
T2.1 ★ 找**型材文件**：★ 优先用**已在盘上的** SolidWorks 自带 `.sldlfp`（★ 硬约束⑦：我不保存）
→ 验收: ★ 给出路径 + 存在性证据

T2.2 ★ 取**草图线段**当 `segment_groups`（★ 查官方入口：`ISketch.GetSketchSegments` 之类，★ 不猜）
→ 验收: ★ 写出签名来源（`C:\swapi\types\...` 或出厂类型库反射）

T2.3 ★ 建结构构件，★ 判据用**特征树增长**（★ 与 `Count` 不同的一条判据 ⇒ 天然绕开那条限制）
→ 验收: ★ `output/*-evidence.json` 的 `verdict: pass` + 注册
```

### T3 · 段 3：`sw_selection_tx.py` 的决断
```
T3.1 ★ 查那四个名字（`SELECTION_FAMILIES` / `SHEET_METAL_SELECTION_FAMILIES` /
     `_FeatureSelection` / `_SheetMetalSelection`）在**官方 API** 里有没有对应物
→ 验收: ★ 逐条给出"官方有/没有 + 依据"（★ 铁律 5：查不到就说查不到）

T3.2 ★ 据此**二选一**：补全（要能真机过）或删除（并同步改引用它的那个测试）
→ 验收: ★ `check_undefined_names.py` ⇒ 那 6 处要么消失、要么 `KNOWN_BROKEN` 条目**被删掉**
```

### T4 · 段 4：剩余该挂分批清理
```
T4.1 ★ 重跑分诊，★ 按模块出"该挂清单"（★ 数字从生成物来）
→ 验收: ★ 给出清单 + 每类的**判据前置声明**（★ 作业单 §二 第 ⑥ 件）

T4.2 ★ 逐批做（★ 每批五件套 + 判据前置声明）
→ 验收: ★ 每批：`verdict: pass` 的 evidence + ToolSpec 已注册 + 契约测试 + `round_chain.ps1` 绿
```

### T5 · 段 5：收敛报告 v2
```
T5.1 ★ 写 `docs/plan-200r-v3-convergence.md`（★ 照 v2 的八章体例）
→ 验收: ★ 沿用 v2 的**核对器**：报告里每个数字都要与生成物**逐项对得上**（★ 上一轮做到 0 处不一致）
```

## 三、判据核查命令表（★ 每条需求怎么机验）

| 需求 | 命令 |
|---|---|
| R1 / R2 | `python tools/check_judge_preflight.py` ⇒ exit 0 |
| R3 / R4 | `python -c` 按「能力 → 工具 × 能力 → 证据文件 verdict=pass」追（★ 上一轮的算法） |
| R5 | `python scripts/check_undefined_names.py` ⇒ 那 6 处消失 |
| R6 | `python tools/triage_real_gaps.py`（该挂数下降） |
| R7 | 报告数字 vs 生成物（★ 上一轮的核对脚本） |
| 全局 | `pwsh -File tools/round_chain.ps1 -Tests tests/<改过的>.py` · `git status --porcelain` 空 |
