# Baseline — EC00 可信工具底座 · G0 基线与权属登记

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`（总计划 §6.1：本轮只批准并展开 EC00）· `output/ENGINEERING_P0_*.md`（五份 P0 草案）· `output/DSH_DECISIONS.md`（D5 编号裁定 · D6 权属裁定 · D8 草案裁定）
**对应任务**: **T001**（`ENGINEERING_P0_TASKS_DRAFT.md` §2）

---

## 一、★★★ 编号与游标（★ 计划 §6.1 第 2 步「G0 核对编号、feature 游标、分支、未提交改动」）

| ★ 项 | ★ 实测读数 | ★ 处置 |
|---|---|---|
| ★ **最高正式编号** | **301**（`specs/301-fifteen-existing-reds/`） | ★★ **本特性取 `302`** —— ★ 与既有编号**无冲突** ✓ |
| ★★ **重号检查** | ★ **`207` × 2**（`207-agent-team-tool-routing` · `207-union-gap-verify`） | ★ **保留不合并**（★ `DSH_DECISIONS.md` **D5** 逐字：「两者都保留、各自负责，**不合并、不重命名**」）—— ★★ **`302` 不受影响** ✓ |
| ★ `feature.json` | ★ 原值 `{"feature_directory": "specs/293-route-change-viability"}`（★ **过期**） | ★★ **本轮改为指向本特性**（★ D5 说「接管方若要修，改一行并**单独提交**」；★ 而本会话红线**禁止 commit** ⇒ ★ **改一行、不提交**，如实登记） |
| ★ 分支 | `master` | ★ **不切分支**（★ 计划 §1.5：「不要现在复制 zcode 的 `.specify/`，不要批量建立 13 个空规格」） |
| ★ `HEAD` | `d072d0c79985f87e9d1f6278241b18fc1f26d713` | ★ 与 `ENGINEERING_PARALLEL_ROSTER.json` 的 `baseline.head` **一致** ✓ |

---

## 二、★★★★ 工作树与权属（★ 计划 §6.1 第 2 步「未提交改动、现有约束、明确本轮允许写哪些文件」）

★★ **实测未提交条目数 = 4136**（★ 计划当时记的是 **264** —— ★ **它涨了**，★ 原因：★ 本会话把仓库根的 2814 个草稿**搬进** `archive/` ⇒ ★ 每个文件**多一条** ` D` + 一条 `??`）。

★★★ **按 `DSH_DECISIONS.md` **D6** 的分组口径**（★ 那是**代业主作出的裁定**，★ 可直接执行）：

| ★ 组 | ★ 内容 | ★ 处置（★ D6 逐字） |
|---|---|---|
| ★★ **A 组** | ★ `M scripts/sw_part.py`（草图图元补 `_MM_TO_M` · `add_dimension` 补换算 · `add_sketch_relation` 白名单化）· ★ `?? scripts/sw_sketch_relations.py`（新增） | ★★ **「可认领」**；★ **但合并/提交仍由 merge owner 单点执行** ⇒ ★★ **本会话只读它、不覆盖它** |
| ★★ **B 组** | ★ 其余（含 `M AGENTS.md` · `M docs/*` · `?? .codebuddy/` · `?? .workbuddy-ai/` · ★ 本会话新增的 `archive/` 与 `specs/294–301`） | ★★★ **「标『未知权属 ⇒ 禁止覆盖』—— 既不当成自己的，也不清理、不暂存、不还原」** |

★★★ **三条硬规矩**（★ D6 逐字，★ 本会话继续遵守）：★ ① **禁 `git add -A`**；★ ② **禁裸 `git commit -m "<多行带引号>"`**；★ ③ **任何槽位不得触碰 B 组里的任何路径**。

---

## 三、★★★ 本轮允许写入的文件（★ 计划 §6.1 第 2 步「明确本轮允许写哪些文件」）

★ 依铁律 3 的顶层白名单与计划 §5 的建议落点，**本轮只写这些**：

| ★ 类 | ★ 路径 | ★ 说明 |
|---|---|---|
| ★ **本特性目录** | `specs/302-ec00-trustworthy-tool-base/**` | ★ 四件套 + `contracts/` + `data-model.md` + `research.md` + `quickstart.md` + `baseline.md` + `checklists/` |
| ★ **判据** | `tests/test_ec00_*.py` | ★ **拟新增**（★ 计划 §10.4 已逐条登记 24 个拟用测试名） |
| ★ **能力实现** | `scripts/`（★ **扩展现有模块为主**） | ★ 计划 §4 逐项给了首选落点（★ 优先扩展、职责确实不同才新增） |
| ★ **知识文档** | `docs/` | ★ 收口时的报告与生成物 |
| ★★ **禁止写** | ★ B 组任何路径 · ★ `AGENTS.md` 的**纪律正文**（★ 只能按 `agents-md-maintenance` 走） · ★ `.gitignore` · ★ `.codebuddy/` · ★ `.workbuddy-ai/` | ★ D6 ③ + 红线 |

---

## 四、★★★ 起点状态（★ 计划 §2「可复用基线与不能默认成立的事」）

| ★ 范围 | ★ 已有组件 | ★ **不表示** |
|---|---|---|
| ★ 工具契约 | ★ `mcp-server/tool_registry.py`（`Param` :292 · `ToolSpec` :330 · `check_spec` :414）· `capabilities.yaml` | ★ 不证明每条公开路径可信 |
| ★ 零件/草图 | ★ `scripts/sw_part.py` · `scripts/sw_sketch_relations.py` | ★ 单位未闭合 · 关系生效未回读 |
| ★ 执行 | ★ `tools/tool_caller.py` · `tools/sw_guard.py` | ★ 超时后状态未定义 |
| ★ 效果/前置 | ★ 原 ToolSpec/效应/预检模块 | ★ 未与工程语义连接 |
| ★ 引用选择 | ★ `scripts/sw_selection_spec.py` | ★ 无语义锚点/几何签名 |
| ★ 比较/验收 | ★ `scripts/delivery_compare.py` · 指纹组件 | ★ 无独立 oracle |
| ★ 工程图 | ★ `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` | ★ 无功能尺寸/基准验收 |
| ★ 门禁 | ★ `tools/round_chain.ps1` · `release_check.py` | ★★ **`round_chain.ps1` 有副作用**（★ 见 §五） |

★★ **接收基线仍有未解决项**（★ 计划 §2 逐字）：草图关系正式注册与契约测试 · 单位待复核清单 · 关系效果不稳定 · 关窗/文档计数 · 采样表示的适用边界。★★★ **「不能只凭上一轮文字记载将它们清零」**。

---

## 五、★★★ 已发现的**副作用风险**（★ 计划 §6.2 点名，★ 本会话实测复核）

| ★ 项 | ★ 实测读数 | ★ 计划要求 |
|---|---|---|
| ★★ `tools/round_chain.ps1` | ★ **L84 / L117 / L150 三处 `git add -A`** · ★ **L199 `reclaim_solidworks.py --close`** | ★★★ **「收尾链不是纯只读脚本」** ⇒ ★ **T029 必须先拆「生成与验证」与「提交与资源处置」**，★ **拆分前不直接运行整条链** |
| ★ `reclaim_solidworks.py --close` | ★ 自带文档判定（★ **有一个不是自己开的文档就拒绝关闭**） | ★ 相对安全，★ 但仍属「资源处置」阶段 |

★★★ **⇒ 本会话纪律**：★ **不跑整条 `round_chain.ps1`**；★ 改用 `release_check.py` + 聚焦 pytest（★ 与 `AGENTS.md` §十六 一致）。

---

## 六、★★★ 九份 `ENGINEERING_*` 草案的裁定（★ 直接引用 `DSH_DECISIONS.md` **D8**）

> ★★ **判为「参考草案、不是契约、不得勾成完成」**。理由：正式 spec 要求**来源 + 许可 + 可运行验收**三项齐；★ 本轮**未逐份核对**这三项 ⇒ ★ **一律不当契约引用**。
> ★ **`compat_buckets.needs_owner_decision` 里的「草案达标裁定」一律保留为 `unknown`** —— ★ **不得因为业主说"你决定"就把它判成达标** ✗（★ 那是**事实缺口**，不是**决策缺口**）。

★★★ **⇒ 本特性的处置**：★ 把五份 P0 草案**整理成正式 spec 302 的四件套与配套**（★ 那是**立项动作**，★ 不是「勾成完成」）；
★ 而 ★ `needs_owner_decision` 的 6 条**保持 `unknown`**（★ 见 §七）。

---

## 七、★★ 仍需业主确认的 6 条（★ 保持 `unknown`，★ 不冒充）

★ 来源：`output/DSH_EXISTING_CONTRACTS.json` 的 `compat_buckets.needs_owner_decision`（★ 逐字）：

| # | ★ 待确认 | ★ 本会话处置 |
|---|---|---|
| ① | ★ MCP 传输口径（479 vs 504 vs 339）与是否包含 `new_document`/`save_document`/`close_documents` | ★★ **本轮实测已澄清一部分**：★ `all_specs()` = **479** · ★ 真 JSON-RPC `tools/list` = **524**（= 479 + 45 装饰器）⇒ ★ **登记读数、口径仍待业主确认** |
| ② | ★ `feature.json` 指针状态（003 / 207 重号 / 221 缺目录） | ★★ **本轮修 `feature.json` 指向本特性**；★ 207 重号**保留** |
| ③ | ★ worktree/隔离方式 · `writeScopes` 语义 · `output/` 是否用于交付 | ★ **沿用 D3**（★ 不建 worktree · staging 隔离） |
| ④ | ★ `route.model.deepseek_v41_flash` / `route.model.hy4` 是否存在 | ★★ **保持 `unknown`**（★ D1 逐字：「**不编造 model ID**」） |
| ⑤ | ★ 并发上限（平台上限未知 · 40 路能否成立） | ★★ **沿用 D2**（★ 只读 6 路 · COM **1 路严格串行**） |
| ⑥ | ★ `output/ENGINEERING_*.md` 九份草案的处置 | ★★ **沿用 D8**（★ 参考草案 · 不当契约） |

---

## 八、★★ G0 判据（★ 计划 §1.4）

| ★ 门 | ★ 放行条件 | ★ 本文件是否满足 |
|---|---|---|
| **G0 基线** | ★ 权属和起点明确；★ **没有覆盖别人的改动** | ★★ **满足** ✓ —— ★ 编号 **302**（无冲突）· ★ 权属按 D6 分组 · ★ 写入面已列 · ★ **未触碰 B 组** |

★★★ **⇒ G0 通过** ⇒ ★ 可进入 **G1（需求冻结，T002–T005）**。
