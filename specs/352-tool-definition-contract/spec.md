# 规格 352 · 工具定义成品化（把 498 个 MCP 工具的**模型可见定义**改成「看一遍就能调对」）

> **业主原话（2026-10-26，本规格的唯一来源）**：
> 「用我最新的这个 MCP builder 技能，把**你所有 SolidWorks 建模的这些 MCP 工具修正一遍**，
> 你现在都是半成品。注意呀，我们现在这个 MCP 工具描述上的东西非常少，
> **你光看一下里面的参数，你可能不懂它到底是干什么的**，你可能会搞错了。
> 所以如果有什么不清楚的，**一定要去查官方的 API 手册、API 工具的手册，或者是查我们自己的文档**都行。
> 我的 token 预算是无限的，要**大大方方地多花 token 去验证去确认，然后再动手**。
> 反正你把这个任务设置一个目标，按照 spec 规范去自动化进行。」

★ 本规格的**唯一目标**是「模型看了能一次调对」，**不是**「描述更短」或「更漂亮」。
字节数下降是副产品（`specs/208` D-9 已把判据从「选了谁」改成「端到端可执行」）。

---

## 一 · 为什么有这条规格

### 1.1 同一个诉求，业主已经提了**第三次**

| 次 | 时间 | 业主原话 | 当时的处置 | 结果 |
|---|---|---|---|---|
| ① | 2026-10-07 | 「你工具描述我看看你写的咋样，**干了 41k，太多了**，你肯定说了一堆废话，**lean 模式的要求是要写的精而准**」 | `tools/measure_lean_catalog.py` 先量；`tools/lean_first_sentence.py` **只加一行短首句** | ★ **没治好** —— doc 主体仍是变更日志 + 证据链 |
| ② | 2026-10-07 | （同上轮）「**写在第三段的话模型根本看不到**」 | `specs/215` 立门禁 `check_lean_first_line_caveat.py` + 8 条首句前置 | ★ 只覆盖「不可用/内部件」两类标记，**其余 490 条没管** |
| ③ | 2026-10-26 | 「**你现在都是半成品**…光看参数不懂它干什么」 | **本规格** | —— |

★ 教训（本规格的立规依据）：**「只做加法」治不了「主体是废话」**。①②都只动首句，
而模型（native 档）看到的是**整段**，lean 档看到的**只有首句** ⇒ 两头都不对。

### 1.2 实测基线（本轮，`output/_audit_tool_docs.py`，可复现）

| 读数 | 值 | 口径 |
|---|---|---|
| 声明式 spec 总数 | **498** | `register_capabilities.all_specs()` |
| `doc` 全文合计 | **149,502 字** · 均 **300** · p50 **268** · p90 **539** · max **1606** | `len(spec.doc)` |
| 首句是**元数据**（`★` / `官方签名` / `查不到` / `**`） | **274 / 498 = 55%** | lean 口径 `split(/[。\n]/)[0]` |
| `doc` 含中文 | **282 / 498 = 57%**（其中 **250** 条含 `。`） | `[\u4e00-\u9fff]` |
| 首句 > 120 字（lean 下被截断） | **215 / 498 = 43%** | `firstLine()` 复刻 |
| 首句为空 | **4** | 同上 |
| 参数总数 | **1183** | `len(spec.params)` |
| 参数**没有说明** | **10**（分布在 6 个工具） | `not p.description.strip()` |
| 参数说明**不以句号收尾** | **647 / 1183 = 55%** | 官方 100% 收尾（n=228） |
| 参数说明是**中文** | **688 / 1183 = 58%** | 同上 |
| 另有**schema 缺陷** | 45 个 `server.py` 手写工具的 `params` **没写 `type`** | `output/lean-lint-report.txt`：lean 下被记成 `object`，**参数形同丢失** |

### 1.3 一条**已核实**的关键机制（决定判据怎么定）

`@local/dsh-lean-mode/index.mjs` **L130-131** 逐字：

```js
const tools = withShape
  ? base.tools.map(t => ({ name: t.name, description: firstLine(t.description), parameters: shallowParameters(t.parameters) }))
  : base.tools
```

⇒ ★★★ **lean 档（`shape: true`）下，模型看到的工具描述 = `firstLine()` 的结果，最多 120 字符**；
★ index 档（`shape: false`）与 native 档下，模型看到**整段** `doc`。
⇒ ★★ **两个档都要治**：首句必须自足（lean），整段必须无废话（native/index）。

---

## 二 · 判据（★ 每条都可机器判，判据落在 `scripts/check_tool_contract.py`）

### 2.1 硬判据（无豁免；违反即门禁红）

| # | 判据 | 怎么判 |
|---|---|---|
| **K1** | `doc` **非空**、**纯 ASCII 英文**（无 CJK、无 `。`、无换行）、以 `.` 收尾 | 正则 |
| **K2** | 首句（lean 口径）**非空**、**≤120 字符**、**不含元数据标记** | 标记集见 §2.3 |
| **K3** | 首句**动词开头**（白名单，见 §2.4） | 首词小写匹配 |
| **K4** | 首句之后**至少还有一句**（`. ` 分隔），且 `doc` **≤ 600 字符** | `len(doc)`；★ 现状仅 **36** 条 >600 ⇒ 可承受 |
| **K5** | 每个 `Param`：`description` **非空**、**纯英文**、**`.` 收尾**；`required` 为真的参数**其说明里出现该参数名** | 正则 |
| **K6** | 证据**零丢失**：改写前 `doc` 的**每一个字节**都在改写后的 `ToolSpec.evidence` 里 | 逐条 `old_doc in evidence` |
| **K7** | 45 个 legacy 工具（`server.py` 手写）的 `params` 带 `type: object` | `tools/list` 读回 |
| **K8** | 既有门禁**零放宽**：`check_lean_first_line_caveat` · 规则 2 / 2b / 3 · `check_param_binding` · 五统一 | `release_check` 全绿 |

### 2.2 棘轮判据（基线只降不升，落 `docs/tool-contract-baseline.json`）

| # | 判据 | 为什么是棘轮 |
|---|---|---|
| **K9** | 带副作用的工具（`writes` 非空 或 `read_only is not True`）的 `doc` 里含副作用词（`Writes` / `Modifies` / `Creates` / `Deletes` / `Clears` / `Overwrites` / `Saves` / `Does not save`）；`read_only is True` 的含 `Read-only` | 语义判断，先量出来再棘轮；★ DSH **不转发 MCP annotations**（`mcp-client/src/tools.ts` 只转 `name/description/parameters/output`）⇒ **副作用只能写在描述里** |

### 2.3 元数据标记集（首句里出现即违规）

```
★  ⚠  ⇒  ✓  ✅  ✗
官方签名   查不到   逐字   事实 数字   已知事实   规格 数字
```

★ **为什么这个集合**：现行 274 条元数据首句里，出现的正是这些（`output/_audit_tool_docs.json` 逐条可查）。
★ 它们**不是不许存在** —— 而是**不许出现在首句**；搬到 `ToolSpec.evidence`（非模型可见）里。

### 2.4 动词白名单（K3）

★ 取自 DSH 官方 72 个工具实测的 82% 动词句（`docs/tool-description-style.md` §一）
＋本仓 216 条已合规英文首句的动词。落成 `check_tool_contract.py::VERBS`，**可扩充但要写理由**：

```
Create Read List Get Set Add Delete Remove Apply Export Import Run Check Insert Update
Open Close Save Start Stop Select Measure Compute Find Report Validate Convert Generate
Activate Suppress Unsuppress Move Copy Rotate Zoom Refresh Clear Build Write Draw Mesh
Solve Query Search Inspect Describe Confirm Cancel Undo Redo Split Trim Extend Offset
Mirror Pattern Annotate Dimension Attach Detach Enable Disable Load Unload Register
Return Extract Rename Reorder Sort Count Hide Show Toggle Interrupt Wait Send Spawn
```

---

## 三 · 决策（★ 每条都有实测依据）

| # | 决策 | 依据 |
|---|---|---|
| **D1** | ★★ **改写 = 重写 `doc`，不是"再加一行"** | ①②两次只加首句，doc 主体仍是考古记录 ⇒ 业主第三次说「半成品」 |
| **D2** | ★★ **模型可见文本一律英文**（`doc` 与 `Param.description`） | ① lean 的 `firstLine()` **只在 `。` / 换行断句，ASCII `.` 不断** ⇒ 中文首句只活 30–50 字符、英文能活 120（`index.mjs` L34 + `specs/215` 的订正）；② 本仓 **216/498 已是英文**，统一到英文是**收敛**而不是新增第三种状态；③ DSH 官方 n=72 实测：82% 动词开头、99% 句号收尾 |
| **D3** | ★★ **工程证据搬进新字段 `ToolSpec.evidence`，`doc` 只留模型要用的** | `agent-experience` 逐字：「**Describe behavior, not implementation.** …omit internal mechanisms … and enforcement details」——现行 `★ 官方签名（逐字…）/ 查不到 / 事实 47` 全是实现与执法细节 |
| **D4** | ★★★ **`evidence` = 改写前 `doc` 的逐字副本**（不是摘要） | ★ 使「零丢失」**可机器证明**（`old_doc in evidence`），★ 且 `git diff` 一眼看得出"搬走了什么"；★ 后续要精简 `evidence` 是**另一个**可再验证的动作 |
| **D5** | **`doc` ≤ 600 字符** | 现状 p90=539、仅 36 条 >600 ⇒ 上限不逼人删真信息；枚举/取值域改放**该参数的说明**（`agent-experience`：「Put parameter rules on the parameter」） |
| **D6** | ★★ **先跑试点（24 工具 × 中英两版 × 真实模型），再全量** | 业主「**先验证再动手**」；语言这一条一旦选错要重做 498 条 ⇒ 用 24 条买这个证据 |
| **D7** | ★ **并行 = 按 `tool_specs_batchNNN.py` 文件切分**，一文件只归一个执行者 | 文件级不相交 ⇒ 无写冲突；117 个批次文件天然可切 |
| **D8** | ★ **门禁落成 `scripts/check_tool_contract.py`（新），复用旧门禁的纯函数** | `check_gate_wiring.py` 要求 `scripts/check_*.py` 必须被 `release_check` 精确形态调用；**不重写** `lean_first()` / `judge()`（十四之四：要扩展就改原模块 / 复用现成） |
| **D9** | **不动**工具名、不动实现、不动 `capabilities.yaml` | 业主只说「描述」；`specs/215` §三已裁定「不删任何工具」、名字改动要另立规格 |
| **D10** | ★ **评测用 `specs/208` 的 D-9 口径**：工具名在目录内 **且** 实参通过真实 Pydantic schema 的必填+类型校验 | `specs/208` D-9 逐字：原判据只看"选了谁"，各档工具名一样 ⇒ 注定打平 |

---

## 四 · 本规格**不做**什么

- ★ **不改工具名**（`specs/215` §三-c 已裁定：改名前先出提案）✗
- ★ **不改 `scripts/` 里的实现**（除非发现描述与实现矛盾且实现是错的 —— 那要另立发现项）✗
- ★ **不删工具**（`specs/215` §三）✗
- ★ **不为了省 token 删信息**（`docs/tool-description-style.md` §〇：省是副产品）✗
- ★ **不碰 lean 插件本体**（是否安装是**另一个决策**，业主没说）✗
- ★ **零真机**：本规格全程不启 SolidWorks、不调 COM（描述改写是静态文本工作）✓

---

## 五 · 硬约束

1. ★★ **证据零丢失**（K6）——`evidence` 逐字承载旧 `doc`，**用脚本回读证明**，不能只看脚本 stdout（事实 48 定则②）。
2. ★★ **不许发明**（铁律 1）：每一句描述都要能指回**三种来源之一** —— ① 官方 `## Remarks` / 签名页（`C:\swapi\types\**` 或 CHM）② 本仓 `scripts/` 里的实现与 docstring ③ 旧 `doc` 里已有的、已验过的内容。**查不到就写"查不到"并留在 `evidence` 里，不许在 `doc` 里编**（铁律 5）。
3. ★ **判据先量后写**：新增/修改任何门禁判据，先给出「命中数 / 真阳性数」（`specs/215` §二-④ 的教训）。
4. ★ **配双侧负例**（事实 62）：门禁必须有「该报而报」与「不该报而不报」两类样本。
5. ★ **收尾走 `round_chain` + 按路径 `commit_mine.py`**（事实 555：链完不许直接 commit）。

---

## 六 · 验收判据（★ 全部机器可判）

| # | 判据 | 怎么验 |
|---|---|---|
| **A1** | ★ **契约门禁全绿**：K1–K8 对 **498/498** 条零违反 | `python scripts/check_tool_contract.py` ⇒ 退出 0 |
| **A2** | ★ **棘轮不升**：K9 违规数 ≤ 基线 | 同上 + `docs/tool-contract-baseline.json` |
| **A3** | ★★ **评测准确率不低于基线**（且报告前后两个数） | `python tools/eval_tool_selection.py --run` ⇒ `output/tool-selection-eval.json` |
| **A4** | ★ **证据零丢失**：498 条逐条 `old_doc in evidence` | `python tools/migrate_tool_evidence.py --verify` ⇒ 丢失 **0** |
| **A5** | ★ **体量读数落盘**（前后对照） | `python tools/measure_lean_catalog.py` ⇒ 工具数 / lean 目录 / native 体量 |
| **A6** | ★ **既有门禁零放宽** | `python -B scripts/release_check.py` ⇒ rc=0，全部段 pass |
| **A7** | ★ **45 个 legacy 工具的 `params.type` 补齐** | `tools/list` 读回，无 `缺 type` 告警 |
| **A8** | ★ **零真机** | 全程无 `sw_guard.py` / COM 调用 |
