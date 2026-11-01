# 规格 353 · 任务清单

> 进度**只写** `goal-bar.md`。完成一条勾一条；每条都写「验收」，验收不成立不许勾。

## P0 · 门禁 + 台账骨架 + 试点（Lead）

- [x] **T-353-01** 立 `scripts/check_tool_official_claims.py`（判据见 `spec.md` §二）
  - 验收：`python -B scripts/check_tool_official_claims.py --report` 能报出 543 个工具的分母
- [x] **T-353-02** 立 `tools/gen_tool_official_claims.py`（草稿生成器：抠成员 + 找官方页 + 抄原始描述行）
  - 验收：`--all` 生成 542 条草稿、0 条崩；未解析成员逐条列出
- [x] **T-353-03** 棘轮基线 `docs/tool-official-claims-baseline.json`（**只承载待核清单**）
  - 验收：写基线后门禁 rc=0；把某工具从台账删掉再跑 ⇒ 仍是 `no-record` 且被基线吸收
- [x] **T-353-04** 双侧负例 `tests/test_tool_official_claims_gate.py`（7 条反例自检）
  - 验收：`pytest tests/test_tool_official_claims_gate.py -q` 全绿；★ 每条反例对应一个真实错法
- [x] **T-353-05** 试点 `docs/tool-official-claims/P0-pilot.json`（4 个拉伸/槽工具，逐条读官方页）
  - 验收：`--only <4 个> --report` ⇒ 已核 4/4、违规 0

## P1 · 接线（Lead）

- [ ] **T-353-06** `release_check.py` 加 `_run_tool_official_claims_gate`（硬门禁）+ 返回体
- [ ] **T-353-07** `docs/gate-classification.json` 登记 `hard`
  - 验收：`python -B scripts/check_gate_wiring.py` rc=0；`release_check` rc=0
- [ ] **T-353-08** 台账格式说明 `docs/tool-official-claims/README.md`（写者照抄）

## P2 · 批次核验（每批一个写者，8 批）

- [ ] **T-353-09** B1 实体特征（拉伸/旋转/孔/圆角倒角）
- [ ] **T-353-10** B2 草图族
- [ ] **T-353-11** B3 装配族
- [ ] **T-353-12** B4 工程图族
- [ ] **T-353-13** B5 钣金/焊件/模具/曲面
- [ ] **T-353-14** B6 仿真/拓扑/成本（★ 79 处查不到页在这里，逐条记账）
- [ ] **T-353-15** B7 读取/属性/导出/视图
- [ ] **T-353-16** B8 编排与门面（无 COM 成员，`claim_evidence.kind=impl`）
  - 每批验收：该批 `no-record` 归零；`member-uncited` 0；查不到的成员有 `documented:false` + `gap`

## P3 · 收口

- [ ] **T-353-17** 全量 `--strict` 复核（543/543 有台账且零违规）
- [ ] **T-353-18** `release_check` 全绿 + `round_chain` 绿 + 按路径提交
