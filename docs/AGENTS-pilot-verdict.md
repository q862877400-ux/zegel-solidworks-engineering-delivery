# 裁断：`pilot` 迁移走选项 A

**结论**：走 A —— 13 条有证据的迁 `verified` 并同批补 `evidence`；6 条无证据的迁 `stitched`；`allowed_modes` 加 `unattended`，原 8 条 `verified` 补、原 19 条 `pilot` 不补；`unattended_allowed()` 改看 `allowed_modes`。

## 三条追加要求（裁断的一部分，不是建议）

**一、13 条同批补 `evidence`**：可以是「跑过它的命令或脚本名 + 结果摘要」，不要求重新跑一遍；缺则 B4 立刻红。

**二、必须附等价性验收测试**：`unattended_allowed()` 为真的 capability_id 集合，迁移前后逐条相同。

**三、同批改 `unattended_allowed()` 的全部调用点与相关测试文件**：缺一即红。

## 不选 B / C 的理由

**不选 C**：同一份数据里不能同时出现「跑过 2024/2026」与「从未运行」—— 错报不是保守。

**不选 B**：保留第六级 `pilot` 等于保留「两个事实共用一个字段」这个腐坏源。

## 你报告 §六 那件事

**`provenance` 暂无处可加（现有 28 条全自研，落地等 B 级并入）**：裁断方确认不是问题、是顺序，按你报告里的顺序做即可。

## 分工

**具体落地归你**：改 `VALID_LEVELS`、删 `pilot` 豁免、迁数据、过 13 个测试文件、bump `schema_version`。

**裁断方只管形态与验收判据。**

本裁断已写进 `docs/capabilities-schema-proposal.md` 的 §1.2 与 §五 R11；一处事实一个家，以那份为准。
