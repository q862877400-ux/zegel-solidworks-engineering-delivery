# 项目现状记录 · 跨维度索引

> **这是入口。** 十条维度的事实文件在 `facts/`，探测器在 `probes/`，机器可读读数在 `inventory-*.json`。
> 本索引只做两件事：**「想知道 X → 去哪看」** 与 **「每个维度最承重的一条读数」**。
> 记录员口径不变：不含判断、不含优先级、不含修复建议。
>
> 三处入口互指：`AGENTS.md` 首段 → 本文件 · 项目级 skill [`sw-project-state`](../../.dsh/skills/sw-project-state/SKILL.md)（含读法/纪律/三个实测坑） → 本文件。

---

## 一、想知道 X → 去哪看

| 我想知道 | 去哪 | 复现命令 |
|---|---|---|
| **项目为什么存在、成功长什么样、验收判据（E1–E7）** | **[`docs/PROJECT-CHARTER.md`](../PROJECT-CHARTER.md)** ← 顶层定义，高于本台账 | 无（定义文档，读即可）|
| 仓库有几个顶层目录、各多大、哪些入库了 | `facts/A-structure.md` | `python docs\state\probes\probe_structure.py --json docs/state/inventory-a.json` |
| MCP 工具声明现在是什么状态（501 条、命名、单位、doc、read_only） | `facts/B-tools.md` | `python docs\state\probes\probe_all_specs.py --json docs/state/inventory-b.json` |
| 能力台账 140 条的 level 与字段齐全度 | `facts/C-capabilities.md` | `python docs\state\probes\probe_capabilities.py --json docs/state/inventory-c.json` |
| `scripts/` 213 个模块的规模、引用关系、门禁读数 | `facts/D-scripts.md` | `python docs\state\probes\probe_scripts.py --json docs/state/inventory-d.json` |
| 55 道门禁各自接线/分类/selftest 情况 | `facts/E-gates.md` | `python docs\state\probes\probe_gates.py --json docs/state/inventory-e.json` |
| 测试能不能收集、哪些文件在收集期就断了 | `facts/F-tests.md` | `python docs\state\probes\probe_tests.py --json docs/state/inventory-f.json` |
| 文档有多少、哪些断链、哪些逐字重复 | `facts/G-docs.md` | `python docs\state\probes\probe_docs.py --json docs/state/inventory-g.json` |
| 每份核心文档的最后提交日/被引用数/是否重复 | `doc-map.md` | `python docs\state\probes\probe_doc_map.py` |
| 281 份规格的状态字段、验收标记、编号缺口 | `facts/H-specs.md` | `python docs\state\probes\probe_specs.py --json docs/state/inventory-h.json` |
| 许可与来源：4 家来源、NOTICE、GPL 族声明 | `facts/I-license.md` | `python docs\state\probes\probe_license.py --json docs/state/inventory-i.json` |
| 运行装配链：server/sw_connect/mcp.json 在哪 | `facts/J-runtime.md` | `python docs\state\probes\probe_runtime.py --json docs/state/inventory-j.json` |

### 第二轮（K–O，深度对应关系）

| 我想知道 | 去哪 | 复现命令 |
|---|---|---|
| 501 条声明是否指向真实函数、签名对不对得上 | `facts/K-signature.md` | `python docs\state\probes\probe_specs_vs_code.py --json docs/state/inventory-k.json` |
| 100 条 `verified` 的 evidence 指向物是否存在 | `facts/L-evidence.md` | `python docs\state\probes\probe_evidence.py --json docs/state/inventory-l.json` |
| 测试的**执行期**结果（门禁类 34 个文件） | `facts/M-tests-run.md` | `python docs\state\probes\probe_tests_run.py --json docs/state/inventory-m.json` |
| 仓库外 26 个克隆的许可、五个未触碰目录的规模 | `facts/N-external.md` | `python docs\state\probes\probe_external.py --json docs/state/inventory-n.json` |
| 文档归并（重复/断链的真实构成） | `facts/O-docs-merge.md` | `python docs\state\probes\probe_doc_consolidate.py --json docs/state/inventory-o.json` |

### 台账空白补记（Q 系列，`docs/state/facts/` 里原「未覆盖」段的收口）

| 我想知道 | 去哪 | 复现命令 |
|---|---|---|
| `apps/` 447 .py 与 `subskills/` 23 .py 是什么 · 26 个克隆与来源清单的对应 · 两份 audit 重叠 · examples 存在率 · `.pyc` 是否入库 | `facts/Q-gaps.md` | `python docs\state\probes\probe_gaps.py --json docs/state/inventory-q.json` |
| 100 条 `verified` 的证据**文本形态**（否定字样/点名测试/点名产物） | `facts/Q2-evidence-substance.md` | `python docs\state\probes\probe_evidence_substance.py --json docs/state/inventory-q3.json` |
| **全量测试的执行期结果**（89 failed / 3944 passed / 63 errors / 20 分 38 秒） | `facts/Q3-tests-full.md` | 见该文件「复现」两条命令 |
| 新旧文档冲突 P-01～P-07 的逐条处置 | `facts/P-doc-conflicts.md` | `python docs\state\probes\probe_docs.py` 等，见该文件 |

---

## 二、每个维度最承重的一条读数

| 维度 | 最承重读数 | 出处 |
|---|---|---|
| **A 结构** | 「目录是否被 ignore」≠「内容是否入库」：`output` 未被 ignore 命中但其中 **456 个文件已入库** | A-03 |
| **B 工具声明** | `check_specs` 返回 **5 条**问题，`register()` 按 docstring **整体拒绝注册**；而 `all_specs()` 仍能返回 501 | B-11 |
| **C 能力台账** | 140 条中 `verified` **100** · `stitched` **37** · `not_implemented` **3**；`provenance` 仅 **1/140** | C-02 · C-03 |
| **D 脚本层** | 213 个模块**来源块 213/213 全覆盖**；ruff **415**、跨文件同函数体 **76** | D-02 · D-07 |
| **E 门禁层** | 55 个 `check_*.py`，**52** 接进 release_check，**1** 个未登记分类，分类表另有 **5** 条指向非 `scripts/` 文件 | E-01 · E-02 · E-03 |
| **F 测试层** | 收集期 **exit=2**，**5 个文件**因 `tool_registry.GateError` 无法收集；**未执行任何用例** | F-03 |
| **G 文档层** | 内部 `.md` 链接 **453** 条、断链 **110**；核心文档断链 **0** | G-04 |
| **H 规格层** | 281 份规格中 **140** 份无 `Status` 行；`→ 验收` 标记 `specs/**` 共 **935** 处、`spec.md` 内仅 **20** 处 | H-03 · H-04 |
| **I 许可** | 4 家来源（MIT×3 + Apache×1）；头部含 GPL 族的 **6** 个文件**全部**是「只读思想」声明或门禁判据 | I-01 · I-05 |
| **J 运行** | 装饰器 **45** + 声明式 **501**；仓库根**无** `mcp.json`，`"solidworks": false` 在 `$DSH_HOME/mcp.json` | J-03 · J-05 |

---

## 三、跨维度的三个「同一件事、多个读数」

> 只列数字与位置，不判断哪个对。

| 对象 | 读数 A | 读数 B | 读数 C |
|---|---|---|---|
| **工具总数** | 声明式 **501**（B-01） | `AGENTS.md` 记「529（497 + 32）」（J-03） | 装饰器 **45**；501+45=**546**（J-03） |
| **`server.py` 行数** | 实测 **3,537**（J-01） | `tool_registry.py:4` docstring 写 **2455**（J-02） | — |
| **`→ 验收` 处数** | `specs/**` **935**（H-03） | `spec.md` 内 **20**（H-03） | `AGENTS.md` 记 **866**（H-03） |
| **NOTICE 规模** | 实测 **169 行 / 8,981 B**（I-02） | `AGENTS.md` 记「153 行 / 6.5 KB」（I-02） | — |
| **顶层目录数** | 磁盘 **42**（A-01） | `AGENTS.md`「39 仓库目录 + 3 工具缓存」= 42（A-01） | 按 AGENTS 自己的名单拆分时 `.pytest_cache` 被两处重复计入（A-01） |
| **测试钉死数** | `test_server_wiring.py:300` 断言 **480**（B-12） | 实测 `all_specs()` **501**（B-01） | 该文件收集期即失败（B-13 / F-03） |

---

## 四、本记录明确没有做的事

- **没有判断**任何读数是好是坏、该不该改（记录员边界，见 `README.md` 抬头）
- **没有执行**任何 MCP 服务、未连 SolidWorks、未运行任何测试用例（只到「收集期」）
- **没有验证** 100 条 `verified` 能力的 `evidence` 是否真实（只统计了字段形态，见 C-04）
- **没有比对**能力级 `provenance` 与来源级清单的逐条对应（C-03 只记了 `provenance` 1/140）
- **没有检查**仓库外克隆（`C:\swprojects\`）的许可现状

---

## 五、一切读数的总复现方式

```powershell
cd <仓库根>
python docs\state\probes\probe_structure.py    --json docs/state/inventory-a.json
python docs\state\probes\probe_all_specs.py    --json docs/state/inventory-b.json
python docs\state\probes\probe_capabilities.py --json docs/state/inventory-c.json
python docs\state\probes\probe_scripts.py      --json docs/state/inventory-d.json
python docs\state\probes\probe_gates.py        --json docs/state/inventory-e.json
python docs\state\probes\probe_tests.py        --json docs/state/inventory-f.json
python docs\state\probes\probe_docs.py         --json docs/state/inventory-g.json
python docs\state\probes\probe_doc_map.py
python docs\state\probes\probe_specs.py        --json docs/state/inventory-h.json
python docs\state\probes\probe_license.py      --json docs/state/inventory-i.json
python docs\state\probes\probe_runtime.py      --json docs/state/inventory-j.json
```

全部只读；唯一副作用是写 `docs/state/` 下的 `inventory-*.json` 与 `doc-map.md`。
