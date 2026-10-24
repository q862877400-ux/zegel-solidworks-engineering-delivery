# Q 维度 · 台账 7 条空白的补记（第一批 5 条）

> 观测时间 **2026-10-24** · 来源：`docs/state/probes/probe_gaps.py`（只读）+ `git ls-files` + 外部源目录扫描
> 复现：
> ```powershell
> python docs\state\probes\probe_gaps.py --json docs/state/inventory-q.json
> ```

---

## 空白 1 · `apps/` 447 个 `.py` 与 `subskills/` 23 个 `.py` 是什么

- **读数**：`apps/` **447** 个 `.py`（无模块 docstring **29**）· 子目录 `desktop` · `workbench-ui`
- **读数**：`subskills/` **23** 个 `.py`（无 docstring **0**）· 子目录 **5** 个：`autocad-automation` · `solidworks-engineering-drawing` · `solidworks-fillet-chamfer-cnc` · `solidworks-threaded-holes` · `solidworks-vibecad`
- **内容（取自模块 docstring 首行，逐字样本）**：
  - `apps/`：`@brief CAD Studio 桌面执行包。` · `CAD 自动化交付工作台。` · `@brief 企业级 Agent 控制平面的任务契约与 prompt 编译器。` · `@brief CAD Studio 多 Agent CLI Provider 发现、命令构建与结果归一化。` · `@brief CAD Studio 任务交付物账本。` · `@brief CAD Studio 双入口/双后端公共数据契约。`
  - `subskills/`：`构建并回归 AutoCAD 2024 .NET 白名单插件。` · `AutoCAD 混合后端前置检查。` · 以及 `@file acad_draw.py` / `acad_headless.py` / `acad_preflight.py` / `acad_preview.py` / `acad_review.py` 这类 `@file` 标记
- **记录员注（陈述）**：`apps/` 的模块自述指向「CAD Studio 桌面端/交付工作台」这条产品线；`subskills/` 是 5 个独立 skill 包（其中 4 个与 SolidWorks 相关、1 个是 AutoCAD）
- **未确认**：这 447 + 23 个模块与主链（`scripts/` + `mcp-server/`）之间是否有 import 关系——本次未做 import 图

## 空白 4 · `C:\swprojects` 26 个克隆 ↔ `tools/union-sources.json` 的对应

- **读数**：克隆 **26** 个 · `union-sources.json` 声明来源 **4** 条 · 克隆目录名**出现在**该清单里的 **5** 个
- **未被提及的（前 8，逐字）**：`CSharpAndSolidWorks` · `Cai-aa__CAD-Agent-Hub` · `_tmp_mcp` · `codestack` · `ddeng-skills` · `deloarts__pyswx` · `just1step__solidworks-mcp` · `mcp-server-solidworks`
- **交叉核对**：`AGENTS.md` §四 记「四家与本项目重叠的外部 MCP 项目」，另称「其余 21 个外部项目克隆的清单…见 `docs/sources.md`」⇒ 与本次实测「26 − 5 = 21 个未在本清单」数量吻合
- **未确认**：那 5 个「被提及」的克隆是否都在 `sources` 数组内（本次用整份 JSON 文本做子串匹配，可能命中 `note` 字段）——未逐条核字段

## 空白 5 · 两份 `verified-evidence-audit` 的内容重叠

- **读数**：`docs/verified-evidence-audit.md`（7,968 B）vs `docs/recon/verified-evidence-audit-2.md`（62,036 B）
  - 4-gram 集合大小：**1,345** vs **12,311**
  - 交集 **462** · **Jaccard 0.027** · **a1 被 a2 覆盖 19.4%**
- **结论性读数（陈述，不做判断）**：两份文件的**共同内容不到两成**，合并会丢失各自独有部分
- **未确认**：那 19.4% 的共同片段是模板句还是实质结论——未抽样比对

## 空白 6 · 断链指向的 examples 在外部源的存在率

- **读数**：`docs/recon/official-source-defects-2.md` 引用 **18** 个不同 `*_Example_*.md`；
  其中 **15** 个存在于 `C:\swapi\examples\`，**3** 个不存在：
  `Create_Motion_Studies_Example_VB.md` · `Create_Plots_and_Get_Values_Example_CSharp.md` · `Create_Plots_and_Get_Values_Example_VB.md`
- **交叉核对**：`facts/G-docs.md` G-04 记的 88 条无解断链即指向这批文件 ⇒ **大部分目标在仓库外可查到，3 个连外部源也没有**
- **未确认**：那 3 个是否曾存在于 CHM 源（`AI Solidworks\官方文档\`）——本次只查了 `C:\swapi\examples`

## 空白 7 · `subskills/` 的 `.pyc` 是否入库

- **读数**：磁盘 **12** 个 `.pyc` · `git ls-files subskills` 列出 **0** 个 `.pyc`
- **读数**：`git check-ignore -v subskills` **无输出** ⇒ **`subskills/` 整个目录没有被 gitignore 命中**
- **记录员注（陈述）**：因此这 12 个 `.pyc` 是**未跟踪、又未被 ignore** 的文件（既不在版本库，也不被忽略规则挡掉）
- **未确认**：是否存在全局/其它层级的 `*.pyc` 忽略规则（本机 `core.excludesFile`）——本次只查了 `git check-ignore subskills`

---

## 剩下 2 条空白（本轮未做）

| 空白 | 为什么留到下一轮 |
|---|---|
| **2 · 444 个测试文件的执行期结果** | 需真跑；`M` 维度只覆盖了 34 个门禁类文件 |
| **3 · 100 条 `verified` 的 evidence 是否真支撑该能力** | 需逐条读证据内容并判断与能力的关系；本轮只核了「指向物是否存在」（L 维度） |
