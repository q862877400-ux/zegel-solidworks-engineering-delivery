# 假设台账（Assumption Ledger）

**为什么有这个文件**：本仓库已有两本台账——`docs/known-facts.md`（**已验证**的技术事实）与 `docs/dead-ends.md`（**已验证失败**的路径）。两者都在「已」这一侧。本台账记**未**侧：我假设了、但还没验证的东西。

**来源**：`docs/text-to-cad-lessons-verdict.md` §6.3（经验⑤「不追问但记录」的改造后采纳形态）。

**判据**（由 `scripts/check_assumption_ledger.py` 机器强制）：

1. 每条必须有 `id` / `档位` / `状态`，三者都在封闭词表内；
2. `confirmed` / `refuted` **必须带证据**——「已验证」不能是空话；
3. `open` 的假设**不得**出现在 `capabilities.yaml` 里 `verified` 条目的 `evidence` 中——**未验证的假设不能当证据**。

**档位**（对应上游 `skills/sdf/references/llm-guardrails.md:28-34` 的五档来源枚举，落成本仓四档）：

| 档位 | 含义 | 上游对应 |
|---|---|---|
| `1-user` | 用户明确给的 | user-provided requirement |
| `2-official` | 官方文档/出厂类型库/上游仓库里查到的 | upstream geometry / target docs |
| `3-measured` | 本机实测或算出来的（方法须写明） | measured or calculated value with method stated |
| `4-assumption` | 我推断的，无直接来源 | explicit assumption recorded in the ledger |

**状态**：`open`（未验证）· `confirmed`（已验证，附证据）· `refuted`（已证伪，附证据）。

---

## 台账

| id | 假设内容 | 档位 | 状态 | 证据 |
|---|---|---|---|---|
| AS001 | `output/` 与 `specs/` 里的数字属存量，不应被「事实来源分级」门禁强制改造 | 2-official | confirmed | `scripts/check_provenance.py:11-13`（存量豁免范式）+ `docs/text-to-cad-lessons-verdict.md` §1.3 |
| AS002 | `capabilities.yaml` 的 `provenance` 只用了 1 条是规则使然，不是欠账 | 2-official | confirmed | `docs/capabilities-schema-proposal.md` 的 level 表格 + `scripts/check_union_conventions.py:237`；实测 `level` 分布 `verified` 100 / `stitched` 37 / `not_implemented` 3，`source_verified` 为 0 |
| AS003 | 「几何关系断言化」（`check_spec()` 模式）在本仓库没有落点 | 3-measured | confirmed | 本仓为能力仓库而非零件仓库：`output/` 的 `.py` 多为一次性探针，`specs/` 为规格文档不可执行；见 `docs/text-to-cad-lessons-verdict.md` §3.2 |
| AS004 | 本仓库的视觉验证已强于上游「强制截图」政策 | 4-assumption | open | 待核：`shot.py` / `ctl.py` 与 `tools/sw_guard.py` 的实际覆盖范围未逐项对照上游 `snapshot-review.md` 的三条要求 |
| AS005 | `check_fact_provenance.py` 的量化断言正则不会在生产文档里产生大量假阳性 | 3-measured | open | 待核：目前只在 `docs/*.md` 增量上跑过一次（2 处命中且均为真阳性），样本量不足以判断长期假阳性率 |
| AS006 | 上游 `llm-guardrails.md` 写在 `skills/sdf/`（机器人描述）而非 `skills/cad/`，其「不信任 agent 静默推断」的结论可推广到 CAD 建模任务 | 4-assumption | open | 同一仓库同一批 skills，措辞通用（`agents are useful at structuring... and weak at silently deriving precise spatial... values`），但源码未明说适用于 CAD |
| AS007 | 本仓库的 `round_chain.ps1` 在新增两道门禁后仍能全绿 | 3-measured | confirmed | `pwsh -File tools/round_chain.ps1 -Tests tests/test_fact_provenance_gate.py` ⇒ exit 0，测试 8 passed；`-Tests tests/test_assumption_ledger_gate.py` ⇒ exit 0，测试 10 passed；`python scripts/release_check.py` ⇒ exit 0，两道新门禁均为 `pass` |
| AS008 | 两道新门禁在**真实破坏**下确实会红（不是恒绿的摆设） | 3-measured | confirmed | 破坏测试：把 AS001 的 `confirmed` 证据改成 `-` ⇒ exit 1；让某条 `verified` 能力的 `evidence` 引用 `open` 假设 AS004 ⇒ exit 1；还原后 ⇒ exit 0 |
