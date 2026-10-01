## 二之补 R 编号登记表（**R1–R14 的唯一登记处**，2026-10-01 轮 193 加）

> ⚑ **为什么补这一节**（轮 193 实测）：
> ```
> · 门禁 `scripts/check_union_conventions.py` 引用 **R1–R14**（14 个编号）
> · 而**代码仓库里此前没有任何一处**说明 R1–R11 是什么 ——
>   它们的权威定义在**另一个仓库**的 `capabilities-schema-proposal.md`（起草时的方案文件）
> · 反过来，**R12 / R13 / R14** 是后来（轮 58 / 59 / 67）加的，**那份提案里没有它们**
> ⇒ ★★ 两个方向都缺：读代码的人**无法核验这些编号代表什么**。
> ⇒ ★ 本节把它们**一次登记齐**，并写明**每条由哪段门禁守**、**权威出处在哪**。
> ```
> ⚠ **本表是**手写**的（因为它含判断与出处），但**编号集合**由一条门禁守**：
> `check_rule_registry()` 保证「门禁段名里引用的每个编号都在本表内」且「本表无缺号」。

| 编号 | 含义（一句话） | 由哪段门禁守 | 权威出处 |
|---|---|---|---|
| **R1** | `capabilities.yaml` 的 `schema_version` 等于约定值 | 「清单形状」段 | 提案 §五（**工作区仓库** `D:/AI/SW/docs/capabilities-schema-proposal.md`） |
| **R2** | 每条 `level` ∈ 五值枚举；且 `scripts/capabilities.py` 的 `VALID_LEVELS` 与本门禁的集合一致 | 「清单形状」段 | 同上 |
| **R3** | `id` 全局唯一且是稳定 slug（`^[a-z][a-z0-9_]*$`） | 「清单形状」段 | 同上 |
| **R4** | 能力条数 ≥ 10 | ★ **`scripts/release_check.py` 的现有断言**（本门禁不重复守） | 同上 |
| **R5** | `verified` ⇒ `evidence` 非空；`backends` 含 CAD 后端时另要 `verified_versions` 非空 | 「验证等级与授权」段 | 同上 |
| **R6** | `level == source_verified` ⇒ `provenance` 非空；带 `provenance` 的条目 `repo` 必须是 `owner/repo`、`license` 在白名单 | 「清单形状」段 | 同上 |
| **R7** | `not_implemented` ⇒ `limitations` 非空 | 「验证等级与授权」段 | 同上 |
| **R8** | 等级审计 `docs/union-level-audit.md` **不得出现「高报」**；且它是**生成物**（重跑必须逐字一致） | 「规范与地图存在性」段（读生成物 + 新鲜度） | 同上 + 本文件 §三 的生成物口径 |
| **R9** | `provenance.files` 为非空数组；`commit`/`tag` 可省或为空串，若出现必须是字符串 | 「清单形状」段 | 同上 |
| **R10** | `provenance.files` 不得落在 `angelsix/solidworks-api` 的 `References/` 下（那是 MIT 仓里被点名的例外） | 「清单形状」段 | 同上 + `docs/sources.md` 的许可例外段 |
| **R11** | `allowed_modes` ⊆ {`interactive`,`reviewed`,`unattended`}；且 `level != verified` ⇒ 不得含 `unattended` | 「验证等级与授权」段 + 「授权真源」段 | 同上 |
| **R12** | `source` 标记的**枚举**（回答「这条是**并入来的**还是**本项目自研的**」）+ 依据非空 | 「清单形状」段 | 代码注释（轮 58 加）—— ⚠ 提案未收录 |
| **R13** | `source` 与 `provenance` 必须**自洽**（`original` 却有 `provenance` ⇒ 报自相矛盾） | 「清单形状」段 | 代码注释（轮 59 加）—— ⚠ 提案未收录 |
| **R14** | 「**不做 + 原因**」：`docs/union-not-doing.json` 的每条都要有 `subject`/`reason`/`evidence` | 「A1 的另一半」段 | 本文件 §二 的 R14 小节（轮 67 加）—— ⚠ 提案未收录 |

**⚠ 两条如实记的限度**：
1. **R4 不在本门禁里守**（它由 `release_check.py` 的既有断言守）⇒ 本门禁的段名里**不出现 R4**，
   所以 `check_rule_registry()` 的「引用 ⊆ 登记」这一半**覆盖不到 R4** —— 它靠**本表**登记，
   靠**另一道断言**执行。★ 这是**分工**，不是遗漏（`check_rule_registry` 的文档串里写明了）。
2. **提案与代码已分叉**（提案 R1–R11 · 代码 R1–R14）⇒ ★ 本节是**代码仓库内的权威**；
   提案在**另一个仓库**，本仓库**不该**依赖它（别的机器上没有）。
