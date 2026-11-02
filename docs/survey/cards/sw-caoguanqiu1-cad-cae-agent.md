# caoguanqiu1-alt/CAD-CAE-Agent

<!-- survey: class=B; repr=code; orchestration=loop; verify=geometry-gate; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `caoguanqiu1-alt/CAD-CAE-Agent` · https://github.com/caoguanqiu1-alt/CAD-CAE-Agent |
| 许可 | **MIT**（仓库 `license.spdx_id = MIT`）；README 明写「本项目基于 [andrewbartels1/SolidworksMCP-python](https://github.com/andrewbartels1/SolidworksMCP-python) 的 MIT 开源代码」⇒ **派生项目，已有明确上游归属** |
| 元数据 | stars **1** · created **2026-09-29** · pushed **2026-10-22** · 约 17.3 MB · 第一方代码 **265 文件 / 94,934 行**（来源：`gh api search/repositories` + 本地行数统计，2026-11-02）|
| 克隆 | `D:\swagent-2026Q4\repos\caoguanqiu1-alt__CAD-CAE-Agent`（`--depth 1`）|
| 证据等级 | **读码**（未运行；读 `sw2020_workflow.py` / `sw2020_plan.py` / `experiments/` / 测试目录）|

## 1. 一句话定位

**1 星，但它把「什么叫验证过」写得比大多数高星项目清楚**：README 里拿一个 100×60×10 mm 的矩形零件举例说——「接口返回'拉伸成功'只是执行反馈。Agent 还需要检查 **1 个实体、60,000 mm³ 的独立预期体积**、所需特征和原生输出文件」，并且对静力分析补一句「**不能仅以求解器成功或云图颜色作为验收依据**」。代码里确实有对独立期望值的体积断言。（来源：README 该段与 `gh api` stars 读数，见 §8）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：工程图 / 尺寸 / 工况 → Agent 制定计划。
**中间表示**：**`plan`（计划对象）** + `Expectations`（期望值 + 容差）。`tests/test_sw2020_plan_contract.py` 里可见形态：`'expected': {'volume_mm3': 60000}` 与 `Expectations(volume_mm3=59000, center_mm=[0,0,6], faces=7)`。
**生成**：Agent 产计划，`sw2020_plan.py` 组织节点，`sw2020_workflow.py` 执行。
**编排**：README 写死的循环是「**计划 → 预检 → 执行 → 回读 → 验收**」的迭代流程。
**执行**：SolidWorks 2020 / Simulation（README 明确版本）。
**验证**（核心，三处硬证据）：
1. **对独立期望值做体积断言**：`src/solidworks_mcp/sw2020_workflow.py:343` 形如 `if expected_volume_mm3 is not None and abs(data['volume_mm3'] - expected_volume_mm3) > volume_tolerance`；
2. **对传进来的期望值做合法性校验**：同文件 `:322` 判 `math.isfinite(expected_volume_mm3)`；
3. **把「未知」当一等状态**：`tests/solidworks_mcp/tools/test_modeling.py:440` 的用例名逐字「A None 'verified' readback **is disclosed** in the message」——读不到回读值时**必须明说**，不许静默当成功。
**交付**：原生 CAD 文件 / 结果归档 / 截图 / **验证记录**；README 明说「当前公开仓库提供代码、文档、截图和脱敏数值，**原生 CAD/CWR 算例留在本地**」。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★★★ 「期望值 + 容差」是一等公民

`sw2020_plan.py:278` 把三样东西一起传进判定：`plan.expected.solid_bodies`、`plan.expected.volume_mm3`、`plan.tolerances.volume_mm3`。
⇒ **结构上就把「实体数 / 体积 / 容差」拆成三个独立字段**，而不是在代码里散着写 `if abs(...) < 0.01`。这正是我仓 `expect` 内联断言该有的形状。

### 3.2 ★★★ 它做了一个「对照实验」并留了原始数据

`experiments/` 下有 `agent_workflow_benchmark.py`、`results.json`、`timings.csv`。
更关键的是：`agent_workflow_benchmark.py:181` 出现 `source["expected"]["volume_mm3"] = 123` —— **把一个期望值故意改成 123 mm³**。这是**负例**：用来证明「门禁真的会拦住错误结果」，而不是只跑成功路径。
⇒ 这条是我们最该抄的**实验设计**：**每条判据都要配一个「它必须失败」的用例**。

### 3.3 ★★ 活的回归套件 115 KB（来源：本卡 §8 的测试文件大小实测）

`tests/` 下最大的是 `test_live_sw_regression.py` **115.1 KB**（另有 `test_live_sw_wave2.py` 9.2 KB、`simulation_phase1_live.py`、`simulation_reconnect_live.py`）。
⇒ 命名区分 `live`（要真机）与合同测试（`test_sw2020_plan_contract.py` 这类型不需要真机），**契约测试与真机测试分家**——与我仓「静态签名比对 → 本机实测」两关同构。

### 3.4 ★★ CAD 与 CAE 一起判

README 明写静力分析要「分别检查**工况、反力与网格变化**」，不能只看求解器成功或云图颜色。
⇒ 这是「**求解器没报错 ≠ 结果对**」的明确表态，与我仓「COM 返回没报错 ≠ 建对了」是同一类教训。

### 3.5 ★ 派生关系的诚实标注

README 第二段就把上游写清楚（`andrewbartels1`，MIT），不遮掩。

## 4. 运行条件与依赖

- **SolidWorks 2020 SP5** + Simulation（README 写的测试环境）。
- `.mcp.json` 声明 MCP；`src/solidworks_mcp/` 为主包；`scripts/`、`deployment/`、`openspec/` 齐全。
- 无需 GPU；FEA 走 SolidWorks Simulation。

## 5. 失败模式与已知坑

1. **1 星、派生项目**：主体能力来自上游 `andrewbartels1`，新增的是 **CAD→CAE 的验证流程与期望值体系**，不是从零重写。
2. **未运行**：所有结论来自读码；`test_live_sw_regression.py` 115 KB **未跑过**。
3. **版本钉死 2020**：README 明写 SOLIDWORKS 2020 SP5；与我方 2026 环境有 6 年差距。
4. **原生算例不公开**：README 自述「原生 CAD/CWR 算例留在本地」⇒ **最有价值的产物我们拿不到**，只能拿代码和脱敏数值。
5. **94,934 行里有多少是上游**：未做逐文件归属统计（已知派生自 `andrewbartels1`）。（来源：本卡 §9 未确认事项）

### 5.5 宣传与关注度（2026-11-02 实测，回答「为什么 1 星」）

**没有社媒宣传**：仓库 `homepage` 为 **null**、`topics` 为空、`has_discussions=false`、**无 release**；README 里没有 B 站 / YouTube / 小红书 / X 的任何链接。

唯一的外部「露出」是一条**参赛线索**：文档里引用了 `scrm.nvidia.cn/lp/dgx-spark-hackathon-agent-skills-20260920`（NVIDIA DGX Spark hackathon · agent skills，2026-09-20）⇒ **疑似为参赛作品**，这也解释了它为什么把「对照实验 + `results.json` + `timings.csv`」做得比同体量项目认真——**评测要交可复现的数据**。

HN（Algolia）、YouTube 搜索均**无命中**（报告 §12.5）。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（四件）**：
1. **★★★ 负例实验**（把 `expected.volume_mm3` 改成 123 证明门禁会拦）——**这是我方 E 判据最缺的一环：我们现在有「通过」的记录，缺「必须失败」的记录**。
2. **★★★ `Expectations` 三元组**（实体数 / 体积 / 容差）结构化传参。
3. **★★ "None 回读必须明说"**：读不到就报「未知」，不许当成功——与 A 线 `qdaia` 的「回执三态」同一条原则，这里落到了测试用例名里。
4. **★★ 契约测试与 live 测试分家**（不需要真机的合同测试 + 需要真机的回归）。

**不能学**：
- **SW2020 钉死**：版本太旧，工具层签名与 2026 有差异。
- **派生上游但未重构**：94,934 行里大部分是上游体量，不能当独立实现评估。（来源：本卡 §9 未确认事项）

## 7. 许可与红线

**MIT**（仓库 `spdx_id`），且上游 `andrewbartels1/SolidworksMCP-python` 也是 MIT。⇒ 可并入，**两处版权声明都要保留**（上游 + 本项目）。

## 8. 证据清单

- `...\CAD-CAE-Agent\README.md`（开头「Skill 组织工作流程，MCP 提供工具接口，SOLIDWORKS 2020 / Simulation 执行」；100×60×10 例与「1 个实体、60,000 mm³ 的独立预期体积」；「不能仅以求解器成功或云图颜色作为验收依据」；「原生 CAD/CWR 算例留在本地」；派生声明）
- `...\src\solidworks_mcp\sw2020_workflow.py:322`（`math.isfinite(expected_volume_mm3)`）· `:343`（`abs(data['volume_mm3']-expected_volume_mm3) > volume_tolerance`）
- `...\src\solidworks_mcp\sw2020_plan.py:278`（`plan.expected.solid_bodies` / `plan.expected.volume_mm3` / `plan.tolerances.volume_mm3`）
- `...\experiments\agent_workflow_benchmark.py:44`（`"expected": {"volume_mm3": 60000 * count}`）· `:181`（`source["expected"]["volume_mm3"] = 123` 负例）· `experiments\results.json` / `timings.csv`
- `...\tests\solidworks_mcp\tools\test_modeling.py:440`（「A None 'verified' readback is disclosed in the message」）
- `...\tests\test_sw2020_plan_contract.py:14`（`'expected': {'volume_mm3': 60000}`）· `:69`（`Expectations(volume_mm3=59000, center_mm=[0,0,6], faces=7)`）；`tests\test_live_sw_regression.py`（115.1 KB）
- 元数据与统计（2026-11-02）：`gh api search/repositories`（stars 1 / MIT / created 2026-09-29 / pushed 2026-10-22）；本地 `Get-ChildItem -Recurse -Include *.py,*.cs,*.ts,*.js` → **265 文件 / 94,934 行**

## 9. 未确认事项

1. **未运行任何测试**（含 115 KB 的 live 套件）。（来源：本卡 §9 未确认事项）
2. **`Expectations` 的默认容差是多少**：只看到字段被用，未读到默认值定义。
3. **94,934 行里上游与本项目的比例**：未做逐文件归属统计。（来源：本卡 §9 未确认事项）
4. **`experiments/results.json` 的实际读数**：只确认文件存在与脚本里写过 `123` 负例，**未读结果数值**。
5. **SW2020 之外是否兼容**：README 只写 2020 SP5。
