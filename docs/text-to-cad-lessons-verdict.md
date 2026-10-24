# text-to-cad 经验内化：五条经验的裁决

**状态**：裁决完成，采纳项已实现门禁与负例测试。
**⚠ 原件已删**：`text-to-cad` 克隆与逆向报告已于 2026-10-19 全部删除（内化完成）。本文中的「上游 `文件:行号`」**已无法回读核对**，保留它们只为说明「当时依据的是哪一段」。删除清单与重核方法见 [`docs/text-to-cad-borrowed.md`](history/text-to-cad-borrowed.md)。
**方法**：每条经验先给**上游原文证据**（文件路径 + 行号 + 逐字引用），再给**本仓库现状核实**（同样带行号），最后给**裁决**。裁决只有三种：`采纳` / `改造` / `不采纳`。
**纪律**：本文件不含未核实的断言。凡我推断的，标「推断」并给依据行。

---

## 零、裁决总表

| # | 经验 | 裁决 | 落点 |
|---|---|---|---|
| ① | 事实/尺寸来源分级 | **改造后采纳** | `check_fact_provenance.py` |
| ② | 几何关系断言化 | **不采纳（本轮）** | 见 §2.4，缺落点 |
| ③ | 强制视觉复核 + 反循环刹车 | **不采纳（已有更强）** | 见 §3.4 |
| ④ | 置信度进名字 | **不采纳（有替代）** | 见 §4.4 |
| ⑤ | 不追问但记录 | **改造后采纳** | `check_assumption_ledger.py` |

**一句话结论**：五条里真正能落地的是两条，而且两条都必须**改造**——直接照搬会在本仓库产生空转门禁（事实 62 的失败形态）。另外三条不采纳，各有明确理由，不是遗漏。

---

## 一、勘察结论（先摆事实，裁决才有依据）

### 1.1 本仓库的产物构成

实测（`Get-ChildItem -Recurse -File` + `Group-Object`）：

| 位置 | 文件数 | 说明 |
|---|---|---|
| `output/` | 9,416 | 其中 `.SLDPRT` 3,060 · `.SLDASM` 652 · `.json` 2,149 · `.txt` 1,110 · `.py` 815 |
| `specs/` | 2,369 | **全部入库**（`git ls-files specs` = 2369） |
| `scripts/` | 248 入库 | 其中 `check_*.py` 49 个 |

`output/` 在 `.gitignore:120` 被忽略，但仍有 **456 个文件被跟踪**（`git ls-files output` = 456）。⇒ `output/` 是「被忽略为主、少数入库」的混合体。

**关键判断**：3,060 个 `.SLDPRT` 是**真机产物**，不是手写源。它们不带可审计的数字，带数字的是生成它们的 `.py` 与规格文档。

### 1.2 `provenance` 字段只用了 1 条——是设计如此，不是未完成

`capabilities.yaml`（实为 JSON，593,936 字节 / 5,700 行）有 140 条能力：

| 字段 | 有条数 |
|---|---|
| `evidence` | 137 |
| `provenance` | **1** |

唯一那条是 `mold_tools`（`level: stitched`）。

**为什么只有 1 条**——`docs/capabilities-schema-proposal.md` 的 level 表格逐字规定：

```
| `source_verified` | 来源声明跑过，我们未复现 | 带 `upstream_verified` 的 `provenance` |
```

而 `scripts/check_union_conventions.py:237` 的注释进一步收窄：

```
⚑ **`provenance` 的触发条件只有 `source_verified`**（裁断修正 B2）：
```

实测 140 条的 `level` 分布是 `verified` 100 / `stitched` 37 / `not_implemented` 3 —— **`source_verified` 为 0 条**。

⇒ **`provenance` 空着是规则的必然结果，不是欠账。** 我此前在报告 §7.3 写的「`capabilities.yaml` 只管代码来源」不够准确，应更正为「`provenance` 只在 `source_verified` 时强制，当前无此级条目」。

### 1.3 本仓库已有的「存量豁免」范式

不是新造，有三处先例：

| 机制 | 文件 | 判据 |
|---|---|---|
| 门禁接线豁免 | `docs/gate-wiring-exemptions.json` | `{gate, reason, evidence[]}`，`check_gate_wiring.py` 读 |
| 用户偏好写入豁免 | `docs/preference-write-exemptions.json` | 同上形状 |
| 增量来源门禁 | `scripts/check_provenance.py:11-13` | 「对每一处相对上游 `origin/main` 的**新增代码行**」 |

`check_provenance.py` 的增量判定在 `:146-164`：

```python
def _added_lines(path: str) -> dict[int, str]:
    """返回 {行号: 该行文本}，只含相对上游新增的行。"""
    diff = _git("diff", "--unified=0", ANCHOR, "--", path)
```

`:59` `ANCHOR = "origin/main"`；`:294-302` 另有未跟踪文件的整文件新增分支。

⇒ **「老代码怎么办」在本仓库已有答案：不办。** 存量天然在基线内，只对增量收税；老代码被改动时，改动行自然进入检查。

### 1.4 动工前基线

`python scripts/release_check.py` ⇒ **exit 0**，耗时 144s，全部门禁 pass/clean。
`git status --porcelain` ⇒ 仅 2 个未跟踪目录（`.rea-scratch/`、`_design-transfer/`），工作树干净。

---

## 二、经验①：事实/尺寸来源分级

### 2.1 上游证据

`models/falcon_heavy/PROVENANCE.md:12-13`（表头）：

```
| Component group | Sources | Type | Confidence | Geometry status |
|---|---|---|---|---|
```

`:14`（高置信度行）：

```
| Overall envelope (70 m × 12.2 m, core 3.66 m, fairing 5.2×13.1 m) | SpaceX FH page / User's Guide | official | High | measured (scale only) |
```

`:24-25`（低置信度行——**明说自己编了**）：

```
| COPV-like placeholders | COPVs in LOX tank publicly known (AMOS-6 reporting); count/placement NOT public | official reporting | Medium (existence) | supported placeholder, **counts/positions invented** |
| Octaweb frames, avionics modules, separation block, payload adapter/payload | existence public at word-level; all geometry invented | index | Low | schematic placeholder, **no internals** |
```

`:28-37`（四档汇总，末档是「根本没建」）：

```
## Confidence map (summary)

- **High:** published envelope figures and engine counts — used for scale only.
- **Medium:** octaweb pattern, LOX-forward tank order, grid fin/leg existence,
  MVac facts.
- **Low:** every station position, internal volume, bracket, and proportion
  beyond published figures.
- **Not modeled:** tank walls, weld schedules, separation internals, avionics
  architecture, COPV counts/placement, feed routing, engine internals
  (see the `src/lib/merlin_common.py` header), pressurization/control logic.
```

`RESEARCH.md:5`（查证方法本身也是事实）：

```
All facts were verified against fetched source content (not memory) at research time.
```

### 2.2 本仓库现状

- `capabilities.yaml` 的 `provenance` 只覆盖**代码来源**，且只在 `source_verified` 时强制（§1.2）。
- **没有任何字段记录「这个数字从哪来」**。`docs/known-facts.md` 记的是**技术事实**（API 行为），不是**设计尺寸**。
- `check_provenance.py` 只查 `.py` 新增行有无 `# ── 来源 ──` 块（`:25` 明写「文档与数据文件不强制」）。

⇒ **缺口真实存在，但落点不是 `capabilities.yaml`。**

### 2.3 裁决：**改造后采纳**

**不照搬的原因**：上游的做法是「每个组件一行五栏表」，那是**建模任务级**的产物。本仓库不是建模仓库，是**能力仓库**；若照搬成 `capabilities.yaml` 的新字段，140 条里 100 条 `verified` 已经由 `evidence` 表达了运行证据，再加一档「尺寸置信度」会与 `level` 语义重叠——这正是**空转门禁**的形态（事实 62）。

**改造后的形状**：把「来源分级」收窄到本仓库**真正会产生未标注数字的地方**——`docs/` 下的规格与台账里的**量化断言**。判据是：

> `docs/*.md` 里出现的形如「N 条 / N 个 / N% / N 秒 / N MB」的量化断言，若来自实测，必须能在同一段落或同行找到可追溯的出处（命令、脚本路径、日志路径、或 `git show` 形式的引用）。

这与上游「每行带 Sources」同构，但**落在文档而不是能力清单**，且**只查增量**（§1.3 范式）。

**实现**：`scripts/check_fact_provenance.py` + 负例测试。

### 2.4 为什么不查 `output/` 与 `specs/` 里的数字

- `output/` 里的 `.SLDPRT` 是二进制，无可查文本（数量见 §1.1 表，实测命令：`Get-ChildItem output -Recurse -File | Group-Object Extension`）；
- `specs/` 下 2,369 个文件是**历史规格**（实测：`git ls-files specs` 计数），其中大量数字是当时的实测结论，现在补出处等于伪造证据链；
- 且二者都是**存量**，按 §1.3 范式不该被强制改造。

⇒ 只查 `docs/` 下**本次之后新增/修改**的量化断言。

---

## 三、经验②：几何关系断言化

### 3.1 上游证据

`models/radial/src/lib/spec.py:1-27` 先以散文定义坐标系（节选）：

```
FRAME (engine frame, millimetres)
  Y   crank axis. +Y = REAR (accessory section), -Y = FRONT (propeller).
  Z   up. Cylinder 1 points straight up.
...
CYLINDER-LOCAL FRAME (author per-cylinder parts once, for cylinder 1)
  h  along the cylinder axis, measured from the crank axis   (cyl 1: +Z)
```

`:38-42`（表达式而非字面量）：

```python
BORE = 146.0                 # 5.75 in (P&W R-1340 Wasp)
STROKE = 146.0               # 5.75 in
R_CRANK = STROKE / 2.0
FIRING_ORDER = (1, 3, 5, 7, 9, 2, 4, 6, 8)
FIRING_INTERVAL_DEG = 720.0 / N_CYL          # 80 deg
```

`:239-262`（`check_spec()`，断言几何关系）：

```python
def check_spec() -> None:
    # every cylinder fires exactly once per 720 deg, 80 deg apart, in FIRING_ORDER
    ...
    assert order == FIRING_ORDER, order
    assert gaps == {80}, gaps
    ...
    # planetary: ring = sun + 2 planet; planets assemble evenly
    assert RED_RING_T == RED_SUN_T + 2 * RED_PLANET_T
    assert (RED_RING_T + RED_SUN_T) % RED_PLANETS == 0
```

`:265`（模块级无条件执行）：`check_spec()`

### 3.2 本仓库现状

本仓库**没有几何设计常量的单一真相源**。理由是结构性的：

- 本仓库是**能力仓库**（`AGENTS.md` §〇「自建仓库，把 SolidWorks 自动化做到……」），不是零件仓库；
- 具体零件的几何参数在 `output/` 的 815 个 `.py` 里，且大部分是一次性探针；
- `specs/` 里 281 个规格是**规格**，不是可执行常量模块。

⇒ **`check_spec()` 这个模式没有落点。**

### 3.3 裁决：**不采纳（本轮）**

**理由**：采纳它需要一个「几何常量单一真相源」的存在。本仓库没有，硬建一个会变成：

- 一个没人 import 的常量模块（等于没有守卫，事实 60 的形态「一个存在但没人用的守卫与没有守卫等价」）；
- 或者一个只在测试里跑的断言集，那与现有 `tests/` 已有能力重复。

**这不是「经验不好」，是「本仓库没有对应的问题」。**

### 3.4 什么情况下应该重新考虑

如果出现以下任一情形，本条应重新裁决为「采纳」：

1. 本仓库开始承载**具体产品零件**（而非探针/示例），且该零件有齿轮/孔阵/装配约束类关系；
2. 出现「同一个尺寸在多处重复定义且已漂移」的实际事故；
3. `specs/` 下的规格开始附带可执行常量模块。

**触发信号（当前由人工复核，未做成门禁）**：若 `output/` 下出现 ≥3 个带 `check_spec()` 同类模式的脚本，或 `docs/known-facts.md` 新增「常量漂移」类事实，则重开本条。

> ⚠ **为什么不做成门禁**：本条裁决是「不采纳」，按 §零 的口径，只有「采纳」项才配门禁。给一条**没有采纳**的经验做门禁，本身就是空转（事实 62 的失败形态）。⇒ 触发信号写在这里供复核，**不承诺机检**。
>
> 复核命令（人工跑）：`Get-ChildItem output -Recurse -File -Filter *.py | Select-String 'def check_spec'`；以及 `Select-String docs/known-facts.md '常量漂移|常量.*漂移'`。

---

## 四、经验③：强制视觉复核 + 反循环刹车

### 4.1 上游证据

`skills/cad/references/snapshot-review.md:11-13`：

```
Every created or visibly updated part or assembly gets at least one reviewed
PNG snapshot of its STEP, or its mesh when no STEP is declared. Passing geometry
checks does not waive this visual review. Use the format's snapshot command.
```

`:27`（反循环刹车）：

```
Do not loop on snapshots. Rerender only when a source repair changed visible geometry or when a specific visual finding needs confirmation.
```

### 4.2 本仓库现状

本仓库**已有更强的东西**：

- `shot.py`（仓库根）+ `ctl.py`（仓库根）——截图能力；
- `docs/` 下 `shots/` 目录（产物）；
- AGENTS.md §十五 的 `tools/sw_guard.py` 弹窗护栏——比「截图」更强的真机安全机制；
- 事实 525 的「用户偏好写入必须可还原」门禁 `check_user_preference_writes.py`。

**关键差异**：上游的「强制视觉复核」是**给建模任务的纪律**；本仓库的视觉产物是**探针证据**，其完整性由 `check_*_evidence.py` 一类门禁保证，不是靠「每次改动必须看一张图」。

### 4.3 裁决：**不采纳**

**理由**：本仓库的验证哲学是「静态比对优先 + 真机证据留档」（AGENTS.md 铁律 2），而不是「人看图确认」。上游那条规则的目标读者是**没有特征树、无法静态验证几何的建模者**；本仓库有 SolidWorks 的真机测量能力，静态与真机两条线都比「看图」强。

**反循环刹车这条**（`:27`）本仓库已有等价物：AGENTS.md 事实 53「同一个启发式连续修补 ≥3 次还没稳定，就该停下回退」。

### 4.4 但有一条子经验值得吸收（并入经验⑤）

上游 `snapshot-review.md:18-25` 的「**Skip saved snapshots only when…**」是一张**豁免清单**，且要求 `When skipping, report the reason and the deterministic evidence that still ran.`（`:25`）。

这个「**跳过必须报理由 + 报仍然跑了什么**」的句式，与本仓库 `gate-wiring-exemptions.json` 的 `{gate, reason, evidence[]}` 完全同构 ⇒ **不需要新机制，已存在**。

---

## 五、经验④：置信度进名字

### 5.1 上游证据

`models/falcon_heavy/PROVENANCE.md:8-10`：

```
Labels embed geometry status
(`__photogrammetric`, `__schematic`, `__decorative`, `__placeholder`,
`__nonfunctional`, `__linked`).
```

### 5.2 本仓库现状

本仓库**已有替代且更结构化**：`capabilities.yaml` 的 `level` 五级枚举（`verified` / `source_verified` / `stitched` / `indexed` / `not_implemented`），由 `check_union_conventions.py` 的 R1 规则强制挂在 `schema_version: 2.0` 上（`:251-255`）：

```python
# R1：schema_version 必须挂在 2.0（五级枚举与 provenance 必填性挂在它上面）
```

以及 AGENTS.md 验收 A7 的禁词门禁：「全文没有一处把 `source_verified` 或 `stitched` 写成 `verified`」。

### 5.3 裁决：**不采纳**

**理由**：上游把状态写进**几何对象的名字**，是因为它**没有别的地方可以挂状态**（STEP 是纯几何，无元数据——这正是其 `packages/cadgen/README.md` 的第 4 条法律 `Zero metadata in written artifacts`）。

本仓库的 `capabilities.yaml` 是一个**结构化清单**，状态有专门的字段与门禁。把状态再复制一份到名字里，会产生**双写不一致**风险——这是本仓库明确反对的形态（`check_union_conventions.py` 的 R13 就在查「`source` 与 `provenance` 必须自洽」，说明双写已经开始产生矛盾了）。

---

## 六、经验⑤：不追问但记录

### 6.1 上游证据

`skills/cad/references/cad-brief.md:9-11`：

```
Clarify missing or conflicting information when it materially affects the result,
especially a mating interface or required scale. Otherwise proceed with explicit
assumptions. Do not ask the user to fill out a template.
```

`skills/sdf/references/llm-guardrails.md:36`：

```
Do not hide guessed values in raw XML: every non-obvious number carries a comment or a ledger line naming its source.
```

`llm-guardrails.md:26-35`（五种合法来源，缺一不可）：

```
## Required mitigation pattern

For every spatial, physical, or simulator-specific value, use one of these sources:

1. user-provided requirement;
2. upstream geometry, robot-description, planning-metadata, mesh manifest, or model package source;
3. target simulator documentation;
4. measured or calculated value with method stated;
5. explicit assumption recorded in the ledger comment block and the final report.
```

### 6.2 本仓库现状

本仓库**部分具备**：

- `docs/known-facts.md` 记技术事实（560 条），每条带依据；
- `docs/dead-ends.md` 记走死的路；
- `capabilities.yaml` 的 `limitations` 字段记「不做 + 原因」；
- `check_known_facts_triage.py`、`check_fact_single_home.py` 是已有门禁。

**缺口**：**没有「假设台账」这个概念**。本仓库有「事实台账」（已知的）与「死路台账」（试过的），但**没有「我假设了但没验证」的台账**。

### 6.3 裁决：**改造后采纳**

**改造点**：上游的 ledger 是**建模任务内**的注释块；本仓库需要的是**跨任务**的假设台账。形状：

- 位置：`docs/assumption-ledger.md`（新增）；
- 每条假设：`{id, 假设内容, 依据来源档位(1-5), 影响面, 验证方式, 状态}`；
- 状态三态：`open`（未验证）/ `confirmed`（已验证，附证据）/ `refuted`（已证伪，附证据）；
- 门禁：`scripts/check_assumption_ledger.py` 查**格式与状态自洽**——`confirmed`/`refuted` 必须带证据；`open` 不得出现在 `capabilities.yaml` 的 `verified` 条目的 `evidence` 里（即：**未验证的假设不能被当成验证证据**）。

最后一条是本条经验的**真正价值**：它把「假设」与「证据」在机器层面隔开。

### 6.4 与既有机制的关系

不与 `known-facts.md` 重复：

| 台账 | 记什么 | 状态语义 |
|---|---|---|
| `known-facts.md` | **已验证**的技术事实 | 无需状态（存在即已验证） |
| `dead-ends.md` | **已验证失败**的路径 | 无需状态（存在即已失败） |
| `assumption-ledger.md`（新） | **未验证 / 验证中 / 已证伪**的假设 | 必须有状态 |

三者互补，判据是「是否已验证」这个二值——`known-facts` 与 `dead-ends` 都在「已」侧，新台账在「未」侧。

---

## 七、实现清单（采纳项）

| 经验 | 门禁脚本 | 负例测试 | 接线 |
|---|---|---|---|
| ① | `scripts/check_fact_provenance.py` | `tests/test_fact_provenance_gate.py` | `release_check.py` |
| ⑤ | `scripts/check_assumption_ledger.py` | `tests/test_assumption_ledger_gate.py` | `release_check.py` |

**负例测试的判据**（依据事实 62「负例测试是唯一的证明」）：

1. 门禁对**故意构造的违规输入**必须报 FAIL（不是恒绿）；
2. 门禁对**合规输入**必须报 PASS（不是恒红）；
3. 用 `git show <修复前>:<path>` 形式取真实历史样本作负例（事实 62 的手法），若不可得则构造最小复现。

**存量豁免**（依据 §1.3 范式）：两道门禁都只查**增量**——以 `docs/assumption-ledger.md` 与 `docs/` 下被修改的 `.md` 为范围，不做全仓清洗。

---

## 八、本裁决书的自我限制

1. **不含未核实断言**：本文所有行号均已回读核对；凡推断处标「推断」。
2. **裁决可被推翻**：§3.4 给了经验②的重开触发信号；经验③④若有新证据（例如本仓库开始承载产品零件），应重开。
3. **不覆盖上游全部经验**：本裁决只处理报告 §7.1 列的五条。上游还有「强制视觉复核的反循环条款」「五种合法来源枚举」等更细的条目，已在 §4.4、§6.1 就近吸收或说明不适用。
