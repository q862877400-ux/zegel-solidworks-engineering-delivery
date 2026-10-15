# Research — **EC00 可信工具底座**：事实、未知、决策与迁移

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_P0_PLAN_DRAFT.md` §6（`research.md` 至少要记的问题表）· `output/ENGINEERING_P0_ACCEPTANCE_DRAFT.md` §1.3（旧欠账迁移模板）
**对应任务**: **T003**（旧任务→新任务迁移表）· **T006**（官方源核验）· **T007**（副作用边界）· **T010**（uncertain 策略）

---

## 一、★★★★★ 旧任务 → 新任务迁移表（★ **T003**）

★★★ **纪律（★ 逐字承 P0 ACCEPTANCE §1.3 与 T003 的人工门）**：
- ★ 每项写明**复用、补验或延期**；
- ★★ **不能自动勾旧任务**（★ 旧状态**不得被新任务自动清空**）；
- ★★ **旧任务与台账权属不得按 git 作者自动认领**；
- ★★★ **未知归属保持 `unknown`**。

### 1.1 ★★ 逐项迁移（★ 2026-10-10 本会话**实测**旧规格状态）

| # | ★ 旧项 | ★ 原规格/证据 | ★ 新任务 | ★ 处理 | ★ **原状态是否变化** |
|---|---|---|---|---|---|
| ① | ★ **单位盘点及边界修复** | ★ `specs/212-unit-discipline/`（★ `goal-bar.md` 逐字：★ **收口验收完成**（C1–C7 逐条达标）· ★ **有意挂起 4 项**）· ★ `docs/unit-conflicts.md`（★ **人工维护**的冲突登记）· ★ `docs/script-layer-units.md` | **T004/T008/T012/T016/T025** | ★★ **复用**局部修复（★ `sw_part.py` 的 `_MM_TO_M`）· ★ **补范围与真机证据** | ★★ **不变**（★ 212 的「收口完成」**保持**） |
| ② | ★ **草图关系正式路径** | ★ `specs/221-sketch-relation-dispatch-safety/`（★ `acceptance.md` 逐字：★ **限定离线行为回归通过；runtime/product=not_run**）· ★ `scripts/sw_sketch_relations.py`（151 行）· ★ `tests/test_sw_sketch_relations_safety.py`（★ **12 例**） | **T006/T017/T018/T025** | ★★ **补**：★ **包装、注册、负例和回读闭合** | ★★ **不变**（★ 221 的「离线通过 / runtime not_run」**保持**） |
| ③ | ★ **效应声明与假成功** | ★ `specs/210-declarative-effects/`（★ `goal-bar.md` 逐字：★ **五批全部收口**（B1–B5）· ★ **B3 全量普查 448 条**）· ★ `docs/effect-declarations.json` | **T009/T013/T018/T021** | ★★ **接**实际效果（★ **不重建系统**） | ★★ **不变** |
| ④ | ★ **文档关闭 / 计数 / 身份** | ★ `docs/ROADMAP.md`（★ 关窗/文档计数欠账）· ★ `scripts/sw_session.py`（★ `open_documents`/`classify_open_documents`/`precheck_session`）· ★ `scripts/sw_fingerprint.py`（★ 九类 · ★ `KNOWN_UNAVAILABLE` 的 `display` 桶） | **T007/T014/T019/T026** | ★ **自有工件身份与状态检查** | ★★ **不变** |
| ⑤ | ★ **非幂等超时 / 护栏** | ★ `tools/sw_guard.py`（★ `classify_dialog` 三级）· ★ `tools/round_chain.ps1`（★ **L84/L117/L150 `git add -A`** · ★ **L199 `--close`**） | **T010/T015/T020/T027** | ★★ **`uncertain` 和受控核验** | ★★ **不变** |
| ⑥ | ★ **齿轮表示 / 根切等设计问题** | ★ 既有交接与方案（★ `output/planetary-10to1/`） | ★ **非 EC00 制造设计任务** | ★★ **保留为后续挑战和设计义务** | ★★ **不变**（★ 计划 §6.1：★ **此时不推进齿轮模型**） |

### 1.2 ★★★ 特别登记：`spec 212` 的**有意挂起 4 项**（★ 不得被本特性自动清空）

★ `specs/212-unit-discipline/goal-bar.md` 逐字：★ **有意挂起 4 项** ——
★★ **其中 3 项同一件事**：★ **C-4 / C-5 / D-6 = 把「只报不拦」升级成 `GateError`**
（★ **前提「清单清空」未达成** ✗ · ★ 且**用户指令明写「先只报不拦」** ✓）；
★ **另 1 项** = ★ **钣金卷边 `relief_width_mm`，等真机结论**。

★★★ **⇒ 本特性的处置**：★ 这 4 项**保持 `spec 212` 的原状态**（★ 不勾、不清空）；
★ 其中「钣金卷边等真机结论」与 EC00 的 **T025**（真机单位验证）**相关** ⇒ ★★ **只登记关联，不代为勾选**。

---

## 二、★★★★ 官方源核验（★ **T006**）

### 2.1 ★ 草图关系族 —— `ISketchRelationManager`

| ★ 项 | ★ 内容 |
|---|---|
| ★ **官方页** | ★ `C:\swapi\types\ISketchRelationManager\AddRelation.md` |
| ★ **入口** | ★ `ISketchRelationManager::AddRelation`（★ 逐字来源：★ `Slacker-LLC` `README.md:227`「`ISketchRelationManager.AddRelation` and verifies via the relation count」） |
| ★ **判据成员** | ★ `ISketchSegment::GetRelationsCount` / `IGetRelationsCount`（★ 逐字：★ `sw_sketch_relations.py:16`「★ `ISketchSegment` 成员表：★ **`GetRelationsCount`** ✓（★ 真判据 ✓）」） |
| ★ **状态成员** | ★ `ISketch::GetConstrainedStatus`（★ 返回 `swConstrainedStatus_e`：★ `1 swUnknownConstraint` · ★ **`2 swUnderConstrained`**） |
| ★ **本仓实现** | ★ `scripts/sw_sketch_relations.py`：★ `apply_sketch_relations(model, *, relations, verify=True)`（L180）· ★ `_rel_count`（L134）· ★ `_status`（L215） |
| ★★ **未核** | ★★ **本会话未逐字读 `AddRelation.md` 的 `## Remarks` 与 Example** ⇒ ★★ **标记为 `unknown`**，★ **不编造签名**（★ 铁律 5） |
| ★★ **待验证包装** | ★ 实参形态（★ 历史记录：★ 主入口 `AddRelation` 曾被**实参形态**阻塞，★ 报 `0x8002000E`） |

### 2.2 ★ 单位族

| ★ 项 | ★ 内容 |
|---|---|
| ★ **冲突登记** | ★ `docs/unit-conflicts.md`（★ **人工维护** · ★ 每条五要素：★ 官方页/官方原话/真机读数/证据文件/处置） |
| ★★ **第 1 条**（★ 未解决） | ★ `IFace2.GetArea` —— ★ 官方说「平方米」，★ 真机：★ **端面 `400.0`**（★ 与 mm² 吻合）· ★ **侧面 `0.4`**（★ 差 **1000 倍**）⇒ ★★ **`units_verified: false`**（★ 见 `scripts/sw_mass_property.py` 的 `SECTION_UNIT_CAVEAT`） |
| ★★ **第 1 条的交叉验证** | ★ `IModelDocExtension.GetSectionProperties2` 的 `retval[1]`（area）与 `GetArea()` ★ **逐面完全相同（12/12 次）** ⇒ ★★ **两成员互相印证** |
| ★ **处置纪律** | ★★ **不许按「换算一下就对」处理**；★ **不断言单位**（★ 铁律 5） |

### 2.3 ★★ 三源裁决顺序（★ 承 `plan.md` §三）

1. ★ **签名冲突**（参数个数/类型/方向）⇒ ★ **以本仓出厂类型库反射为准**；
2. ★ **Remarks/示例/运行证据的语义冲突** ⇒ ★ **不静默取其一**，★ **单独登记**并**停止该成员的实现**；
3. ★ **查不到就写「查不到」**。

---

## 三、★★★★ `round_chain` 副作用边界（★ **T007**）

★ 逐字承 P0 PLAN §6 的问题表：「★ **收尾副作用** —— 已发现 `round_chain` 全量暂存/关闭 SW 风险，
★ **不能作为纯验证入口**；★ **T029 拆分阶段、增加文件白名单与工件权属校验后才运行**」。

★★★ **本会话实测（★ 可复核）**：

| ★ 位置 | ★ 逐字 | ★ 副作用 |
|---|---|---|
| ★ `tools/round_chain.ps1` **L84** | ★ `git add -A` | ★★ **全量暂存**（★ 会把他人改动也暂存） |
| ★ `tools/round_chain.ps1` **L117** | ★ `git add -A` | ★★ 同上 |
| ★ `tools/round_chain.ps1` **L150** | ★ `git add -A` | ★★ 同上 |
| ★ `tools/round_chain.ps1` **L199** | ★ `python tools\reclaim_solidworks.py --close` | ★ **关闭 SolidWorks**（★ 自带文档判定：★ **有一个不是自己开的文档就拒绝关闭**） |

★★★ **⇒ EC00 的收尾设计**（★ 本会话已执行）：
- ★ **不跑整条 `round_chain.ps1`**；
- ★★ **改用 `release_check.py`（只读门禁）+ 聚焦 pytest**（★ 与 `AGENTS.md` §十六 一致）；
- ★ **T029 的产物** = ★ 拆成「生成与验证」与「提交与资源处置」两个入口 + 显式文件白名单。

---

## 四、★★★★ 上下文 / 指纹 / 版本（★ **T007** 续 · **T010**）

| ★ 问题 | ★ 现有事实 | ★ 未知 | ★ 决策规则 |
|---|---|---|---|
| ★ **单位与重复转换** | ★ `sw_part.py` 已有局部修复（★ `_MM_TO_M`）；★★ **不能假设所有工具一致** | ★ 全仓逐边界清单 | ★★ **逐边界盘点**，★ **保留旧契约证据** |
| ★ **`AddRelation` 参数包装** | ★ 仍属**待解决堵点** | ★ 实参形态 | ★★ **官方三件套 → 冲突/死路 → 限定探针**，★ **不猜签名** |
| ★ **关系/几何回读** | ★ 部分不稳定（★ 历史：★ 主入口曾报 `0x8002000E`） | ★ 几何语义判据 | ★★ **不把返回 `true` 视为已验证**；★ **无回读 `unknown`** |
| ★ **指纹覆盖** | ★ `sw_fingerprint.py` 九类；★★ **`KNOWN_UNAVAILABLE` 的 `display` 桶全抛 `com_error -2147417851`** | ★ 能否检测尺寸/特征/配置变化 | ★★ **区分内存与文件、配置与文档**；★ **无可靠检测就降级承诺** |
| ★ **收尾副作用** | ★ 已发现（★ 见 §三） | ★ 拆分形态 | ★★ **T029 拆分阶段后才运行** |
| ★ **正式运行环境** | ★ 本会话**未视为就绪** | ★ SW/COM/MCP 实测 | ★★ **离线与 runtime 分任务** |

★★★ **本会话实测补充**：★ SolidWorks **正在运行**（★ PID **41468** · ★ 10-09 23:15 启动）·
★ Python **3.14.7** 的 `comtypes`/`win32com`/`pythoncom`/`pywintypes` **四个齐全** · ★ `tools/sw_guard.py` 就位。
★★ **但「就绪」的定义由 T024 判**（★ **不靠猜测就绪**）。

---

## 五、★★★★ `uncertain` 恢复策略（★ **T010**）

★ 逐字承 P0 PLAN §5.5/§5.6：

```text
validated → context_checked → executing
  ├─ known no execution → rejected / failed
  ├─ returned → inspecting → pass / fail / unknown
  └─ timeout / ambiguous COM error → uncertain
                                  └─ inspect / recover，不能直接 retry
```

| ★ 规则 | ★ 内容 |
|---|---|
| ★ **R1** | ★★ **「没有完成返回」不等于「没有修改」** |
| ★ **R2** | ★ 异步护栏退出、COM 服务错误和读取失败**都可能产生不确定状态** |
| ★ **R3** | ★ 只有**操作可证实未执行、已满足或可受控补偿**时，才能选择下一步 |
| ★ **R4** | ★★ **不对所有动作提供通用 rollback**；★ COM 操作**不是数据库事务** |
| ★ **R5** | ★ **保存重开只操作自有样例**；★★ **用户未保存文档不在自动关闭/重启范围** |
| ★ **R6** | ★ 特征创建超时：★ 先检查是否存在**预期效果及多余实体**；★ 无法判断则**停止** |
| ★ **R7** | ★★ **旧入口兼容时不改变恢复语义**，★★ **更不能把 `unknown` 压回 `true`** |

---

## 六、★★★ 未知清单（★ 一律 `unknown`，★ **不用占位值冒充**）

| # | ★ 未知 | ★ 为什么不编 |
|---|---|---|
| ① | ★ `AddRelation` 的 `## Remarks` 与 Example **逐字** | ★ **本会话未读** ⇒ ★ 按铁律 5 **不编造** |
| ② | ★ `IFace2.GetArea` 侧面 **1000 倍**的成因 | ★ 已按**事实 53**（同一路线推 3 轮即停手）**收队** |
| ③ | ★ 出厂 interop 类型库 DLL 的**实际路径** | ★ 本会话**未定位** ⇒ ★ 只登记「历史既有引用」 |
| ④ | ★ `run_locked` 的**定义位置与所属模块** | ★ 仅核到**调用点** `tool_registry.py:693` |
| ⑤ | ★ 可靠**内存版本检测**能否实现 | ★ 需研究（★ 计划 §5.2） |
| ⑥ | ★ 平台**并发上限** | ★ `DSH_DECISIONS.md` D2 记「未知」 |
| ⑦ | ★ `deepseek_v41_flash` / `hy4` 的真实 model ID | ★ D1 逐字「**不编造 model ID**」 |
| ⑧ | ★ 九份 `ENGINEERING_*` 草案的**达标裁定** | ★ D8 逐字「**一律保留为 `unknown`**」 |

---

## 七、★★★ 决策记录（★ 承 P0 PLAN §10 的 C01–C16 冻结基线）

★★ **本轮明确冻结的 5 条兼容决策**（★ 逐字见 `plan.md` §十）：

| # | ★ 决策 | ★ 依据 |
|---|---|---|
| D-001 | ★ 旧 MCP **标量参数、`required`/`default` 语义保持** | ★ C01；`tool_registry.py` `Param` |
| D-002 | ★ 自动追加 `response_format`（默认 JSON）与 **Markdown 字符串返回路径保持** | ★ C02；`build_input_model()` |
| D-003 | ★ 公开调用经 `run_locked` **返回字符串**保持 | ★ C11；`make_tool_function()` 末行 |
| D-004 | ★ 旧 `precheck` 异常／`unchecked`／`SW_PRECHECK=off` 的**放行行为保持** | ★ C16；`PRECHECK_ENABLED` |
| D-005 | ★ 该工程路径**不允许回退旧入口绕门**（★ **仅限已纳入本特性迁移表的代表工具**） | ★ FR-014／SC-007 **已同步收窄** |

★★★ **统一约束**：★ **单位逐成员一次转换** · ★ **指纹是「有限状态类」的量具，不是完整 `model_revision`** · ★★ **`unknown`/`uncertain` 不通过**。

---

## 八、★★ 替代方案（★ 已考虑并否决）

| # | ★ 方案 | ★ 否决理由 |
|---|---|---|
| ① | ★ 新建第二套工具注册/选择/锁/证据系统 | ★★ 计划 §1 逐字：「**不要新建第二套**」⇒ ★ 以现有 `ToolSpec` 与执行入口为权威 |
| ② | ★ 把旧 `float` 入参**批量换成 `Quantity` 对象** | ★★ D-001 逐字：「**不**把旧 `float` 入参批量换成 `Quantity` 对象」（★ 会破坏旧契约） |
| ③ | ★ 用**文件哈希**当内存版本 | ★★ 计划 §5.2 逐字：「**文件哈希只能描述保存字节，不能代表尚未保存的内存模型**」 |
| ④ | ★ 引用失效时**自动挑最近的面** | ★★ 计划 §5.3 逐字：「**几何接近也不能自动确认是原对象**」 |
| ⑤ | ★ 用**截图**当效果证据 | ★★ 计划 §5.4 逐字：「**不将「看截图像对」升级成机器通过**」 |
| ⑥ | ★ 把 `unknown` 压回 `true` | ★★ 计划 §5.6 R7 逐字：「**更不能把 `unknown` 压回 `true`**」 |
