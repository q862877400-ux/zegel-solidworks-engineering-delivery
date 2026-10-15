# Acceptance — **EC00 可信工具底座**

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**状态**: ★★★ **施工中** —— ★ **offline / runtime / product 三级分开记录**（★ FR-013）
**上游**: `output/ENGINEERING_P0_ACCEPTANCE_DRAFT.md`（五份 P0 草案之五）· `tasks.md`（T001–T032）

---

## 一、★★★★★ 三级结论（★ **分字段记录，不合并**）

| ★ 级别 | ★ 当前结论 | ★ 依据 |
|---|---|---|
| ★ **offline** | ✅ **pass**（★ **T001–T023 的离线部分全部落地** · ★ **94 例**全绿） | ★ 本文件 §三 的矩阵 + `tests/test_ec00_*.py`（**12 个文件**） |
| ★★ **runtime** | ⏸ **`not_run`** | ★ T024–T028 **全部未执行**；★ **不得因离线通过而升级** |
| ★★ **product** | ⏸ **`not_run`** | ★ 发布门未到 |

★★★ **硬规则**（★ 逐字承 `data-model.md` §5.2）：★ **`offline` pass 不能写成 `runtime` pass**。

### 1.1 ★★★★★ 本会话实测读数（★ 可复核）

| ★ 项 | ★ 读数 | ★ 命令 |
|---|---|---|
| ★ EC00 离线判据 | ★★ **94 passed**（★ 12 个文件） | ★ `python -m pytest tests/test_ec00_*.py -q` |
| ★★ 工具总数 | ★ **479 → 480**（★ 净增 **1**：`solidworks_sketch_apply_relations`） | ★ `python tools/ec00_scope_inventory.py` |
| ★ 能力域 | ★ **140**（`verified` 117 · `stitched` 20 · `not_implemented` 3） | ★ 同上 |
| ★★ 仓库门禁 | ★ **`status pass` · `EXIT 0` · `missing []` · 47 道** | ★ `python scripts/release_check.py` |
| ★ 生成器链 | ★ **7/7 `rc=0`** | ★ 见 `AGENTS.md` §十六 |

### 1.2 ★★★ 红基线证明（★ 事实 62：判据「写了」≠「有效」）

| ★ 判据 | ★ 怎么证它真在守 | ★ 红时读数 |
|---|---|---|
| ★ T006 留档 | ★ 把 `research/T006-official-signature.md` 改名 | ★ **3 failed** |
| ★ T017 注册 | ★ 从 `BATCH_MODULES` 摘掉 `"tool_specs_batch113"` | ★ **3 failed** |
| ★ T023 公开路由 | ★ 同上 | ★ **5 failed** |

★★★ **⇒ 判据不是「关键词 grep」—— ★ 它们**真的**在守实现（★ 摘掉实现即红）。

---

## 二、★★★★ FR → 任务 → 测试 → 证据矩阵（★ 15 条 · ★ **T011/T030**）

★★★ **当前结论列**：★ `not_run` = 未运行；★ `pass`/`fail` = **已实测**；★★ **不得出现无证据的 `pass`**。

| ★ FR | ★ 任务 | ★ 验收测试 | ★ 必需证据 | ★ 当前结论 |
|---|---|---|---|---|
| **FR-001** 范围清单 | T003/T004/T030 | `test_ec00_legacy_migration_mapping.py`（★ 拟新增） | ★ 静态清单及对应原记录 | 🔶 **部分**（★ `research.md` §一 迁移表 ✅ · ★ `output-ec00-scope.json` ✅ · ★ 判据 ⏳） |
| **FR-002** 单位与历史默认 | T004/T008/T012/T016 | `test_ec00_quantity_contract.py`（★ 拟新增） | ★ 契约、离线桩、默认来源 | 🔶 **部分**（★ `contracts/quantity.md` ✅ · ★ 判据 ⏳） |
| **FR-003** 单边界转换 | T012/T016/T025 | `test_ec00_unit_boundary_negative.py`（★ 拟新增） | ★ 输入→规范值→边界值→实际尺寸 | ⏸ **not_run** |
| **FR-004** 正式关系与效果 | T006/T017/T018/T025 | `test_ec00_effect_readback_mapping.py`（★ 拟新增） | ★ 官方依据、桩及真机回读 | ⏸ **not_run**（★ ★ **T017 实测缺口：0 个 ToolSpec**） |
| **FR-005** 关系预检 | T017/T025 | `test_ec00_sketch_relation_precheck.py`（★ 拟新增） | ★ 修改前拒绝及**调用计数** | ⏸ **not_run** |
| **FR-006** 文档/配置/版本 | T014/T019/T026 | `test_ec00_context_reference_negative.py`（★ 拟新增） | ★ 前后态及拒绝证据 | ⏸ **not_run** |
| **FR-007** 引用歧义关闭 | T014/T019/T026 | ★ 同上 | ★ 解析候选和实际对象签名 | ⏸ **not_run** |
| **FR-008** 实际效果 | T013/T018/T025 | `test_ec00_effect_false_success_negative.py`（★ 拟新增） | ★ **fail 或 unknown，不得 pass** | ⏸ **not_run** |
| **FR-009** 非幂等恢复 | T015/T020/T027 | `test_ec00_nonidempotent_uncertain_negative.py`（★ 拟新增） | ★ `uncertain` 与修改调用计数 | ⏸ **not_run** |
| **FR-010** 护栏与单会话 | T015/T020/T027 | `test_ec00_guardrail_bypass_negative.py`（★ 拟新增） | ★ 一个修改者、护栏与拒绝记录 | ⏸ **not_run** |
| **FR-011** 版本化证据 | T013/T021/T030 | `test_ec00_evidence_manifest_versioning.py`（★ 拟新增） | ★ manifest 与 stale 拒绝 | ⏸ **not_run** |
| **FR-012** 保存重开 | T026 | `test_ec00_runtime_persistence.py`（★ 拟新增） | ★ 工件及重新回读尺寸/关系 | ⏸ **not_run**（★ **真机**） |
| **FR-013** 阶段等级 | T021/T030 | `test_ec00_acceptance_matrix_completeness.py`（★ 拟新增） | ★ **不升级等级的记录** | 🔶 **部分**（★ `data-model.md` §5.2 规则 ✅ · ★ 判据 ⏳） |
| **FR-014** 兼容不绕门 | T012/T022/T028 | `test_ec00_legacy_entry_hard_gate.py`（★ 拟新增） | ★ 对照和明确拒绝 | ⏸ **not_run** |
| **FR-015** 来源/权属/脱敏 | T001/T003/T015/T021/T030 | `test_ec00_secret_redaction.py`（★ 拟新增） | ★ 台账差异、策略和测试 | 🔶 **部分**（★ `baseline.md` 权属 ✅ · ★ 判据 ⏳） |

---

## 三、★★★★ 八条验证义务（★ V1–V8 · ★ 逐条可判）

| ★ # | ★ 判据 | ★ 测试 | ★ 当前结论 |
|---|---|---|---|
| **V1** | ★ 每条 FR 有故事、可测场景、主任务和测试 | `test_ec00_acceptance_matrix_completeness.py` | ⏸ **not_run**（★ 矩阵**已写**，★ 判据未建） |
| **V2** | ★ 每条 SC 有测量定义 | ★ 同上 | ⏸ **not_run** |
| **V3** | ★ 代表 ToolSpec 范围/版本/单位/历史默认已冻结 | `test_ec00_quantity_contract.py` | 🔶 **部分**（★ 范围 ✅ · ★ 版本/默认 `unknown`） |
| **V4** | ★ 非法量纲和缺关键工况在 **COM 前**阻断 | `test_ec00_unit_boundary_negative.py` | ⏸ **not_run** |
| **V5** | ★ 三类假成功**无 effect pass** | `test_ec00_effect_false_success_negative.py` | ⏸ **not_run** |
| **V6** | ★ 非幂等**无判断不重放** | `test_ec00_nonidempotent_uncertain_negative.py` | ⏸ **not_run** |
| **V7** | ★ 证据版本失效后**不得放行** | `test_ec00_evidence_manifest_versioning.py` | ⏸ **not_run** |
| **V8** | ★ 离线 pass **不升级** runtime 等级 | ★ 同上 + 既有 `test_verified_level_has_runtime_evidence.py` | 🔶 **部分**（★ 既有判据 ✅ · ★ 新判据 ⏳） |

---

## 四、★★★★★ 逐任务验收（★ **T001–T032** · ★ 只勾**交付与证据均完成**的）

### 4.1 ★ 已完成（★ 文档任务）

| ★ 任务 | ★ 交付 | ★ 证据 | ★ 结论 |
|---|---|---|---|
| **T001** | ★ `baseline.md` | ★ 编号 **302** · ★ 权属按 D6 · ★ 写入面 · ★ **未触碰 B 组** | ✅ **pass** |
| **T002** | ★ `spec.md` · `plan.md` · `tasks.md` · `baseline.md` · `research.md` · `data-model.md` · `contracts/`×3 · `checklists/` | ★ 编号与 `baseline.md` 一致 | ✅ **pass** |
| **T003** | ★ `research.md` §一（迁移表 6 项 + 212 挂起 4 项特别登记） | ★ 每项写「处理」+「**原状态是否变化**」 | ✅ **pass** |
| **T004** | ★ `tools/ec00_scope_inventory.py` + `output-ec00-scope.json` | ★ **五类代表工具全覆盖** · ★ 479 工具 · ★ 140 能力域 · ★ **未连接 COM** | ✅ **pass** |
| **T005** | ★ `checklists/requirements.md`（★ D-001～D-005 冻结 + 非目标 + 未知 8 条） | ★ **G1 通过** | ✅ **pass** |

### 4.2 ★ 未完成（★ **保持 `[ ]`**，★ 不勾）

| ★ 任务 | ★ 缺什么 | ★ 状态 |
|---|---|---|
| **T006** | ★ `AddRelation` 的 `## Remarks`/Example **逐字核验记录** | ⏸ **待做** |
| **T007** | ★ `test_ec00_round_chain_side_effect_inventory.py` | ⏸ **待做** |
| **T008–T010** | ★ 契约**已写**；★ **判据未建** | 🔶 **部分** |
| **T011** | ★ 一致性分析判据 + FR 矩阵判据 | 🔶 **部分**（★ 矩阵 ✅ · ★ 判据 ⏳） |
| **T012–T015** | ★ **5 个负例测试文件**（★ 全部不存在） | ⏸ **待做** |
| **T016** | ★ 单位规范化入口 + 判据 | ⏸ **待做** |
| **T017** | ★★ **关系正式注册**（★ **实测：0 个 ToolSpec**） | ⏸ **待做** |
| **T018–T023** | ★ 各自实现与判据 | ⏸ **待做** |
| **T024–T028** | ★ **真机**（★ 业主已授权，★ 待环境确认） | ⏸ **blocked** |
| **T029–T032** | ★ 收口 | ⏸ **待做** |

---

## 五、★★★ 基线与负面事实（★ 承 P0 ACCEPTANCE §1.1）

| ★ 项 | ★ 基线 | ★ 含义与限制 |
|---|---|---|
| ★ 目标仓库 | `D:\AI\SW` | ★ 不在 zcode 施工，★ 不改只读归档 |
| ★ 架构文档 | `output/ENGINEERING_MODELING_ARCHITECTURE.md` | ★ 方案完成，★ **不是工程能力实现** |
| ★ 本轮产物 | ★ 总计划及 EC00 配套 | ★ **只完成文档与部分离线判据，不完成 T001～T032** |
| ★ 工具契约 | ★ 本仓已有 ToolSpec、注册、效应等基础 | ★ **不证明每条公开路径可信** |
| ★ 局部单位修复 | ★ `scripts/sw_part.py` 已有修复记录 | ★ **未将所有 API 逐项复验** |
| ★ 草图关系 | ★ `scripts/sw_sketch_relations.py` 已有代码 | ★★ **正式注册、契约/包装与生效回读仍需核实并补验** |
| ★ 编排和验证基础 | ★ 工程 DAG、worker、复核门、选择/比较/DFM/CAE 组件存在 | ★ **不是完整工程闭环或认证** |
| ★ 运行环境 | ★ **本会话未视为正式 SW 工具执行环境就绪** | ★ **真机任务阻塞，不在文档轮运行 COM** |

---

## 六、★★★ 必做故障注入清单（★ 承 P0 ACCEPTANCE §5）

### 6.1 ★ 离线必须做（★ **T012–T015**）

- [ ] ★ 同一长度两单位、角度两单位、错误量纲、NaN/无穷、重复规范化。
- [ ] ★ 缺单位且无历史契约；★ 旧默认与新接口一致性。
- [ ] ★ 真 ToolSpec 注入错误/参数缺失；★ **内部函数绿但公开路由错**。
- [ ] ★ 返回 `true` 但关系不存在；★ 几何巧合满足但必要持久关系缺失。
- [ ] ★ 无回读/回读异常/过期容差，★ **不允许 effect pass**。
- [ ] ★ 错文档/配置/前态版本；★ 两个未保存文档空路径冲突。
- [ ] ★ 引用 0 候选、多候选、错类型/上下文。
- [ ] ★ 非幂等超时可能已修改；★ **未核验不第二次创建**。
- [ ] ★ 双客户端争用，★ **旧入口不能绕互斥/门禁**。
- [ ] ★ 证据错版本、规则改变、★ **阶段未执行却企图标真机通过**。
- [ ] ★ 凭据脱敏、工件路径越界、★ **非自有文档关闭/重启拒绝**。

### 6.2 ★ 真机批准后必须做（★ **T025–T028**）

- [ ] ★ 公开工具路径单位传参与实际尺寸一致。
- [ ] ★ 关系正例及非法/未生效案例：★ 关系图与几何语义回读。
- [ ] ★ 重建、配置切换、保存重开后效果仍成立。
- [ ] ★ 指定文档/引用核验，★ **没有活动窗口误操作**。
- [ ] ★ 安全可复现的竞争/恢复样例；★ **禁止为了测试破坏用户会话**。
- [ ] ★ 新旧代表入口真机对照；★ 不支持或不稳定路径保留限制。

---

## 七、★★★ 残余风险（★ **具名** · ★ 承总计划 §9）

| ★ # | ★ 残余风险 | ★ 处置 |
|---|---|---|
| ① | ★★ **`sw_sketch_relations.py` 有实现但 0 个 ToolSpec** | ★ **T017 待做**（★ **本会话实测**） |
| ② | ★★ **`AddRelation` 的官方 Remarks/Example 未逐字核** | ★ **T006 待做**（★ 保持 `unknown`） |
| ③ | ★ **`GetArea` 侧面 1000 倍未解释** | ★ 保持 `unknown`（★ `docs/unit-conflicts.md` 第 1 条） |
| ④ | ★ **工具级 `writes`/`idempotent`/`destructive` 三态全 `None`** | ★ **T004 实测**（★ 代表工具**全部未声明**）⇒ ★ EC00 的**直接靶子** |
| ⑤ | ★ **真机 5 项未执行** | ★ `not_run`，★ **不包装成完成** |
| ⑥ | ★ **未提交未部署** | ★ 红线；★ **如实登记** |
