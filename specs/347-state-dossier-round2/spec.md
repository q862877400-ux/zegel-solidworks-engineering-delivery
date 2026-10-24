# 规格 347 · 项目现状记录 第二轮（深度对应关系）

**Created**: 2026-10-24
**Status**: 进行中（K 维度已交付）
**触发**：业主 2026-10-24 指令 ——「项目了解透彻了吗，没有的话继续自动化 spec 运行」。

---

## §1 为什么要有第二轮

第一轮（`docs/state/facts/A–J`）记的是**结构信号**：多少条、多大、有没有、断没断。
它没有回答一个更硬的问题：**声明的东西在代码里对不对得上**。
⇒ 第二轮只做这一类：**可证伪的对应关系**。

---

## §2 五个维度（K–O）与判据

| 维度 | 要核的对应关系 | 判据（可跑） |
|---|---|---|
| **K** | `ToolSpec` 声明 → `scripts/` 里的真实函数与签名 | AST 静态解析；**不 import**（避免触发 COM） |
| **L** | `capabilities.yaml` 的 100 条 `verified` → 其 `evidence` 指向的文件/命令是否真实存在 | 抽样 + 逐个 `Path.exists` / 命令可执行性 |
| **M** | 测试的**执行期**结果（第一轮只到收集期） | `pytest` 真跑；5 个 `GateError` 阻断文件单独统计用例数 |
| **N** | 仓库外来源（`C:\swprojects\` 克隆）与尚未触碰的目录（`apps/` `dotnet/` `ai_team/` `subskills/` `references/`） | 目录扫描 + 许可读原文 |
| **O** | 文档归并（业主已授权自主执行） | 每次归并写一行记录：合并了什么、落到哪、删了什么 |

---

## §3 K 维度交付物（2026-10-24）

- 探测器：`docs/state/probes/probe_specs_vs_code.py`
- 事实文件：`docs/state/facts/K-signature.md`
- 机器可读：`docs/state/inventory-k.json`
- 读数摘要：501/501 解析成功；`inject` 与声明参数**零错配**；79 条存在「函数有、声明面没有」的形参，
  其中 34 条有 `derived_args`（可能由其补齐，未证实）、**45 条没有**（形参自声明面不可达）

---

## §4 记录员口径（与第一轮一致，不因第二轮改变）

只写观察到的事实与可复核读数；**不判断**对错、**不给**优先级、**不给**修复建议。
`derived_args` 是否真的补上了某个形参，**未证实就写未证实**。

---

## §5 收工判据

1. K–O 五个维度各一份 `docs/state/facts/<X>-*.md`，每条事实带证据与未确认；
2. `docs/state/INDEX.md` 增加 K–O 的导航行与「最承重读数」；
3. 每轮 `python scripts\release_check.py` 为 EXIT 0；
4. 全程只读探测；唯一写入面是 `docs/state/`、`specs/` 与 `docs/state/probes/`。
