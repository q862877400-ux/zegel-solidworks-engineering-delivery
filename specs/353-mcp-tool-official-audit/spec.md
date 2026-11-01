# 规格 353 · MCP 工具官方依据台账（把「不许凭记忆」落成机械门禁）

**Feature Branch**: `353-mcp-tool-official-audit`
**Created**: 2026-11-01
**Status**: In progress（P0 门禁 + 试点已落地；批次核验进行中）

> **业主原话（本规格的唯一来源，2026-11-01）**：
> 「我新的 MCP builder 改了，你把我们这个项目的**所有 mcp 工具都过一遍**，
> **无法过门禁的修改好**。记得修改的时候**不能根据记忆和印象，必须去 SolidWorks
> 官方 API 文档对照着自己的文档确认这个工具到底是干什么的**。这是多轮任务，
> 你按照 spec 规范**一批一批**来。……**这个要求必须落成机械门禁**。」

---

## 一 · 为什么有这条规格

### 1.1 同一个病，已经复发过

| 时间 | 病灶 | 当时的处置 | 结果 |
|---|---|---|---|
| 2026-10-01 | 凭印象写 COM 成员名（9 次：`IDisplayDimension.GetValue` / `ISectionViewData.AccessSelections` 等） | `scripts/check_member_names.py`（名字存在性） | ★ 只治「名字在不在」，不治「这工具到底在干什么」 |
| 2026-10-26 | 工具描述是变更日志，模型看不懂 | `specs/352`（描述成品化，契约门禁 K1–K10） | ★ 治了「描述形态」，**没治「描述内容有出处」** |
| 2026-11-01 | 改描述时仍可能**凭记忆**写语义 | **本规格** | —— |

★ 结论：前面两道门禁都只判**形态**（名字存在 / 句子合规）。**语义有没有官方出处**，
此前没有任何机器判据 —— 全靠「我记得我查过」。这正是业主点名的那个缺口。

### 1.2 实测基线（2026-11-01，命令见每条「复现」）

| 读数 | 值 | 复现 |
|---|---|---|
| 工具面（真 MCP 握手） | **543**（498 声明式 + 45 手写） | `python -B -c "from tools.mcp_tools_list import tools_list; print(len(tools_list()))"` |
| 新 builder 的 schema 门禁 | **543/543 通过**，0 违规；每工具 2 条 `$defs/$ref` 建议 | `node …/check-mcp-schema.cjs --tool output/mcp-tools-list.json --server-name solidworks` |
| 新 builder 的「Use when…」项 | **0/543** 描述里有「何时用」 | 同上 `--tool` 单条模式（每条 1 条警告） |
| 实现函数里**有官方页路径** | **7 / 494** | `tools/gen_tool_official_claims.py` 的成员提取 + `docs/state` 探针 |
| 实现 docstring 里的「官方引文」 | 244 条，**裸比对命中 0**（markdown `**` 打断） | 见 §三 D2 的归一化 |
| 官方成员反查表覆盖 | 成员引用 **1427 处 / 318 个不同名字**，其中 **79 个**在 `C:\swapi\types` 里查不到页 | `python -B tools/gen_tool_official_claims.py --all` |
| 查不到页的成员分布 | `sw_topology` 39 · `sw_simulation` 26 · `sw_simulation_results` 16 · `sw_costing` 13 · `sw_simulation_study` 9 · 其余 4 | 同上 |
| **有官方依据台账的工具** | **0 / 543**（本规格 P0 前） | `python -B scripts/check_tool_official_claims.py --report` |

★ 「79 个查不到页」不是小数字：它们集中在 **Simulation / Topology / Costing 三个 add-in**
（本机离线文档树 `C:\swapi\types` 只覆盖 `sldworks` 与部分 `cosworks`）。按铁律 5，
这些**不许编页**，必须在台账里写成「查不到 + 查过哪些源」，并计入已核清单的缺口。

---

## 二 · 判据（全部机器可判，落在 `scripts/check_tool_official_claims.py`）

台账：`docs/tool-official-claims/<批次>.json`（每批一个文件、**写者不相交**）。
以 `_` 开头的是生成器草稿，**门禁不读**。

| 代号 | 判据 | 治哪种错 |
|---|---|---|
| `no-record` | 工具在 `tools/list` 里，台账没有它 | 没查 |
| `impl-missing` | `impl` 指向的 `<文件>:<函数>` 不存在 | 台账过期 |
| `member-uncited` | 实现里调用了成员，台账没登记（含 `allowed_non_com` 写了却没理由） | **漏查** |
| `page-missing` | 登记的官方页不存在 | 编页 |
| `page-mismatch` | 页 front-matter 的 `type`/`member` 与登记不符 | **指错页** |
| `anchor-not-found` | 锚点在所指文件里**逐字**找不到（归一化后） | **伪造引文** |
| `claim-mismatch` | 台账 `claim` ≠ 工具 `doc` 首句 | 台账说的 ≠ 模型看到的 |
| `claim-unanchored` | `claim_evidence` 缺失或锚点找不到 | 语义没出处 |
| `unverified` | 没有 `verified.by` / `verified.at` | 没人核过 |
| `unknown-tool` | 台账有、注册表没有 | 改名后没同步 |

★ `member-extra`（台账多登记）**只进报表**，不进判据：更深一层的帮手函数合法。

### 2.1 棘轮

`docs/tool-official-claims-baseline.json` **只承载 `no-record` 的待核清单**。
已有台账的记录一律**硬判** —— 半成品记录不许借基线蒙混。核完一个工具就从
`pending` 删一个 ⇒ **清单只降**（`--write-baseline` 拒绝上涨）。

### 2.2 它**不能**保证什么（诚实边界）

* 锚点存在 ≠ 语义正确。本门禁消灭的是**引用类错误**（编引文 / 指错页 / 漏查成员），
  语义那一关仍是「核验人真读了官方页」，落成 `verified.notes` 供复核。
  （同 `dsh-mcp-builder/references/claim-verification.md` §六）
* 成员提取只跨**一层**仓内委托（薄封装工具 252 个靠这条）。更深一层的成员
  靠核验人补登（门禁对「多登记」只提示、不拦）。

---

## 三 · 决策

| # | 决策 | 依据 |
|---|---|---|
| **D1** | ★★ **台账是人写的工件，草稿是机器写的**（`_` 前缀隔离） | 机器只做「抠成员 / 找官方页 / 抄原始描述行」；语义由人读页确认 —— 机器抄的锚点不许冒充人核过 |
| **D2** | ★★ **锚点比对先归一化 markdown 排版**（去 `**`/反引号/列表符、压空白、小写） | 实测：244 条 docstring 引文**裸比对命中 0**，归一化后命中 —— 裸比对会把真引文判成伪造，那种门禁会被关掉 |
| **D3** | ★ **`claim` 必须逐字等于工具 `doc` 首句** | 否则「台账说的」和「模型看到的」是两句话，核验白做 |
| **D4** | ★ **`claim_evidence.kind` 三档**：`official` / `impl` / `runtime` | 有些语义官方页确实没写（如中面「每侧一半」），但本仓**真机包围盒**有证据；分档让复核者知道该信谁 |
| **D5** | ★ **成员提取只跨一层** | 再深就是猜调用图；猜正是本门禁要治的病 |
| **D6** | ★ **查不到官方页的成员写成缺口，不编页**（铁律 5） | `C:\swapi\types` 覆盖不到的三个 add-in 集中在 Simulation/Topology/Costing，79 处 |
| **D7** | ★ **按批次文件切分、每批一个写者** | 543 条 × 多轮 ⇒ 文件级不相交才有并行 |

---

## 四 · 本规格**不做**什么

- ★ **不改工具名、不删工具**（`specs/215` §三已裁定）✗
- ★ **不为过门禁而放宽判据**：基线只许降 ✗
- ★ **不把「查不到」写成「已验证」**（铁律 5）✗
- ★ **零真机**：本规格只读离线官方文档树与源码，不启 SolidWorks ✓

---

## 五 · 验收判据（全机器可判）

| # | 判据 | 怎么验 |
|---|---|---|
| **A1** | 门禁自证有效：7 条反例全部被拒 | `python -B -m pytest tests/test_tool_official_claims_gate.py -q` |
| **A2** | 门禁接线为硬门禁 | `python -B scripts/check_gate_wiring.py` rc=0 |
| **A3** | **已核工具数只增不减**（当前 4/543 试点） | `python -B scripts/check_tool_official_claims.py --report` |
| **A4** | `release_check` 全绿 | `python -B scripts/release_check.py` rc=0 |
| **A5** | 每批的「查不到页」成员都有记账（不编页） | 该批台账 `members[].documented=false` + `gap` 字段 |
| **A6** | 零真机 | 全程无 `sw_guard.py` / COM 调用 |

---

## 六 · 批次划分（多轮施工）

按工具域切分，每批一个台账文件、一个写者（教训：`specs/352` D7）。

| 批 | 域 | 工具数 | 状态 |
|---|---|---|---|
| **P0** | 试点：拉伸/槽（`extrude_*`、`sketch_add_slot`） | 4 | ★ 已核（本规格 P0） |
| **B1** | 拉伸/旋转/孔/圆角倒角（实体特征） | ~60 | 待核 |
| **B2** | 草图族（建草图 + 画几何 + 关系 + 尺寸） | ~70 | 待核 |
| **B3** | 装配族 | ~60 | 待核 |
| **B4** | 工程图族 | ~60 | 待核 |
| **B5** | 钣金 / 焊件 / 模具 / 曲面 | ~80 | 待核 |
| **B6** | 仿真 / 拓扑 / 成本（★ 79 处查不到页在这里） | ~80 | 待核 |
| **B7** | 读取类 / 文档属性 / 导出 / 视图 | ~70 | 待核 |
| **B8** | 编排与门面工具（无 COM 成员，`claim_evidence` 用 `impl`） | ~60 | 待核 |

★ 每批的收工判据（三条都成立才勾）：① 该批全部工具有台账且 `claim` 与 `doc` 首句一致；
② 成员覆盖 0 条 `member-uncited`；③ 查不到的成员逐条记账（`documented=false` + `gap`）。
