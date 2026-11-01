# 规格 353 · 目标栏（唯一进度字段）

> ★ 进度只看上面那一行；其余段落是上下文，不是判据。

**阶段：**★ **收口（T-353-01 … T-353-18 全部完成）** —— 台账 **523/543** 已核（**人工 190 · 自动 333**）·
基线待核 **20**（全部是复核人判定的**描述与实现/官方不符**，逐条在 `defects.md`）·
门禁硬接线 · `release_check` rc=0 · `round_chain` 绿 · 下一步 = 另立规格修那 20 条缺陷

---

## 一 · 业主指令（本规格唯一来源）

> 「把**所有 mcp 工具都过一遍**，**无法过门禁的修改好**。修改的时候**不能根据记忆和印象，
> 必须去 SolidWorks 官方 API 文档对照着自己的文档确认这个工具到底是干什么的**……
> 这个要求**必须落成机械门禁**。」

## 二 · 读数（详见 `spec.md` §1.2）

| 读数 | 值 |
|---|---|
| 工具面（真握手） | **543**（498 声明式 + 45 手写） |
| 新 builder 的 schema 门禁 | **543/543 通过**（0 违规；每工具 2 条 `$defs/$ref` 建议） |
| 描述里有「Use when…」 | **0/543**（新 builder 的警告项） |
| 实现里有官方页路径 | **7 / 494** |
| 官方成员反查覆盖 | 1427 处引用 / 318 个名字，**79 个查不到页**（Simulation/Topology/Costing 三个 add-in） |
| **有官方依据台账** | **523 / 543**（人工 190 · 自动 333）· 基线待核 **20** |
| 复核发现的缺陷 | **20 条**（见 `defects.md`；本规格只登记、不改实现） |
| 查不到页的成员（已记账） | **33 处**（126 → 102 → 33；逐棵离线源查过，`gap` 写明结论形态） |

## 三 · 落地形态

- 门禁：`scripts/check_tool_official_claims.py`（第 66 道，**hard**）——
  判据 `no-record` / `impl-missing` / `member-uncited` / `page-missing` / `page-mismatch` /
  `anchor-not-found` / `claim-mismatch` / `claim-unanchored` / `unverified` / `unknown-tool`。
- 生成器：`tools/gen_tool_official_claims.py`（草稿；`_` 前缀，门禁不读）。
- 台账：`docs/tool-official-claims/<批次>.json` + `README.md`（写者须知）。
- 基线：`docs/tool-official-claims-baseline.json`（**只承载待核工具名**，只许降）。
- 自证：`tests/test_tool_official_claims_gate.py`（7 条反例全部被拒）。

## 四 · 试点发现的真缺口（只登记，本规格不改实现）

1. `solidworks_extrude_midplane` 的「每侧一半」**官方页没写** —— 证据在真机包围盒
   （`tools/capture_feature_build_evidence.py`）⇒ 台账 `claim_evidence.kind=runtime`。
   官方只给 `swEndConditions_e.swEndCondMidPlane = 6`（`C:\swapi\enums\swEndConditions_e.md`）。
2. `solidworks_sketch_add_slot`：官方 `Width` 是**槽宽**，实现传 `2*radius` ⇒ 与「radius 是
   槽宽一半」一致（`ISketchManager.CreateSketchSlot.md` Parameters 段）。
3. 79 处成员在本机离线文档树里**查不到页**，集中在 Simulation/Topology/Costing
   ⇒ 按铁律 5 记账，不许编页。

## 下一个动作（只写一条）

★ **本规格已收口**。下一步（**另立规格**）：处理 `defects.md` 的 20 条 —— 它们要么改模型可见描述
（改完 `claim` 与 `evidence` 同步），要么改实现（需真机验证）。★ 在那之前，这 20 个工具保持
`no-record`：台账不替它们编证据。
