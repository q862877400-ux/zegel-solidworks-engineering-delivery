# 挂机队列（≥ 8 小时）—— 按 Spec Kit 宪法排

> **建立** 2026-10-01（轮 205）· **目标页** `goal-a16db85f-48d9-4b6e-a683-dccab949a701`
> **作业指导书**：`.specify/commands/speckit.<name>.md`（读它、按它执行；**不要**复制到 skill 目录）
> **宪法**：`.specify/memory/constitution.md`（§I–§V 是 `analyze` 要对齐的判据）
> **模板形状**：`.specify/templates/{spec,plan,tasks,checklist}-template.md`

---

## 〇、每个特性必须产出的（**全路径，缺一不算完成**）

```
specs/<NNN>-<slug>/
  spec.md        ← 模板形状：User Scenarios（P1/P2/P3 分优先级）+ Acceptance Scenarios（Given/When/Then）
                   ★ 宪法 §I：**每条需求带「来源」**（四种合法来源之一）；§IV：来源行带 **license**
  plan.md        ← ★ 宪法 §II：列出要查的**官方源**（CHM / C:\swapi / interop 反射）与**冲突裁决顺序**
                   + **Constitution Check** 闸（§I–§V 逐条过）
  tasks.md       ← ★ 宪法 §V：**每条任务带 `→ 验收:`** 且是**能跑出绿的命令**
  checklist.md   ← 质量闸（照 checklist-template）
  analyze 结论   ← 跨制品一致性（宪法 §I–§V 逐条 grep 得出）
  converge.md    ← 结果表 + **未查证逐条**（宪法：不许写"当前进度"——那在 capabilities.yaml 与 ROADMAP 游标）
```

★ **Flow-forward**：完成的目录**不改**；需求变了开新号。
★ **三处不许写**：当前进度 / 六条铁律 / 已知事实。

## 〇之二、每项收工必须做的（**不做完不算完成**）

```
1. `python scripts/release_check.py` ⇒ exit 0
2. `python -m pytest tests -q` ⇒ 0 failed（★ 计数类测试报红 ⇒ **同步更新那个数**，那是设计意图）
3. `python scripts/sync_bundled_skill.py`（改了运行期文件后**必须**）
4. ROADMAP §一 游标 +5 行（anchor `^\s+NNN `）
5. `docs/known-facts.md` 追加一条
6. `git commit` **两仓库各自**（本地；**不 push**）
```

---

## 一、A 组：挂柜台续批（≈ 5.9 h）

★ **候选源唯一**：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
★ 每批的选法**写进 `tool_specs_batchNN.py` 头部**（取/不取 + 理由），照 `batch7` / `batch11` 格式。

| # | 特性 | 做什么 | 来源 / 许可 | 验收命令 | 估时 |
|---|---|---|---|---|---|
| **A1** | `124` | 拓扑族第二批：`create_demold_control` · `create_stress_constraint` · `create_symmetry_control`；并给已挂的 `create_preserved_region` 补枚举说明 | 本项目自身（包装既有 `scripts/sw_topology.py`，MIT）；**枚举**来自出厂反射 `D:/AI/SW/_raw/reflect/enum_cosworks.txt` | `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"` + `pytest tests/test_server_wiring.py` | 20 min |
| **A2** | `125` | `sw_simulation_study` 族：`generate_report` · `create_mesh_for_control` · `default_element_size_and_tolerance` | 本项目自身（MIT）；既有 `study` 注入模板 | 同上 | 25 min |
| **A3** | `126` | 视图/选择族：`get_active_view` · `activate_view` · `add_perspective` · `entities_on_body` | 本项目自身（MIT）| 同上 | 25 min |
| **A4** | `127` | 审查/报告族：`build_review_report` · `activate_plot` | 本项目自身（MIT）| 同上 | 25 min |
| **A5** | `128` | `sw_part` 安全子集：`add_sketch_relation` · `add_dimension`（★ **跳过含 `angle_rad` 的**）| 本项目自身（MIT）| 同上 | 30 min |
| **A6** | `129` | ★ 先定 `angle_rad → _deg` 的**换算边界**（规则 2），再挂 `circular_pattern` 等 | 规则 2 + `sw_connect.mm()` 既有模式 | 同上 | 40 min |
| **A7** | `130` | ★ 先定 `sw_surface` 的「返回值跨次会变」（事实 40）的**行为**（抛 or 回读校验），再挂 | 本项目既有 `_invoke` 抛错模式 | 同上 | 45 min |
| **A8** | `131` | ★ 先写**包装层**（裸坐标 → 声明式 selection，规则 3），再挂 `sw_simulation_loads` 的 `add_force`/`add_pressure` | 规则 3 + 既有 `sw_selection_spec` 模式 | 同上 | 60 min |
| **A9** | `132` | 把"可注入 47"**剩下的一次性扫完**（逐条取/不取 + 理由）| 同上 | 同上 | 45 min |
| **A10** | `133` | 从**非首参可注入**的 251 个里找**第二类可挂形态**（首参是 `manager`/`doc` ⇒ 需新注入器）—— 先出**可行性判断**，不硬挂 | 同上 | 同上 | 40 min |

## 二、B 组：真机验证（≈ 1.5 h）★ **把"暴露"升级为"验证"**

| # | 特性 | 做什么 | 验收命令 | 估时 |
|---|---|---|---|---|
| **B1** | `134` | 跑**静力学**那条验收（许可已确认生效）| `python tools/capture_simulation_evidence.py`（期望 `verdict: pass`）| 10 min |
| **B2** | `135` | 把 A1 的拓扑新工具**串成真机链**跑一次（目标+约束+控制 ⇒ 求解）| `python tools/capture_topology_evidence.py` 或新脚本 | 30 min |
| **B3** | `136` | 给 A3/A4 的视图/审查族各挑 1 个代表做真机冒烟（**只读，不碰模型**）| 该族冒烟脚本 exit 0 | 25 min |
| **B4** | `137` | ★ **把"暴露了但没验过"清点出来**（机器可查：工具 → 有无真机证据）| 生成 `D:/AI/SW/output/exposed-but-unverified.json` | 25 min |

## 三、C 组：B 级并入第一刀（≈ 1.1 h）

| # | 特性 | 做什么 | 验收命令 | 估时 |
|---|---|---|---|---|
| **C1** | `138` | ★ **先把"265 操作名缺口"做成可复现清单**（同 A 组那招：先修判据再动手）| 生成 `D:/AI/SW/output/union-gap-list.json` | 35 min |
| **C2** | `139` | 从清单里取**「我们已有、只是没挂名字」**那一档的第一批 | 该批的验收命令 | 30 min |

## 四、D 组：纪律与维护（≈ 1.25 h，穿插）

| # | 做什么 | 估时 |
|---|---|---|
| **D1** | 审计 §八 那 **25 个零调用族**逐条判「该做 / 不做 + 原因」（写进 known-facts）| 25 min |
| **D2** | 修 `D:/AI/SW-transfer/test-plan-final.md` 的 **4 处小错**（少一层 `scripts/` 等）| 10 min |
| **D3** | 每 3–4 项插一次**全链刷新**（游标 / 报告数字 / digest / 地图）| 穿插 ~40 min |

## 五、E 组：测试计划试跑（≈ 0.7 h，有余力才做）

| # | 做什么 | 估时 |
|---|---|---|
| **E1** | 按 `test-plan-final.md` 跑 **T1（选型检索）** 与 **T5（造端板+螺丝孔）**（都是 ✅ 档）| 40 min |

---

## 六、执行顺序

```
A1 → B1 → A2 → A3 → B2 → A4 → A5 → A6 → D1 → A7 → B3 → A8 → A9 → A10
   → C1 → C2 → B4 → D2 → E1        （每 3–4 项插 D3；每项收工都提交两仓库）
```
**合计估时 ≈ 10.2 h** ⇒ 覆盖 8 小时有余。

## 七、★ 停下等用户的条件（**只有这几条**）

```
① 需要 push / 任何远端写入（红线：要批准）
② 需要碰注册表 / 系统层 / 破解相关（红线）
③ 真机操作可能造成不可逆后果（删文档 / 覆盖用户数据）
④ 同一处**连续 3 次**修不好（事实 53：回退 + 记证据，不再试）
⑤ 需要用户才能提供的东西（凭据 / 业务口径 / 许可）
★ 除以上**一律自行判断并继续**；不确定的写进"未查证"，不要停下来问。
```

## 八、已知障碍（写这里省得每轮重查）

| 障碍 | 依据 | 处置 |
|---|---|---|
| `sw_surface.Create*Surface` 返回值**跨次会变** | 事实 40 | 先定行为再挂（A7）|
| `sw_part` 的 `angle_rad` ⇒ 与规则 2 冲突 | 规则 2 | 先定换算边界（A6）|
| `sw_simulation_loads` 入参是**裸坐标** ⇒ 规则 3 会拒 | 既有批次记录 | 写包装层（A8）|
| `symmetry_type` 的**枚举名**本地转储里没有 | 轮 205 实测 | ★ 按**官方 VBA 示例**的 0/1/2 声明，**并如实标注来源** |
| "同一条链上" ≠ "这个函数跑过" | 事实 143 | 别用邻接关系代替证据 |
| 探针的候选清单**曾 87% 看不见** | 事实 143 | 选批前**先确认清单是全量** |
| 计数类测试会**当场报红** | 设计意图 | 加批次就同步更新那两个数 |
| 改运行期文件忘同步 | 事实 55 | 跑 `sync_bundled_skill.py` |
| 长文本嵌同类引号 ⇒ SyntaxError | 事实 48 | 长内容先写独立文件再搬运 |
