# 规格 352 · 任务清单

> 进度**只写** `goal-bar.md`。本文件是逐任务 checklist，完成一条勾一条。
> ★ 每个任务都写「验收」，验收不成立就不许勾。

## P0 · 契约 + 门禁 + 基线（Lead，独占写盘）

- [ ] **T-352-01** 立 `scripts/check_tool_contract.py`
  - 判据 K1–K5、K9（见 `spec.md` §二）；**复用** `check_lean_first_line_caveat.lean_first/judge`，不重写
  - 支持 `--report` / `--only <name>` / `--baseline <path>` / `--json <path>`
  - 验收：对当前 498 条跑出**与 `output/_audit_tool_docs.json` 逐条一致**的首句/长度读数（交叉核对，防口径漂移）
- [ ] **T-352-02** 生成棘轮基线 `docs/tool-contract-baseline.json`
  - 记 `{"violations": {工具名: [判据…]}, "counts": {...}}`；门禁判据 = **只许降**
  - 验收：`check_tool_contract.py` 读基线后退出 0（当前状态绿）；手改一条 `doc` 造违规 ⇒ 退出 1
- [ ] **T-352-03** 接线三处：`release_check.py` 调用 + `_gate_results` + 返回体；`docs/gate-classification.json` 登记 **hard**
  - 验收：`python -B scripts/release_check.py` rc=0 且**多出这一段**；`check_gate_wiring.py` 绿
- [ ] **T-352-04** 双侧负例 `tests/test_tool_contract_gate.py`
  - 「该报」：元数据首句 / 中文首句 / 首句 >120 / 参数无说明 / 参数说明无句号
  - 「不该报」：合规英文两句 / 参数说明带 `defaults to` / `Read-only.`
  - 验收：`pytest tests/test_tool_contract_gate.py` 全绿；★ 每类至少 1 正 1 负

## P1 · 证据字段 + 迁移器

- [ ] **T-352-05** `ToolSpec` 加 `evidence: str = ""`（非模型可见；`make_tool_function` 只用 `doc`）
  - 验收：`tests/test_tool_registry.py` 仍绿；`tools/list` 的 `description` 里**不出现** `evidence` 内容（采样 10 条）
- [ ] **T-352-06** `tools/migrate_tool_evidence.py`（`--dry-run` / `--apply` / `--verify`）
  - 做：把每个 spec 的旧 `doc` **逐字**写进 `evidence=`，并把 `doc` 换成新文本（新文本来自映射文件）
  - 验收：`--verify` ⇒ 498 条 `old_doc in evidence` **丢失 0**；`--dry-run` 不写盘

## P2 · 评测基线

- [ ] **T-352-07** 题集 `specs/352-.../eval-tasks.json`：**≥40 题**，覆盖 8 域，**中文提问**，每题带 `want_tool` + `want_args` + 5 题**弃权题**
  - 复用 `tools/probe_tool_rag_cn_vs_en.py::TASKS` 的 24 题作为种子
  - 验收：题集自检脚本（每题 `want_tool` 在 `all_specs()` 里、`want_args` 通过真实 input model 校验）
- [ ] **T-352-08** `tools/eval_tool_selection.py`：真实 `tools/list`（stdio 握手）→ 拼 prompt → 调模型 → 按 D-9 口径判
  - 验收：`--run --tag baseline` 落 `output/tool-selection-baseline.json`；含**原始输出**与逐题判定

## P3 · 试点（★ 用证据决定语言与句式）

- [ ] **T-352-09** 24 条样板：**英文版 + 中文版**各一套（中文版不用 `。`）
  - 验收：两套都通过 P0 门禁（中文版需临时豁免 K1 的语言项，作为实验分支记录）
- [ ] **T-352-10** 试点评测：现况 / 英文 / 中文 三组，同一 24 题
  - 验收：`specs/352-.../pilot.md` 给出三组准确率 + 结论；★ 若中文胜出则**改 D2** 并记录理由

## P4 · 全量改写（并行）

- [ ] **T-352-11** 把 117 个批次文件按体积均衡切成 **8 组**，写进 `specs/352-.../groups.json`
- [ ] **T-352-12** … **T-352-19** 每组一个执行者：改写 → 自跑 `check_tool_contract.py --only` → 报「改了几条 / 剩余几条 / 有疑义的条目」
  - 验收（每组）：该组文件 `doc` 零违规；`evidence` 零丢失；`python -B scripts/release_check.py` 该组相关段不红
- [ ] **T-352-20** Lead 抽检 ≥30 条：把 `doc` 里的断言与官方页/实现逐字对照，落 `specs/352-.../spotcheck.md`

## P5 · 收尾

- [ ] **T-352-21** 全量评测（`--tag after`），与 baseline 并列成表
- [ ] **T-352-22** `tools/measure_lean_catalog.py` 前后对照落盘
- [ ] **T-352-23** 45 个 legacy 工具补 `params.type`（K7）
- [ ] **T-352-24** `release_check` 全绿 + `round_chain` 绿
- [ ] **T-352-25** 回写 `docs/ROADMAP.md` 游标 + 按路径提交
